import pandas as pd
import plotly.express as px
import requests
import unicodedata
import json
import os

# ==========================
# PETA HELPER
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

# ==========================
# LOAD DATA
# ==========================
df = pd.read_csv("Data/data_penjualan_clean.csv")
df['order_date'] = pd.to_datetime(df['order_date'])
df['revenue'] = df['final_price'] * df['quantity']

# ==========================
# GEOJSON
# ==========================
url = "https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia-province-simple.json"
resp = requests.get(url, timeout=30)
indo_geojson = resp.json()
for feature in indo_geojson['features']:
    nama_asli_geojson = feature['properties']['Propinsi']
    feature['properties']['match_key'] = alias_key(nama_asli_geojson)

# ==========================
# AGGREGATIONS
# ==========================
monthly_sales = df.groupby(df['order_date'].dt.to_period('M'))['revenue'].sum().reset_index()
monthly_sales['order_date'] = monthly_sales['order_date'].astype(str)

def format_rupiah(value):
    if value >= 1_000_000_000:
        return f"Rp {value/1_000_000_000:.2f}B"
    elif value >= 1_000_000:
        return f"Rp {value/1_000_000:.2f}M"
    else:
        return f"Rp {value:,.0f}"

df['match_key'] = df['customer_province'].apply(alias_key)
revenue_provinsi = df.groupby(['customer_province', 'match_key'])['revenue'].sum().reset_index()
revenue_provinsi['Total Revenue'] = revenue_provinsi['revenue'].apply(format_rupiah)

total_revenue = (df['final_price'] * df['quantity']).sum()
total_orders = df['order_id'].nunique()
return_rate = (df['is_returned'].sum() / total_orders) * 100
avg_rating = df['rating'].mean()

return_df = (df[df["is_returned"] == True]
    .groupby("return_reason").size().reset_index(name="total_return")
    .sort_values("total_return", ascending=True)
)

revenue_category = (df.groupby("product_category")["revenue"]
    .sum().reset_index().sort_values("revenue", ascending=True)
)
revenue_category['revenue_label'] = revenue_category['revenue'].apply(format_rupiah)

top_subproduct = (df.groupby("product_subcategory")["revenue"]
    .sum().reset_index().sort_values("revenue", ascending=False).head(10)
)
top_subproduct['revenue_label'] = top_subproduct['revenue'].apply(format_rupiah)

# ==========================
# CHARTS
# ==========================
fig_trend = px.line(monthly_sales, x='order_date', y='revenue', markers=True)
fig_trend.update_layout(
    margin=dict(l=10, r=10, t=10, b=10),
    paper_bgcolor="white", plot_bgcolor="white", font=dict(color="black"),
    xaxis_title=None, yaxis_title=None,
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor="#E5E7EB")
)

fig_return = px.bar(return_df, x="total_return", y="return_reason", orientation="h", text="total_return")
fig_return.update_traces(textposition="outside")
fig_return.update_layout(
    paper_bgcolor="white", plot_bgcolor="white", margin=dict(l=10, r=10, t=10, b=10),
    xaxis_title=None, yaxis_title=None, font=dict(color="black"),
    xaxis=dict(showgrid=True, gridcolor="#E5E7EB"),
    yaxis=dict(showgrid=False)
)

fig_category = px.bar(revenue_category, x="revenue", y="product_category", orientation="h", 
                      color="revenue", color_continuous_scale="Blues", text="revenue_label")
fig_category.update_traces(textposition="outside")
fig_category.update_layout(
    paper_bgcolor="white", plot_bgcolor="white", margin=dict(l=10, r=10, t=10, b=10),
    xaxis_title=None, yaxis_title=None, font=dict(color="black"), showlegend=False, coloraxis_showscale=False,
    xaxis=dict(showgrid=True, gridcolor="#E5E7EB"),
    yaxis=dict(showgrid=False)
)

fig_map = px.choropleth_mapbox(revenue_provinsi, geojson=indo_geojson, locations='match_key',
    featureidkey='properties.match_key', color='revenue', color_continuous_scale="Blues",
    mapbox_style="carto-positron", zoom=3.0, center={"lat": -2.0, "lon": 118.0}, opacity=0.8,
    hover_name='customer_province', hover_data={'revenue': False, 'match_key': False, 'Total Revenue': True} 
)
fig_map.update_layout(
    margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="white", plot_bgcolor="white",
    coloraxis_showscale=False, dragmode=False 
)

# Convert plots to JSON for JS frontend
plots = {
    'trend': json.loads(fig_trend.to_json()),
    'return': json.loads(fig_return.to_json()),
    'category': json.loads(fig_category.to_json()),
    'map': json.loads(fig_map.to_json())
}

# ==========================
# BUILD HTML / CSS / JS
# ==========================

top_product_html = ""
for i, row in enumerate(top_subproduct.itertuples(), 1):
    top_product_html += f'''
    <div class="top-product-item">
        <div class="top-product-rank">{i}</div>
        <div class="top-product-details">
            <div class="top-product-name">{row.product_subcategory}</div>
            <div class="top-product-rev">{row.revenue_label}</div>
        </div>
    </div>
    '''

html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Sales Report</title>
    <link rel="stylesheet" href="style.css">
    <script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
