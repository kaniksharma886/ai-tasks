import streamlit as st
import config
import core
import rag_manager_test


st.title("Dashboard")

if "llm_msg" not in st.session_state:
    st.session_state.llm_msg = ""

if "telemetry_data" not in st.session_state:
    st.session_state.telemetry_data = ""


st.text(f"""Chat Started.

This LLM based chat can reply to all queries that can be covered by the model's training data.

It has abount 50 MB of text from different free novels. 
Responses related to novel stories will have a high level of bias towards the information from novel.

Chat history is saved and LLM will refer to last {config.MESSAGE_HISTORY_LIMIT} messages.

""")



msg = st.text_input("User message")

if st.button("Send"):
    resp, telemetry = core.chat_helper(msg)
    st.session_state.llm_msg += str(resp) +"\n"
    st.session_state.telemetry_data += str(telemetry) + "\n"

st.text_area("LLM Response", value=st.session_state.llm_msg)

st.text_area("Latency Data", value= st.session_state.telemetry_data)





if st.button("RAG result"):
	st.info("Retrieval accuracy curves")

if st.button("Agent result"):
	st.warning("Agent success/failure")

