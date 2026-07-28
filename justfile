set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]
import 'scripts/just/fleet.just'

# ── Dashboard ─────────────────────────────────────────────────────────────────

# Open the interactive recipe dashboard in the browser
default:
    @just --list

# ── Environment ────────────────────────────────────────────────────────────────

# Sync Python deps from pyproject.toml
sync:
    Set-Location '{{justfile_directory()}}'; uv sync

# ── Development ──────────────────────────────────────────────────────────────

# Run MCP server over stdio
mcp:
    Set-Location '{{justfile_directory()}}'; uv run vroidstudio-mcp

# Start backend + frontend
web:
    Set-Location '{{justfile_directory()}}'; powershell.exe -NoProfile -File .\start.ps1

# Frontend only
frontend:
    Set-Location '{{justfile_directory()}}\webapp'; npm run dev

# ── Quality ───────────────────────────────────────────────────────────────────

# Python lint
lint:
    Set-Location '{{justfile_directory()}}'; uv run ruff check .

# Auto-fix
fix:
    Set-Location '{{justfile_directory()}}'; uv run ruff check . --fix --unsafe-fixes
    Set-Location '{{justfile_directory()}}'; uv run ruff format .

# ── Testing ───────────────────────────────────────────────────────────────────

# Run tests
test:
    Set-Location '{{justfile_directory()}}'; uv run pytest tests/ -v

# ── Security ─────────────────────────────────────────────────────────────────

# Bandit scan
check-sec:
    Set-Location '{{justfile_directory()}}'; uv run bandit -r src/

# ── Tauri NSIS ─────────────────────────────────────────────────────────────────

# Build the PyInstaller backend .exe and copy to Tauri resources
build-sidecar:
    powershell.exe -NoProfile -File native\build-sidecar.ps1

# Build the Tauri NSIS desktop installer
build-native: build-sidecar
    $env:Path = "$env:USERPROFILE\.cargo\bin;$env:Path"
    $vcvars = "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
    $envOutput = cmd /c "`"$vcvars`" > nul & set" | Where-Object { $_ -match '^(INCLUDE|LIB|LIBPATH|VCToolsVersion|WindowsSdkDir|UniversalCRTSdkDir|UCRTVersion)=' }
    foreach ($line in $envOutput) { $parts = $line.Split('=', 2); Set-Item -Path "env:$($parts[0])" -Value $parts[1] -ErrorAction SilentlyContinue }
    Set-Location '{{justfile_directory()}}\native'
    npx @tauri-apps/cli build --bundles nsis

