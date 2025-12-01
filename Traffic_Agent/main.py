from aiohttp import web
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner

from traffic_tools import tool_get_traffic_flow, tool_get_eta, tool_get_incidents
from config import GEMINI_API_KEY

# -----------------------------
# Create LLM Traffic Agent
# -----------------------------
model = Gemini(model_name="gemini-2.0-flash", api_key=GEMINI_API_KEY)

traffic_agent = Agent(
    name="tomtom_traffic_agent",
    model=model,
    tools=[tool_get_traffic_flow, tool_get_incidents, tool_get_eta],
)

runner = InMemoryRunner(traffic_agent)

async def run_agent(prompt: str):
    events = await runner.run_debug(prompt)
    text_output = ""
    function_responses = []

    for e in events:
        if not e.content or not e.content.parts:
            continue

        for part in e.content.parts:
            # Plain text output
            if getattr(part, "text", None):
                text_output += part.text + " "

            # Tool call / response
            if getattr(part, "function_response", None):
                fr = part.function_response
                function_responses.append({
                    "name": fr.name,
                    "response": fr.response
                })

    text_output = text_output.strip()
    if not text_output:
        text_output = "No output"

    return text_output, function_responses
# -----------------------------
# HTTP server for MCP
# -----------------------------
async def mcp_handler(request):
    data = await request.json()
    prompt = data.get("prompt", "")
    text, funcs = await run_agent(prompt)
    return web.json_response({
        "text": text,
        "function_responses": funcs
    })

app = web.Application()
app.router.add_post("/mcp", mcp_handler)  # endpoint is /mcp

if __name__ == "__main__":
    print("🚀 Traffic Agent MCP server running on http://127.0.0.1:8000/mcp")
    web.run_app(app, host="127.0.0.1", port=8000)
