# Tarvo Closing Agent — Hackathon Barte AI

Solução autônoma de conciliação e fechamento financeiro mensal da **Tarvo Pagamentos**, desenvolvida com **LangGraph**, cascata de triagem de arquivos (**Jev / TypeSafe AI** -> **Gemini 3.8 Flash** -> **DeepSeek V1 Flash** -> **Heurística Local Offline**) e núcleo determinístico em Python com valores em `Decimal` e conferência das somas do rastro.

Cobertura funcional dos níveis **mínimo, alvo e extra** verificada no data pack de setembro e em cenários sintéticos de outubro. Isso não representa homologação da banca nem aprovação financeira de Helena. Os testes verificam as somas do rastro para comissões, notas, divergências, lançamentos e pendências; as limitações e os requisitos gerais de entrega ainda pendentes constam na auditoria em `PROMPTS/memoria/`.

---

## 🏛️ Arquitetura e Decisões Técnicas

A solução é construída sobre um **grafo de estados (LangGraph / StateGraph Dual-Mode)** composto por 5 estágios:

1. **Estágio 0 — Ingestão Dinâmica e Triagem em Quatro Camadas:**
   - Varredura dinâmica da pasta onde o executável/script estiver rodando.
   - Triagem híbrida em cascata:
     1. **Tier 1 (Jev / TypeSafe AI):** Cliente opcional de classificação estruturada de arquivos; desempenho e calibração não homologados nesta revisão.
     2. **Tier 2 (Gemini 3.8 Flash):** Cliente opcional de classificação de arquivos; um leitor ainda precisa validar o layout antes de calcular.
     3. **Tier 3 (DeepSeek V1 Flash):** Cliente opcional de contingência para classificação de arquivos, sem desempenho externo homologado.
     4. **Tier 4 (Heurística Local Offline):** Roteamento local por regras de nomes e conteúdo, disponível sem credenciais; falhas de fonte continuam sujeitas a diagnóstico e bloqueio.
2. **Estágio 1 — Camada Silver, Cobertura de Fontes & Guardrail 1 (Error Detector):**
   - Limpeza estrutural e formatação canônica (ISO-8601 `AAAA-MM-DD`, CNPJ numérico 14 dígitos, decimais com ponto `0.00`, delimitador `;`).
   - Rastreamento explícito de cobertura por domínio (`cobertura_fontes`): distingue fontes `PROCESSADA`, `AUSENTE`, `INVALIDA`, `VALIDA_SEM_MOVIMENTOS` e `BLOQUEADA_POR_DEPENDENCIA`, registrando motivo, dependência e responsável sem transformar falhas ou layouts desconhecidos em zero silencioso.
   - Normalização com preservação da linha física real original no extrato Aurora (`L9` a `L92`) e `FITID` no Meridiano.
3. **Estágio 2 — Motores de Domínio (Camada Gold, Parametrizados por Competência):**
   - **Motor de Checkout:** Filtra movimentos por competência, mantendo busca histórica (`tx_primarias`) para vendas originais; aplica as vigências da Bridge e a isenção da Casa entre setembro e dezembro. A Casa tem comissão negativa de `R$ -5,50` por estorno de agosto, sem nota, e devolução pendente de `R$ 15.396,77` com 118 contribuições Orbe. Atlas permanece sem faturamento, com `R$ 7.876,05` de taxas observadas em pendências. Diferenças isoladas de bandeira são preservadas sem alarme. IDs conflitantes ficam integralmente bloqueados.
   - **Motor de Câmbio:** Filtra pela contratação, extrai o CNPJ Ponte do e-mail e apura 50% do spread realizado elegível (`R$ 39.543,42`). Gera uma única nota **proposta** para a Ponte, exclui os negativos e identifica `R$ 1.418,88` de cobrança a maior da Mundo Aberto para contestação humana. Conflitos de `num_operacao` bloqueiam todas as versões; nenhuma contestação é enviada automaticamente.
   - **Motor Bancário e Classificação Proposta:** Classificação determinística pelo plano Fênix ERP (`1.1.03.001`, `2.1.04.001`, `4.2.01`, etc.), detecção dinâmica de transferências em trânsito bancário entre contas próprias (`R$ 300.000,00` no Aurora em 30/09 sem compensação no Meridiano), crédito Pix não identificado (`R$ 7.350,00` na `L50`), devolução sem causa (`R$ 12.400,00` na `L65`) e tratamento de movimentos sem regra com `metodo = "HUMANO"`, `confianca = 0.00` e transitória `1.1.09.002`. Casos conhecidos de Pix sem origem, devolução e repasses Atlas usam `REGRA/1.00` com pendência humana; contas e justificativas estão em P2 de `HIPOTESES.md`.
