use keyring::Entry;
use reqwest::Client;
use serde::{Deserialize, Serialize};
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
    remote_lock_enabled: bool,
}

#[derive(Clone)]
struct AgentState(Arc<Mutex<Option<EnrolledDevice>>>);

#[derive(Debug, Deserialize)]
struct PollResponse {
    commands: Vec<RemoteCommand>,
}

#[derive(Debug, Deserialize)]
struct RemoteCommand {
    id: String,
    action: String,
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

fn credential_entry() -> Result<Entry, String> {
    Entry::new(KEYRING_SERVICE, KEYRING_ACCOUNT)
        .map_err(|error| format!("The operating-system credential store is unavailable: {error}"))
}

fn load_device() -> Option<EnrolledDevice> {
    let secret = credential_entry().ok()?.get_password().ok()?;
    serde_json::from_str(&secret).ok()
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
    state: State<'_, AgentState>,
) -> Result<(), String> {
    if !server_url.starts_with("https://") && !server_url.starts_with("http://localhost") {
        return Err("An HTTPS server URL is required outside local development".into());
    }
    let device = EnrolledDevice {
        server_url: server_url.trim_end_matches('/').to_string(),
        device_id,
        device_token,
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
