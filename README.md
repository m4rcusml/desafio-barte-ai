# Tarvo Closing Agent — Hackathon Barte AI

Solução autônoma de conciliação e fechamento financeiro mensal da **Tarvo Pagamentos**, desenvolvida com **LangGraph**, quadrupla cascata de triagem semântica (**Jev / TypeSafe AI** -> **Gemini 2.5 Flash** -> **DeepSeek V1 Flash** -> **Heurística Local Offline**) e núcleo determinístico em Python com rigor matemático absoluto.

Entrega homologada no **Nível Extra**, com 100% de prova real matemática no `rastro.csv` ($\sum \text{rastro.valor} \equiv \text{valor\_reportado}$ para `COM`, `NF`, `DIV`, `LAN` e `PEN`), tratamento de ajustes tardios (`06_orbe`), classificação de linhas físicas reais do Aurora (`L9` a `L92`), conciliação dinâmica de transferências em trânsito e arquitetura resiliente pronta para rodar em outubro sem retrabalho.

---

## 🏛️ Arquitetura e Decisões Técnicas

A solução é construída sobre um **grafo de estados (LangGraph / StateGraph Dual-Mode)** composto por 5 estágios:

1. **Estágio 0 — Ingestão Dinâmica & Triagem Tri-Tier em Cascata:**
   - Varredura dinâmica da pasta onde o executável/script estiver rodando.
   - Triagem híbrida em cascata:
     1. **Tier 1 (Jev / TypeSafe AI):** Decisões tipadas estruturadas em sub-500ms com probabilidades calibradas.
     2. **Tier 2 (Gemini 2.5 Flash):** Raciocínio semântico contextual para anomalias e novos layouts.
     3. **Tier 3 (DeepSeek V1 Flash):** Fallback semântico veloz para contingência de rede/APIs de LLM.
     4. **Tier 4 (Heurística Local Offline):** Roteamento determinístico imediato (0ms, offline) baseado em regex e assinaturas de colunas, garantindo 100% de disponibilidade.
2. **Estágio 1 — Camada Silver & Guardrail 1 (Error Detector):**
   - Limpeza estrutural e formatação canônica (ISO-8601 `AAAA-MM-DD`, CNPJ numérico 14 dígitos, decimais com ponto `0.00`, delimitador `;`).
   - Normalização com preservação da linha física real original no extrato Aurora (`L9` a `L92`) e FITID no Meridiano.
   - Validação de integridade e **Detector de Colisões de ID** (sinalização como pendência se houver choque de valores, conforme orientação da Helena).
3. **Estágio 2 — Motores de Domínio em Paralelo (Camada Gold):**
   - **Motor de Checkout:** Processa lotes principal e tardio (`06_orbe`), corte temporal da Bridge (15/09), isenção total de taxas da Casa do Estudante com faturamento apenas do estorno de agosto (R$ -5,50), bloqueio integral de faturamento da Atlas Idiomas (R$ 262.138,61 em pendências) e preservação dos 7 estornos com bandeiras divergentes.
   - **Motor de Câmbio:** Extração dinâmica do CNPJ da Ponte Câmbio (`75374179000146`) a partir do `.eml`, 50% split de spread realizado com a Ponte Câmbio, emissão de nota fiscal única da parceria, exclusão dinâmica de spreads negativos (`spread_brl < 0`) e contestação de sobretaxa da Mundo Aberto (1,50% vs 1,20%).
   - **Motor Bancário e Conciliação Dinâmica:** Classificação determinística pelo plano Fênix ERP (`1.1.03.001`, `2.1.04.001`, `4.2.01`, etc.), detecção dinâmica de transferências em trânsito bancário entre contas próprias (R$ 300.000,00 no Aurora em 30/09 sem compensação no Meridiano), crédito Pix não identificado (R$ 7.350,00 na L50), devolução sem causa (R$ 12.400,00 na L65) e eliminação total de fake IA (`metodo = "HUMANO"`, `confianca = 0.00`, transitória `1.1.09.002`).
4. **Estágio 3 — Guardrail 2 (Auditoria de Divergências Reais):**
   - Descarte de falsos positivos de arredondamento de centavos ($|\text{taxa aplicada} - \text{contratada}| \ge 0.005\%$).
5. **Estágio 4 — Emissor Atômico das Saídas e Auditoria Universal:**
   - Validação matemática formal da Prova Real: $\forall id\_saida : \sum \text{rastro.valor} \equiv \text{valor\_reportado}$.
   - Gravação simultânea dos 6 CSVs oficiais e 2 manifestos de execução tanto na pasta local (`fechamento-completo/`) quanto no diretório oficial canônico (`saida/`).
   - Geração de `auditoria_execucao.json` e `auditoria_execucao.md` contendo inventário físico, hashes e carimbo ISO.

---

## 🚀 Como Rodar do Zero

### Opção 1: Execução Direta via Python (Recomendada)

Não requer bibliotecas pesadas ou compiladores C++. Roda direto com a biblioteca padrão do Python:

```bash
# 1. Navegue até o diretório da solução
cd barte-solution/desafio-barte-ai

# 2. Execute o agente apontando para a pasta com os arquivos brutos
python src/app.py --data-dir ../../Tarvo_Data_Pack_set2026
```

