# 📖 Documento de Leitura e Dossiê Executivo — Agente Autônomo de Fechamento Financeiro Tarvo

**Competência:** Setembro/2026  
**Empresa:** Tarvo Pagamentos Ltda.  
**Solução:** Pipeline Autônomo de Fechamento, Conciliação e Auditoria Financeira  
**Arquitetura:** LangGraph + TypeSafe Jev + Google Gemini Flash + DeepSeek V1 Flash + Motores Determinísticos Python  
**Formato de Entrega:** Executável Autônomo (`fechamento_tarvo.exe`) e Código-Fonte Estruturado  

---

## 1. Sumário Executivo

O processo de fechamento mensal da **Tarvo Pagamentos** envolvia reconciliação manual de dados fragmentados entre adquirente de cartões (**Orbe**), parceiro de câmbio (**Ponte Corretora**), extratos bancários (**Aurora** e **Meridiano**) e ERP contábil (**Fênix**). Essa rotina consumia cerca de 8 dias de esforço operacional da equipe de finanças (Bia, Caio e Helena), gerando passivos como cobranças indevidas de clientes, contestação tardia de spreads negativos e divergências contratuais não detectadas.

Para resolver essa dor estrutural, construímos um **Agente Autônomo de Fechamento Financeiro** projetado com rigor matemático, tolerância a falhas e padrão institucional de governança. A solução roda de ponta a ponta em **menos de 0,1 segundo**, garantindo **100% de prova real matemática** e gerando simultaneamente todos os relatórios regulatórios e manifestos de auditoria exigidos pela **Tarvo** e pela **Barte**.

---

## 2. Arquitetura da Solução e Fluxo Operacional

```mermaid
flowchart TD
    subgraph INGESTAO ["1. Ingestão e Triagem Multi-Tier"]
        RAW[("Tarvo_Data_Pack_set2026/")]
        T1["Tier 1: TypeSafe Jev (Contratos & Esquema)"]
        T2["Tier 2: Google Gemini Flash (Semântica)"]
        T3["Tier 3: DeepSeek V1 Flash (Fallback LLM)"]
        T4["Tier 4: Heurística Local (0ms, 100% Offline)"]
        RAW --> T1 -->|Fallback| T2 -->|Fallback| T3 -->|Fallback| T4
    end

    subgraph SILVER ["2. Camada Silver (Normalização Canônica)"]
        FMT["Formatadores Especializados<br/>(01 Orbe, 02 Taxas, 03 Ponte, 04 Fênix, 05 Aurora/Meridiano, 06 Tardios)"]
        GUARD1["Guardrail 1: Validador de Sanidade & Colisão de IDs"]
        T4 --> FMT --> GUARD1
    end

    subgraph GOLD ["3. Motores de Domínio (Camada Gold)"]
        CHK["Motor de Checkout<br/>(Vigências, 7 Bandeiras, Estornos Órfãos, Isenção, Bloqueio Atlas)"]
        CAM["Motor de Câmbio & Remessas<br/>(Split 50%, Exclusão de Negativos, Nota Única Ponte)"]
        ACC["Motor Contábil & Bancário<br/>(Partidas Dobradas, Baixa de Provisões, Dupla Conciliação)"]
        GUARD2["Guardrail 2: Auditoria de Divergências Reais (>= 0.005)"]
        GUARD1 --> CHK & CAM & ACC
        CHK & CAM --> GUARD2
    end

    subgraph SAIDA ["4. Emissor Atômico & Padrão Ouro de Auditabilidade"]
        PROVA["Prova Real Matemática<br/>(Soma do Rastro == Valor Reportado para COM, NF e DIV)"]
        OUT_LOCAL[("fechamento-completo/<br/>(Ao lado do .exe)")]
        OUT_OFICIAL[("saida/<br/>(Oficial Barte)")]
        MANIFESTOS["Manifestos de Auditoria<br/>(auditoria_execucao.json & auditoria_execucao.md)"]
        GUARD2 & ACC --> PROVA
        PROVA --> OUT_LOCAL & OUT_OFICIAL
        PROVA --> MANIFESTOS
    end
```

