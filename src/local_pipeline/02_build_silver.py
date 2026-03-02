from __future__ import annotations

import os
from datetime import datetime, timezone

import pandas as pd


BRONZE_DIR = "data/bronze"
SILVER_DIR = "data/processed/silver"


def utc_now_z() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def ensure_dirs() -> None:
    os.makedirs(SILVER_DIR, exist_ok=True)


def build_silver_cash_movements_enriched() -> str:
    mov_path = os.path.join(BRONZE_DIR, "bronze_cash_movements.csv")
    fx_path = os.path.join(BRONZE_DIR, "bronze_fx_rates.csv")

    mov = pd.read_csv(mov_path)
    fx = pd.read_csv(fx_path)

    # Tipagem
    mov["movement_id"] = mov["movement_id"].astype(int)
    mov["movement_ts"] = pd.to_datetime(mov["movement_ts"])
    mov["movement_date"] = pd.to_datetime(mov["movement_date"]).dt.date
    mov["amount"] = mov["amount"].astype(float)

    fx["rate_date"] = pd.to_datetime(fx["rate_date"]).dt.date
    fx["rate"] = fx["rate"].astype(float)

    # -------------------------
    # Dedup (MVP)
    # Se houver duplicatas por movement_id, mantemos a última pelo 'ingested_at' (se existir),
    # senão mantemos a última ocorrência no arquivo.
    # -------------------------
    if "ingested_at" in mov.columns:
        # parse ingested_at se possível
        mov["_ingested_at_parsed"] = pd.to_datetime(mov["ingested_at"], errors="coerce")
        mov = mov.sort_values(["movement_id", "_ingested_at_parsed"]).drop_duplicates(
            subset=["movement_id"], keep="last"
        )
        mov = mov.drop(columns=["_ingested_at_parsed"])
    else:
        mov = mov.drop_duplicates(subset=["movement_id"], keep="last")

    # -------------------------
    # Enriquecimento com FX
    # - left join por movement_date = rate_date
    # - só faz sentido para USD->BRL, mas no MVP vamos trazer a taxa do dia e aplicar condicionalmente
    # -------------------------
    fx_day = fx.loc[(fx["from_ccy"] == "USD") & (fx["to_ccy"] == "BRL"), ["rate_date", "rate"]].rename(
        columns={"rate_date": "movement_date", "rate": "usd_brl_rate"}
    )

    enriched = mov.merge(fx_day, on="movement_date", how="left")

    # amount_original (preserva o bruto)
    enriched["amount_original"] = enriched["amount"]

    # fx_rate_to_brl: 1.0 se BRL, senão usd_brl_rate
    enriched["fx_rate_to_brl"] = enriched.apply(
        lambda r: 1.0 if r["currency"] == "BRL" else r["usd_brl_rate"],
        axis=1,
    )

    # amount_brl
    enriched["amount_brl"] = enriched["amount_original"] * enriched["fx_rate_to_brl"]

    # Auditoria
    enriched["processed_at"] = utc_now_z()

    # Seleção e ordenação final (para ficar "contrato" da silver)
    cols = [
        "movement_id",
        "movement_ts",
        "movement_date",
        "desk",
        "currency",
        "movement_type",
        "category",
        "amount_original",
        "fx_rate_to_brl",
        "amount_brl",
        "reference",
        "ingested_at",
        "bronze_loaded_at",
        "processed_at",
    ]
    # só mantém colunas que existirem
    cols = [c for c in cols if c in enriched.columns]
    enriched = enriched[cols].sort_values(["movement_date", "desk", "movement_id"])

    out_path = os.path.join(SILVER_DIR, "silver_cash_movements_enriched.csv")
    enriched.to_csv(out_path, index=False)
    return out_path


def main() -> None:
    ensure_dirs()
    out = build_silver_cash_movements_enriched()
    print("✅ Silver gerada:")
    print(f"- {out}")


if __name__ == "__main__":
    main()