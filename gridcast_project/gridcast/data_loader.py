"""Data ingestion and daily electricity-consumption preparation for GridCast."""
from __future__ import annotations

from io import BytesIO, StringIO
from pathlib import Path
from typing import Union
import pandas as pd
import numpy as np

PathLike = Union[str, Path]


def _read_file(path_or_buffer, filename: str | None = None) -> pd.DataFrame:
    name = (filename or getattr(path_or_buffer, "name", "data.csv")).lower()
    if name.endswith(".txt"):
        return pd.read_csv(path_or_buffer, sep=";", na_values=["?", ""], low_memory=False,
                           usecols=lambda c: c.strip() in {"Date", "Time", "Global_active_power", "date", "time", "global_active_power"})
    # UCI's file is a semicolon-separated text table; this branch also supports CSV exports.
    if hasattr(path_or_buffer, "read"):
        data = path_or_buffer.read()
        if isinstance(data, bytes):
            prefix = data[:8192].decode("utf-8", errors="replace")
            stream = BytesIO(data)
        else:
            prefix = data[:8192]
            stream = StringIO(data)
        sep = ";" if prefix.count(";") > prefix.count(",") else ","
        stream.seek(0)
        try:
            return pd.read_csv(stream, sep=sep, na_values=["?", ""], low_memory=False)
        except Exception:
            stream.seek(0)
            return pd.read_csv(stream, sep=None, engine="python", na_values=["?", ""])
    path = Path(path_or_buffer)
    with path.open("r", encoding="utf-8", errors="replace") as f:
        prefix = f.read(8192)
    sep = ";" if prefix.count(";") > prefix.count(",") else ","
    return pd.read_csv(path, sep=sep, na_values=["?", ""], low_memory=False)


def load_daily_consumption(path: PathLike, min_coverage: float = 0.90) -> tuple[pd.DataFrame, dict]:
    """Load a raw UCI household-power text file or a prepared daily CSV.

    UCI raw data: uses mean valid one-minute Global_active_power (kW) × 24 hours
    to estimate a full day's energy consumption (kWh), provided coverage >= threshold.
    Prepared daily CSV should contain Date and Consumption_kWh.
    """
    df = _read_file(path, str(path))
    return prepare_daily_consumption(df, min_coverage=min_coverage, filename=str(path))


def load_daily_consumption_bytes(filename: str, payload: bytes, min_coverage: float = 0.90) -> tuple[pd.DataFrame, dict]:
    stream = BytesIO(payload)
    df = _read_file(stream, filename)
    return prepare_daily_consumption(df, min_coverage=min_coverage, filename=filename)


