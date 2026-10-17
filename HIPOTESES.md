# Hipóteses, premissas e confirmações — Tarvo

Registro atualizado com o [Checkpoint 1 enviado em 17/10/2026](PROMPTS/outputs/checkpoint-1.txt), seu [feedback](PROMPTS/outputs/checkpoint-1-feedback.txt) e as respostas documentadas em [duvidas-slack.md](PROMPTS/outputs/duvidas-slack.md) e [nossas-duvidas.md](PROMPTS/outputs/nossas-duvidas.md). O checkpoint registra intenção de desenvolvimento, não funcionalidades implementadas. O feedback reconhece a leitura da causa raiz, mas não homologa limites, contas contábeis ou resultados numéricos.

O feedback orienta considerar premissas que alteram o fechamento e exclui a hipótese de caixa das entregas. P1 e P2 abaixo descrevem as escolhas implementadas pela equipe, sujeitas aos limites indicados; P3 fica como histórico fora de escopo. As confirmações do financeiro estão separadas dessas escolhas. A revisão documental de 17/10/2026 usa os CSVs reproduzidos da main `cd2d849` e o código dos motores; não altera fontes nem regras financeiras.

**Estado atual:** o núcleo determinístico em Python, os geradores dos 6 CSVs oficiais e o subagente consultivo estão implementados e verificados no fechamento de setembro/2026 (`01 + 06`) e na simulação parametrizada de outubro/2026 (`--competencia 2026-10`). A aprovação final do fechamento permanece humana (`status_aprovacao = PROVISORIO` até homologação de Helena).

## Hipóteses de causa raiz

| ID | Hipótese e evidência | Situação e limite |
|---|---|---|
| H1 | Cadastros, taxas, vigências e exceções fragmentados geram associação manual e retrabalho. Helena confirmou conhecimento concentrado; faltam ECs na planilha e há condições desatualizadas. Checkout leva cerca de três dias, metade de associação e metade de retrabalho, segundo o financeiro. | Sustentada pelos relatos e arquivos. Não implica ausência completa de cadastro: existe uma planilha, mas ela é incompleta e desatualizada. Tempos são estimativas do cliente. |
| H2 | A conferência atual não detecta sistematicamente diferenças contratuais antes de afetarem lojistas. Há reclamação por cobrança indevida e casos como Rota, Bridge e Mundo Aberto. | Sustentada pelas ocorrências; não afirmar que ninguém confere, pois existe conferência manual. |
| H3 | Repasses anteriores à liquidação contribuem para a necessidade de financiamento. | O uso da conta garantida para esses adiantamentos foi confirmado. Participação no saldo negativo e custo não quantificados; ver P3. Reconhecimento de receita por competência não é causa direta de saída de caixa. |

## Premissas propostas no Checkpoint 1 e adotadas na implementação

### P1 — Tolerância de divergência de remessa

- **Decisão implementada pela equipe (escolha delegada):** o motor de remessas seleciona cobranças a maior quando `spread_pct_aplicado - spread_contratado_pct >= 0.01` ponto percentual. O filtro posterior usa diferença absoluta `>= 0.005` ponto percentual e não amplia a seleção já feita pelo motor. O limite efetivo de remessa é, portanto, inclusivo de `0.01` p.p.; não é o limite estrito de `0.005` p.p. descrito em versões anteriores deste documento.
- **Justificativa e limite:** a faixa evita alertas por pequenas diferenças na representação percentual e distingue as operações de setembro com excesso de `0.30` p.p. O valor contestado é calculado com as cotações, sem usar o percentual arredondado como base monetária: `valor_me × (taxa_cliente − ptax_ref × (1 + spread_contratado))`, arredondado por operação com `ROUND_HALF_UP`. É uma tolerância operacional escolhida pela equipe, não uma regra homologada por Helena; pode omitir excessos inferiores a `0.01` p.p. em novos dados. Não há filtro monetário mínimo adicional no motor.
- **Efeito verificado em setembro/2026:** captura integralmente as **23 operações da Mundo Aberto Intercâmbio** em que a Ponte Câmbio aplicou `1,50%` sobre a PTAX em vez do spread renegociado de `1,20%` (diferença de `+0,30` p.p.), totalizando **R$ 1.418,88** de divergência a contestar pelo valor cheio pago a mais pelo lojista. Nenhuma operação legítima dos demais 13 lojistas (todos a `1,50%` exatos) é afetada ou omitida.
- **Invariância da comissão:** conforme regra confirmada, a comissão da Tarvo permanece calculada sobre 50% do spread realizado elegível (**R$ 39.543,42**).
- **Fonte:** pergunta e resposta do item 9 de `duvidas-slack.md`.

