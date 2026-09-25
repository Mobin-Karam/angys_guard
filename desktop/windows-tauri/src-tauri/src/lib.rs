use base64::{engine::general_purpose::URL_SAFE_NO_PAD, Engine as _};
use keyring::Entry;
use reqwest::Client;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::{
    fs,
    path::{Path, PathBuf},
    sync::Arc,
};
use tauri::{AppHandle, Manager, State};
use tokio::sync::Mutex;

const KEYRING_SERVICE: &str = "com.angysguard.desktop";
const KEYRING_ACCOUNT: &str = "enrolled-device";
#[cfg(target_os = "linux")]
const BUNDLED_RUNTIME_DIRECTORY: &str = "binaries/laptop-guard-runtime";
#[cfg(target_os = "linux")]
const BUNDLED_RUNTIME_NAME: &str = "laptop-guard-runtime";
#[cfg(target_os = "linux")]
const BUNDLED_RUNTIME_VERSION: &str = env!("CARGO_PKG_VERSION");

#[derive(Clone, Debug, Deserialize, Serialize)]
struct EnrolledDevice {
    server_url: String,
    device_id: String,
    device_token: String,
    account_id: String,
    remote_lock_enabled: bool,
}

#[derive(Clone)]
struct AgentState(Arc<Mutex<Option<EnrolledDevice>>>);

#[derive(Debug, Deserialize)]
struct PollResponse {
    commands: Vec<RemoteCommand>,
}

#[derive(Clone, Debug, Deserialize)]
struct RemoteCommand {
    id: String,
    action: String,
    account_id: String,
    issued_at: i64,
    expires_at: i64,
    signature: String,
}

#[derive(Debug, Deserialize, Serialize)]
struct LocalProtectionStatus {
    configured: bool,
    managed_local_profile: bool,
    consent_recorded: bool,
    armed: bool,
    device_name: String,
    service_active: bool,
}

#[derive(Debug, Deserialize, Serialize)]
struct ConsumedCommand {
    id: String,
    expires_at: i64,
}

fn credential_entry() -> Result<Entry, String> {
    Entry::new(KEYRING_SERVICE, KEYRING_ACCOUNT)
        .map_err(|error| format!("The operating-system credential store is unavailable: {error}"))
}

fn load_device() -> Option<EnrolledDevice> {
    let secret = credential_entry().ok()?.get_password().ok()?;
    serde_json::from_str(&secret).ok()
}

fn command_payload(command: &RemoteCommand, device: &EnrolledDevice) -> Vec<u8> {
    format!(
        "{}\n{}\n{}\n{}\n{}\n{}",
        device.device_id,
        command.account_id,
        command.action,
        command.id,
        command.issued_at,
        command.expires_at,
    )
    .into_bytes()
}

fn command_now() -> Result<i64, String> {
    std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|duration| duration.as_secs() as i64)
        .map_err(|_| "The device clock is invalid".into())
}

fn hmac_sha256(key: &[u8], payload: &[u8]) -> [u8; 32] {
    // HMAC construction from RFC 2104. The derived device key is SHA-256
    // sized, but retain the long-key branch to keep this helper correct.
    let normalized = if key.len() > 64 {
        Sha256::digest(key).to_vec()
    } else {
        key.to_vec()
    };
    let mut block = [0_u8; 64];
    block[..normalized.len()].copy_from_slice(&normalized);
    let mut inner_pad = [0_u8; 64];
    let mut outer_pad = [0_u8; 64];
    for (index, value) in block.iter().enumerate() {
        inner_pad[index] = value ^ 0x36;
        outer_pad[index] = value ^ 0x5c;
    }
    let mut inner = Sha256::new();
    inner.update(inner_pad);
    inner.update(payload);
    let mut outer = Sha256::new();
    outer.update(outer_pad);
    outer.update(inner.finalize());
    outer.finalize().into()
}

fn constant_time_equal(left: &[u8], right: &[u8]) -> bool {
    if left.len() != right.len() {
        return false;
    }
    left.iter()
        .zip(right)
        .fold(0_u8, |difference, (a, b)| difference | (a ^ b))
        == 0
}

