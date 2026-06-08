import asyncio
from vroidstudio_mcp.automation import _extract_handle
from vroidstudio_mcp.pywinauto_client import windows


async def main() -> None:
    r = await windows("find", title="VRoid Studio")
    print("raw:", r)
    print("handle:", _extract_handle(r))


asyncio.run(main())
