import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3, os
from datetime import datetime, date
from PIL import Image
from streamlit_autorefresh import st_autorefresh

if not os.path.exists("glass_defects.db"):
    import init_db  # Runs the init script if DB doesn't exist

st.set_page_config(page_title="Glass Guard", layout="wide")
st_autorefresh(interval=300_000, key="auto_refresh")          # 5-min refresh

# ── Logo ────────────────────────────────────────────────────
st.markdown("<div style='text-align:center'>", unsafe_allow_html=True)
st.image("KV-Logo-1.png", width=150)
st.markdown("</div>", unsafe_allow_html=True)
st.sidebar.info("Build: 2025-07-11 09:12")

# ── Paths ──────────────────────────────────────────────────
import pathlib
BASE_DIR = pathlib.Path(__file__).parent

DB_PATH  = BASE_DIR / "glass_defects.db"
IMG_DIR  = BASE_DIR / "images"
os.makedirs(IMG_DIR, exist_ok=True)


# ── DB & DataFrame ─────────────────────────────────────────
conn   = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()
df     = pd.read_sql_query("SELECT * FROM defects", conn)

# ── Tabs ───────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📝 Data Entry", "📄 Data Table"])

# ╭────────────────────────── TAB 1 – Dashboard ────────────╮
with tab1:
    st.title("📊 GlassGuard – Glass Scratch Summary Dashboard")
    st.caption("Track. Analyze. Improve.")
    if df.empty:
        st.warning("⚠️ No data yet – add a record in “📝 Data Entry”.")
    else:
        df["Date"]  = pd.to_datetime(df["Date"], errors="coerce")
        df["Year"]  = df["Date"].dt.year
        df["Week#"] = df["Date"].dt.isocalendar().week

        sel_year = st.radio("Choose Year", sorted(df["Year"].unique()), horizontal=True)
        dfy      = df[df["Year"] == sel_year]

        st.markdown("### 📅 Weekly Scratch Volume")
        weekly = dfy.groupby("Week#")["Quantity"].sum().reset_index()
        st.plotly_chart(px.line(weekly, x="Week#", y="Quantity", markers=True), use_container_width=True)

        st.markdown("### 🪟 Scratch Type Distribution")
        st.plotly_chart(
            px.bar(dfy.groupby("Scratch_Type")["Quantity"].sum().reset_index(),
                   x="Scratch_Type", y="Quantity", color="Scratch_Type"),
            use_container_width=True)

        st.markdown("### 🧊 Glass Type with Scratches")
        st.plotly_chart(
            px.bar(dfy.groupby("Glass_Type")["Quantity"].sum().reset_index(),
                   x="Glass_Type", y="Quantity", color="Glass_Type"),
            use_container_width=True)

        st.markdown("### 🧺 Rack Type Breakdown")
        st.plotly_chart(
            px.pie(dfy.groupby("Rack_Type")["Quantity"].sum().reset_index(),
                   names="Rack_Type", values="Quantity", hole=0.4),
            use_container_width=True)
        
        st.markdown("### 🏭 Vendor Distribution")
        st.plotly_chart(
            px.pie(dfy.groupby("Vendor")["Quantity"].sum().reset_index(),
                   names="Vendor", values="Quantity", hole=0.4),
            use_container_width=True)

