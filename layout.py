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

/* SEMBUNYIKAN TOOLBAR BAWAAN STREAMLIT (Deploy, menu, dsb) */
header[data-testid="stHeader"]{
    visibility:hidden;
    height:0;
}

[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
#MainMenu,
footer{
    visibility:hidden;
    height:0;
}

/* PAGE PADDING */
.block-container{
    padding-top:1.2rem !important;
    padding-bottom:0.8rem !important;
    padding-left:2rem !important;
    padding-right:2rem !important;
}

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
    border-radius:12px;
    padding:8px 14px;
    box-shadow:0 3px 10px rgba(0,0,0,.08);
    overflow:hidden;
}

/* ---------- ROW 1 ---------- */

/* Summary */
.st-key-summary_card{
    height:20vh;
}

/* Trend */
.st-key-trend_card{
    height:20vh;
}

/* ---------- ROW 2 ---------- */

/* Province (tall, kiri) */
.st-key-row2_left_card{
    height:29vh;
}

/* Top Product (bawah kiri) */
.st-key-top_card{
    height:21vh;
}

/* Category (kanan atas) */
.st-key-row2_middle_card{
    height:25vh;
}

/* Return (kanan bawah) */
.st-key-row2_right_card{
    height:25vh;
}

/* ================= HEADINGS ================= */

.st-key-summary_card h3,
.st-key-trend_card h3,
.st-key-top_card h3,
.st-key-row2_left_card h3,
.st-key-row2_middle_card h3,
.st-key-row2_right_card h3{
    font-size:15px;
    margin:0 0 6px 0;
}

[data-testid="stMetricValue"]{
    font-size:20px !important;
}

[data-testid="stMetricLabel"]{
    font-size:12px !important;
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

/* ================= SALES SUMMARY BOXES ================= */

.summary-grid{
    display:flex;
    gap:12px;
    margin-top:14px;
    margin-bottom:20px;
}

.summary-box{
    flex:1;
    background:#DCEAFB;
    border-radius:14px;
    padding:14px 12px;
    display:flex;
    flex-direction:column;
    align-items:flex-start;
    height: 100px;
    width: 100px;
}

.summary-icon{
    width:27px;
    height:27px;
    border-radius:50%;
    background:#1B2559;
    color:#FFFFFF !important;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:15px;
    margin-bottom:10px;
}

.summary-value{
    font-size:20px;
    font-weight:700;
    color:#111 !important;
    line-height:1.1;
}

.summary-label{
    font-size:12.5px;
    color:#666 !important;
    margin-top:2px;
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
# REVENUE PER PRODUCT CATEGORY
# ==========================

revenue_category = (
    df.groupby("product_category")["revenue"]
    .sum()
    .reset_index()
    .sort_values("revenue", ascending=True)
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
    height=115,
    margin=dict(l=10, r=10, t=30, b=10),

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

    height=135,

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

fig_category = px.bar(
    revenue_category,
    x="revenue",
    y="product_category",
    orientation="h",
    color="revenue",
    color_continuous_scale="Blues",
    text="revenue"
)

fig_category.update_traces(
    texttemplate="%{text:.2s}",
    textposition="outside"
)

fig_category.update_layout(
    height=135,

    paper_bgcolor="white",
    plot_bgcolor="white",

    margin=dict(l=10, r=10, t=10, b=10),

    xaxis_title=None,
    yaxis_title=None,

    font=dict(color="black"),

    showlegend=False,
    coloraxis_showscale=False,

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
    height=135, 
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

# =====================================
# ROW 1: Summary | Trend
# =====================================

row1_left, row1_right = st.columns([1.28, 1], gap="small")

with row1_left:

    # ---------- Sales Summary ----------
    with st.container(key="summary_card"):

        st.markdown("### 📊 Sales Summary")

        st.markdown(f"""
        <div class="summary-grid">
            <div class="summary-box">
                <div class="summary-icon">📊</div>
                <div class="summary-value">{format_rupiah(total_revenue)}</div>
                <div class="summary-label">Total Revenue</div>
            </div>
            <div class="summary-box">
                <div class="summary-icon">📄</div>
                <div class="summary-value">{total_orders:,}</div>
                <div class="summary-label">Total Order</div>
            </div>
            <div class="summary-box">
                <div class="summary-icon">⭐</div>
                <div class="summary-value">{avg_rating:.2f}</div>
                <div class="summary-label">Average Rating</div>
            </div>
            <div class="summary-box">
                <div class="summary-icon">📦</div>
                <div class="summary-value">{return_rate:.2f}%</div>
                <div class="summary-label">Return Rate</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with row1_right:

    # ---------- Trend ----------
    with st.container(key="trend_card"):

        st.markdown("### 📈 Tren Penjualan")

        st.plotly_chart(
            fig,
            width="stretch",
            config={"displayModeBar": False}
        )

st.markdown("<div style='height:5px'></div>", unsafe_allow_html=True)

# =====================================
# ROW 2: (Province + Top Product) | (Category + Return)
# =====================================

row2_left, row2_right = st.columns([1, 1.85], gap="small")

with row2_left:

    # ---------- Revenue Province ----------
    with st.container(key="row2_left_card"):

        st.markdown("### 🌍 Revenue per Province")

        st.plotly_chart(
            fig_map, 
            use_container_width=True, 
            config={"displayModeBar": False, "scrollZoom": True} 
)

    st.markdown("<div style='height:5px'></div>", unsafe_allow_html=True)

    # ---------- Top Product ----------
    with st.container(key="top_card"):

        st.markdown("### 🏆 Top 10 Subproduct")

        st.empty()

with row2_right:

    # ---------- Revenue Category ----------
    with st.container(key="row2_middle_card"):

        st.markdown("### 🛍 Revenue per Category")

        st.plotly_chart(
            fig_category,
            width="stretch",
            config={"displayModeBar": False}
        )

    st.markdown("<div style='height:5px'></div>", unsafe_allow_html=True)

    # ---------- Return ----------
    with st.container(key="row2_right_card"):

        st.markdown("### ↩️ Return Analysis")

        st.plotly_chart(
            fig_return,
            width="stretch",
            config={"displayModeBar": False}
        )