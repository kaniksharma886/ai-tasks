import rag_manager_test
import streamlit as st
import travel_agent
import config
import core
import json

st.title("Dashboard")
col1, col2 = st.columns([4, 1])



if "llm_msg" not in st.session_state:
    st.session_state.llm_msg = ""

if "telemetry_data" not in st.session_state:
    st.session_state.telemetry_data = ""

if "msg" not in st.session_state:
    st.session_state.msg = ""

if "run_list" not in st.session_state:
    st.session_state.run_list = []

msg = ""


with col2:
    if st.button("Send"):
        resp, telemetry = core.chat_helper(msg)
        st.session_state.llm_msg += str(resp) +"\n"
        st.session_state.telemetry_data += str(telemetry) + "\n"


    if st.button("RAG test"):
        st.session_state.msg, st.session_state.run_list = rag_manager_test.create_test_report()

    if st.button("Agent result"):
        prompt = "Plan a 2-day trip to Auckland for under NZ$500"
        st.text_input(prompt)
        travel_result = json.loads(travel_agent.run_trip_planner_agent(prompt))
        st.text("PASS: Cost is <= 500" if travel_result["total_cost"] <= 500 else "Cost is more than 500" )
        st.text_area("Agent Result", f"{travel_result}")


with col1:
    msg = st.text_input("User message")
    st.text_area("LLM Response", value = st.session_state.llm_msg)
    st.text_area("Latency Data", value = st.session_state.telemetry_data)
    st.text_area("RAG result", value = st.session_state.msg)
    st.bar_chart(st.session_state.run_list)


