# Multi-Agent AI Travel Guide System

This project is a premium multi-agent travel guide planner built using **FastAPI**, **LangChain**, **LangGraph**, and **OpenRouter** (configured with fast free cloud LLM models like `meta-llama/llama-3-8b-instruct:free` by default).

The system delegates travel planning tasks to 9 specialized agents, coordinated by a central **Supervisor Agent**:
1. **Destination Agent**: Researches sightseeing spots and attractions.
2. **Weather Agent**: Retrieves live conditions and evaluates travel comfort.
3. **Transport Agent**: Recommends transit methods (train, bus, flights, cabs).
4. **Hotel Agent**: Suggests the best stay neighborhoods.
5. **Food Agent**: Explores local cuisine and dining spots.
6. **Budget Agent**: Performs programmatic budget cost calculations.
7. **Itinerary Agent**: Creates realistic day-wise schedules.
8. **Booking Link Agent**: Supplies direct booking/search links for hotels and transport.
9. **Safety Agent**: Recommends safety guidelines and checklists.

---

## Setup & Installation

### 1. Create a Virtual Environment
Navigate to the `travel_multi_agent/` directory:
```bash
python -m venv venv
```

**Activate it:**
- **On Windows (PowerShell):**
  ```powershell
  venv\Scripts\activate
  ```
- **On macOS/Linux:**
  ```bash
  source venv/bin/activate
  ```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Create `.env` file
Configure your API keys in the `.env` file at the root of `travel_multi_agent/`:
```env
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=meta-llama/llama-3-8b-instruct:free
TAVILY_API_KEY=your_tavily_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
APP_NAME=AI Travel Guide Agent
```

---

## How to Run

