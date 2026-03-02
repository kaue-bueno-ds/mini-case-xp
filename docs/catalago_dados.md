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

# (Planejado) Camada Gold (SSOT para BI)

## gold_liquidity_daily (Delta)

**Descrição:** Tabela final pronta para dashboard (SSOT).  
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