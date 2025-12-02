## **Introduction**

This project implements an agent-based traffic information application that responds with real-time traffic updates based on a name of place or address provided by user. The application combines multiple specialized agents—such as a Geo Agent for converting name of place or address into precise latitude and longitude coordinates, and a Traffic Agent that queries live traffic data from external providers like TomTom. An Orchestrator Agent manages the workflow: it receives a natural-language request from the user, forwards it to the Geo Agent to resolve the location, sends the resulting coordinates to the Traffic Agent for traffic flow, ETA, or incident data, and finally summarizes the results into an easy-to-understand response. This multi-agent architecture interprets the user’s prompt and leverages an LLM to determine when and how to interact with other agents, gathering the necessary information before delivering a clear and accurate response.

## **Architecture**

The application is built on a modular, multi-agent architecture designed to provide real-time traffic insights from user-specified locations. At the core, a Orchestrator Agent interprets user queries and coordinates with specialized sub-agents to gather the necessary information. These sub-agents—such as the Geolocation Agent and the Traffic Data Agent—are responsible for resolving place names into precise coordinates and retrieving live traffic conditions from external APIs.

## **Flowchart**
                       ┌──────────────────────────┐
                       │        User Input        │
                       │  (Place name, query)     │
                       └─────────────┬────────────┘
                                     │
                                     ▼
                       ┌──────────────────────────┐
                       │  Orchestrator LLM Agent  │
                       │  - Interprets intent     │
                       │  - Determines tool use   │
                       └─────────────┬────────────┘
                                     │
                ┌────────────────────┼──────────────────────┐
                │                                           │
                ▼                                           ▼
     ┌──────────────────┐                          ┌──────────────────┐
     │  Geo Agent       │                          │ Traffic Agent    │
     │  - Name → Lat/Lon│                          │  - Traffic flow  │
     │                  │                          │  - Incidents     │
     └───────────┬──────┘                          └──────────┬───────┘
                 │                                            │
                 ▼                                            ▼
    ┌──────────────────────┐                      ┌──────────────────────┐
    │  Coordinates Output  │                      │   Traffic Data       │          
    │  (lat, lon)          │                      │ (speed, ETA, events) │
    └──────────┬───────────┘                      └──────────┬───────────┘
               │                                             │
               └───────────────┬────────┴───────────┬────────┘
                               ▼                    ▼
                   ┌────────────────────────────────────────┐
                   │   Orchestrator LLM Aggregation Layer   │
                   │  - Merges results                      │
                   │  - Formats natural-language response   │
                   └───────────────────┬────────────────────┘
                                       │
                                       ▼
                           ┌──────────────────────────┐
                           │        Final Output      │
                           │   (Live traffic summary) │
                           └──────────────────────────┘


## **Components & Responsibilities**
**Orchestrator Agent**
- Receives natural-language requests from the user.
- Uses an LLM to extract intent and decide which sub-agents/tools to call.
- Calls Geo Agent (MCP HTTP) when a place name needs geocoding.
- Calls Traffic Agent (MCP HTTP) with coordinates to fetch flow/ETA/incidents.
- Normalizes and synthesizes tool outputs and returns user-facing text.

**Geo Agent (MCP HTTP)**
- Accepts POST /mcp with {"prompt": "..."}
- Uses an external geocoder (Nominatim or another geocode API) to resolve place names into coordinates.
- Returns structured JSON with both human-readable text and function_responses (structured tool outputs).

**Traffic Agent (MCP HTTP)**
- Accepts POST /mcp with {"prompt": "..."}
- Uses TomTom or custom TomTom client to fetch traffic flow, ETA, incidents.
- Returns structured JSON: {"text": "...", "function_responses": [...]} where function_responses includes name and response keys.

**TomTom client**
- tomtom_client.py — asynchronous client using aiohttp for TomTom REST endpoints (flow, incidents, routing).
- Returns structured dicts, never empty; returns clear status on errors.

**Runner / ADK Layer**
- Each agent uses InMemoryRunner(agent) to run locally and runner.run_debug(prompt) to obtain event-level detail when debugging.
- Agents call out to tools by passing async functions in tools=[...].

**Monitoring & Ops**
- Rate-limit metrics, request counts, error rates, latency histograms.
- Logging of runner.run_debug() events for debugging tool-calls and model decisions.

## **Setup**
- Install all packages listed in the requirements.txt file
- Go to each agent folder and update config.py with your Google API Key and Tomtom API Key (https://www.tomtom.com/)
- Startup Traffic Agent (main.py) and Geocoding Agent (main.py)
- Update prompt for specific location in main function (main.py) and startup Parent (Orchestrator) Agent