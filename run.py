import os
import sys
import subprocess
import time

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_dir)

    venv_dir = os.path.abspath(os.path.join(current_dir, "..", "venv"))
    if os.name == "nt":
        python_exe = os.path.join(venv_dir, "Scripts", "python.exe")
        streamlit_exe = os.path.join(venv_dir, "Scripts", "streamlit.exe")
    else:
        python_exe = os.path.join(venv_dir, "bin", "python")
        streamlit_exe = os.path.join(venv_dir, "bin", "streamlit")

    # Fallback to system python/streamlit if venv not found
    if not os.path.exists(python_exe):
        python_exe = sys.executable
        streamlit_exe = "streamlit"

    print("====================================================")
    print("🚀 Starting Multi-Agent AI Travel Guide Planner App")
    print("====================================================")

    # 1. Start FastAPI Backend Server
    print("👉 Starting FastAPI Backend on http://127.0.0.1:8000 ...")
    backend_proc = subprocess.Popen(
        [python_exe, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=current_dir
    )

    # Give backend a moment to start
    time.sleep(3)

    # 2. Start Streamlit Frontend App
    print("👉 Starting Streamlit Frontend on http://localhost:8501 ...")
    frontend_proc = subprocess.Popen(
        [streamlit_exe, "run", "frontend/streamlit_app.py"],
        cwd=current_dir
    )

    print("\n✅ Application is fully running!")
    print("- Backend API Docs: http://127.0.0.1:8000/docs")
    print("- Streamlit Web App: http://localhost:8501")
    print("- SSE Demo Page: Open frontend/streaming_demo.html in browser")
    print("====================================================")
    print("Press Ctrl+C to terminate both servers.")
    print("====================================================")

    try:
        while True:
            # Check if any process has exited
            if backend_proc.poll() is not None:
                print("❌ Backend server stopped unexpectedly!")
                break
            if frontend_proc.poll() is not None:
                print("❌ Frontend server stopped unexpectedly!")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down both servers...")
    finally:
        backend_proc.terminate()
        frontend_proc.terminate()
        backend_proc.wait()
        frontend_proc.wait()
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()
