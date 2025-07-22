import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3, os, io, pathlib
from datetime import datetime, date
from PIL import Image
from streamlit_autorefresh import st_autorefresh

# ── Paths ──────────────────────────────────────────────────
BASE_DIR = pathlib.Path(__file__).parent
DB_PATH  = BASE_DIR / "glass_defects.db"
IMG_DIR  = BASE_DIR / "images"
os.makedirs(IMG_DIR, exist_ok=True)

# ── DB bootstrap ───────────────────────────────────────────
if not os.path.exists(DB_PATH):
    from init_db import init_db
    init_db()

# ── DB connection ──────────────────────────────────────────
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()
def load_data():
    df = pd.read_sql_query("SELECT * FROM defects", conn)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df

#── CLEANUP any leftover test records (optional) ────────────
cursor.execute("DELETE FROM defects WHERE Tag LIKE '%test%'")
conn.commit()

# ── Load df into session_state (or load if not present) ────
if "df" not in st.session_state:
    st.session_state["df"] = pd.read_sql_query("SELECT * FROM defects", conn)
    st.session_state["df"]["Date"] = pd.to_datetime(st.session_state["df"]["Date"], errors="coerce")

df = st.session_state["df"]

# ── Streamlit config ───────────────────────────────────────
st.set_page_config(page_title="Glass Guard", layout="wide")
st_autorefresh(interval=300_000, key="auto_refresh")   # 5-min auto-refresh

