import streamlit as st
import sqlite3
import hashlib
import pandas as pd
from datetime import datetime
import os

DB_NAME = "property_dealer.db"
UPLOAD_DIR = "property_images"

os.makedirs(UPLOAD_DIR, exist_ok=True)

st.set_page_config(
    page_title="Luxury Property CRM",
    page_icon="🏠",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif; }

.stApp {
    background:
    radial-gradient(circle at top left, rgba(99,102,241,0.18), transparent 30%),
    radial-gradient(circle at top right, rgba(236,72,153,0.15), transparent 30%),
    linear-gradient(135deg,#f8fafc 0%,#eef2ff 45%,#fdf2f8 100%);
}

section[data-testid="stSidebar"] {
    background: rgba(15,23,42,0.95);
    backdrop-filter: blur(20px);
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

.hero-card {
    background: linear-gradient(135deg,#2563eb,#7c3aed,#db2777);
    padding: 38px;
    border-radius: 32px;
    color: white;
    margin-bottom: 28px;
    box-shadow: 0 25px 60px rgba(79,70,229,0.35);
}

.hero-card h1 {
    color: white !important;
    font-size: 40px;
    font-weight: 800;
}

.hero-card p {
    color: #eef2ff !important;
    font-size: 17px;
}

.card {
    background: rgba(255,255,255,0.80);
    backdrop-filter: blur(22px);
    border-radius: 28px;
    padding: 24px;
    margin-bottom: 24px;
    box-shadow: 0 18px 45px rgba(15,23,42,0.08);
}

.stTextInput input,
.stNumberInput input,
textarea {
    border-radius: 16px !important;
    padding: 13px !important;
    border: 1px solid #cbd5e1 !important;
}

.stButton>button,
.stFormSubmitButton>button {
    background: linear-gradient(135deg,#2563eb,#7c3aed,#db2777);
    color: white !important;
    border: none;
    border-radius: 16px;
    padding: 13px 22px;
    font-weight: 800;
}

.stDownloadButton>button {
    background: linear-gradient(135deg,#0f172a,#334155);
    color: white !important;
    border: none;
    border-radius: 16px;
    padding: 13px 22px;
    font-weight: 800;
}

[data-testid="metric-container"] {
    background: rgba(255,255,255,0.85);
    border-radius: 22px;
    padding: 20px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.08);
}

#MainMenu, footer, header {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# ================= DATABASE =================

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
        image_path TEXT DEFAULT '',
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()

def fix_old_database():
    conn = get_conn()
    c = conn.cursor()

    c.execute("PRAGMA table_info(properties)")
    columns = [col[1] for col in c.fetchall()]

    required_columns = {
        "image_path": "TEXT DEFAULT ''",
        "description": "TEXT DEFAULT ''",
        "status": "TEXT DEFAULT 'Available'",
        "owner_contact": "TEXT DEFAULT ''",
        "owner_name": "TEXT DEFAULT ''",
        "price": "REAL DEFAULT 0",
        "area_size": "TEXT DEFAULT ''",
        "location": "TEXT DEFAULT ''",
        "property_type": "TEXT DEFAULT ''",
        "deal_type": "TEXT DEFAULT ''",
        "title": "TEXT DEFAULT ''",
        "created_at": "TEXT DEFAULT ''"
    }

    for col_name, col_type in required_columns.items():
        if col_name not in columns:
            c.execute(f"ALTER TABLE properties ADD COLUMN {col_name} {col_type}")

    conn.commit()
    conn.close()

create_tables()
fix_old_database()


# ================= USER FUNCTIONS =================

def signup_user(name, email, phone, password, agency):
    conn = get_conn()
    c = conn.cursor()

    try:
        c.execute("""
        INSERT INTO users
        (name,email,phone,password,agency_name,city,address,created_at)
        VALUES(?,?,?,?,?,?,?,?)
        """, (
            name, email, phone, hash_password(password),
            agency, "", "",
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
    SELECT id,name,email,phone,agency_name,city,address
    FROM users
    WHERE email=? AND password=?
    """, (email, hash_password(password)))

    user = c.fetchone()
    conn.close()
    return user

def get_user(user_id):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    SELECT id,name,email,phone,agency_name,city,address
    FROM users
    WHERE id=?
    """, (user_id,))

    user = c.fetchone()
    conn.close()
    return user

def update_profile(user_id, name, phone, agency, city, address):
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    UPDATE users
    SET name=?, phone=?, agency_name=?, city=?, address=?
    WHERE id=?
    """, (name, phone, agency, city, address, user_id))

    conn.commit()
    conn.close()


# ================= PROPERTY FUNCTIONS =================

def save_image(uploaded_file):
    if uploaded_file is None:
        return ""

    safe_name = uploaded_file.name.replace(" ", "_")
    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{safe_name}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return filepath

def add_property(user_id, title, deal_type, property_type, location, area_size,
                 price, owner_name, owner_contact, status, description, image_path):

    conn = get_conn()
    c = conn.cursor()

    c.execute("""
    INSERT INTO properties
    (user_id,title,deal_type,property_type,location,area_size,price,
     owner_name,owner_contact,status,description,image_path,created_at)
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (
        user_id, title, deal_type, property_type, location, area_size, price,
        owner_name, owner_contact, status, description, image_path,
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
    """, conn, params=(user_id,))

    conn.close()

    if "image_path" not in df.columns:
        df["image_path"] = ""

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
        title, deal_type, property_type, location, area_size,
        price, owner_name, owner_contact, status, description, prop_id
    ))

    conn.commit()
    conn.close()

def delete_property(prop_id):
    conn = get_conn()
    c = conn.cursor()

    c.execute("DELETE FROM properties WHERE id=?", (prop_id,))

    conn.commit()
    conn.close()


# ================= SESSION =================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None


# ================= HERO =================

st.markdown("""
<div class="hero-card">
<h1>🏠 Luxury Property CRM</h1>
<p>Premium real estate management dashboard for dealers and agencies.</p>
</div>
""", unsafe_allow_html=True)


# ================= LOGIN / SIGNUP =================

if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.subheader("Welcome Back")

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = login_user(email, password)

            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user[0]
                st.success("Login successful")
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
        password = st.text_input("Password", type="password", key="signup_password")

        if st.button("Create Account"):
            if name and email and phone and password:
                created = signup_user(name, email, phone, password, agency)

                if created:
                    st.success("Account created")
                else:
                    st.error("Email already exists")
            else:
                st.warning("Fill all required fields")

        st.markdown('</div>', unsafe_allow_html=True)


# ================= MAIN APP =================

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

    df = get_properties(st.session_state.user_id)

    if menu == "Dashboard":
        st.subheader("Dashboard")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total", len(df))
        col2.metric("Available", len(df[df["status"] == "Available"]) if not df.empty else 0)
        col3.metric("Sold", len(df[df["status"] == "Sold"]) if not df.empty else 0)
        col4.metric("Rented", len(df[df["status"] == "Rented"]) if not df.empty else 0)

        if not df.empty:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Property Analytics")
            st.bar_chart(df["property_type"].value_counts())
            st.markdown('</div>', unsafe_allow_html=True)

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
            phone = st.text_input("Phone", user[3])
            agency = st.text_input("Agency", user[4])
            city = st.text_input("City", user[5])
            address = st.text_area("Address", user[6])

            submit = st.form_submit_button("Save Profile")

            if submit:
                update_profile(st.session_state.user_id, name, phone, agency, city, address)
                st.success("Profile updated")
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "Add Property":
        st.subheader("Add Property")

        st.markdown('<div class="card">', unsafe_allow_html=True)

        with st.form("property_form"):
            col1, col2 = st.columns(2)

            with col1:
                title = st.text_input("Property Title")
                deal_type = st.selectbox("Deal Type", ["Sale", "Rent"])
                property_type = st.selectbox("Property Type", ["House", "Flat", "Plot", "Shop", "Office", "Commercial"])
                location = st.text_input("Location")
                area_size = st.text_input("Area Size")

            with col2:
                price = st.number_input("Price", min_value=0.0)
                owner_name = st.text_input("Owner Name")
                owner_contact = st.text_input("Owner Contact")
                status = st.selectbox("Status", ["Available", "Sold", "Rented"])
                image = st.file_uploader("Upload Property Image", type=["jpg", "jpeg", "png"])
                description = st.text_area("Description")

            submit = st.form_submit_button("Save Property")

            if submit:
                if title and location:
                    image_path = save_image(image)

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
                        description,
                        image_path
                    )

                    st.success("Property added successfully")
                else:
                    st.warning("Property title aur location zaroor fill karo.")

        st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "View / Search Properties":
        st.subheader("View / Search Properties")

        if df.empty:
            st.info("No properties found")
        else:
            col1, col2, col3 = st.columns(3)

            with col1:
                search = st.text_input("Search Location")

            with col2:
                deal_filter = st.selectbox("Deal Type", ["All", "Sale", "Rent"])

            with col3:
                status_filter = st.selectbox("Status", ["All", "Available", "Sold", "Rented"])

            filtered_df = df.copy()

            if search:
                filtered_df = filtered_df[
                    filtered_df["location"].str.contains(search, case=False, na=False)
                ]

            if deal_filter != "All":
                filtered_df = filtered_df[filtered_df["deal_type"] == deal_filter]

            if status_filter != "All":
                filtered_df = filtered_df[filtered_df["status"] == status_filter]

            st.dataframe(filtered_df, use_container_width=True)

            st.subheader("Property Cards")

            for _, row in filtered_df.iterrows():
                st.markdown('<div class="card">', unsafe_allow_html=True)

                col1, col2 = st.columns([1, 2])

                with col1:
                    image_path = row.get("image_path", "")

                    if image_path and os.path.exists(str(image_path)):
                        st.image(str(image_path), use_container_width=True)
                    else:
                        st.info("No image")

                with col2:
                    st.markdown(f"### {row.get('title', '')}")
                    st.write(f"**Type:** {row.get('property_type', '')}")
                    st.write(f"**Deal:** {row.get('deal_type', '')}")
                    st.write(f"**Location:** {row.get('location', '')}")
                    st.write(f"**Area:** {row.get('area_size', '')}")
                    st.write(f"**Price:** {row.get('price', '')}")
                    st.write(f"**Status:** {row.get('status', '')}")
                    st.write(f"**Owner:** {row.get('owner_name', '')}")
                    st.write(f"**Contact:** {row.get('owner_contact', '')}")
                    st.write(row.get("description", ""))

                    phone = str(row.get("owner_contact", "")).replace("+", "").replace(" ", "")

                    if phone:
                        st.markdown(f"[📲 WhatsApp](https://wa.me/{phone})")

                st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "Edit Property":
        st.subheader("Edit Property")

        if df.empty:
            st.info("No property available")
        else:
            selected_id = st.selectbox("Select Property ID", df["id"].tolist())
            selected = df[df["id"] == selected_id].iloc[0]

            st.markdown('<div class="card">', unsafe_allow_html=True)

            with st.form("edit_form"):
                title = st.text_input("Property Title", selected.get("title", ""))
                deal_type = st.selectbox("Deal Type", ["Sale", "Rent"])
                property_type = st.selectbox("Property Type", ["House", "Flat", "Plot", "Shop", "Office", "Commercial"])
                location = st.text_input("Location", selected.get("location", ""))
                area_size = st.text_input("Area Size", selected.get("area_size", ""))
                price = st.number_input("Price", min_value=0.0, value=float(selected.get("price", 0) or 0))
                owner_name = st.text_input("Owner Name", selected.get("owner_name", ""))
                owner_contact = st.text_input("Owner Contact", selected.get("owner_contact", ""))
                status = st.selectbox("Status", ["Available", "Sold", "Rented"])
                description = st.text_area("Description", selected.get("description", ""))

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

                    st.success("Property updated")
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

    elif menu == "Delete Property":
        st.subheader("Delete Property")

        if df.empty:
            st.info("No property available")
        else:
            selected_id = st.selectbox("Select Property ID", df["id"].tolist())

            if st.button("Delete Property"):
                delete_property(selected_id)
                st.success("Property deleted")
                st.rerun()

    elif menu == "Export Data":
        st.subheader("Export Properties")

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