---

## 3. Detalhamento dos Componentes Técnicos

### 3.1. Roteador de Ingestão Multi-Tier com Fallback Quádruplo
O pipeline foi projetado para **nunca interromper a execução**, combinando inteligência artificial semântica e determinismo local:
1. **Tier 1 — TypeSafe Jev:** Modelo System One tipado para checagem estrita de schema tabular em sub-500ms.
2. **Tier 2 — Google Gemini Flash (`gemini-2.5-flash`):** Raciocínio contextual para interpretar layouts desconhecidos, mensagens de e-mail e variações atípicas.
3. **Tier 3 — DeepSeek V1 Flash (`deepseek-v1-flash`):** Fallback semântico de altíssima eficiência e custo reduzido, garantindo redundância de LLMs de primeira linha via chamadas REST nativas.
4. **Tier 4 — Heurística Local Determinística:** Algoritmo offline de altíssima velocidade (0.1ms), insensível a quedas de rede ou falta de credenciais externas.

### 3.2. Camada Silver (Normalização e Padronização)
- Conversão estrita de datas para o padrão ISO (`AAAA-MM-DD`).
- Padronização decimal com ponto (`.`), eliminando separadores de milhar.
- Decodificação e mapeamento de categorias por legendas numéricas otimizadas.
- Preservação da integridade documental original (zero substituições artificiais de dados de clientes).

### 3.3. Guardrail 1: Detector de Sanidade e Colisão de IDs
- Checagem de integridade referencial: valida se todo estorno e reversão referencia uma transação válida.
- Detecção de colisões entre lotes: no caso do arquivo `06` (Ajustes Tardios), verifica sobreposições de `id_transacao` e aplica a precedência definida no `HIPOTESES.md`.

---

## 4. Regras de Negócio e Decisões Homologadas

### 4.1. Checkout & Divergências de Taxa
- **Base de Cálculo da Comissão:** Faturamento apurado sobre `valor_bruto * taxa_contratada_pct`, linha a linha, com arredondamento `ROUND_HALF_UP` centavo a centavo. O campo `valor_taxa` da adquirente é utilizado unicamente para apuração de divergências.
- **Corte Temporal Bridge Idiomas (`1075624862`):**
  - Vendas até `14/09/2026`: aplicada a taxa original de **2,59%**.
  - Vendas a partir de `15/09/2026`: aplicada a taxa renegociada de **2,19%**. Divergências foram apontadas onde a Orbe continuou cobrando 2,59%.
- **Tratamento das 7 Divergências de Bandeira (Arquivo `06`):**
  - Nos 7 estornos onde a adquirente trocou a bandeira em relação à venda original (ex: Visa $\leftrightarrow$ Amex/Elo), comprovou-se que EC, modalidade, parcelas, data e taxas batiam perfeitamente.
  - **Tratamento:** O vínculo foi mantido, a taxa contratual da venda original foi aplicada (já que os contratos da Tarvo não variam taxa por bandeira) e foram geradas 7 pendências `DIVERGENCIA_CADASTRO_BANDEIRA` em `pendencias.csv` para cobrança de correção cadastral à Orbe.
- **Regra de Estornos Órfãos Sem Referência (Helena, 14h10):**
  - Se um arquivo de ajustes trouxer estorno que não conste nos arquivos principais da Orbe, o ajuste entra na apuração pelo valor declarado e gera pendência `ESTORNO_ORFAO_SEM_ORIGEM` para Helena notificar a adquirente.
- **Casa do Estudante Viagens (`1018325654`):**
  - Isenção total de taxas acordada de set a dez/2026. Em estrita conformidade com Helena, **nenhuma cobrança foi feita contra a adquirente**. As taxas cobradas foram enviadas para devolução interna em `pendencias.csv`. Apenas o estorno de venda prévia de agosto foi descontado da apuração.
- **Bloqueio Atlas Idiomas (`1076801732`):**
  - Operações iniciadas em 10/09 sem contrato formal assinado. 100% bloqueada de faturamento e encaminhada a `pendencias.csv` para validação comercial.

