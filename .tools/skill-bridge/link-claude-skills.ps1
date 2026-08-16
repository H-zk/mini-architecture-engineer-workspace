<#
.SYNOPSIS
  Idempotently create the Claude Code skills junction: .claude/skills/ -> .agents/skills/

.DESCRIPTION
  Claude Code only discovers .claude/skills/; it does not scan .agents/skills/
  (the kilo/opencode/codex/copilot convention that is this workspace's single source
  of truth). This script bridges the two via a Windows junction.

  Why a junction (not a symlink): mklink /D (symlink) needs admin / Developer Mode;
  mklink /J (junction) does not, and Node fs (Claude Code is a Node program) follows it
  — verified: lstatSync().isSymbolicLink() == true, realpathSync() resolves.

  Safe by design: never deletes anything the user placed. If .claude/skills already
  exists as a non-junction, or as a junction pointing elsewhere, it errors out and asks
  for manual inspection rather than overwriting.

  See the README.md in this directory (.tools/skill-bridge/) for the full rationale.

.PARAMETER WorkspaceRoot
  Workspace root (defaults to two levels above this script: .tools/skill-bridge -> .. -> ..).

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File .tools/skill-bridge/link-claude-skills.ps1
#>
[CmdletBinding()]
param(
    [string]$WorkspaceRoot
)

$ErrorActionPreference = 'Stop'

if (-not $WorkspaceRoot) {
    # .tools/skill-bridge -> .tools -> workspace root
    $WorkspaceRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
}

$LinkPath   = Join-Path $WorkspaceRoot '.claude\skills'
$TargetPath = Join-Path $WorkspaceRoot '.agents\skills'

if (-not (Test-Path -LiteralPath $TargetPath)) {
    throw "Target source of truth missing: $TargetPath (expected .agents/skills/ to exist)"
}

if (Test-Path -LiteralPath $LinkPath) {
    $item = Get-Item -LiteralPath $LinkPath -Force
    if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
        $existingTarget = $item.Target
        if ($existingTarget -and (Resolve-Path -LiteralPath $existingTarget).Path -eq (Resolve-Path -LiteralPath $TargetPath).Path) {
            Write-Host "[skip] junction already correct: $LinkPath -> $TargetPath"
            return
        }
        throw "$LinkPath is a reparse point but targets '$existingTarget', not $TargetPath. Inspect manually before re-running."
    }
    throw "$LinkPath already exists and is NOT a junction. Inspect manually before re-running."
}

New-Item -ItemType Junction -Path $LinkPath -Target $TargetPath | Out-Null
Write-Host "[ok] junction created: $LinkPath -> $TargetPath"
Write-Host "Restart Claude Code so it discovers the new top-level .claude/skills/ directory."
