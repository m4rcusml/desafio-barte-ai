# 📋 Manifesto de Auditoria da Execução — Fechamento Financeiro Tarvo
**ID da Execução:** `EXEC-2026-09-2fa31a-91fee9b8`  
**Versão de Regras:** `2.1.0-padrao-ouro`  
**Competência:** `2026-09` (09/2026)  
**Data e Hora:** 2026-10-17T17:14:01.910167-03:00  
**Estado Técnico:** `CONCLUIDO`  
**Status de Aprovação Humana:** `PROVISORIO`  
**Auditoria Matemática de Rastro:** `✅ 100% CONCILIADO`  

---
## 1. Cobertura e Estado das Fontes por Frente
| Domínio | Frente | Estado | Arquivo | Motivo / Detalhe | Dependência | Responsável |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `ORBE_FECHAMENTO_PRINCIPAL` | CHECKOUT | `PROCESSADA` | `01_orbe_relatorio_comissoes_set2026.csv` | Fonte validada e processada com 1943 registros. | TABELA_TAXAS_CONTRATUAIS | Caio / Operações Checkout |
| `ORBE_AJUSTES_TARDIOS` | CHECKOUT | `PROCESSADA` | `06_orbe_ajustes_tardios_set2026.csv` | Fonte validada e processada com 14 registros. | ORBE_FECHAMENTO_PRINCIPAL, TABELA_TAXAS_CONTRATUAIS | Helena / Conciliação |
| `TABELA_TAXAS_CONTRATUAIS` | CHECKOUT, REMESSA | `PROCESSADA` | `02_tabela_taxas_contratadas.xlsx` | Fonte validada e processada com 25 registros. | Nenhuma (Fonte Mestre de Contratos) | Bia / Comercial |
| `EMAIL_PONTE_CAMBIO` | REMESSA | `PROCESSADA` | `03_email_ponte_cambio_relatorio_set2026.eml` | Fonte validada e processada com 233 registros. | TABELA_TAXAS_CONTRATUAIS | Caio / Câmbio |
| `PLANO_CONTAS_FENIX` | CONTABIL | `PROCESSADA` | `04_plano_de_contas_fenix_erp.csv` | Fonte validada e processada com 52 registros. | Nenhuma (Plano de Contas ERP) | Helena / Contabilidade |
| `EXTRATO_AURORA` | CONTABIL | `PROCESSADA` | `05a_extrato_banco_aurora_cc4471_set2026.csv` | Fonte validada e processada com 84 registros. | EXTRATO_MERIDIANO (Conferência de Trânsito) | Caio / Conciliação Bancária |
| `EXTRATO_MERIDIANO` | CONTABIL | `PROCESSADA` | `05b_extrato_banco_meridiano_cc90233_set2026.ofx` | Fonte validada e processada com 100 registros. | EXTRATO_AURORA (Conferência de Trânsito) | Caio / Conciliação Bancária |

---
## 2. Inventário de Arquivos de Entrada (SHA-256)
| Arquivo | Domínio Identificado | Linhas | Tamanho (Bytes) | SHA-256 (Prefixo) | Método de Triagem |
| :--- | :--- | :---: | :---: | :--- | :--- |
| `01_orbe_relatorio_comissoes_set2026.csv` | ORBE_FECHAMENTO_PRINCIPAL | 1944 | 221,518 | `fdbc2bad2dd3` | HEURISTICA |
| `02_tabela_taxas_contratadas.xlsx` | TABELA_TAXAS_CONTRATUAIS | 66 | 10,092 | `d0c7d2b13ac4` | HEURISTICA |
| `03_email_ponte_cambio_relatorio_set2026.eml` | EMAIL_PONTE_CAMBIO | 569 | 42,076 | `e36808cab907` | HEURISTICA |
| `04_plano_de_contas_fenix_erp.csv` | PLANO_CONTAS_FENIX | 53 | 3,205 | `fb99c63b151c` | HEURISTICA |
| `05a_extrato_banco_aurora_cc4471_set2026.csv` | EXTRATO_AURORA | 95 | 6,896 | `7303b72fa76d` | HEURISTICA |
| `05b_extrato_banco_meridiano_cc90233_set2026.ofx` | EXTRATO_MERIDIANO | 848 | 18,306 | `27f11fae20c1` | HEURISTICA |
| `06_orbe_ajustes_tardios_set2026.csv` | ORBE_AJUSTES_TARDIOS | 15 | 2,088 | `b1cfd183945f` | HEURISTICA |

---
## 3. Métricas Consolidadas e Hashes das Saídas
- **Comissões por Lojista:** 35 registros (Total: R$ 243278.76)
- **Notas Fiscais a Emitir:** 21 registros (Total: R$ 243284.26)
- **Divergências de Taxa:** 115 operações contestadas (Total: R$ 2995.11)
- **Lançamentos Contábeis:** 184 conciliações bancárias
- **Pendências Operacionais:** 68 itens para decisão
- **Rastro Universal:** 4503 vínculos auditáveis
- **Hash Combinado de Entradas:** `2fa31a1ba3a1eb9d65a9972eeac5fad4b9e795fbd1f5e90392271d5fab65d652`
- **Hash Combinado de Saídas:** `91fee9b800c40b852d255bbfa013836c9e1c7ea393ef188ec91e1ceef1f1340c`

---
## 4. Comparação com Execução Anterior e Governança de Aprovação
- **Execução Anterior Encontrada:** `True`
- **Entradas Idênticas:** `True`
- **Saídas Idênticas:** `True`
- **Herança de Aprovação Bloqueada por Alteração:** `False`
- **Arquivos de Saída Alterados:** `Nenhum`

---
## 5. Validação da Prova Real do Rastro
Todos os 423 identificadores de saída (`COM-XXXX`, `NF-XXXX`, `DIV-XXXX`, `LAN-XXXX` e `PEN-XXXX`) foram verificados.
A soma das transações vinculadas no `rastro.csv` é identicamente igual ao valor total reportado em cada relatório oficial.

---
## 6. Regras e Decisões Aplicadas nesta Execução
- Checkout: Comissões apuradas pela taxa contratada por modalidade/parcelamento e filtradas por competência.
- Checkout: Bridge Idiomas (1075624862) split temporal de taxa em 15/09/2026 respeitando data da venda original em estornos.
- Checkout: Atlas Idiomas (1076801732) bloqueio total por ausência de contrato assinado (Bia/Comercial).
- Checkout: Casa do Estudante (1018325654) isenção set-dez consolidada em pendência com 118 transações reais no rastro.
- Checkout/Remessas: Deduplicação estrita de cópias idênticas e bloqueio integral de todas as versões em IDs conflitantes.
- Checkout: 7 divergências de bandeira no lote 06 vinculadas por referência sem abrir pendência indevida (homologado por Helena).
- Checkout: Estornos órfãos sem referência no relatório principal aceitos pelo valor declarado com pendência para Helena.
- Remessas: Split de 50% sobre o Spread BRL realizado (Ponte Câmbio).
- Remessas: Exclusão de 4 operações com spread negativo para contestação integral com a Ponte.
- Remessas: Deduplicação de PC-0926-0162 e contestação de spread contratual Mundo Aberto (1.20% vs 1.50%).
- Contábil: Classificação contábil com dupla conciliação bancária (Aurora CC 44710 e Meridiano CC 902335).
