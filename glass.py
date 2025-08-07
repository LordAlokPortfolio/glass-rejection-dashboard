import os, io, pathlib
from datetime import datetime, date

import mysql.connector
import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image
from streamlit_autorefresh import st_autorefresh

# ---------- Streamlit basic setup ----------
st.set_page_config(page_title="Glass Guard", layout="wide")
st_autorefresh(interval=300_000, key="auto_refresh")   # 5‑min auto refresh

# ---------- Helpers ----------
def log_custom_runs(date_val, runs_val):
    cur, conn = get_cursor()
    cur.execute(
        "INSERT INTO custom_runs (run_date, runs) VALUES (%s, %s)",
        (date_val.strftime("%Y-%m-%d"), runs_val)
    )
    conn.commit()
    cur.close()

def looks_like_image(b: bytes) -> bool:
    # quick sniff for JPG/PNG
    return bool(b) and len(b) > 8 and (b[:2] == b"\xFF\xD8" or b[:8] == b"\x89PNG\r\n\x1a\n")

@st.cache_resource
def get_conn():
    cfg = st.secrets["mysql"]
    conn = mysql.connector.connect(
        **cfg,
        connection_timeout=15,
        pool_name="glasspool",
        pool_size=5,
    )
    return conn

def get_cursor():
    conn = get_conn()
    try:
        # Try "ping" (preferred) — if fails, try reconnect
        conn.ping(reconnect=True, attempts=3, delay=2)
    except Exception:
        try:
            conn.reconnect(attempts=3, delay=2)
        except Exception as e:
            st.error(f"Database connection failed: {e}")
            raise
    return conn.cursor(dictionary=True), conn

@st.cache_data(ttl=300)
def load_data_cached():
    cur, _ = get_cursor()
    cur.execute("SELECT * FROM defects")
    rows = cur.fetchall()
    cur.close()
    df = pd.DataFrame(rows)
    if not df.empty and "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df

