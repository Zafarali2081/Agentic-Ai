import sys
import os
import argparse

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.memory import AgentMemory
from src.agent import PersonalBudgetAgent


def run_demo():
    """Run automated demo showing all rubric scenarios."""
    print("=" * 70)
    print("PERSONAL BUDGET ASSISTANT - AGENTIC AI DEMO")
    print("=" * 70)


    memory = AgentMemory()
    agent = PersonalBudgetAgent(memory=memory)

    print("\n--- DEMO 1: Single Expense Addition ---")
    agent.run("I spent ₹500 on food.")

    print("\n--- DEMO 2: Multi-Turn Memory Persistence ---")
    agent.run("I spent another ₹300 on food.")
    agent.run("How much have I spent on food?")

    print("\n--- DEMO 3: Additional Category ---")
    agent.run("I spent ₹1000 on travel.")

    print("\n--- DEMO 4: Complex Multi-Step Affordability Goal ---")
    agent.run("I have ₹5000. I spent ₹1000 on food and ₹500 on travel. Can I afford a ₹2000 trip?")

    print("\n--- DEMO 5: Tool Failure & Graceful Recovery ---")
    agent.run("I spent -₹500 on food.")

    print("\n" + "=" * 70)
    print("[SUCCESS] ALL DEMO SCENARIOS COMPLETED SUCCESSFULLY!")
    print("=" * 70)


def run_interactive():
    """Run interactive chat session with the agent."""
    print("=" * 70)
    print("Welcome to Personal Budget Assistant (Agentic AI)!")
    print("Type your expense or budget question below.")
    print("Commands:")
    print("  'exit' or 'quit' -> Exit program")
    print("  'clear'         -> Reset session memory")
    print("  'summary'       -> Print current structured memory")
    print("=" * 70)

    memory = AgentMemory()
    agent = PersonalBudgetAgent(memory=memory)

    while True:
        try:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "q"]:
                print("\nGoodbye! Have a great day managing your budget.")
                break

            if user_input.lower() == "clear":
                memory.clear()
                print("[INFO] Memory cleared! Starting fresh session.")
                continue

            if user_input.lower() == "summary":
                summary = memory.get_structured_summary()
                print(f"[SUMMARY] Total = Rs. {summary['total_overall']:.2f}, Categories = {summary['categories']}")
                continue

            # Run agent with full trace
            agent.run(user_input, verbose=True)

        except KeyboardInterrupt:
            print("\nSession interrupted. Exiting.")
            break
        except Exception as e:
            print(f"\n[ERROR]: {e}")



def main():
    parser = argparse.ArgumentParser(description="Personal Budget Assistant - Agentic AI")
    parser.add_argument("--demo", action="store_true", help="Run automated demonstration of all scenarios")
    args = parser.parse_args()

    if args.demo:
        run_demo()
    else:
        run_interactive()


if __name__ == "__main__":
    main()