</head>
<body>
    <div class="block-container">
        <!-- ROW 1 -->
        <div class="row" style="grid-template-columns: 1.28fr 1fr;">
            <!-- Summary -->
            <div class="card summary-card">
                <h3>📊 Sales Summary</h3>
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
            </div>
            
            <!-- Trend -->
            <div class="card trend-card">
                <h3>📈 Tren Penjualan</h3>
                <div id="trendChart" class="chart-container"></div>
            </div>
        </div>

        <!-- ROW 2 -->
        <div class="row" style="grid-template-columns: 1fr 1.85fr;">
            <!-- Left Col -->
            <div class="col">
                <div class="card map-card" style="height: 33vh; margin-bottom: 15px;">
                    <h3>🌍 Revenue per Province</h3>
                    <div id="mapChart" class="chart-container"></div>
                </div>
                <div class="card top-product-card" style="height: 25vh;">
                    <div style="margin-bottom: 5px;">
                        <div style="font-size: 16px; font-weight: 700; color: #001C3F; margin: 0;">Top 10 Subproduct</div>
                        <div style="font-size: 12px; color: #6D849C; margin-top: 2px;">by Revenue &middot; 2024</div>
                    </div>
                    <div class="top-product-list">
                        {top_product_html}
                    </div>
                </div>
            </div>

            <!-- Right Col -->
            <div class="col">
                <div class="card category-card" style="height: 29vh; margin-bottom: 15px;">
                    <h3>🛍 Revenue per Category</h3>
                    <div id="categoryChart" class="chart-container"></div>
                </div>
                <div class="card return-card" style="height: 29vh;">
                    <h3>↩️ Return Analysis</h3>
                    <div id="returnChart" class="chart-container"></div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        const plotData = {json.dumps(plots)};
    </script>
    <script src="script.js"></script>
</body>
</html>
'''

css_content = '''body {
    margin: 0;
    font-family: "Source Sans Pro", sans-serif;
    background: #EAF5FF;
}

.block-container {
    padding: 1.2rem 2rem;
}

.row {
    display: grid;
    gap: 15px;
    margin-bottom: 15px;
}

.col {
    display: flex;
    flex-direction: column;
}

.card {
    background: white;
    border-radius: 12px;
    padding: 12px 14px;
    box-shadow: 0 3px 10px rgba(0,0,0,.08);
    display: flex;
    flex-direction: column;
    box-sizing: border-box;
}

.card h3 {
    font-size: 15px;
    margin: 0 0 10px 0;
    color: black;
}

.chart-container {
    flex: 1;
    width: 100%;
    min-height: 0;
}

/* ================= SALES SUMMARY BOXES ================= */
.summary-grid {
    display: flex;
    gap: 12px;
    margin-top: 10px;
    height: 100%;
}

.summary-box {
    flex: 1;
    background: #DCEAFB;
    border-radius: 14px;
    padding: 14px 12px;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
}

.summary-icon {
    width: 27px;
    height: 27px;
    border-radius: 50%;
    background: #1B2559;
    color: #FFFFFF;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 15px;
    margin-bottom: 10px;
}

.summary-value {
    font-size: 20px;
    font-weight: 700;
    color: #111;
    line-height: 1.1;
}

.summary-label {
    font-size: 12.5px;
    color: #666;
    margin-top: 2px;
}

/* ================= TOP 10 LIST ================= */
.top-product-list {
    flex: 1;
    overflow-y: auto;
    padding-right: 4px;
    margin-top: 8px;
}

.top-product-list::-webkit-scrollbar {
    width: 5px;
}
.top-product-list::-webkit-scrollbar-track {
    background: transparent;
}
.top-product-list::-webkit-scrollbar-thumb {
    background: #90B4EE;
    border-radius: 10px;
}

.top-product-item {
    display: flex;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid #F0F4F8;
}
.top-product-item:last-child {
    border-bottom: none;
}

.top-product-rank {
    width: 26px;
    height: 26px;
    min-width: 26px;
    background-color: #215299;
    color: white;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 12px;
    margin-right: 12px;
}

.top-product-details {
    display: flex;
    flex-direction: column;
    overflow: hidden;
    flex: 1;
}

.top-product-name {
    font-size: 13px;
    font-weight: 600;
    color: #001C3F;
    margin-bottom: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    width: 100%;
}

.top-product-rev {
    font-size: 11px;
    color: #6D849C;
}
'''

js_content = '''// script.js
const config = {responsive: true, displayModeBar: false};

// Render Trend Chart
Plotly.newPlot('trendChart', plotData.trend.data, plotData.trend.layout, config);

// Render Category Chart
Plotly.newPlot('categoryChart', plotData.category.data, plotData.category.layout, config);

// Render Return Chart
Plotly.newPlot('returnChart', plotData.return.data, plotData.return.layout, config);

// Render Map Chart
const mapConfig = {responsive: true, displayModeBar: false, scrollZoom: true};
Plotly.newPlot('mapChart', plotData.map.data, plotData.map.layout, mapConfig);
'''

# Save the files
with open("public/index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

with open("public/style.css", "w", encoding="utf-8") as f:
    f.write(css_content)

with open("public/script.js", "w", encoding="utf-8") as f:
    f.write(js_content)

print("Build successful! Files are saved in the 'public' directory.")
