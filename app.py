import streamlit as st
import sqlite3
import hashlib
import pandas as pd
from datetime import datetime

DB_NAME = "property_dealer.db"

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="Luxury Property CRM",
    page_icon="🏠",
    layout="wide"
)

# ---------------- PREMIUM ULTRA UI ----------------

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* {
    font-family: 'Inter', sans-serif;
}

/* Background */

.stApp {
    background:
    radial-gradient(circle at top left, rgba(99,102,241,0.18), transparent 30%),
    radial-gradient(circle at top right, rgba(236,72,153,0.15), transparent 30%),
    linear-gradient(135deg, #f8fafc 0%, #eef2ff 45%, #fdf2f8 100%);
}

/* Main Container */

.block-container {
    max-width: 1280px;
    padding-top: 2rem;
}

/* Sidebar */

section[data-testid="stSidebar"] {
    background: rgba(15,23,42,0.95);
    backdrop-filter: blur(20px);
    border-right: 1px solid rgba(255,255,255,0.08);
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

section[data-testid="stSidebar"] .stRadio > div {
    background: rgba(255,255,255,0.05);
    padding: 14px;
    border-radius: 18px;
}

/* Hero Card */

.hero-card {
    background:
    linear-gradient(
        135deg,
        rgba(37,99,235,0.98),
        rgba(124,58,237,0.95),
        rgba(219,39,119,0.92)
    );

    padding: 38px;
    border-radius: 32px;
    color: white;

    box-shadow:
    0 25px 60px rgba(79,70,229,0.35);

    margin-bottom: 28px;
}

.hero-card h1 {
    color: white !important;
    font-size: 40px;
    font-weight: 800;
    margin-bottom: 10px;
}

.hero-card p {
    color: #eef2ff !important;
    font-size: 17px;
}

/* Titles */

h1,h2,h3 {
    color: #0f172a !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em;
}

/* Glass Cards */

.card {
    background: rgba(255,255,255,0.72);

    backdrop-filter: blur(22px);

    border: 1px solid rgba(255,255,255,0.75);

    border-radius: 28px;

    padding: 26px;

    box-shadow:
    0 18px 45px rgba(15,23,42,0.08),
    inset 0 1px 0 rgba(255,255,255,0.7);

    margin-bottom: 24px;
}

/* Metrics */

[data-testid="metric-container"] {

    background: rgba(255,255,255,0.78);

    backdrop-filter: blur(20px);

    border-radius: 26px;

    padding: 24px;

    border: 1px solid rgba(255,255,255,0.8);

    box-shadow:
    0 18px 45px rgba(15,23,42,0.08);
}

[data-testid="metric-container"] label {
    color: #64748b !important;
    font-weight: 700;
}

[data-testid="stMetricValue"] {
    color: #111827 !important;
    font-weight: 900;
}

/* Inputs */

.stTextInput input,
.stNumberInput input,
textarea {

    background: rgba(255,255,255,0.92) !important;

    border: 1px solid #cbd5e1 !important;

    border-radius: 16px !important;

    color: #0f172a !important;

    padding: 13px !important;
}

.stTextInput input:focus,
.stNumberInput input:focus,
textarea:focus {

    border: 1px solid #6366f1 !important;

    box-shadow:
    0 0 0 4px rgba(99,102,241,0.16) !important;
}

/* Selectbox */

.stSelectbox div[data-baseweb="select"] {

    background: rgba(255,255,255,0.92) !important;

    border-radius: 16px !important;

    border: 1px solid #cbd5e1 !important;
}

/* Buttons */

.stButton>button,
.stFormSubmitButton>button {

    background:
    linear-gradient(
        135deg,
        #2563eb,
        #7c3aed,
        #db2777
    );

    color: white !important;

    border: none;

    border-radius: 16px;

    padding: 13px 22px;

    font-weight: 800;

    transition: all 0.25s ease;

    box-shadow:
    0 15px 35px rgba(124,58,237,0.28);
}

.stButton>button:hover,
.stFormSubmitButton>button:hover {

    transform: translateY(-3px);

    box-shadow:
    0 22px 42px rgba(124,58,237,0.38);
}

/* Download Button */

.stDownloadButton>button {

    background:
    linear-gradient(135deg,#0f172a,#334155);

    color: white !important;

    border: none;

    border-radius: 16px;

    padding: 13px 22px;

    font-weight: 800;
}

/* Dataframes */

[data-testid="stDataFrame"] {

    background: rgba(255,255,255,0.82);

    border-radius: 24px;

    border: 1px solid rgba(255,255,255,0.8);

    overflow: hidden;

    box-shadow:
    0 18px 42px rgba(15,23,42,0.08);
}

/* Tabs */

.stTabs [data-baseweb="tab-list"] {
    gap: 12px;
}

.stTabs [data-baseweb="tab"] {

    background: rgba(255,255,255,0.7);

    border-radius: 18px;

    padding: 12px 22px;

    border: 1px solid rgba(255,255,255,0.85);

    font-weight: 800;
}

.stTabs [aria-selected="true"] {

    background:
    linear-gradient(135deg,#2563eb,#7c3aed) !important;

    color: white !important;
}

/* Alerts */

.stSuccess,
.stWarning,
.stError,
.stInfo {

    border-radius: 18px;
}

/* Hide Streamlit */

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
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

# ---------------- USERS ----------------

def signup_user(name,email,phone,password,agency_name):

    conn = get_conn()
    c = conn.cursor()

    try:

        c.execute("""
        INSERT INTO users
        (name,email,phone,password,agency_name,city,address,created_at)
        VALUES (?,?,?,?,?,?,?,?)
        """,(
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

def login_user(email,password):

    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    SELECT id,name,email,phone,agency_name,city,address
    FROM users
    WHERE email=? AND password=?
    """,(email,hash_password(password)))

    user = c.fetchone()

    conn.close()

    return user

def update_profile(user_id,name,phone,agency_name,city,address):

    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    UPDATE users
    SET name=?, phone=?, agency_name=?, city=?, address=?
    WHERE id=?
    """,(name,phone,agency_name,city,address,user_id))

    conn.commit()
    conn.close()

def get_user(user_id):

    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    SELECT id,name,email,phone,agency_name,city,address
    FROM users
    WHERE id=?
    """,(user_id,))

    user = c.fetchone()

    conn.close()

    return user

# ---------------- PROPERTIES ----------------

def add_property(user_id,title,deal_type,property_type,location,area_size,
                 price,owner_name,owner_contact,status,description):

    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    INSERT INTO properties
    (user_id,title,deal_type,property_type,location,area_size,price,
    owner_name,owner_contact,status,description,created_at)

    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """,(
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
    SELECT *
    FROM properties
    WHERE user_id=?
    ORDER BY id DESC
    """,conn,params=(user_id,))

    conn.close()

    return df

# ---------------- SESSION ----------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

# ---------------- HERO ----------------

st.markdown("""
<div class="hero-card">
    <h1>🏠 Luxury Property CRM</h1>
    <p>
    Premium real estate management dashboard for dealers,
    agencies and property businesses.
    </p>
</div>
""", unsafe_allow_html=True)

# ---------------- LOGIN ----------------

if not st.session_state.logged_in:

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:

        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.subheader("Welcome Back")

        email = st.text_input("Email")

        password = st.text_input(
            "Password",
            type="password"
        )

        if st.button("Login"):

            user = login_user(email,password)

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

        st.subheader("Create Account")

        name = st.text_input("Name")

        email = st.text_input("Email", key="signup_email")

        phone = st.text_input("Phone")

        agency = st.text_input("Agency Name")

        password = st.text_input(
            "Password",
            type="password",
            key="signup_password"
        )

        if st.button("Create Account"):

            if name and email and phone and password:

                created = signup_user(
                    name,
                    email,
                    phone,
                    password,
                    agency
                )

                if created:
                    st.success("Account created successfully")
                else:
                    st.error("Email already exists")

            else:
                st.warning("Fill all required fields")

        st.markdown('</div>', unsafe_allow_html=True)

# ---------------- DASHBOARD ----------------

else:

    user = get_user(st.session_state.user_id)

    st.sidebar.title("🏢 Dealer Panel")

    st.sidebar.success(user[1])

    menu = st.sidebar.radio(
        "Navigation",
        [
            "Dashboard",
            "Profile",
            "Add Property",
            "View Properties",
            "Export Data"
        ]
    )

    if st.sidebar.button("Logout"):

        st.session_state.logged_in = False
        st.session_state.user_id = None

        st.rerun()

    # DASHBOARD

    if menu == "Dashboard":

        st.subheader("Dashboard Overview")

        df = get_properties(st.session_state.user_id)

        col1,col2,col3,col4 = st.columns(4)

        col1.metric("Total", len(df))

        col2.metric(
            "Available",
            len(df[df["status"]=="Available"]) if not df.empty else 0
        )

        col3.metric(
            "Sold",
            len(df[df["status"]=="Sold"]) if not df.empty else 0
        )

        col4.metric(
            "Rented",
            len(df[df["status"]=="Rented"]) if not df.empty else 0
        )

        st.markdown("""
        <div class="card">
        <h3>Premium Real Estate CRM</h3>
        <p>
        Manage your dealer profile, properties,
        owner records, prices and locations professionally.
        </p>
        </div>
        """, unsafe_allow_html=True)

        if not df.empty:

            st.markdown('<div class="card">', unsafe_allow_html=True)

            st.subheader("Recent Properties")

            st.dataframe(df.head(5), use_container_width=True)

            st.markdown('</div>', unsafe_allow_html=True)

    # PROFILE

    elif menu == "Profile":

        st.subheader("Dealer Profile")

        st.markdown('<div class="card">', unsafe_allow_html=True)

        with st.form("profile_form"):

            name = st.text_input("Name", user[1])

            email = st.text_input(
                "Email",
                user[2],
                disabled=True
            )

            phone = st.text_input("Phone", user[3])

            agency = st.text_input("Agency", user[4])

            city = st.text_input("City", user[5])

            address = st.text_area("Address", user[6])

            submit = st.form_submit_button("Save Profile")

            if submit:

                update_profile(
                    st.session_state.user_id,
                    name,
                    phone,
                    agency,
                    city,
                    address
                )

                st.success("Profile updated")

                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # ADD PROPERTY

    elif menu == "Add Property":

        st.subheader("Add New Property")

        st.markdown('<div class="card">', unsafe_allow_html=True)

        with st.form("property_form"):

            col1,col2 = st.columns(2)

            with col1:

                title = st.text_input("Property Title")

                deal_type = st.selectbox(
                    "Deal Type",
                    ["Sale","Rent"]
                )

                property_type = st.selectbox(
                    "Property Type",
                    ["House","Flat","Plot","Shop","Office"]
                )

                location = st.text_input("Location")

                area_size = st.text_input("Area Size")

            with col2:

                price = st.number_input(
                    "Price",
                    min_value=0.0
                )

                owner_name = st.text_input("Owner Name")

                owner_contact = st.text_input("Owner Contact")

                status = st.selectbox(
                    "Status",
                    ["Available","Sold","Rented"]
                )

                description = st.text_area("Description")

            submit = st.form_submit_button("Save Property")

            if submit:

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

                st.success("Property added successfully")

        st.markdown('</div>', unsafe_allow_html=True)

    # VIEW

    elif menu == "View Properties":

        st.subheader("All Properties")

        df = get_properties(st.session_state.user_id)

        if df.empty:
            st.info("No properties found")

        else:

            st.markdown('<div class="card">', unsafe_allow_html=True)

            st.dataframe(df, use_container_width=True)

            st.markdown('</div>', unsafe_allow_html=True)

    # EXPORT

    elif menu == "Export Data":

        st.subheader("Export Data")

        df = get_properties(st.session_state.user_id)

        if df.empty:

            st.info("No data available")

        else:

            csv = df.to_csv(index=False).encode("utf-8")

            st.download_button(
                "Download CSV",
                csv,
                "properties.csv",
                "text/csv"
            )
