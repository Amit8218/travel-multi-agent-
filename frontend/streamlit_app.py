import streamlit as st
import requests
import sys
import os
import datetime

# Ensure the parent app directory is in python path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.config import OPENROUTER_MODEL, validate_config, SHOW_AGENT_PROGRESS
from app.workflow.graph import run_workflow

# 1. Page Configuration
st.set_page_config(
    page_title="AI Travel Guide - Multi-Agent Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inject Premium Custom CSS
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Space+Grotesk:wght@400;700&display=swap');

    /* Global Body and Font Settings */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Premium Background */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #020617 100%);
        color: #f8fafc;
    }
    
    /* Header Gradient Style */
    .header-container {
        text-align: center;
        padding: 2.5rem 1rem;
        background: rgba(30, 27, 75, 0.4);
        border-radius: 24px;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 2.5rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
    }
    
    .main-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8 0%, #a855f7 50%, #f43f5e 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .sub-title {
        font-size: 1.2rem;
        color: #94a3b8;
        font-weight: 300;
    }
    
    /* Custom Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.8) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(8px);
    }
    
    /* Input field customization */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div, .stDateInput>div>div>input {
        background-color: rgba(15, 23, 42, 0.6) !important;
        color: #f8fafc !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        transition: all 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus, .stDateInput>div>div>input:focus {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 10px rgba(56, 189, 248, 0.3) !important;
    }
    
    /* Custom Cards for output */
    .result-card {
        background: rgba(30, 41, 59, 0.45);
        border-radius: 20px;
        padding: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(16px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        margin-bottom: 1.5rem;
    }
    
    .agent-pill {
        display: inline-block;
        background: linear-gradient(135deg, #0369a1 0%, #0284c7 100%);
        color: #f0f9ff;
        padding: 6px 14px;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 4px;
        box-shadow: 0 4px 10px rgba(2, 132, 199, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.15);
        text-transform: capitalize;
        transition: transform 0.2s;
    }
    .agent-pill:hover {
        transform: translateY(-2px);
    }
    
    /* Premium Button Style */
    div.stButton > button {
        background: linear-gradient(90deg, #0284c7 0%, #7c3aed 50%, #db2777 100%) !important;
        color: white !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        border: none !important;
        padding: 14px 28px !important;
        border-radius: 12px !important;
        box-shadow: 0 8px 20px rgba(124, 58, 237, 0.35) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 25px rgba(124, 58, 237, 0.5) !important;
    }
    
    div.stButton > button:active {
        transform: translateY(1px) !important;
    }
    
    /* Section dividers */
    .section-title {
        font-family: 'Space Grotesk', sans-serif;
        color: #38bdf8;
        border-bottom: 2px solid rgba(56, 189, 248, 0.2);
        padding-bottom: 0.5rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# 3. Header Segment
st.markdown("""
<div class="header-container">
    <div class="main-title">Ready-to-Go Travel Planner</div>
    <div class="sub-title">Concurrence-Optimized Multi-Agent AI travel bookings and recommendations</div>
</div>
""", unsafe_allow_html=True)

# 4. Config check
missing_keys = validate_config()

# 5. Sidebar - Parameters Panel
st.sidebar.markdown("<h2 style='font-family:Space Grotesk; font-weight:700; color:#38bdf8;'>Configure Trip</h2>", unsafe_allow_html=True)
st.sidebar.write("Specify your trip preferences:")

source = st.sidebar.text_input("Source City", "Delhi")
destination = st.sidebar.text_input("Destination City", "Jaipur")
travel_date_val = st.sidebar.date_input("Travel Date", datetime.date(2026, 7, 10))
travel_date = travel_date_val.strftime("%Y-%m-%d")

days = st.sidebar.number_input("Duration (Days)", min_value=1, max_value=30, value=3, step=1)
people = st.sidebar.number_input("Number of Travelers", min_value=1, max_value=20, value=2, step=1)
budget = st.sidebar.text_input("Budget (e.g. 15000 or 50000 INR)", "15000")
interests = st.sidebar.text_input("Interests (comma separated)", "history, food, photography")
travel_style = st.sidebar.selectbox("Travel Style", ["budget", "medium", "luxury"], index=0)
food_preference = st.sidebar.text_input("Food Preference (optional)", "vegetarian")

st.sidebar.markdown("---")
st.sidebar.write(f"**LLM Model:** `{OPENROUTER_MODEL}`")

# Helper function to extract specific markdown sections
def extract_section(text, header_name):
    try:
        # Match from "## header_name" to the next "## " or end of string
        pattern = rf"(##\s*{header_name}.*?)(?=##|\Z)"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
    except Exception:
        pass
    return ""

# Helper functions for streaming API requests and rendering status pills
def stream_plan_from_api(url, payload):
    import json
    
    try:
        response = requests.post(url, json=payload, stream=True, timeout=300)
        if response.status_code != 200:
            yield "error", {"message": f"Server returned error code {response.status_code}"}
            return
            
        buffer = ""
        for chunk in response.iter_content(chunk_size=512, decode_unicode=True):
            if chunk:
                buffer += chunk
                while "\n\n" in buffer:
                    part, buffer = buffer.split("\n\n", 1)
                    if not part.strip():
                        continue
                    
                    event_type = ""
                    data_json = ""
                    for line in part.split("\n"):
                        if line.startswith("event:"):
                            event_type = line.replace("event:", "").strip()
                        elif line.startswith("data:"):
                            data_json = line.replace("data:", "").strip()
                            
                    if event_type and data_json:
                        try:
                            data = json.loads(data_json)
                            yield event_type, data
                        except Exception:
                            pass
    except Exception as e:
        yield "error", {"message": f"Connection failed: {str(e)}"}

def render_agent_pills(statuses):
    html = '<div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 15px;">'
    for agent, status in statuses.items():
        if status == "completed":
            color = "linear-gradient(135deg, #059669 0%, #10b981 100%)"
            text_color = "#f0fdf4"
            icon = "✅"
        elif status in ["active", "started"]:
            color = "linear-gradient(135deg, #0891b2 0%, #06b6d4 100%)"
            text_color = "#ecfeff"
            icon = "🔄"
        elif status == "failed":
            color = "linear-gradient(135deg, #dc2626 0%, #ef4444 100%)"
            text_color = "#fef2f2"
            icon = "❌"
        else:
            color = "rgba(148, 163, 184, 0.1)"
            text_color = "#94a3b8"
            icon = "⏳"
        html += f'<span class="agent-pill" style="background: {color}; color: {text_color}; border-color: rgba(255,255,255,0.05); margin-right: 5px; margin-bottom: 5px; padding: 4px 10px; border-radius: 20px; font-size: 0.8rem; display: inline-block;">{icon} {agent}</span>'
    html += '</div>'
    return html

# Main Page Flow
if "OPENROUTER_API_KEY" in missing_keys:
    st.error("🔑 **Configuration Error:** `OPENROUTER_API_KEY` is not configured. Please add it to your `.env` file to enable LLM generation.")
else:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(f"""
        <div class="result-card" style="height: 100%;">
            <h3 style="font-family:Space Grotesk; margin-top:0; color:#38bdf8;">Concurrence-Optimized System</h3>
            <p style="color:#94a3b8; font-size:0.95rem; line-height:1.6;">
                This system initiates specialized agents <b>in parallel</b> to fetch weather, search tourist attractions, compare transport routes, and generate verified stay options. A new <b>Booking Link Agent</b> automatically injects direct search links for Booking.com, MakeMyTrip, RedBus, and Agoda without storing credentials or making payments.
            </p>
            <h4 style="color:#e2e8f0; margin-bottom: 8px;">Active Specialized Agents:</h4>
            <span class="agent-pill">supervisor</span>
            <span class="agent-pill">destination</span>
            <span class="agent-pill">weather</span>
            <span class="agent-pill">transport</span>
            <span class="agent-pill">hotel</span>
            <span class="agent-pill">food</span>
            <span class="agent-pill">budget</span>
            <span class="agent-pill">booking_link</span>
            <span class="agent-pill">itinerary</span>
            <span class="agent-pill">safety</span>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="result-card" style="height: 100%; display: flex; flex-direction: column; justify-content: center;">
            <h3 style="font-family:Space Grotesk; margin-top:0; text-align: center; color:#db2777;">Ready-to-Go Travel Pack</h3>
            <p style="color:#94a3b8; text-align: center; font-size:0.95rem; margin-bottom: 1rem;">
                Trigger all agents to retrieve recommendations, build a custom itinerary, generate search links, and stream your final plan progressively.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            generate_btn = st.button("Ready-to-Go Plan 🚀")
        with btn_col2:
            stream_btn = st.button("Stream Plan ⚡")

    if generate_btn:
        st.markdown("---")
        import re
        
        with st.spinner("🔄 Coordinating specialized agents and creating Ready-to-Go Package..."):
            api_url = "http://127.0.0.1:8000/ready-to-go-plan"
            payload = {
                "source": source,
                "destination": destination,
                "days": int(days),
                "people": int(people),
                "budget": budget,
                "interests": interests,
                "travel_style": travel_style,
                "food_preference": food_preference,
                "travel_date": travel_date
            }
            
            plan_data = None
            agents_used = []
            
            try:
                response = requests.post(api_url, json=payload, timeout=180)
                if response.status_code == 200:
                    data = response.json()
                    plan_data = data.get("ready_to_go_plan")
                    agents_used = data.get("agents_used", [])
            except Exception:
                pass
                
            if not plan_data:
                # Fallback to direct python graph execution
                try:
                    res = run_workflow(payload)
                    plan_data = res.get("final_answer")
                    agents_used = res.get("agents_used", [])
                except Exception as ex:
                    st.error(f"❌ Planning Failed: {str(ex)}")
            
            if plan_data:
                st.balloons()
                
                # Show agents used
                st.markdown("### 🤖 Specialized Agents Active")
                pills_html = "".join([f'<span class="agent-pill">{agent}</span>' for agent in agents_used])
                st.markdown(f"<div>{pills_html}</div>", unsafe_allow_html=True)
                st.write("")
                
                # Tabbed presentation
                tab1, tab2, tab3 = st.tabs(["📋 Complete Ready-to-Go Package", "🔗 Booking & Search Links", "✅ Pre-Booking Checklist"])
                
                with tab1:
                    st.markdown(f'<div class="result-card">{plan_data}</div>', unsafe_allow_html=True)
                    
                with tab2:
                    booking_sec = extract_section(plan_data, "9. Booking Links")
                    transport_sec = extract_section(plan_data, "3. Best Transport Options")
                    stay_sec = extract_section(plan_data, "4. Stay Recommendations")
                    
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    st.write("### 🔗 Recommended Booking & Search Resources")
                    st.write("Click these links to manually check prices, timings, and verify listings:")
                    if booking_sec:
                        st.markdown(booking_sec)
                    if transport_sec:
                        st.markdown(transport_sec)
                    if stay_sec:
                        st.markdown(stay_sec)
                    if not (booking_sec or transport_sec or stay_sec):
                        st.info("Direct links are nested inside the complete plan text in Tab 1.")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                with tab3:
                    checklist_sec = extract_section(plan_data, "12. Final Checklist Before Booking")
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    st.write("### 🚨 Essential Verification Steps")
                    if checklist_sec:
                        st.markdown(checklist_sec)
                    else:
                        st.markdown("""
                        - **Verify timings:** Check train/bus/flight schedules.
                        - **Check reviews:** Always verify hotel reviews on multiple sites.
                        - **Cancellation Policy:** Read cancellation guidelines carefully.
                        - **Weather check:** Re-verify local weather forecast 24 hours prior.
                        - **Documents:** Carry valid photo ID proofs.
                        - **Offline maps:** Save map data for offline usage.
                        - **Cash:** Keep some emergency physical cash handy.
                        """)
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error("Could not generate Ready-to-Go plan. Please verify that your API keys are correct and OpenRouter is reachable.")

    if stream_btn:
        st.markdown("---")
        
        if SHOW_AGENT_PROGRESS:
            st.markdown("### ⚡ Live Multi-Agent Execution Progress")
            
            # Initialize agent statuses
            agent_statuses = {
                "supervisor": "pending",
                "destination": "pending",
                "weather": "pending",
                "transport": "pending",
                "hotel": "pending",
                "food": "pending",
                "budget": "pending",
                "itinerary": "pending",
                "booking_link": "pending",
                "safety": "pending",
                "final_merge": "pending"
            }
            
            # UI placeholders
            pills_placeholder = st.empty()
            pills_placeholder.markdown(render_agent_pills(agent_statuses), unsafe_allow_html=True)
            
            status_text = st.empty()
            status_text.info("Connecting to multi-agent stream...")
        else:
            status_text = st.empty()
            status_text.info("Generating your travel plan...")
            
        plan_title = st.empty()
        plan_placeholder = st.empty()
        
        payload = {
            "source": source,
            "destination": destination,
            "days": int(days),
            "people": int(people),
            "budget": budget,
            "interests": interests,
            "travel_style": travel_style,
            "food_preference": food_preference,
            "travel_date": travel_date
        }
        
        api_url = "http://127.0.0.1:8000/ready-to-go-plan/stream"
        
        accumulated_text = ""
        trace_id = None
        agents_used = []
        
        try:
            for event_type, data in stream_plan_from_api(api_url, payload):
                if event_type == "start":
                    if SHOW_AGENT_PROGRESS:
                        status_text.info(f"🔄 Connection active: {data.get('message', 'Processing...')}")
                    else:
                        status_text.info("Generating your travel plan...")
                    
                elif event_type == "progress":
                    if SHOW_AGENT_PROGRESS:
                        agent = data.get("agent")
                        status = data.get("status")
                        if agent in agent_statuses:
                            agent_statuses[agent] = status
                            pills_placeholder.markdown(render_agent_pills(agent_statuses), unsafe_allow_html=True)
                        if status == "started":
                            status_text.info(f"🔄 Running `{agent.capitalize()} Agent`...")
                        elif status == "completed":
                            status_text.success(f"✅ `{agent.capitalize()} Agent` completed!")
                        
                elif event_type == "token":
                    if not accumulated_text:
                        plan_title.markdown("### 📋 Streaming Travel Plan")
                        status_text.empty()
                    accumulated_text += data.get("content", "")
                    plan_placeholder.markdown(f'<div class="result-card">{accumulated_text}</div>', unsafe_allow_html=True)
                    
                elif event_type == "error":
                    agent = data.get("agent", "unknown")
                    msg = data.get("message", "")
                    st.warning(f"⚠️ `{agent.capitalize()}` Alert: {msg}")
                    if SHOW_AGENT_PROGRESS and agent in agent_statuses:
                        agent_statuses[agent] = "failed"
                        pills_placeholder.markdown(render_agent_pills(agent_statuses), unsafe_allow_html=True)
                        
                elif event_type == "final":
                    trace_id = data.get("trace_id")
                    agents_used = data.get("agents_used", [])
                    
                elif event_type == "done":
                    if SHOW_AGENT_PROGRESS:
                        status_text.success("🎉 Trip planning execution finished!")
                    else:
                        status_text.empty()
                    
            if accumulated_text:
                plan_title.empty()
                plan_placeholder.empty()
                st.balloons()
                
                # Tabbed presentation
                tab1, tab2, tab3 = st.tabs(["📋 Complete Ready-to-Go Package", "🔗 Booking & Search Links", "✅ Pre-Booking Checklist"])
                
                with tab1:
                    st.markdown(f'<div class="result-card">{accumulated_text}</div>', unsafe_allow_html=True)
                    
                with tab2:
                    booking_sec = extract_section(accumulated_text, "9. Booking Links")
                    transport_sec = extract_section(accumulated_text, "3. Best Transport Options")
                    stay_sec = extract_section(accumulated_text, "4. Stay Recommendations")
                    
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    st.write("### 🔗 Recommended Booking & Search Resources")
                    st.write("Click these links to manually check prices, timings, and verify listings:")
                    if booking_sec:
                        st.markdown(booking_sec)
                    if transport_sec:
                        st.markdown(transport_sec)
                    if stay_sec:
                        st.markdown(stay_sec)
                    if not (booking_sec or transport_sec or stay_sec):
                        st.info("Direct links are nested inside the complete plan text in Tab 1.")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                with tab3:
                    checklist_sec = extract_section(accumulated_text, "12. Final Checklist Before Booking")
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    st.write("### 🚨 Essential Verification Steps")
                    if checklist_sec:
                        st.markdown(checklist_sec)
                    else:
                        st.markdown("""
                        - **Verify timings:** Check train/bus/flight schedules.
                        - **Check reviews:** Always verify hotel reviews on multiple sites.
                        - **Cancellation Policy:** Read cancellation guidelines carefully.
                        - **Weather check:** Re-verify local weather forecast 24 hours prior.
                        - **Documents:** Carry valid photo ID proofs.
                        - **Offline maps:** Save map data for offline usage.
                        - **Cash:** Keep some emergency physical cash handy.
                        """)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                if trace_id and SHOW_AGENT_PROGRESS:
                    st.info(f"🔗 Langfuse Trace ID: `{trace_id}`")
            else:
                st.error("Could not generate plan content.")
        except Exception as ex:
            st.error(f"❌ Connection or processing failed: {str(ex)}")

