# Final Submission Checklist

## Before you submit

- [ ] Download the real UCI dataset and store `household_power_consumption.txt` in `data/`.
- [ ] Install dependencies from `requirements.txt`.
- [ ] Run `python run_analysis.py --input data/household_power_consumption.txt --horizon 14 --model "ARIMA(2,1,2)"`.
- [ ] Verify generated `outputs/summary.json`, `outputs/model_comparison.csv`, `outputs/future_forecast.csv`, and PNG charts.
- [ ] Update the report and slides with the **real UCI-run** observations and model metrics; do not use the synthetic demo metrics as actual dataset results.
- [ ] Save screenshots of the interactive dashboard and include them in the report if your teacher requires screenshot evidence.
- [ ] Explain the daily energy estimate, 90% coverage threshold, interpolation method, chronological holdout, MAE and RMSE in your own words.
- [ ] Include UCI attribution and the CC BY 4.0 license note.
- [ ] Test the Streamlit dashboard once with the real raw dataset and once with a prepared daily CSV if time permits.

## Suggested report figures

1. Daily consumption and 7-day moving average.
2. Average consumption by month.
3. Average consumption by day of week.
4. Weekly time-series decomposition.
5. Actual vs holdout forecasts for all models.
6. Future daily forecast.

## Metrics table to paste into the report

Use `outputs/model_comparison.csv`. Report Model, MAE_kWh, RMSE_kWh, and Test_Days. State which model has the lowest RMSE and that it is selected for the specified holdout, not universally.
