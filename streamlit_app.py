import streamlit as st
import requests
import os
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Car Management — Dealer Dashboard", layout="wide")

with st.sidebar:
    st.markdown("# Settings")
    API_URL = st.text_input("API base URL", value="http://127.0.0.1:8000/api")
    API_KEY = st.text_input("API Key", type="password")
    if st.button("Refresh / Seed"):
        try:
            # optional: call seed endpoint via script or let user run `python scripts/seed.py`
            st.experimental_rerun()
        except Exception:
            st.warning("Could not seed automatically — run `python scripts/seed.py` instead.")

st.markdown(
    """
    <style>
    .stApp { background: linear-gradient(180deg, #001f3f 0%, #0b2545 100%); color: #c0c0c0; }
    .card { background: rgba(255,255,255,0.03); padding: 12px; border-radius:8px; border:1px solid rgba(192,192,192,0.08); }
    .stButton>button { background-color:#0b2545; color:#c0c0c0; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Car Management — Dealer Dashboard")

headers = {"X-API-Key": API_KEY} if API_KEY else {}

col1, col2 = st.columns((3, 2))

with col1:
    st.subheader("Cars")
    if not API_KEY:
        st.info("Enter your API key in the sidebar to fetch data.")
    else:
        try:
            r = requests.get(f"{API_URL}/cars", headers=headers, timeout=5)
            r.raise_for_status()
            cars = r.json()
            df = pd.DataFrame(cars)
            if not df.empty:
                # Join with models and brands
                r2 = requests.get(f"{API_URL}/models", headers=headers, timeout=5)
                r2.raise_for_status()
                models = pd.DataFrame(r2.json())
                r3 = requests.get(f"{API_URL}/brands", headers=headers, timeout=5)
                r3.raise_for_status()
                brands = pd.DataFrame(r3.json())
                df = df.merge(models, left_on='model_id', right_on='id', suffixes=("", "_model"))
                df = df.merge(brands, left_on='brand_id', right_on='id', suffixes=("", "_brand"))
                df_display = df[["id", "name_brand", "name", "vin", "color", "price", "status", "year"]]
                df_display.columns = ["car_id", "brand", "model", "vin", "color", "price", "status", "year"]
                st.dataframe(df_display)
            else:
                st.info("No cars found.")
        except Exception as e:
            st.error(str(e))

with col2:
    st.subheader("Analytics")
    try:
        if API_KEY:
            r = requests.get(f"{API_URL}/cars", headers=headers, timeout=5)
            r.raise_for_status()
            cars = r.json()
            df = pd.DataFrame(cars)
            if not df.empty and "price" in df.columns:
                fig = px.histogram(df, x="price", nbins=20, title="Price distribution", template="plotly_dark")
                st.write(fig)
            else:
                st.info("No pricing data to show.")
    except Exception as e:
        st.error(str(e))