# ── Logo ───────────────────────────────────────────────────
st.markdown("<div style='text-align:center'>", unsafe_allow_html=True)
st.image("KV-Logo-1.png", width=150)
st.markdown("</div>", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📝 Data Entry", "📄 Data Table"])

# ╭────────────────────────── TAB 1 – Dashboard ────────────╮
with tab1:
    st.title("📊 GlassGuard – Glass Defect Summary Dashboard")
    st.caption("Track. Analyze. Improve.")

    if df.empty:
        st.warning("⚠️ No data yet – add a record in “📝 Data Entry”.")
    else:
        df["Year"]  = df["Date"].dt.year
        df["Week#"] = df["Date"].dt.isocalendar().week

        sel_year = st.radio("Choose Year", sorted(df["Year"].unique()), horizontal=True)
        dfy      = df[df["Year"] == sel_year]

        st.markdown("### 🧾 FACTS – Core Defect Types Overview")
        facts_only = ["Scratched", "Production Issue", "Stain Mark", "Broken", "Missing"]
        facts_df   = dfy[dfy["Scratch_Type"].isin(facts_only)]
        facts_summary = (
            facts_df.groupby("Scratch_Type")["Quantity"]
            .sum()
            .reset_index()
            .sort_values("Quantity", ascending=False)
        )
        st.plotly_chart(
            px.bar(facts_summary, x="Scratch_Type", y="Quantity",
                   color="Scratch_Type", title="FACTS: Defect Volume"),
            use_container_width=True
        )

        st.markdown("### 🔍 Breakdown by Glass Type for Selected Scratch Type")
        available = dfy["Scratch_Type"].unique().tolist()
        sel_type  = st.radio("Select Scratch Type", available, horizontal=True)
        sub_df = dfy[dfy["Scratch_Type"] == sel_type]
        if sub_df.empty:
            st.info(f"No '{sel_type}' records for {sel_year}.")
        else:
            glass_summary = (
                sub_df.groupby("Glass_Type")["Quantity"]
                .sum()
                .reset_index()
                .sort_values("Quantity", ascending=False)
            )
            st.dataframe(glass_summary, use_container_width=True, hide_index=True)
            st.plotly_chart(
                px.bar(glass_summary, x="Glass_Type", y="Quantity",
                       color="Glass_Type", title=f"{sel_type} – by Glass Type"),
                use_container_width=True
            )

        st.markdown("### 📅 Weekly Rejections")
        weekly = dfy.groupby("Week#")["Quantity"].sum().reset_index()
        st.plotly_chart(px.line(weekly, x="Week#", y="Quantity", markers=True),
                        use_container_width=True)

        st.markdown("### 🪟 Glass Type Distribution")
        dist = dfy.groupby("Glass_Type")["Quantity"].sum().reset_index()
        st.plotly_chart(px.bar(dist, x="Glass_Type", y="Quantity", color="Glass_Type"),
                        use_container_width=True)

        st.markdown("### 🧺 Rack Type Breakdown")
        rack = dfy.groupby("Rack_Type")["Quantity"].sum().reset_index()
        st.plotly_chart(px.pie(rack, names="Rack_Type", values="Quantity", hole=0.4),
                        use_container_width=True)

        st.markdown("### 🏭 Vendor Distribution")
        vendor = dfy.groupby("Vendor")["Quantity"].sum().reset_index()
        st.plotly_chart(px.pie(vendor, names="Vendor", values="Quantity", hole=0.4),
                        use_container_width=True)

# ╭────────────────────────── TAB 2 – Data Entry ───────────╮
with tab2:
    st.title("📝 Enter New Scratch Record")

    form_keys = {
        "size": "size", "po": "po", "tag": "tag", "qty": "qty",
        "dval": "dval", "loc": "loc", "stype": "stype",
        "gtype": "gtype", "rtype": "rtype", "img": "img",
        "vendor": "vendor", "note": "note"
    }

    with st.form("scratch_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            size = st.text_input("Glass Size", key=form_keys["size"])
            po   = st.text_input("PO# (optional)", key=form_keys["po"])
            tag  = st.text_input("Tag#", key=form_keys["tag"])
            qty  = st.number_input("Quantity", min_value=1, value=1, key=form_keys["qty"])
            date_val = st.date_input("Date", value=date.today(), key=form_keys["dval"])
            st.write("Selected date from form:", date_val)

        with c2:
            loc  = st.selectbox("Location of Scratch", 
                    ["Top Left","Top Center","Top Right","Center Left","Center",
                     "Center Right","Bottom Left","Bottom Center","Bottom Right",
                     "Edge (Vertical)","Edge (Horizontal)","Full Panel","Unknown"],
                    key=form_keys["loc"])
            stype = st.selectbox("Type of Scratch",
                    ["Scratch","Production Issue","Stain Mark","Broken","Missing"],
                    key=form_keys["stype"])
            gtype = st.selectbox("Glass Type (Coating)",
                    ["CLEAR","LOWE 272","LOWE 180","LOWE 366","i89/IS20/SUNGUARD",
                     "MATT","6331","GRAY","HAMMERED","LOWE SHAPE","NIAGARA/RAIN",
                     "PINHEAD","1/2 REED","ACID ETCH"],
                    key=form_keys["gtype"])
            rtype  = st.selectbox("Rack Type", ["A-frame","Bungee Cart","Other"], key=form_keys["rtype"])
            vendor = st.selectbox("Vendor", ["Cardinal CG","Woodbridge","Universal","Trimlite"], key=form_keys["vendor"])
            note   = st.text_area("Notes / Extra details (optional)", key=form_keys["note"])
        up_img = st.file_uploader("Upload Image (Max 2MB)", type=["jpg","jpeg","png"], key=form_keys["img"])
        if up_img:
            st.image(up_img, caption="🖼️ Preview", use_container_width=False, width=200)

        submit_btn = st.form_submit_button("🚀 SAVE RECORD")

    if submit_btn:
        if not tag:
            st.error("Tag# is required.")
        elif not date_val:
            st.error("Date is required.")
        else:
            po_clean = po.strip() or None
            actual_date = date_val if date_val else date.today()
            chosen_date = actual_date.strftime("%Y-%m-%d")
            st.write("Chosen date for insert:", chosen_date)  # debug line

            img_bytes = None
            if up_img:
                up_img.seek(0, os.SEEK_END)
                if up_img.tell() > 2 * 1024 * 1024:
                    st.error("Image exceeds 2 MB.")
                    st.stop()
                up_img.seek(0)
                img_bytes = up_img.read()

            cursor.execute("""
                INSERT INTO defects
                (PO, Tag, Size, Quantity, Scratch_Location, Scratch_Type,
                 Glass_Type, Rack_Type, Vendor, Date, Note, ImageData)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (po_clean, tag.strip(), size.strip(), qty, loc, stype,
                  gtype, rtype, vendor, chosen_date, note.strip(), img_bytes))
            conn.commit()

            # Reload df and save to session state after insert
            st.session_state["df"] = load_data()

            st.success("✅ Submitted!")
            st.toast("Record saved!", icon="💾")
            st.rerun()

# ╭────────────────────────── TAB 3 – Data Table ────────────╮
with tab3:
    df = st.session_state["df"]  # Use latest df from session state

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Records", len(df))
    m2.metric("Total Scratches", int(df["Quantity"].sum()) if not df.empty else 0)

    glass_sums = df.groupby("Glass_Type")["Quantity"].sum()
    if not glass_sums.empty:
        top_glass = glass_sums.idxmax()
        m3.metric("Top Glass Type", f"{top_glass} ({int(glass_sums.max())})")
    else:
        m3.metric("Top Glass Type", "N/A")

    st.title("📄 All Scratch Records")
    with st.expander("🔒 Admin: Delete rows by Tag#"):
        tags_in = st.text_input("Tag#s to delete (comma-separated)")
    if st.button("🚨 Delete Selected"):
        tags = [t.strip() for t in tags_in.split(",") if t.strip()]
        if tags:
            ph = ",".join("?"*len(tags))
            cursor.execute(f"DELETE FROM defects WHERE Tag IN ({ph})", tags)
            conn.commit()

            # Reload df after delete
            st.session_state["df"] = load_data()
            st.success(f"Deleted: {', '.join(tags)}")
            st.rerun()
        else:
            st.warning("No tags entered.")

    if df.empty:
        st.info("No data available.")
    else:
        all_df = (
            df.sort_values("Date", ascending=False)
              .loc[:, ["Tag", "Date", "Quantity", "Scratch_Type", "Glass_Type"]]
              .rename(columns={
                  "Tag": "Tag#",
                  "Quantity": "QTY",
                  "Scratch_Type": "Type",
                  "Glass_Type": "Glass"
              })
        )
        all_df["Date"] = all_df["Date"].dt.strftime("%Y-%m-%d").fillna("N/A")
        all_df = all_df.reset_index(drop=True)
        all_df.index = all_df.index + 1
        all_df.index.name = "Sr. No"
        
        st.dataframe(all_df, use_container_width=True, height=350)

        sel = st.selectbox("Select Tag# to download its image", all_df["Tag#"])
        row = df[df["Tag"] == sel].iloc[0]
        img_bytes = row.get("ImageData")

        if isinstance(img_bytes, (bytes, bytearray)):
            st.image(img_bytes, width=100, caption="📷 Preview")
            date_val = pd.to_datetime(row["Date"], errors="coerce")
            date_str = date_val.strftime("%Y-%m-%d") if not pd.isna(date_val) else "unknown"
            st.download_button(
                "⬇️ Download Image",
                data=img_bytes,
                file_name=f"{sel}_{date_str}.jpg",
                mime="image/jpeg",
            )
        else:
            st.info("No image for this record.")

        # Excel export with proper date formatting
        export_df = df.copy()
        export_df["Date"] = export_df["Date"].dt.strftime("%Y-%m-%d")

        buf = io.BytesIO()
        export_df.to_excel(buf, index=False)
        buf.seek(0)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            "⬇️ Download full backup (Excel)",
            data=buf,
            file_name=f"glass_defects_backup_{ts}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