4. **Estágio 3 — Guardrail 2 (Auditoria de Divergências Reais):**
   - Checkout e filtro posterior usam diferença absoluta de pelo menos `0.005` ponto percentual; o motor de remessas seleciona somente cobranças a maior de pelo menos `0.01` ponto percentual. Diferença apenas no valor truncado não constitui mudança de taxa. O valor de remessa usa cotações e PTAX, conforme P1 de `HIPOTESES.md`.
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

O fluxo determinístico foi verificado sem chaves de API e sem chamadas a modelos externos, usando a heurística local. Arquivos inválidos ou ausentes geram bloqueios explícitos; falhas de cálculo ou publicação podem interromper a execução preservando as saídas anteriores. Os testes de fallback não homologam os provedores em nuvem.

Os clientes leem variáveis do ambiente do processo. `src/utils.py` também carrega
automaticamente o primeiro `.env` encontrado em `src/`, na raiz ou no diretório
de execução; variáveis já definidas no processo têm precedência. Copie
`src/.env.example` para `src/.env` e preencha suas chaves para ativar as integrações.
Arquivos `.env` com credenciais não devem ser versionados. Se já possui um `.env`,
atualize também os modelos e a rota Jev abaixo, pois ele sobrescreve os padrões
dos clientes. `LOG_LEVEL` não possui consumidor no código atual.

