"""Run GridCast analysis and save reproducible CSV/PNG outputs."""
from pathlib import Path
import argparse
import json
import pandas as pd
import matplotlib.pyplot as plt

from gridcast.data_loader import load_daily_consumption
from gridcast.analytics import daily_series, decompose_series, evaluate_models, forecast_future, dashboard_summary

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description="GridCast electricity consumption analytics")
    parser.add_argument("--input", default=str(ROOT / "data" / "sample_daily_consumption.csv"), help="Path to UCI raw .txt or prepared daily CSV")
    parser.add_argument("--horizon", type=int, default=14, help="Future forecast horizon in days (7–60 recommended)")
    parser.add_argument("--model", default="ARIMA(2,1,2)", choices=["ARIMA(2,1,2)", "7-day seasonal naive", "7-day moving average", "Linear trend"])
    args = parser.parse_args()
    out = ROOT / "outputs"
    out.mkdir(exist_ok=True)
    daily, metadata = load_daily_consumption(args.input)
    daily.to_csv(out / "daily_cleaned.csv", index=False)
    series = daily_series(daily)
    summary = dashboard_summary(daily)
    if len(series) >= 60:
        metrics, predictions, best = evaluate_models(series, test_days=30)
        metrics.to_csv(out / "model_comparison.csv", index=False)
        predictions.to_csv(out / "holdout_predictions.csv", index=False)
        (out / "best_holdout_model.txt").write_text(best, encoding="utf-8")
        future = forecast_future(series, max(1, min(60, args.horizon)), args.model)
        future.to_csv(out / "future_forecast.csv", index=False)
    else:
        print("Warning: fewer than 60 daily observations; forecast comparison skipped.")
        metrics = predictions = future = None
        best = None
    with (out / "summary.json").open("w", encoding="utf-8") as f:
        json.dump({"input_file": str(Path(args.input).name), "dataset_metadata": metadata, "summary": summary, "best_holdout_model": best}, f, indent=2, default=str)

    # Trend chart
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(series.index, series.values, label="Daily consumption", linewidth=0.75)
    ax.plot(series.index, series.rolling(7, min_periods=1).mean(), label="7-day moving average", linewidth=2)
    ax.set_title("GridCast: Daily Electricity Consumption")
    ax.set_xlabel("Date"); ax.set_ylabel("Estimated consumption (kWh/day)"); ax.legend(); fig.tight_layout()
    fig.savefig(out / "daily_consumption_trend.png", dpi=160); plt.close(fig)

    # Decomposition chart
    if len(series) >= 14:
        try:
            dec = decompose_series(series, period=7)
            fig = dec.plot(); fig.set_size_inches(12, 8); fig.tight_layout()
            fig.savefig(out / "weekly_decomposition.png", dpi=160); plt.close(fig)
        except Exception as exc:
            print(f"Could not create decomposition chart: {exc}")

    # Holdout chart
    if predictions is not None and metrics is not None:
        test_days = int(metrics["Test_Days"].max())
        actual = series.iloc[-test_days:]
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(actual.index, actual.values, label="Actual", linewidth=2.5)
        for model_name in predictions["Model"].unique():
            tmp = predictions[predictions["Model"] == model_name]
            ax.plot(tmp["Date"], tmp["Predicted_kWh"], label=model_name, linestyle="--", linewidth=1.3)
        ax.set_title("Chronological Holdout: Actual vs Forecast")
        ax.set_xlabel("Date"); ax.set_ylabel("Consumption (kWh)"); ax.legend(); fig.tight_layout()
        fig.savefig(out / "holdout_comparison.png", dpi=160); plt.close(fig)

    print("GridCast analysis completed.")
    print(f"Input: {args.input}")
    print(f"Observations: {summary['observations']}; dates: {metadata['date_start']} to {metadata['date_end']}")
    print(f"Average daily consumption: {summary['mean_daily_kwh']:.3f} kWh")
    if metrics is not None:
        print("\nHoldout model comparison (last 30 days; lowest RMSE first):")
        print(metrics.round(3).to_string(index=False))
        print(f"\nBest model by holdout RMSE: {best}")
        print(f"Future forecast saved to {out / 'future_forecast.csv'}")
    print(f"Outputs saved to: {out}")

if __name__ == "__main__":
    main()
