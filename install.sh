#!/usr/bin/env bash
set -uo pipefail

cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"
VENV_DIR="${VENV_DIR:-.venv}"
REQUIREMENTS_FILE="${REQUIREMENTS_FILE:-requirements.txt}"
OS_RELEASE_FILE="${ANGYSGUARD_OS_RELEASE_FILE:-/etc/os-release}"
MIN_PYTHON_MAJOR=3
MIN_PYTHON_MINOR=11
TMP_VENV=""
TMP_LOG=""
VENV_BACKUP=""
INSTALL_SUCCEEDED=0

info() { printf '[INFO] %s\n' "$*"; }
ok() { printf '[ OK ] %s\n' "$*"; }
warn() { printf '[WARN] %s\n' "$*"; }
error() { printf '[FAIL] %s\n' "$*" >&2; }

cleanup() {
  [[ -n "$TMP_VENV" && -e "$TMP_VENV" ]] && rm -rf -- "$TMP_VENV"
  [[ -n "$TMP_LOG" && -e "$TMP_LOG" ]] && rm -f -- "$TMP_LOG"

  if [[ -n "$VENV_BACKUP" && -e "$VENV_BACKUP" ]]; then
    if (( INSTALL_SUCCEEDED )); then
      rm -rf -- "$VENV_BACKUP"
    else
      warn "Restoring the previous $VENV_DIR after the failed installation."
      rm -rf -- "$VENV_DIR"
      if ! mv -- "$VENV_BACKUP" "$VENV_DIR"; then
        error "Could not automatically restore $VENV_DIR. Previous environment remains at: $VENV_BACKUP"
      fi
    fi
  fi
}
trap cleanup EXIT

fail_install() {
  error "$1"
  printf '\nInstallation summary: FAILED\n'
  [[ -n "${2:-}" ]] && printf '%s\n' "$2"
  exit 1
}

load_os_release() {
  OS_ID=""
  OS_PRETTY_NAME="Linux"
  OS_VERSION_CODENAME=""
  if [[ -r "$OS_RELEASE_FILE" ]]; then
    # shellcheck disable=SC1090
    . "$OS_RELEASE_FILE"
    OS_ID="${ID:-}"
    OS_PRETTY_NAME="${PRETTY_NAME:-Linux}"
    OS_VERSION_CODENAME="${VERSION_CODENAME:-}"
  fi
  [[ "$OS_ID" == "ubuntu" ]]
}

apt_package_installed() {
  local package="$1"
  command -v dpkg-query >/dev/null 2>&1 || return 1
  dpkg-query -W -f='${Status}' "$package" 2>/dev/null | grep -q '^install ok installed$'
}

classify_apt_log() {
  local log="$1"
  if grep -Eqi '404 Not Found|does not have a Release file|Release file .* expired' "$log"; then
    warn "APT mirror/release metadata looks broken or obsolete."
  elif grep -Eqi 'Temporary failure resolving|Could not resolve|Network is unreachable|Connection failed|Connection timed out' "$log"; then
    warn "APT cannot reach the configured mirrors (DNS/network failure)."
  elif grep -Eqi 'NO_PUBKEY|signatures? couldn.t be verified|repository .* is not signed' "$log"; then
    warn "APT repository signing metadata is invalid or incomplete."
  elif grep -Eqi 'Hash Sum mismatch' "$log"; then
    warn "APT mirror metadata appears out of sync (Hash Sum mismatch)."
  elif grep -Eqi 'Failed to fetch|^E:' "$log"; then
    warn "APT reported a repository or mirror failure."
  else
    return 1
  fi
  return 0
}

diagnose_apt_health() {
  local package="$1"
  command -v apt-cache >/dev/null 2>&1 || return 0

  if ! apt-cache show "$package" >/dev/null 2>&1; then
    warn "APT metadata does not currently contain $package."
    warn "The package lists may be stale, the configured mirror may be incomplete, or $PYTHON may not come from Ubuntu packages."
  fi

  # Only probe mirrors on the failure path. Use temporary APT state so this does
  # not modify the user's package lists or require root privileges.
  command -v apt-get >/dev/null 2>&1 || return 0
  command -v timeout >/dev/null 2>&1 || return 0

  local apt_tmp apt_log rc
  apt_tmp="$(mktemp -d)" || return 0
  mkdir -p "$apt_tmp/lists/partial" "$apt_tmp/cache/archives/partial"
  chmod 755 "$apt_tmp" "$apt_tmp/lists" "$apt_tmp/lists/partial" "$apt_tmp/cache" "$apt_tmp/cache/archives" "$apt_tmp/cache/archives/partial" 2>/dev/null || true
  apt_log="$apt_tmp/apt-update.log"

  timeout 15s apt-get \
    -o "Dir::State::lists=$apt_tmp/lists" \
    -o "Dir::Cache::archives=$apt_tmp/cache/archives" \
    -o "APT::Get::List-Cleanup=0" \
    -o "Acquire::Retries=0" \
    update >"$apt_log" 2>&1
  rc=$?

  if ! classify_apt_log "$apt_log" && (( rc != 0 )); then
    warn "APT health probe did not complete successfully."
  fi
  rm -rf -- "$apt_tmp"
}

