# app.py
import streamlit as st
from datetime import datetime
from utils.db import get_db
from utils import auth
import pandas as pd

# ---------------- Page Configuration ----------------
st.set_page_config(page_title="Digital Marketing Agency Dashboard", layout="wide")

# ---------------- CSS Styling ----------------
st.markdown("""
    <style>
    .stApp { background: linear-gradient(180deg,#f8fafc,#ffffff); }
    .title { font-size:34px; font-weight:700; }
    .card { padding:12px; border-radius:12px; box-shadow:0 4px 14px rgba(0,0,0,0.04); background:white; }
    </style>
""", unsafe_allow_html=True)

# ---------------- Authentication ----------------
if "user" not in st.session_state:
    st.session_state.user = None

with st.sidebar:
    st.image("https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?w=800&q=80", use_column_width=True)
    st.title(st.secrets.get("site_name", "Your Agency"))

    if not st.session_state.user:
        st.subheader("Sign in")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Login"):
                user = auth.authenticate(email, password)
                if user:
                    st.session_state.user = user
                    st.success(f"Welcome back, {user.get('full_name', user['email'])}!")
                    st.experimental_rerun()
                else:
                    st.error("Invalid credentials")
        with col2:
            if st.button("Sign up"):
                try:
                    auth.create_user(email, password)
                    st.success("Account created — now log in.")
                except Exception as e:
                    st.error(str(e))
    else:
        st.write(f"Logged in as: {st.session_state.user.get('email')}")
        if st.button("Logout"):
            st.session_state.user = None
            st.experimental_rerun()

# ---------------- Main Area ----------------
if not st.session_state.user:
    st.markdown("# Welcome to your Digital Marketing Agency App")
    st.write("Please sign in or create an account from the left sidebar to continue.")
    st.stop()

user = st.session_state.user
db = get_db()

# ---------------- Dashboard ----------------
st.header(f"Dashboard — {st.secrets.get('site_name', 'Agency')}")

col1, col2, col3 = st.columns(3)
with col1:
    leads_count = db["leads"].count_documents({})
    st.metric("Leads", leads_count)
with col2:
    clients_count = db["clients"].count_documents({})
    st.metric("Clients", clients_count)
with col3:
    campaigns_count = db["campaigns"].count_documents({})
    st.metric("Campaigns", campaigns_count)

st.markdown("---")

# ---------------- Add Lead Form ----------------
st.subheader("Add a Lead")
with st.form("add_lead"):
    name = st.text_input("Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    source = st.selectbox("Source", ["Website", "Referral", "Ads", "Cold Call", "Other"])
    notes = st.text_area("Notes")
    submit = st.form_submit_button("Add Lead")

    if submit:
        lead = {
            "name": name,
            "email": email,
            "phone": phone,
            "source": source,
            "notes": notes,
            "created_at": datetime.utcnow(),
            "owner": user.get("email"),
        }
        db["leads"].insert_one(lead)
        st.success("Lead added successfully!")

# ---------------- Recent Leads ----------------
st.subheader("Recent Leads")
leads = list(db["leads"].find().sort("created_at", -1).limit(10))
if leads:
    df = pd.DataFrame(leads)
    if "_id" in df.columns:
        df["_id"] = df["_id"].astype(str)
    st.dataframe(df)
else:
    st.info("No leads yet — add one!")

# ---------------- Campaign Chart ----------------
st.subheader("Campaign Performance (sample)")
campaigns = list(db["campaigns"].find())
if campaigns:
    dfc = pd.DataFrame(campaigns)
    if "impressions" in dfc.columns and "clicks" in dfc.columns:
        st.line_chart(dfc.set_index("name")["impressions"].fillna(0))
else:
    st.info("No campaign data yet. Create campaigns in the Admin section.")

# ---------------- Admin Section ----------------
if "admin" in user.get("roles", []):
    st.markdown("---")
    st.subheader("Admin: Manage Services & Campaigns")

    with st.expander("Add Service"):
        with st.form("add_service"):
            sname = st.text_input("Service Name")
            price = st.number_input("Base Price", min_value=0)
            desc = st.text_area("Description")
            ok = st.form_submit_button("Add Service")
            if ok:
                db["services"].insert_one({"name": sname, "price": price, "description": desc})
                st.success("Service added!")

    with st.expander("Add Campaign"):
        with st.form("add_campaign"):
            cname = st.text_input("Campaign Name")
            cclient = st.text_input("Client")
            budget = st.number_input("Budget", min_value=0)
            impressions = st.number_input("Impressions", min_value=0)
            clicks = st.number_input("Clicks", min_value=0)
            submit2 = st.form_submit_button("Create Campaign")
            if submit2:
                db["campaigns"].insert_one({
                    "name": cname,
                    "client": cclient,
                    "budget": budget,
                    "impressions": impressions,
                    "clicks": clicks,
                    "created_at": datetime.utcnow(),
                })
                st.success("Campaign created successfully!")

st.markdown("---")
st.write("Built with ❤️ by Stilfy Digital Marketing Agency")