fn verify_command_signature(
    command: &RemoteCommand,
    device: &EnrolledDevice,
) -> Result<(), String> {
    let now = command_now()?;
    if command.account_id != device.account_id {
        return Err("command scope does not match this device".into());
    }
    if !matches!(
        command.action.as_str(),
        "status" | "arm" | "disarm" | "lock"
    ) {
        return Err("unsupported command action".into());
    }
    if command.id.is_empty()
        || command.id.len() > 64
        || command.issued_at > now + 15
        || command.expires_at < now
        || command.expires_at - command.issued_at > 120
    {
        return Err("command is expired or invalid".into());
    }
    let credential_key = Sha256::digest(device.device_token.as_bytes());
    let signature = URL_SAFE_NO_PAD
        .decode(command.signature.as_bytes())
        .map_err(|_| "command signature is invalid".to_string())?;
    let expected = hmac_sha256(&credential_key, &command_payload(command, device));
    if constant_time_equal(&expected, &signature) {
        Ok(())
    } else {
        Err("command signature is invalid".into())
    }
}

fn consume_command_replay_marker(app: &AppHandle, command: &RemoteCommand) -> Result<(), String> {
    let now = command_now()?;
    let directory = app
        .path()
        .app_local_data_dir()
        .map_err(|error| format!("Could not resolve local command storage: {error}"))?;
    fs::create_dir_all(&directory)
        .map_err(|error| format!("Could not create local command storage: {error}"))?;
    let path = directory.join("consumed-managed-commands.json");
    let mut consumed: Vec<ConsumedCommand> = match fs::read(&path) {
        Ok(data) => serde_json::from_slice(&data).map_err(|_| {
            "Local command replay storage is invalid; refusing the command".to_string()
        })?,
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => Vec::new(),
        Err(_) => return Err("Could not read local command replay storage".into()),
    };
    consumed.retain(|item| item.expires_at >= now);
    if consumed.iter().any(|item| item.id == command.id) {
        return Err("replayed command".into());
    }
    consumed.push(ConsumedCommand {
        id: command.id.clone(),
        expires_at: command.expires_at,
    });
    let encoded = serde_json::to_vec(&consumed)
        .map_err(|_| "Could not serialize local command replay storage".to_string())?;
    let temporary = directory.join(".consumed-managed-commands.new");
    fs::write(&temporary, encoded)
        .map_err(|_| "Could not write local command replay storage".to_string())?;
    fs::rename(&temporary, &path)
        .map_err(|_| "Could not finalize local command replay storage".to_string())?;
    Ok(())
}

async fn send_completion(client: &Client, device: &EnrolledDevice, command_id: &str, result: &str) {
    let _ = client
        .post(format!("{}/v1/device/commands/complete", device.server_url))
        .header("Authorization", format!("Device {}", device.device_token))
        .json(&serde_json::json!({"command_id": command_id, "result": result}))
        .send()
        .await;
}

#[cfg(target_os = "windows")]
async fn lock_workstation() -> Result<(), String> {
    if unsafe { windows_sys::Win32::UI::WindowsAndMessaging::LockWorkStation() } == 0 {
        return Err("Windows refused lock request".into());
    }
    Ok(())
}

#[cfg(target_os = "linux")]
fn provisioned_runtime_path(app: &AppHandle) -> Result<PathBuf, String> {
    app.path()
        .app_local_data_dir()
        .map(|root| {
            root.join("runtime")
                .join(BUNDLED_RUNTIME_VERSION)
                .join(BUNDLED_RUNTIME_NAME)
        })
        .map_err(|error| format!("Could not resolve the local AngysGuard data directory: {error}"))
}

#[cfg(target_os = "linux")]
fn bundled_runtime_directory(app: &AppHandle) -> Option<PathBuf> {
    app.path()
        .resource_dir()
        .ok()
        .map(|root| root.join(BUNDLED_RUNTIME_DIRECTORY))
        .filter(|directory| directory.join(BUNDLED_RUNTIME_NAME).is_file())
}

#[cfg(target_os = "linux")]
fn copy_runtime_tree(source: &Path, destination: &Path) -> Result<(), String> {
    fs::create_dir_all(destination)
        .map_err(|error| format!("Could not create the local runtime directory: {error}"))?;
    for entry in fs::read_dir(source)
        .map_err(|error| format!("Could not read the bundled runtime: {error}"))?
    {
        let entry =
            entry.map_err(|error| format!("Could not read a bundled runtime file: {error}"))?;
        let source_path = entry.path();
        let destination_path = destination.join(entry.file_name());
        let metadata = fs::metadata(&source_path)
            .map_err(|error| format!("Could not inspect a bundled runtime file: {error}"))?;
        if metadata.is_dir() {
            copy_runtime_tree(&source_path, &destination_path)?;
        } else if metadata.is_file() {
            fs::copy(&source_path, &destination_path)
                .map_err(|error| format!("Could not provision the local runtime: {error}"))?;
            fs::set_permissions(&destination_path, metadata.permissions()).map_err(|error| {
                format!("Could not preserve local runtime permissions: {error}")
            })?;
        } else {
            return Err("The bundled runtime contains an unsupported file type".into());
        }
    }
    Ok(())
}