### P2 — Contrapartida de movimentos sem identificação suficiente

- **Escolha implementada pela equipe:** propor contrapartidas patrimoniais existentes no plano Fênix ERP (`04_plano_de_contas_fenix_erp.csv`), com pendências humanas para origem, causa ou contrato ainda não resolvidos. As contas específicas são propostas contábeis da equipe; Helena confirmou os fatos, não esses códigos.
  1. **Crédito Pix sem origem identificada (`L50`, 16/09/2026, `R$ 7.350,00`):** `1.1.09.002` (*Valores a Identificar / Conciliar*), `metodo = REGRA`, `confianca = 1.00`, com pendência `CREDITO_NAO_IDENTIFICADO` (`Helena / Financeiro`). A conta transitória evita reconhecer receita sem origem.
  2. **Devolução de repasse Mundo Aberto sem motivo confirmado (`L65`, 23/09/2026, `R$ 12.400,00`):** `2.1.01.001`, `metodo = REGRA`, `confianca = 1.00`, com pendência `DEVOLUCAO_SEM_CAUSA` (`Helena / Comercial`). A proposta recompõe a obrigação de repasse ao lojista; a causa do retorno permanece desconhecida e exige revisão.
  3. **Repasses operacionais para Atlas Idiomas (`L34`, `R$ -112.220,15`; `L60`, `R$ -137.081,62`):** `2.1.01.001`, `metodo = REGRA`, `confianca = 1.00`, com pendências `REPASSE_LOJISTA_BLOQUEADO` (`Helena / Comercial`). A proposta baixa obrigação de repasse; o bloqueio de faturamento por falta de contrato não transforma o pagamento em despesa nem comprova que ele foi autorizado. Os valores são os dos movimentos bancários, sem substituição por estimativas do texto anterior.
  4. **Transferência entre contas próprias sem compensação no mês (`L92`, 30/09/2026, `R$ -300.000,00`):** alocada em `1.1.09.001` (*Valores em Trânsito Bancário*), `metodo = REGRA`, `confianca = 1.00`, gerando pendência `TRANSITO_BANCARIO` (`Caio / Conciliação Bancária`).
- **Significado de método e confiança:** `REGRA/1.00` registra a aplicação determinística da classificação proposta, não certeza da origem, aprovação comercial ou decisão de Helena. Movimentos sem regra conhecida recebem `HUMANO/0.00`, conta `1.1.09.002` e pendência `LANCAMENTO_SEM_REGRA`. Todos os lançamentos continuam provisórios até revisão.
- **Alternativa e impacto:** usar transitória também em L65/L34/L60 mudaria a conta proposta, sem alterar os valores bancários, comissões ou notas. A implementação mantém a contrapartida de repasse e explicita a decisão pendente. Uma revisão contábil pode exigir reclassificação.
- **Fontes dos fatos:** itens 8, 10 e 12 de `duvidas-slack.md`. **Evidência da escolha implementada:** `src/engines/banking_engine.py` e `saida/lancamentos_classificados.csv`.

### P3 — Impacto dos adiantamentos no caixa (histórico; fora das entregas)

- **Decisão após feedback:** retirada das premissas de fechamento; não será quantificada nem usada para alterar valores das entregas. O texto abaixo preserva o contexto do que foi enviado, sem constituir tarefa de desenvolvimento.

- **Hipótese:** repasses anteriores à liquidação contribuem para a necessidade de financiamento, mas sua participação no saldo negativo e seu custo ainda não foram quantificados.
- **Fatos conhecidos:** a regra é repassar o já liquidado perto dos dias 10 e 24; Bia às vezes adianta pagamentos sob pressão, usando a conta garantida, sem limite documentado. A Orbe deposita tudo no Aurora, com prazos distintos por modalidade.
- **Validação necessária:** agenda de recebíveis, vínculo dos repasses aos recebimentos e condições/custos da conta garantida, ausentes ou insuficientes no pacote. A quantificação completa está fora do escopo enviado.
- **Se não se sustentar:** revisar a explicação do impacto financeiro. Não atribuir todo o saldo negativo aos adiantamentos, anunciar perda não comprovada ou aplicar automaticamente a taxa de antecipação de 2,1% a esse evento distinto.
- **Fontes:** item 16 e esclarecimento complementar de repasse em `duvidas-slack.md`; situação atual em `nossas-duvidas.md`.

