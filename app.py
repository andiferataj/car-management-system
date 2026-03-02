import streamlit as st
import requests
import pandas as pd

import urllib.parse


API = "http://localhost:8000"

st.set_page_config(page_title="🚗 Car Management", layout="wide")
st.title("🚗 Car Management System")

page = st.sidebar.radio("Navigation", [
    "📊 Dashboard",
    "👤 Users",     "➕ Add User",  "✏️ Edit User",  "🗑️ Delete User",
    "🚗 Cars",      "➕ Add Car",   "✏️ Edit Car",   "🗑️ Delete Car",
    "🔍 Car Scraper",
])


def fetch_users():
    return requests.get(f"{API}/users").json().get("users", [])

def fetch_cars():
    return requests.get(f"{API}/cars").json().get("cars", [])

if page == "📊 Dashboard":
    st.header("📊 Dashboard")
    users = fetch_users()
    cars  = fetch_cars()

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Users", len(users))
    c2.metric("Total Cars",  len(cars))
    c3.metric("Unassigned Cars", sum(1 for c in cars if not c["user_id"]))

    st.divider()

    if cars:
        df = pd.DataFrame(cars)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Cars by Brand")
            st.bar_chart(df["brand"].value_counts())
        with col2:
            st.subheader("Cars by Year")
            st.bar_chart(df["year"].value_counts().sort_index())



elif page == "👤 Users":
    st.header("👤 All Users")
    users = fetch_users()
    if users:
        st.dataframe(pd.DataFrame(users), use_container_width=True, hide_index=True)
    else:
        st.info("No users yet. Add one from the sidebar!")


elif page == "➕ Add User":
    st.header("➕ Add a User")
    with st.form("add_user"):
        name      = st.text_input("Name *")
        email     = st.text_input("Email *")
        submitted = st.form_submit_button("Add User")

    if submitted:
        if not name or not email:
            st.warning("Name and Email are required.")
        else:
            res = requests.post(f"{API}/users", json={"name": name, "email": email})
            if res.status_code == 201:
                st.success(f"✅ User '{name}' added!")
            else:
                st.error(res.json().get("detail", res.text))


elif page == "✏️ Edit User":
    st.header("✏️ Edit a User")
    user_id = st.number_input("User ID", min_value=1, step=1)

    if st.button("Load"):
        res = requests.get(f"{API}/users/{user_id}")
        if res.status_code == 200:
            st.session_state["loaded_user"] = res.json()
        else:
            st.error("User not found.")

    if "loaded_user" in st.session_state:
        u = st.session_state["loaded_user"]
        with st.form("edit_user"):
            name  = st.text_input("Name",  value=u["name"])
            email = st.text_input("Email", value=u["email"])
            saved = st.form_submit_button("Save")

        if saved:
            res = requests.put(f"{API}/users/{user_id}", json={"name": name, "email": email})
            if res.status_code == 200:
                st.success("✅ User updated!")
                del st.session_state["loaded_user"]
            else:
                st.error(res.json().get("detail", res.text))


elif page == "🗑️ Delete User":
    st.header("🗑️ Delete a User")
    user_id = st.number_input("User ID", min_value=1, step=1)
    if st.button("🗑️ Delete", type="primary"):
        res = requests.delete(f"{API}/users/{user_id}")
        if res.status_code == 200:
            st.success("✅ User deleted.")
        elif res.status_code == 404:
            st.error("User not found.")
        else:
            st.error(res.text)


elif page == "🚗 Cars":
    st.header("🚗 All Cars")
    brand_f = st.text_input("Filter by brand")
    params  = {}
    if brand_f: params["brand"] = brand_f

    cars = requests.get(f"{API}/cars", params=params).json().get("cars", [])
    st.write(f"**{len(cars)} car(s) found**")
    if cars:
        st.dataframe(pd.DataFrame(cars), use_container_width=True, hide_index=True)
    else:
        st.info("No cars found.")