/// Provision a packaged runtime in a durable per-user directory. AppImage mount
/// paths are temporary, so they must never be written into a user service.
#[cfg(target_os = "linux")]
fn provision_runtime(app: &AppHandle) -> Result<PathBuf, String> {
    let target = provisioned_runtime_path(app)?;
    if target.is_file() {
        return Ok(target);
    }
    let Some(source) = bundled_runtime_directory(app) else {
        return Ok(PathBuf::from("laptop-guard"));
    };
    let target_directory = target.parent().ok_or("Invalid local runtime path")?;
    copy_runtime_tree(&source, target_directory)?;
    if !target.is_file() {
        return Err("The bundled runtime did not contain its executable".into());
    }
    Ok(target)
}

/// Resolve an already-provisioned sidecar, otherwise use the packaged resource
/// for status checks before first setup or a local developer fallback.
#[cfg(target_os = "linux")]
fn runtime_program(app: &AppHandle) -> PathBuf {
    if let Ok(provisioned) = provisioned_runtime_path(app) {
        if provisioned.is_file() {
            return provisioned;
        }
    }
    bundled_runtime_directory(app)
        .map(|directory| directory.join(BUNDLED_RUNTIME_NAME))
        .filter(|candidate| candidate.is_file())
        .unwrap_or_else(|| PathBuf::from("laptop-guard"))
}

/// Invoke only a fixed Laptop Guard command. Never pass bot text or
/// server-provided arguments to a process.
#[cfg(target_os = "linux")]
async fn run_laptop_guard_with_program(program: &Path, args: &[&str]) -> Result<(), String> {
    let bundled_path = program.is_absolute().then_some(program);
    let mut command = tokio::process::Command::new(program);
    command
        .args(args)
        .stdout(std::process::Stdio::null())
        .stderr(std::process::Stdio::null());
    if let Some(path) = bundled_path {
        // The service installer records this absolute installed sidecar path;
        // it never uses a shell lookup or a temporary unpacking directory.
        command.env("ANGYSGUARD_RUNTIME_EXECUTABLE", path);
    }
    let status = tokio::time::timeout(std::time::Duration::from_secs(20), command.status())
        .await
        .map_err(|_| "Local Laptop Guard command timed out".to_string())?
        .map_err(|_| {
            "The local Laptop Guard runtime is not installed or cannot be started".to_string()
        })?;
    if status.success() {
        Ok(())
    } else {
        Err("Local Laptop Guard rejected the action; review its local setup".into())
    }
}

#[cfg(target_os = "linux")]
async fn run_laptop_guard(app: &AppHandle, args: &[&str]) -> Result<(), String> {
    let program = runtime_program(app);
    run_laptop_guard_with_program(&program, args).await
}

/// Invoke only a fixed, locally installed Laptop Guard command. Never pass bot
/// text or server-provided arguments to a process.
#[cfg(target_os = "linux")]
async fn run_laptop_guard_action(app: &AppHandle, action: &str) -> Result<(), String> {
    let allowed_action = match action {
        "status" | "arm" | "disarm" => action,
        _ => return Err("Unsupported local Laptop Guard action".into()),
    };
    run_laptop_guard(app, &[allowed_action]).await
}

#[cfg(target_os = "linux")]
async fn lock_workstation() -> Result<(), String> {
    let status = tokio::time::timeout(
        std::time::Duration::from_secs(5),
        tokio::process::Command::new("loginctl")
            .arg("lock-session")
            .status(),
    )
    .await
    .map_err(|_| "Linux session lock timed out".to_string())?
    .map_err(|error| format!("Linux loginctl is unavailable: {error}"))?;
    if status.success() {
        Ok(())
    } else {
        Err("Linux session manager refused the lock request".into())
    }
}

#[cfg(not(any(target_os = "windows", target_os = "linux")))]
async fn lock_workstation() -> Result<(), String> {
    Err("Session lock is not available on this platform".into())
}

