use keyring::Entry;
use reqwest::Client;
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tauri::{Manager, State};
use tokio::sync::Mutex;

const KEYRING_SERVICE: &str = "com.angysguard.desktop";
const KEYRING_ACCOUNT: &str = "enrolled-device";

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

/// Invoke only a fixed, locally installed Laptop Guard command.  Never pass
/// bot text or server-provided arguments to a process.
#[cfg(target_os = "linux")]
async fn run_laptop_guard(args: &[&str]) -> Result<(), String> {
    let status = tokio::time::timeout(
        std::time::Duration::from_secs(20),
        tokio::process::Command::new("laptop-guard")
            .args(args)
            .stdout(std::process::Stdio::null())
            .stderr(std::process::Stdio::null())
            .status(),
    )
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

/// Invoke only a fixed, locally installed Laptop Guard command. Never pass bot
/// text or server-provided arguments to a process.
#[cfg(target_os = "linux")]
async fn run_laptop_guard_action(action: &str) -> Result<(), String> {
    let allowed_action = match action {
        "status" | "arm" | "disarm" => action,
        _ => return Err("Unsupported local Laptop Guard action".into()),
    };
    run_laptop_guard(&[allowed_action]).await
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

async fn apply_command(command: &RemoteCommand, device: &EnrolledDevice) -> String {
    #[cfg(target_os = "linux")]
    if matches!(command.action.as_str(), "status" | "arm" | "disarm") {
        return match run_laptop_guard_action(&command.action).await {
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

async fn poll_forever(state: AgentState) {
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
                        let result = apply_command(&command, &device).await;
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
    run_laptop_guard(&[
        "desktop-setup",
        "--device-name",
        normalized_name,
        "--consent",
    ])
    .await?;
    run_laptop_guard(&["service", "install"]).await?;
    local_protection_status().await
}

#[cfg(target_os = "linux")]
#[tauri::command]
async fn stop_local_protection() -> Result<LocalProtectionStatus, String> {
    run_laptop_guard(&["service", "stop"]).await?;
    local_protection_status().await
}

#[cfg(target_os = "linux")]
#[tauri::command]
async fn local_protection_status() -> Result<LocalProtectionStatus, String> {
    let output = tokio::time::timeout(
        std::time::Duration::from_secs(10),
        tokio::process::Command::new("laptop-guard")
            .arg("desktop-status")
            .output(),
    )
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
async fn prepare_local_protection(_device_name: String, _consent: bool) -> Result<(), String> {
    Err("Automatic local Laptop Guard setup is currently available only on Linux".into())
}

#[cfg(not(target_os = "linux"))]
#[tauri::command]
async fn stop_local_protection() -> Result<(), String> {
    Err("Local Laptop Guard service control is currently available only on Linux".into())
}

#[cfg(not(target_os = "linux"))]
#[tauri::command]
async fn local_protection_status() -> Result<(), String> {
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
            tauri::async_runtime::spawn(poll_forever(agent_state));
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running AngysGuard desktop agent");
}
