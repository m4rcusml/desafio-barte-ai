# Momentos Críticos de Interação com a IA (MOMENTOS.md)

Este documento registra 3 momentos decisivos de interação com a IA durante a construção da solução de fechamento financeiro da Tarvo Pagamentos, conforme exigido pelas instruções do hackathon.

---

### Momento 1: Proposta de LLM-as-a-judge na Ingestão vs. Modelo System One (Jev)
- **O que foi pedido:** Solicitou-se avaliar a adição de um LLM-as-a-judge na entrada da Camada Silver para inspecionar e rotear arquivos atípicos ou tardios (como o lote `06_orbe_ajustes_tardios`).
- **O que a IA devolveu:** A IA inicialmente aceitou a premissa de flexibilidade, mas apontou que colocar um LLM generativo convencional na rota crítica de dados traria alta latência (~3s), custos desnecessários de tokens e risco de não-determinismo em infraestrutura básica de conciliação. Em seguida, ao ser questionada sobre o modelo **Jev (TypeSafe AI)**, demonstrou que o Jev atua como um *Smart if-statement* tipado (`Choice`/`Noul`), não-autoregressivo e calibrado matematicamente.
- **O que fizemos com isso:** Adotamos a **Tripla Triagem Híbrida** (`Jev -> Gemini Flash -> Heurística Local`), garantindo alta capacidade semântica na ingestão sem nunca travar o pipeline caso a rede oscile.

---

### Momento 2: Erro de Dependência Externa e Criação do StateGraph Nativo (Onde a IA Errou/Corrigiu)
- **O que foi pedido:** Solicitou-se instalar e usar a biblioteca `langgraph` para orquestrar o fechamento em um binário autônomo `.exe`.
- **O que a IA devolveu:** A tentativa de instalação de pacotes pesados de terceiros via `pip install langgraph` falhou miseravelmente devido à dependência do pacote `zstandard`, que exigia compiladores C++ (`Microsoft Visual C++ 14.0`) inexistentes no ambiente Windows Python 3.15. Se insistisse, o `.exe` final ficaria inchado, frágil e dependente de DLLs de sistema.
- **O que fizemos com isso:** A IA foi corrigida e construiu uma implementação de **StateGraph Nativo (Dual-Mode)** dentro do código (`src/graph.py`). O sistema consome a biblioteca oficial do `langgraph` caso ela exista no ambiente, mas roda com 100% de paridade de API (`add_node`, `add_edge`, `compile`, `invoke`) usando apenas a biblioteca padrão do Python, permitindo compilar um executável `.exe` leve, seguro e imune a falhas de build.

---

### Momento 3: Incorporação do Arquivo 06 e Máquina de Estados de Fechamento da Helena
- **O que foi pedido:** Solicitou-se processar o novo arquivo complementar `06_orbe_ajustes_tardios_set2026.csv` e incorporar a resposta de Helena (13h34) sobre aprovação e colisões de `id_transacao`.
- **O que a IA devolveu:** A IA auditou as 14 linhas do arquivo 06 (10 estornos, 3 reversões de antecipação e 1 venda tardia da Kiwi Experience), comprovou que todas as taxas bateram 100% com os contratos e modelou a máquina de estados: se chega antes da aprovação de Helena (`PROVISORIO`), consolida no mês de movimento; se chega depois, joga para outubro. Além disso, definiu a política de precedência (*Last-Write-Wins*) preservando a linha antiga no `rastro.csv` com status `SUPERSEDED` e gerando alerta em `pendencias.csv`.
- **O que fizemos com isso:** Documentamos a premissa **P4** no `HIPOTESES.md`, atualizamos o motor de checkout e geramos as saídas oficiais em `saida/`, atingindo prova real matemática exata ($\sum \text{rastro.csv} \equiv \text{total\_reportado}$) em 100% das 35 comissões e 21 notas fiscais.
