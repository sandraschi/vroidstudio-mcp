param(
    [switch]$Headless,
    [switch]$BackendOnly,
    [switch]$FrontendOnly,
    [switch]$NoBrowser
)

$WebappStart = Join-Path $PSScriptRoot "web_sota\start.ps1"
if (-not (Test-Path $WebappStart)) {
    Write-Host "Missing web_sota/start.ps1" -ForegroundColor Red
    exit 1
}

& $WebappStart @PSBoundParameters
exit $LASTEXITCODE
