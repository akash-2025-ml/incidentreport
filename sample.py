import subprocess
import time
import requests
import signal
import sys


def start_fastapi_server():
    """Start the FastAPI server as a background process."""
    print("🚀 Starting FastAPI server from main.py...")
    process = subprocess.Popen(
        ["uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # Wait a few seconds for the server to start
    time.sleep(3)
    return process


def stop_fastapi_server(process):
    """Stop the FastAPI server process."""
    print("🛑 Stopping FastAPI server...")
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


def send_request():
    """Send GET request to FastAPI endpoint."""
    url = "http://127.0.0.1:8000/incidents/summary"
    params = {
        "start_time": "2025-11-01 00:00:00",
        "end_time": "2025-11-10 00:00:00",
        "top_limit": 10,
    }
    try:
        print("📡 Sending request to FastAPI server...")
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            print("✅ Response received successfully:\n")
            print(response.json())
        else:
            print(f"❌ Server returned {response.status_code}: {response.text}")
    except Exception as e:
        print(f"⚠️ Request failed: {e}")


if __name__ == "__main__":
    # Start FastAPI
    server_process = start_fastapi_server()
    try:
        # Send the request
        send_request()
    finally:
        # Stop FastAPI
        stop_fastapi_server(server_process)
