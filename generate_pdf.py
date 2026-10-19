import os
import sys
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Custom canvas that performs two-pass rendering to dynamically compute
    and display the total page count in the footer. Also draws running headers,
    footers, and cover page layout templates.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        # Save state for the second pass
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # Page 1: Cover Page layout
        if self._pageNumber == 1:
            # Draw premium left-border colored banners
            self.setFillColor(colors.HexColor('#1E3A8A')) # Primary Deep Blue
            self.rect(0, 0, 18, 792, fill=True, stroke=False)
            self.setFillColor(colors.HexColor('#0D9488')) # Secondary Teal
            self.rect(18, 0, 6, 792, fill=True, stroke=False)
            
            # Subtle accent shape on top-right
            self.setFillColor(colors.HexColor('#F1F5F9')) # Light Gray
            p = self.beginPath()
            p.moveTo(450, 792)
            p.lineTo(612, 792)
            p.lineTo(612, 630)
            p.close()
            self.drawPath(p, fill=True, stroke=False)
            
        else:
            # Pages 2+: Running Header
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor('#4B5563')) # Charcoal Gray
            self.drawString(54, 750, "Multi-Agent AI Travel Guide System")
            self.drawRightString(558, 750, "TECHNICAL DOCUMENTATION & DESIGN MANUAL")
            
            # Header separator line
            self.setStrokeColor(colors.HexColor('#D1D5DB')) # Light Gray
            self.setLineWidth(0.75)
            self.line(54, 742, 558, 742)
            
            # Running Footer
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor('#6B7280')) # Medium Gray
            self.drawString(54, 40, "Confidential - For Development and Review Only")
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(558, 40, page_text)
            
            # Footer separator line
            self.line(54, 52, 558, 52)
            
        self.restoreState()


def make_code_block(code_text, style):
    """
    Helper to wrap code snippets inside a single-cell Table with custom padding,
    borders, and a light background to simulate terminal code blocks.
    """
    formatted_text = code_text.replace("\n", "<br/>").replace(" ", "&nbsp;")
    p = Paragraph(f"<font face='Courier' size='8'>{formatted_text}</font>", style)
    t = Table([[p]], colWidths=[504])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    return t


