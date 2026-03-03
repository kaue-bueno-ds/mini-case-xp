# Mini Case XP — Cash & Liquidity Snapshot (Atacado / Tesouraria / FP&A)

## Objetivo
Construir um mini pipeline estilo lakehouse para atender uma demanda típica do banco de atacado:
entregar tabelas prontas no lake para consumo em dashboards (Power BI), com KPIs de liquidez e caixa.

## Pedido do negócio (enunciado)
O time de Tesouraria/FP&A precisa acompanhar diariamente:
- saldo de caixa por desk (Treasury, Funding, FX, ...)
- entradas e saídas (cash-in/cash-out) e fluxo líquido
- conversão para BRL quando houver movimentos em USD
- visão pronta para dashboard (sem necessidade de tratamentos manuais)

A área pediu uma tabela final (SSOT) no lake com granularidade diária por desk, já com métricas calculadas.

## Status (MVP)
- [x] Gerador local de dados fictícios (CSV)
- [x] Catálogo de dados (raw)
- [x] Glossário
- [x] Camadas Bronze/Silver/Gold no Databricks (Delta)
- [x] Conexão Power BI consumindo a camada Gold

## Como rodar (local)

> Pré-requisito: Python 3.12+ (ou 3.10+) e ambiente virtual criado.

1) Ative o venv e instale dependências
```bash
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2) Gere os dados RAW
```bash
python src/generator/generate_data.py
```

3) Construa as camadas locais (Bronze -> Silver -> Gold)
```bash
python src/local_pipeline/01_build_bronze.py
python src/local_pipeline/02_build_silver.py
python src/local_pipeline/03_build_gold.py
```
