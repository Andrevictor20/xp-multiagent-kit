<#
.SYNOPSIS
    XP Multi-Agent Kit v3.1 — Unified Windows PowerShell Bootstrapper (PT / EN Auto-Detected)
    Supports Antigravity, OpenCode, Cursor, Qoder, and Codex (IDE & CLI)
.DESCRIPTION
    Installs, configures, and injects the XP Multi-Agent Kit on Windows environments.
.EXAMPLE
    .\install.ps1
    .\install.ps1 -Scope global -Target all -Yes
    .\install.ps1 -ProjectDir "C:\workspace\my-app" -Target cursor,codex -Yes
#>
[CmdletBinding()]
param(
    [string]$Target,
    [string]$Scope,
    [string]$ProjectDir,
    [string]$Lang,
    [switch]$DryRun,
    [switch]$Yes
)

$ErrorActionPreference = "Stop"

$RepoUrl = if ($env:XP_KIT_REPO_URL) { $env:XP_KIT_REPO_URL } else { "https://github.com/Andrevictor20/xp-multiagent-kit.git" }
$DefaultCloneDir = Join-Path $env:USERPROFILE ".local\share\xp-multiagent-kit"

# Detect system language (pt or en)
$SysLang = if ($Lang) { $Lang } elseif ($env:XP_LANG) { $env:XP_LANG } else { [System.Globalization.CultureInfo]::CurrentUICulture.TwoLetterISOLanguageName }
$IsPt = $SysLang.ToLower().StartsWith("pt")

if ($IsPt) {
    $MsgPyErr = "❌ Erro: Python 3 é obrigatório para executar o instalador do XP Multi-Agent Kit (instale via python.org ou 'winget install Python.Python.3.11')."
    $MsgGitErr = "❌ Erro: Git é obrigatório para baixar o kit (instale via git-scm.com ou 'winget install Git.Git')."
    $MsgDl = "⬇️  Baixando XP Multi-Agent Kit em"
    $MsgUpd = "🔄 Atualizando instalação existente em"
} else {
    $MsgPyErr = "❌ Error: Python 3 is required to run the XP Multi-Agent Kit installer (install via python.org or 'winget install Python.Python.3.11')."
    $MsgGitErr = "❌ Error: Git is required to download the kit (install via git-scm.com or 'winget install Git.Git')."
    $MsgDl = "⬇️  Downloading XP Multi-Agent Kit to"
    $MsgUpd = "🔄 Updating existing installation at"
}

# Locate Python executable
$PyExe = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $PyExe = "python"
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $PyExe = "py"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $PyExe = "python3"
}

if (-not $PyExe) {
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host "⏳ Python 3 não encontrado. Tentando instalar via winget..." -ForegroundColor Cyan
        winget install --id Python.Python.3.11 -e --silent --accept-package-agreements --accept-source-agreements
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        if (Get-Command python -ErrorAction SilentlyContinue) { $PyExe = "python" }
        elseif (Get-Command py -ErrorAction SilentlyContinue) { $PyExe = "py" }
    }
}

if (-not $PyExe) {
    Write-Error $MsgPyErr
    exit 1
}

# Check if running from local repository clone
$KitInstallerPath = $null
if ($PSScriptRoot -and (Test-Path (Join-Path $PSScriptRoot "scripts\kit_installer.py"))) {
    $KitInstallerPath = Join-Path $PSScriptRoot "scripts\kit_installer.py"
}

# If not running from local repository, download or update via git
if (-not $KitInstallerPath) {
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        if (Get-Command winget -ErrorAction SilentlyContinue) {
            Write-Host "⏳ Git não encontrado. Tentando instalar via winget..." -ForegroundColor Cyan
            winget install --id Git.Git -e --silent --accept-package-agreements --accept-source-agreements
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        }
    }
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        Write-Error $MsgGitErr
        exit 1
    }

    if (Test-Path (Join-Path $DefaultCloneDir ".git")) {
        Write-Host "$MsgUpd $DefaultCloneDir..." -ForegroundColor Cyan
        git -C $DefaultCloneDir pull --ff-only --quiet
    } else {
        Write-Host "$MsgDl $DefaultCloneDir..." -ForegroundColor Cyan
        New-Item -ItemType Directory -Path (Split-Path $DefaultCloneDir -Parent) -Force | Out-Null
        git clone --depth 1 $RepoUrl $DefaultCloneDir
    }
    $KitInstallerPath = Join-Path $DefaultCloneDir "scripts\kit_installer.py"
}

# Forward arguments to python kit_installer.py
$PyArgs = @($KitInstallerPath)

if ($Target) { $PyArgs += "--target", $Target }
if ($Scope -eq "global") { $PyArgs += "--global" }
if ($Scope -eq "project" -and $ProjectDir) { $PyArgs += "--project", $ProjectDir }
if ($Scope -eq "both" -and $ProjectDir) { $PyArgs += "--both", $ProjectDir }
if ($Lang) { $PyArgs += "--lang", $Lang }
if ($DryRun) { $PyArgs += "--dry-run" }
if ($Yes) { $PyArgs += "--yes" }

# Execute installer
if ($PyExe -eq "py") {
    & py -3 $PyArgs
} else {
    & $PyExe $PyArgs
}