def build_pdf(filename="Multi-Agent_Travel_Guide_Documentation.pdf"):
    # Target printable area: margins 54 (0.75 in) left/right, 72 (1.0 in) top/bottom
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette Styling
    primary_color = colors.HexColor('#1E3A8A')
    secondary_color = colors.HexColor('#0D9488')
    charcoal = colors.HexColor('#1F2937')
    light_bg = colors.HexColor('#F3F4F6')

    # Define custom typography styles
    style_cover_title = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=34,
        textColor=primary_color,
        spaceAfter=15,
        spaceBefore=120
    )
    
    style_cover_subtitle = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=18,
        textColor=colors.HexColor('#4B5563'),
        spaceAfter=150
    )
    
    style_cover_meta = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#6B7280'),
        spaceAfter=5
    )
    
    style_h1 = ParagraphStyle(
        'DocH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=primary_color,
        spaceBefore=18,
        spaceAfter=10,
        keepWithNext=True
    )

    style_h2 = ParagraphStyle(
        'DocH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=secondary_color,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )

    style_body = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=charcoal,
        spaceAfter=8
    )

    style_bullet = ParagraphStyle(
        'DocBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=charcoal,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    style_code_p = ParagraphStyle(
        'CodeP',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#374151')
    )

    style_table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white
    )

    style_table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=charcoal
    )

    style_table_cell_bold = ParagraphStyle(
        'TableCellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=charcoal
    )

    story = []

    # ================= COVER PAGE =================
    story.append(Spacer(1, 40))
    story.append(Paragraph("TECHNICAL SPECIFICATION & DESIGN MANUAL", ParagraphStyle('CoverPre', fontName='Helvetica-Bold', fontSize=10, textColor=secondary_color, leading=12, spaceAfter=10)))
    story.append(Paragraph("Multi-Agent AI Travel Guide System", style_cover_title))
    story.append(Paragraph("A High-Performance Parallelized Agentic Travel Guide Architecture Built on FastAPI, LangGraph, and OpenRouter LLMs with Langfuse Trace Observability.", style_cover_subtitle))
    
    story.append(Spacer(1, 80))
    story.append(Paragraph("<b>Author:</b> Antigravity AI Pair Programmer", style_cover_meta))
    story.append(Paragraph("<b>Version:</b> v1.0.0 (Production Release)", style_cover_meta))
    story.append(Paragraph(f"<b>Date:</b> {datetime.datetime.now().strftime('%B %d, %Y')}", style_cover_meta))
    story.append(Paragraph("<b>Target Environment:</b> Python 3.11+ / Streamlit / Langfuse Cloud", style_cover_meta))
    story.append(PageBreak())

    # ================= TABLE OF CONTENTS =================
    story.append(Paragraph("Table of Contents", style_h1))
    story.append(Spacer(1, 10))
    
    toc_data = [
        ["1. Executive Summary & Overview", ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "Page 3"],
        ["2. System Architecture & Orchestration Workflow", ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "Page 3"],
        ["3. Deep-Dive: Core LLM Configuration & Base Agent", ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "Page 4"],
        ["4. Specialized Agent Registry", ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "Page 5"],
        ["5. Tool Registry & External APIs Integration", ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "Page 6"],
        ["6. Streaming Architecture & Server-Sent Events", ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "Page 6"],
        ["7. Tracing & Instrumentation (Langfuse)", ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "Page 7"],
        ["8. Setup & Execution Commands Reference", ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "Page 8"],
    ]
    
    t_toc = Table(toc_data, colWidths=[200, 260, 44])
    t_toc.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('TEXTCOLOR', (0,0), (0,-1), primary_color),
        ('TEXTCOLOR', (1,0), (1,-1), colors.HexColor('#9CA3AF')),
        ('TEXTCOLOR', (2,0), (2,-1), charcoal),
        ('ALIGN', (2,0), (2,-1), 'RIGHT'),
    ]))
    story.append(t_toc)
    story.append(PageBreak())

    # ================= 1. EXECUTIVE SUMMARY & OVERVIEW =================
    story.append(Paragraph("1. Executive Summary & Overview", style_h1))
    story.append(Paragraph(
        "The Multi-Agent AI Travel Guide System is a production-grade travel planning software built "
        "on Python. The system coordinates the execution of nine specialized child agents and one supervisor agent "
        "to deliver a consolidated, fully customized travel package. By leveraging LangGraph for orchestration "
        "and LangChain for prompt structures, it resolves complex dependency trees (such as generating an "
        "itinerary only after accommodations, weather details, and tourist landmarks are defined).",
        style_body
    ))
    story.append(Paragraph(
        "The application provides a FastAPI backend featuring both traditional synchronous JSON endpoints "
        "and advanced real-time streaming Server-Sent Events (SSE) endpoints. The frontend is a rich "
        "Streamlit-based dashboard allowing users to visualize agent lifecycle progressions, read streaming outputs "
        "word-by-word, and review detailed booking links.",
        style_body
    ))

    # ================= 2. SYSTEM ARCHITECTURE & ORCHESTRATION WORKFLOW =================
    story.append(Paragraph("2. System Architecture & Orchestration Workflow", style_h1))
    story.append(Paragraph(
        "The core runtime engine is designed as an agentic state machine using <b>LangGraph</b>. The state "
        "is defined by the <code>AgentState</code> TypedDict structure, which propagates extracted user constraints "
        "and agent execution reports through nodes.",
        style_body
    ))
    
    story.append(Paragraph("<b>AgentState Data Structure:</b>", style_h2))
    story.append(Paragraph("• <code>user_message</code>: The raw text prompt provided by the user.", style_bullet))
    story.append(Paragraph("• <code>source</code> / <code>destination</code>: The starting point and travel destination.", style_bullet))
    story.append(Paragraph("• <code>days</code> / <code>people</code> / <code>budget</code>: Extracted quantitative constraints.", style_bullet))
    story.append(Paragraph("• <code>interests</code> / <code>travel_style</code> / <code>food_preference</code>: Extracted qualitative preferences.", style_bullet))
    story.append(Paragraph("• <code>agents_to_run</code>: Active routing path array containing agents that need to execute.", style_bullet))
    story.append(Paragraph("• <code>agents_used</code>: Tracking log indicating which agents have completed execution.", style_bullet))
    story.append(Paragraph("• <code>[agent_name]_result</code>: String variables storing individual output logs from child nodes.", style_bullet))
    story.append(Paragraph("• <code>final_answer</code>: The final merged response formatted and returned to the user.", style_bullet))

    story.append(Paragraph("<b>Workflow Topology & Execution Nodes:</b>", style_h2))
    story.append(Paragraph(
        "The graph is composed of four main logical execution nodes organized to optimize execution time via parallel threading:",
        style_body
    ))
    story.append(Paragraph(
        "<b>1. Supervisor Analyze Node (<code>supervisor_analyze</code>)</b>: Parses free-form text input using a structured JSON prompt template. "
        "Extracts numeric constraints and selects which specialized child agents must run. If critical inputs (like destination) "
        "are missing, it halts routing and returns a targeted follow-up question directly.",
        style_bullet
    ))
    story.append(Paragraph(
        "<b>2. Parallel Execution Node (<code>execute_agents_parallel</code>)</b>: Executes Batch 1 agents concurrently. "
        "Using Python's <code>concurrent.futures.ThreadPoolExecutor</code>, it spins up independent agents in parallel "
        "(Destination, Weather, Transport, Hotel, Food, Budget, Booking Link, and Safety) to achieve significant latency reduction.",
        style_bullet
    ))
    story.append(Paragraph(
        "<b>3. Itinerary Node (<code>itinerary</code>)</b>: Runs in Batch 2. Because a daily schedule requires context about "
        "accommodation neighborhoods, sights, local food, and climate conditions, this node executes sequentially only "
        "after its dependencies (Destination, Weather, Hotel, Food) have completed.",
        style_bullet
    ))
    story.append(Paragraph(
        "<b>4. Supervisor Merge Node (<code>supervisor_merge</code>)</b>: Collects all outputs from active child nodes "
        "and executes a final LLM pass to compile, format, and structure the unified report according to a predefined "
        "twelve-part heading structure.",
        style_bullet
    ))
    
    story.append(Spacer(1, 10))
    story.append(PageBreak())

    # ================= 3. CORE LLM CONFIGURATION & BASE AGENT =================
    story.append(Paragraph("3. Deep-Dive: Core LLM Configuration & Base Agent", style_h1))
    story.append(Paragraph(
        "All specialized agents in the system inherit from the <code>BaseAgent</code> class defined in "
        "<code>app/agents/base.py</code>. This provides a unified constructor, handles tracing context managers, "
        "and encapsulates the LangChain ChatOpenAI LLM client wrapper.",
        style_body
    ))

    story.append(Paragraph("<b>Model Choice & API Endpoint:</b>", style_h2))
    story.append(Paragraph(
        "The system connects to <b>OpenRouter</b> as its LLM backend. The default model is configured as "
        "<code>openrouter/free</code>, which dynamically translates to high-performance, fast-response models like "
        "<code>meta-llama/llama-3-8b-instruct:free</code>. This model choice provides rapid throughput "
        "appropriate for streaming tokens. The client is initialized with <code>temperature=0.2</code> for high deterministic "
        "reliability, and a network timeout threshold of 60 seconds.",
        style_body
    ))

    story.append(Paragraph("<b>Base Agent Client Code Implementation:</b>", style_h2))
    base_agent_code = """class BaseAgent:
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
        api_key = OPENROUTER_API_KEY if OPENROUTER_API_KEY else "dummy_key"
        
        self.llm = ChatOpenAI(
            model=OPENROUTER_MODEL,
            api_key=api_key,
            base_url=OPENROUTER_BASE_URL,
            temperature=0.2,
            timeout=60,
        )"""
    story.append(make_code_block(base_agent_code, style_code_p))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>API Failures & Rate-Limit Mitigation:</b>", style_h2))
    story.append(Paragraph(
        "The <code>generate_response</code> method wraps LLM invocation inside standard exception blocks. "
        "If a rate limit (HTTP 429) or temporary server unavailability (HTTP 503) occurs on the free LLM endpoint, "
        "the agent intercepts the exception and returns a friendly error message instructing the user to try again later or "
        "switch to a paid model, ensuring the backend server does not crash.",
        style_body
    ))
    
    story.append(PageBreak())

    # ================= 4. SPECIALIZED AGENT REGISTRY =================
    story.append(Paragraph("4. Specialized Agent Registry", style_h1))
    story.append(Paragraph(
        "The table below details the full registry of specialized agents configured within the travel guide system, "
        "outlining their roles and tools:",
        style_body
    ))

    # Columns: Agent (70), Responsibility (254), Tools & Technology (180) -> Total 504
    agent_headers = [
        Paragraph("<b>Agent Name</b>", style_table_header),
        Paragraph("<b>Core Responsibility & Prompt Strategy</b>", style_table_header),
        Paragraph("<b>Tools & Technology</b>", style_table_header)
    ]
    
    agent_rows = [
        agent_headers,
        [
            Paragraph("<b>Supervisor</b>", style_table_cell_bold),
            Paragraph("Orchestrates routing, parses JSON query analysis, extracts entities, and merges final outputs.", style_table_cell),
            Paragraph("LangGraph workflows, regex cleaner, base models", style_table_cell)
        ],
        [
            Paragraph("<b>Destination</b>", style_table_cell_bold),
            Paragraph("Researches landmarks, local attraction lists, opening hours, and ticket entry prices.", style_table_cell),
            Paragraph("<code>search_places</code> (Tavily Search API)", style_table_cell)
        ],
        [
            Paragraph("<b>Weather</b>", style_table_cell_bold),
            Paragraph("Retrieves live meteorological conditions and evaluates packing checklist suitability.", style_table_cell),
            Paragraph("<code>get_current_weather</code> (OpenWeather API)", style_table_cell)
        ],
        [
            Paragraph("<b>Transport</b>", style_table_cell_bold),
            Paragraph("Analyzes routes and compares train, bus, flight, and driving times.", style_table_cell),
            Paragraph("<code>search_transport</code> (Tavily Search API)", style_table_cell)
        ],
        [
            Paragraph("<b>Hotel</b>", style_table_cell_bold),
            Paragraph("Identifies top hospitality neighborhoods, safe zones, and budget hostel/hotel options.", style_table_cell),
            Paragraph("<code>search_hotels</code> (Tavily Search API)", style_table_cell)
        ],
        [
            Paragraph("<b>Food</b>", style_table_cell_bold),
            Paragraph("Explores local regional cuisines, famous dishes, street food hubs, and restaurant selections.", style_table_cell),
            Paragraph("<code>search_food_places</code> (Tavily Search API)", style_table_cell)
        ],
        [
            Paragraph("<b>Budget</b>", style_table_cell_bold),
            Paragraph("Formulates numeric cost estimates based on travel style rates.", style_table_cell),
            Paragraph("<code>estimate_budget</code> (Programmatic Calculator Tool)", style_table_cell)
        ],
        [
            Paragraph("<b>Itinerary</b>", style_table_cell_bold),
            Paragraph("Constructs logical day-by-day plans integrating outputs from Destination, Hotel, and Food agents.", style_table_cell),
            Paragraph("Sequential execution using merged memory context", style_table_cell)
        ],
        [
            Paragraph("<b>Booking Link</b>", style_table_cell_bold),
            Paragraph("Compiles direct search/booking URL templates for flights, trains, and hotels.", style_table_cell),
            Paragraph("<code>generate_hotel_booking_links</code>, <code>generate_transport_booking_links</code>", style_table_cell)
        ],
        [
            Paragraph("<b>Safety</b>", style_table_cell_bold),
            Paragraph("Provides security lists, travel advisory checks, packing gear advice, and regional guidelines.", style_table_cell),
            Paragraph("<code>search_safety_updates</code> (Tavily Search API)", style_table_cell)
        ]
    ]

    t_agents = Table(agent_rows, colWidths=[75, 249, 180])
    t_agents.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D1D5DB')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F9FAFB')]),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    
    story.append(t_agents)
    story.append(Spacer(1, 10))
    story.append(PageBreak())

    # ================= 5. TOOL REGISTRY & EXTERNAL APIS INTEGRATION =================
    story.append(Paragraph("5. Tool Registry & External APIs Integration", style_h1))
    story.append(Paragraph(
        "To prevent hallucination, the system utilizes active search tools which query external APIs in real-time. "
        "These tools are declared using LangChain's <code>@tool</code> decorator.",
        style_body
    ))

    story.append(Paragraph("<b>OpenWeather API Integration:</b>", style_h2))
    story.append(Paragraph(
        "The Weather Agent uses the <code>get_current_weather</code> tool to execute a GET request to the OpenWeather endpoint "
        "(<code>https://api.openweathermap.org/data/2.5/weather</code>). It fetches current temperature, feels-like "
        "index, humidity levels, and wind speed in metric units, raising descriptive error exceptions on invalid city inputs "
        "or API key issues.",
        style_body
    ))

    story.append(Paragraph("<b>Tavily Search API Integration:</b>", style_h2))
    story.append(Paragraph(
        "For arbitrary web querying, the system integrates the Tavily API (<code>https://api.tavily.com/search</code>). "
        "Rather than scraping raw pages, Tavily performs structured search ranking, returning title, content snippets, and URL resources. "
        "This is used in specialized tools such as <code>search_places</code>, <code>search_transport_recommendations</code>, "
        "and <code>search_stay_recommendations</code>.",
        style_body
    ))

    story.append(Paragraph("<b>Booking URL Generators:</b>", style_h2))
    story.append(Paragraph(
        "The Booking Link Agent uses <code>generate_hotel_booking_links</code> and <code>generate_transport_booking_links</code>. "
        "These tools programmatically format search templates by URL-encoding inputs. For example, hotel queries generate links for "
        "Booking.com, MakeMyTrip, Agoda, and Google Hotels, while transport queries generate links for IRCTC (railways), "
        "RedBus (buses), MakeMyTrip Flights, and Google Maps Direction Routing.",
        style_body
    ))

    # ================= 6. STREAMING ARCHITECTURE & SERVER-SENT EVENTS =================
    story.append(Paragraph("6. Streaming Architecture & Server-Sent Events", style_h1))
    story.append(Paragraph(
        "For a responsive user interface, the system exposes a SSE (Server-Sent Events) endpoint that streams the "
        "generated travel plan chunk-by-chunk. This is accomplished using FastAPI's <code>StreamingResponse</code> wrapping "
        "an asynchronous generator.",
        style_body
    ))

    story.append(Paragraph("<b>Server-Sent Events (SSE) Protocol Design:</b>", style_h2))
    story.append(Paragraph(
        "The streaming protocol returns a <code>text/event-stream</code> content type. Depending on the environment configuration, "
        "the stream operates in one of two modes:",
        style_body
    ))
    story.append(Paragraph(
        "• <b>Standard Mode (<code>SHOW_AGENT_PROGRESS=false</code>)</b>: Streams only the final travel plan tokens to the user, "
        "shielding them from background execution steps. It yields <code>token</code> events containing JSON-wrapped chunks, followed by "
        "<code>final</code> (delivering the trace ID) and <code>done</code> events.",
        style_bullet
    ))
    story.append(Paragraph(
        "• <b>Debug Mode (<code>SHOW_AGENT_PROGRESS=true</code>)</b>: Interleaves agent execution progress markers into the event stream, "
        "allowing the frontend to render live progress updates (e.g., highlighting active agents as they start or finish).",
        style_bullet
    ))

    story.append(Paragraph("<b>Event Type Structure Table:</b>", style_h2))
    
    event_rows = [
        [
            Paragraph("<b>Event Name</b>", style_table_header),
            Paragraph("<b>Payload Content Structure</b>", style_table_header),
            Paragraph("<b>Description</b>", style_table_header)
        ],
        [
            Paragraph("<code>start</code>", style_table_cell_bold),
            Paragraph("<code>{\"message\": \"Generating...\"}</code>", style_table_cell),
            Paragraph("Emitted at client handshake to initiate streaming.", style_table_cell)
        ],
        [
            Paragraph("<code>progress</code>", style_table_cell_bold),
            Paragraph("<code>{\"agent\": \"hotel\", \"status\": \"started\"}</code>", style_table_cell),
            Paragraph("Indicates child agent execution states (Debug only).", style_table_cell)
        ],
        [
            Paragraph("<code>token</code>", style_table_cell_bold),
            Paragraph("<code>{\"content\": \"...text chunk...\"}</code>", style_table_cell),
            Paragraph("Contains actual markdown characters of the final plan.", style_table_cell)
        ],
        [
            Paragraph("<code>error</code>", style_table_cell_bold),
            Paragraph("<code>{\"agent\": \"weather\", \"message\": \"...\"}</code>", style_table_cell),
            Paragraph("Fires on non-fatal child failures during processing.", style_table_cell)
        ],
        [
            Paragraph("<code>final</code>", style_table_cell_bold),
            Paragraph("<code>{\"trace_id\": \"92419404-313b...\"}</code>", style_table_cell),
            Paragraph("Delivers the Langfuse trace ID for tracking.", style_table_cell)
        ],
        [
            Paragraph("<code>done</code>", style_table_cell_bold),
            Paragraph("<code>{\"status\": \"completed\"}</code>", style_table_cell),
            Paragraph("Final event in stream closing the HTTP connection.", style_table_cell)
        ]
    ]

    t_events = Table(event_rows, colWidths=[70, 204, 230])
    t_events.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), secondary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D1D5DB')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F9FAFB')]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_events)
    story.append(PageBreak())

    # ================= 7. TRACING & INSTRUMENTATION (LANGFUSE) =================
    story.append(Paragraph("7. Tracing & Instrumentation (Langfuse)", style_h1))
    story.append(Paragraph(
        "Observability is a core feature of this architecture. If enabled in environment variables, the system "
        "automatically logs all traces, spans, and metadata to <b>Langfuse Cloud</b>.",
        style_body
    ))

    story.append(Paragraph("<b>OTel Span Tree Topology:</b>", style_h2))
    story.append(Paragraph(
        "A typical travel guide query produces a nested span hierarchy in Langfuse, linking client requests, "
        "agent invocations, API queries, and merging sequences:",
        style_body
    ))
    
    trace_tree = """travel_plan_request
└── supervisor_agent
    ├── destination_agent
    │   └── tavily_web_search
    ├── weather_agent
    │   └── openweather_api_call
    ├── hotel_agent
    │   └── tavily_web_search
    ├── budget_agent
    │   └── estimate_budget (Tool)
    ├── itinerary_agent
    └── final_merge"""
    story.append(make_code_block(trace_tree, style_code_p))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Multithreaded Context Tracking:</b>", style_h2))
    story.append(Paragraph(
        "Because Batch 1 agents run concurrently in a thread pool, standard Python context variables (which "
        "store the active OTel span data) do not automatically propagate to worker threads. To bridge this, the system "
        "implements <code>copy_context_to_thread</code> inside <code>app/tracing.py</code>. This function copies context variables "
        "and runs the target agent function within the context of the parent trace. This ensures that concurrent tasks "
        "are correctly nested under the <code>supervisor_agent</code> parent span in Langfuse.",
        style_body
    ))
    
    ctx_code = """def copy_context_to_thread(func, *args, **kwargs):
    \"\"\"
    Helper to execute func with the current contextvars copied.
    Crucial for propagating active spans/traces to thread pool threads.
    \"\"\"
    ctx = contextvars.copy_context()
    return ctx.run(func, *args, **kwargs)"""
    story.append(make_code_block(ctx_code, style_code_p))
    story.append(Spacer(1, 10))
    story.append(PageBreak())

    # ================= 8. SETUP & EXECUTION COMMANDS REFERENCE =================
    story.append(Paragraph("8. Setup & Execution Commands Reference", style_h1))
    story.append(Paragraph(
        "Follow these standard instructions to configure, launch, and test the multi-agent system:",
        style_body
    ))

    story.append(Paragraph("<b>1. Environment Configuration:</b>", style_h2))
    story.append(Paragraph(
        "Create a <code>.env</code> file in the <code>travel_multi_agent/</code> root directory with the following variables:",
        style_body
    ))
    
    env_content = """OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=meta-llama/llama-3-8b-instruct:free
TAVILY_API_KEY=your_tavily_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_ENABLED=true"""
    story.append(make_code_block(env_content, style_code_p))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>2. Runtime Execution Commands:</b>", style_h2))
    
    cmd_rows = [
        [
            Paragraph("<b>Target Action</b>", style_table_header),
            Paragraph("<b>Execution Command</b>", style_table_header),
            Paragraph("<b>Service Address / Details</b>", style_table_header)
        ],
        [
            Paragraph("<b>Run Unified App</b>", style_table_cell_bold),
            Paragraph("<code>python run.py</code>", style_table_cell),
            Paragraph("Launches both FastAPI & Streamlit concurrently.", style_table_cell)
        ],
        [
            Paragraph("<b>Run API Server Only</b>", style_table_cell_bold),
            Paragraph("<code>uvicorn app.main:app --reload</code>", style_table_cell),
            Paragraph("API endpoints run on <code>http://127.0.0.1:8000</code>.", style_table_cell)
        ],
        [
            Paragraph("<b>Run Web UI Only</b>", style_table_cell_bold),
            Paragraph("<code>streamlit run frontend/streamlit_app.py</code>", style_table_cell),
            Paragraph("Launches dashboard on <code>http://localhost:8501</code>.", style_table_cell)
        ],
        [
            Paragraph("<b>Run Console CLI</b>", style_table_cell_bold),
            Paragraph("<code>python cli.py</code>", style_table_cell),
            Paragraph("Runs the interactive terminal chat utility.", style_table_cell)
        ],
        [
            Paragraph("<b>Test API Endpoint</b>", style_table_cell_bold),
            Paragraph("<code>Invoke-RestMethod -Uri http://127.0.0.1:8000/chat ...</code>", style_table_cell),
            Paragraph("PowerShell POST validation command.", style_table_cell)
        ]
    ]

    t_cmds = Table(cmd_rows, colWidths=[100, 204, 200])
    t_cmds.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#D1D5DB')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F9FAFB')]),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_cmds)
    
    story.append(Spacer(1, 20))
    story.append(Paragraph(
        "<b>Disclaimer:</b> Ensure that your Python virtual environment is activated before running installation "
        "or execution scripts. The <code>run.py</code> script automatically detects the virtual environment path dynamically "
        "on Windows, macOS, and Linux systems.",
        style_body
    ))

    # Build the document using the custom numbered canvas
    doc.build(story, canvasmaker=NumberedCanvas)


if __name__ == "__main__":
    pdf_path = "Multi-Agent_Travel_Guide_Documentation.pdf"
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    
    print(f"Generating technical documentation PDF: {pdf_path}...")
    build_pdf(pdf_path)
    print("PDF generation completed successfully!")
