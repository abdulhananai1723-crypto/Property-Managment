import streamlit as st
import sqlite3
import hashlib
import pandas as pd
from datetime import datetime

DB_NAME = "property_dealer.db"

st.set_page_config(
    page_title="Property Dealer App",
    page_icon="🏠",
    layout="wide"
)

# ---------------- PROFESSIONAL THEME ----------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #f4f7fb;
    color: #0f172a;
}

.block-container {
    padding-top: 1.8rem;
    padding-left: 2rem;
    padding-right: 2rem;
    max-width: 1200px;
}

section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid #e5e7eb;
}

section[data-testid="stSidebar"] * {
    color: #0f172a !important;
}

h1 {
    color: #0f172a !important;
    font-weight: 800 !important;
    letter-spacing: -0.04em;
}

h2, h3 {
    color: #111827 !important;
    font-weight: 700 !important;
}

p, label, span {
    color: #334155 !important;
}

.hero-card {
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    padding: 30px;
    border-radius: 24px;
    color: white;
    box-shadow: 0 20px 45px rgba(37, 99, 235, 0.22);
    margin-bottom: 24px;
}

.hero-card h2 {
    color: white !important;
    margin-bottom: 8px;
}

.hero-card p {
    color: #e0e7ff !important;
    font-size: 16px;
}

.card {
    background: #ffffff;
    padding: 24px;
    border-radius: 22px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
    margin-bottom: 20px;
}

[data-testid="metric-container"] {
    background: #ffffff;
    border-radius: 22px;
    padding: 22px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
}

[data-testid="metric-container"] label {
    color: #64748b !important;
    font-weight: 600;
}

[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #0f172a !important;
    font-weight: 800;
}

.stTextInput input,
.stNumberInput input,
textarea {
    background-color: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 14px !important;
    color: #0f172a !important;
    padding: 12px !important;
}

.stTextInput input:focus,
.stNumberInput input:focus,
textarea:focus {
    border: 1px solid #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.12) !important;
}

.stSelectbox div[data-baseweb="select"] {
    background: #ffffff !important;
    border-radius: 14px !important;
    border: 1px solid #d1d5db !important;
}

.stButton>button {
    background: linear-gradient(90deg, #2563eb, #7c3aed);
    color: white !important;
    border: none;
    border-radius: 14px;
    padding: 12px 20px;
    font-weight: 700;
    transition: all 0.2s ease;
}

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 25px rgba(37,99,235,0.28);
}

.stDownloadButton>button {
    background: #0f172a;
    color: white !important;
    border: none;
    border-radius: 14px;
    padding: 12px 20px;
    font-weight: 700;
}

[data-testid="stDataFrame"] {
    background: #ffffff;
    border-radius: 20px;
    border: 1px solid #e5e7eb;
    overflow: hidden;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05);
}

.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
}

.stTabs [data-baseweb="tab"] {
    background: #ffffff;
    border-radius: 14px;
    padding: 10px 18px;
    border: 1px solid #e5e7eb;
    font-weight: 700;
}

.stTabs [aria-selected="true"] {
    background: #2563eb !important;
    color: white !important;
}

.stRadio > div {
    background: #ffffff;
    padding: 12px;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
}

.stSuccess, .stWarning, .stError, .stInfo {
    border-radius: 14px;
}

hr {
    border: none;
    border-top: 1px solid #e5e7eb;
}
</style>
""", unsafe_allow_html=True)

# ---------------- DATABASE ----------------

def get_conn():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_tables():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        phone TEXT,
        password TEXT,
        agency_name TEXT,
        city TEXT,
        address TEXT,
        created_at TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS properties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        deal_type TEXT,
        property_type TEXT,
        location TEXT,
        area_size TEXT,
        price REAL,
        owner_name TEXT,
        owner_contact TEXT,
        status TEXT,
        description TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()

create_tables()

# ---------------- USER FUNCTIONS ----------------

def signup_user(name, email, phone, password, agency_name):
    conn = get_conn()
    c = conn.cursor()

    try:
        c.execute("""
        INSERT INTO users 
        (name, email, phone, password, agency_name, city, address, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            email,
            phone,
            hash_password(password),
            agency_name,
            "",
            "",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))

        conn.commit()
        return True

    except sqlite3.IntegrityError:
        return False

    finally:
        conn.close()

def login_user(email, password):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    SELECT id, name, email, phone, agency_name, city, address
    FROM users 
    WHERE email = ? AND password = ?
    """, (email, hash_password(password)))

    user = c.fetchone()
    conn.close()
    return user

def update_profile(user_id, name, phone, agency_name, city, address):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    UPDATE users
    SET name=?, phone=?, agency_name=?, city=?, address=?
    WHERE id=?
    """, (name, phone, agency_name, city, address, user_id))

    conn.commit()
    conn.close()

