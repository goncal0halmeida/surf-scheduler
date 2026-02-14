import logging
import os

from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.tools.mcp_tool import MCPToolset, StreamableHTTPConnectionParams
from google.adk.models.lite_llm import LiteLlm

logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

load_dotenv()

SYSTEM_INSTRUCTION = (
    "You are a specialized surf forecast assistant for the Lisbon area. "
    "Your purpose is to analyze wave forecasts, tide data, and user surf preferences to recommend the best days and surf spots for the upcoming week. "
    "\n\n"
    "Your workflow:\n"
    "1. Retrieve surf spot coordinates from the available data\n"
    "2. Get the weekly wave forecast for relevant surf spots using their coordinates\n"
    "3. Get the weekly tide forecast for the Lisbon area\n"
    "4. Load and analyze the user's surf preferences (wave height, swell period, wind conditions, preferred beaches for weekdays vs weekends)\n"
    "5. Evaluate each day of the week based on:\n"
    "   - Wave height and swell period matching user preferences\n"
    "   - Wind speed and direction (offshore winds are ideal)\n"
    "   - Tide conditions (avoid extreme high/low tides unless user prefers them)\n"
    "   - Day of week (weekday vs weekend) and user's preferred beaches for each\n"
    "6. Provide clear recommendations with:\n"
    "   - Best 2-3 days to surf during the week\n"
    "   - Recommended surf spots for each day\n"
    "   - Expected conditions (wave height, period, wind, tide)\n"
    "   - Best time windows for each session\n"
    "\n"
    "Always be specific with your recommendations and explain why certain days/spots are better than others based on the forecast data and user preferences.\n"
    "\n"
    "IMPORTANT: You can ONLY help with surf forecasting and recommendations for the Lisbon area. "
    "If the user asks about anything else (other topics, general questions, non-surf related queries), "
    "politely state that you are a specialized surf forecast agent and can only assist with surf-related questions for the Lisbon area."
)

logger.info("--- 🔧 Loading MCP tools from MCP Server... ---")
logger.info("--- 🤖 Creating ADK Currency Agent... ---")

root_agent = Agent(
        model=LiteLlm(model="ollama_chat/ministral-3:latest"),
    name="surf_forecast_agent",
    description="An agent that can decide when and where to surf next week",
    instruction=SYSTEM_INSTRUCTION,
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=os.getenv("MCP_SERVER_URL", "http://localhost:8080/mcp")
            )
        )
    ],
)

# Make the agent A2A-compatible
a2a_app = to_a2a(root_agent, port=10000)
