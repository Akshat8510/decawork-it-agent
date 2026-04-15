"""
IT Support Agent — Main Entry Point

Usage:
    python agent/agent.py "reset password for john@company.com"
    python agent/agent.py "create a new user Jane Doe jane@company.com role Engineer"
    python agent/agent.py "check if carol@company.com exists, if not create her, then assign Slack Pro"
    python agent/agent.py --headless "disable the account for bob@company.com"
"""

import sys
import argparse
from .browser_agent import run


# ── Pre-built scenario shortcuts ──────────────────────────────────────────────
DEMO_TASKS = {
    "1": (
        "reset_password",
        "Go to the Users page and reset the password for alice@company.com. "
        "Confirm the temporary password shown in the flash message.",
    ),
    "2": (
        "create_user",
        "Create a new user: full name 'Carol Williams', email 'carol@company.com', role 'DevOps Engineer'. "
        "Then assign her the 'Slack Pro' license.",
    ),
    "3": (
        "disable_user",
        "Disable the account for bob@company.com. Verify the status changes to 'disabled'.",
    ),
    "4": (
        "conditional_flow",
        "Check if 'dave@company.com' exists. If the user does NOT exist, create them with the name "
        "'Dave Kumar' and role 'Analyst'. Then assign the 'Microsoft 365' license to dave@company.com.",
    ),
    "5": (
        "revoke_license",
        "Revoke the license currently assigned to alice@company.com.",
    ),
}


def print_menu():
    print("\n┌─────────────────────────────────────────────┐")
    print("│         IT Support Agent — Demo Menu         │")
    print("├─────────────────────────────────────────────┤")
    for key, (name, _) in DEMO_TASKS.items():
        print(f"│  {key}. {name:<41}│")
    print("│  c. custom task (type your own)             │")
    print("│  q. quit                                    │")
    print("└─────────────────────────────────────────────┘")


def main():
    parser = argparse.ArgumentParser(description="IT Support Agent")
    parser.add_argument("task", nargs="*", help="Natural-language IT task")
    parser.add_argument("--headless", action="store_true", help="Run browser headlessly")
    parser.add_argument("--demo", action="store_true", help="Show interactive demo menu")
    args = parser.parse_args()

    headless = args.headless

    # Interactive demo menu
    if args.demo or not args.task:
        print_menu()
        choice = input("\nSelect option: ").strip().lower()
        if choice == "q":
            sys.exit(0)
        elif choice == "c":
            task = input("Enter your task: ").strip()
        elif choice in DEMO_TASKS:
            _, task = DEMO_TASKS[choice]
            print(f"\n[Agent] Task: {task}\n")
        else:
            print("Invalid choice.")
            sys.exit(1)
    else:
        task = " ".join(args.task)

    print(f"\n{'='*60}")
    print(f"[IT Agent] Starting task...")
    print(f"{'='*60}")
    print(f"Task: {task}")
    print(f"{'='*60}\n")

    result = run(task, headless=headless)

    print(f"\n{'='*60}")
    print("[IT Agent] Task Complete")
    print(f"{'='*60}")
    print(result)
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()