print_venv_recovery() {
  local package="$1"
  printf '\nPython virtual-environment support is missing for %s.\n' "$PYTHON_VERSION"
  if [[ "$IS_UBUNTU" == "1" ]]; then
    printf 'Install the matching Ubuntu package with:\n'
    printf '  sudo apt update\n'
    printf '  sudo apt install %s\n' "$package"
    printf '\nIf `sudo apt update` reports 404, Release-file, signature, or Failed-to-fetch errors:\n'
    printf '  1. Fix or disable the failing entry in /etc/apt/sources.list or /etc/apt/sources.list.d/.\n'
    printf '  2. If this Ubuntu release is end-of-life, upgrade it or use the official old-releases archive.\n'
    printf '  3. Run `sudo apt update` again, install %s, then rerun ./install.sh.\n' "$package"
  else
    printf 'Install the venv/ensurepip package that matches Python %s for your distribution, then rerun ./install.sh.\n' "$PYTHON_MAJOR.$PYTHON_MINOR"
  fi
}

detect_python() {
  if ! command -v "$PYTHON" >/dev/null 2>&1; then
    fail_install "Python executable '$PYTHON' was not found." "Install Python 3.11 or newer, then rerun ./install.sh."
  fi

  if ! PYTHON_VERSION="$("$PYTHON" -c 'import sys; print(".".join(map(str, sys.version_info[:3])))' 2>/dev/null)"; then
    fail_install "Could not determine the version of '$PYTHON'." "Try: $PYTHON --version"
  fi

  IFS=. read -r PYTHON_MAJOR PYTHON_MINOR PYTHON_PATCH <<<"$PYTHON_VERSION"
  if (( PYTHON_MAJOR < MIN_PYTHON_MAJOR || (PYTHON_MAJOR == MIN_PYTHON_MAJOR && PYTHON_MINOR < MIN_PYTHON_MINOR) )); then
    fail_install "Python $PYTHON_VERSION is too old." "Laptop Guard requires Python 3.11 or newer."
  fi

  VENV_APT_PACKAGE="python${PYTHON_MAJOR}.${PYTHON_MINOR}-venv"
  info "Python: $PYTHON_VERSION ($PYTHON)"
}

check_venv_support() {
  if "$PYTHON" -c 'import ensurepip, venv' >/dev/null 2>&1; then
    ok "Required Python venv support is available."
    return 0
  fi

  diagnose_apt_health "$VENV_APT_PACKAGE"
  print_venv_recovery "$VENV_APT_PACKAGE"
  fail_install "Cannot create a usable virtual environment with $PYTHON."
}

