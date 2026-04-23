from agent import DebateAgent
import random

from agentprofiles import CON_STYLES, PRO_STYLES

MODELS = ["llama3.2:3b", "gemma3:4b"]


class DebateOrchestrator:
    def __init__(self, topic: str, max_turns: int = 5):
        self.topic = topic
        self.max_turns = max_turns
        self.history = []

        pro_style = random.choice(PRO_STYLES)
        con_style = random.choice(CON_STYLES)
        pro_model = random.choice(MODELS)
        con_model = random.choice(MODELS)

        self.agent_a = DebateAgent(
            name=f"{pro_style}... · \n{pro_model}",
            position="FOR",
            style=pro_style,
            model=pro_model,
            topic=topic,
        )
        self.agent_b = DebateAgent(
            name=f"{con_style}... · \n{con_model}",
            position="AGAINST",
            style=con_style,
            model=con_model,
            topic=topic,
        )
        self.agents = [self.agent_a, self.agent_b]

        self.pro_style = pro_style
        self.con_style = con_style
        self.pro_model = pro_model
        self.con_model = con_model

    def run(self):
        print(f"\nStarting debate: \"{self.topic}\"\n")
        print(f"Agent A: {self.agent_a.name}")
        print(f"Agent B: {self.agent_b.name}\n")

        for turn in range(self.max_turns * 2):
            current_agent = self.agents[turn % 2]
            opponent = self.agents[(turn + 1) % 2]

            print(f"[Turn {turn + 1}] {current_agent.name}")
            print("-" * 40)

            try:
                response = current_agent.respond(self.history)
            except Exception as e:
                print(f"  Error calling {current_agent.name}: {e}")
                break

            clean_response, agreed = self._parse_response(response)
            self.history.append({"agent": current_agent.name, "content": clean_response})

            print(clean_response)
            print()

            if agreed:
                print("=" * 60)
                print(f"  {current_agent.name} agrees with {opponent.name}!")
                print("  Debate concluded by consensus.")
                print("=" * 60)
                self._save_transcript()
                return

        print("=" * 60)
        print("  Maximum turns reached. Debate ended without consensus.")
        print("=" * 60)
        self._save_transcript()

    def _parse_response(self, raw: str) -> tuple[str, bool]:
        agreed = "[AGREE]" in raw
        clean = raw.replace("[AGREE]", "").replace("[CONTINUE]", "").strip()
        return clean, agreed

    def _save_transcript(self):
        with open("transcript.txt", "w", encoding="utf-8") as f:
            f.write("DEBATE TRANSCRIPT\n")
            f.write(f"Topic: {self.topic}\n")
            f.write(f"Agent A: {self.agent_a.name}\n")
            f.write(f"Agent B: {self.agent_b.name}\n")
            f.write("=" * 60 + "\n\n")
            for i, msg in enumerate(self.history, 1):
                f.write(f"[{i}] {msg['agent']}\n")
                f.write(msg['content'] + "\n\n")
        print("\nTranscript saved to transcript.txt")