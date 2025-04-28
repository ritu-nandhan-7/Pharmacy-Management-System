import streamlit as st
import sqlite3
import pandas as pd
import requests
import time
from math import radians, cos, sin, asin, sqrt

import base64

def set_background(image_file):
    with open(image_file, "rb") as img:
        encoded = base64.b64encode(img.read()).decode()
    st.markdown(f"""
    <style>
    body, .stApp {{
        background-image: url("data:image/jpg;base64,{encoded}");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
        background-position: center;
        color: black !important;
    }}
    </style>
    """, unsafe_allow_html=True)


# DB connection
conn = sqlite3.connect("pharmacy.db", check_same_thread=False)
c = conn.cursor()

# Page settings
# Page settings
st.set_page_config(page_title="Pharmacy DB", layout="centered")
set_background("bg.jpg")  # 🔄 Add this line to set the background


# ---------------------- Styling ---------------------- #
st.markdown("""
<style>
    body, .stApp {
        
        color: black !important;
    }

    /* Override top bar/header */
    header.css-18ni7ap {
        background-color: #0e456e !important;
    }

    html, body, [class*="css"] {
        font-family: 'Georgia', serif !important;
        color: black !important;
    }

    .stTextInput > div > input,
    .stNumberInput > div > input,
    .stDateInput > div > input,
    .stSelectbox > div > div,
    textarea {
        background-color: black !important;
        color: white !important;
    }

    .stButton > button {
        font-size: 16px !important;
        background-color: #0e619e !important;
        color: white !important;
        padding: 10px 20px;
        border-radius: 10px;
    }

    .stTabs [role="tablist"] {
        border-bottom: 2px solid #7c1b54 !important;
    }

    /* Ensuring radio and select texts are black */
    .stRadio > div label, .stSelectbox label {
        color: black !important;
    }

    h1, h2, h3, h4, h5, h6, p, label, span {
        color: black !important;
    }
</style>
""", unsafe_allow_html=True)




# ---------------------- Helper Functions ---------------------- #

def get_coordinates(address):
    url = f"https://nominatim.openstreetmap.org/search?q={address}&format=json"
    headers = {"User-Agent": "PharmaApp/1.0"}
    try:
        response = requests.get(url, headers=headers).json()
        if response:
            return float(response[0]['lat']), float(response[0]['lon'])
    except:
        return None, None
    return None, None

def haversine(lat1, lon1, lat2, lon2):
    if None in [lat1, lon1, lat2, lon2]:
        return 0
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 6371 * 2 * asin(sqrt(a))

def login(username, password, role):
    c.execute("SELECT * FROM users WHERE username=? AND password=? AND user_type=?", (username, password, role))
    return c.fetchone() is not None

def register(username, password, role):
    try:
        c.execute("INSERT INTO users (username, password, user_type) VALUES (?, ?, ?)", (username, password, role))
        conn.commit()
        return True
    except:
        return False

# ---------------------- Session Init ---------------------- #
if "page" not in st.session_state:
    st.session_state.page = "role"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""

# ---------------------- Navigation ---------------------- #
def go_to(page):
    st.session_state.page = page

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.session_state.page = "role"
    st.rerun()

# ---------------------- Pages ---------------------- #

