from __future__ import annotations

import os
from datetime import datetime, timezone

import pandas as pd


SILVER_DIR = "data/processed/silver"
GOLD_DIR = "data/processed/gold"


def utc_now_z() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def ensure_dirs() -> None:
    os.makedirs(GOLD_DIR, exist_ok=True)


def build_gold_liquidity_daily() -> str:
    src = os.path.join(SILVER_DIR, "silver_cash_movements_enriched.csv")
    df = pd.read_csv(src)

    # Tipagem mínima
    df["movement_date"] = pd.to_datetime(df["movement_date"]).dt.date
    df["amount_brl"] = df["amount_brl"].astype(float)

    # inflow/outflow
    df["inflow_brl"] = df.apply(lambda r: r["amount_brl"] if r["movement_type"] == "IN" else 0.0, axis=1)
    df["outflow_brl"] = df.apply(lambda r: r["amount_brl"] if r["movement_type"] == "OUT" else 0.0, axis=1)

    agg = (
        df.groupby(["movement_date", "desk"], as_index=False)
        .agg(
            inflow_brl=("inflow_brl", "sum"),
            outflow_brl=("outflow_brl", "sum"),
            movements_count=("movement_id", "count"),
        )
    )

    agg["net_flow_brl"] = agg["inflow_brl"] - agg["outflow_brl"]
    agg["last_refresh_utc"] = utc_now_z()

    # Contrato final (ordem de colunas)
    agg = agg[["movement_date", "desk", "inflow_brl", "outflow_brl", "net_flow_brl", "movements_count", "last_refresh_utc"]]
    agg = agg.sort_values(["movement_date", "desk"])

    out_path = os.path.join(GOLD_DIR, "gold_liquidity_daily.csv")
    agg.to_csv(out_path, index=False)
    return out_path


def main() -> None:
    ensure_dirs()
    out = build_gold_liquidity_daily()
    print("✅ Gold gerada:")
    print(f"- {out}")


if __name__ == "__main__":
    main()