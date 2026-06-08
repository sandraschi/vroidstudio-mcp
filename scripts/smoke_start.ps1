# Start fleet backends for smoke_e2e.py (no frontends)
param()

$ErrorActionPreference = "Stop"

function Start-BackendHidden {
    param([string]$Label, [string]$WorkDir, [string]$Command)
    Write-Host "Starting $Label ..." -ForegroundColor Cyan
    Start-Process pwsh -ArgumentList "-NoProfile", "-Command", $Command -WorkingDirectory $WorkDir -WindowStyle Hidden
}

$PywinautoRoot = "D:\Dev\repos\pywinauto-mcp"
$VroidRoot = "D:\Dev\repos\vroidstudio-mcp"
$SysAdminRoot = "D:\Dev\repos\system-admin-mcp"

$srcPath = Join-Path $PywinautoRoot "src"
Start-BackendHidden -Label "cua-mcp :10789" -WorkDir $PywinautoRoot -Command @"
`$env:PYTHONPATH = '$srcPath'
Set-Location '$PywinautoRoot'
uv run uvicorn pywinauto_mcp.server:app --host 127.0.0.1 --port 10789 --log-level warning
"@

Start-Sleep -Seconds 2

Start-BackendHidden -Label "vroidstudio-mcp :10881" -WorkDir $VroidRoot -Command @"
`$env:VROIDSTUDIO_MCP_PORT = '10881'
Set-Location '$VroidRoot'
uv run vroidstudio-mcp
"@

Start-Sleep -Seconds 1
$sysSrc = Join-Path $SysAdminRoot "src"
Start-BackendHidden -Label "system-admin-mcp :10861" -WorkDir $SysAdminRoot -Command @"
`$env:PYTHONPATH = '$sysSrc'
Set-Location '$SysAdminRoot'
uv run uvicorn system_admin_mcp.server:app --host 127.0.0.1 --port 10861 --log-level warning
"@

Write-Host "Waiting for health endpoints (60s max) ..." -ForegroundColor Yellow
$urls = @(
    "http://127.0.0.1:10789/api/v1/health",
    "http://127.0.0.1:10881/health"
)
$urls += "http://127.0.0.1:10861/api/health"

foreach ($url in $urls) {
    $ready = $false
    for ($i = 0; $i -lt 60; $i++) {
        try {
            $null = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 2
            Write-Host "  up  $url" -ForegroundColor Green
            $ready = $true
            break
        } catch {
            Start-Sleep -Seconds 1
        }
    }
    if (-not $ready) {
        Write-Host "  down $url" -ForegroundColor Red
        exit 1
    }
}

Write-Host "Backends ready. Run: uv run python scripts/smoke_e2e.py" -ForegroundColor Green