# 🔘 Role Selection Page
if st.session_state.page == "role":
    # Centered title
    st.markdown("<h1 style='text-align:center;color:#7c1b54;'>Welcome to Pharmacy DB</h1>", unsafe_allow_html=True)

    # Centered subheading
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <h3 style='color:black;'>Please choose your role:</h3>
    </div>
    """, unsafe_allow_html=True)

    # Centered radio buttons
    col1, col2, col3 = st.columns([1, 0.8, 1])
    with col2:
        role = st.radio(" ", ["User", "Admin"], horizontal=True, label_visibility="collapsed")

    # Move button slightly to the right
    col1, col2, col3 = st.columns([1, 0.6, 1])
    with col2:
        if st.button("Continue"):
            st.session_state.role = role.lower()
            go_to("login")
            st.rerun()





# 🔐 Login Page
elif st.session_state.page == "login":
    st.markdown(f"<h2 style='text-align:center;color:#7c1b54;'> {st.session_state.role.capitalize()} Login</h2>", unsafe_allow_html=True)
    username = st.text_input(" Username")
    password = st.text_input(" Password", type="password")
    if st.button("Login"):
        if login(username, password, st.session_state.role):
            st.success("✅ Login successful!")
            st.session_state.logged_in = True
            st.session_state.username = username
            go_to("dashboard")
            st.rerun()
        else:
            st.error("❌ Invalid credentials.")
    if st.button("Sign Up"):
        go_to("signup")
        st.rerun()

# 📝 Signup Page
elif st.session_state.page == "signup":
    st.markdown(f"<h2 style='text-align:center;color:#7c1b54;'> {st.session_state.role.capitalize()} Sign Up</h2>", unsafe_allow_html=True)
    new_user = st.text_input(" New Username")
    new_pass = st.text_input(" New Password", type="password")
    if st.button("Create Account"):
        if register(new_user, new_pass, st.session_state.role):
            st.success("✅ Account created! Redirecting to login...")
            time.sleep(2)
            go_to("login")
            st.rerun()
        else:
            st.error("❌ Username already exists.")

# 🧾 Dashboard
elif st.session_state.page == "dashboard":
    st.title(f" Hello, {st.session_state.username}!")
    st.button(" Logout", on_click=logout)

    # Fill in missing coordinates
    c.execute("SELECT pharmacy_id, address FROM pharmacy WHERE latitude IS NULL OR longitude IS NULL")
    missing_coords = c.fetchall()
    for pid, address in missing_coords:
        lat, lon = get_coordinates(address)
        if lat and lon:
            c.execute("UPDATE pharmacy SET latitude=?, longitude=? WHERE pharmacy_id=?", (lat, lon, pid))
            conn.commit()

    if st.session_state.role == "user":
        tab1, tab2 = st.tabs([" Search Medicine", " My Profile"])

        with tab1:
            st.subheader("Find Medicine Nearby")
            medicine = st.text_input(" Enter medicine name")
            location = st.text_input(" Enter your location")

            if st.button("Search"):
                lat, lon = get_coordinates(location)
                if lat is None or lon is None:
                    st.error("❌ Invalid location. Please enter a valid address.")
                else:
                    c.execute("""
                        SELECT m.name, m.price, p.name, p.address, p.latitude, p.longitude
                        FROM medicine m
                        JOIN availability a ON m.medicine_id = a.medicine_id
                        JOIN pharmacy p ON a.pharmacy_id = p.pharmacy_id
                        WHERE m.name LIKE ?
                    """, ('%' + medicine + '%',))
                    rows = c.fetchall()
                    result = []
                    for mname, price, pname, address, plat, plon in rows:
                        dist = haversine(lat, lon, plat, plon) if plat and plon else None
                        result.append((mname, f"₹{price:.2f}", pname, address, f"{dist:.2f} km" if dist else "N/A"))

                    if result:
                        df = pd.DataFrame(result, columns=["Medicine", "Price", "Pharmacy", "Address", "Distance"])
                        df["DistanceNum"] = df["Distance"].apply(lambda x: float(x.split()[0]) if x != "N/A" else float("inf"))
                        df = df.sort_values(by="DistanceNum").drop("DistanceNum", axis=1)
                        st.dataframe(df, use_container_width=True)
                    else:
                        st.warning("No matching medicine found.")

        with tab2:
            st.info("📄 Profile info and future features coming soon.")

    elif st.session_state.role == "admin":
        tab1, tab2 = st.tabs([" Add Medicine", " View All Medicines"])

        with tab1:
            st.subheader("Add New Medicine")
            med_name = st.text_input("Medicine Name")
            med_price = st.number_input("Price (₹)", min_value=0.0, format="%.2f")
            med_exp = st.date_input("Expiry Date")
            med_qty = st.number_input("Quantity", min_value=0)

            c.execute("SELECT pharmacy_id, name FROM pharmacy")
            pharmacies = c.fetchall()
            if pharmacies:
                options = [f"{pname} (ID: {pid})" for pid, pname in pharmacies]
                selected = st.selectbox("Select Pharmacy", options)
                selected_id = int(selected.split("ID: ")[1].strip(")"))
                if st.button("Add Medicine"):
                    c.execute("INSERT INTO medicine (name, price, expiry_date, quantity) VALUES (?, ?, ?, ?)",
                              (med_name, med_price, med_exp, med_qty))
                    conn.commit()
                    med_id = c.lastrowid
                    c.execute("INSERT INTO availability (pharmacy_id, medicine_id) VALUES (?, ?)",
                              (selected_id, med_id))
                    conn.commit()
                    st.success("✅ Medicine added.")
            else:
                st.warning("No pharmacies available.")

        with tab2:
            c.execute("""
                SELECT m.name, m.price, m.expiry_date, m.quantity, p.name
                FROM medicine m
                JOIN availability a ON m.medicine_id = a.medicine_id
                JOIN pharmacy p ON a.pharmacy_id = p.pharmacy_id
            """)
            meds = c.fetchall()
            if meds:
                df = pd.DataFrame(meds, columns=["Name", "Price", "Expiry", "Qty", "Pharmacy"])
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("No medicines in database.")
