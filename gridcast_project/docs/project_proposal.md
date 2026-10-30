# GridCast — Project Proposal

## Abstract
GridCast is a Data Mining and Analytics mini-project for analyzing historical electricity consumption and forecasting short-term daily usage. It creates a repeatable pipeline for data ingestion, cleaning, time-series exploration, weekly decomposition, moving-average smoothing, and forecasting. It compares a 7-day moving-average baseline, 7-day seasonal-naive baseline, linear trend, and ARIMA(2,1,2) using a chronological holdout. Mean Absolute Error (MAE) and Root Mean Squared Error (RMSE) are used to compare forecasts. A Streamlit dashboard presents key statistics, trends, weekday/monthly patterns, holdout comparison, and future estimates. The bundled data is synthetic for testing; the final analysis should use the real UCI Individual Household Electric Power Consumption dataset.

## Problem statement
Electricity-use records are often high-frequency and difficult to interpret directly. A compact analytics workflow is needed to transform raw readings into daily consumption, identify trends and recurring patterns, evaluate forecasting approaches, and communicate the results visually.

## Aim
To analyze daily electricity-consumption patterns using descriptive time-series analytics and compare forecasting methods for short-term demand estimation.

## Objectives
1. Load and clean a real electricity-consumption dataset.
2. Convert minute-level active-power observations into estimated daily energy consumption.
3. Summarize data quality and calculate descriptive statistics.
4. Visualize trend, weekly patterns, monthly averages and 7-day moving averages.
5. Decompose the series into trend, seasonal and residual components.
6. Compare simple baselines, linear trend and ARIMA forecasting.
7. Evaluate models using chronological holdout MAE and RMSE.
8. Present the analysis through an interactive dashboard and reproducible output files.

## Scope
The project focuses on one historical household dataset, daily aggregation and short-horizon forecasting. It is a student analytics prototype, not an electricity-grid operational tool. The source data is historical and geographically limited.

## Dataset
UCI Individual Household Electric Power Consumption, DOI 10.24432/C58K54. It provides one-minute measurements across approximately 47 months and includes Date, Time, Global_active_power, Global_reactive_power, Voltage, Global_intensity and sub-metering fields. GridCast uses Date, Time and Global_active_power. Mean valid minute-level active power (kW) multiplied by 24 hours is used as an estimate of daily kWh, provided daily coverage is at least 90%.

## Proposed tools
Python, pandas, NumPy, Matplotlib, statsmodels, scikit-learn, Plotly and Streamlit. Power BI/Tableau can be used for an optional separate dashboard using `outputs/daily_cleaned.csv`.

## Expected deliverables
- Cleaned daily dataset and data-quality summary.
- Time-series line chart and 7-day moving-average chart.
- Monthly and weekday analysis charts.
- Weekly decomposition plot.
- Forecast model comparison table with MAE/RMSE.
- Future forecast CSV and interactive dashboard.
- Project report and presentation.
