"""Exploratory analysis, forecasting, and holdout evaluation for GridCast."""
from __future__ import annotations
import warnings
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.seasonal import seasonal_decompose


def daily_series(daily_df: pd.DataFrame) -> pd.Series:
    s = daily_df.set_index(pd.to_datetime(daily_df["Date"]))["Consumption_kWh"].astype(float)
    s = s[~s.index.duplicated(keep="last")].sort_index().asfreq("D")
    return s.interpolate(method="time").ffill().bfill()


def decompose_series(series: pd.Series, period: int = 7):
    if len(series) < 2 * period:
        raise ValueError(f"At least {2 * period} observations are required for period={period} decomposition.")
    return seasonal_decompose(series, model="additive", period=period, extrapolate_trend="freq")


def _forecast_one(series: pd.Series, horizon: int, model_name: str) -> pd.Series:
    horizon = int(horizon)
    future_index = pd.date_range(series.index[-1] + pd.Timedelta(days=1), periods=horizon, freq="D")
    if model_name == "ARIMA(2,1,2)":
        if len(series) < 40:
            raise ValueError("ARIMA forecasting needs at least 40 daily observations in this project configuration.")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            fitted = ARIMA(series, order=(2, 1, 2), enforce_stationarity=False, enforce_invertibility=False).fit()
            pred = fitted.forecast(steps=horizon)
        values = np.asarray(pred, dtype=float)
    elif model_name == "7-day seasonal naive":
        pattern = series.iloc[-min(7, len(series)):].to_numpy(dtype=float)
        values = np.resize(pattern, horizon)
    elif model_name == "7-day moving average":
        mean = float(series.iloc[-min(7, len(series)):].mean())
        values = np.repeat(mean, horizon)
    elif model_name == "Linear trend":
        # Fit a line to at most the last 365 days to avoid older regimes dominating.
        fit = series.iloc[-min(365, len(series)):]
        x = np.arange(len(fit), dtype=float)
        slope, intercept = np.polyfit(x, fit.to_numpy(dtype=float), deg=1)
        future_x = np.arange(len(fit), len(fit) + horizon, dtype=float)
        values = intercept + slope * future_x
    else:
        raise ValueError(f"Unknown model: {model_name}")
    # kWh cannot be negative; retain valid numeric predictions only.
    values = np.maximum(values, 0.0)
    return pd.Series(values, index=future_index, name=model_name)


def evaluate_models(series: pd.Series, test_days: int = 30) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    if len(series) < 60:
        raise ValueError("Use at least 60 daily observations to compare forecasting models reliably.")
    test_days = min(int(test_days), max(7, len(series) // 4))
    train, test = series.iloc[:-test_days], series.iloc[-test_days:]
    forecasts = {}
    errors = []
    for model_name in ["7-day moving average", "7-day seasonal naive", "Linear trend", "ARIMA(2,1,2)"]:
        try:
            forecasts[model_name] = _forecast_one(train, len(test), model_name)
            pred = forecasts[model_name].to_numpy(dtype=float)
            actual = test.to_numpy(dtype=float)
            errors.append({
                "Model": model_name,
                "MAE_kWh": float(mean_absolute_error(actual, pred)),
                "RMSE_kWh": float(np.sqrt(mean_squared_error(actual, pred))),
                "Test_Days": int(len(test)),
            })
        except Exception as exc:
            errors.append({"Model": model_name, "MAE_kWh": np.nan, "RMSE_kWh": np.nan, "Test_Days": int(len(test)), "Note": str(exc)})
    metrics = pd.DataFrame(errors).sort_values("RMSE_kWh", na_position="last").reset_index(drop=True)
    valid = metrics.dropna(subset=["RMSE_kWh"])
    if valid.empty:
        raise RuntimeError("All forecasting models failed. Check the data and dependencies.")
    best_model = str(valid.iloc[0]["Model"])
    prediction_rows = []
    for model_name, pred_series in forecasts.items():
        for timestamp, pred_value in pred_series.items():
            prediction_rows.append({"Date": timestamp, "Actual_kWh": float(test.loc[timestamp]), "Predicted_kWh": float(pred_value), "Model": model_name})
    prediction_df = pd.DataFrame(prediction_rows)
    return metrics, prediction_df, best_model


def forecast_future(series: pd.Series, horizon: int, model_name: str = "ARIMA(2,1,2)") -> pd.DataFrame:
    future = _forecast_one(series, int(horizon), model_name)
    return pd.DataFrame({"Date": future.index, "Forecast_kWh": future.to_numpy(dtype=float), "Model": model_name})


def dashboard_summary(daily_df: pd.DataFrame) -> dict:
    s = daily_series(daily_df)
    weekly = s.resample("W").mean()
    recent = s.tail(min(30, len(s))).mean()
    previous = s.iloc[-min(60, len(s)):-min(30, len(s))].mean() if len(s) >= 60 else np.nan
    pct = (recent - previous) / previous * 100 if pd.notna(previous) and previous != 0 else np.nan
    return {
        "observations": int(len(s)),
        "mean_daily_kwh": float(s.mean()),
        "peak_daily_kwh": float(s.max()),
        "latest_daily_kwh": float(s.iloc[-1]),
        "recent_vs_previous_30d_pct": float(pct) if pd.notna(pct) else np.nan,
        "weekly_mean_kwh": float(weekly.mean()) if len(weekly) else float(s.mean()),
    }
