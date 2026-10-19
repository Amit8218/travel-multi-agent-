import sys
import asyncio
import json
from app.config import OPENROUTER_MODEL, validate_config
from app.workflow.graph import supervisor_agent

async def main():
    print("=" * 75)
    print("        MULTI-AGENT AI TRAVEL PLANNING SYSTEM - CLI CHAT CLIENT        ")
    print("=" * 75)
    print(f"[*] LLM Model Provider: OpenRouter ({OPENROUTER_MODEL})")
    
    # Validate API configuration
    missing_keys = validate_config()
    if missing_keys:
        print("\n[!] Warning: Missing API configurations in your .env:")
        for key in missing_keys:
            print(f"  - {key}")
        if "OPENROUTER_API_KEY" in missing_keys:
            print("\n[Error] OPENROUTER_API_KEY is missing. The LLM cannot execute without it.")
            print("Please configure your OPENROUTER_API_KEY in the .env file and try again.")
            sys.exit(1)
        else:
            print("[!] Note: Weather searches and web lookups will fail if their respective tools are invoked.")
    else:
        print("[+] All API configurations are loaded successfully.")

    print("-" * 75)
    print("Instructions:")
    print("- Type your travel-related questions or planning requests and press Enter.")
    print("- Examples: ")
    print("  * 'Plan a 3-day Jaipur trip from Delhi for 2 people under 15000'")
    print("  * 'What is the weather in Manali right now?'")
    print("  * 'Suggest budget stay areas in Jaipur'")
    print("- Type 'exit', 'quit', or 'bye' to exit.")
    print("=" * 75)

    while True:
        try:
            # Run blocking input in a thread executor to keep loop responsive
            user_input = await asyncio.to_thread(input, "\nYou > ")
            user_input = user_input.strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("\n[+] Thank you for using AI Travel Guide. Safe travels! Goodbye!")
                break
                
            print("\n[*] Initializing multi-agent planner...")
            
            started_response = False
            agents_used = []
            
            async for sse_event in supervisor_agent.run_stream(params={"user_message": user_input}, endpoint="/cli"):
                lines = sse_event.strip().split("\n")
                event_type = ""
                data_json = ""
                
                for line in lines:
                    if line.startswith("event:"):
                        event_type = line.replace("event:", "").strip()
                    elif line.startswith("data:"):
                        data_json = line.replace("data:", "").strip()
                        
                if event_type and data_json:
                    try:
                        data = json.loads(data_json)
                        if event_type == "progress":
                            agent = data.get("agent", "unknown")
                            status = data.get("status", "")
                            if status == "started":
                                print(f"  └─ 🔄 [{agent.capitalize()} Agent] Coordinating...", end="\r", flush=True)
                            elif status == "completed":
                                print(f"  └─ ✅ [{agent.capitalize()} Agent] Completed        ", flush=True)
                            elif status == "failed":
                                print(f"  └─ ❌ [{agent.capitalize()} Agent] Failed           ", flush=True)
                        elif event_type == "token":
                            if not started_response:
                                print("\nAgent Plan > ", end="", flush=True)
                                started_response = True
                            print(data.get("content", ""), end="", flush=True)
                        elif event_type == "error":
                            print(f"\n  └─ ⚠️ Alert [{data.get('agent', 'System')}]: {data.get('message', '')}", flush=True)
                        elif event_type == "final":
                            agents_used = data.get("agents_used", [])
                    except Exception:
                        pass
                        
            print("\n" + "-" * 75)
            if agents_used:
                print(f"[Specialized Agents Active: {', '.join(agents_used)}]")
                print("-" * 75)

        except KeyboardInterrupt:
            print("\n\n[+] Interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"\n[Error] An unexpected error occurred: {str(e)}")
            print("-" * 75)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[+] Goodbye!")

