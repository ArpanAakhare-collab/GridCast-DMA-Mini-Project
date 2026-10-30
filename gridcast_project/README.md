# GridCast — Electricity Consumption Analytics & Demand Forecasting

**Course:** CS3203T-A — Data Mining and Analytics (DMA)  
**Mini-project focus:** Time-series descriptive analytics, moving-average analysis, ARIMA forecasting, model evaluation and dashboarding.

GridCast analyses daily electricity consumption, separates trend and weekly seasonality, compares forecasting methods on a chronological holdout, and forecasts the next selected number of days. It is aligned with the DMA manual's Experiment 8 (time-series descriptive analytics and simple forecasting) and Experiment 9 (ARIMA, stationarity/differencing concepts and MAE/RMSE evaluation).

> **Important data note:** The bundled `data/sample_daily_consumption.csv` is **synthetic demonstration data** so the project can be tested immediately. For final academic analysis, download and use the real UCI dataset described below. Do not present demo-data metrics as results from the UCI dataset.

## Web dashboard theme

The Streamlit dashboard uses the requested **charcoal black, forest green, and crimson red** palette. Charcoal is used for the canvas and chart backgrounds, forest green for primary data and controls, and crimson for contrasting comparisons/highlights. The Streamlit theme is in `.streamlit/config.toml`; the chart and component styling is in `app.py`.

## Features

- Dataset ingestion for the UCI raw `household_power_consumption.txt` file or a prepared daily CSV.
- Data validation, missing-value handling, daily energy estimation, and 7-day moving average.
- Trend chart, monthly averages, weekday patterns, and additive time-series decomposition.
- Chronological holdout evaluation comparing:
  - 7-day moving-average baseline
  - 7-day seasonal-naive baseline
  - Linear trend
  - ARIMA(2,1,2)
- MAE and RMSE model evaluation.
- Interactive Streamlit dashboard with CSV exports.
- Reproducible outputs saved to `outputs/`.

## Dataset

Use the **UCI Individual Household Electric Power Consumption** dataset:

- Official page: https://archive.ics.uci.edu/dataset/235/individualhouseholdelectricpowerconsumption
- Citation: Hebrail, G. & Berard, A. (2006). *Individual Household Electric Power Consumption*. UCI Machine Learning Repository. DOI: https://doi.org/10.24432/C58K54
- License: CC BY 4.0 (give attribution when reusing/adapting).
- The dataset contains minute-level measurements for one household in Sceaux, France, from December 2006 to November 2010. It is historical household data, not a current city or national grid dataset.

### Download

From a terminal inside this project folder, run:

```bash
python download_dataset.py
```

If the automated download fails, open the official UCI page, download the ZIP, extract `household_power_consumption.txt`, and place it inside `data/`.

For raw UCI data, GridCast estimates daily energy as:

`daily estimated kWh = mean valid minute-level Global_active_power (kW) × 24 hours`

Days with less than 90% valid minute-reading coverage are treated as missing before interpolation. This gives an estimated daily total and assumes valid readings reasonably represent the full day; discuss this limitation in the report.

## Setup (Windows / VS Code)

Python 3.10+ recommended.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, you can use Command Prompt:

```bat
.venv\Scripts\activate.bat
```

## Run analysis and save outputs

With the included synthetic sample:

```bash
python run_analysis.py
```

With the real UCI raw text file:

```bash
python run_analysis.py --input data/household_power_consumption.txt --horizon 14 --model "ARIMA(2,1,2)"
```

The script generates `outputs/` files including:

- `daily_cleaned.csv`
- `model_comparison.csv`
- `holdout_predictions.csv`
- `future_forecast.csv`
- `summary.json`
- `daily_consumption_trend.png`
- `weekly_decomposition.png`
- `holdout_comparison.png`

The model-comparison holdout uses the final 30 daily observations (or a shorter valid window for a short dataset). The time order is preserved; no random split is used.

## Run the interactive dashboard

```bash
streamlit run app.py
```

The dashboard starts with the included synthetic sample. Use the sidebar uploader to upload either:

1. The raw UCI `household_power_consumption.txt` file, or
2. A prepared daily CSV with columns `Date` and `Consumption_kWh`.

For a prepared CSV, each row must represent one day's energy in kWh. Do not upload raw kW values in this column unless you have already converted them.

## Project structure

```text
GridCast/
├── app.py
├── run_analysis.py
├── download_dataset.py
├── requirements.txt
├── gridcast/
│   ├── __init__.py
│   ├── data_loader.py
│   └── analytics.py
├── data/
│   ├── sample_daily_consumption.csv   # synthetic demonstration data
│   └── household_power_consumption.txt  # downloaded real dataset (not bundled)
├── docs/
│   ├── project_proposal.md
│   ├── viva_questions.md
│   └── submission_checklist.md
└── outputs/                           # generated by run_analysis.py
```

## Methodology overview

1. **Extract:** Load the UCI raw text file or prepared daily CSV.
2. **Transform:** Parse dates, convert numeric fields, estimate daily kWh, handle low-coverage days and fill gaps transparently.
3. **Explore:** Calculate descriptive statistics; plot daily trend, monthly mean, weekday patterns and the 7-day moving average.
4. **Decompose:** Use additive seasonal decomposition with period 7 to inspect trend, weekly seasonality and residuals.
5. **Forecast:** Compare moving average, seasonal naive, linear trend and ARIMA(2,1,2).
6. **Evaluate:** Use a chronological holdout and report MAE/RMSE; select the lowest-RMSE model for that holdout only.
7. **Present:** Use the dashboard and generated figures/CSVs to explain findings.

## Important interpretation cautions

- Forecast accuracy on one historical household does not imply accuracy for a city, utility, or future period.
- ARIMA(2,1,2) is an initial model configuration, not a universally optimal setting. Record the measured holdout metrics and consider another order only with a documented comparison.
- Report actual metrics from the real UCI dataset in your final submission. The sample metrics printed by the script when using the bundled CSV are only a software demonstration.
- The code interpolates missing daily values. State this when discussing results and limitations.

## Attribution

Dataset: Hebrail, G. & Berard, A. (2006). *Individual Household Electric Power Consumption*. UCI Machine Learning Repository. https://doi.org/10.24432/C58K54 (CC BY 4.0).

Concepts: Course manual CS3203T-A Data Mining and Analytics, Experiments 8 and 9.
