# app.py
st.subheader("Add a lead")
with st.form("add_lead"):
name = st.text_input("Name")
email = st.text_input("Email")
phone = st.text_input("Phone")
source = st.selectbox("Source", ["Website", "Referral", "Ads", "Cold Call", "Other"])
notes = st.text_area("Notes")
submit = st.form_submit_button("Add lead")
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
st.success("Lead added")


st.subheader("Recent leads")
leads = list(db["leads"].find().sort("created_at", -1).limit(10))
if leads:
df = pd.DataFrame(leads)
if "_id" in df.columns:
df["id"] = df["_id"].astype(str)
df = df.drop(columns=["_id"])
st.dataframe(df)
else:
st.info("No leads yet — add one!")


# Simple campaign performance chart
st.subheader("Campaign performance (sample)")
campaigns = list(db["campaigns"].find())
if campaigns:
dfc = pd.DataFrame(campaigns)
if "impressions" in dfc.columns and "clicks" in dfc.columns:
st.line_chart(dfc.set_index("name")["impressions"].fillna(0))
else:
st.info("No campaign data. Create campaigns in the Admin area.")


# Admin area for users with admin role
if "admin" in user.get("roles", []):
st.markdown("---")
st.subheader("Admin: Manage Services & Campaigns")
with st.expander("Add service"):
with st.form("add_service"):
sname = st.text_input("Service name")
price = st.number_input("Base price", min_value=0)
desc = st.text_area("Description")
ok = st.form_submit_button("Add")
if ok:
db["services"].insert_one({"name": sname, "price": price, "description": desc})
st.success("Service added")


with st.expander("Add campaign"):
with st.form("add_campaign"):
cname = st.text_input("Campaign name")
cclient = st.text_input("Client")
budget = st.number_input("Budget", min_value=0)
impressions = st.number_input("Impressions", min_value=0)
clicks = st.number_input("Clicks", min_value=0)
submit2 = st.form_submit_button("Create campaign")
if submit2:
db["campaigns"].insert_one({
"name": cname,
"client": cclient,
"budget": budget,
"impressions": impressions,
"clicks": clicks,
"created_at": datetime.utcnow(),
})
st.success("Campaign created")


st.markdown("---")
st.write("Built with love. Export or extend this app to add invoicing, reporting, and automations.")