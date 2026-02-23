import streamlit as st
import requests
import os

API_URL = st.text_input("API base URL", value="http://127.0.0.1:8000/api")
API_KEY = st.text_input("API Key", type="password")

st.markdown("""
<style>
.stApp { background: linear-gradient(180deg, #001f3f 0%, #0b2545 100%); color: #c0c0c0; }
.card { background: rgba(255,255,255,0.03); padding: 12px; border-radius:8px; border:1px solid rgba(192,192,192,0.08); }
</style>
""", unsafe_allow_html=True)

st.title("Car Management — Dealer Dashboard")

if API_KEY:
    headers = {"X-API-Key": API_KEY}
    if st.button("List Cars"):
        try:
            r = requests.get(f"{API_URL}/cars", headers=headers, timeout=5)
            r.raise_for_status()
            cars = r.json()
            st.write(cars)
        except Exception as e:
            st.error(str(e))
else:
    st.info("Enter your API key to interact with the API")
