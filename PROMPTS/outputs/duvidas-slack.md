# Dúvidas e respostas do Slack — Tarvo

Leitura inicial realizada em **17/10/2026**, pelo Slack no navegador, no canal [#duvidas-hackathon-ai](https://app.slack.com/client/T0CA2KVNG4U/C0CA0S5D37B). A busca sem termos adicionais, restrita ao canal, retornou **36 mensagens em duas páginas**, incluindo respostas nas conversas. Todas foram lidas com os textos expandidos. O histórico inicial encontrado vai de 16/10 às 19h46 a 17/10 às 8h43. Mensagens administrativas de entrada de membro e renomeação do canal não contêm dúvidas e foram omitidas. Uma leitura posterior incluiu atualizações até **17/10 às 9h49** e o HTML “Do Cartão ao Caixa”; os esclarecimentos relevantes às nossas dúvidas foram incorporados abaixo, com suas fontes.

As perguntas abaixo são paráfrases organizadas por publicação, preservando suas partes relevantes. As respostas de `manuel.freitas` assinadas por **Helena, financeiro da Tarvo**, são tratadas como confirmação do cliente. Propostas e números de participantes são identificados como tais; silêncio não significa validação. As regras logísticas são respostas da organização. Este registro retrata o conteúdo disponível no momento da consulta.

## 1. Onde enviar perguntas ao cliente?

**Autor/data:** Alex Chequer, 16/10, 19h57.

**Pergunta:** O documento indica #tarvo-financeiro, ainda inexistente. Podemos enviar dúvidas neste canal ou devemos esperar?

**Resposta útil:** Podem enviar aqui, indicando na conversa se a dúvida é para a Tarvo ou sobre o hackathon.

[Pergunta](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792191465288839) · [Resposta, 19h59](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792191557825119)

## 2. Qual é a base da comissão de checkout e como tratar diferença?

**Autor/data:** Alex Chequer / Fox AI, 16/10, 20h01, dentro da conversa anterior.

**Perguntas:** Usar `valor_taxa` cobrado pela Orbe ou bruto × taxa contratada? Qual vai para a nota? A diferença é devolvida ao lojista?

**Resposta útil:** Faturar bruto × taxa contratada da planilha, linha por linha. `valor_taxa` mostra o que a Orbe cobrou e pode divergir do contrato. A nota usa a comissão contratada. Taxa aplicada diferente da contratada é divergência. Quando a Orbe cobra a mais, a diferença volta ao lojista e Helena cobra a Orbe, após analisar cada caso com transação e valor. **Não é automático.**

[Pergunta](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792191694474319) · [Resposta, 20h05](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792191952289259)

## 3. Como estornos afetam a comissão e a competência?

**Autor/data:** Nader Taha / MN AI, 16/10, 20h04.

**Perguntas:** O estorno devolve a taxa e abate a comissão? Venda de agosto estornada em setembro entra em setembro, volta para agosto ou fica fora? Exemplo: TX88444848, Oxford Prep, venda de 22/08 estornada em 01/09.

**Resposta útil:** Devolve a taxa ao lojista e reduz a comissão no mês do estorno. O exemplo afeta setembro; agosto não é reaberto. Usar a taxa contratada vigente na data da venda original, nesse caso 22/08.

[Pergunta](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792191877776469) · [Resposta, 20h06](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792192019611209)

## 4. A entrega pode ter vários repositórios?

**Autor/data:** MN AI - murilo godoy, 16/10, 20h08.

**Pergunta:** Podemos criar vários repositórios ou a entrega deve ser única?

**Resposta útil da organização:** A entrega é **um repositório por time**, enviado por e-mail até 18h30; apenas esse link é avaliado. Durante o trabalho podem existir outros repositórios. O entregue deve conter código, `saida/`, `PROMPTS/`, `HIPOTESES.md` e `README.md` para executar do zero. Backend e interface ficam em pastas do mesmo repositório. Partes em plataformas online entram como links no README com instruções de teste. Mudanças após 18h30 não contam. A resposta não explicita a data desse horário; não o reinterpretar como prazo futuro.

[Pergunta](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792192104351419) · [Resposta, 20h13](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792192415046529)

## 5. Como identificar os ECs ausentes e faturar a Atlas?

**Autor/data:** Alex Chequer / Fox AI, 16/10, 20h16.

**Perguntas:** Quatro ECs não constam na aba vigente: 1043300981, 1043396662, 1076801732 e 1038867654. Quais são seus CNPJs e taxas? As duas Horizonte e a Kiwi correspondem às linhas sem EC? Atlas aparece apenas na aba de 2025: continua ativa?

**Resposta útil:**

- `1043300981`: Novo Horizonte Intercâmbio, linha “Novo Horizonte Intercambio”.
- `1043396662`: Horizonte Viagens e Turismo, linha “Horizonte Viagens”. As duas Horizonte são empresas diferentes.
- `1038867654`: Kiwi Experience, linha “Kiwi Experience”.
- CNPJs e taxas dessas três devem ser obtidos nas respectivas linhas da aba vigente; a resposta não transcreve os números.
- Atlas começou a transacionar em 10/09. Helena não tem contrato assinado vigente e não sabe qual taxa vale. **Não faturar até o comercial confirmar.** A presença na aba de 2025 não confirma a taxa atual.

[Pergunta](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792192601377449) · [Resposta, 20h24](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792193059964329)

## 6. Quais são as regras para montar notas fiscais?

**Autor/data:** Nader Taha / MN AI, 16/10, 20h26.

**Perguntas:** Checkout gera uma nota por lojista/mês com vendas menos estornos à taxa original? Antecipação entra na mesma nota? Reversão anula a original? Saldo zero/negativo não emite e passa para o mês seguinte? Na remessa, tomador é Ponte ou cada lojista? Existe discriminação padrão?

**Resposta útil:**

- Checkout: uma nota por lojista por mês, pela comissão contratada. Estorno abate pela taxa da venda original. Antecipação integra a mesma nota; reversão só anula a taxa da antecipação referenciada.
- Zero ou negativo: não emitir nota. Negativo não passa automaticamente ao próximo mês; deixar pendência para Helena tratar com o lojista.
- Remessa: uma única nota à **Ponte Câmbio**, tomadora e pagadora, pelo total da participação mensal. Não há nota de remessa por lojista.
- Sem texto padrão obrigatório: serviço e competência bastam.

[Pergunta](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792193219408319) · [Resposta, 20h47](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792194465573829)

## 7. Qual é a base da remessa e como tratar suas exceções?

**Autor/data:** MN AI - murilo godoy, 16/10, 20h30.

**Perguntas:** A comissão é 50% do “Spread R$” realizado ou recalculada pela taxa contratada? Cobrança acima do contrato, como Mundo Aberto, é divergência? Quanto vale “padrão” ou vazio? Como tratar spread negativo com trava D-1, operação repetida/reprocessada, compliance com ressalva e contratação em setembro com liquidação em outubro?

**Resposta útil:**

- Comissão: **50% do campo “Spread R$” realizado**.
- Mundo Aberto negociou 1,20% em julho; a Ponte já deveria aplicar. Cobrança superior é divergência e Helena contesta com a Ponte.
- Taxa vazia ou “padrão”: 1,5% sobre a PTAX de referência.
- Os spreads negativos questionados são rejeitados: a trava contratual vale duas horas e essas operações ultrapassaram o prazo. Ficam fora da comissão e da nota, com contestação por Helena. A explicação se refere a esses casos.
- Número da operação é único: repetição não são duas operações legítimas. A resposta não define precedência entre linhas conflitantes.
- “APROVADO C/ RESSALVA” não altera o tratamento para a Tarvo.
- Competência: data de contratação.
- Para situações fora dessas regras, Helena pede proposta de tratamento com justificativa.

[Pergunta](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792193429257939) · [Resposta, 20h48](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792194515838639)

## 8. Rota Global, Casa do Estudante e movimentos bancários especiais

**Autor/data:** Lucca Landeiro, 16/10, 20h36.

**Perguntas:**

1. O aumento de 0,50 p.p. aplicado pela Orbe à Rota Global desde 12/09 foi reajuste contratual ou divergência?
2. Há condição especial para Casa do Estudante indicada nos comentários da planilha?
3. Folha e tributos de agosto pagos em setembro, além da comissão de agosto da Ponte recebida em setembro, pertencem a qual competência?
4. Qual a origem/tratamento do Pix de R$ 7.350 sem identificação, da devolução Mundo Aberto de R$ 12.400 e da transferência de R$ 300 mil ao Meridiano sem crédito em setembro?

**Resposta útil:**

1. Não houve mudança no contrato da Rota em 2026.
2. Casa do Estudante tem MDR e antecipação zerados de setembro a dezembro por acordo comercial para retenção. Remessa segue normal. A Orbe não foi avisada e cobrou; Helena devolve ao lojista com o comercial. **Esclarecimento posterior, 17/10 às 9h44:** a cobrança seguiu a planilha e não deve gerar cobrança contra a Orbe pela isenção não comunicada. Separar das divergências contratuais, com o valor a devolver ao lojista, como pendência de Helena com o comercial. [Resposta específica](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792241097683849).
3. Folha, ISS, INSS, FGTS e DARFs são de agosto e já estavam provisionados. Recebimento Ponte de 04/09 é spread de agosto já registrado como comissão a receber. Helena pede aos participantes que proponham os lançamentos.
4. Origem do Pix de R$ 7.350 desconhecida: não é receita até identificação. A devolução é repasse que voltou; motivo desconhecido. A transferência saiu do Aurora em 30/09 e entra no Meridiano em 01/10. O tratamento contábil deve ser proposto pelos participantes.

[Pergunta](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792193803331999) · [Resposta, 20h49](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792194576391779)

## 9. Divergência de remessa: valor cheio ou metade? Qual tolerância?

**Autor/data:** Alex Chequer / Fox AI, 16/10, 20h52.

**Perguntas:** A divergência é `(spread aplicado − contratado) × PTAX × valor em moeda estrangeira`, no valor cheio pago a mais ou só 50%? Podemos ignorar diferenças abaixo de 0,01 p.p., já que aparecem oscilações de cerca de ±0,002 p.p.? Foram apresentados R$ 29,56 para PC-0926-0011 e R$ 1.418,85 em 23 operações da Mundo Aberto.

**Resposta útil:** Contestar **o valor cheio** pago a mais pela Mundo Aberto. Os 50% descrevem apenas a divisão da Ponte com a Tarvo. A tolerância é escolha dos participantes, desde que escrita e justificada: evitar alarmes de centavos sem deixar diferenças reais passarem. A resposta **não fixa nem homologa explicitamente 0,01 p.p.**, nem valida individualmente os números apresentados.

[Pergunta](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792194771073879) · [Resposta, 20h58](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792195101083859)

## 10. Proposta de lançamentos: está diferente da rotina da Tarvo?

**Autor/data:** Lucca Landeiro, 16/10, 21h06, na conversa do item 8.

**Pergunta/proposta:** Baixar passivos provisionados de folha/tributos; baixar comissões a receber no recebimento Ponte; registrar Pix desconhecido em créditos não identificados; devolver o repasse retornado a repasses a lojistas a pagar; manter a transferência de R$ 300 mil em conta de trânsito até 01/10. Pede aviso se algo diferir da prática da Tarvo.

**Resposta útil:** Não foi encontrada resposta específica validando essa proposta. A resposta posterior do item 12 confirma a lógica de baixar saldos já registrados, mas **não aprova nominalmente todas as contas sugeridas por Lucca**.

[Publicação](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792195576794659)

## 11. Arredondamento e cálculo das divergências

**Autor/data:** Helio Henrique / Fox AI, 16/10, 21h07.

**Perguntas:** A Orbe parece truncar centavos. A Tarvo deve truncar ou arredondar? Como tratar negativos e meio centavo? Calcular por linha ou pelo total? Divergência é `valor_taxa − comissão contratada` ou `bruto × (taxa aplicada − contratada)`? Nas remessas, arredondar os 50% por operação ou depois da soma? Exemplo: metade de R$ 262,01.

**Resposta útil:** A Orbe trunca; a Tarvo **arredonda para centavos**, com meio centavo para cima em magnitude: `-0,005 → -0,01`. Arredondar cada linha e depois somar. Divergência decorre da taxa aplicada diferente da contratada; centavo gerado pelo truncamento não é divergência. Valor da divergência de checkout: `bruto × (taxa aplicada − contratada)`. Na remessa, calcular e arredondar por operação com a mesma regra: metade de R$ 262,01 resulta em R$ 131,01.

[Pergunta](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792195651974369) · [Resposta, 21h13](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792196013836169)

## 12. O que representa conta_codigo na classificação dos extratos?

**Autor/data:** Helio Henrique / Fox AI, 16/10, 21h08.

**Perguntas:** Usar contrapartida bancária, baixando obrigações/recebíveis, ou natureza de receita/despesa? Exemplos: Salários a pagar versus despesa salarial; comissão a receber versus receita de intermediação. Podemos pressupor apropriação anterior de salários, tributos, fornecedores e comissões? E se o extrato não disser?

**Resposta útil:** Usar a **contrapartida do movimento bancário**. Valor já registrado é baixado, sem reconhecer receita/despesa novamente. Folha, tributos de agosto e Ponte de 04/09 já estavam registrados. Além desses, nada estava provisionado: tarifas, aluguel, cloud, assinaturas e serviços entram como despesa do mês. Quando o extrato não esclarecer, declarar a premissa em `HIPOTESES.md` e seguir.

[Pergunta](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792195685607029) · [Resposta, 21h14](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792196067326279)

## 13. O excesso cobrado da Mundo Aberto integra a comissão e a nota?

**Autor/data:** Theo Garcia, 16/10, 21h16.

**Pergunta:** Como 50% do spread realizado inclui o excesso de 1,50% sobre 1,20% contratado, essa metade entra em setembro ou fica fora até a contestação? Propõe faturar realizado e deixar ajuste pendente.

**Resposta útil:** **Entra em setembro**, pelo realizado. Contestação é processo separado. Se a Ponte devolver a diferença à Mundo Aberto, a metade da Tarvo será retirada no mês do ajuste. Deixar pendência para Helena está correto.

[Pergunta](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792196203351619) · [Resposta, 21h45](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792197913743739)

## 14. Validar valores de remessa e prever o TED de outubro?

**Autor/data:** Lucca Landeiro, 16/10, 21h56.

**Perguntas/proposta:** Excluir quatro spreads negativos; listar R$ 3.565,98 de divergência e R$ 917,03 de impacto na participação; contar PC-0926-0162 uma vez; aponta duplicidade de R$ 410,94 no repasse e propõe nota de R$ 39.543,45. Prevê TED cerca de R$ 506 menor e pede validação.

**Resposta útil:** Helena **não valida os números**; os participantes devem fechar e demonstrar o rastro. Como a contestação ainda não foi aberta, ela não sabe como a Ponte pagará e não se deve pressupor desconto no repasse. Conferir o TED quando cair é pendência de Helena. Todos os valores acima são da proposta de Lucca, não resultados homologados.

[Pergunta](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792198608227769) · [Resposta, 22h33](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792200816394409)

## 15. O prazo de contestação venceu? A duplicata também deve ser contestada?

**Autor/data:** João Pedro Lucena / INSPER AI, 16/10, 22h04.

**Perguntas:** O e-mail de 02/10 dá cinco dias úteis, aparentemente até 09/10. Mundo Aberto e negativos já foram contestados ou houve extensão? Prazo vencido mudaria o fechamento? Duplicata exige contestação ou basta contar uma vez?

**Resposta útil:** Helena ainda **não contestou nada**. Para o case, considerar dentro do prazo, com fechamento nesta semana. Manter pendência com valores e operações para ela enviar à Ponte. Contar a duplicata uma vez e incluí-la na lista de correções do relatório. Não há confirmação de uma extensão formal específica: há uma orientação explícita para o tratamento no case.

[Pergunta](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792199088314709) · [Resposta, 22h34](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792200848816529)

## 16. Qual o fluxo Orbe–Tarvo e por que Aurora fica negativo?

**Autor/data:** Gustavo / INSPER AI, 16/10, 22h09.

**Perguntas:** Aurora chega a saldo negativo de R$ 2.289.532,94; há R$ 3.557.246,29 de créditos Orbe versus R$ 7.264.348,20 líquidos no relatório. Tudo entra no Aurora ou existem outras contas/pagamentos diretos? Como antecipações, reversões e prazos de liquidação afetam a conciliação setembro/outubro?

**Resposta útil:** A Orbe deposita **tudo no Aurora e não paga lojistas diretamente**. Débito e Pix entram no dia seguinte. Crédito e parcelado entram nos meses seguintes, conforme parcelas. O banco de setembro não precisa coincidir com o líquido do relatório de setembro. O saldo negativo decorre da **conta garantida do Aurora**, usada para pagar lojistas antes da liquidação Orbe. Neste fechamento, classificar os créditos da Orbe; conciliação parcela por parcela fica para quando houver agenda de recebíveis. A resposta não fornece essa agenda nem detalha todos os eventos de antecipação/reversão no caixa.

[Pergunta](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792199352656099) · [Resposta, 22h34](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792200869514179)

## 17. A comissão de checkout desconta custo Orbe? Inclui estornos e antecipações?

**Autor/data:** as.pereira.leite / Fox AI, 16/10, 22h20.

**Perguntas:** A comissão é a taxa inteira ou menos custo da Orbe? Os 59 estornos, inclusive nove de vendas de agosto, reduzem setembro? As 38 antecipações entram e as seis reversões abatem?

**Resposta útil:** É a taxa inteira **pela taxa contratada**, sem desconto de custo Orbe; não usar `valor_taxa` como base. Estornos de agosto também reduzem setembro. Antecipações entram na mesma nota e reversões abatem. Helena remete às respostas anteriores. Isso confirma a base do case, mas não descreve uma tabela comercial de custos cobrados pela Orbe à Tarvo.

[Pergunta](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792200039150939) · [Resposta, 22h34](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792200888817559)

## 18. Negativos entram na lista de divergências ou só na contestação?

**Autor/data:** MN AI - murilo godoy, 17/10, 8h43, mensagem editada.

**Pergunta:** PC-0926-0210, -0326, -0491 e -0545 já ficam fora da comissão e da nota. Devem também integrar divergências de taxa, já que têm taxas negativas contra contrato positivo, ou apenas pendência de contestação? O participante propõe só pendência porque não houve cobrança a maior ao lojista.

**Resposta útil, 17/10 às 9h44:** os negativos são pendências de contestação, pois o prejuízo é da Tarvo com a Ponte e não cobrança a maior ao lojista. Podem também aparecer nas divergências, desde que fique clara sua natureza distinta. Essa inclusão não é obrigatória; permanecem fora da comissão e da nota. A resposta substitui o registro anterior de dúvida ainda em aberto.

[Pergunta](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792237413528249) · [Resposta, 9h44](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792241055140729)

## Atualizações consultadas em 17/10 até 9h49

### Casa do Estudante: devolução por isenção não comunicada

Helena distinguiu esse caso das divergências contratuais comuns: a Orbe cobrou conforme a planilha e não foi informada da isenção. Não há o que cobrar da Orbe por essa isenção. Registrar valor separado das divergências contratuais, como devolução ao lojista pendente com Helena e comercial. A taxa do estorno de venda de 21/08 continua sendo a vigente na venda original, anterior à isenção.

[Resposta para Mateus, 9h44](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792241097683849)

### Aprovação de regras e cobertura de férias

Em resposta à MN AI, Helena confirmou: o comercial aprova taxas e condições comerciais; ela registra. Regras de como fechar são aprovadas por ela. Hoje ninguém fecha o mês durante suas férias. Registrar quem aprovou e quando foi considerado adequado. Isso não descreve a composição completa da equipe nem quem aprova cada resultado operacional.

[Pergunta, 9h35](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792240517567649) · [Resposta, 9h49](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792241342797889)

### Material de apoio: Do Cartão ao Caixa

O HTML compartilhado por Leandro Kauffmann às 9h15 foi lido integralmente. Explica os participantes do arranjo, autorização versus liquidação e o MDR descontado de cada venda do lojista. Ressalva que não define as regras específicas de cobrança, faturamento e exceções da Tarvo; não substitui as confirmações do financeiro.

[Publicação, 9h15](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792239350495969) · [HTML](https://bartehackathonai.slack.com/files/U0C9HJFNW4X/F0C9W3T96VB/do_cart__o_ao_caixa.html)

## Esclarecimentos posteriores ao contexto do AGENTS.md

O canal contém respostas que complementam lacunas do resumo local: regra completa de arredondamento (item 11), contrapartida e provisões na classificação (12), tratamento do excesso de spread no realizado (13), orientação de prazo para contestação (15) e fluxo de liquidação/conta garantida (16). A tolerância de remessa recebeu resposta (9), mas seu limite numérico foi delegado aos participantes. Esses esclarecimentos não resolvem a precedência de duplicatas conflitantes, a agenda detalhada de recebíveis ou o procedimento fiscal completo.