Variáveis suportadas:
```env
# Tier 1: TypeSafe Jev AI
JEV_API_KEY=
JEV_API_URL=https://api.typesafe.ai/v1/systemone
JEV_MODEL=jev-latest

# Tier 2: Google Gemini Flash
GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.8-flash

# Tier 3: DeepSeek V1 Flash
DEEPSEEK_API_KEY=
DEEPSEEK_API_URL=https://api.deepseek.com/chat/completions
DEEPSEEK_MODEL=deepseek-flash
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
2. **Casa do Estudante (EC 1018325654):** Isenção de MDR e antecipação acordada (set–dez/2026, informada pelo financeiro); taxas cobradas pela Orbe (`R$ 15.396,77`) consolidadas na pendência única `PEN-0058` para alinhamento comercial com Helena, preservando no `rastro.csv` todas as **118 contribuições individuais reais do arquivo `01_orbe_relatorio_comissoes_set2026.csv`** (sem vínculo com o extrato Aurora). A comissão líquida de setembro apurou apenas o estorno da venda de agosto (`R$ -5,50`), constando em `comissoes_por_lojista.csv` (`COM-0005`), porém **sem emissão de nota fiscal** em `notas_a_emitir.csv` por saldo não positivo (gerando 20 notas de checkout em vez de 21, totalizando `R$ 203.740,84`).
3. **Reversões de Antecipação no Arquivo 06:** Três reversões de antecipação foram abatidas da comissão de setembro e calculadas à taxa da antecipação original referenciada.
4. **Política de Duplicidade e Bloqueio Integral de Conflitos:** Cópias idênticas nos campos relevantes contam uma vez, com evidência. IDs conflitantes bloqueiam todas as versões, sem precedência automática. Na Orbe, a pendência é `DUPLICIDADE_CONFLITANTE`; na Ponte, `OPERACAO_DUPLICADA` com motivo explícito de conflito e bloqueio.
5. **Cobertura de Fontes e Fechamento Parcial:** Fontes ausentes (`AUSENTE`), corrompidas/layout inválido (`INVALIDA`), válidas sem movimentos na competência (`VALIDA_SEM_MOVIMENTOS`) e bloqueadas por falta de cadastro/plano (`BLOQUEADA_POR_DEPENDENCIA`) são explicitadas no manifesto e em `pendencias.csv`, nunca gerando zero silencioso.
6. **Guardrails Agênticos e Aprovação Humana:** O subagente consultivo atua exclusivamente em modo consultivo/explicativo; `estado_tecnico` concluído não equivale a aprovação financeira (`status_aprovacao`), e mudanças em dados, regras, código ou resultados impedem herdar a aprovação anterior na nova execução; o registro da execução antiga é preservado. O status informado pelo operador não autentica Helena.


## Evidências e limites da entrega

A revisão técnica de 17/10/2026 executou **58 testes**, reproduziu os seis CSVs
com o ZIP original e o complemento `06`, e conferiu 423 resultados por soma do
rastro. O mínimo, o alvo e o extra são cumulativos e estão cobertos nos dados de
setembro e cenários sintéticos de outubro; isso não equivale ao gabarito privado
da banca nem à aprovação financeira. O nível intermediário oficial é **alvo**.

`REGRA/1.00` identifica aplicação de uma regra de classificação proposta; uma
pendência associada ainda pode exigir decisão de Helena. Não representa certeza
da origem de um crédito ou homologação das contas contábeis. Não há conciliação
parcela por parcela nem geração de partidas dobradas completas para o ERP.

O roteiro local atualizado está em `apresentacao/entrega/roteiro-pitch-tarvo.txt`.
A revisão local não sincroniza automaticamente as notas do deck remoto.
`PROMPTS/MOMENTOS.md` contém quatro intervenções, mas não substitui o histórico
integral exigido pelo regulamento. Os exports das sessões de Marcus estão em
`PROMPTS/marcus/`, com índice, momentos, hashes e corte da captura. As sessões dos
demais integrantes precisam ser reunidas por eles. O usuário confirmou as
postagens/checkpoints e os prazos; esta exportação não acrescenta recibos de envio. Relatórios
antigos em `PROMPTS/memoria/` e o plano em `PROMPTS/outputs/arquitetura-stack.md`
preservam o estado de suas versões; o README e o dossiê descrevem a implementação
atual. Consulte `PROMPTS/memoria/revalidacao-main-cd2d849-2026-10-17.txt`.


### Correções verificadas na revisão final de 17/10

- Contrato fora da vigência, taxa vazia/inválida e condição ambígua bloqueiam a
  contribuição afetada com pendência e rastro; zero explícito continua válido.
  O estado técnico indica bloqueios, sem impedir o cálculo das partes independentes.
- Todos os lotes Orbe são preservados também entre os nós do LangGraph.
- O consultor prioriza nome exato/CNPJ e pede identificação em consultas ambíguas.
  Pendências sem comissão, como Atlas, são consultáveis pelo índice de CNPJ do
  manifesto. Para saídas antigas sem esse índice, reprocessar as fontes preservadas.
- `--competencia` valida a competência do manifesto, sem trocar o rótulo dos
  valores. Para consultar outro mês, selecionar seu snapshot com `--output-dir`.
- Respostas inválidas de Gemini/DeepSeek são rejeitadas, permitindo o fallback.
  Chamadas reais aos provedores continuam sem homologação por falta de credenciais.
- O EXE foi compilado e executado com saída redirecionada em UTF-8. O pacote
  inclui somente fontes Python e metadados do build; `.env` e dados não são
  embutidos. O snapshot preserva esses fontes e registra o hash do executável.

Os 58 testes passaram nos dois executores. A repetição dos 19 casos adicionais
da auditoria passou após as correções. Os seis CSVs de setembro mantêm os mesmos
valores e conteúdo; os manifestos foram renovados com a versão de regras e o
índice consultivo. Evidências em `PROMPTS/memoria/correcoes-features-2026-10-17.txt`.