async fn apply_command(
    app: &AppHandle,
    command: &RemoteCommand,
    device: &EnrolledDevice,
) -> String {
    if let Err(error) = verify_command_signature(command, device) {
        return format!("denied: {error}");
    }
    if let Err(error) = consume_command_replay_marker(app, command) {
        return format!("denied: {error}");
    }
    #[cfg(target_os = "linux")]
    if matches!(command.action.as_str(), "status" | "arm" | "disarm") {
        return match run_laptop_guard_action(app, &command.action).await {
            Ok(()) => format!("completed: local Laptop Guard {} action", command.action),
            Err(error) => format!("failed: {error}"),
        };
    }
    match command.action.as_str() {
        "status" => "online: AngysGuard desktop agent is running".to_string(),
        "arm" => {
            "accepted: local guard arming integration is pending Windows capability validation"
                .to_string()
        }
        "disarm" => {
            "accepted: local guard disarming integration is pending Windows capability validation"
                .to_string()
        }
        "lock" if !device.remote_lock_enabled => {
            "denied: remote lock has not been enabled locally".to_string()
        }
        "lock" => match lock_workstation().await {
            Ok(()) => "completed: local session locked".to_string(),
            Err(error) => format!("failed: {error}"),
        },
        _ => "denied: unsupported remote action".to_string(),
    }
}

async fn poll_forever(state: AgentState, app: AppHandle) {
    let client = Client::new();
    loop {
        let device = { state.0.lock().await.clone() };
        if let Some(device) = device {
            if let Ok(response) = client
                .get(format!("{}/v1/device/commands", device.server_url))
                .header("Authorization", format!("Device {}", device.device_token))
                .send()
                .await
            {
                if let Ok(pending) = response.json::<PollResponse>().await {
                    for command in pending.commands {
                        let result = apply_command(&app, &command, &device).await;
                        send_completion(&client, &device, &command.id, &result).await;
                    }
                }
            }
        }
        tokio::time::sleep(std::time::Duration::from_secs(10)).await;
    }
}

#[tauri::command]
async fn store_device(
    server_url: String,
    device_id: String,
    device_token: String,
    account_id: String,
    state: State<'_, AgentState>,
) -> Result<(), String> {
    if !server_url.starts_with("https://") && !server_url.starts_with("http://localhost") {
        return Err("An HTTPS server URL is required outside local development".into());
    }
    if device_id.is_empty()
        || device_id.len() > 64
        || account_id.is_empty()
        || account_id.len() > 64
    {
        return Err("The server returned an invalid enrollment scope".into());
    }
    let device = EnrolledDevice {
        server_url: server_url.trim_end_matches('/').to_string(),
        device_id,
        device_token,
        account_id,
        remote_lock_enabled: false,
    };
    credential_entry()?
        .set_password(&serde_json::to_string(&device).map_err(|error| error.to_string())?)
        .map_err(|error| format!("Unable to store the device credential: {error}"))?;
    *state.0.lock().await = Some(device);
    Ok(())
}

#[tauri::command]
async fn set_remote_lock_enabled(
    enabled: bool,
    state: State<'_, AgentState>,
) -> Result<(), String> {
    let mut guard = state.0.lock().await;
    let device = guard.as_mut().ok_or("Enroll this device first")?;
    device.remote_lock_enabled = enabled;
    credential_entry()?
        .set_password(&serde_json::to_string(device).map_err(|error| error.to_string())?)
        .map_err(|error| format!("Unable to update the operating-system credential store: {error}"))
}

#[cfg(target_os = "linux")]
async fn systemd_user_service_active() -> bool {
    tokio::time::timeout(
        std::time::Duration::from_secs(5),
        tokio::process::Command::new("systemctl")
            .args(["--user", "is-active", "--quiet", "laptop-guard.service"])
            .status(),
    )
    .await
    .ok()
    .and_then(Result::ok)
    .is_some_and(|status| status.success())
}

#[cfg(target_os = "linux")]
#[tauri::command]
async fn prepare_local_protection(
    app: AppHandle,
    device_name: String,
    consent: bool,
) -> Result<LocalProtectionStatus, String> {
    if !consent {
        return Err("Local privacy consent is required before protection can start".into());
    }
    let normalized_name = device_name.trim();
    if normalized_name.is_empty() || normalized_name.chars().count() > 80 {
        return Err("Device name must contain 1 to 80 characters".into());
    }
    // `device_name` is locally typed, length-bounded, and supplied as one
    // argument; no provider/server content is ever executed here.
    let runtime = provision_runtime(&app)?;
    run_laptop_guard_with_program(
        &runtime,
        &[
            "desktop-setup",
            "--device-name",
            normalized_name,
            "--consent",
        ],
    )
    .await?;
    run_laptop_guard_with_program(&runtime, &["service", "install"]).await?;
    local_protection_status(app).await
}

#[cfg(target_os = "linux")]
#[tauri::command]
async fn stop_local_protection(app: AppHandle) -> Result<LocalProtectionStatus, String> {
    run_laptop_guard(&app, &["service", "stop"]).await?;
    local_protection_status(app).await
}