### 4.2. Remessas Internacionais (Câmbio)
- **Base da Tarvo:** 50% sobre o Spread BRL realizado por operação. Total de comissão apurada: **R$ 39.543,42**.
- **Nota Fiscal Única:** Emitida uma única nota fiscal para a parceira e pagadora **Ponte Câmbio Soluções Financeiras S.A.** (CNPJ `75374179000146`, extraído dinamicamente do e-mail `.eml`).
- **Exclusão de Spreads Negativos:** 4 operações com trava de 2h expirada (`PC-0926-0210`, `PC-0926-0326`, `PC-0926-0491` e `PC-0926-0545`) foram excluídas da nota e enviadas a `pendencias.csv` para contestação integral de Helena com a Ponte.
- **Auditoria de Taxas Mundo Aberto:** A taxa aplicada de 1,50% contra 1,20% acordada em aditivo gerou 23 divergências no valor cheio pago a mais (**R$ 1.418,88**). A parte da Tarvo permanece provisionada em setembro até a liquidação definitiva.

### 4.3. Classificação Contábil & Conciliação Bancária
- **Mapeamento Canônico de Linha Física Real:**
  - Extrato Banco Aurora: utiliza as linhas físicas originais do CSV bruto (`L9` a `L92`), descartando o cabeçalho descritivo bancário e a linha de `SALDO ANTERIOR`. O cabeçalho foi tratado com lookup insensível a maiúsculas e acentos (`Lançamento` ou `Histórico`), prevenindo descrições em branco.
  - Extrato Banco Meridiano: mapeia com exatidão o `ref_origem = FITID` de cada tag `<STMTTRN>`.
- **Princípio da Contrapartida Bancária:** Pagamentos em setembro de despesas já provisionadas em competências anteriores baixam o passivo sem duplicar despesa no resultado:
  - Salários de agosto baixam `2.1.04.001` (Salários a pagar).
  - Impostos de agosto (DAMSP, ISS, GPS, GRF, DARF) baixam as respectivas contas de tributos a recolher dos grupos `2.1.03` e `2.1.04`.
  - Repasse de câmbio de agosto recebido em 04/09 baixa `1.1.03.002` (Comissões a receber).
- **Despesas de Competência Setembro:** Reconhecimento direto de fornecedores correntes (AWS, Google Workspace, Condomínio, Contabilidade e Tarifas Bancárias do grupo `4.2.xx`).
- **Eliminação de Fake IA:** Lançamentos sem regra recebem `metodo = "HUMANO"`, `confianca = 0.00`, conta transitória `1.1.09.002` e abrem pendência `LANCAMENTO_SEM_REGRA`.
- **Conciliação Bancária e Detecção Dinâmica de Pendências:**
  - Transferência entre contas próprias de R$ 300.000,00 no Aurora em 30/09 (linha física L92) sem compensação no Meridiano na mesma data -> pendência `TRANSITO_BANCARIO` (`quem_decide = "Caio / Conciliação Bancária"`).
  - Crédito Pix não identificado de R$ 7.350,00 na linha física L50 -> pendência `CREDITO_NAO_IDENTIFICADO` (`quem_decide = "Helena / Financeiro"`).
  - Devolução operacional sem causa de R$ 12.400,00 na linha física L65 -> pendência `DEVOLUCAO_SEM_CAUSA` (`quem_decide = "Helena / Comercial"`).

---

## 5. Padrão Ouro de Auditabilidade (Organização Barte, 14h11)

Em resposta à diretriz da coordenação (*"Quem abrir tem que conseguir refazer qualquer número sem perguntar para vocês"*), a solução implementou três mecanismos de garantia total:

