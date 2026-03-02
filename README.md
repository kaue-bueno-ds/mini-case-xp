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
- [ ] Camadas Bronze/Silver/Gold no Databricks (Delta)
- [ ] Conexão Power BI consumindo a camada Gold