elif page == "➕ Add Car":
    st.header("➕ Add a Car")
    users = fetch_users()
    user_options = {"None": None} | {u["name"]: u["id"] for u in users}

    with st.form("add_car"):
        col1, col2 = st.columns(2)
        name      = col1.text_input("Car Name *")
        brand     = col2.text_input("Brand *")
        serie     = col1.text_input("Serie *")
        year      = col2.number_input("Year *", min_value=1900, max_value=2100, value=2020)
        owner     = st.selectbox("Assign to User", list(user_options.keys()))
        submitted = st.form_submit_button("Add Car")

    if submitted:
        if not name or not brand or not serie:
            st.warning("Name, Brand and Serie are required.")
        else:
            res = requests.post(f"{API}/cars", json={
                "name": name, "brand": brand, "serie": serie,
                "year": year, "user_id": user_options[owner]
            })
            if res.status_code == 201:
                st.success(f"✅ {brand} {name} added!")
            else:
                st.error(res.json().get("detail", res.text))


elif page == "✏️ Edit Car":
    st.header("✏️ Edit a Car")
    car_id = st.number_input("Car ID", min_value=1, step=1)

    if st.button("Load"):
        res = requests.get(f"{API}/cars/{car_id}")
        if res.status_code == 200:
            st.session_state["loaded_car"] = res.json()
        else:
            st.error("Car not found.")

    if "loaded_car" in st.session_state:
        car   = st.session_state["loaded_car"]
        users = fetch_users()
        user_options = {"None": None} | {u["name"]: u["id"] for u in users}
        current_owner = next((k for k, v in user_options.items() if v == car.get("user_id")), "None")

        with st.form("edit_car"):
            col1, col2 = st.columns(2)
            name  = col1.text_input("Car Name", value=car["name"])
            brand = col2.text_input("Brand",    value=car["brand"])
            serie = col1.text_input("Serie",    value=car["serie"])
            year  = col2.number_input("Year",   value=car["year"], min_value=1900, max_value=2100)
            owner = st.selectbox("Assign to User", list(user_options.keys()),
                                 index=list(user_options.keys()).index(current_owner))
            saved = st.form_submit_button("Save")

        if saved:
            res = requests.put(f"{API}/cars/{car_id}", json={
                "name": name, "brand": brand, "serie": serie,
                "year": year, "user_id": user_options[owner]
            })
            if res.status_code == 200:
                st.success("✅ Car updated!")
                del st.session_state["loaded_car"]
            else:
                st.error(res.text)

elif page == "🗑️ Delete Car":
    st.header("🗑️ Delete a Car")
    car_id = st.number_input("Car ID", min_value=1, step=1)
    if st.button("🗑️ Delete", type="primary"):
        res = requests.delete(f"{API}/cars/{car_id}")
        if res.status_code == 200:
            st.success("✅ Car deleted.")
        elif res.status_code == 404:
            st.error("Car not found.")
        else:
            st.error(res.text)


