from aiohttp import web, ClientSession
from typing import List, Dict
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from config import GEMINI_API_KEY
# -----------------------------
# Async tool function to get lat/lon from place names
# -----------------------------
async def geocode_places(place_names: List[str]) -> Dict[str, Dict[str, str]]:
    """
    Return latitude and longitude for a list of place names using Nominatim API.
    """
    results = {}
    async with ClientSession() as session:
        for place in place_names:
            url = "https://nominatim.openstreetmap.org/search"
            params = {"q": place, "format": "json", "limit": 1}
            async with session.get(url, params=params) as resp:
                if resp.status != 200:
                    results[place] = {"error": f"HTTP {resp.status}"}
                    continue
                data = await resp.json()
                if not data:
                    results[place] = {"error": "Place not found"}
                    continue
                results[place] = {"lat": data[0]["lat"], "lon": data[0]["lon"]}
    return results

# -----------------------------
# Create LLM agent
# -----------------------------
model = Gemini(model_name="gemini-2.0-flash", api_key=GEMINI_API_KEY)

geo_agent = Agent(
    name="geo_agent",
    model=model,
    tools=[geocode_places],
)

runner = InMemoryRunner(geo_agent)
# -----------------------------
# Run the agent with multiple places
# -----------------------------
async def run_geo_agent(prompt: str) -> str:
    events = await runner.run_debug(prompt)
    for e in reversed(events):
        for part in getattr(e.content, "parts", []):
            if hasattr(part, "text") and part.text:
                return part.text
    return "No output"
# -----------------------------
# HTTP server for MCP
# -----------------------------
async def mcp_handler(request):
    data = await request.json()
    prompt = data.get("prompt", "")
    text = await run_geo_agent(prompt)
    return web.json_response({
        "text": text
    })

app = web.Application()
app.router.add_post("/geo", mcp_handler)  # endpoint is /geo

if __name__ == "__main__":
    print("🚀 Traffic Agent MCP server running on http://127.0.0.1:8001/geo")
    web.run_app(app, host="127.0.0.1", port=8001)
