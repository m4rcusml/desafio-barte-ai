# Tarvo Closing Agent — Hackathon Barte AI

Solução autônoma de conciliação e fechamento financeiro mensal da **Tarvo Pagamentos**, desenvolvida com **LangGraph**, quadrupla cascata de triagem semântica (**Jev / TypeSafe AI** -> **Gemini 2.5 Flash** -> **DeepSeek V1 Flash** -> **Heurística Local Offline**) e núcleo determinístico em Python com rigor matemático absoluto.

Cobertura funcional dos níveis **mínimo, alvo e extra** verificada no data pack de setembro e em cenários sintéticos de outubro. Isso não representa homologação da banca nem aprovação financeira de Helena. Os testes verificam as somas do rastro para comissões, notas, divergências, lançamentos e pendências; as limitações e os requisitos gerais de entrega ainda pendentes constam na auditoria em `PROMPTS/memoria/`.

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
2. **Estágio 1 — Camada Silver, Cobertura de Fontes & Guardrail 1 (Error Detector):**
   - Limpeza estrutural e formatação canônica (ISO-8601 `AAAA-MM-DD`, CNPJ numérico 14 dígitos, decimais com ponto `0.00`, delimitador `;`).
   - Rastreamento explícito de cobertura por domínio (`cobertura_fontes`): distingue fontes `PROCESSADA`, `AUSENTE`, `INVALIDA`, `VALIDA_SEM_MOVIMENTOS` e `BLOQUEADA_POR_DEPENDENCIA`, registrando motivo, dependência e responsável sem transformar falhas ou layouts desconhecidos em zero silencioso.
   - Normalização com preservação da linha física real original no extrato Aurora (`L9` a `L92`) e `FITID` no Meridiano.
3. **Estágio 2 — Motores de Domínio em Paralelo (Camada Gold, Parametrizados por Competência):**
   - **Motor de Checkout:** Filtra movimentos ativos por `competencia` (`AAAA-MM`) mantendo busca histórica integral (`tx_primarias`) para vendas originais de meses anteriores; aplica corte temporal da Bridge (15/09), isenção total de MDR/antecipação da Casa do Estudante (set–dez/2026) com faturamento apenas do estorno de agosto (`R$ -5,50`) e restauração das **118 transações Orbe reais** no `rastro.csv` da pendência consolidada (`PEN-0058`, `R$ 15.396,77`), bloqueio integral de faturamento da Atlas Idiomas (`R$ 7.876,05` em taxas retidas em pendências), preservação dos 7 estornos com bandeiras divergentes e **bloqueio integral de IDs conflitantes** (`DUPLICIDADE_CONFLITANTE`, sem *First-Write-Wins* ou *Last-Write-Wins*).
   - **Motor de Câmbio:** Filtra por `data_contratacao` da competência, extrai dinamicamente o CNPJ da Ponte Câmbio (`75374179000146`) a partir do `.eml`, aplica 50% split de spread realizado elegível (`R$ 39.543,42`), emite nota fiscal única da parceria com discriminação dinâmica da competência (`MM/AAAA`), exclui spreads negativos (`spread_brl < 0`), contesta sobretaxa da Mundo Aberto (`1,50%` vs `1,20%`, `R$ 1.418,88`) e bloqueia integralmente `num_operacao` conflitantes.
   - **Motor Bancário e Conciliação Dinâmica:** Classificação determinística pelo plano Fênix ERP (`1.1.03.001`, `2.1.04.001`, `4.2.01`, etc.), detecção dinâmica de transferências em trânsito bancário entre contas próprias (`R$ 300.000,00` no Aurora em 30/09 sem compensação no Meridiano), crédito Pix não identificado (`R$ 7.350,00` na `L50`), devolução sem causa (`R$ 12.400,00` na `L65`) e eliminação total de fake IA (`metodo = "HUMANO"`, `confianca = 0.00`, transitória `1.1.09.002`).
4. **Estágio 3 — Guardrail 2 (Auditoria de Divergências Reais):**
   - Descarte de falsos positivos de truncamento/arredondamento de centavos ($|\text{taxa aplicada} - \text{contratada}| \ge 0.005\%$).