## Perguntas ao financeiro e respostas recebidas

Resumo das confirmações relevantes. As perguntas completas, autores, datas e links estão nos registros referenciados; os seis esclarecimentos à Turma do Barulho foram fornecidos pelo usuário, sem permalink da resposta. Propostas sem resposta não são confirmação.

| Tema perguntado | Resposta recebida | Referência |
|---|---|---|
| Base de checkout e diferenças | Bruto × taxa contratada, sem desconto de custo Orbe. Devolução e cobrança em divergências comuns dependem da análise de Helena. | `duvidas-slack.md`, itens 2 e 17 |
| Estornos, antecipações e notas | Estorno afeta o mês do estorno à taxa da venda original; antecipação entra e reversão abate. Uma nota positiva por lojista/mês; negativo não passa automaticamente ao mês seguinte. | Itens 3 e 6 |
| ECs ausentes e Atlas | Vínculos Kiwi/Horizonte confirmados; Atlas não deve ser faturada sem confirmação comercial. | Item 5 |
| Remessa e competência | 50% do spread realizado elegível, por contratação; padrão 1,5%; uma nota para a Ponte. Ressalva de compliance não impede por si só. | Itens 6 e 7 |
| Divergência de remessa e ajuste | Contestar valor integral pago a mais; excesso de Mundo Aberto permanece na participação de setembro. Ajuste da participação ocorre no mês do ajuste. Limite de tolerância delegado à equipe. | Itens 9 e 13 |
| Arredondamento | Centavos por linha/operação, meio centavo para cima em magnitude. Truncamento da Orbe não é divergência sozinho; checkout usa bruto × diferença das taxas. | Item 11 |
| Provisões e conta de classificação | Contrapartida bancária; folha, tributos de agosto e recebimento Ponte de 04/09 já registrados. Além desses, nada provisionado; despesas indicadas entram no mês. | Item 12 |
| Negativos, duplicata e contestação | Quatro negativos questionados excluídos da comissão/nota e pendentes com Helena. Duplicata contada uma vez e listada para correção. Para o case, considerar prazo de contestação aberto. | Itens 7, 15 e 18 |
| Casa do Estudante | MDR e antecipação zero de setembro a dezembro (informado pelo financeiro em resposta no Slack, pois a planilha trazia apenas a anotação "ver c/ comercial"); devolução separada com Helena/comercial, sem cobrança à Orbe por isenção não comunicada. Estornos anteriores respeitam taxa original. Não emite NF por saldo negativo (R$ -5,50). | Atualização de 17/10 às 9h44 via Slack |
| Atlas Idiomas | Operações iniciadas em 10/09 sem contrato assinado: R$ 7.876,05 de taxas observadas em 57 movimentos pendentes; não são comissão contratual confirmada. No arquivo 01, as vendas somam R$ 135.428,90. A soma algébrica dos brutos de todos os movimentos é R$ 262.138,61: vendas + antecipações de R$ 235.943,10 − reversões de R$ 108.712,14 − estornos de R$ 521,25. Essa soma inclui bases sobrepostas e não representa vendas novas. Não faturar até confirmação comercial. | Regra: resposta de Helena e item 5. Valores: recálculo do arquivo 01 na revisão de cd2d849 |
| Rotina, esforço e responsáveis | Bia: checkout/taxas; Caio: bancos/remessas; Helena: revisão, exceções e aprovação. Estimativa: 3 dias checkout, 2 remessa, 2 bancos e 1 notas/revisão. Controle por “ok” e data. | Resposta para Turma do Barulho |
| Desconto, repasses e ajustes Ponte | Taxa descontada na liquidação; nota documenta, sem nova cobrança. Repasse regular do já liquidado e exceção por conta garantida. Ponte responde por e-mail e ajusta relatório posterior; Helena confere. | Resposta e complemento para Turma do Barulho |