def get_user(user_id):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    SELECT id, name, email, phone, agency_name, city, address
    FROM users WHERE id=?
    """, (user_id,))

    user = c.fetchone()
    conn.close()
    return user

# ---------------- PROPERTY FUNCTIONS ----------------

def add_property(user_id, title, deal_type, property_type, location, area_size,
                 price, owner_name, owner_contact, status, description):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    INSERT INTO properties
    (user_id, title, deal_type, property_type, location, area_size, price,
     owner_name, owner_contact, status, description, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        title,
        deal_type,
        property_type,
        location,
        area_size,
        price,
        owner_name,
        owner_contact,
        status,
        description,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

def get_properties(user_id):
    conn = get_conn()

    df = pd.read_sql_query("""
    SELECT 
        id,
        title,
        deal_type,
        property_type,
        location,
        area_size,
        price,
        owner_name,
        owner_contact,
        status,
        description,
        created_at
    FROM properties
    WHERE user_id=?
    ORDER BY id DESC
    """, conn, params=(user_id,))

    conn.close()
    return df

def update_property(prop_id, title, deal_type, property_type, location, area_size,
                    price, owner_name, owner_contact, status, description):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    UPDATE properties
    SET title=?, deal_type=?, property_type=?, location=?, area_size=?,
        price=?, owner_name=?, owner_contact=?, status=?, description=?
    WHERE id=?
    """, (
        title,
        deal_type,
        property_type,
        location,
        area_size,
        price,
        owner_name,
        owner_contact,
        status,
        description,
        prop_id
    ))

    conn.commit()
    conn.close()

def delete_property(prop_id):
    conn = get_conn()
    c = conn.cursor()

    c.execute("DELETE FROM properties WHERE id=?", (prop_id,))

    conn.commit()
    conn.close()

# ---------------- SESSION ----------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

# ---------------- HEADER ----------------

st.markdown("""
<div class="hero-card">
    <h2>🏠 Property Dealer Management System</h2>
    <p>Professional dashboard for managing dealer profiles, properties, owners, prices and records.</p>
</div>
""", unsafe_allow_html=True)

# ---------------- LOGIN / SIGNUP ----------------

if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Login to your account")

        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            user = login_user(email, password)

            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user[0]
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Wrong email or password")

        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Create new account")

        name = st.text_input("Your Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone / WhatsApp")
        agency_name = st.text_input("Agency Name")
        password = st.text_input("Password", type="password")

        if st.button("Signup"):
            if name and email and phone and password:
                created = signup_user(name, email, phone, password, agency_name)

                if created:
                    st.success("Account created. Now login.")
                else:
                    st.error("Email already exists.")
            else:
                st.warning("Please fill all required fields.")

        st.markdown('</div>', unsafe_allow_html=True)

# ---------------- MAIN APP ----------------

