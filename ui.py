import streamlit as st

st.title("Dashboard")


if st.button("Latency result"):
	st.success("Latency and cost metrics")

if st.button("RAG result"):
	st.info("Retrieval accuracy curves")

if st.button("Agent result"):
	st.warning("Agent success/failure")