## Decisões da equipe implementadas e lacunas externas

- **Núcleo de checkout e remessas:** implementados e verificados com `01 + 02 + 03 + 06`, respeitando vigências históricas (`tx_primarias`) e corte por competência (`--competencia AAAA-MM`).
- **Divergências de remessa (P1):** limite efetivo inclusivo de `0.01` ponto percentual para cobrança a maior, capturando as 23 operações da Mundo Aberto (`R$ 1.418,88`).
- **Classificações bancárias (P2):** contrapartidas patrimoniais `1.1.09.001`, `1.1.09.002` e `2.1.01.001`, fundamentadas por caso e acompanhadas de pendência. Método e confiança descrevem a classificação aplicada, sem substituir a revisão humana.
- **Camada agêntica:** subagente consultivo implementado em `src/agent/consultant.py`, operando sobre os CSVs e manifestos oficiais com guardrails estritos contra aprovação autônoma de exceções ou operações financeiras externas.
- **Lacunas externas:** Atlas (`CADASTRO_PENDENTE`), conflitos de ID (`DUPLICIDADE_CONFLITANTE`) e fontes ausentes/inválidas (`cobertura_fontes`) possuem bloqueio conservador e rastreável implementado. Custos da adquirência e agenda detalhada de recebíveis permanecem fora do escopo do case.

## Lacunas que permanecem

- Ajustes Orbe futuros: identificação de complemento versus substituição, competência quando não declarada e procedimento para revisar período já aprovado. Para o `06`, formato igual ao `01`, caráter complementar e inclusão em setembro foram esclarecidos pelo anúncio da organização de 17/10; não são mais lacunas desse envio. O critério de completude das fontes permanece sem definição.
- Contrato/taxa vigente da Atlas: bloqueio de faturamento já definido, percentual não conhecido.
- Precedência para duplicidades futuras com valores conflitantes. O par concreto `PC-0926-0162` tem dados financeiros iguais e difere apenas na observação; não há conflito financeiro a resolver nesse caso.
- Agenda detalhada de recebíveis e custos Orbe–Tarvo/conta garantida: não necessários à comissão definida no case, mas necessários a análises financeiras adicionais.
- Contas específicas para casos bancários ambíguos e decisões sobre valores sem origem ou devolução sem motivo identificado.

Os nove estornos de agosto analisados têm vigências contratuais aplicáveis nos arquivos, conforme `nossas-duvidas.md`; não registrar falta de histórico como bloqueio desses casos. Arredondamento, valor integral da contestação e rotina operacional já receberam resposta.

## Confirmação posterior — inputs e fechamento parcial

Helena confirmou mesmas fontes e colunas como estrutura mensal esperada, com mudança de registros, lojistas e condições. Atrasos, ajustes posteriores da Orbe e alterações inesperadas de layout acontecem e devem gerar aviso. Concluir partes independentes, marcar provisórios e explicitar bloqueios/motivos. A liberação cabe a Helena; taxa/cadastro passam antes pelo comercial.

Fonte e transcrição: [nossas-duvidas.md](PROMPTS/outputs/nossas-duvidas.md), resposta fornecida pelo usuário em 17/10/2026, sem horário ou permalink. Esses comportamentos passam a ser requisitos confirmados, não novas premissas. A escolha de dependências, estados e mecanismos de reprocessamento é proposta técnica documentada em [arquitetura-stack.md](PROMPTS/outputs/arquitetura-stack.md).

## Confirmação posterior — complemento Orbe `06`

