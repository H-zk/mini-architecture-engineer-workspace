#!/usr/bin/env bash
# Idempotently create the Claude Code skills symlink: .claude/skills -> .agents/skills/
# (macOS/Linux counterpart of link-claude-skills.ps1, which uses a Windows junction.)
#
# Claude Code only discovers .claude/skills/; it does not scan .agents/skills/
# (the kilo/opencode/codex/copilot convention that is this workspace's single source
# of truth). This script bridges the two via a plain symlink (no admin needed on
# macOS/Linux, unlike Windows).
#
# Safe by design: never deletes anything the user placed. If .claude/skills already
# exists as a non-symlink, or as a symlink pointing elsewhere, it errors out and
# asks for manual inspection rather than overwriting.
#
# Usage: bash .tools/skill-bridge/link-claude-skills.sh
set -euo pipefail

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
root=$(cd "$script_dir/../.." && pwd)
link="$root/.claude/skills"
target="$root/.agents/skills"

if [ ! -d "$target" ]; then
    echo "ERROR: target source of truth missing: $target (expected .agents/skills/ to exist)" >&2
    exit 1
fi

if [ -L "$link" ]; then
    resolved=$(cd "$(dirname "$link")" && cd "$(readlink "$link")" && pwd)
    if [ "$resolved" = "$(cd "$target" && pwd)" ]; then
        echo "[skip] symlink already correct: $link -> $target"
        exit 0
    fi
    echo "ERROR: $link is a symlink but targets '$(readlink "$link")', not $target. Inspect manually before re-running." >&2
    exit 1
fi

if [ -e "$link" ]; then
    echo "ERROR: $link already exists and is NOT a symlink. Inspect manually before re-running." >&2
    exit 1
fi

ln -s "$target" "$link"
echo "[ok] symlink created: $link -> $target"
echo "Restart Claude Code so it discovers the new top-level .claude/skills/ directory."
