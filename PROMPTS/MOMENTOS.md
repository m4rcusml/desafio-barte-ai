# Momentos Críticos de Interação com a IA (MOMENTOS.md)

Este documento registra 4 momentos decisivos de interação com a IA durante a construção da solução de fechamento financeiro da Tarvo Pagamentos, conforme exigido pelas instruções do hackathon.

---

### Momento 1: Proposta de LLM-as-a-judge na Ingestão vs. Modelo System One (Jev)
- **O que foi pedido:** Solicitou-se avaliar a adição de um LLM-as-a-judge na entrada da Camada Silver para inspecionar e rotear arquivos atípicos ou tardios (como o lote `06_orbe_ajustes_tardios`).
- **O que a IA devolveu:** A IA inicialmente aceitou a premissa de flexibilidade, mas apontou que colocar um LLM generativo convencional na rota crítica de dados traria alta latência (~3s), custos desnecessários de tokens e risco de não-determinismo em infraestrutura básica de conciliação. Em seguida, ao ser questionada sobre o modelo **Jev (TypeSafe AI)**, demonstrou que o Jev atua como um *Smart if-statement* tipado (`Choice`/`Noul`), não-autoregressivo e calibrado matematicamente.
- **O que fizemos com isso:** Adotamos a **Tripla Triagem Híbrida** (`Jev -> Gemini Flash -> DeepSeek V1 Flash -> Heurística Local`), garantindo alta capacidade semântica na ingestão sem nunca travar o pipeline caso a rede oscile.

---

### Momento 2: Erro de Dependência Externa e Criação do StateGraph Nativo (Onde a IA Errou/Corrigiu)
- **O que foi pedido:** Solicitou-se instalar e usar a biblioteca `langgraph` para orquestrar o fechamento em um binário autônomo `.exe`.
- **O que a IA devolveu:** A tentativa de instalação de pacotes pesados de terceiros via `pip install langgraph` falhou miseravelmente devido à dependência do pacote `zstandard`, que exigia compiladores C++ (`Microsoft Visual C++ 14.0`) inexistentes no ambiente Windows Python 3.15. Se insistisse, o `.exe` final ficaria inchado, frágil e dependente de DLLs de sistema.
- **O que fizemos com isso:** A IA foi corrigida e construiu uma implementação de **StateGraph Nativo (Dual-Mode)** dentro do código (`src/graph.py`). O sistema consome a biblioteca oficial do `langgraph` caso ela exista no ambiente, mas roda com 100% de paridade de API (`add_node`, `add_edge`, `compile`, `invoke`) usando apenas a biblioteca padrão do Python, permitindo compilar um executável `.exe` leve, seguro e imune a falhas de build.

---

### Momento 3: Incorporação do Arquivo 06, Bloqueio de Conflitos sem Precedência Cega e Governança de Aprovação
- **O que foi pedido:** Solicitou-se processar o novo arquivo complementar `06_orbe_ajustes_tardios_set2026.csv` e incorporar as orientações de Helena sobre aprovação humana e colisões de `id_transacao` / `num_operacao`.
- **O que a IA devolveu:** Inicialmente, a IA havia proposto uma política de precedência automática (*Last-Write-Wins* / `SUPERSEDED`) ou *First-Write-Wins* para IDs repetidos. Ao confrontar essa sugestão com as regras do negócio, identificou-se que escolher automaticamente uma versão em registros conflitantes violaria a governança financeira de Helena.
- **O que fizemos com isso:** Corrigimos o desenho para um pré-agrupamento estrito por assinatura completa tanto na Orbe quanto na Ponte: (1) cópias efetivamente idênticas em todos os campos relevantes são deduplicadas uma única vez preservando evidência no `rastro.csv`; (2) IDs com valores conflitantes têm **todas as suas ocorrências bloqueadas** (`DUPLICIDADE_CONFLITANTE`) sem escolha automática; e (3) separamos `estado_tecnico` (`CONCLUIDO` / `PARCIAL_COM_BLOQUEIOS`) de `status_aprovacao` (`PROVISORIO` / `APROVADO_POR_HELENA` / `REABERTO_PARA_REVISAO`), garantindo que qualquer alteração de insumos, regras ou resultados rebaixe automaticamente aprovações anteriores para `REABERTO_PARA_REVISAO`.

---

### Momento 4: Eliminação de "Fake IA" Contábil e Rastreabilidade Física Real do Extrato Aurora (Onde a IA Errou/Corrigiu)
- **O que foi pedido:** Solicitou-se classificar os lançamentos dos extratos bancários (Aurora e Meridiano) contra o plano de contas Fênix ERP e mapear cada lançamento às linhas originais no `rastro.csv`.
- **O que a IA devolveu:** A IA inicialmente cometeu dois erros graves: (1) Para lançamentos bancários não mapeados por regex/regras determinísticas, atribuiu silenciosamente o rótulo fictício `metodo = "IA"` com confiança arbitrária `0.85` sem realizar nenhuma chamada real a um modelo de linguagem; (2) No extrato do Banco Aurora, utilizou como referência de origem o índice relativo do arquivo intermediário formatado (`L3` a `L86`), em vez da linha física real do arquivo CSV bruto original (`L9` a `L92`), além de falhar na leitura da coluna de descrição por buscar `Histórico` quando o cabeçalho bruto era `Lançamento`.
- **O que fizemos com isso:** Repudiamos a simulação de IA ("Fake IA") e instruímos a correção imediata: se não houver chamada real de LLM ou regra homologada, o registro deve ser honestamente classificado como `metodo = "HUMANO"`, `confianca = 0.00`, alocado na conta transitória `1.1.09.002` e enviado como pendência em `pendencias.csv`. No formatador do Aurora, implementamos lookup insensível a acentos/maiúsculas (`Lançamento` ou `Histórico`), descartamos a linha de saldo anterior e capturamos a numeração física 1-indexed real do arquivo bruto original (`L9` a `L92`), alcançando conformidade total com a diretriz de auditoria da Barte.

---

### Momento 5: Alucinação de CNPJ da Ponte Câmbio vs. Extração Determinística do E-mail (Onde a IA Errou/Corrigiu)
- **O que foi pedido:** Emitir a nota fiscal única de intermediação da Ponte Câmbio (`NF-0021`) no valor exato de 50% dos spreads positivos realizados de setembro/2026.
- **O que a IA devolveu:** Inicialmente, um modelo generativo propôs o CNPJ `40892317000144` para a Ponte Câmbio Soluções Financeiras S.A. Ao submeter esse valor ao guardrail de integridade referencial e validação de dígitos verificadores (módulo 11 da Receita Federal), o CNPJ foi sumariamente rejeitado como inválido — tratava-se de uma clássica alucinação de LLM sobre dados cadastrais fiscais.
- **O que fizemos com isso:** Bloqueamos qualquer inferência probabilística de CNPJ. Desenvolvemos no formatador da Ponte (`src/formatters/ponte_formatter.py`) um parser MIME/regex direto sobre o arquivo bruto original `03_email_ponte_cambio_relatorio_set2026.eml`, extraindo o CNPJ legal autêntico informado no cabeçalho do e-mail da parceira: `75.374.179/0001-46` (armazenado estritamente com 14 dígitos numéricos: `75374179000146`). Adicionalmente, corrigimos o `rastro.csv` para apontar diretamente para o arquivo `.eml` bruto, preservando a regra de ouro de rastreabilidade até os dados não manipulados do data pack.

