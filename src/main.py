"""Start the Loan vs Investment Analyzer web interface.

Run:  python src/main.py
Then open the address printed in the terminal.
"""
import os

import uvicorn

from app import app

# Port 8070 keeps clear of the other home lab apps:
#   8000 = MCP server, 8080 = AI Assistant, 30090 = AI Agents
DEFAULT_PORT = 8070

# HOST decides who can connect:
#   127.0.0.1 = only this computer (safe default when running with Python on Windows)
#   0.0.0.0   = any network interface (needed inside Docker; the Dockerfile sets this)
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", DEFAULT_PORT))


def print_banner():
    """Print the port as a reminder before the server starts."""
    line = "=" * 60
    print(line)
    print("  Loan vs Investment Analyzer")
    print(f"  Running on PORT {PORT}")
    print(f"  Open in your browser:  http://localhost:{PORT}")
    if HOST == "0.0.0.0":
        print(f"  (Docker: start the container with  -p {PORT}:{PORT})")
    print("  Press Ctrl+C to stop.")
    print(line)


def main():
    print_banner()
    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Ctrl+C: exit quietly instead of printing a traceback
        print("\nStopped.")