#[cfg(target_os = "linux")]
#[tauri::command]
async fn local_protection_status(app: AppHandle) -> Result<LocalProtectionStatus, String> {
    let program = runtime_program(&app);
    let bundled_path = program.is_absolute().then_some(program.clone());
    let mut command = tokio::process::Command::new(program);
    command.arg("desktop-status");
    if let Some(path) = bundled_path {
        command.env("ANGYSGUARD_RUNTIME_EXECUTABLE", path);
    }
    let output = tokio::time::timeout(std::time::Duration::from_secs(10), command.output())
        .await
        .map_err(|_| "Local Laptop Guard status check timed out".to_string())?
        .map_err(|_| {
            "The local Laptop Guard runtime is not installed or cannot be started".to_string()
        })?;
    if !output.status.success() {
        return Err("Local Laptop Guard could not report its status".into());
    }
    let mut status: LocalProtectionStatus = serde_json::from_slice(&output.stdout)
        .map_err(|_| "Local Laptop Guard returned an invalid status response".to_string())?;
    status.service_active = systemd_user_service_active().await;
    Ok(status)
}

#[cfg(not(target_os = "linux"))]
#[tauri::command]
async fn prepare_local_protection(
    _app: AppHandle,
    _device_name: String,
    _consent: bool,
) -> Result<(), String> {
    Err("Automatic local Laptop Guard setup is currently available only on Linux".into())
}

#[cfg(not(target_os = "linux"))]
#[tauri::command]
async fn stop_local_protection(_app: AppHandle) -> Result<(), String> {
    Err("Local Laptop Guard service control is currently available only on Linux".into())
}

#[cfg(not(target_os = "linux"))]
#[tauri::command]
async fn local_protection_status(_app: AppHandle) -> Result<(), String> {
    Err("Local Laptop Guard status is currently available only on Linux".into())
}

pub fn run() {
    let state = AgentState(Arc::new(Mutex::new(load_device())));
    tauri::Builder::default()
        .manage(state.clone())
        .plugin(tauri_plugin_autostart::init(
            tauri_plugin_autostart::MacosLauncher::LaunchAgent,
            None,
        ))
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![
            store_device,
            set_remote_lock_enabled,
            prepare_local_protection,
            stop_local_protection,
            local_protection_status,
        ])
        .setup(move |app| {
            let agent_state = app.state::<AgentState>().inner().clone();
            tauri::async_runtime::spawn(poll_forever(agent_state, app.handle().clone()));
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running AngysGuard desktop agent");
}

#[cfg(test)]
mod tests {
    use super::*;

    fn signed_command(device: &EnrolledDevice) -> RemoteCommand {
        let now = command_now().expect("clock");
        let mut command = RemoteCommand {
            id: "test-command".into(),
            action: "status".into(),
            account_id: device.account_id.clone(),
            issued_at: now,
            expires_at: now + 60,
            signature: String::new(),
        };
        let key = Sha256::digest(device.device_token.as_bytes());
        command.signature = URL_SAFE_NO_PAD.encode(hmac_sha256(&key, &command_payload(&command, device)));
        command
    }

    #[test]
    fn signed_command_rejects_tampering_and_wrong_scope() {
        let device = EnrolledDevice {
            server_url: "https://example.test".into(),
            device_id: "device-1".into(),
            device_token: "device-token".into(),
            account_id: "account-1".into(),
            remote_lock_enabled: false,
        };
        let command = signed_command(&device);
        assert!(verify_command_signature(&command, &device).is_ok());

        let mut changed = command.clone();
        changed.action = "lock".into();
        assert!(verify_command_signature(&changed, &device).is_err());
        let mut wrong_scope = command;
        wrong_scope.account_id = "account-2".into();
        assert!(verify_command_signature(&wrong_scope, &device).is_err());
    }

    #[test]
    fn hmac_matches_the_managed_api_canonical_vector() {
        // Produced by server.app.security.sign_device_command.  Keeping a
        // fixed vector here prevents accidental Rust/Python payload drift.
        let device = EnrolledDevice {
            server_url: "https://example.test".into(),
            device_id: "device-1".into(),
            device_token: "device-token".into(),
            account_id: "account-1".into(),
            remote_lock_enabled: false,
        };
        let command = RemoteCommand {
            id: "test-command".into(),
            action: "status".into(),
            account_id: "account-1".into(),
            issued_at: 1_700_000_000,
            expires_at: 1_700_000_060,
            signature: String::new(),
        };
        let key = Sha256::digest(device.device_token.as_bytes());
        assert_eq!(
            URL_SAFE_NO_PAD.encode(hmac_sha256(&key, &command_payload(&command, &device))),
            "MSjxhmK8zjHG6clWWp17ZyR1hphxWhO5mreJWCEVhVU"
        );
    }
}
