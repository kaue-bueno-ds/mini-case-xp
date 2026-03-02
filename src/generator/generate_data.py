"""
Gerador de dados fictícios - Case: Cash & Liquidity Snapshot (Atacado/Tesouraria/FP&A)

Gera arquivos CSV em ./data/raw com duas "tabelas":
1) raw_cash_movements.csv  -> movimentos de caixa (entradas/saídas)
2) raw_fx_rates.csv        -> câmbio diário (USD->BRL) para conversão

Objetivo: simular dados que depois serão processados (Bronze/Silver/Gold) no Databricks.
"""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from random import Random
from typing import Iterable, List

import pandas as pd


# -------------------------
# Configuração do gerador
# -------------------------

DESKS = ["Treasury", "Funding", "FX", "Credit", "Equities"]
CURRENCIES = ["BRL", "USD"]

OUT_CATEGORIES = ["FundingCost", "Hedge", "Fees", "Payroll", "Infra", "Taxes"]
IN_CATEGORIES = ["ClientDeposit", "Settlement", "Interest", "FundingInflow"]


@dataclass(frozen=True)
class GeneratorConfig:
    start_date: date
    end_date: date
    n_users: int
    movements_per_day_min: int
    movements_per_day_max: int
    seed: int
    out_dir: str


def daterange(d1: date, d2: date) -> Iterable[date]:
    cur = d1
    while cur <= d2:
        yield cur
        cur = cur + timedelta(days=1)


def gen_fx_rates(cfg: GeneratorConfig, rng: Random) -> pd.DataFrame:
    """
    Gera USD->BRL por dia (simples, com leve ruído).
    """
    rows = []
    usd_brl = 5.00  # base fictícia
    for d in daterange(cfg.start_date, cfg.end_date):
        # pequeno random walk
        usd_brl = max(3.5, min(7.5, usd_brl + rng.uniform(-0.05, 0.05)))
        rows.append(
            {
                "rate_date": d.isoformat(),
                "from_ccy": "USD",
                "to_ccy": "BRL",
                "rate": round(usd_brl, 4),
                "source": "FAKE_PROVIDER",
                "ingested_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
            }
        )
    return pd.DataFrame(rows)


def gen_cash_movements(cfg: GeneratorConfig, rng: Random) -> pd.DataFrame:
    """
    Gera movimentos de caixa (IN/OUT), com desk, moeda e categoria.
    """
    rows: List[dict] = []
    movement_id = 1

    for d in daterange(cfg.start_date, cfg.end_date):
        n = rng.randint(cfg.movements_per_day_min, cfg.movements_per_day_max)

        for _ in range(n):
            desk = rng.choice(DESKS)
            ccy = rng.choice(CURRENCIES)

            # mix: mais OUT em alguns desks, mais IN em outros
            bias = 0.55 if desk in ("Funding", "Treasury") else 0.45
            movement_type = "OUT" if rng.random() < bias else "IN"

            if movement_type == "OUT":
                category = rng.choice(OUT_CATEGORIES)
                amount = rng.uniform(5_000, 500_000)
            else:
                category = rng.choice(IN_CATEGORIES)
                amount = rng.uniform(10_000, 800_000)

            # FX desk tende a ter valores menores/médios e mais USD
            if desk == "FX":
                amount *= rng.uniform(0.3, 0.8)
                if rng.random() < 0.65:
                    ccy = "USD"

            # timestamps ao longo do dia
            hh = rng.randint(8, 19)
            mm = rng.randint(0, 59)
            ss = rng.randint(0, 59)
            ts = datetime(d.year, d.month, d.day, hh, mm, ss)

            rows.append(
                {
                    "movement_id": movement_id,
                    "movement_ts": ts.isoformat(sep=" "),
                    "movement_date": d.isoformat(),
                    "desk": desk,
                    "currency": ccy,
                    "movement_type": movement_type,  # IN / OUT
                    "category": category,
                    "amount": round(amount, 2),
                    "reference": f"REF-{movement_id:08d}",
                    "ingested_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
                }
            )
            movement_id += 1

    return pd.DataFrame(rows)


def ensure_out_dir(out_dir: str) -> None:
    os.makedirs(out_dir, exist_ok=True)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--start-date", type=str, default="2026-01-01")
    p.add_argument("--end-date", type=str, default="2026-02-28")
    p.add_argument("--movements-min", type=int, default=40)
    p.add_argument("--movements-max", type=int, default=80)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--out-dir", type=str, default="data/raw")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    cfg = GeneratorConfig(
        start_date=date.fromisoformat(args.start_date),
        end_date=date.fromisoformat(args.end_date),
        n_users=0,  # reservado p/ futuras extensões
        movements_per_day_min=args.movements_min,
        movements_per_day_max=args.movements_max,
        seed=args.seed,
        out_dir=args.out_dir,
    )

    rng = Random(cfg.seed)
    ensure_out_dir(cfg.out_dir)

    df_fx = gen_fx_rates(cfg, rng)
    df_mov = gen_cash_movements(cfg, rng)

    fx_path = os.path.join(cfg.out_dir, "raw_fx_rates.csv")
    mov_path = os.path.join(cfg.out_dir, "raw_cash_movements.csv")

    df_fx.to_csv(fx_path, index=False)
    df_mov.to_csv(mov_path, index=False)

    print("✅ Arquivos gerados:")
    print(f"- {fx_path}  (rows={len(df_fx)})")
    print(f"- {mov_path} (rows={len(df_mov)})")


if __name__ == "__main__":
    main()