# ╭────────────────────────── TAB 2 – Data Entry ───────────╮
with tab2:
    st.title("📝 Enter New Scratch Record")

    form_keys = {
        "size": "size", "po": "po", "tag": "tag", "qty": "qty",
        "dval": "dval", "loc": "loc", "stype": "stype",
        "gtype": "gtype", "rtype": "rtype", "img": "img", "vendor": "vendor"

    }

    # ---- the input form --------------------------------------------------
    with st.form("scratch_form", clear_on_submit=False):
        c1, c2 = st.columns(2)

        with c1:
            size = st.text_input("Glass Size", key=form_keys["size"])
            po   = st.text_input("PO#",        key=form_keys["po"])
            tag  = st.text_input("Tag#",       key=form_keys["tag"])
            qty  = st.number_input("Quantity", min_value=1, value=1, key=form_keys["qty"])
            date_val = st.date_input("Date", value=date.today(), key=form_keys["dval"])

        with c2:
            loc   = st.selectbox("Location of Scratch",
                                 ["Top Left","Top Center","Top Right","Center Left","Center",
                                  "Center Right","Bottom Left","Bottom Center","Bottom Right",
                                  "Edge (Vertical)","Edge (Horizontal)","Full Panel","Unknown"],
                                 key=form_keys["loc"])

            stype = st.selectbox("Type of Scratch",
                                 ["Surface Scratch","Deep Scratch","Drag Mark","Swirl Mark",
                                  "Spot Scratch","Edge Scratch","Center Scratch","Suction Cup Mark",
                                  "Handling Damage","Rack Damage","Machine Scratch","Unknown"],
                                 key=form_keys["stype"])

            gtype = st.selectbox("Glass Type (Coating)",
                                 ["CLEAR","LOWE 272","LOWE 180","LOWE 366","i89/IS20/SUNGUARD",
                                  "MATT","6331","GRAY","HAMMERED","LOWE SHAPE","NIAGARA/RAIN",
                                  "PINHEAD","1/2 REED","ACID ETCH"],
                                 key=form_keys["gtype"])

            rtype = st.selectbox("Rack Type", ["A-frame","Bungee Cart","Other"],
                                 key=form_keys["rtype"])
            vendor = st.selectbox("Vendor", ["Cardinal CG", "Woodbridge", "Universal", "Trimlite"], key=form_keys["vendor"])


        up_img = st.file_uploader("📸 Upload Scratch Image (optional)",
                                  type=["jpg","jpeg","png"], key=form_keys["img"])

        submit_btn = st.form_submit_button("✅ Submit")

    # ---- handle SUBMIT (outside the form block) --------------------------
    if submit_btn:
        if not (po and tag):
            st.error("PO# and Tag# are required.")
        else:
            chosen_date = date_val.strftime("%Y-%m-%d")

            cursor.execute("""
            INSERT INTO defects
            (PO, Tag, Size, Quantity, Scratch_Location, Scratch_Type,
            Glass_Type, Rack_Type, Vendor, Date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (po.strip(), tag.strip(), size.strip(), qty, loc, stype,
            gtype, rtype, vendor, chosen_date))

            conn.commit()

        if up_img:
            safe_tag = tag.strip().replace(" ", "_")
            date_str = chosen_date
            ext = up_img.name.split('.')[-1].lower()
            fname = f"{safe_tag}_{date_str}.{ext}"
            fpath = os.path.join(IMG_DIR, fname)

            counter = 1
            while os.path.exists(fpath):
                fname = f"{safe_tag}_{date_str}_{counter}.{ext}"
            fpath = os.path.join(IMG_DIR, fname)
            counter += 1

            Image.open(up_img).save(fpath)


            st.success("✅ Submitted!")
            st.rerun()

    
# ╭────────────────────────── TAB 3 – Data Table ────────────╮
with tab3:
    st.title("📄 All Scratch Records")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Records", len(df))
    col2.metric("Total Scratches", int(df["Quantity"].sum()) if not df.empty else 0)
    if not df.empty:
        top = df["Scratch_Type"].mode()[0]
        col3.metric("Top Type", f"{top} ({df[df['Scratch_Type']==top]['Quantity'].sum()})")

    st.dataframe(df.sort_values("Date", ascending=False),
                 use_container_width=True, height=600)


# ╭────────────────────── Today’s Scratch Summary ─────────────╮
from datetime import date

st.markdown("### 📋 Today’s Scratch Summary")

if st.button("Generate Table", key="gen_today"):
    if df.empty:
        st.warning("No data in DB.")
    else:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df_today = df[df["Date"].dt.date == date.today()]

        if df_today.empty:
            st.warning("No records logged today.")
        else:
            table = (df_today.loc[:, ["PO","Tag","Size","Quantity","Glass_Type","Date"]]
                               .rename(columns={"PO":"PO#","Tag":"Tag#",
                                                "Quantity":"QTY","Glass_Type":"Glass Type"}))
            st.dataframe(table, use_container_width=True, hide_index=True)

            clip = table.to_csv(index=False, sep="\t").replace("`","'").replace("\n","\\n")
            st.components.v1.html(
                f"""
                <button onclick="navigator.clipboard.writeText(`{clip}`)
                          .then(()=>alert('✅ Copied to clipboard!'))">
                    📋 Copy Table to Clipboard
                </button>
                """,
                height=50
            )
