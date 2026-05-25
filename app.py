import streamlit as st
import sqlite3
import hashlib
import pandas as pd
from datetime import datetime

DB_NAME = "property_dealer.db"

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
        user_id, title, deal_type, property_type, location, area_size, price,
        owner_name, owner_contact, status, description,
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
        title, deal_type, property_type, location, area_size, price,
        owner_name, owner_contact, status, description, prop_id
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

# ---------------- UI ----------------

st.set_page_config(
    page_title="Property Dealer App",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 Property Dealer Management App")

# ---------------- LOGIN / SIGNUP ----------------

if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        st.subheader("Login")

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

    with tab2:
        st.subheader("Create Account")

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

# ---------------- MAIN APP ----------------

else:
    user = get_user(st.session_state.user_id)

    st.sidebar.success(f"Logged in: {user[1]}")
    menu = st.sidebar.radio(
        "Menu",
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

    # -------- DASHBOARD --------

    if menu == "Dashboard":
        st.subheader("Dashboard")

        df = get_properties(st.session_state.user_id)

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Properties", len(df))
        col2.metric("Available", len(df[df["status"] == "Available"]) if not df.empty else 0)
        col3.metric("Sold", len(df[df["status"] == "Sold"]) if not df.empty else 0)
        col4.metric("Rented", len(df[df["status"] == "Rented"]) if not df.empty else 0)

        st.info("Yahan dealer apni properties, profile aur data manage kar sakta hai.")

    # -------- PROFILE --------

    elif menu == "Profile":
        st.subheader("Dealer Profile")

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

    # -------- ADD PROPERTY --------

    elif menu == "Add Property":
        st.subheader("Add New Property")

        with st.form("add_property_form"):
            title = st.text_input("Property Title")
            deal_type = st.selectbox("Deal Type", ["Sale", "Rent"])
            property_type = st.selectbox(
                "Property Type",
                ["House", "Flat", "Plot", "Shop", "Office", "Commercial"]
            )
            location = st.text_input("Location")
            area_size = st.text_input("Area Size e.g. 5 Marla, 10 Marla")
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

    # -------- VIEW / SEARCH --------

    elif menu == "View / Search Properties":
        st.subheader("View / Search Properties")

        df = get_properties(st.session_state.user_id)

        if df.empty:
            st.info("Abhi koi property saved nahi hai.")
        else:
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

    # -------- EDIT PROPERTY --------

    elif menu == "Edit Property":
        st.subheader("Edit Property")

        df = get_properties(st.session_state.user_id)

        if df.empty:
            st.info("Edit karne ke liye koi property nahi hai.")
        else:
            property_ids = df["id"].tolist()
            selected_id = st.selectbox("Select Property ID", property_ids)

            selected = df[df["id"] == selected_id].iloc[0]

            with st.form("edit_property_form"):
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

    # -------- DELETE PROPERTY --------

    elif menu == "Delete Property":
        st.subheader("Delete Property")

        df = get_properties(st.session_state.user_id)

        if df.empty:
            st.info("Delete karne ke liye koi property nahi hai.")
        else:
            selected_id = st.selectbox("Select Property ID", df["id"].tolist())

            selected = df[df["id"] == selected_id].iloc[0]

            st.warning(f"Are you sure you want to delete: {selected['title']}?")

            if st.button("Delete Property"):
                delete_property(selected_id)
                st.success("Property deleted successfully.")
                st.rerun()

    # -------- EXPORT DATA --------

    elif menu == "Export Data":
        st.subheader("Export Properties Data")

        df = get_properties(st.session_state.user_id)

        if df.empty:
            st.info("Export ke liye koi data nahi hai.")
        else:
            st.dataframe(df, use_container_width=True)

            csv = df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="properties_data.csv",
                mime="text/csv"
            )