5. **Estágio 4 — Emissor Atômico, Versionamento de Execução e Auditoria Universal:**
   - Validação matemática formal da Prova Real: $\forall id\_saida \in \{COM, NF, DIV, LAN, PEN\} : \sum \text{rastro.valor} \equiv \text{valor\_reportado}$.
   - Geração e validação em uma pasta temporária, preservação em `execucoes/AAAA-MM/<id_execucao>/` e publicação dos CSVs e manifestos em `fechamento-completo/` e `saida/`, com restauração dos destinos se uma troca falhar.
   - Cada execução guarda as entradas, uma cópia do código, resultados, manifesto, aprovação declarada e diferenças por lojista, nota e pendência. Uma nova execução com entradas, resultados, regras ou código alterados exige revisão; as versões anteriores e seus registros de aprovação permanecem intactos. Consulte [execucoes/README.md](execucoes/README.md).

---

## 🚀 Como Rodar do Zero

### Opção 1: Execução Direta via Python (Recomendada)

Não requer bibliotecas pesadas ou compiladores C++. Roda direto com a biblioteca padrão do Python:

```bash
# Execute na raiz do repositório; Python 3.14 foi usado na verificação.
# Prepare o data pack sem editar os arquivos:
python -m zipfile -e dados/originais/Tarvo_Data_Pack_set2026.zip dados/entrada
python -c "import shutil; shutil.copyfile('dados/originais/06_orbe_ajustes_tardios_set2026.csv', 'dados/entrada/06_orbe_ajustes_tardios_set2026.csv')"

# 2. Execute o fechamento de setembro/2026 apontando para a pasta com os arquivos brutos
python src/app.py --data-dir dados/entrada --competencia 2026-09

# 3. (Opcional) Parametrizar explícita ou dinamicamente outra competência (ex: outubro/2026)
python src/app.py --data-dir caminho/para/fontes_de_outubro --competencia 2026-10
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

### Opção 3: Executar a Suíte de Testes Automatizados (100% Reproduzível do Zero)

Para setembro/2026, o complemento `06_orbe_ajustes_tardios_set2026.csv` é obrigatório.
Sem ele, as frentes disponíveis continuam sendo calculadas, mas o fechamento fica
`PARCIAL_COM_BLOQUEIOS`, com pendência de fonte obrigatória ausente. Essa exigência
é específica desse envio de setembro e não se estende automaticamente a outubro.
O rastro bancário preserva o nome efetivo do arquivo bruto recebido, inclusive
quando os extratos de outro mês têm nomes diferentes.

```bash
python -m unittest discover -s tests -v
```
*(Os testes usam ambientes temporários isolados e fixtures próprias ou extraídas do ZIP original + `06`. Cobrem setembro, as três frentes em outubro, conflitos, idempotência, preservação de versões e aprovação por execução, falhas de cálculo/publicação, fontes ausentes/inválidas/vazias e rastro até as fontes brutas. A ausência do `06` bloqueia a conclusão técnica de setembro.)*

### Opção 4: Consultar o Subagente de Apresentação e Governança

Para interagir com o subagente consultivo da equipe:

```bash
# Resumo executivo do fechamento (lê competência, estado técnico e aprovação do manifesto)
python -m src.agent.consultant --summary

# Filtrar/validar explicitamente uma competência específica
python -m src.agent.consultant --summary --competencia 2026-09

# Explicar regras e vigências de um lojista específico
python -m src.agent.consultant --lojista "Bridge Idiomas"

# Listar pendências abertas agrupadas por tomador de decisão (Helena, Caio, Bia)
python -m src.agent.consultant --pendencias "Helena"

