import asyncio

from fastmcp import Client


async def test_server():
    # Test the MCP server using streamable-http transport.
    # Use "/sse" endpoint if using sse transport.
    async with Client("http://localhost:8080/mcp") as client:
        # List available tools
        tools = await client.list_tools()
        for tool in tools:
            print(f"--- 🛠️  Tool found: {tool.name} ---")
        # Call get_exchange_rate tool
        print("--- 🪛  Calling get_wave_forecast_week tool for Carcavelos ---")
        # print("--- 🪛  Calling get_tide_forecast_week tool for Lisbon ---")
        result = await client.call_tool(
            "get_wave_forecast_week", {"lat": "38.6756", "lng": "-9.3378"}
            # "get_tide_forecast_week" 
        )
        result1 = await client.call_tool(
            "get_wind_forecast_week", {"lat": "38.6756", "lng": "-9.3378"}
            # "get_tide_forecast_week" 
        )
        print(f"--- ✅  Success: {result.content[0].text} ---")
        print(f"--- ✅  Success: {result1.content[0].text} ---")
        # print("--- 🪛  Calling  resource get_surf_spots_coordinates ---")
        # content = await client.read_resource("data://surf-spots-coordinates")
        #
        # for item in content:
        #     if hasattr(item, 'text'):
        #         print(f"Text content: {item.text}")
        #         print(f"MIME type: {item.mimeType}")
        #
        # print("--- 🪛  Calling  resource get_surf_preferences ---")
        # content = await client.read_resource("data://surf-preferences")
        #
        # for item in content:
        #     if hasattr(item, 'text'):
        #         print(f"Text content: {item.text}")
        #         print(f"MIME type: {item.mimeType}")
if __name__ == "__main__":
    asyncio.run(test_server())
