# Per-repo fleet start config for vroidstudio-mcp
# Edit ports/backend target here - start.ps1 is fleet-standard.
@{
    Name         = 'vroidstudio-mcp'
    BackendPort  = 10881
    FrontendPort = 10880
    HealthPath   = '/health'
    WebRoot      = 'D:\Dev\repos\vroidstudio-mcp\web_sota'
    Backend = @{
        Kind          = 'uvicorn'
        UvicornTarget = 'vroidstudio_mcp.server:app'
        SyncExtras    = @('dev')
        Env           = @{ WEB_PORT = '10881' }
    }
    Frontend = @{
        Kind           = 'vite-npm'
        PackageManager = 'npm'
        PortEnvVar     = 'VITE_PORT'
        ApiTargetEnv   = 'VITE_API_TARGET'
    }
}