### 1. Run Backend & Frontend Together (Recommended)
You can start both the FastAPI backend server and the Streamlit frontend together with a single command:
```bash
python run.py
```
This launches:
- FastAPI Backend on [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Streamlit Frontend on [http://localhost:8501](http://localhost:8501)

Press `Ctrl+C` in that terminal to cleanly shut down both servers.

### 2. Run Individually
If you prefer to run them in separate terminals:

#### A. Run the FastAPI Server
Launch the backend server:
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- Interactive Swagger docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

#### B. Run the Streamlit Web Frontend
Open the visual dashboard:
```bash
streamlit run frontend/streamlit_app.py
```

### 3. Run the Interactive CLI Chat
Run the system inside your console:
```bash
python cli.py
```

---

## Testing Endpoints with PowerShell

### A. Test Chat Endpoint (`/chat`)
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/chat" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"message":"Plan a 3-day trip to Jaipur from Delhi for 2 people under 15000. Include weather, transport, places, food, stay, budget, safety and itinerary."}'
```

### B. Test Full Plan Endpoint (`/plan-trip`)
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/plan-trip" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"source":"Delhi","destination":"Jaipur","days":3,"people":2,"budget":"15000","interests":"history, food, photography","travel_style":"budget","food_preference":"vegetarian"}'
```

### C. Test Individual Agent Endpoint (`/agent-test`)
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/agent-test" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"agent":"weather","query":"Weather in Manali right now"}'
```

### D. Test Ready-to-Go Plan Endpoint (`/ready-to-go-plan`)
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/ready-to-go-plan" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"source":"Delhi","destination":"Jaipur","days":3,"people":2,"budget":"15000","interests":"history, food, photography","travel_style":"budget","food_preference":"vegetarian","travel_date":"2026-07-10"}'
```

---

## Streaming Endpoints & Server-Sent Events (SSE)

The system supports real-time Server-Sent Events (SSE) chunk streaming. By default, streaming endpoints hide the internal agent execution flow and show only the final generated travel plan content like ChatGPT.

To debug the agent execution flow on the frontend and see progress events, you can set the environment variable:
```env
SHOW_AGENT_PROGRESS=true
```

### 1. Streaming Endpoints
All streaming endpoints accept a `POST` request and return a `text/event-stream` content type:
- `POST /chat/stream`: Streams conversational plans based on freeform user query (`ChatRequest`).
- `POST /plan-trip/stream`: Streams trip plans using pre-extracted parameters (`PlanTripRequest`).
- `POST /ready-to-go-plan/stream`: Streams comprehensive booking plans including checklist and direct search links (`ReadyToGoRequest`).

### 2. SSE Protocol Event Structure
When `SHOW_AGENT_PROGRESS=false` (Default):
- Only the final answer text/content is streamed to the user.
- Allowed frontend events are:
  - `event: start` -> data: `{"message": "Generating your travel plan..."}`
  - `event: token` -> data: `{"content": "..."}`
  - `event: final` -> data: `{"trace_id": "..."}`
  - `event: error` -> data: `{"agent": "...", "message": "..."}`
  - `event: done` -> data: `{"status": "completed"}`

When `SHOW_AGENT_PROGRESS=true` (Debug Mode):
- The backend yields progress details about active agents.
- Event structure also includes `progress` events indicating agent lifecycle states:
  - `event: progress` -> data: `{"agent": "destination", "status": "started|completed|failed", "message": "..."}`

### 3. How to Test & Verify Streaming

#### A. Streamlit Web Dashboard
Run the dashboard and click **Stream Plan ⚡** to see agents color-code live and text stream word-by-word:
```bash
streamlit run frontend/streamlit_app.py
```

#### B. HTML Browser Client
Open `frontend/streaming_demo.html` in your browser. This web page uses vanilla Javascript and HTML to read, decode, and print the event-stream dynamically.

#### C. Curl Command Line Test (Windows/macOS/Linux)
Test real-time terminal output using curl (`curl.exe` on PowerShell):
```bash
curl.exe -N -X POST http://127.0.0.1:8000/chat/stream `
  -H "Content-Type: application/json" `
  -d '{"message":"Plan a 2-day budget trip to Jaipur from Delhi"}'
```

---


## Langfuse Tracing Setup

1. Go to [Langfuse Cloud](https://cloud.langfuse.com).
2. Create a project.
3. Copy your **Public Key** and **Secret Key**.
4. Add them to your `.env` file:
   ```env
   LANGFUSE_PUBLIC_KEY=your_public_key
   LANGFUSE_SECRET_KEY=your_secret_key
   LANGFUSE_HOST=https://cloud.langfuse.com
   LANGFUSE_ENABLED=true
   ```
5. Run the app:
   ```bash
   uvicorn app.main:app --reload
   ```
6. Make a request to `/ready-to-go-plan` (see test command below).
7. Open your Langfuse dashboard.
8. You should see a trace named:
   **`travel_plan_request`**

### Expected Trace Flow Tree
```
travel_plan_request
└── supervisor_agent
    ├── destination_agent
    │   └── tavily_web_search
    ├── weather_agent
    │   └── openweather_api_call
    ├── transport_agent
    │   └── tavily_web_search
    ├── hotel_agent
    │   └── tavily_web_search
    ├── food_agent
    │   └── tavily_web_search
    ├── budget_agent
    ├── itinerary_agent
    ├── booking_link_agent
    │   └── booking_link_generation
    ├── safety_agent
    │   └── tavily_web_search
    └── final_merge
```

---

## Testing Examples & Tracing Verification

Try querying the system with:
- `Weather in Manali right now`
- `Best places to visit in Jaipur`
- `How to reach Rishikesh from Delhi`
- `Famous vegetarian food in Amritsar`
- `Suggest budget stay areas in Manali`
- `Plan a 3-day Jaipur trip from Delhi for 2 people under 15000`
- `Make a 2-day Mussoorie itinerary for friends`
- `Latest travel updates for Himachal`

### Final Tracing Testing Command (PowerShell)

To verify tracing is working fully across all components, invoke the `/ready-to-go-plan` endpoint:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/ready-to-go-plan" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"source":"Delhi","destination":"Jaipur","days":3,"people":2,"budget":"15000","interests":"history, food, photography","travel_style":"budget","food_preference":"vegetarian","travel_date":"2026-07-10"}'
```

**Expected Response format:**
- `ready_to_go_plan` is generated.
- `agents_used` lists all utilized agents.
- `trace_id` is returned.

Check the Langfuse dashboard to confirm that all agent spans, tool calls, and final merges are nested and visible in the trace tree.

# travel-multi-agent-