def prepare_daily_consumption(df: pd.DataFrame, min_coverage: float = 0.90, filename: str = "uploaded dataset") -> tuple[pd.DataFrame, dict]:
    original_rows = int(len(df))
    if df.empty:
        raise ValueError("The supplied file contains no rows.")

    # Normalize names without otherwise changing the source fields.
    rename = {c: str(c).strip().lower().replace(" ", "_") for c in df.columns}
    x = df.rename(columns=rename).copy()
    columns = set(x.columns)

    # UCI minute-level dataset: Date + Time + Global_active_power (kW).
    if {"date", "time", "global_active_power"}.issubset(columns):
        x["timestamp"] = pd.to_datetime(
            x["date"].astype(str).str.strip() + " " + x["time"].astype(str).str.strip(),
            dayfirst=True, errors="coerce"
        )
        x["global_active_power"] = pd.to_numeric(x["global_active_power"], errors="coerce")
        x = x.dropna(subset=["timestamp"]).sort_values("timestamp")
        x["day"] = x["timestamp"].dt.floor("D")
        grouped = x.groupby("day")["global_active_power"]
        daily = grouped.agg([("mean_kw", "mean"), ("valid_readings", "count"), ("rows", "size")])
        # The source is sampled once per minute. Daily mean power in kW × 24 hours estimates kWh/day.
        daily["coverage"] = daily["valid_readings"] / 1440.0
        daily.loc[daily["coverage"] < min_coverage, "mean_kw"] = np.nan
        daily["consumption_kwh"] = daily["mean_kw"] * 24.0
        daily = daily.rename_axis("Date").reset_index()
        meta = {
            "source_type": "raw UCI minute-level power data",
            "source_rows": original_rows,
            "daily_rows_before_gap_handling": int(len(daily)),
            "missing_power_values": int(pd.to_numeric(x["global_active_power"], errors="coerce").isna().sum()),
            "coverage_threshold": min_coverage,
            "energy_method": "daily mean Global_active_power (kW) × 24 hours; only days with at least the selected minute-reading coverage are retained for interpolation",
        }
    else:
        # Prepared daily dataset, used for the included demo and user-created summaries.
        date_col = next((c for c in ["date", "datetime", "timestamp", "day", "month"] if c in columns), None)
        value_col = next((c for c in ["consumption_kwh", "daily_consumption_kwh", "daily_kwh", "energy_kwh", "consumption", "usage_kwh", "global_active_power", "sales"] if c in columns), None)
        if not date_col or not value_col:
            raise ValueError(
                "Could not identify the dataset columns. For the UCI raw file, use Date, Time, Global_active_power. "
                "For a prepared daily CSV, use Date and Consumption_kWh."
            )
        date_text = x[date_col].astype(str).str.strip()
        iso_like = date_text.str.match(r"^\d{4}-\d{2}-\d{2}").mean() > 0.8
        x["Date"] = pd.to_datetime(x[date_col], errors="coerce", dayfirst=not iso_like)
        x["consumption_kwh"] = pd.to_numeric(x[value_col], errors="coerce")
        x = x.dropna(subset=["Date"]).sort_values("Date")
        x["Date"] = x["Date"].dt.floor("D")
        daily = x.groupby("Date", as_index=False)["consumption_kwh"].mean()
        daily["coverage"] = 1.0
        daily["valid_readings"] = 1
        daily["rows"] = 1
        meta = {
            "source_type": "prepared daily time series",
            "source_rows": original_rows,
            "daily_rows_before_gap_handling": int(len(daily)),
            "missing_power_values": int(pd.to_numeric(x["consumption_kwh"], errors="coerce").isna().sum()),
            "coverage_threshold": min_coverage,
            "energy_method": f"daily values imported from '{value_col}' without unit conversion; ensure values are daily kWh",
        }

    daily["Date"] = pd.to_datetime(daily["Date"], errors="coerce")
    daily = daily.dropna(subset=["Date"]).sort_values("Date").drop_duplicates("Date", keep="last")
    daily = daily.set_index("Date").asfreq("D")
    before_missing = int(daily["consumption_kwh"].isna().sum())
    # Time interpolation fills short internal gaps. Edge gaps use nearest observed day.
    daily["consumption_kwh"] = daily["consumption_kwh"].interpolate(method="time", limit=3, limit_direction="both")
    daily["consumption_kwh"] = daily["consumption_kwh"].ffill().bfill()
    daily["coverage"] = daily["coverage"].fillna(0.0)
    daily["valid_readings"] = daily["valid_readings"].fillna(0).astype(int)
    daily["rows"] = daily["rows"].fillna(0).astype(int)
    if daily.empty or daily["consumption_kwh"].isna().all():
        raise ValueError("No usable daily consumption values were found.")
    if (daily["consumption_kwh"] < 0).any():
        raise ValueError("Consumption values include negatives. Check the source data and units.")
    daily = daily.reset_index().rename(columns={"consumption_kwh": "Consumption_kWh", "coverage": "Coverage", "valid_readings": "Valid_Readings", "rows": "Rows_Observed"})
    daily["Rolling_7D_kWh"] = daily["Consumption_kWh"].rolling(7, min_periods=1).mean()
    meta.update({
        "date_start": str(daily["Date"].min().date()),
        "date_end": str(daily["Date"].max().date()),
        "daily_days": int(len(daily)),
        "missing_days_filled_or_interpolated": before_missing,
        "mean_daily_kwh": float(daily["Consumption_kWh"].mean()),
        "median_daily_kwh": float(daily["Consumption_kWh"].median()),
        "max_daily_kwh": float(daily["Consumption_kWh"].max()),
        "min_daily_kwh": float(daily["Consumption_kWh"].min()),
    })
    return daily, meta
