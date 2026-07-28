# vroidstudio-mcp (MCPB Bundle)

VRoid Studio brute-force automation via pywinauto-mcp — 55 archetypes, state machine, verification.

## Usage

Add to \claude_desktop_config.json\:
\\\json
{
  "mcpServers": {
    "vroidstudio-mcp": {
      "command": "uv",
      "args": ["run", "--directory", "\D:\Dev\repos", "python", "-m", "vroidstudio_mcp"],
      "env": { "PYTHONPATH": "\D:\Dev\repos/src" }
    }
  }
}
\\\

## Tools

- **vroid_studio**: vroid_studio

## Requirements

- Python 3.12+
- uv