elif page == "🔍 Car Scraper":
    st.header("🔍 Car Scraper")
    st.markdown(
        "Search for cars using **free public APIs** (NHTSA + CarQuery). "
        "No API key required. Results can be imported into your Car Management system."
    )

    HEADERS = {"User-Agent": "CarManagementApp/1.0"}


    @st.cache_data(ttl=3600)
    def get_all_makes():
        """Fetch all car makes from NHTSA."""
        try:
            url = "https://vpic.nhtsa.dot.gov/api/vehicles/getallmakes?format=json"
            res = requests.get(url, headers=HEADERS, timeout=10)
            data = res.json()
            makes = sorted([m["Make_Name"].title() for m in data.get("Results", [])])
            return makes
        except Exception:
            return []

    @st.cache_data(ttl=3600)
    def get_models_for_make(make: str):
        """Fetch all models for a given make from NHTSA."""
        try:
            url = f"https://vpic.nhtsa.dot.gov/api/vehicles/getmodelsformake/{urllib.parse.quote(make)}?format=json"
            res = requests.get(url, headers=HEADERS, timeout=10)
            data = res.json()
            models = sorted([m["Model_Name"] for m in data.get("Results", [])])
            return models
        except Exception:
            return []

    @st.cache_data(ttl=3600)
    def search_carquery(make: str, model: str, year: int):
        """Search CarQuery API for trim/spec data."""
        try:
            params = {"cmd": "getTrims", "make": make.lower(), "model": model.lower(), "year": str(year)}
            url = "https://www.carqueryapi.com/api/0.3/?" + urllib.parse.urlencode(params)
            res = requests.get(url, headers=HEADERS, timeout=10)
            text = res.text.strip()
            # CarQuery wraps in callback sometimes
            if text.startswith("("):
                text = text[1:-1]
            data = __import__("json").loads(text)
            return data.get("Trims", [])
        except Exception:
            return []

    def search_nhtsa_recalls(make: str, model: str, year: int):
        """Search NHTSA for safety recalls."""
        try:
            url = f"https://api.nhtsa.gov/recalls/recallsByVehicle?make={urllib.parse.quote(make)}&model={urllib.parse.quote(model)}&modelYear={year}"
            res = requests.get(url, headers=HEADERS, timeout=10)
            return res.json().get("results", [])
        except Exception:
            return []

    def search_nhtsa_complaints(make: str, model: str, year: int):
        """Search NHTSA for safety complaints."""
        try:
            url = f"https://api.nhtsa.gov/complaints/complaintsByVehicle?make={urllib.parse.quote(make)}&model={urllib.parse.quote(model)}&modelYear={year}"
            res = requests.get(url, headers=HEADERS, timeout=10)
            return res.json().get("results", [])
        except Exception:
            return []

    st.subheader("🔎 Search Vehicle Information")

    with st.spinner("Loading makes from NHTSA..."):
        all_makes = get_all_makes()

    col1, col2, col3 = st.columns(3)

    if all_makes:
        make_input = col1.selectbox("Make (Brand)", [""] + all_makes, index=0)
    else:
        make_input = col1.text_input("Make (Brand)", placeholder="e.g. Toyota")

    models_list = []
    if make_input:
        with st.spinner(f"Loading models for {make_input}..."):
            models_list = get_models_for_make(make_input)

    if models_list:
        model_input = col2.selectbox("Model", [""] + models_list, index=0)
    else:
        model_input = col2.text_input("Model", placeholder="e.g. Camry")

    year_input = col3.number_input("Year", min_value=1990, max_value=2025, value=2020)

    search_btn = st.button("🔍 Search", type="primary")

    if search_btn and make_input and model_input:
        st.session_state["search_make"]  = make_input
        st.session_state["search_model"] = model_input
        st.session_state["search_year"]  = year_input

        with st.spinner("Fetching vehicle data..."):
            trims    = search_carquery(make_input, model_input, year_input)
            recalls  = search_nhtsa_recalls(make_input, model_input, year_input)
            complaints = search_nhtsa_complaints(make_input, model_input, year_input)

        st.session_state["scraper_trims"]      = trims
        st.session_state["scraper_recalls"]    = recalls
        st.session_state["scraper_complaints"] = complaints

    elif search_btn:
        st.warning("Please select both a Make and a Model.")

    if "scraper_trims" in st.session_state:
        make_s  = st.session_state["search_make"]
        model_s = st.session_state["search_model"]
        year_s  = st.session_state["search_year"]
        trims      = st.session_state["scraper_trims"]
        recalls    = st.session_state["scraper_recalls"]
        complaints = st.session_state["scraper_complaints"]

        st.divider()
        st.subheader(f"Results for {year_s} {make_s} {model_s}")

        tab1, tab2, tab3 = st.tabs(["🔧 Trims & Specs", "⚠️ Recalls", "📋 Complaints"])

        with tab1:
            if trims:
                st.success(f"Found **{len(trims)}** trim(s)")
                trim_rows = []
                for t in trims:
                    trim_rows.append({
                        "Trim":        t.get("model_trim", "Base"),
                        "Engine":      t.get("model_engine_cc", "N/A"),
                        "HP":          t.get("model_engine_power_ps", "N/A"),
                        "Cylinders":   t.get("model_engine_cyl", "N/A"),
                        "Fuel":        t.get("model_engine_fuel", "N/A"),
                        "Drive":       t.get("model_drive", "N/A"),
                        "Transmission":t.get("model_transmission_type", "N/A"),
                        "Doors":       t.get("model_doors", "N/A"),
                        "Seats":       t.get("model_seats", "N/A"),
                        "0-60 (s)":    t.get("model_0_to_100_kph", "N/A"),
                        "Top Speed":   t.get("model_top_speed_kph", "N/A"),
                        "Weight (kg)": t.get("model_weight_kg", "N/A"),
                    })
                st.dataframe(pd.DataFrame(trim_rows), use_container_width=True, hide_index=True)
            else:
                st.info("No trim data found from CarQuery for this vehicle. Try a different year or popular model.")

        with tab2:
            if recalls:
                st.warning(f"⚠️ Found **{len(recalls)}** recall(s)")
                recall_rows = []
                for r in recalls:
                    recall_rows.append({
                        "Date":        r.get("reportReceivedDate", "N/A")[:10] if r.get("reportReceivedDate") else "N/A",
                        "Component":   r.get("component", "N/A"),
                        "Summary":     r.get("summary", "N/A")[:120] + "..." if len(r.get("summary","")) > 120 else r.get("summary","N/A"),
                        "Consequence": r.get("consequence", "N/A")[:100] + "..." if len(r.get("consequence","")) > 100 else r.get("consequence","N/A"),
                        "NHTSA ID":    r.get("nhtsaCampaignNumber", "N/A"),
                    })
                st.dataframe(pd.DataFrame(recall_rows), use_container_width=True, hide_index=True)
            else:
                st.success("✅ No recalls found for this vehicle.")

        with tab3:
            if complaints:
                st.info(f"📋 Found **{len(complaints)}** complaint(s)")
                comp_rows = []
                for c in complaints:
                    comp_rows.append({
                        "Date":      str(c.get("dateOfIncident", "N/A"))[:10],
                        "Component": c.get("components", "N/A"),
                        "Summary":   c.get("description", "N/A")[:150] + "..." if len(c.get("description","")) > 150 else c.get("description","N/A"),
                        "Injuries":  c.get("numberOfInjuries", 0),
                        "Deaths":    c.get("numberOfDeaths", 0),
                    })
                df_comp = pd.DataFrame(comp_rows)
                st.dataframe(df_comp, use_container_width=True, hide_index=True)

                if "Component" in df_comp.columns:
                    st.subheader("📊 Complaints by Component")
                    st.bar_chart(df_comp["Component"].value_counts())
            else:
                st.success("✅ No complaints found for this vehicle.")

        st.divider()

        st.subheader("📥 Import into Car Management")
        users = fetch_users()
        user_options = {"None": None} | {u["name"]: u["id"] for u in users}

        trim_names = [t.get("model_trim", "Base") for t in trims] if trims else ["Base"]

        with st.form("import_scraped_car"):
            ic1, ic2 = st.columns(2)
            imp_name  = ic1.text_input("Car Name",  value=model_s)
            imp_brand = ic2.text_input("Brand",     value=make_s)
            imp_serie = ic1.selectbox("Serie / Trim", trim_names) if trim_names else ic1.text_input("Serie", value="Base")
            imp_year  = ic2.number_input("Year", min_value=1900, max_value=2100, value=int(year_s))
            imp_owner = st.selectbox("Assign to User", list(user_options.keys()))
            import_btn = st.form_submit_button("📥 Import Car", type="primary")

        if import_btn:
            res = requests.post(f"{API}/cars", json={
                "name": imp_name, "brand": imp_brand, "serie": imp_serie,
                "year": imp_year, "user_id": user_options[imp_owner]
            })
            if res.status_code == 201:
                st.success(f"✅ '{imp_brand} {imp_name} {imp_serie}' imported!")
                st.balloons()
            else:
                st.error(res.json().get("detail", res.text))

