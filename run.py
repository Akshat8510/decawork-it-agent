"""
run.py — One-shot launcher
Starts the Flask admin panel in a background thread, then runs the agent.

Usage:
    python run.py                          # interactive demo menu
    python run.py "reset password for alice@company.com"
    python run.py --headless --demo
"""

import sys
import time
import threading
import argparse
import subprocess
import requests

FLASK_PORT = 5000
FLASK_URL  = f"http://127.0.0.1:{FLASK_PORT}"


def wait_for_flask(timeout: int = 10) -> bool:
    """Block until Flask is ready or timeout expires."""
    for _ in range(timeout * 2):
        try:
            r = requests.get(FLASK_URL, timeout=1)
            if r.status_code < 500:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def start_flask():
    """Start the Flask app as a subprocess."""
    proc = subprocess.Popen(
        [sys.executable, "-m", "flask", "--app", "app.main", "run", "--port", str(FLASK_PORT)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return proc


def main():
    parser = argparse.ArgumentParser(description="IT Support Agent Launcher")
    parser.add_argument("task", nargs="*", help="IT task to run")
    parser.add_argument("--headless", action="store_true")
    parser.add_argument("--demo",     action="store_true")
    args = parser.parse_args()

    # ── Start Flask ──────────────────────────────────────────────────────────
    print("[*] Starting mock IT admin panel...")
    flask_proc = start_flask()

    if not wait_for_flask(timeout=10):
        print("[!] Flask failed to start. Exiting.")
        flask_proc.terminate()
        sys.exit(1)

    print(f"[✓] Admin panel running at {FLASK_URL}\n")

    # ── Run agent ────────────────────────────────────────────────────────────
    try:
        # Import here so Flask has time to start
        from agent.agent import main as agent_main
        # Patch sys.argv so agent_main uses our args
        new_argv = [sys.argv[0]]
        if args.headless:
            new_argv.append("--headless")
        if args.demo or not args.task:
            new_argv.append("--demo")
        else:
            new_argv.extend(args.task)
        sys.argv = new_argv
        agent_main()
    finally:
        flask_proc.terminate()
        print("\n[*] Admin panel stopped.")


if __name__ == "__main__":
    main()