check_recommended_system_packages() {
  [[ "$IS_UBUNTU" == "1" ]] || return 0
  command -v dpkg-query >/dev/null 2>&1 || return 0

  local packages=(python3-tk ffmpeg vlc gnome-screenshot libnotify-bin)
  local missing=()
  local package
  for package in "${packages[@]}"; do
    apt_package_installed "$package" || missing+=("$package")
  done

  if (( ${#missing[@]} == 0 )); then
    ok "Recommended Ubuntu runtime packages are installed."
  else
    warn "Recommended Ubuntu packages not installed: ${missing[*]}"
    printf 'Optional/recommended features can be enabled with:\n'
    printf '  sudo apt install'
    printf ' %q' "${missing[@]}"
    printf '\n'
  fi

  if [[ "${XDG_SESSION_TYPE:-}" == "wayland" ]]; then
    local wayland_missing=()
    apt_package_installed grim || wayland_missing+=(grim)
    apt_package_installed wf-recorder || wayland_missing+=(wf-recorder)
    if (( ${#wayland_missing[@]} > 0 )); then
      warn "Wayland fallback packages not installed: ${wayland_missing[*]}"
      printf '  sudo apt install'
      printf ' %q' "${wayland_missing[@]}"
      printf '\n'
    fi
  fi
}

venv_matches_selected_python() {
  [[ -x "$VENV_DIR/bin/python" ]] || return 1
  local venv_version
  venv_version="$("$VENV_DIR/bin/python" -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")' 2>/dev/null)" || return 1
  [[ "$venv_version" == "$PYTHON_MAJOR.$PYTHON_MINOR" ]] || return 1
  "$VENV_DIR/bin/python" -m pip --version >/dev/null 2>&1
}

create_or_reuse_venv() {
  if venv_matches_selected_python; then
    ok "Reusing existing $VENV_DIR (Python $PYTHON_MAJOR.$PYTHON_MINOR)."
    return 0
  fi

  if [[ -e "$VENV_DIR" ]]; then
    warn "$VENV_DIR is incomplete or uses a different Python version; a replacement will be staged safely."
  fi

  TMP_VENV="${VENV_DIR}.tmp.$"
  rm -rf -- "$TMP_VENV"
  TMP_LOG="$(mktemp)"

  if ! "$PYTHON" -m venv "$TMP_VENV" >"$TMP_LOG" 2>&1; then
    rm -rf -- "$TMP_VENV"
    TMP_VENV=""
    print_venv_recovery "$VENV_APT_PACKAGE"
    fail_install "Virtual environment creation failed." "The existing $VENV_DIR, if any, was left unchanged."
  fi

  rm -f -- "$TMP_LOG"
  TMP_LOG=""

  if [[ -e "$VENV_DIR" ]]; then
    VENV_BACKUP="${VENV_DIR}.backup.$"
    rm -rf -- "$VENV_BACKUP"
    if ! mv -- "$VENV_DIR" "$VENV_BACKUP"; then
      fail_install "Could not stage the existing $VENV_DIR for replacement." "The current environment was left unchanged."
    fi
  fi

  if ! mv -- "$TMP_VENV" "$VENV_DIR"; then
    TMP_VENV=""
    fail_install "Could not activate the newly created virtual environment." "The previous environment will be restored automatically."
  fi
  TMP_VENV=""
  ok "Created $VENV_DIR."
}

print_pip_failure_summary() {
  local log="$1"
  grep -E '^(ERROR:|WARNING:)|No matching distribution found|Could not find a version|Failed building wheel|subprocess-exited-with-error|Temporary failure|Could not resolve|Connection (timed out|refused)' "$log" | tail -n 8 || true
}

run_pip_step() {
  local description="$1"
  shift
  TMP_LOG="$(mktemp)"
  if "$@" >"$TMP_LOG" 2>&1; then
    rm -f -- "$TMP_LOG"
    TMP_LOG=""
    ok "$description"
    return 0
  fi

  error "$description failed."
  print_pip_failure_summary "$TMP_LOG"
  rm -f -- "$TMP_LOG"
  TMP_LOG=""
  return 1
}

install_python_dependencies() {
  [[ -f "$REQUIREMENTS_FILE" ]] || fail_install "Missing $REQUIREMENTS_FILE."
  local vpy="$VENV_DIR/bin/python"

  if ! run_pip_step "Updated pip" "$vpy" -m pip install --upgrade pip; then
    fail_install "Could not update pip." "The virtual environment is recoverable. Rerun ./install.sh after fixing the reported package/network problem."
  fi

  if ! run_pip_step "Installed Python dependencies" "$vpy" -m pip install -r "$REQUIREMENTS_FILE"; then
    fail_install "Python dependency installation failed." "The virtual environment is recoverable. Fix the reported package/network problem, then rerun ./install.sh."
  fi
}

verify_installation() {
  local vpy="$VENV_DIR/bin/python"
  TMP_LOG="$(mktemp)"
  if ! "$vpy" -m pip check >"$TMP_LOG" 2>&1; then
    error "Python dependency verification failed."
    cat "$TMP_LOG" >&2
    fail_install "The installation is not usable yet." "Repair the dependency conflict, then rerun ./install.sh."
  fi
  rm -f -- "$TMP_LOG"
  TMP_LOG=""
  ok "Python dependency verification passed."
}

launch_first_run_ui() {
  local vpy="$VENV_DIR/bin/python"
  if [[ -z "${DISPLAY:-}" && -z "${WAYLAND_DISPLAY:-}" ]]; then
    info "No graphical session detected; skipping the setup window."
    return 0
  fi
  if ! "$vpy" -c 'import tkinter' >/dev/null 2>&1; then
    warn "Tkinter is unavailable; the setup window could not be opened."
    return 0
  fi
  info "Opening the AngysGuard first-run setup window."
  nohup "$vpy" -m laptop_guard onboarding >/dev/null 2>&1 &
}

main() {
  printf 'AngysGuard / Laptop Guard installer\n\n'
  detect_python

  IS_UBUNTU=0
  if load_os_release; then
    IS_UBUNTU=1
    info "OS: $OS_PRETTY_NAME"
  else
    info "OS: $OS_PRETTY_NAME (Ubuntu-specific package guidance disabled)"
  fi

  check_venv_support
  check_recommended_system_packages
  create_or_reuse_venv
  install_python_dependencies
  verify_installation

  INSTALL_SUCCEEDED=1
  launch_first_run_ui
  printf '\nInstallation summary: PASS\n'
  printf 'The Python environment is usable.\n\n'
  printf 'Next command:\n'
  printf '  ./run.sh setup\n'
  printf 'Then verify with:\n'
  printf '  ./run.sh doctor\n'
}

main "$@"
