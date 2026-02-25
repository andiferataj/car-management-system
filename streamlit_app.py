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
    /* lighter overall background */
    .stApp { background: linear-gradient(180deg, #f5f8fb 0%, #e9f2fb 100%); color: #111827; }

    /* cards and panels with subtle white backing */
    .card { background: rgba(255,255,255,0.9); padding: 12px; border-radius:8px; border:1px solid rgba(0,0,0,0.06); }

    /* buttons */
    .stButton>button { background-color:#0b5fb8; color:#ffffff; }

    /* headings and subtitles: make them more visible on light background */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5 {
        color: #0b3b66 !important;
    }

    /* form labels and small subtitles (brand id, model name, etc.) */
    label, .css-1aumxhk, .stMarkdown p, .stTextInput>div>label {
        color: #274a6b !important;
    }

    /* make table header text slightly darker for readability */
    .stDataFrame thead th {
        color: #0b3b66 !important;
    }
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

    st.markdown("---")
    st.subheader("Create / Seed")
    with st.expander("Create Brand"):
        bname = st.text_input("Brand name", key="brand_name")
        if st.button("Create Brand", key="create_brand"):
            try:
                r = requests.post(f"{API_URL}/brands", headers=headers, json={"name": bname}, timeout=5)
                r.raise_for_status()
                st.success("Created brand")
                st.experimental_rerun()
            except Exception as e:
                st.error(str(e))

    with st.expander("Create Model"):
        m_brand = st.text_input("Brand ID", key="m_brand")
        m_name = st.text_input("Model name", key="m_name")
        m_year = st.number_input("Year", min_value=1900, max_value=2100, value=2023, key="m_year")
        if st.button("Create Model", key="create_model"):
            try:
                payload = {"brand_id": m_brand, "name": m_name, "year": int(m_year)}
                r = requests.post(f"{API_URL}/models", headers=headers, json=payload, timeout=5)
                r.raise_for_status()
                st.success("Created model")
                st.experimental_rerun()
            except Exception as e:
                st.error(str(e))

    with st.expander("Create Car"):
        c_model = st.text_input("Model ID", key="c_model")
        c_vin = st.text_input("VIN", key="c_vin")
        c_color = st.text_input("Color", key="c_color")
        c_price = st.number_input("Price", min_value=0.0, format="%.2f", key="c_price")
        if st.button("Create Car", key="create_car"):
            try:
                payload = {"model_id": c_model, "vin": c_vin, "color": c_color, "price": float(c_price), "status": "available"}
                r = requests.post(f"{API_URL}/cars", headers=headers, json=payload, timeout=5)
                r.raise_for_status()
                st.success("Created car")
                st.experimental_rerun()
            except Exception as e:
                st.error(str(e))

    st.markdown("---")
    st.subheader("Scraper")
    html = st.text_area("Paste listing HTML here (or fetch externally)")
    if st.button("Parse HTML"):
        if not API_KEY:
            st.error("API key required in sidebar")
        else:
            try:
                r = requests.post(f"{API_URL}/scrape", headers=headers, json={"html": html}, timeout=10)
                r.raise_for_status()
                res = r.json()
                st.write(res)
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

