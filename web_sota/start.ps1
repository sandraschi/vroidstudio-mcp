param(
    [switch]$Headless,
    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [switch]$NoBrowser
)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$FleetStartPath = Join-Path $ProjectRoot "scripts\FleetStartMode.ps1"
if (-not (Test-Path -LiteralPath $FleetStartPath)) {
    Write-Host "ERROR: Missing vendored launcher helper: $FleetStartPath" -ForegroundColor Red
    exit 1
}
. $FleetStartPath
$FleetStart = Initialize-FleetStartMode @PSBoundParameters
Enter-FleetHeadlessConsole -Headless:$Headless -BackendOnly:$BackendOnly

$WebPort = 10880
$BackendPort = 10881
$WebappDir = Join-Path $ProjectRoot "webapp"

Stop-FleetPortSquatters -Ports @($WebPort, $BackendPort) -Label "vroidstudio-mcp"

if (-not (Assert-FleetPortsAvailable -Ports @($WebPort, $BackendPort) -Label "vroidstudio-mcp")) { exit 1 }

if ($FleetStart.RunBackend) {
    Write-Host "Starting vroidstudio-mcp backend on port $BackendPort ..." -ForegroundColor Cyan
    $backendCmd = @"
`$env:VROIDSTUDIO_MCP_PORT = '$BackendPort'
Set-Location '$ProjectRoot'
uv run vroidstudio-mcp
"@
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd -WorkingDirectory $ProjectRoot -WindowStyle Normal

    $healthUrl = "http://127.0.0.1:$BackendPort/health"
    for ($i = 0; $i -lt 60; $i++) {
        try {
            $null = Invoke-WebRequest -Uri $healthUrl -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
            break
        } catch {
            Start-Sleep -Seconds 1
        }
    }
}

if (-not $FleetStart.RunFrontend) { return }

if (-not (Test-Path $WebappDir)) {
    Write-Host "Missing webapp directory: $WebappDir" -ForegroundColor Red
    exit 1
}

Set-Location $WebappDir
if (-not (Test-Path "node_modules")) { npm install }

Write-Host "Starting Vite frontend on port $WebPort ..." -ForegroundColor Green
npm run dev -- --port $WebPort --host 127.0.0.1


