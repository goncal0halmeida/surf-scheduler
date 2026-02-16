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


@mcp.tool()
def get_surf_spots_coordinates() -> str:
    """Get Lisbon surf spots with coordinates.

    Returns: JSON with spot names as keys, each containing 'lat' and 'long'.
    Example: {"Carcavelos": {"lat": 38.6756, "long": -9.3378}}
    """
    surfspots_path = (
        Path(__file__).parent / "surf-spots.json"
    )  # Load from local JSON file
    with open(surfspots_path, "r") as f:
        return f.read()


@mcp.tool()
def get_surf_preferences() -> str:
    """Get user's surf preferences.

    Returns: JSON with waveHeight (min/max/preferred), preferredBeaches (weekday/weekend),
    sessionTimes (weekday/weekend), and skillLevel.
    """
    surf_preferences_path = (
        Path(__file__).parent / "surf-preferences.json"
    )  # Load from local JSON file
    with open(surf_preferences_path, "r") as f:
        return f.read()


@mcp.tool()
def get_wave_forecast_week(
    lat: str,
    lng: str,
):
    """Get 7-day wave forecast for a surf spot.

    Args:
        lat: Latitude (e.g., "38.6756")
        lng: Longitude (e.g., "-9.3378")

    Returns: JSON with daily arrays (synchronized by index):
        - time: ISO8601 dates
        - wave_height_max: meters (m)
        - wave_direction_dominant: degrees (0°=N, clockwise)
        - wave_period_max: seconds (higher=better quality, 12-20s ideal)
    """
    logger.info(
        f"--- 🛠️ Tool: get_wave_forecast_week called for the coordinates {lat}, {lng} ---"
    )

    try:
        response = httpx.get(
            f"https://marine-api.open-meteo.com/v1/marine",
            params={
                "latitude": float(lat),
                "longitude": float(lng),
                "daily": ",".join(
                    ["wave_height_max", "wave_direction_dominant", "wave_period_max"]
                ),
            },
        )
        response.raise_for_status()

        data = response.json()
        if "latitude" not in data:
            logger.error(f"❌ latitude not found in response: {data}")
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
def get_wind_forecast_week(
    lat: str,
    lng: str,
):
    """Get 7-day wind forecast for a surf spot.

    Args:
        lat: Latitude (e.g., "38.6756")
        lng: Longitude (e.g., "-9.3378")

    Returns: JSON with daily arrays (synchronized by index):
        - time: ISO8601 dates
        - wind_speed_10m_max: km/h (ideal <15, blown out >25)
        - wind_direction_10m_dominant: degrees (0°=N, wind FROM direction)
        - wind_gusts_10m_max: km/h

    For Lisbon (west-facing): Offshore winds 90°-180° (ideal), Onshore 225°-315° (avoid).
    """
    logger.info(
        f"--- 🛠️ Tool: get_wind_forecast_week called for the coordinates {lat}, {lng} ---"
    )

    try:
        response = httpx.get(
            f"https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": float(lat),
                "longitude": float(lng),
                "daily": ",".join(
                    [
                        "wind_speed_10m_max",
                        "wind_gusts_10m_max",
                        "wind_direction_10m_dominant",
                    ]
                ),
            },
        )
        response.raise_for_status()

        data = response.json()
        if "latitude" not in data:
            logger.error(f"❌ latitude not found in response: {data}")
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
def get_daily_tide_forecast():
    """Get hourly tide forecast for Lisbon (7 days).

    Returns: JSON with hourly sea_level_height_msl in meters.
    Low tide = powerful/close to shore. High tide = cleaner/further out.
    Mid-incoming/outgoing often ideal.
    """
    logger.info(f"--- 🛠️ Tool: get_tide_forecast_week called for Lisbon ---")

    try:
        response = httpx.get(
            f"https://marine-api.open-meteo.com/v1/marine",
            params={
                "latitude": 38.6756,
                "longitude": -9.3378,
                "hourly": "sea_level_height_msl",
            },
        )
        response.raise_for_status()

        data = response.json()
        if "latitude" not in data:
            logger.error(f"❌ latitude not found in response: {data}")
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
