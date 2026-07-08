// script.js
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
