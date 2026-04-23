"""
Tournament runner: every unique style pair debates one topic.
Scores agreement and reports the most/least agreeing pair.
"""

from agent import DebateAgent
from agentprofiles import PRO_STYLES, CON_STYLES
import itertools
import random

MODELS = ["llama3.2:3b", "gemma3:4b"]
MAX_TURNS = 3  # turns per agent per debate — keep short for speed


ALL_STYLES = [(s, "PRO") for s in PRO_STYLES] + [(s, "CON") for s in CON_STYLES]

# Short label for display
def label(style: str) -> str:
    return style.split(".")[0]


def run_debate(topic: str, style_a: str, style_b: str) -> dict:
    """
    Run one debate between style_a (FOR) and style_b (AGAINST).
    Returns agreement info.
    """
    model_a = random.choice(MODELS)
    model_b = random.choice(MODELS)

    agent_a = DebateAgent(
        name=label(style_a),
        position="FOR",
        style=style_a,
        model=model_a,
        topic=topic,
    )
    agent_b = DebateAgent(
        name=label(style_b),
        position="AGAINST",
        style=style_b,
        model=model_b,
        topic=topic,
    )

    agents = [agent_a, agent_b]
    history = []
    agreed_on_turn = None

    total_turns = MAX_TURNS * 2
    for turn in range(total_turns):
        current = agents[turn % 2]
        try:
            raw = current.respond(history)
        except Exception as e:
            print(f"  [Error] {current.name}: {e}")
            break

        agreed = "[AGREE]" in raw
        clean = raw.replace("[AGREE]", "").replace("[CONTINUE]", "").strip()
        history.append({"agent": current.name, "content": clean})

        if agreed:
            agreed_on_turn = turn + 1
            break

    # agreement_score: 1.0 = agreed on turn 1, 0.0 = never agreed
    if agreed_on_turn is not None:
        agreement_score = 1.0 - (agreed_on_turn - 1) / total_turns
    else:
        agreement_score = 0.0

    return {
        "style_a": style_a,
        "style_b": style_b,
        "agreed": agreed_on_turn is not None,
        "agreed_on_turn": agreed_on_turn,
        "agreement_score": agreement_score,
        "history": history,
    }


def run_tournament(topic: str):
    print("=" * 70)
    print("  DEBATE TOURNAMENT")
    print(f"  Topic: {topic}")
    print(f"  Styles: {len(ALL_STYLES)} | Pairs: {len(ALL_STYLES) * (len(ALL_STYLES) - 1) // 2}")
    print(f"  Turns per debate: {MAX_TURNS} per agent")
    print("=" * 70)

    pairs = list(itertools.combinations(ALL_STYLES, 2))
    results = []

    for i, ((style_a, _), (style_b, _)) in enumerate(pairs, 1):
        print(f"\n[{i}/{len(pairs)}] {label(style_a)}  vs  {label(style_b)}", end=" ... ", flush=True)
        result = run_debate(topic, style_a, style_b)
        results.append(result)
        status = f"AGREED (turn {result['agreed_on_turn']})" if result["agreed"] else "no agreement"
        print(status)

    # Sort by agreement score
    results.sort(key=lambda r: r["agreement_score"], reverse=True)

    most = results[0]
    least = results[-1]

    print("\n" + "=" * 70)
    print("  RESULTS")
    print("=" * 70)

    print("\n  MOST AGREEING PAIR:")
    print(f"    {label(most['style_a'])}")
    print(f"    vs")
    print(f"    {label(most['style_b'])}")
    print(f"    Score: {most['agreement_score']:.2f}  |  Agreed: {most['agreed']}  |  Turn: {most['agreed_on_turn']}")

    print("\n  LEAST AGREEING PAIR:")
    print(f"    {label(least['style_a'])}")
    print(f"    vs")
    print(f"    {label(least['style_b'])}")
    print(f"    Score: {least['agreement_score']:.2f}  |  Agreed: {least['agreed']}  |  Turn: {least['agreed_on_turn']}")

    _save_results(topic, results)
    return results


def _save_results(topic: str, results: list):
    with open("tournament_results.txt", "w", encoding="utf-8") as f:
        f.write("TOURNAMENT RESULTS\n")
        f.write(f"Topic: {topic}\n")
        f.write(f"Turns per agent: {MAX_TURNS}\n")
        f.write("=" * 70 + "\n\n")

        f.write("RANKING (most → least agreeing):\n\n")
        for i, r in enumerate(results, 1):
            f.write(
                f"{i:3}. [{r['agreement_score']:.2f}] "
                f"{label(r['style_a'])}  vs  {label(r['style_b'])}"
                f"  ({'agreed turn ' + str(r['agreed_on_turn']) if r['agreed'] else 'no agreement'})\n"
            )

        f.write("\n\n" + "=" * 70 + "\n")
        f.write("DEBATE TRANSCRIPTS\n")
        f.write("=" * 70 + "\n")
        for i, r in enumerate(results, 1):
            f.write(f"\n{'─' * 70}\n")
            f.write(f"DEBATE #{i}  |  Score: {r['agreement_score']:.2f}\n")
            f.write(f"FOR:     {label(r['style_a'])}\n")
            f.write(f"AGAINST: {label(r['style_b'])}\n")
            outcome = f"Agreed on turn {r['agreed_on_turn']}" if r['agreed'] else "No agreement reached"
            f.write(f"Outcome: {outcome}\n")
            f.write(f"{'─' * 70}\n\n")
            for j, msg in enumerate(r['history'], 1):
                f.write(f"[Turn {j}] {msg['agent']}\n")
                f.write(msg['content'] + "\n\n")

    print("\n  Full ranking saved to tournament_results.txt")


if __name__ == "__main__":
    print("=" * 70)
    print("  AI DEBATE TOURNAMENT")
    print("=" * 70)
    topic = input("\nEnter a debate topic: ").strip()
    if not topic:
        topic = "Artificial intelligence will do more harm than good"

    run_tournament(topic)
