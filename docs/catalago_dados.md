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

---
# (Planejado) Camada Bronze (Delta)

## bronze_cash_movements (Delta)

**Origem:** `raw_cash_movements.csv`  
**Descrição:** Movimentos de caixa brutos, carregados para o lake.  
**Granularidade:** 1 linha por movimento (pode conter duplicatas no raw)  
**Chave sugerida:** `movement_id` (pode repetir no bronze)

| Coluna         | Tipo        | Descrição |
|---------------|-------------|----------|
| movement_id   | long/int    | Identificador do movimento |
| movement_ts   | timestamp   | Data/hora do movimento |
| movement_date | date        | Data do movimento |
| desk          | string      | Mesa/área |
| currency      | string      | Moeda (`BRL`/`USD`) |
| movement_type | string      | `IN` / `OUT` |
| category      | string      | Categoria |
| amount        | double      | Valor do movimento na moeda (`currency`) |
| reference     | string      | Referência do movimento |
| ingested_at   | timestamp/string | Timestamp do raw |

---

## bronze_fx_rates (Delta)

**Origem:** `raw_fx_rates.csv`  
**Descrição:** Taxa de câmbio diária (USD->BRL) bruta no lake.  
**Granularidade:** 1 linha por dia  
**Chave sugerida:** (`rate_date`, `from_ccy`, `to_ccy`)

| Coluna       | Tipo        | Descrição |
|-------------|-------------|----------|
| rate_date   | date        | Data da taxa |
| from_ccy    | string      | Moeda origem (`USD`) |
| to_ccy      | string      | Moeda destino (`BRL`) |
| rate        | double      | Taxa USD->BRL |
| source      | string      | Fonte |
| ingested_at | timestamp/string | Timestamp do raw |

---

# (Planejado) Camada Silver (Delta)

## silver_cash_movements_enriched (Delta)

**Origem:** `bronze_cash_movements` + `bronze_fx_rates`  
**Descrição:** Movimentos tratados e enriquecidos com FX, com valor normalizado em BRL sem perder o original.  
**Granularidade:** 1 linha por movimento (`movement_id` único)  
**Partição sugerida:** `movement_date`  
**Chave:** `movement_id`

| Coluna          | Tipo      | Descrição |
|----------------|-----------|----------|
| movement_id    | long      | Identificador único do movimento |
| movement_ts    | timestamp | Data/hora do movimento |
| movement_date  | date      | Data do movimento |
| desk           | string    | Mesa/área |
| currency       | string    | Moeda original (`BRL`/`USD`) |
| movement_type  | string    | `IN` / `OUT` |
| category       | string    | Categoria |
| amount_original| double    | Valor original (mesmo do bronze `amount`) |
| fx_rate_to_brl | double    | 1.0 se BRL, senão taxa USD->BRL do dia |
| amount_brl     | double    | `amount_original * fx_rate_to_brl` |
| reference      | string    | Referência |
| ingested_at    | timestamp/string | Timestamp do raw |
| processed_at   | timestamp | Timestamp de processamento da Silver |

**Regras (MVP):**
- Deduplicar por `movement_id` (mantendo o registro mais recente por `ingested_at`, quando aplicável).
- Left join com FX por (`movement_date` = `rate_date`) para movimentos em USD.
- Se `currency='BRL'`, `fx_rate_to_brl=1.0`.
---
# (Planejado) Camada Gold (SSOT para BI)

## gold_liquidity_daily (Delta)

**Descrição:** Tabela final pronta para dashboard (SSOT).
**Saída local**: `data/processed/gold/gold_liquidity_daily.csv`
**Origem:** `raw_cash_movements` + `raw_fx_rates` (depois via Bronze/Silver)  
**Granularidade:** 1 linha por dia, por desk (valores em BRL)  
**Chave:** (`date`, `desk`)

| Coluna              | Tipo   | Descrição |
|---------------------|--------|----------|
| date                | date   | Dia de referência (YYYY-MM-DD) |
| desk                | string | Mesa/área (Treasury, Funding, FX, ...) |
| inflow_brl          | double | Soma das entradas do dia convertidas para BRL |
| outflow_brl         | double | Soma das saídas do dia convertidas para BRL |
| net_flow_brl        | double | `inflow_brl - outflow_brl` |
| movements_count     | long   | Quantidade de movimentos no dia (IN+OUT) |
| last_refresh_utc    | timestamp/string | Data/hora da última atualização da Gold |

**Regras de negócio (MVP):**
- Movimentos em BRL entram direto.
- Movimentos em USD são convertidos usando `raw_fx_rates` do mesmo `movement_date` (USD->BRL).
- `inflow_brl` considera apenas `movement_type = 'IN'`.
- `outflow_brl` considera apenas `movement_type = 'OUT'`.