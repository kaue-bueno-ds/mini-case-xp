# Glossário

Termos e conceitos usados no projeto.

---

## Atacado (Wholesale)
Área que atende empresas (PJ) e operações mais complexas (ex.: tesouraria, funding, câmbio), geralmente com necessidades de reporting e análise próximas de FP&A e estratégia.

## Tesouraria (Treasury)
Função responsável por gestão de caixa, liquidez, funding, risco e alocação de recursos no curto prazo.

## Liquidez (Liquidity)
Capacidade de honrar obrigações no tempo certo. Aqui, medimos via saldos de caixa e fluxo líquido (entradas - saídas).

## Desk
No contexto do case, é uma “mesa”/sub-área (ex.: Treasury, Funding, FX) usada para segmentar o caixa e os movimentos.

## Movimento de caixa (Cash movement)
Evento de entrada (`IN`) ou saída (`OUT`) de dinheiro, com valor (`amount`), categoria e moeda.

## FX / Taxa de câmbio (FX rate)
Taxa usada para converter valores entre moedas. No case, usamos USD->BRL por dia.

## Camadas Bronze / Silver / Gold
Padrão de lakehouse:
- **Bronze:** dado bruto (raw), histórico e rastreável
- **Silver:** dado tratado (tipagem, limpeza, regras)
- **Gold:** dado pronto para consumo (BI), agregações e métricas

## Granularidade
Nível de detalhe de uma tabela (ex.: “1 linha por movimento” vs “1 linha por dia por desk”).

## SSOT (Single Source of Truth)
“Fonte única da verdade”: tabela/dataset padronizado e confiável que todos usam para evitar números divergentes.