import streamlit as st
import requests
import pandas as pd

API = "http://localhost:8000"

st.set_page_config(page_title="🚗 Car Management", layout="wide")
st.title("🚗 Car Management System")

page = st.sidebar.radio("Navigation", [
    "📊 Dashboard",
    "👤 Users",     "➕ Add User",  "✏️ Edit User",  "🗑️ Delete User",
    "🚗 Cars",      "➕ Add Car",   "✏️ Edit Car",   "🗑️ Delete Car",
])


def fetch_users():
    return requests.get(f"{API}/users").json().get("users", [])

def fetch_cars():
    return requests.get(f"{API}/cars").json().get("cars", [])


# ─────────────────────────────────────────────────────────────────────────────
# 📊 DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
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


# ─────────────────────────────────────────────────────────────────────────────
# 👤 USERS LIST
# ─────────────────────────────────────────────────────────────────────────────
elif page == "👤 Users":
    st.header("👤 All Users")
    users = fetch_users()
    if users:
        st.dataframe(pd.DataFrame(users), use_container_width=True, hide_index=True)
    else:
        st.info("No users yet. Add one from the sidebar!")


# ─────────────────────────────────────────────────────────────────────────────
# ➕ ADD USER
# ─────────────────────────────────────────────────────────────────────────────
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


# ─────────────────────────────────────────────────────────────────────────────
# ✏️ EDIT USER
# ─────────────────────────────────────────────────────────────────────────────
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


# ─────────────────────────────────────────────────────────────────────────────
# 🗑️ DELETE USER
# ─────────────────────────────────────────────────────────────────────────────
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


# ─────────────────────────────────────────────────────────────────────────────
# 🚗 CARS LIST
# ─────────────────────────────────────────────────────────────────────────────
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


# ─────────────────────────────────────────────────────────────────────────────
# ➕ ADD CAR
# ─────────────────────────────────────────────────────────────────────────────
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


# ─────────────────────────────────────────────────────────────────────────────
# ✏️ EDIT CAR
# ─────────────────────────────────────────────────────────────────────────────
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


# ─────────────────────────────────────────────────────────────────────────────
# 🗑️ DELETE CAR
# ─────────────────────────────────────────────────────────────────────────────
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
