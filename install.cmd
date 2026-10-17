@echo off
rem ==============================================================================
rem XP Multi-Agent Kit v3.1 — Windows CMD / Batch Bootstrapper
rem Supports Antigravity, OpenCode, Cursor, Qoder, and Codex (IDE & CLI)
rem ==============================================================================

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "KIT_INSTALLER=%SCRIPT_DIR%scripts\kit_installer.py"

rem Verify Python is available
where python >nul 2>nul
if %errorlevel% equ 0 (
    set "PY_CMD=python"
    goto :RUN_INSTALLER
)

where py >nul 2>nul
if %errorlevel% equ 0 (
    set "PY_CMD=py -3"
    goto :RUN_INSTALLER
)

echo [ERROR] Python 3 was not found in your PATH.
echo Please install Python 3 (https://python.org or 'winget install Python.Python.3.11').
echo.
pause
exit /b 1

:RUN_INSTALLER
if exist "%KIT_INSTALLER%" (
    %PY_CMD% "%KIT_INSTALLER%" %*
) else (
    set "DEFAULT_CLONE=%USERPROFILE%\.local\share\xp-multiagent-kit"
    if exist "!DEFAULT_CLONE!\scripts\kit_installer.py" (
        %PY_CMD% "!DEFAULT_CLONE!\scripts\kit_installer.py" %*
    ) else (
        where git >nul 2>nul
        if !errorlevel! equ 0 (
            echo [*] Downloading XP Multi-Agent Kit to !DEFAULT_CLONE!...
            git clone --depth 1 https://github.com/Andrevictor20/xp-multiagent-kit.git "!DEFAULT_CLONE!"
            if exist "!DEFAULT_CLONE!\scripts\kit_installer.py" (
                %PY_CMD% "!DEFAULT_CLONE!\scripts\kit_installer.py" %*
            ) else (
                echo [ERROR] Installation failed.
                pause
                exit /b 1
            )
        ) else (
            echo [ERROR] Cannot locate scripts\kit_installer.py and git is not installed.
            echo Please clone the repository or install Git (https://git-scm.com).
            pause
            exit /b 1
        )
    )
)

endlocal