### Opção 2: Compilação e Execução como Executável (.exe)

Para gerar o binário autônomo portátil que pode ser colocado na mesma pasta dos arquivos recebidos:

```bash
# 1. Execute o script de build
python src/build_exe.py

# 2. O executável será gerado em: dist/fechamento_tarvo.exe
# Basta copiar o fechamento_tarvo.exe para dentro da pasta do fechamento mensal e executar!
.\fechamento_tarvo.exe
```

### Opção 3: Executar a Suíte de Testes Automatizados

```bash
python -m unittest discover -s tests -v
```
*(Todos os 23 testes rodam em ~0.15 segundos com 100% de aprovação, cobrindo riscos financeiros, deduplicação, referências, arredondamento, simulação de outubro e fechamento parcial).*

### Opção 4: Consultar o Subagente de Apresentação e Governança

Para interagir com o subagente consultivo da equipe:

```bash
# Resumo executivo do fechamento
python -m src.agent.consultant --summary

# Explicar regras e vigências de um lojista específico
python -m src.agent.consultant --lojista "Bridge Idiomas"

# Listar pendências abertas agrupadas por tomador de decisão (Helena, Caio, Bia)
python -m src.agent.consultant --pendencias "Helena"

# Auditar a composição exata de qualquer ID de saída (COM, NF, DIV, LAN, PEN)
python -m src.agent.consultant --explain "NF-0021"
```

---

## 🔑 Configuração de Ambiente (.env)

A solução foi desenhada para **nunca travar**, mesmo sem nenhuma chave de API ou conexão de rede (graças ao Tier 4 de Heurística Local Offline). 

Para ativar os tiers de IA em nuvem, copie o arquivo de exemplo e insira suas credenciais:
```bash
cp src/.env.example src/.env
```

Variáveis suportadas:
```env
# Tier 1: TypeSafe Jev AI
JEV_API_KEY=
JEV_BASE_URL=https://api.jev.ai/v1
JEV_MODEL=jev-financial-classifier-v1

# Tier 2: Google Gemini Flash
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash

# Tier 3: DeepSeek V1 Flash
DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-v1-flash
```

---

## 📁 Estrutura de Arquivos e Entregáveis

Ao executar, o agente gera os 6 CSVs obrigatórios com separador `;` e ponto decimal tanto em `./fechamento-completo/` quanto em `saida/`:

| Arquivo | Registros Gerados | Descrição |
| :--- | :---: | :--- |
| `comissoes_por_lojista.csv` | 35 | Comissões apuradas por lojista em Checkout (R$ 203.735,34) e Remessa (R$ 39.543,42). |
| `divergencias_taxa.csv` | 115 | Transações com divergência de taxa contratada (Checkout Rota Global e Remessas Mundo Aberto R$ 1.418,88). |
| `notas_a_emitir.csv` | 21 | Notas líquidas positivas de Checkout e Nota Única da Ponte Câmbio (CNPJ 75374179000146). |
| `lancamentos_classificados.csv` | 184 | Classificação contábil dos extratos Aurora (L9 a L92) e Meridiano (FITID) no plano Fênix ERP. |
| `pendencias.csv` | 68 | Casos que exigem decisão humana com exposição real em disputa (Atlas R$ 7,9k, Casa R$ 15,4k, Spreads Negativos, Trânsito 300k, Pix 7.350, Devolução 12.4k, Repasses Atlas). |
| `rastro.csv` | 4.386 | Vínculos auditáveis 1-para-1 até os arquivos brutos (.eml, .csv, .ofx) com 100% de prova real matemática. |
| `auditoria_execucao.json` | 1 | Manifesto estruturado de metadados, contagem de linhas e hashes SHA-256. |
| `auditoria_execucao.md` | 1 | Relatório executivo institucional para a diretoria e Helena. |

---

## ⚠️ Limitações Conhecidas & Governança

1. **Atlas Idiomas (EC 1076801732):** Operações iniciadas em 10/09 sem contrato assinado retidas em 100% no arquivo `pendencias.csv` pelo valor da taxa em disputa (R$ 7.876,05) até liberação formal do Comercial (Bia). Repasses operacionais via PIX (L34 e L60) também sinalizados para averiguação.
2. **Casa do Estudante (EC 1018325654):** Isenção de MDR acordada; taxas cobradas indevidamente pela Orbe (R$ 15.396,77) consolidadas em pendência única para devolução interna com Helena e Comercial, faturando apenas o abatimento do estorno de agosto (R$ -5,50).
3. **Reversões de Antecipação no Arquivo 06:** Três reversões de antecipação (R$ 124.353,87 em volume) foram abatidas da receita da Tarvo e calculadas à taxa da antecipação original referenciada.
4. **Política de Duplicidade e Colisão de Linhas:** Transações com o mesmo `id_transacao` e dados idênticos são deduplicadas; transações conflitantes são bloqueadas sem precedência cega e encaminhadas a `pendencias.csv`.
5. **Guardrails Agênticos:** O subagente consultivo atua exclusivamente em modo consultivo/explicativo, sendo estritamente impedido de autorizar exceções financeiras ou emitir pagamentos externos.