else:
    user = get_user(st.session_state.user_id)

    st.sidebar.title("🏢 Dealer Panel")
    st.sidebar.caption("Property CRM")
    st.sidebar.success(f"Logged in: {user[1]}")

    menu = st.sidebar.radio(
        "Navigation",
        [
            "Dashboard",
            "Profile",
            "Add Property",
            "View / Search Properties",
            "Edit Property",
            "Delete Property",
            "Export Data"
        ]
    )

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.rerun()

    if menu == "Dashboard":
        st.subheader("Dashboard")

        df = get_properties(st.session_state.user_id)

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Properties", len(df))
        col2.metric("Available", len(df[df["status"] == "Available"]) if not df.empty else 0)
        col3.metric("Sold", len(df[df["status"] == "Sold"]) if not df.empty else 0)
        col4.metric("Rented", len(df[df["status"] == "Rented"]) if not df.empty else 0)

        st.markdown("""
        <div class="card">
            <h3>Welcome to your professional property dashboard</h3>
            <p>
                Yahan aap apni agency profile, property records, owner contacts,
                prices, locations aur property status easily manage kar sakte hain.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if not df.empty:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Recent Properties")
            st.dataframe(df.head(5), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "Profile":
        st.subheader("Dealer Profile")

        st.markdown('<div class="card">', unsafe_allow_html=True)

        with st.form("profile_form"):
            name = st.text_input("Name", user[1])
            email = st.text_input("Email", user[2], disabled=True)
            phone = st.text_input("Phone / WhatsApp", user[3])
            agency_name = st.text_input("Agency Name", user[4])
            city = st.text_input("City / Area", user[5])
            address = st.text_area("Office Address", user[6])

            submit = st.form_submit_button("Save Profile")

            if submit:
                update_profile(
                    st.session_state.user_id,
                    name,
                    phone,
                    agency_name,
                    city,
                    address
                )
                st.success("Profile saved successfully.")
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "Add Property":
        st.subheader("Add New Property")

        st.markdown('<div class="card">', unsafe_allow_html=True)

        with st.form("add_property_form"):
            col1, col2 = st.columns(2)

            with col1:
                title = st.text_input("Property Title")
                deal_type = st.selectbox("Deal Type", ["Sale", "Rent"])
                property_type = st.selectbox(
                    "Property Type",
                    ["House", "Flat", "Plot", "Shop", "Office", "Commercial"]
                )
                location = st.text_input("Location")
                area_size = st.text_input("Area Size e.g. 5 Marla, 10 Marla")

            with col2:
                price = st.number_input("Price", min_value=0.0)
                owner_name = st.text_input("Owner Name")
                owner_contact = st.text_input("Owner Contact")
                status = st.selectbox("Status", ["Available", "Sold", "Rented"])
                description = st.text_area("Description")

            submit = st.form_submit_button("Save Property")

            if submit:
                if title and location and owner_contact:
                    add_property(
                        st.session_state.user_id,
                        title,
                        deal_type,
                        property_type,
                        location,
                        area_size,
                        price,
                        owner_name,
                        owner_contact,
                        status,
                        description
                    )
                    st.success("Property saved successfully.")
                else:
                    st.warning("Title, location aur owner contact zaroor fill karo.")

        st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "View / Search Properties":
        st.subheader("View / Search Properties")

        df = get_properties(st.session_state.user_id)

        if df.empty:
            st.info("Abhi koi property saved nahi hai.")
        else:
            st.markdown('<div class="card">', unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)

            with col1:
                search_location = st.text_input("Search by Location")

            with col2:
                deal_filter = st.selectbox("Deal Type", ["All", "Sale", "Rent"])

            with col3:
                status_filter = st.selectbox("Status", ["All", "Available", "Sold", "Rented"])

            filtered_df = df.copy()

            if search_location:
                filtered_df = filtered_df[
                    filtered_df["location"].str.contains(search_location, case=False, na=False)
                ]

            if deal_filter != "All":
                filtered_df = filtered_df[filtered_df["deal_type"] == deal_filter]

            if status_filter != "All":
                filtered_df = filtered_df[filtered_df["status"] == status_filter]

            st.dataframe(filtered_df, use_container_width=True)

            st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "Edit Property":
        st.subheader("Edit Property")

        df = get_properties(st.session_state.user_id)

        if df.empty:
            st.info("Edit karne ke liye koi property nahi hai.")
        else:
            st.markdown('<div class="card">', unsafe_allow_html=True)

            selected_id = st.selectbox("Select Property ID", df["id"].tolist())
            selected = df[df["id"] == selected_id].iloc[0]

            with st.form("edit_property_form"):
                col1, col2 = st.columns(2)

                with col1:
                    title = st.text_input("Property Title", selected["title"])
                    deal_type = st.selectbox(
                        "Deal Type",
                        ["Sale", "Rent"],
                        index=["Sale", "Rent"].index(selected["deal_type"])
                    )
                    property_type = st.selectbox(
                        "Property Type",
                        ["House", "Flat", "Plot", "Shop", "Office", "Commercial"],
                        index=["House", "Flat", "Plot", "Shop", "Office", "Commercial"].index(selected["property_type"])
                    )
                    location = st.text_input("Location", selected["location"])
                    area_size = st.text_input("Area Size", selected["area_size"])

                with col2:
                    price = st.number_input("Price", min_value=0.0, value=float(selected["price"]))
                    owner_name = st.text_input("Owner Name", selected["owner_name"])
                    owner_contact = st.text_input("Owner Contact", selected["owner_contact"])
                    status = st.selectbox(
                        "Status",
                        ["Available", "Sold", "Rented"],
                        index=["Available", "Sold", "Rented"].index(selected["status"])
                    )
                    description = st.text_area("Description", selected["description"])

                submit = st.form_submit_button("Update Property")

                if submit:
                    update_property(
                        selected_id,
                        title,
                        deal_type,
                        property_type,
                        location,
                        area_size,
                        price,
                        owner_name,
                        owner_contact,
                        status,
                        description
                    )
                    st.success("Property updated successfully.")
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "Delete Property":
        st.subheader("Delete Property")

        df = get_properties(st.session_state.user_id)

        if df.empty:
            st.info("Delete karne ke liye koi property nahi hai.")
        else:
            st.markdown('<div class="card">', unsafe_allow_html=True)

            selected_id = st.selectbox("Select Property ID", df["id"].tolist())
            selected = df[df["id"] == selected_id].iloc[0]

            st.warning(f"Are you sure you want to delete: {selected['title']}?")

            if st.button("Delete Property"):
                delete_property(selected_id)
                st.success("Property deleted successfully.")
                st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "Export Data":
        st.subheader("Export Properties Data")

        df = get_properties(st.session_state.user_id)

        if df.empty:
            st.info("Export ke liye koi data nahi hai.")
        else:
            st.markdown('<div class="card">', unsafe_allow_html=True)

            st.dataframe(df, use_container_width=True)

            csv = df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="properties_data.csv",
                mime="text/csv"
            )

            st.markdown('</div>', unsafe_allow_html=True)