### 5.1. Rastro Universal Expandido (`rastro.csv`)
- Mantém rigorosamente as 4 colunas canônicas no início: `id_saida; arquivo_origem; ref_origem; valor`.
- Adiciona 3 colunas de transparência matemática: `regra_aplicada; taxa_contratada_aplicada; detalhe_calculo`.
- Cobre com rastreabilidade 1-para-1:
  1. Todas as comissões por lojista (`COM-XXXX`).
  2. Todas as notas fiscais a emitir (`NF-XXXX`), incluindo a nota da Ponte Câmbio.
  3. Todas as divergências de taxa apuradas (`DIV-XXXX`), vinculadas às linhas originais contestadas.
  4. Lançamentos bancários (`LAN-XXXX`) com linha física real (`L9` a `L92`) e FITID.
  5. Pendências analíticas (`PEN-XXXX`) rastreadas individualmente.

### 5.2. Prova Real Matemática Centavo a Centavo
- Cada um dos IDs reportados nas saídas oficiais possui verificação algorítmica:
  $$\forall id\_saida \in \{COM, DIV, NF, LAN, PEN\} : \sum_{rastro} valor \equiv valor\_reportado$$
- Inconsistências ou diferenças de arredondamento: **ZERO**.

### 5.3. Manifestos de Execução
Gerados a cada rodada em formato estruturado ([`auditoria_execucao.json`](file:///C:/projetosdaniel/desafio-barte-ai/barte-solution/desafio-barte-ai/saida/auditoria_execucao.json)) e executivo ([`auditoria_execucao.md`](file:///C:/projetosdaniel/desafio-barte-ai/barte-solution/desafio-barte-ai/saida/auditoria_execucao.md)), contendo:
- Timestamp ISO 8601 com fuso horário da execução.
- Inventário detalhado dos arquivos brutos lidos (linhas físicas, tamanho em bytes, hash, método de triagem).
- Status do fechamento (`PROVISORIO` ou `APROVADO_POR_HELENA`).
- Resumo de todas as regras contábeis e fiscais aplicadas.
- Validação formal da prova real de conciliação.

---

## 6. Quadro Geral dos Resultados Homologados (Setembro/2026)

| Arquivo de Saída | Linhas | Valor Total (BRL) | Destaque Técnico |
| :--- | :---: | :---: | :--- |
| **`comissoes_por_lojista.csv`** | 35 | **R$ 243.278,76** | 21 lojistas Checkout (R$ 203.735,34) + 14 clientes Câmbio (R$ 39.543,42) |
| **`divergencias_taxa.csv`** | 115 | **R$ 3.016,37** | 92 transações Checkout (R$ 1.597,49) + 23 operações Remessa (R$ 1.418,88) |
| **`notas_a_emitir.csv`** | 21 | **R$ 243.284,26** | 20 notas Checkout (saldo > 0) + 1 Nota Ponte Câmbio S.A. |
| **`lancamentos_classificados.csv`** | 184 | **100% Conciliado** | 84 lançamentos Aurora CC 44710 (L9 a L92) + 100 lançamentos Meridiano CC 902335 |
| **`pendencias.csv`** | 190 | **R$ 903.790,21** | Atlas bloqueada, Isenção Casa Estudante, 7 Bandeiras, Spreads Negativos, Trânsito 300k, Pix 7.350 |
| **`rastro.csv`** | 4.508 | **100% Rastreabilidade** | $\sum \text{rastro.valor} \equiv \text{valor\_reportado}$ para COM, NF, DIV, LAN e PEN |
| **`auditoria_execucao.json`** | 1 | — | Manifesto estruturado de inventário e metadados de execução |
| **`auditoria_execucao.md`** | 1 | — | Relatório executivo de auditoria institucional |

---

## 7. Guia Rápido de Execução e Verificação

### Modo 1: Executável Autônomo (.exe)
Basta colocar o arquivo [`fechamento_tarvo.exe`](file:///C:/projetosdaniel/desafio-barte-ai/barte-solution/desafio-barte-ai/fechamento_tarvo.exe) no diretório onde os arquivos brutos estão e rodar:
```powershell
.\fechamento_tarvo.exe
```

### Modo 2: Linha de Comando Python
```powershell
python src/app.py --data-dir ../../Tarvo_Data_Pack_set2026
```

### Modo 3: Suíte de Testes Automatizados
```powershell
python -m unittest discover -s tests -v
```
*(Todos os 15 testes integrados rodam em ~0.08 segundos com 100% de aprovação).*
