import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import unicodedata

st.set_page_config(
    page_title="Dashboard Sales Report",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================
# PETA
# ==========================
def normalize(name: str) -> str:
    name = str(name).strip().lower()
    name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode()
    name = name.replace('di ', '').replace('dki ', '').replace('.', '')
    return name.strip()

ALIAS = {
    'yogyakarta': 'yogyakarta',
    'jakarta raya': 'jakarta',
    'jakarta': 'jakarta',
    'kepulauan bangka belitung': 'bangka belitung',
    'bangka belitung': 'bangka belitung',
    'kepulauan riau': 'kepulauan riau',
}

def alias_key(name: str) -> str:
    n = normalize(name)
    return ALIAS.get(n, n)

@st.cache_data
def load_geojson():
    url = "https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia-province-simple.json"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    geojson_data = resp.json()
    
    for feature in geojson_data['features']:
        nama_asli_geojson = feature['properties']['Propinsi']
        feature['properties']['match_key'] = alias_key(nama_asli_geojson)
        
    return geojson_data

indo_geojson = load_geojson()

# ==========================
# CSS
# ==========================
st.markdown("""
<style>

/* BACKGROUND */
.stApp{
    background:#EAF5FF;
}

/* ================= CARD ================= */

.st-key-summary_card,
.st-key-trend_card,
.st-key-top_card,
.st-key-row2_left_card,
.st-key-row2_middle_card,
.st-key-row2_right_card{

    background:white;
    border-radius:14px;
    padding:18px;
    box-shadow:0 3px 10px rgba(0,0,0,.08);
}

/* ---------- ROW 1 ---------- */

/* Summary */
.st-key-summary_card{
    height:22vh;
}

/* Trend */
.st-key-trend_card{
    height:42vh;
}

/* Top Product */
.st-key-top_card{
    height:42vh;
}

/* ---------- ROW 2 ---------- */

/* Province */
.st-key-row2_left_card{
    height:62vh;
}

/* Category */
.st-key-row2_middle_card{
    height:42vh;
}

/* Return */
.st-key-row2_right_card{
    height:42vh;
}

/* ================= TEXT ================= */

.st-key-summary_card *,
.st-key-trend_card *,
.st-key-top_card *,
.st-key-row2_left_card *,
.st-key-row2_middle_card *,
.st-key-row2_right_card *{

    color:black !important;
}

[data-testid="stMetricLabel"]{
    color:#555 !important;
}

[data-testid="stMetricValue"]{
    color:#111 !important;
}

</style>
""", unsafe_allow_html=True)

# ==========================
# DATA
#===========================

df = pd.read_csv("Data/data_penjualan_clean.csv")
# Ubah order_date menjadi datetime
df['order_date'] = pd.to_datetime(df['order_date'])

# Hitung revenue
df['revenue'] = df['final_price'] * df['quantity']

# Group per bulan
monthly_sales = (
    df.groupby(df['order_date'].dt.to_period('M'))['revenue']
      .sum()
      .reset_index()
)

def format_rupiah(value):
    if value >= 1_000_000_000:
        return f"Rp {value/1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"Rp {value/1_000_000:.2f}M"
    else:
        return f"Rp {value:,.0f}"



monthly_sales['order_date'] = monthly_sales['order_date'].astype(str)


df['match_key'] = df['customer_province'].apply(alias_key)
revenue_provinsi = df.groupby(['customer_province', 'match_key'])['revenue'].sum().reset_index()
revenue_provinsi['Total Revenue'] = revenue_provinsi['revenue'].apply(format_rupiah)



# ==========================
# SALES SUMMARY
# ==========================

# Revenue
total_revenue = (df['final_price'] * df['quantity']).sum()


# Total Order
total_orders = df['order_id'].nunique()

# Return Rate
return_rate = (df['is_returned'].sum() / total_orders) * 100

# Rating Rata-rata
avg_rating = df['rating'].mean()

# ==========================
# RETURN ANALYSIS
# ==========================

return_df = (
    df[df["is_returned"] == True]
    .groupby("return_reason")
    .size()
    .reset_index(name="total_return")
    .sort_values("total_return", ascending=True)
)

# ==========================
# CHART
# ==========================

# Line chart
fig = px.line(
    monthly_sales,
    x='order_date',
    y='revenue',
    markers=True
)

fig.update_layout(
    height=210,
    margin=dict(l=10, r=10, t=40, b=10),

    paper_bgcolor="white",     # Background luar
    plot_bgcolor="white",      # Background area grafik

    font=dict(color="black"),  # Warna tulisan

    xaxis_title=None,
    yaxis_title=None,

    xaxis=dict(
        showgrid=False,
        tickfont=dict(color="black")
    ),

    yaxis=dict(
        showgrid=True,
        gridcolor="#E5E7EB",
        tickfont=dict(color="black")
    )
)

fig_return = px.bar(
    return_df,
    x="total_return",
    y="return_reason",
    orientation="h",
    text="total_return"
)

fig_return.update_traces(
    textposition="outside"
)

fig_return.update_layout(

    height=210,

    paper_bgcolor="white",
    plot_bgcolor="white",

    margin=dict(l=10, r=10, t=10, b=10),

    xaxis_title=None,
    yaxis_title=None,

    font=dict(color="black"),

    xaxis=dict(
        showgrid=True,
        gridcolor="#E5E7EB",
        tickfont=dict(color="black")
    ),

    yaxis=dict(
        showgrid=False,
        tickfont=dict(color="black")
    )
)

# Map Chart Revenue per Provinsi
fig_map = px.choropleth_mapbox(
    revenue_provinsi,
    geojson=indo_geojson,
    locations='match_key',
    featureidkey='properties.match_key',
    color='revenue',
    color_continuous_scale="Blues",
    mapbox_style="carto-positron",
    zoom=3.0, 
    center={"lat": -2.0, "lon": 118.0},
    opacity=0.8,
    hover_name='customer_province',
    hover_data={'revenue': False, 'match_key': False, 'Total Revenue': True} 
)

fig_map.update_layout(
    height=400, 
    margin={"r":0,"t":0,"l":0,"b":0},
    paper_bgcolor="white",
    plot_bgcolor="white",
    coloraxis_showscale=False,
    dragmode=False 
)


# ==========================
# HEADER
# ==========================

# st.markdown(
#     "<h3 style='color:#8A8A8A;margin-top:0;'></h3>",
#     unsafe_allow_html=True
# )

# =====================================
# DASHBOARD
# =====================================

col1, col2, col3 = st.columns(3, gap="medium")

# =====================================
# COLUMN 1
# =====================================

with col1:

    # ---------- Sales Summary ----------
    with st.container(key="summary_card"):

        st.markdown("### 📊 Sales Summary")

        c1, c2 = st.columns(2)

        with c1:
            st.metric("💰 Revenue", format_rupiah(total_revenue))
            st.metric("📦 Orders", f"{total_orders:,}")

        with c2:
            st.metric("↩️ Return", f"{return_rate:.2f}%")
            st.metric("⭐ Rating", f"{avg_rating:.2f}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------- Revenue Province ----------
    with st.container(key="row2_left_card"):

        st.markdown("### 🌍 Revenue per Province")

        st.plotly_chart(
            fig_map, 
            use_container_width=True, 
            config={"displayModeBar": False, "scrollZoom": True} 
)

# =====================================
# COLUMN 2
# =====================================

with col2:

    # ---------- Trend ----------
    with st.container(key="trend_card"):

        st.markdown("### 📈 Tren Penjualan")

        st.plotly_chart(
            fig,
            width="stretch",
            config={"displayModeBar": False}
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------- Revenue Category ----------
    with st.container(key="row2_middle_card"):

        st.markdown("### 🛍 Revenue per Category")

        st.empty()

# =====================================
# COLUMN 3
# =====================================

with col3:

    # ---------- Top Product ----------
    with st.container(key="top_card"):

        st.markdown("### 🏆 Top 10 Subproduct")

        st.empty()

    st.markdown("<br>", unsafe_allow_html=True)

    # ---------- Return ----------
    with st.container(key="row2_right_card"):

        st.markdown("### ↩️ Return Analysis")

        st.plotly_chart(
            fig_return,
            width="stretch",
            config={"displayModeBar": False}
        )