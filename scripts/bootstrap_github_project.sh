#!/usr/bin/env bash
set -euo pipefail

BLUEPRINT="${1:-.github/repository-management/project-v2.json}"

if [[ ! -f "$BLUEPRINT" ]]; then
  echo "Project blueprint not found: $BLUEPRINT" >&2
  exit 2
fi

for command in gh jq; do
  if ! command -v "$command" >/dev/null 2>&1; then
    echo "Required command not found: $command" >&2
    exit 2
  fi
done

if [[ -z "${GH_TOKEN:-}" ]]; then
  echo "GH_TOKEN is required and must have the GitHub 'project' scope." >&2
  exit 2
fi

OWNER="$(jq -r '.owner' "$BLUEPRINT")"
TITLE="$(jq -r '.title' "$BLUEPRINT")"
DESCRIPTION="$(jq -r '.description' "$BLUEPRINT")"
VISIBILITY="$(jq -r '.visibility // "PRIVATE"' "$BLUEPRINT")"
REPO="${GITHUB_REPOSITORY:-$(jq -r '.repository_current' "$BLUEPRINT")}"
REPO_NAME="${REPO#*/}"

projects_json="$(gh project list --owner "$OWNER" --closed --format json)"
project_number="$(jq -r --arg title "$TITLE" '.projects[]? | select(.title == $title) | .number' <<<"$projects_json" | head -n1)"

if [[ -z "$project_number" || "$project_number" == "null" ]]; then
  echo "Creating GitHub Project: $TITLE"
  created="$(gh project create --owner "$OWNER" --title "$TITLE" --format json)"
  project_number="$(jq -r '.number' <<<"$created")"
else
  echo "Using existing GitHub Project #$project_number: $TITLE"
fi

gh project edit "$project_number" \
  --owner "$OWNER" \
  --title "$TITLE" \
  --description "$DESCRIPTION" \
  --visibility "$VISIBILITY" >/dev/null

# Linking is idempotent enough for bootstrap use; ignore an already-linked response.
gh project link "$project_number" --owner "$OWNER" --repo "$REPO_NAME" >/dev/null 2>&1 || true

ensure_single_select_field() {
  local name="$1"
  local options="$2"
  local fields
  fields="$(gh project field-list "$project_number" --owner "$OWNER" --limit 100 --format json)"
  if jq -e --arg name "$name" '.fields[]? | select(.name == $name)' <<<"$fields" >/dev/null; then
    return 0
  fi
  gh project field-create "$project_number" \
    --owner "$OWNER" \
    --name "$name" \
    --data-type SINGLE_SELECT \
    --single-select-options "$options" >/dev/null
}

ensure_single_select_field "Priority" "P0,P1,P2,P3"
ensure_single_select_field "Track" "Product,Architecture,Security,Release,Repository,Platform,Desktop App,Mobile,Managed Service"
ensure_single_select_field "Area" "Setup,Runtime,Provider,Storage,UX,CI,Release,Docs,Platform,Desktop App,Mobile,Managed Service"
ensure_single_select_field "Effort" "XS,S,M,L,XL"
ensure_single_select_field "Target" "v11.2,v11.3,v12.0,v13.0,v14.0,Future Platform Expansion,Architecture Evolution"
ensure_single_select_field "Blocked" "No,Yes"

map_track() {
  local labels="$1"
  if grep -qx 'area:managed-service' <<<"$labels"; then echo "Managed Service"; return; fi
  if grep -qx 'area:mobile' <<<"$labels"; then echo "Mobile"; return; fi
  if grep -qx 'area:desktop-app' <<<"$labels"; then echo "Desktop App"; return; fi
  if grep -qx 'area:platform' <<<"$labels"; then echo "Platform"; return; fi
  if grep -qx 'type:architecture' <<<"$labels"; then echo "Architecture"; return; fi
  if grep -qx 'type:security' <<<"$labels"; then echo "Security"; return; fi
  if grep -qx 'type:release' <<<"$labels"; then echo "Release"; return; fi
  if grep -qx 'project' <<<"$labels"; then echo "Repository"; return; fi
  echo "Product"
}

map_area() {
  local labels="$1"
  local pair
  for pair in \
    'area:managed-service|Managed Service' \
    'area:desktop-app|Desktop App' \
    'area:mobile|Mobile' \
    'area:platform|Platform' \
    'area:setup|Setup' \
    'area:runtime|Runtime' \
    'area:provider|Provider' \
    'area:storage|Storage' \
    'area:ux|UX' \
    'area:ci|CI' \
    'area:release|Release'; do
    if grep -qx "${pair%%|*}" <<<"$labels"; then
      echo "${pair##*|}"
      return
    fi
  done
  echo "Docs"
}

set_field() {
  local url="$1"
  local field="$2"
  local value="$3"
  [[ -z "$value" || "$value" == "null" ]] && return 0
  gh project item-edit "$project_number" \
    --owner "$OWNER" \
    --url "$url" \
    --field "$field" \
    --value "$value" >/dev/null
}

while IFS=$'\t' read -r target issue; do
  [[ -z "$issue" ]] && continue

  issue_json="$(gh issue view "$issue" --repo "$REPO" --json url,labels,state)"
  url="$(jq -r '.url' <<<"$issue_json")"
  labels="$(jq -r '.labels[].name' <<<"$issue_json")"
  state="$(jq -r '.state' <<<"$issue_json")"

  gh project item-add "$project_number" --owner "$OWNER" --url "$url" >/dev/null 2>&1 || true

  priority="$(grep -E '^priority:P[0-3]$' <<<"$labels" | head -n1 | cut -d: -f2 || true)"
  track="$(map_track "$labels")"
  area="$(map_area "$labels")"
  blocked="No"
  grep -qx 'status:blocked' <<<"$labels" && blocked="Yes"

  [[ "$target" == "project" ]] && target=""

  # Only synchronize stable lifecycle states. Open work may intentionally be in
  # Backlog, Ready, In progress, or Review, so rerunning the bootstrap must not
  # overwrite a maintainer's active workflow state.
  if [[ "$state" == "CLOSED" || "$state" == "closed" ]]; then
    set_field "$url" "Status" "Done"
  elif grep -qx 'status:needs-validation' <<<"$labels"; then
    set_field "$url" "Status" "Validation"
  fi

  set_field "$url" "Priority" "$priority"
  set_field "$url" "Track" "$track"
  set_field "$url" "Area" "$area"
  set_field "$url" "Target" "$target"
  set_field "$url" "Blocked" "$blocked"
done < <(jq -r '.milestone_issue_groups | to_entries[] | .key as $target | .value[] | [$target, tostring] | @tsv' "$BLUEPRINT")

echo "AngysGuard Project v2 is synchronized: owner=$OWNER project=$project_number repository=$REPO"
