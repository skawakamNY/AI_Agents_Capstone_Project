import asyncio
import aiohttp
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from config import GEMINI_API_KEY

# -----------------------------
# Define a simple async function to query the traffic agent MCP server
# -----------------------------
async def traffic_agent_tool(prompt: str) -> str:
    url = "http://127.0.0.1:8000/mcp"  # Traffic Agent MCP endpoint
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"prompt": prompt}) as resp:
            data = await resp.json()
            # Prefer function responses
            frs = data.get("function_responses", [])
            if frs:
                texts = []
                for fr in frs:
                    resp_dict = fr.get("response", {})
                    texts.append(", ".join(f"{k}: {v}" for k, v in resp_dict.items()))
                return " | ".join(texts)
            return data.get("text", "No output")
# -----------------------------
# Run the agent with multiple places
# -----------------------------
async def run_geo_agent(prompt: str) -> str:
    url = "http://127.0.0.1:8001/geo"  # Traffic Agent MCP endpoint
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"prompt": prompt}) as resp:
            parts = await resp.json()
            if parts:
                return parts.get('text', '')

    return "No output"
# -----------------------------
# Create Parent Agent with Gemini LLM
# -----------------------------
parent_model = Gemini(model_name="gemini-2.0-flash", api_key=GEMINI_API_KEY)

parent_agent = Agent(
    name="parent_agent",
    model=parent_model,
    tools=[run_geo_agent, traffic_agent_tool],
)

runner = InMemoryRunner(parent_agent)

# -----------------------------
# Run Parent Agent
# -----------------------------
async def run_parent_agent(prompt: str) -> str:
    events = await runner.run_debug(prompt)
    # Extract the last text output from the events
    for e in reversed(events):
        for part in getattr(e.content, "parts", []):
            if hasattr(part, "text"):
                return part.text
            elif hasattr(part, "function_response"):
                resp = part.function_response.response
                return " | ".join(f"{k}: {v}" for k, v in resp.items())
    return "No output"

async def main():
    prompt = "How is traffic near JFK airport and Madison Squre Garden"
    result = await run_parent_agent(prompt)
    print("Parent Agent Result:\n", result)

if __name__ == "__main__":
    asyncio.run(main())
