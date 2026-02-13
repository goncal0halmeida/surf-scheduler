import asyncio
import json
import logging
import os
from pathlib import Path

import arrow
import httpx
from fastmcp import FastMCP

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

mcp = FastMCP("Surf Scheduler MCP Server 🌊")

@mcp.resource("data://surf-spots-coordinates")
def get_surf_spots_coordinates() -> str:
    """Provides surf spots coordinates as JSON."""
    surfspots_path = Path(__file__).parent / "surfspots.json"
    with open(surfspots_path, 'r') as f:
        return f.read()

@mcp.tool()
def get_wave_forecast_week(
    lat: str,
    lng: str,
):
    """Use this to get wave forecast for a surf spot for the week.

    Args:
        lat: Latitute of the surf spot.
        lng: Longitude of the surf spot.

    Returns:
        The data object contains the actual wave forecast data on an hourly basis for a whole week or an error message if the request fails.
    """
    logger.info(
            f"--- 🛠️ Tool: get_wave_forecast_week called for the coordinates {lat}, {lng} ---"
    )

    # Get 8:00 timestamp of next monday
    start = arrow.now().shift(weekday=0).replace(hour=8, minute=0, second=0)
    
    # Get 18:00 timestamp of next sunday
    end = start.shift(days=6).replace(hour=18, minute=0, second=0)

    try:
        response = httpx.get(
            f"https://api.stormglass.io/v2/weather/point",
            params={
                'lat': float(lat),
                'lng': float(lng),
                'params': ','.join([
                    'swellHeight',
                    'swellPeriod',
                    'swellDirection',
                    'secondarySwellHeight',
                    'secondarySwellPeriod',
                    'secondarySwellDirection',
                    'waveHeight',
                    'wavePeriod',
                    'waveDirection',
                    'windSpeed',
                    'windDirection',
                    'windWaveHeight',
                    'windWavePeriod'
                ]),
                'start': start.to('UTC').timestamp(),  # Convert to UTC timestamp
                'end': end.to('UTC').timestamp(),  # Convert to UTC timestamp
                'source': 'sg' # SG - Storm Glass AI
            },
            headers={
                'Authorization': os.getenv('STORMGLASS_API_KEY')
            }
        )
        response.raise_for_status()

        data = response.json()
        if "hours" not in data:
            logger.error(f"❌ hours not found in response: {data}")
            return {"error": "Invalid API response format."}
        logger.info(f"✅ API response: {data}")
        return data
    except httpx.HTTPError as e:
        logger.error(f"❌ API request failed: {e}")
        return {"error": f"API request failed: {e}"}
    except ValueError:
        logger.error("❌ Invalid JSON response from API")
        return {"error": "Invalid JSON response from API."}

@mcp.tool()
def get_tide_forecast_week():
    """Use this to get the tide forecast for the Lisbon area for the week.

    Returns:
        Retrieve information about high and low tide times and the corresponding relative sea level in meters for the Lisbon area. If nothing is specified, the returned values will be in relative to Mean Sea Level - MSL.    """
    logger.info(
            f"--- 🛠️ Tool: get_tide_forecast_week called for Lisbon ---"
    )

    # Approximate center coordinates for Lisbon area surf spots
    # This covers Carcavelos, Guincho, Ericeira, Caparica, and surrounding areas
    lat = 38.705217
    lng = -9.494883

    # Get start of next Monday (midnight)
    start = arrow.now().shift(weekday=0).floor('day')
    
    # Get end of next Sunday (midnight of the following Monday)
    end = start.shift(days=7).floor('day')

    try:
        response = httpx.get(
            f"https://api.stormglass.io/v2/tide/extremes/point",
            params={
                'lat': float(lat),
                'lng': float(lng),
                'start': start.to('UTC').timestamp(),  # Convert to UTC timestamp
                'end': end.to('UTC').timestamp(),  # Convert to UTC timestamp
            },
            headers={
                'Authorization': os.getenv('STORMGLASS_API_KEY')
            }
        )
        response.raise_for_status()

        data = response.json()
        if "data" not in data:
            logger.error(f"❌ data not found in response: {data}")
            return {"error": "Invalid API response format."}
        logger.info(f"✅ API response: {data}")
        return data
    except httpx.HTTPError as e:
        logger.error(f"❌ API request failed: {e}")
        return {"error": f"API request failed: {e}"}
    except ValueError:
        logger.error("❌ Invalid JSON response from API")
        return {"error": "Invalid JSON response from API."}



if __name__ == "__main__":
    logger.info(f"🚀 MCP server started on port {os.getenv('PORT', 8080)}")
    # Could also use 'sse' transport, host="0.0.0.0" required for Cloud Run.
    asyncio.run(
        mcp.run_async(
            transport="http",
            host="0.0.0.0",
            port=os.getenv("PORT", 8080),
        )
    )