# Auditar a composição exata de qualquer ID de saída (COM, NF, DIV, LAN, PEN)
python -m src.agent.consultant --explain "PEN-0058"
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
| `comissoes_por_lojista.csv` | 35 | Comissões apuradas por lojista em Checkout (`R$ 203.735,34`) e Remessa (`R$ 39.543,42`), totalizando `R$ 243.278,76`. |
| `divergencias_taxa.csv` | 115 | Transações com divergência de taxa contratada: 92 Checkout (`R$ 1.576,23`) + 23 Remessas Mundo Aberto (`R$ 1.418,88`), totalizando `R$ 2.995,11`. |
| `notas_a_emitir.csv` | 21 | 20 notas líquidas positivas de Checkout (`R$ 203.740,84`) + 1 Nota Única da Ponte Câmbio (`R$ 39.543,42`, CNPJ `75374179000146`), totalizando `R$ 243.284,26`. |
| `lancamentos_classificados.csv` | 184 | Classificação contábil dos extratos Aurora (`L9` a `L92`) e Meridiano (`FITID`) no plano Fênix ERP (`R$ 5.839.423,46` em volume absoluto). |
| `pendencias.csv` | 68 | Casos que exigem decisão humana (`R$ 594.980,52`): 57 Atlas (`R$ 7.876,05`), 1 Casa do Estudante consolidada (`R$ 15.396,77`), 1 duplicata Ponte (`R$ 821,88`), 4 spreads negativos Ponte (`R$ 1.834,05`) e 5 pendências bancárias Aurora (`R$ 569.051,77`). |
| `rastro.csv` | 4.503 | Vínculos auditáveis 1-para-1 até os arquivos brutos (`.eml`, `.csv`, `.ofx`), incluindo as **118 transações Orbe reais** de `PEN-0058`, com 100% de prova real matemática. |
| `auditoria_execucao.json` | 1 | Manifesto estruturado com `id_execucao`, `versao_regras`, cobertura de fontes, hashes SHA-256 e comparação entre execuções. |
| `auditoria_execucao.md` | 1 | Relatório executivo institucional para a diretoria e Helena. |
| `historico_execucoes.json` | 1 | Trilha histórica acumulativa de execuções para rastreabilidade e governança de aprovação. |

---

## ⚠️ Limitações Conhecidas & Governança

1. **Atlas Idiomas (EC 1076801732):** Operações iniciadas em 10/09 sem contrato assinado retidas em 100% no arquivo `pendencias.csv` pelo valor da taxa em disputa (`R$ 7.876,05` em 57 transações) até liberação formal do Comercial (Bia). Repasses operacionais via PIX (`L34` e `L60`) também sinalizados para averiguação.
2. **Casa do Estudante (EC 1018325654):** Isenção de MDR e antecipação acordada (set–dez/2026); taxas cobradas indevidamente pela Orbe (`R$ 15.396,77`) consolidadas na pendência única `PEN-0058` para devolução interna com Helena e Comercial, preservando no `rastro.csv` todas as **118 contribuições individuais reais do arquivo `01_orbe_relatorio_comissoes_set2026.csv`** (sem vínculo fictício com o extrato Aurora) e faturando na comissão apenas o abatimento do estorno de venda de agosto (`R$ -5,50`).
3. **Reversões de Antecipação no Arquivo 06:** Três reversões de antecipação foram abatidas da comissão de setembro e calculadas à taxa da antecipação original referenciada.
4. **Política de Duplicidade e Bloqueio Integral de Conflitos:** Registros efetivamente idênticos em todos os campos relevantes são deduplicados com evidência preservada no `rastro.csv`; já registros com o mesmo `id_transacao` (Orbe) ou `num_operacao` (Ponte) e valores conflitantes têm **todas as suas ocorrências bloqueadas** (`DUPLICIDADE_CONFLITANTE`), sem escolha automática da primeira ou última versão.
5. **Cobertura de Fontes e Fechamento Parcial:** Fontes ausentes (`AUSENTE`), corrompidas/layout inválido (`INVALIDA`), válidas sem movimentos na competência (`VALIDA_SEM_MOVIMENTOS`) e bloqueadas por falta de cadastro/plano (`BLOQUEADA_POR_DEPENDENCIA`) são explicitadas no manifesto e em `pendencias.csv`, nunca gerando zero silencioso.
6. **Guardrails Agênticos e Aprovação Humana:** O subagente consultivo atua exclusivamente em modo consultivo/explicativo; `estado_tecnico` concluído não equivale a aprovação financeira (`status_aprovacao`), e qualquer mudança nos dados ou regras revoga aprovações anteriores para `REABERTO_PARA_REVISAO`.

