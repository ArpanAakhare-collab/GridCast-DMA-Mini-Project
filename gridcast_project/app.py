from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import matplotlib.pyplot as plt

from gridcast.data_loader import load_daily_consumption, load_daily_consumption_bytes
from gridcast.analytics import daily_series, decompose_series, evaluate_models, forecast_future, dashboard_summary

ROOT = Path(__file__).resolve().parent
SAMPLE = ROOT / "data" / "sample_daily_consumption.csv"

# GridCast visual system: charcoal black + forest green + crimson red.
CHARCOAL = "#101411"
SURFACE = "#171D19"
SURFACE_RAISED = "#1D2620"
FOREST = "#2E8B57"
FOREST_BRIGHT = "#43A86F"
CRIMSON = "#C1123F"
TEXT = "#EEF3EF"
MUTED = "#A5B2A9"
GRID = "#2B3830"

st.set_page_config(page_title="GridCast | Electricity Analytics", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

# Streamlit-native theme is configured in .streamlit/config.toml; CSS adds the project-specific finish.
st.markdown(f"""
<style>
:root {{
  --gridcast-bg: {CHARCOAL};
  --gridcast-surface: {SURFACE};
  --gridcast-raised: {SURFACE_RAISED};
  --gridcast-green: {FOREST};
  --gridcast-red: {CRIMSON};
  --gridcast-text: {TEXT};
  --gridcast-muted: {MUTED};
}}
[data-testid=\"stAppViewContainer\"] {{
  background: radial-gradient(ellipse at 92% 0%, rgba(46,139,87,.15), transparent 35%), {CHARCOAL};
  color: {TEXT};
}}
[data-testid=\"stHeader\"] {{ background: rgba(16,20,17,.86); }}
[data-testid=\"stSidebar\"] {{ background: linear-gradient(180deg, #171D19 0%, #121713 100%); border-right: 1px solid #2B3830; }}
[data-testid=\"stSidebar\"] h2, [data-testid=\"stSidebar\"] label {{ color: {TEXT}; }}
.block-container {{ max-width: 1560px; padding-top: 2.0rem; padding-bottom: 3rem; }}
h1 {{ color: {TEXT} !important; font-weight: 850 !important; letter-spacing: -.045em; }}
h2, h3 {{ color: {TEXT} !important; font-weight: 700 !important; letter-spacing: -.02em; }}
p, li, label {{ color: #D5DED8; }}
[data-testid=\"stMetric\"] {{ background: linear-gradient(135deg, #1D2620 0%, #151A17 100%); border: 1px solid #304638; border-left: 4px solid {FOREST}; border-radius: 14px; padding: 16px 18px; box-shadow: 0 8px 24px rgba(0,0,0,.14); }}
[data-testid=\"stMetricLabel\"] {{ color: {MUTED} !important; font-size: .88rem; }}
[data-testid=\"stMetricValue\"] {{ color: {TEXT} !important; font-weight: 760; }}
[data-testid=\"stMetricDelta\"] svg {{ color: {CRIMSON}; }}
[data-testid=\"stInfo\"] {{ background: #17251C; border: 1px solid #2F6848; border-radius: 10px; }}
[data-testid=\"stSuccess\"] {{ background: #17251C; border: 1px solid {FOREST}; border-radius: 10px; }}
[data-testid=\"stWarning\"], [data-testid=\"stError\"] {{ background: #29171D; border: 1px solid {CRIMSON}; border-radius: 10px; }}
[data-testid=\"stPlotlyChart\"], [data-testid=\"stDataFrame\"] {{ border: 1px solid #28352D; border-radius: 12px; overflow: hidden; }}
[data-testid=\"stFileUploader\"] {{ background: #151B17; border: 1px dashed #3A6248; border-radius: 12px; padding: 8px; }}
.stDownloadButton button, .stButton button {{ background: {FOREST}; color: white; border: 1px solid {FOREST_BRIGHT}; border-radius: 9px; font-weight: 650; transition: all .15s ease; }}
.stDownloadButton button:hover, .stButton button:hover {{ background: #246D45; border-color: {CRIMSON}; color: white; }}
[data-baseweb=\"select\"] > div, [data-baseweb=\"input\"] > div {{ background: #151B17; border-color: #36473C; }}
hr {{ border-color: #2B3830; }}
footer {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)

# Apply one consistent Plotly theme to charts, labels, grids and hover surfaces.
pio.templates["gridcast_dark"] = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor=CHARCOAL, plot_bgcolor=SURFACE, font=dict(color=TEXT, family="Inter, Segoe UI, sans-serif"),
        colorway=[FOREST_BRIGHT, CRIMSON, FOREST, "#8FA99A"],
        xaxis=dict(gridcolor=GRID, linecolor=GRID, zerolinecolor=GRID, ticks="outside", tickcolor=GRID),
        yaxis=dict(gridcolor=GRID, linecolor=GRID, zerolinecolor=GRID, ticks="outside", tickcolor=GRID),
        legend=dict(bgcolor="rgba(16,20,17,.65)", bordercolor=GRID, borderwidth=0),
        hoverlabel=dict(bgcolor="#1D2620", bordercolor=FOREST, font=dict(color=TEXT)),
        title=dict(font=dict(color=TEXT, size=16)),
    )
)
pio.templates.default = "gridcast_dark"

# A custom header creates a more deliberate first impression without adding visual clutter.
st.markdown(
    f"""<div style=\"display:flex;align-items:center;gap:14px;margin:0 0 4px 0;\">
      <div style=\"width:48px;height:48px;display:flex;align-items:center;justify-content:center;border-radius:13px;background:linear-gradient(145deg,{FOREST},#163D29);border:1px solid #4A9D6A;font-size:25px;box-shadow:0 8px 24px rgba(0,0,0,.25);\">⚡</div>
      <div><div style=\"font-size:2.2rem;line-height:1.05;font-weight:850;letter-spacing:-.05em;color:{TEXT};\">GridCast</div>
      <div style=\"font-size:1rem;color:{MUTED};margin-top:5px;\">Electricity Consumption Analytics &amp; Demand Forecasting</div></div>
      <div style=\"margin-left:auto;padding:7px 11px;border-radius:99px;border:1px solid #385642;background:#17251C;color:#8DD7A9;font-size:.78rem;font-weight:700;letter-spacing:.07em;\">DMA · TIME SERIES</div>
    </div>
    <div style=\"height:1px;background:linear-gradient(90deg,{FOREST},#2B3830 55%,transparent);margin:20px 0 10px;\"></div>""",
    unsafe_allow_html=True,
)
st.caption("Time-series analytics · Descriptive statistics · Moving averages · ARIMA forecasting")

with st.sidebar:
    st.header("Data & Forecast Settings")
    upload = st.file_uploader("Upload data", type=["txt", "csv"], help="UCI raw file: household_power_consumption.txt; or prepared daily CSV with Date and Consumption_kWh.")
    horizon = st.slider("Forecast horizon (days)", min_value=7, max_value=60, value=14, step=7)
    st.markdown("**Forecasting models**")
    selected_model = st.selectbox("Future forecast model", ["ARIMA(2,1,2)", "7-day seasonal naive", "7-day moving average", "Linear trend"])
    st.caption("Use chronological holdout evaluation; do not randomly shuffle time-series data.")

try:
    if upload is not None:
        daily, meta = load_daily_consumption_bytes(upload.name, upload.getvalue())
        data_label = upload.name
    else:
        daily, meta = load_daily_consumption(SAMPLE)
        data_label = "Included synthetic demonstration data"
except Exception as exc:
    st.error(f"Could not load the selected dataset: {exc}")
    st.info("For a prepared daily CSV, use columns named Date and Consumption_kWh. For UCI raw data, keep Date, Time and Global_active_power.")
    st.stop()

series = daily_series(daily)
summary = dashboard_summary(daily)

st.info(f"Loaded: **{data_label}** · {summary['observations']:,} daily observations · {meta['date_start']} to {meta['date_end']}. The included sample is synthetic; use the UCI dataset for your final academic results.")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Average daily consumption", f"{summary['mean_daily_kwh']:.2f} kWh")
k2.metric("Peak daily consumption", f"{summary['peak_daily_kwh']:.2f} kWh")
k3.metric("Latest day", f"{summary['latest_daily_kwh']:.2f} kWh")
if pd.notna(summary["recent_vs_previous_30d_pct"]):
    k4.metric("Recent 30-day change", f"{summary['recent_vs_previous_30d_pct']:+.1f}%")
else:
    k4.metric("Recent 30-day change", "N/A")

st.markdown("### 1. Consumption trend")
trend = daily.copy()
fig = go.Figure()
fig.add_trace(go.Scatter(x=trend["Date"], y=trend["Consumption_kWh"], mode="lines", name="Daily consumption", line=dict(color=FOREST_BRIGHT, width=1.6), fill="tozeroy", fillcolor="rgba(46,139,87,.10)"))
fig.add_trace(go.Scatter(x=trend["Date"], y=trend["Rolling_7D_kWh"], mode="lines", name="7-day moving average", line=dict(color=CRIMSON, width=3)))
fig.update_layout(height=400, margin=dict(l=10, r=10, t=25, b=10), xaxis_title="Date", yaxis_title="Estimated daily consumption (kWh)", legend=dict(orientation="h", y=1.12), hovermode="x unified")
st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    st.markdown("### 2. Monthly pattern")
    month = daily.assign(Month=pd.to_datetime(daily["Date"]).dt.to_period("M").astype(str)).groupby("Month", as_index=False)["Consumption_kWh"].mean()
    figm = px.bar(month, x="Month", y="Consumption_kWh", title="Average consumption by month", labels={"Consumption_kWh": "Mean kWh/day"})
    figm.update_traces(marker_color=FOREST, marker_line_color=FOREST_BRIGHT, marker_line_width=0.7)
    figm.update_layout(height=350, margin=dict(l=10, r=10, t=45, b=10), xaxis_tickangle=-45)
    st.plotly_chart(figm, use_container_width=True)
with right:
    st.markdown("### 3. Day-of-week pattern")
    weekday = daily.assign(Day=pd.to_datetime(daily["Date"]).dt.day_name()).groupby("Day", as_index=False)["Consumption_kWh"].mean()
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday["Day"] = pd.Categorical(weekday["Day"], categories=order, ordered=True)
    weekday = weekday.sort_values("Day")
    figw = px.bar(weekday, x="Day", y="Consumption_kWh", title="Average consumption by day of week", labels={"Consumption_kWh": "Mean kWh/day"})
    figw.update_traces(marker_color=CRIMSON, marker_line_color="#E04B6C", marker_line_width=0.7)
    figw.update_layout(height=350, margin=dict(l=10, r=10, t=45, b=10))
    st.plotly_chart(figw, use_container_width=True)

st.markdown("### 4. Trend, seasonality and residual decomposition")
if len(series) >= 14:
    try:
        result = decompose_series(series, period=7)
        figd, axes = plt.subplots(4, 1, figsize=(12, 8), sharex=True, facecolor=CHARCOAL)
        series_colors = [FOREST_BRIGHT, FOREST, CRIMSON, MUTED]
        axis_labels = ["Observed", "Trend", "Weekly", "Residual"]
        for ax, values, color, label in zip(axes, [result.observed, result.trend, result.seasonal, result.resid], series_colors, axis_labels):
            ax.set_facecolor(SURFACE)
            ax.plot(values, linewidth=1.35, color=color)
            ax.set_ylabel(label, color=TEXT, fontsize=9)
            ax.tick_params(colors=MUTED, labelsize=8)
            ax.grid(True, color=GRID, linewidth=0.6, alpha=0.75)
            for spine in ax.spines.values():
                spine.set_color(GRID)
        axes[3].set_xlabel("Date", color=TEXT)
        figd.tight_layout(pad=1.2)
        st.pyplot(figd, use_container_width=True)
        plt.close(figd)
    except Exception as exc:
        st.warning(f"Decomposition could not be calculated: {exc}")
else:
    st.warning("At least 14 daily observations are required for weekly decomposition.")

st.markdown("### 5. Forecasting model comparison")
if len(series) >= 60:
    try:
        metrics, test_predictions, best_model = evaluate_models(series, test_days=30)
        st.caption("Evaluation uses the last 30 days as a chronological holdout; earlier observations are used for training. Lowest RMSE is marked as best for this holdout only.")
        st.dataframe(metrics.round(3), use_container_width=True, hide_index=True)
        valid = metrics.dropna(subset=["RMSE_kWh"])
        if not valid.empty:
            st.success(f"Lowest holdout RMSE: **{best_model}**. This does not guarantee it will be best for every future period.")
        comp = test_predictions[test_predictions["Model"].isin([best_model, "7-day seasonal naive"])].copy()
        if not comp.empty:
            figc = go.Figure()
            actual = series.iloc[-int(metrics["Test_Days"].max()):]
            figc.add_trace(go.Scatter(x=actual.index, y=actual.values, mode="lines", name="Actual", line=dict(color=FOREST_BRIGHT, width=3)))
            for m in comp["Model"].unique():
                sub = comp[comp["Model"] == m]
                figc.add_trace(go.Scatter(x=sub["Date"], y=sub["Predicted_kWh"], mode="lines", name=m, line=dict(color=CRIMSON if m != best_model else FOREST, dash="dash", width=2)))
            figc.update_layout(height=350, margin=dict(l=10, r=10, t=20, b=10), xaxis_title="Date", yaxis_title="Consumption (kWh)")
            st.plotly_chart(figc, use_container_width=True)
        future = forecast_future(series, horizon, selected_model)
        figf = go.Figure()
        figf.add_trace(go.Scatter(x=series.tail(60).index, y=series.tail(60).values, mode="lines", name="Recent actual", line=dict(color=FOREST_BRIGHT, width=2)))
        figf.add_trace(go.Scatter(x=future["Date"], y=future["Forecast_kWh"], mode="lines+markers", name=f"{selected_model} forecast", line=dict(color=CRIMSON, width=3, dash="dash"), marker=dict(size=6, color=CRIMSON)))
        figf.update_layout(height=380, margin=dict(l=10, r=10, t=25, b=10), xaxis_title="Date", yaxis_title="Forecast consumption (kWh)")
        st.plotly_chart(figf, use_container_width=True)
        st.download_button("Download forecast CSV", data=future.to_csv(index=False).encode("utf-8"), file_name="gridcast_forecast.csv", mime="text/csv")
        st.download_button("Download model comparison CSV", data=metrics.to_csv(index=False).encode("utf-8"), file_name="gridcast_model_metrics.csv", mime="text/csv")
    except Exception as exc:
        st.error(f"Model comparison failed: {exc}")
else:
    st.warning("At least 60 daily observations are needed for a meaningful holdout comparison.")

with st.expander("Dataset quality and processing details"):
    st.json(meta)
    st.write("For the UCI raw file, daily estimated energy is computed as daily mean valid active power (kW) × 24 hours. Days with less than 90% minute-reading coverage are treated as missing before time interpolation. This is an estimate; it assumes the valid readings are reasonably representative of the day.")
    st.write("Source dataset: UCI Individual Household Electric Power Consumption. This source represents one household in France from December 2006 to November 2010, not a current city or national grid.")

st.markdown("<div style='margin-top:26px;padding:14px 16px;border-top:1px solid #2B3830;color:#8F9F95;font-size:.82rem;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;'><span><b style='color:#43A86F'>GRIDCAST</b> · Academic demand analytics</span><span>Charcoal · Forest Green · Crimson</span></div>", unsafe_allow_html=True)
st.caption("GridCast is an academic demonstration. Forecasts are estimates, not operational instructions for a utility provider.")
