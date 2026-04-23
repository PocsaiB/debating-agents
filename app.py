import streamlit as st
from debate import DebateOrchestrator

st.set_page_config(page_title="AI Debate App", page_icon="🎙️", layout="centered")

st.title("🎙️ AI Debate App")
st.caption("Two AI agents debate a topic until they reach consensus.")

topic = st.text_input("Debate topic", placeholder="e.g. Social media does more harm than good")
max_turns = st.slider("Max turns per agent", min_value=1, max_value=10, value=5)

if st.button("Start Debate", disabled=not topic):
    orchestrator = DebateOrchestrator(topic=topic, max_turns=max_turns)

    st.divider()
    st.subheader(f"📌 {topic}")

    for turn in range(max_turns * 2):
        current_agent = orchestrator.agents[turn % 2]
        opponent = orchestrator.agents[(turn + 1) % 2]

        response = current_agent.respond(orchestrator.history)
        clean_response, agreed = orchestrator._parse_response(response)

        orchestrator.history.append({
            "agent": current_agent.model+' style',
            "content": clean_response
        })

        if current_agent.position == "FOR":
            with st.chat_message("user"):
                st.markdown(f"**{current_agent.name} (FOR)**")
                st.write(clean_response)
        else:
            with st.chat_message("assistant"):
                st.markdown(f"**{current_agent.name} (AGAINST)**")
                st.write(clean_response)

        if agreed:
            st.success(f"✅ {current_agent.name} agrees with {opponent.name}. Debate concluded!")
            break
    else:
        st.warning("⏱️ Max turns reached without consensus.")

    orchestrator._save_transcript()
