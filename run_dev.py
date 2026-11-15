"""One-command runner to start both FrontDeskAI Web Server and Voice Agent concurrently."""
import subprocess
import sys
import time


def main():
    print("=" * 60)
    print("🚀 Starting FrontDeskAI System")
    print("   🌐 Web Dashboard (Frontend & API): http://localhost:8000")
    print("   🎙️ LiveKit Voice Agent Worker:    Dev Mode")
    print("=" * 60)

    # 1. Start FastAPI server
    server_cmd = [sys.executable, "-m", "uvicorn", "src.web_server:app", "--port", "8000", "--reload"]
    server_proc = subprocess.Popen(server_cmd)

    time.sleep(1.2)

    # 2. Start LiveKit agent worker
    agent_cmd = [sys.executable, "-m", "src.agent", "dev"]
    agent_proc = subprocess.Popen(agent_cmd)

    try:
        server_proc.wait()
        agent_proc.wait()
    except KeyboardInterrupt:
        print("\n🛑 Gracefully shutting down FrontDeskAI services...")
        server_proc.terminate()
        agent_proc.terminate()
        server_proc.wait()
        agent_proc.wait()
        print("✅ Shutdown complete.")


if __name__ == "__main__":
    main()