**Evidências:** anúncio da organização transcrito pelo usuário em 17/10/2026, sem permalink, e leitura do [06_orbe_ajustes_tardios_set2026.csv](https://drive.google.com/file/d/1JFUOwyEUaQK_HkYGEJ54JbWdxwIGHgEN/view). A organização informa: ajustes de setembro que ficaram fora do relatório, 14 linhas no mesmo formato do `01`, inclusão obrigatória na entrega das 18h30 e disponibilidade de Helena até 17h45.

| Situação | Confirmação ou limite | Consequência |
|---|---|---|
| Confirmado para o `06` | Complemento do `01`, de competência setembro/2026 | Reprocessar `01 + 06`; não substituir o `01` nem mover para outubro pela chegada tardia |
| Observado no arquivo | 10 estornos, 3 reversões de antecipação e 1 venda, todos em 30/09; sete lojistas | Rever comissões e propostas de notas dos lojistas afetados, com diferenças rastreáveis |
| Aplicação de regra já confirmada | Estornos Bridge remetem a 12 e 13/09, antes da nova vigência de 15/09 | Usar condições da venda original; não criar nova hipótese sobre vigência |
| Verificação técnica executada em 17/10 | 1.957 IDs únicos e não vazios, sem duplicatas; 13 referências únicas encontradas no `01`, sem outra anulação referenciada; bruto/taxa/líquido opostos exatos | Comissão e notas já apuradas no conjunto `01 + 06`: checkout `203735.34`, notas checkout `203740.84`. Sete diferenças de bandeira esclarecidas por Helena, sem pendência ou contestação |
| Desenho implementado e testado | Múltiplos arquivos Orbe, deduplicação de repetição idêntica, snapshots por execução e comparação entre versões | Testes verificam repetição sem duplicação e bloqueio integral de conflitos; resultados alterados não herdam aprovação |
| Não definido pelo anúncio | Protocolo geral de outros ajustes, conflitos, reabertura de período aprovado e completude do mês | Manter perguntas e bloqueios específicos; não extrapolar a semântica deste complemento |

As reversões são de Oxford (duas) e Maple (uma). Após a apuração, ambos mantêm checkout positivo: Oxford `13845.71` e Maple `14165.77`, com notas propostas. A nova venda é da Kiwi. Foram aplicados contratos, arredondamento por linha e anulação da comissão da antecipação referenciada; `valor_taxa` não vira base de faturamento. A regra distinta dos ajustes Ponte no mês em que aparecem permanece. O anúncio não modifica P1/P2 nem inclui a hipótese de caixa nas entregas.

### Lacunas e perguntas propostas após o `06`

A pergunta sobre as sete diferenças de bandeira foi enviada pelo usuário e respondida por Helena; resposta fornecida pelo usuário em 17/10/2026, sem horário ou permalink. Bandeira não muda a taxa; a Orbe às vezes a troca no estorno. Manter os vínculos pela referência, sem contestar nem abrir pendência apenas pela bandeira. As perguntas gerais e condicionais da tabela abaixo continuam propostas, sem envio confirmado. Conferências de arquivo são trabalho técnico; a análise do conjunto conhecido foi concluída e as lacunas futuras não a reabrem.

**Conferência concluída:** [relatório com evidências consolidadas](PROMPTS/outputs/orbe-01-06-verificacao.md). Não foram acionados os gatilhos de ID conflitante, referência ausente/ambígua ou anulação repetida descritos na tabela. Datas, ECs, modalidades, parcelas e taxas aplicadas conferem nos 13 pares; há sete diferenças de bandeira e seis variações de nome, preservadas nas evidências. Nomes diferentes com EC igual não constituem por si só conflito de identidade.

**Pergunta concreta respondida — bandeiras:** a proposta inicial de abrir pendência de qualidade/correção com a Orbe foi dispensada por Helena. O vínculo por `id_referencia` foi confirmado para os sete pares. Preservar as diferenças como evidência, sem tratá-las como pendência, bloqueio ou divergência de taxa. A orientação vale para diferença de bandeira em estorno, que não altera a taxa da Tarvo; não valida automaticamente referência incorreta ou conflito em outros campos. A pergunta e a resposta estão no relatório. Não resta dúvida específica aberta desta investigação do `06`; as lacunas gerais abaixo permanecem. A aprovação final do fechamento permanece sujeita à revisão humana de Helena.

| Prioridade e gatilho | Pergunta proposta | Efeito e tratamento enquanto não respondida |
|---|---|---|
| Futuro/condicional: mesmo `id_transacao` com conteúdo financeiro conflitante; não encontrado em `01 + 06` | Para estes IDs e campos divergentes, qual registro é válido? O novo corrige/substitui o anterior ou representa outro movimento? Qual evidência confirma o tratamento? | Bloquear apenas contribuições dependentes; não aplicar regra de “último arquivo vence”. Apresentar IDs, diferenças e impacto calculável na pergunta |
| Condicional: referência ausente/inconsistente ou anulação anterior | Para estas operações, qual é a referência correta e o alcance do estorno/reversão? Se a reversão exceder ou repetir a antecipação já anulada, qual tratamento foi autorizado? | Pedir somente dados necessários que não puderem ser recuperados das fontes; não bloquear estorno apenas por ausência da venda se houver base contratual suficiente |
| Útil para operação recorrente; sem bloqueio demonstrado deste envio | Em futuros ajustes Orbe, qual evidência informa se o arquivo complementa ou substitui outro e a qual competência pertence? Como tratar quando isso não vier declarado? | Não generalizar o `06`; sem semântica suficiente, registrar pendência em vez de somar indiscriminadamente |
| Útil antes de automatizar revisão de período aprovado | Se um ajuste chegar depois da aprovação, quem autoriza a reabertura e como tratar resultado já faturado? Qual registro documenta a decisão? | Preservar execução/aprovação anteriores; gerar revisão técnica sem emitir nota, reabrir ou aprovar automaticamente |
| Útil para declarar cobertura do fechamento | Como Helena confirma que as fontes do mês estão completas para revisão, e como registrar ressalvas quando ainda podem chegar ajustes? | Arquivo recebido não prova completude; registrar cobertura conhecida e pendências, sem inventar prazo de corte |

## Confirmação — Estornos Órfãos Sem Referência (Helena, 14h10)

> *"Em setembro isso não acontece: todas as referências do arquivo de ajustes estão no relatório. Se um dia acontecer, o ajuste entra pelo valor que veio e vira pendência para eu pedir a original à Orbe.*
> *— Helena"*

- **Confirmação e limite:** o texto recebido diz “valor que veio”, sem definir qual coluna deve virar comissão quando falta a referência. Em setembro não há esse caso no `06`. O código registra `ESTORNO_ORFAO_SEM_ORIGEM` pelo `valor_bruto` declarado, com rastro e responsável Helena, enquanto a comissão segue o cálculo contratual disponível. Não afirmar que esse ramo homologa qualquer ajuste órfão futuro ou substitui a comissão pelo bruto; a base e o alcance precisam de revisão antes de tratar um caso novo como fechado. Nenhuma comunicação externa é enviada automaticamente.

## Padrão Ouro de Auditabilidade e Rastro (Organização Barte, 14h11)

> *"O mínimo é o rastro.csv no formato das instruções (id_saida; arquivo_origem; ref_origem; valor): toda comissão e toda nota com um id_saida, e a soma de valor por id_saida batendo com o número reportado.*
> *Para ficar auditável de verdade, ajuda ter:*
> *1. rastro também das divergências e da nota da Ponte;*
> *2. um registro de cada execução: quais arquivos entraram, quantas linhas de cada, data e hora;*
> *3. em cada linha, a regra aplicada (taxa contratada usada, isenção, estorno pela venda original).*
> *Quem abrir tem que conseguir refazer qualquer número sem perguntar para vocês.*
> *— Organização"*

### Implementação do Padrão Ouro na Solução:
1. **Rastro Universal Expandido (`rastro.csv`):** Mantém as 4 colunas canônicas obrigatórias (`id_saida; arquivo_origem; ref_origem; valor`) e adiciona as colunas de alta auditabilidade: `regra_aplicada; taxa_contratada_aplicada; detalhe_calculo`.
2. **Rastro Integral:** Liga comissões (`COM-XXXX`), notas propostas (`NF-XXXX`), divergências (`DIV-XXXX`), lançamentos (`LAN-XXXX`) e pendências (`PEN-XXXX`) às contribuições de origem. Um resultado pode ter várias contribuições, incluindo as 118 transações da pendência Casa (`PEN-0058 = R$ 15.396,77`).
3. **Manifesto de Execução e Histórico (`auditoria_execucao.json`, `auditoria_execucao.md` e `historico_execucoes.json`):** Gerados automaticamente a cada rodada, registrando `id_execucao`, `versao_regras`, timestamp ISO, hashes SHA-256 individuais e combinados de entrada/saída, estado de cobertura por domínio (`cobertura_fontes`), separação entre `estado_tecnico` e `status_aprovacao`, comparação rastreável com a execução anterior (`comparacao_execucao_anterior`) e prova real matemática centavo a centavo.

## Regras confirmadas e escolhas operacionais da equipe — revisão de 17/10

### P4 — Vínculos cadastrais confirmados pelo financeiro
- **Contexto:** Kiwi Experience, Horizonte Viagens e Novo Horizonte Intercâmbio constavam sem código de estabelecimento (`cod_estabelecimento`) explícito na planilha cadastral inicial.
- **Tratamento confirmado:** EC `1043300981` = Novo Horizonte Intercâmbio; EC `1043396662` = Horizonte Viagens; EC `1038867654` = Kiwi Experience. Os CNPJs e contratos são os das respectivas linhas vigentes. A autoridade para esses vínculos é a resposta do financeiro registrada no item 5 de `PROMPTS/outputs/duvidas-slack.md`; semelhança de nome ou coincidência de taxa não confirma identidade nem contrato.

### P5 — Truncamento da Orbe vs Arredondamento Tarvo (`ROUND_HALF_UP`)
- **Contexto:** A adquirente Orbe trunca a coluna `valor_taxa` no segundo dígito decimal, enquanto o contrato e a regra de Helena exigem arredondamento canônico por operação (`ROUND_HALF_UP`).
- **Limite da evidência:** não se mantém a contagem anterior de 929 linhas/R$ 8,57 como resultado validado desta revisão. Diferença entre taxa observada e comissão contratual também pode ter outras causas; o truncamento deve ser isolado por operação antes de ser quantificado.
- **Decisão:** Conforme orientação formal, diferença decorrente puramente de truncamento não constitui divergência contratual de taxa e não é cobrada do lojista nem contestada à adquirente.

### P6 — Classificação da Folha de Salários de Agosto Paga em Setembro (`2.1.04.001`)
- **Contexto:** Lançamento no Banco Aurora em 04/09/2026 (linha física L15) no valor de R$ -184.732,18 ("PAGTO SALARIOS - FOLHA 08/2026").
- **Fato confirmado e proposta contábil:** a folha pertence a agosto e já estava provisionada. O pagamento de 04/09 baixa o passivo, sem repetir a despesa em setembro. A conta proposta pela equipe é `2.1.04.001` (Salários a Pagar - Passivo Circulante).

### P7 — Trânsito Bancário Aurora–Meridiano em 30/09 (R$ 300.000,00)
- **Contexto:** O Banco Aurora registra quatro transferências entre contas para o Banco Meridiano em setembro. Três compensaram em setembro (02/09 R$ 350k, 10/09 R$ 100k, 17/09 R$ 150k).
- **Tratamento:** A quarta transferência, de R$ 300.000,00 em 30/09 (L92), não possui crédito correspondente no extrato do Meridiano em setembro. Classificada na conta `1.1.09.001` (Valores em Trânsito Bancário) e enviada como pendência de conciliação para Caio acompanhar a compensação no extrato de outubro.

### P8 — Deduplicação Estrita de Cópias Idênticas vs. Bloqueio Integral de Conflitos (`DUPLICIDADE_CONFLITANTE`)
- **Contexto:** Tanto nos relatórios da Orbe (`id_transacao`) quanto nos relatórios da Ponte Câmbio (`num_operacao`), podem surgir registros repetidos sob o mesmo identificador.
- **Tratamento:** Os motores realizam pré-agrupamento por identificador comparando todos os campos operacionais e financeiros relevantes:
  1. **Cópias Efetivamente Idênticas:** Quando todas as ocorrências compartilham exatamente os mesmos valores operacionais e financeiros (ex: `PC-0926-0162` na Ponte, ou reprocessamento idêntico de linha Orbe), a operação é contabilizada uma única vez e a evidência das múltiplas ocorrências é preservada no `rastro.csv` (e em `OPERACAO_DUPLICADA` na Ponte).
  2. **Duplicidades Conflitantes:** Quando um mesmo `id_transacao` ou `num_operacao` aparece com valores divergentes em campo relevante, nenhuma ocorrência é escolhida automaticamente. Todas as versões daquele ID são bloqueadas das comissões, divergências e notas, com versões detalhadas no rastro para decisão de Helena. A Orbe usa o tipo `DUPLICIDADE_CONFLITANTE`; a Ponte usa `OPERACAO_DUPLICADA` com motivo explícito de conflito e bloqueio integral.



