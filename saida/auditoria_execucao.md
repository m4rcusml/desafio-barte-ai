# 📋 Manifesto de Auditoria da Execução — Fechamento Financeiro Tarvo
**Competência:** 2026-09  
**Data e Hora:** 2026-10-17T14:52:58.326968-03:00  
**Status do Fechamento:** `PROVISORIO`  
**Auditoria Matemática de Rastro:** `✅ 100% CONCILIADO`  

---
## 1. Inventário de Arquivos de Entrada
| Arquivo | Domínio Identificado | Linhas | Tamanho (Bytes) | Método de Triagem |
| :--- | :--- | :---: | :---: | :--- |
| `01_orbe_relatorio_comissoes_set2026.csv` | ORBE_FECHAMENTO_PRINCIPAL | 1944 | 221,518 | HEURISTICA |
| `02_tabela_taxas_contratadas.xlsx` | TABELA_TAXAS_CONTRATUAIS | 66 | 10,092 | HEURISTICA |
| `03_email_ponte_cambio_relatorio_set2026.eml` | EMAIL_PONTE_CAMBIO | 569 | 42,076 | HEURISTICA |
| `04_plano_de_contas_fenix_erp.csv` | PLANO_CONTAS_FENIX | 53 | 3,205 | HEURISTICA |
| `05a_extrato_banco_aurora_cc4471_set2026.csv` | EXTRATO_AURORA | 95 | 6,896 | HEURISTICA |
| `05b_extrato_banco_meridiano_cc90233_set2026.ofx` | EXTRATO_MERIDIANO | 848 | 18,306 | HEURISTICA |
| `06_orbe_ajustes_tardios_set2026.csv` | ORBE_AJUSTES_TARDIOS | 15 | 2,088 | HEURISTICA |

---
## 2. Métricas Consolidadas das Saídas
- **Comissões por Lojista:** 35 registros (Total: R$ 243278.76)
- **Notas Fiscais a Emitir:** 21 registros (Total: R$ 243284.26)
- **Divergências de Taxa:** 115 operações contestadas (Total: R$ 3016.37)
- **Lançamentos Contábeis:** 184 conciliações bancárias
- **Pendências Operacionais:** 187 itens para decisão
- **Rastro Universal:** 4134 vínculos 1-para-1 auditáveis

---
## 3. Validação da Prova Real do Rastro
Todos os 171 identificadores de saída (`COM-XXXX`, `NF-XXXX` e `DIV-XXXX`) foram verificados.
A soma das transações vinculadas no `rastro.csv` é identicamente igual ao valor total reportado em cada relatório oficial.

---
## 4. Regras e Decisões Aplicadas nesta Execução
- Checkout: Comissões apuradas pela taxa contratada por modalidade/parcelamento.
- Checkout: Bridge Idiomas (1075624862) split temporal de taxa em 15/09/2026.
- Checkout: Atlas Idiomas (1076801732) bloqueio total por ausência de contrato assinado (Bia/Comercial).
- Checkout: Casa do Estudante (1018325654) isenção set-dez com estornos anteriores respeitados à taxa original.
- Checkout: Ajustes tardios (06) consolidados em setembro como lote complementar.
- Checkout: 7 divergências de bandeira no lote 06 vinculadas e reportadas em pendências para correção Orbe.
- Checkout: Estornos órfãos sem referência no relatório principal aceitos pelo valor declarado com pendência para Helena.
- Remessas: Split de 50% sobre o Spread BRL realizado (Ponte Câmbio).
- Remessas: Exclusão de 4 operações com spread negativo para contestação integral com a Ponte.
- Remessas: Deduplicação de PC-0926-0162 e contestação de spread contratual Mundo Aberto (1.20% vs 1.50%).
- Contábil: Classificação contábil com dupla conciliação bancária (Aurora CC 44710 e Meridiano CC 902335).
