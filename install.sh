#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_SRC="$SCRIPT_DIR/skills/incisive"
MODE="symlink"
FORCE=0
TARGET=""

usage() {
  cat <<'EOF'
Usage: ./install.sh [claude|cursor|codex|opencode|agents|all] [--copy] [--force]

  Target defaults to claude. Flags may appear in any position.
  --copy    Copy the skill instead of symlinking it to this checkout.
  --force   Replace an existing "incisive" directory that this installer did not create.
  all       Install for every supported tool whose config directory already exists.
EOF
}

for arg in "$@"; do
  case "$arg" in
    --copy) MODE="copy" ;;
    --force) FORCE=1 ;;
    -h|--help) usage; exit 0 ;;
    claude|cursor|codex|opencode|agents|all)
      if [[ -n "$TARGET" ]]; then
        echo "Error: more than one target given ('$TARGET' and '$arg')." >&2
        usage
        exit 1
      fi
      TARGET="$arg"
      ;;
    *)
      echo "Error: unknown argument '$arg'." >&2
      usage
      exit 1
      ;;
  esac
done
TARGET="${TARGET:-claude}"

if [[ ! -f "$SKILL_SRC/SKILL.md" ]]; then
  echo "Error: skill source not found at $SKILL_SRC" >&2
  exit 1
fi

# True when $1 is something this installer put there: a symlink, or a copied incisive skill.
is_previous_install() {
  local dest="$1"
  [[ -L "$dest" ]] && return 0
  [[ -f "$dest/SKILL.md" ]] && grep -q '^name: incisive$' "$dest/SKILL.md"
}

install_to() {
  local dest_root="$1"
  local label="$2"
  local dest="$dest_root/incisive"

  if [[ -e "$dest" || -L "$dest" ]]; then
    if ! is_previous_install "$dest" && [[ "$FORCE" -ne 1 ]]; then
      echo "[skip] $dest exists and is not an incisive install; rerun with --force to replace it ($label)" >&2
      return 1
    fi
    rm -rf "$dest"
  fi

  mkdir -p "$dest_root"
  if [[ "$MODE" == "copy" ]]; then
    cp -R "$SKILL_SRC" "$dest"
  else
    ln -s "$SKILL_SRC" "$dest"
  fi
  echo "[ok] Installed incisive ($MODE) -> $dest ($label)"
}

# For `all`: only touch tools whose config directory is already present.
install_if_present() {
  local config_dir="$1"
  local dest_root="$2"
  local label="$3"
  if [[ ! -d "$config_dir" ]]; then
    echo "[skip] $label not found ($config_dir does not exist)"
    return 0
  fi
  install_to "$dest_root" "$label"
}

case "$TARGET" in
  claude)   install_to "$HOME/.claude/skills" "Claude Code" ;;
  cursor)   install_to "$HOME/.cursor/skills" "Cursor" ;;
  codex)    install_to "$HOME/.codex/skills" "Codex CLI" ;;
  opencode) install_to "$HOME/.config/opencode/skills" "OpenCode" ;;
  agents)   install_to "$HOME/.agents/skills" "Generic Agent Skills" ;;
  all)
    failed=0
    install_if_present "$HOME/.claude" "$HOME/.claude/skills" "Claude Code" || failed=1
    install_if_present "$HOME/.cursor" "$HOME/.cursor/skills" "Cursor" || failed=1
    install_if_present "$HOME/.codex" "$HOME/.codex/skills" "Codex CLI" || failed=1
    install_if_present "$HOME/.config/opencode" "$HOME/.config/opencode/skills" "OpenCode" || failed=1
    install_if_present "$HOME/.agents" "$HOME/.agents/skills" "Generic Agent Skills" || failed=1
    exit "$failed"
    ;;
esac
