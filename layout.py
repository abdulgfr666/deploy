import streamlit as st

st.set_page_config(
    page_title="Dashboard Sales Report",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================
# CSS
# ==========================
st.markdown("""
<style>

/* ===== Background ===== */
.stApp{
    background:#EAF5FF;
}

/* ===== Container ===== */
.block-container{
    max-width:100%;
    padding-top:18px;
    padding-bottom:10px;
    padding-left:40px;
    padding-right:40px;
}

/* ===== Card ===== */
.card{
    background:#FFFFFF;
    border-radius:14px;
    padding:18px;
    box-shadow:0 3px 10px rgba(0,0,0,.08);
    margin-bottom:16px;
}

.card-title{
    font-size:18px;
    font-weight:600;
    color:#22335B;
}

/* Hilangkan jarak column */
div[data-testid="column"]{
    padding:0 .35rem;
}

</style>
""", unsafe_allow_html=True)

# ==========================
# HEADER
# ==========================

st.markdown(
    "<h3 style='color:#8A8A8A;margin-bottom:0;'>    </h3>",
    unsafe_allow_html=True
)

# ==========================
# ROW 1
# ==========================

left, right = st.columns([1.25,1])

with left:

    st.markdown("""
    <div class="card" style="height:150px;">
        <div class="card-title">
            Sales Summary
        </div>
    </div>
    """, unsafe_allow_html=True)

with right:

    st.markdown("""
    <div class="card" style="height:150px;">
        <div class="card-title">
            Tren Penjualan
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==========================
# ROW 2
# ==========================

left, right = st.columns([0.9,1.8])

with left:

    st.markdown("""
    <div class="card" style="height:250px;">
        <div class="card-title">
            Revenue per Province atau City
        </div>
    </div>
    """, unsafe_allow_html=True)

with right:

    st.markdown("""
    <div class="card" style="height:250px;">
        <div class="card-title">
            Revenue per Product Category
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==========================
# ROW 3
# ==========================

left, right = st.columns([0.9,1.8])

with left:

    st.markdown("""
    <div class="card" style="height:180px;">
        <div class="card-title">
            Top 10 Product Subcategory
        </div>
    </div>
    """, unsafe_allow_html=True)

with right:

    st.markdown("""
    <div class="card" style="height:180px;">
        <div class="card-title">
            Return Analysis
        </div>
    </div>
    """, unsafe_allow_html=True)