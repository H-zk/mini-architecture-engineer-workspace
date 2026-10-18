<#
.SYNOPSIS
  Idempotently create the Claude Code skills junction: .claude/skills/ -> .agents/skills/
  With -Verify: read-only reachability check of the skills discovery setup.

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

  -Verify: read-only one-shot check — .agents/skills exists, junction present and
  targeting the source of truth. Tool-specific discovery configs (e.g. .kilo/kilo.jsonc)
  are checked only when present (template workspace keeps tool configs optional).
  Exits 1 with [fail] lines on any gap. Intended as the last step of machine setup.

.PARAMETER WorkspaceRoot
  Workspace root (defaults to two levels above this script: .tools/skill-bridge -> .. -> ..).

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File .tools/skill-bridge/link-claude-skills.ps1

.EXAMPLE
  powershell -NoProfile -ExecutionPolicy Bypass -File .tools/skill-bridge/link-claude-skills.ps1 -Verify
#>
[CmdletBinding()]
param(
    [string]$WorkspaceRoot,
    [switch]$Verify
)

$ErrorActionPreference = 'Stop'

if (-not $WorkspaceRoot) {
    # .tools/skill-bridge -> .tools -> workspace root
    $WorkspaceRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
}

$LinkPath   = Join-Path $WorkspaceRoot '.claude\skills'
$TargetPath = Join-Path $WorkspaceRoot '.agents\skills'

if ($Verify) {
    $fail = @()
    if (-not (Test-Path -LiteralPath $TargetPath)) {
        $fail += "missing source of truth: $TargetPath"
    } else {
        $n = (Get-ChildItem -LiteralPath $TargetPath -Directory).Count
        Write-Host "[ok] .agents/skills exists ($n skills)"
    }
    if (Test-Path -LiteralPath $LinkPath) {
        $item = Get-Item -LiteralPath $LinkPath -Force
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            $rt = [string]($item.Target | Select-Object -First 1)
            if ($rt -and (Test-Path -LiteralPath $rt) -and ((Resolve-Path -LiteralPath $rt).Path -ieq (Resolve-Path -LiteralPath $TargetPath).Path)) {
                Write-Host "[ok] junction: .claude/skills -> $TargetPath"
            } else {
                $fail += ".claude/skills junction targets '$rt' (expected $TargetPath)"
            }
        } else {
            $fail += ".claude/skills exists but is NOT a junction (real-dir copy stole the bridge)"
        }
    } else {
        $fail += ".claude/skills missing (bridge not rebuilt on this machine; run this script without -Verify to create)"
    }
    $kilo = Join-Path $WorkspaceRoot '.kilo\kilo.jsonc'
    if (Test-Path -LiteralPath $kilo) {
        $kiloTxt = Get-Content -LiteralPath $kilo -Raw
        if ($kiloTxt -match '\.agents[/\\]skills') {
            Write-Host "[ok] kilo skills.paths declares .agents/skills"
        } else {
            $fail += "kilo kilo.jsonc found but skills.paths lacks .agents/skills"
        }
    } else {
        Write-Host "[skip] no .kilo/kilo.jsonc on this machine (tool config optional)"
    }
    if ($fail.Count -gt 0) {
        $fail | ForEach-Object { Write-Host "[fail] $_" }
        exit 1
    }
    Write-Host "[verify] all reachable from single source: .agents/skills"
    exit 0
}

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