# ---------- One-time table create ----------
def init_table():
    cur, conn = get_cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS defects (
          PO VARCHAR(255),
          Tag VARCHAR(255),
          Size VARCHAR(255),
          Quantity INT,
          Scratch_Location VARCHAR(255),
          Scratch_Type VARCHAR(255),
          Glass_Type VARCHAR(255),
          Rack_Type VARCHAR(255),
          Vendor VARCHAR(255),
          Date DATE,
          Note TEXT,
          ImageData LONGBLOB
        ) ENGINE=InnoDB;
    """)
    conn.commit()
    cur.close()

# --- DB Status check ---
try:
    cur, conn = get_cursor()
    cur.execute("SELECT 1")
    _ = cur.fetchall()    # <-- THIS fetches any result, clears buffer!
    cur.close()
    st.success("✅ Database: Connected")
except Exception as e:
    st.error(f"❌ Database: Not connected\n\n{e}")


# ---------- Paths (not critical but kept) ----------
BASE_DIR = pathlib.Path(__file__).parent
IMG_DIR = BASE_DIR / "images"
os.makedirs(IMG_DIR, exist_ok=True)

# ---------- Load initial df ----------
if "df" not in st.session_state:
    init_table()  # Ensure table exists
    st.session_state["df"] = load_data_cached()
df = st.session_state["df"]

# ---------- UI: Logo ----------
st.markdown("<div style='text-align:center'>", unsafe_allow_html=True)
st.image("KV-Logo-1.png", width=150)
st.markdown("</div>", unsafe_allow_html=True)

# ---------- Tabs ----------
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📝 Data Entry", "📄 Data Table"])

# ===== TAB 1: Dashboard =====
with tab1:
    st.title("📊 GlassGuard – Glass Defect Summary Dashboard")
    st.caption("Track. Analyze. Improve.")

    if df.empty:
        st.warning("⚠️ No data yet – add a record in “📝 Data Entry”.")
    else:
        df["Year"] = df["Date"].dt.year
        df["Week#"] = df["Date"].dt.isocalendar().week

        sel_year = st.radio("Choose Year", sorted(df["Year"].unique()), horizontal=True)

        with st.expander("⚙️ Advanced Options", expanded=False):
            show_all_vendors = st.checkbox("Show All Vendors", value=False)

        # Filter by vendor and year
        df_filtered = df.copy()
        if not show_all_vendors:
            df_filtered = df_filtered[df_filtered["Vendor"] == "Cardinal CG"]

        dfy = df_filtered[df_filtered["Year"] == sel_year]

        st.markdown("### 🧾 FACTS – Core Defect Types Overview")
        facts_only = ["Scratched", "Production Issue", "Stain Mark", "Broken", "Missing"]
        facts_df = dfy[dfy["Scratch_Type"].isin(facts_only)]
        facts_summary = (
            facts_df.groupby("Scratch_Type")["Quantity"].sum().reset_index().sort_values("Quantity", ascending=False)
        )
        st.plotly_chart(
            px.bar(facts_summary, x="Scratch_Type", y="Quantity", color="Scratch_Type", title="FACTS: Defect Volume"),
            use_container_width=True
        )

        st.markdown("### 🔍 Breakdown by Glass Type for Selected Scratch Type")
        available = dfy["Scratch_Type"].unique().tolist()
        sel_type = st.radio("Select Scratch Type", available, horizontal=True)
        sub_df = dfy[dfy["Scratch_Type"] == sel_type]
        if sub_df.empty:
            st.info(f"No '{sel_type}' records for {sel_year}.")
        else:
            glass_summary = (
                sub_df.groupby("Glass_Type")["Quantity"].sum().reset_index().sort_values("Quantity", ascending=False)
            )
            st.dataframe(glass_summary, use_container_width=True, hide_index=True)
            st.plotly_chart(
                px.bar(glass_summary, x="Glass_Type", y="Quantity", color="Glass_Type",
                       title=f"{sel_type} – by Glass Type"),
                use_container_width=True
            )

        st.markdown("### 📅 Weekly Rejections")
        weekly = dfy.groupby("Week#")["Quantity"].sum().reset_index()
        st.plotly_chart(px.line(weekly, x="Week#", y="Quantity", markers=True), use_container_width=True)

        # REMOVED vendor distribution chart (as per your boss)
        # REPLACED with Cardinal CG vs Production Issue
        st.markdown("### 🏭 Cardinal CG vs Production Issue")
        cf_df = dfy.copy()
        cf_df["Origin"] = cf_df["Scratch_Type"].apply(
            lambda x: "Production Issue" if x == "Production Issue" else "Cardinal CG"
        )
        summary = cf_df.groupby("Origin")["Quantity"].sum().reset_index()
        st.plotly_chart(px.pie(summary, names="Origin", values="Quantity", hole=0.4), use_container_width=True)

        st.markdown("### 🧺 Rack Type Breakdown")
        rack = dfy.groupby("Rack_Type")["Quantity"].sum().reset_index()
        st.plotly_chart(px.pie(rack, names="Rack_Type", values="Quantity", hole=0.4), use_container_width=True)

# ===== TAB 2: Data Entry =====
with tab2:
    st.title("📝 Enter New Scratch Record")

    form_keys = {
        "size": "size", "po": "po", "tag": "tag", "qty": "qty",
        "dval": "dval", "loc": "loc", "stype": "stype",
        "gtype": "gtype", "rtype": "rtype", "img": "img",
        "vendor": "vendor", "note": "note"
    }

    with st.form("scratch_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            size = st.text_input("Glass Size", key=form_keys["size"])
            po = st.text_input("PO# (optional)", key=form_keys["po"])
            tag = st.text_input("Tag#", key=form_keys["tag"])
            qty = st.number_input("Quantity", min_value=1, value=1, key=form_keys["qty"])
            date_val = st.date_input("Date", value=date.today(), key=form_keys["dval"])
            

        with c2:
            loc = st.selectbox(
                "Location of Scratch",
                ["Top Left","Top Center","Top Right","Center Left","Center","Center Right",
                 "Bottom Left","Bottom Center","Bottom Right","Edge (Vertical)","Edge (Horizontal)",
                 "Full Panel","Unknown"],
                key=form_keys["loc"]
            )
            stype = st.selectbox(
                "Type of Scratch",
                ["Scratched","Production Issue","Stain Mark","Broken","Missing"],
                key=form_keys["stype"]
            )
            gtype = st.selectbox(
                "Glass Type (Coating)",
                ["CLEAR","LOWE 272","LOWE 180","LOWE 366","i89/IS20/SUNGUARD",
                 "MATT","6331","GRAY","HAMMERED","LOWE SHAPE","NIAGARA/RAIN",
                 "PINHEAD","1/2 REED","ACID ETCH"],
                key=form_keys["gtype"]
            )
            rtype = st.selectbox("Rack Type", ["A-frame","Bungee Cart"], key=form_keys["rtype"])
            vendor = st.selectbox("Vendor", ["Cardinal CG","Woodbridge","Universal","Trimlite"], key=form_keys["vendor"])
            note = st.text_area("Notes / Extra details (optional)", key=form_keys["note"])

        up_img = st.file_uploader("Upload Image (Max 4MB)", type=["jpg","jpeg","png"], key=form_keys["img"])
        if up_img:
            st.image(up_img, caption="🖼️ Preview", width=200)

        submitted = st.form_submit_button("🚀 SAVE RECORD")

    if submitted:
        if not tag:
            st.error("Tag# is required.")
        else:
            po_clean = po.strip() or None
            chosen_date = date_val.strftime("%Y-%m-%d")

            img_bytes = None
            if up_img:
                up_img.seek(0, os.SEEK_END)
                if up_img.tell() > 4 * 1024 * 1024:
                    st.error("Image exceeds 4 MB.")
                    st.stop()
                up_img.seek(0)
                img_bytes = up_img.read()

            cur, conn = get_cursor()
            cur.execute("""
                INSERT INTO defects
                (PO, Tag, Size, Quantity, Scratch_Location, Scratch_Type,
                 Glass_Type, Rack_Type, Vendor, Date, Note, ImageData)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (po_clean, tag.strip(), size.strip(), qty, loc, stype,
                  gtype, rtype, vendor, chosen_date, note.strip(), img_bytes))
            conn.commit()
            cur.close()

            load_data_cached.clear()
            st.session_state["df"] = load_data_cached()

            st.success("✅ Submitted!")
            st.toast("Record saved!", icon="💾")
            st.rerun()

