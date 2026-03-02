from __future__ import annotations

import os
from datetime import datetime, timezone

import pandas as pd


RAW_DIR = "data/raw"
BRONZE_DIR = "data/bronze"


def utc_now_z() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def ensure_dirs() -> None:
    os.makedirs(BRONZE_DIR, exist_ok=True)


def build_bronze_fx_rates() -> str:
    src = os.path.join(RAW_DIR, "raw_fx_rates.csv")
    dst = os.path.join(BRONZE_DIR, "bronze_fx_rates.csv")

    df = pd.read_csv(src)

    
    df["rate_date"] = pd.to_datetime(df["rate_date"]).dt.date
    df["rate"] = df["rate"].astype(float)

    
    df["bronze_loaded_at"] = utc_now_z()

    df.to_csv(dst, index=False)
    return dst


def build_bronze_cash_movements() -> str:
    src = os.path.join(RAW_DIR, "raw_cash_movements.csv")
    dst = os.path.join(BRONZE_DIR, "bronze_cash_movements.csv")

    df = pd.read_csv(src)

    # Tipagem mínima
    df["movement_id"] = df["movement_id"].astype(int)
    df["movement_ts"] = pd.to_datetime(df["movement_ts"])
    df["movement_date"] = pd.to_datetime(df["movement_date"]).dt.date
    df["amount"] = df["amount"].astype(float)

    df["bronze_loaded_at"] = utc_now_z()

    df.to_csv(dst, index=False)
    return dst


def main() -> None:
    ensure_dirs()

    fx_path = build_bronze_fx_rates()
    mov_path = build_bronze_cash_movements()

    print("✅ Bronze local gerada:")
    print(f"- {fx_path}")
    print(f"- {mov_path}")


if __name__ == "__main__":
    main()