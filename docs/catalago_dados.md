# Catálogo de Dados

Este documento descreve as tabelas/datasets do projeto, com colunas, tipos e significado.

> Convenção de nomes:
> - `raw_*` = dados gerados localmente (pré-lake)
> - (futuro) `bronze_*`, `silver_*`, `gold_*` = camadas no lake (Delta)

---

## raw_fx_rates (CSV)

**Arquivo:** `data/raw/raw_fx_rates.csv`  
**Granularidade:** 1 linha por dia (USD -> BRL)  
**Chave sugerida:** (`rate_date`, `from_ccy`, `to_ccy`)

| Coluna        | Tipo   | Descrição |
|--------------|--------|----------|
| rate_date    | string (YYYY-MM-DD) | Data de referência da taxa |
| from_ccy     | string | Moeda origem (sempre `USD`) |
| to_ccy       | string | Moeda destino (sempre `BRL`) |
| rate         | float  | Taxa USD->BRL do dia |
| source       | string | Fonte do dado (fictícia) |
| ingested_at  | string (ISO-8601 UTC) | Timestamp de geração/ingestão |

---

## raw_cash_movements (CSV)

**Arquivo:** `data/raw/raw_cash_movements.csv`  
**Granularidade:** 1 linha por movimento de caixa (entrada/saída)  
**Chave sugerida:** `movement_id`

| Coluna         | Tipo   | Descrição |
|---------------|--------|----------|
| movement_id   | int    | Identificador único do movimento |
| movement_ts   | string (YYYY-MM-DD HH:MM:SS) | Timestamp do movimento |
| movement_date | string (YYYY-MM-DD) | Data do movimento |
| desk          | string | “Mesa”/área (ex.: Treasury, Funding, FX, ...) |
| currency      | string | Moeda do movimento (`BRL`/`USD`) |
| movement_type | string | Tipo do movimento (`IN` entrada / `OUT` saída) |
| category      | string | Categoria do movimento (ex.: Fees, Hedge, ClientDeposit...) |
| amount        | float  | Valor do movimento na moeda (`currency`) |
| reference     | string | Referência fictícia do movimento |
| ingested_at   | string (ISO-8601 UTC) | Timestamp de geração/ingestão |