# ===== TAB 3: Data Table =====
with tab3:
    df = st.session_state["df"]

    # --- Custom Runs Entry Form (does NOT create defect record) ---
    with st.expander("📦 Log Today's Custom Runs (does NOT create defect record)"):
        cr_date = st.date_input("Date", value=date.today(), key="customrun_date")
        cr_runs = st.number_input("Custom Runs (today)", min_value=0, value=0, key="customrun_val")
        if st.button("Save Custom Runs"):
            log_custom_runs(cr_date, cr_runs)
            st.success(f"Logged {cr_runs} runs for {cr_date}")

    # ---- 📅 Cumulative Custom Run & Damage Stats ----

    def get_cumulative_custom_runs():
        cur, _ = get_cursor()
        # Get sum of all runs up to and including Dec 31, 2025
        cur.execute(
            "SELECT SUM(runs) as total_runs FROM custom_runs WHERE run_date <= %s",
            ('2025-12-31',)
        )
        res = cur.fetchone()
        cur.close()
        return res['total_runs'] if res and res['total_runs'] else 0

    total_custom_runs = get_cumulative_custom_runs()
    try:
        total_custom_runs = int(total_custom_runs)
    except (TypeError, ValueError):
        total_custom_runs = 0

    total_damages = df['Quantity'].sum() if not df.empty else 0
    damage_percent = (total_damages / total_custom_runs) * 100 if total_custom_runs > 0 else 0

    st.markdown("#### 📅 Cumulative Custom Runs & Damage Stats (till Dec 31, 2025)")
    c1, c2, c3 = st.columns(3)
    c1.metric("Custom Runs", total_custom_runs)
    c2.metric("Damaged Pieces", total_damages)
    c3.metric("Damage %", f"{damage_percent:.2f}%")

    st.markdown("#### 📊 Overall Stats")
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Records", len(df))
    m2.metric("Total Damages", int(df["Quantity"].sum()) if not df.empty else 0)

    glass_sums = df.groupby("Glass_Type")["Quantity"].sum() if not df.empty else pd.Series(dtype=int)
    if not glass_sums.empty:
        top_glass = glass_sums.idxmax()
        m3.metric("Top Glass Type", f"{top_glass} ({int(glass_sums.max())})")
    else:
        m3.metric("Top Glass Type", "N/A")

    st.title("📄 All Scratch Records")

    # Delete rows
    with st.expander("🔒 Admin: Delete rows by Tag#"):
        tags_in = st.text_input("Tag#s to delete (comma-separated)")
        delete_btn = st.button("🚨 Delete Selected", key="delete_btn")
        if delete_btn:
            tags = [t.strip() for t in tags_in.split(",") if t.strip()]
            if not tags:
                st.warning("No tags entered.")
            else:
                try:
                    present_tags = df["Tag"].astype(str).tolist()
                    delete_these = [t for t in tags if t in present_tags]
                    if not delete_these:
                        st.warning("None of those Tag#s are present in the data.")
                    else:
                        ph = ",".join(["%s"] * len(delete_these))
                        cursor = get_conn().cursor()
                        cursor.execute(f"DELETE FROM defects WHERE Tag IN ({ph})", delete_these)
                        get_conn().commit()
                        cursor.close()
                        load_data_cached.clear()
                        st.session_state["df"] = load_data_cached()
                        st.success(f"Deleted: {', '.join(delete_these)}")
                        st.rerun()
                except Exception as e:
                    st.error(f"Delete failed: {e}")

    if df.empty:
        st.info("No data available.")
    else:
        all_df = (
            df.sort_values("Date", ascending=False)
              .loc[:, ["Size", "Tag", "Date", "Quantity", "Scratch_Type", "Glass_Type", "Rack_Type"]]
              .rename(columns={
                  "Size": "Size",
                  "Tag": "Tag#",
                  "Quantity": "QTY",
                  "Scratch_Type": "Type",
                  "Glass_Type": "Glass",
                  "Rack_Type": "Rack"
              })
        )
        all_df["Date"] = pd.to_datetime(all_df["Date"], errors="coerce").dt.strftime("%Y-%m-%d").fillna("N/A")
        all_df = all_df.reset_index(drop=True)
        all_df.index = all_df.index + 1
        all_df.index.name = "Sr. No"

        st.dataframe(all_df, use_container_width=True, height=350)

        # --- Only show Tag#s with images in the dropdown ---
        tags_with_images = df[
            df['ImageData'].notnull() & 
            df['ImageData'].apply(lambda x: isinstance(x, (bytes, bytearray)) and len(x) > 0)
        ]['Tag'].unique().tolist()

        if tags_with_images:
            sel = st.selectbox("Select Tag# (with image)", tags_with_images)
            row = df[df["Tag"] == sel].iloc[0]
            img_bytes = row.get("ImageData")
            if isinstance(img_bytes, (bytes, bytearray)) and looks_like_image(img_bytes):
                st.image(img_bytes, width=100, caption="📷 Preview")
                date_val = pd.to_datetime(row["Date"], errors="coerce")
                date_str = date_val.strftime("%Y-%m-%d") if not pd.isna(date_val) else "unknown"
                st.download_button(
                    "⬇️ Download Image",
                    data=img_bytes,
                    file_name=f"{sel}_{date_str}.jpg",
                    mime="image/jpeg"
                )
            else:
                st.info("No valid image for this record.")
        else:
            st.info("No tags with images found.")

        # Excel export
        export_df = df.copy()
        export_df["Date"] = pd.to_datetime(export_df["Date"], errors="coerce").dt.strftime("%Y-%m-%d")
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
