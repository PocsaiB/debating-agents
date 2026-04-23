import os
from debate import DebateOrchestrator

def main():
    print("=" * 60)
    print("         AI DEBATE APPLICATION")
    print("=" * 60)

    topic = input("\nEnter a debate topic: ").strip()
    if not topic:
        topic = "Artificial intelligence will do more harm than good"

    try:
        max_turns = int(input("Max turns per agent (default 5): ").strip() or "5")
    except ValueError:
        max_turns = 5

    print(f"\nTopic: {topic}")
    print(f"Max turns: {max_turns}")
    print("-" * 60)

    orchestrator = DebateOrchestrator(topic=topic, max_turns=max_turns)
    orchestrator.run()

if __name__ == "__main__":
    main()