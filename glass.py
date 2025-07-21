import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3, os, io, pathlib
from datetime import datetime, date
from PIL import Image
from streamlit_autorefresh import st_autorefresh

# ── DB bootstrap ───────────────────────────────────────────
if not os.path.exists("glass_defects.db"):
    from init_db import init_db
    init_db()

# ── Streamlit config ───────────────────────────────────────
st.set_page_config(page_title="Glass Guard", layout="wide")
st_autorefresh(interval=300_000, key="auto_refresh")   # 5‑min auto-refresh

# ── Logo ───────────────────────────────────────────────────
st.markdown("<div style='text-align:center'>", unsafe_allow_html=True)
st.image("KV-Logo-1.png", width=150)
st.markdown("</div>", unsafe_allow_html=True)

# ── Paths ──────────────────────────────────────────────────
BASE_DIR = pathlib.Path(__file__).parent
DB_PATH  = BASE_DIR / "glass_defects.db"
IMG_DIR  = BASE_DIR / "images"
os.makedirs(IMG_DIR, exist_ok=True)

# ── DB connection & dataframe ──────────────────────────────
conn   = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

#── CLEANUP any leftover test records (optional) ────────────
cursor.execute("DELETE FROM defects WHERE Tag LIKE '%test%'")
conn.commit()

df     = pd.read_sql_query("SELECT * FROM defects", conn)
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

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
        # ── PREVIEW RIGHT AFTER UPLOAD ─────────────────────────
        if up_img:
            st.image(up_img, caption="🖼️ Preview", use_container_width=True)
        submit_btn = st.form_submit_button("🚀 SAVE RECORD")

    if submit_btn:
        if not tag:
            st.error("Tag# is required.")
        else:
            po_clean = po.strip() or None
            chosen_date = date_val.strftime("%Y-%m-%d")

            # ── Image → hex storage ───────────────────
            if up_img:
                max_mb = 2
                up_img.seek(0, os.SEEK_END)
                if up_img.tell()/(1024*1024) > max_mb:
                    st.error(f"Image exceeds {max_mb} MB.")
                    st.stop()
                up_img.seek(0)
                hex_str = up_img.read().hex()
                safe_tag = tag.replace(" ", "_")
                hex_name = f"{safe_tag}_{chosen_date}.hex"
                p = IMG_DIR/hex_name
                ctr = 1
                while p.exists():
                    p = IMG_DIR/f"{safe_tag}_{chosen_date}_{ctr}.hex"
                    ctr += 1
                p.write_text(hex_str)

            cursor.execute("""
                INSERT INTO defects
                (PO, Tag, Size, Quantity, Scratch_Location, Scratch_Type,
                 Glass_Type, Rack_Type, Vendor, Date, Note)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (po_clean, tag.strip(), size.strip(), qty, loc, stype,
                  gtype, rtype, vendor, chosen_date, note.strip()))
            conn.commit()

            st.success("✅ Submitted!")
            st.toast("Record saved!", icon="💾")
            st.rerun()


# ╭────────────────────────── TAB 3 – Data Table ────────────╮
with tab3:
    st.title("📄 All Scratch Records")

    # … your metrics and delete-expander here …

    if df.empty:
        st.info("No data available.")
    else:
        st.markdown("### 📋 All Scratch Records Table")
        all_df = (
            df.sort_values("Date", ascending=False)
              .loc[:, ["Tag","Date","Quantity","Scratch_Type","Glass_Type"]]
              .rename(columns={
                  "Tag":"Tag#","Quantity":"QTY",
                  "Scratch_Type":"Type","Glass_Type":"Glass"
              })
        )
        all_df["Date"] = all_df["Date"].dt.strftime("%Y-%m-%d")
        st.dataframe(all_df, use_container_width=True, height=400)

        sel = st.selectbox("Select Tag# to download its image", all_df["Tag#"])
        row = df[df["Tag"] == sel].iloc[0]

        # build a prefix and glob for ANY matching .hex
        prefix = sel.replace(" ", "_")
        matches = list(IMG_DIR.glob(f"{prefix}_*.hex"))

        if matches:
            hex_path = matches[0]
            img_bytes = bytes.fromhex(hex_path.read_text())
            st.download_button(
                "⬇️ Download Image",
                data=img_bytes,
                file_name=f"{sel}.jpg",
                mime="image/jpeg",
            )
        else:
            st.info("No image for this record.")

        # Excel export
        buf = io.BytesIO()
        df.to_excel(buf, index=False)
        buf.seek(0)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            "⬇️ Download full backup (Excel)",
            data=buf,
            file_name=f"glass_defects_backup_{stamp}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

# ╭────────────────────────── END ──────────────────────────╮