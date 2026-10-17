# Nossas dúvidas × Slack, documento do case, data pack e material de apoio

## Variação dos inputs entre meses — respondida

**Situação:** resposta de Helena recebida e fornecida pelo usuário nesta conversa em 17/10/2026. Horário e permalink não informados; não houve nova leitura nem envio ao Slack pelo agente. O registro anterior era um rascunho sem envio registrado; a resposta abaixo o complementa sem inventar metadados do envio.

**Texto preparado:**

[financeiro] Turma do Barulho: para entender como o fechamento muda de um mês para outro, em outubro podemos receber arquivos com colunas, abas ou formatos diferentes, novas fontes, arquivos ausentes ou correções de arquivos já enviados? Ou a estrutura permanece igual e mudam apenas os registros, lojistas e condições comerciais?

Quando faltar uma fonte ou chegar uma informação nova sem regra definida, vocês esperam que o fechamento inteiro aguarde ou que as partes independentes sejam concluídas, deixando explícitos os resultados provisórios, os bloqueios e as pendências? Quem decide quando esses casos podem ser liberados?

**Contexto:** o LEIA-ME prevê arquivos novos no mesmo formato em outubro. Helena confirmou a estrutura mensal esperada e esclareceu as exceções operacionais.

**Resposta recebida (transcrição):**

> [Financeiro] Resposta para Turma do Barulho
> A estrutura é a mesma todo mês: mesmas fontes, mesmas colunas. Mudam os registros, os lojistas e as condições. Mas na prática acontece de arquivo chegar atrasado, de a Orbe mandar ajuste depois do relatório, e já teve parceiro mudando o layout sem avisar. Prefiro que a solução avise a que quebre sem ninguém perceber.
> Quando falta alguma coisa, eu não seguro o mês inteiro. Fecha o que não depende daquilo, marca o que é provisório e deixa claro o que está bloqueado e por quê. Quem libera sou eu. Se for taxa ou cadastro, o comercial decide antes.
> — Helena

**Confirmado:** mesmas fontes/colunas como contrato esperado; mudanças de registros, lojistas e condições; possibilidade de atraso, ajuste posterior da Orbe e mudança inesperada de layout. Continuar partes independentes, identificar provisórios e bloqueios com motivo e avisar sobre problemas. Helena libera; taxa/cadastro exigem decisão prévia do comercial.

**Limites da resposta:** não define formato de ajustes Orbe, se são incrementais ou substitutivos, nem autoriza reabrir automaticamente períodos aprovados. Também não exige adaptação automática a layout desconhecido. O desenho técnico de dependências, alertas e versões está em `arquitetura-stack.md`.

## Situação atual — resposta da Tarvo às seis perguntas

As seis perguntas enviadas pela Turma do Barulho foram respondidas por Helena. O texto foi fornecido pelo usuário nesta conversa em 17/10/2026; não houve nova leitura do Slack para esta atualização, e não foi fornecido o horário ou permalink da resposta. [Mensagem enviada às 10h32](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792243935921379).

| Pergunta | Resposta confirmada |
|---|---|
| 1. Sequência, execução, conferência e registro | Baixar Orbe, e-mail Ponte e extratos → casar Orbe com taxas e apurar checkout por lojista → apurar remessa → classificar extratos no ERP → montar notas. Bia e Caio executam; Helena confere e aprova. A conclusão é marcada com “ok” e data numa aba de controle da mesma planilha. |
| 2. Equipe e duração | Bia cuida do checkout e da planilha de taxas; Caio, de bancos e remessas; Helena revisa, decide exceções e fala com comercial, Orbe e Ponte. Checkout: cerca de 3 dias, metade manual para casar nomes/EC/CNPJ e metade retrabalho por planilha desatualizada. Remessa: cerca de 2 dias, principalmente espera por Ponte e comercial. Extratos: cerca de 2 dias, quase tudo manual, linha por linha. Último dia: notas e revisão de Helena. |
| 3. Regras tácitas | Quase tudo já descoberto no canal estava concentrado em Helena: condições combinadas pelo comercial, correspondência entre nomes/EC/CNPJ, aceitação ou contestação da Ponte e provisões anteriores. São usadas na comissão, remessa e classificação. Sua ausência impede aplicar essas regras. A resposta identifica os grupos de conhecimento; não fornece uma contagem exaustiva de regras. |
| 4. Desconto e nota | A Orbe liquida o líquido: a taxa é descontada quando ela paga. O lojista vê o desconto no extrato de repasse enviado pela Tarvo. A nota documenta a taxa já descontada e não gera nova cobrança. Cobrança a maior reduz o valor recebido e exige devolução, observada a exceção da Casa do Estudante já registrada. |
| 5. Repasse | Pela regra, a Tarvo repassa duas vezes por mês, perto dos dias 10 e 24, o que a Orbe já liquidou. A condição consta do contrato de adesão de cada lojista, guardado em pasta do comercial. Helena esclareceu depois que Bia às vezes paga antes da liquidação, sob pressão do lojista, usando a conta garantida. Essa exceção não está documentada e não tem limite definido. “Perto” não define dias exatos nem regra de feriados. |
| 6. Contestação Ponte | A Ponte responde por e-mail e envia o ajuste como crédito ou débito no relatório do mês seguinte. Helena confere e registra no fechamento do mês em que o ajuste aparece. |

**Contradição esclarecida por Helena:** repassar o já liquidado é a regra. Na prática, quando um lojista pressiona, Bia às vezes paga antes de a Orbe liquidar, usando a conta garantida. Essa exceção não está escrita e não tem limite definido; depende de quem executa. Portanto, as respostas anteriores descreviam a regra e uma exceção operacional, sem que uma revogasse a outra. A falta de documentação e de limite é um fato confirmado sobre a operação, não uma regra a ser inventada pela solução. Não equiparar automaticamente esse adiantamento de caixa às operações de antecipação tarifadas no CSV Orbe. A conciliação parcela por parcela continua fora do escopo já delimitado.

**Proveniência do esclarecimento:** resposta “[Financeiro] Resposta para Turma do Barulho (repasse)”, copiada pelo usuário nesta conversa em 17/10/2026, sem horário ou permalink informado. Não foi feita nova consulta ou postagem no Slack nesta atualização.

As perguntas gerais abaixo ficam como histórico da investigação, não como lista pendente para reenvio. O maior consumo de tempo e o retorno da contestação, antes não respondidos, agora estão esclarecidos. Os custos Orbe–Tarvo continuam sem valores informados, mas não são necessários para a comissão definida no case. Nenhuma nova mensagem foi enviada ao Slack nesta atualização.

## Histórico da análise anterior à resposta da Turma do Barulho

Comparação feita em **17/10/2026**, inicialmente com as 36 mensagens retornadas pela busca do [canal de dúvidas](https://app.slack.com/client/T0CA2KVNG4U/C0CA0S5D37B), incluindo respostas nas conversas, e atualizada com as mensagens lidas até **9h49** e o HTML “Do Cartão ao Caixa”. O registro das perguntas e respostas úteis está em [duvidas-slack.md](duvidas-slack.md).

**Critério:** confirmado = resposta explícita suficiente para aquele ponto; ambíguo = há esclarecimento parcial, mas falta uma distinção ou detalhe para resolver a pergunta inteira; não respondido = não foi encontrada resposta direta. Uma pergunta composta pode ter partes em categorias diferentes. Propostas de participantes não são tratadas como confirmação do cliente.

**Fontes da revisão:** [instruções do case](https://docs.google.com/document/d/1GwHs0lgLWXdw-jIrPyYAxyJ_xEJJxViE/edit), os sete arquivos do [Tarvo_Data_Pack_set2026.zip](C:/Users/marcus/Downloads/Tarvo_Data_Pack_set2026.zip), incluindo o XLSX anexado ao e-mail, o [HTML “Do Cartão ao Caixa”](https://bartehackathonai.slack.com/files/U0C9HJFNW4X/F0C9W3T96VB/do_cart__o_ao_caixa.html) e as respostas do Slack lidas até 9h49. A análise distingue resultados exigidos da solução, explicações gerais do arranjo, evidências dos arquivos e rotina atual do financeiro. A lista final contém apenas as lacunas restantes; a antiga pergunta 7 foi retirada porque recebeu resposta.

## Confirmado

### O que fazem quando o cliente reclama de taxa cobrada a mais?

Helena analisa os casos individualmente, com identificação da transação e valor. Em divergências contratuais comuns com cobrança a maior, trata a devolução ao lojista e a cobrança à Orbe. **A devolução não é automática.**

**Exceção confirmada às 9h44 — Casa do Estudante:** a Orbe cobrou conforme a planilha porque não foi avisada da isenção. **Não há valor a cobrar da Orbe por essa isenção não comunicada.** Registrar separadamente das divergências contratuais, com o valor a devolver ao lojista, como pendência de Helena com o comercial. Isso não altera o acordo de MDR e antecipação zerados de setembro a dezembro nem aplica a isenção retroativamente às vendas de agosto.

O canal confirma a decisão e os responsáveis, mas não detalha prazo, meio de devolução ou fluxo de atendimento da reclamação.

Fontes: [checkout e devolução](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792191952289259), [isenção da Casa do Estudante](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792194576391779), [tratamento específico confirmado às 9h44](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792241097683849).

### O que acontece com o relatório que contém spread negativo? Alguém é acionado?

Para os negativos questionados, a trava de taxa vale duas horas e as operações passaram desse prazo. **São excluídos da comissão e da nota e ficam como contestação para Helena encaminhar à Ponte.** Ela ainda não havia aberto a contestação: precisa receber a lista com operações e valores. Para o case, orientou considerar o prazo de contestação em aberto. Duplicata também deve constar na lista para correção, sendo contada uma única vez no fechamento.

**Classificação confirmada às 9h44:** esses negativos são pendências de contestação, pois o prejuízo é da Tarvo com a Ponte e não cobrança a maior ao lojista. Podem também aparecer nas divergências, desde que sua natureza distinta fique explícita; essa inclusão não é obrigatória. A antiga pergunta 7 está respondida. A explicação se refere aos quatro casos questionados, sem estabelecer rejeição universal para qualquer spread negativo futuro.

Fontes: [negativos e exceções](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792194515838639), [responsável e situação da contestação](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792200848816529), [classificação confirmada às 9h44](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792241055140729).

### Quem aprova regras e quem cobre as férias de Helena?

Às 9h49, Helena confirmou: o comercial aprova taxas e condições comerciais, e ela as registra. As regras de como fechar são aprovadas por ela. **Hoje ninguém fecha o mês durante suas férias.** O registro de quem aprovou cada regra e quando foi considerado adequado. Isso resolve a dúvida sobre cobertura atual e parte das aprovações, mas não descreve todas as funções da equipe ou o processo completo.

Fonte: [resposta sobre aprovação e férias](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792241342797889).

## Revisão dos sete pontos inicialmente ambíguos

### “Quais etapas vocês têm no processo de fechamento?”

**O que já sabemos:** há regras para apurar checkout, validar taxas/cadastros, tratar estornos e antecipações, apurar remessa, registrar divergências e pendências, preparar notas e classificar extratos. Helena esclareceu que a conciliação Orbe/banco parcela por parcela não integra o escopo deste fechamento: depende de agenda de recebíveis.

**Ambiguidade:** os esclarecimentos descrevem tarefas e decisões, mas não enumeram o processo operacional completo, sua ordem, responsáveis, dependências ou critérios de conclusão. A lista acima é uma reconstrução a partir das respostas, não um fluxo confirmado pela Tarvo.

**Após ler o documento — parcialmente esclarecido:** “Sua missão” explicita as frentes do fechamento solicitado: apuração das duas linhas, divergências, notas a emitir, classificação dos extratos e pendências humanas, com rastreabilidade. Não precisamos perguntar novamente quais trabalhos a solução deve cobrir. O documento não descreve a sequência da operação atual, responsáveis, dependências ou aprovações; essa lacuna permanece.

**Após analisar o ZIP:** `00_LEIA-ME.md` identifica como cada fonte chega: portal Orbe, planilha manual do financeiro, caixa de entrada, exportação ERP e internet banking. Isso esclarece a coleta dos insumos, mas não documenta a sequência interna do fechamento ou as aprovações. A lacuna foi reduzida aos procedimentos e responsáveis que os arquivos não mostram.

**Após a resposta das 9h49:** aprovação de condições comerciais cabe ao comercial e de regras do fechamento, à Helena. Falta descrever a execução e conferência das etapas e a aprovação do fechamento concluído; essas aprovações de resultados não devem ser confundidas com aprovação de regras.

**Complemento útil:** pedir a sequência real, quem executa e confere cada etapa, quais registros indicam conclusão e quem libera o fechamento concluído. Não repetir quem aprova taxas e regras.

Fontes: [faturamento](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792194465573829), [classificação dos bancos](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792196067326279), [limite da conciliação](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792200869514179).

### “Qual o entregável quando uma etapa acaba?”

**O que já sabemos:** checkout gera uma nota por lojista/mês com saldo positivo; remessa gera uma nota à Ponte pelo total mensal. Helena precisa de pendências de contestação com operações e valores, além de rastreabilidade dos cálculos. O canal também define os arquivos exigidos na entrega do hackathon.

**Ambiguidade:** não foram definidos os artefatos internos de cada etapa do fechamento da Tarvo, seu formato, aprovador ou condição de aceite. A entrega do hackathon não prova que esses arquivos sejam entregáveis da operação atual. As regras das notas esclarecem sua montagem, mas não demonstram que a Tarvo efetivamente emite cada nota ao concluir uma etapa específica.

**Após ler o documento — resolvido para a solução do desafio:** “Arquivos de saída em saida/” determina os entregáveis abaixo, com colunas obrigatórias. O formato é CSV separado por ponto e vírgula, decimal com ponto, datas AAAA-MM-DD e CNPJ com 14 dígitos numéricos.

| Trabalho | Entregável exigido |
|---|---|
| Apurar comissões por lojista e linha | `comissoes_por_lojista.csv` |
| Conferir taxas aplicadas contra contratadas | `divergencias_taxa.csv` |
| Preparar faturamento | `notas_a_emitir.csv` |
| Classificar movimentos dos dois bancos | `lancamentos_classificados.csv` |
| Encaminhar exceções humanas, com motivo e decisor | `pendencias.csv` |
| Ligar os números às linhas de origem | `rastro.csv` |

A entrega referente ao faturamento é a lista de notas **a emitir**; não há exigência de emissão fiscal efetiva. A soma dos valores de origem por `id_saida` deve coincidir com o número reportado. Esses são resultados exigidos da solução, não prova dos artefatos usados hoje pelo financeiro.

**Complemento útil:** dispensar a pergunta sobre quais saídas a solução deve gerar. Se necessário para entender a rotina atual, investigar apenas os artefatos internos e quem os aprova, junto da sequência operacional.

Fontes: [notas](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792194465573829), [lista para contestação](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792200848816529), [entrega do hackathon](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792192415046529).

### “Quais são as regras que apenas você conhece e quantas são?”

**O que já sabemos:** diversas regras foram explicitadas: taxa contratada no checkout; estornos na competência do estorno à taxa original; isenção Casa do Estudante; contrato Rota sem reajuste; Atlas bloqueada para faturar; identificação dos ECs; remessa pelo realizado; negativos, duplicatas e ressalvas; arredondamento; provisões e movimentos bancários. O registro completo está em `duvidas-slack.md`.

**Ambiguidade:** o canal não afirma que todas essas regras eram conhecidas exclusivamente por Helena, nem que a lista é exaustiva. Também não informa a quantidade total das regras tácitas. Não seria correto contar as respostas e apresentar esse número como inventário oficial.

**Após ler o documento — permanece ambíguo:** o contexto confirma que uma pessoa concentra conhecimento e mantém a planilha de taxas, mas não fornece inventário ou quantidade de regras tácitas. As regras conhecidas já estão registradas; a investigação restante deve se restringir às decisões e exceções ainda não cobertas.

**Após analisar o ZIP:** o `00_LEIA-ME.md` afirma que existem regras de negócio não escritas nos arquivos. A planilha contém pistas concretas, como o comentário da célula A13 sobre consultar Diego, do comercial, quanto à condição especial da Casa do Estudante. Essa condição já foi esclarecida no Slack. O ZIP não permite afirmar que o inventário de regras tácitas esteja completo nem quantificá-lo.

**Após a resposta das 9h49:** a ausência de substituto de Helena está confirmada, assim como a divisão de aprovação entre comercial e financeiro. Isso confirma a dependência, mas não inventaria outras regras tácitas. Perguntar somente pelas decisões e exceções adicionais que ainda não foram esclarecidas no canal.

**Complemento útil:** identificar regras ainda não documentadas e as atividades em que aparecem, sem repetir aprovações ou cobertura de férias.

Fontes: [condições especiais](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792194576391779), [remessas](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792194515838639), [arredondamento](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792196013836169).

### “Essas regras são aplicadas em qual parte do fechamento?”

**O que já sabemos:** o conteúdo permite associar taxas, cadastros e arredondamento à apuração; estornos/reversões à comissão; exceções de remessa à inclusão e competência; saldo positivo à preparação das notas; provisões à classificação bancária; diferenças à lista de contestação.

**Ambiguidade:** essa associação é inferida da finalidade das regras. Não existe um mapa confirmado entre todas as regras tácitas e etapas formais da rotina, nem a distinção completa entre decisões durante a operação e no fechamento.

**Após ler o documento — resolvido funcionalmente para as regras conhecidas:** as saídas exigidas permitem organizar a aplicação das regras já esclarecidas:

| Regras conhecidas | Aplicação na solução |
|---|---|
| Taxas, cadastros, vigências, estornos, antecipações e arredondamento | Apuração das comissões |
| Taxa aplicada diferente da contratada, observadas as exceções confirmadas | Identificação e quantificação de divergências; Casa do Estudante por isenção não comunicada fica separada, como devolução pendente com Helena e comercial |
| Tomador, agrupamento mensal e saldo faturável | Preparação das notas a emitir |
| Provisões e contrapartidas bancárias | Classificação dos extratos |
| Exceções que dependem de decisão humana | Registro das pendências e de quem decide |

Esse mapa é uma associação analítica entre as respostas do Slack e os resultados exigidos pelo documento, suficiente para estruturar a solução. Não confirma quem aplica cada regra nem o momento em que ela é consultada na operação atual.

**Complemento útil:** dispensar a pergunta genérica sobre onde aplicar as regras conhecidas na solução. Investigar apenas regras específicas sem aplicação clara ou os responsáveis e momentos da rotina atual, evitando repetir a pergunta sobre as etapas.

Fontes: [base do checkout](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792191952289259), [notas](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792194465573829), [contrapartidas](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792196067326279).

### “Quando vocês mandam a taxa para ele pagar? Antes do fechamento, durante a operação ou só no fim do mês?”

**O que já sabemos:** o relatório traz a taxa que a Orbe já cobrou. A comissão e a nota de checkout são apuradas por lojista/mês pela taxa contratada. Há casos de cobrança já realizada que exigem devolução, como Casa do Estudante.

**Ambiguidade:** isso não informa o instante da cobrança, se há desconto na liquidação, cobrança separada, exposição no checkout ou comunicação prévia ao lojista. A nota mensal não prova que a taxa só seja cobrada no fim do mês. “Ele” também precisa ser distinguido entre lojista e aluno; as respostas sobre devolução se referem ao lojista.

**Após ler o documento — permanece ambíguo:** “Duas linhas de negócio” confirma que os lojistas recebem dos alunos por cartão e Pix pela Tarvo, que usa a Orbe, e que a Tarvo ganha MDR e taxa de antecipação. Não informa quando a taxa é exibida, descontada ou cobrada, nem como se relaciona com a nota mensal. O momento da cobrança continua sem definição suficiente.

**Após analisar o ZIP — mecanismo no relatório confirmado; momento financeiro ainda parcial:** nas 1.943 linhas do CSV Orbe, `valor_liquido = valor_bruto − valor_taxa`. No Pix `TX88410916`, em 01/09, bruto de R$ 939,15 menos taxa de R$ 8,35 resulta em líquido de R$ 930,80. Portanto, a taxa já está abatida do líquido informado pela Orbe. Isso não comprova o instante do desconto no caixa do lojista, como é exibido ou comunicado, nem sua relação com a nota mensal. Também não transforma `valor_taxa` em comissão contratual faturável.

**Após o HTML — mecanismo geral esclarecido:** o lojista paga o MDR descontado de cada venda; o portador paga o preço da compra, não a taxa da loja. A subadquirente recebe da adquirente e repassa ao lojista descontando sua taxa. O material ressalva que não descreve as regras específicas de cobrança, faturamento ou exceções da Tarvo. Falta o evento operacional em que o desconto se efetiva para o lojista, a comunicação e a relação com a nota mensal.

**Complemento útil:** perguntar somente por esses três detalhes específicos da Tarvo. Não repetir quem paga o MDR ou se ele aparece abatido no relatório.

Fontes: [taxa cobrada versus faturamento](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792191952289259), [nota mensal](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792194465573829).

### “Qual a ordem em que os processos de transação passam pela Orbe e pela Tarvo?”

**O que já sabemos:** a Orbe deposita tudo no Aurora e não paga lojistas diretamente. Débito/Pix entram no dia seguinte; crédito/parcelado, nos meses seguintes conforme parcelas. A Tarvo utiliza conta garantida para pagar lojistas antes da liquidação Orbe. Não há equivalência direta entre o líquido das transações de setembro e o crédito bancário do mês.

**Ambiguidade:** o fluxo financeiro de liquidação foi esclarecido em parte, mas falta a sequência ponta a ponta de autorização, captura, aplicação/desconto da taxa, custódia, repasse ao lojista, antecipação e reversão. Também faltam agenda de recebíveis e prazos detalhados de repasse por cenário.

**Após ler o documento — permanece parcialmente esclarecido:** o documento identifica os participantes e a relação aluno–lojista–Tarvo–Orbe, mas não acrescenta os eventos e prazos do fluxo transacional. O esclarecimento mais específico continua sendo o do Slack sobre depósitos no Aurora, liquidação e conta garantida. A conciliação parcela por parcela já foi excluída deste fechamento por Helena; não deve ser reintroduzida como requisito por causa dessa lacuna.

**Após analisar o ZIP — exemplos disponíveis; ligação bancária ausente:** já existem vendas Pix (`TX88410916`), crédito parcelado (`TX88410128`), antecipação (`AN88444915`) e sua reversão (`AN88445114`, que referencia a original com valores opostos). O extrato Aurora mostra créditos da Orbe e pagamentos aos lojistas, mas não contém identificadores que liguem cada movimento bancário a essas transações. Não há agenda detalhada de recebíveis no pacote.

**Após o HTML:** a cadeia geral de autorização é portador → lojista → subadquirente → adquirente → bandeira → emissor, com retorno da autorização. Liquidação é movimento posterior do dinheiro; aprovação não equivale a recebimento. Isso esclarece os papéis gerais, mas não determina o calendário ou o valor de repasse de cada lojista da Tarvo, nem onde essas condições ficam registradas.

**Complemento útil:** dispensar pedidos genéricos de exemplos e explicações dos participantes do arranjo. Investigar apenas a regra operacional da Tarvo para data e valor do repasse e sua fonte de registro. Isso não reabre a conciliação parcela por parcela já excluída do fechamento.

Fonte: [fluxo Orbe → Aurora e conta garantida](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792200869514179).

### “Tarifas dos métodos de pagamento”

**O que já sabemos:** o canal remete à planilha vigente como fonte contratual, com exceções confirmadas. Para Rota, não houve reajuste em 2026; para Casa do Estudante, MDR e antecipação são zero de setembro a dezembro; Atlas não tem taxa confirmada. Não existe indicação de uma tarifa única aplicável a todos os lojistas.

**Ambiguidade inicial:** “tarifas” pode significar taxa contratada do lojista, taxa efetivamente aplicada pela Orbe ou custo da Orbe para a Tarvo. O canal não transcrevia a tabela por modalidade, lojista e vigência; a consulta ao ZIP abaixo resolve a localização dos percentuais disponíveis.

**Após ler o documento — permanece parcialmente esclarecido:** o documento identifica cartão, Pix, MDR e antecipação, mas não apresenta percentuais. As taxas contratuais devem ser consultadas na planilha, com as exceções do Slack. A falta de transcrição no canal não justifica perguntar novamente todos os percentuais ao cliente. Custos Orbe–Tarvo são um assunto distinto, já registrado na seção “Não respondido”.

**Após analisar o ZIP — resolvido como consulta genérica às tarifas dos lojistas:** a aba “Taxas vigentes”, colunas D:I, traz débito, crédito à vista, crédito de 2–6x, crédito de 7–12x, Pix e antecipação. Na linha 8, Horizonte Viagens tem, respectivamente, 1,49%, 2,69%, 3,19%, 3,79%, 0,89% e 2,10%. Colunas J e K trazem spread de remessa e vigência. As taxas aplicadas estão no CSV Orbe, na coluna `taxa_aplicada_pct`, e no relatório Ponte. Os valores contratuais e aplicados devem ser distinguidos.

Na Bridge, E6 e E7 documentam crédito à vista de 2,59% até 14/09 e 2,19% a partir de 15/09. A linha da Casa do Estudante ainda tem taxas positivas: aplicar a isenção no cálculo contratual, mas separar o valor cobrado como devolução pendente com Helena e comercial, sem cobrança contra a Orbe por essa isenção não comunicada. Atlas segue sem taxa vigente confirmada; a orientação de não faturar até confirmação já foi dada. A aba antiga não deve ser usada para inventar sua condição atual. Os custos Orbe–Tarvo não constam dessa tabela.

**Complemento útil:** não perguntar novamente uma tabela geral de tarifas. Tratar apenas condições ausentes, conflitantes ou não confirmadas. A falta de confirmação da Atlas já tem tratamento operacional definido, mesmo sem percentual disponível.

Fontes: [planilha e cálculo](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792191952289259), [cadastros e Atlas](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792193059964329), [Rota e Casa](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792194576391779).

## Outros esclarecimentos obtidos no ZIP

### Duplicata da Ponte: não há conflito de valores neste caso

Na aba “Operações” do XLSX anexado ao e-mail, as linhas 76 e 77 têm o mesmo número `PC-0926-0162` e os mesmos dados financeiros, datas, cliente e status. Somente a segunda contém “reprocessada” na observação. Com a regra do Slack de contar uma vez, não é necessário perguntar qual valor prevalece nessa duplicata. Precedência entre registros conflitantes continua sem regra geral, mas é uma hipótese futura, não um bloqueio demonstrado nesse par.

### Estornos de agosto: há referências contratuais aplicáveis

O CSV contém nove estornos de vendas de agosto, com data original, modalidade e parcelas. As vendas originais não estão no CSV de setembro, mas as linhas contratuais dos respectivos lojistas têm vigência que abrange as datas informadas. Com as regras já confirmadas no Slack, não foi identificada necessidade de pedir histórico adicional de taxas para esses nove casos. Na Casa do Estudante, a venda original de agosto antecede a isenção iniciada em setembro; a taxa do estorno é a da data original, não automaticamente zero.

Isso é uma conclusão sobre os casos disponíveis e a vigência declarada na fonte, não uma confirmação de que todo histórico contratual futuro estará completo.

## Revisão das três perguntas inicialmente não respondidas

### “Qual parte do fechamento consome mais tempo?”

**Documento do case:** informa oito dias úteis, conferência de fontes uma por uma, concentração de conhecimento e equipe de três pessoas. A avaliação de “Causa raiz” exige entender por que o fechamento é lento e erra. Não há distribuição de tempo por tarefa.

**Data pack:** revela fontes heterogêneas, cadastros inconsistentes, tipos misturados na planilha, exceções e duplicidade. São evidências de trabalho de conferência e investigação, mas não medem duração, espera ou retrabalho.

**Slack:** as respostas lidas esclarecem regras e pendências, mas não ordenam as atividades por esforço nem identificam a mais demorada.

**Conclusão — continua não respondido e é útil para entender a causa raiz:** não se pode inferir o maior gargalo apenas do volume de linhas ou da existência de erros. Precisamos distinguir execução manual, retrabalho e espera por informação. Não impede calcular os resultados solicitados, mas ajuda a priorizar a solução e fundamentar seu impacto.

**Pergunta ainda útil:** quais são as três atividades que mais consomem tempo, quanto cada uma toma e quanto disso é execução versus espera por informação?

**Fontes:** documento, seções “O cliente” e “O que avaliamos”; `00_LEIA-ME.md`; estrutura dos relatórios e planilha do ZIP. Nenhuma dessas fontes contém medição de tempo por atividade.

### “Vocês refazem os cálculos na fonte para recalcular o spread?”

**Documento do case:** exige apuração, divergências e pendências humanas com rastreabilidade. Não exige corrigir o sistema da Ponte ou alterar os arquivos originais.

**Data pack:** o e-mail pede resposta em até cinco dias úteis em caso de divergência e define participação de 50% do spread realizado, com repasse previsto em 06/10 mediante nota. O anexo apresenta taxa do cliente, PTAX, spread realizado e estimado, além da observação “Taxa travada no pedido (D-1)” nos negativos. A planilha contém valores, sem fórmulas; não há relatório corrigido nem registro da investigação. A observação D-1, sozinha, não comprova duração da trava ou vencimento: esses esclarecimentos vieram do financeiro no Slack.

**Slack:** Helena excluiu os negativos questionados da comissão e da nota e assumiu a contestação. Informou que ainda não havia contestado, pediu lista de operações e valores e orientou considerar o prazo aberto para o case. Para a devolução do excesso da Mundo Aberto, confirmou ajuste da participação no mês em que ocorrer. Não descreveu quem investiga dentro da Ponte, que evidências são usadas ou como uma correção é devolvida à Tarvo.

**Conclusão — parcialmente esclarecido; procedimento na fonte continua não respondido:** já sabemos o que a Tarvo deve fazer neste fechamento. Apurar divergência não autoriza substituir o spread realizado pelo estimado ou pelo contratado. A dúvida residual é o retorno e acompanhamento da contestação, não se devemos recalcular a comissão de setembro com uma base diferente. Não é bloqueio para o tratamento desses negativos no case; é relevante se a solução acompanhar correções posteriores.

**Investigação residual:** como a Ponte comunica a conclusão da contestação, qual documento comprova a correção e quem na Tarvo confere e incorpora o ajuste. Não é necessário repetir a pergunta sobre aceitar os quatro negativos ou quem os contesta.

Fontes: `03_email_ponte_cambio_relatorio_set2026.eml` e seu XLSX, aba “Operações”; documento, “Sua missão”; [regra dos negativos](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792194515838639), [contestação ainda não aberta](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792200848816529), [ajuste após devolução à Mundo Aberto](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792197913743739).

### “Qual a taxa contratual entre Orbe e Tarvo?”

**Documento do case:** descreve MDR e antecipação como receitas da Tarvo e pede comissões, divergências, notas e classificação bancária. Não pede apuração de lucro líquido ou da margem após custos de adquirência.

**Data pack:** o `00_LEIA-ME.md` identifica a planilha como taxas negociadas com cada lojista. Ela não é um contrato Orbe–Tarvo. O CSV Orbe traz taxa aplicada, taxa em reais e líquido, sem coluna que isole custo da adquirente ou sua remuneração. Os extratos e o plano de contas não fornecem uma tabela contratual que permita determinar esse custo.

**Slack:** Helena confirmou que a comissão é a taxa contratada inteira, sem desconto de custo Orbe, e que `valor_taxa` não deve substituir o cálculo contratual.

**Conclusão — contrato comercial não respondido; tratamento da comissão resolvido:** não sabemos os custos contratuais Orbe–Tarvo, nem podemos presumir que sejam zero. Entretanto, não é necessário obter essa informação para calcular a comissão definida no case. Uma ausência de informação sobre custos não deve ser tratada como ambiguidade na fórmula já confirmada.

**Necessidade de perguntar:** dispensável para os cálculos de comissão e notas solicitados. Só retomar se o escopo incluir margem/lucro, conciliação de descontos da adquirente ou algum movimento bancário específico cuja natureza dependa desse contrato. Antes de perguntar, identificar esse uso concreto; não perguntar novamente se o custo deve ser abatido da comissão.

Fontes: documento, “Duas linhas de negócio” e “Sua missão”; `00_LEIA-ME.md`; `01_orbe_relatorio_comissoes_set2026.csv`; `02_tabela_taxas_contratadas.xlsx`; extratos e plano de contas; [comissão sem desconto de custo Orbe](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792200888817559).

## Situação após a revisão das três fontes

Na comparação inicial com o Slack, os 11 tópicos da lista foram organizados em 12 pontos: dois confirmados, sete parcialmente esclarecidos e três sem resposta direta. A pergunta composta sobre spread foi desmembrada entre destino/responsável e recálculo na fonte.

Dos sete pontos inicialmente ambíguos, três deixam de exigir perguntas genéricas para construir a solução: entregáveis, aplicação funcional das regras conhecidas e tarifas disponíveis dos lojistas. Quatro continuam com lacunas sobre a rotina: sequência operacional, inventário das regras tácitas, momento efetivo da cobrança e eventos/vínculos do fluxo transacional. As tarifas ainda têm exceções específicas, como Atlas, cujo bloqueio de faturamento já foi confirmado.

A revisão dos três pontos inicialmente não respondidos está concluída:

| Tema | Situação após documento, ZIP e Slack | Necessidade para a próxima conversa |
|---|---|---|
| Maior consumo de tempo no fechamento | Sem resposta sobre duração ou ranking das atividades | Útil para causa raiz e priorização |
| Recálculo/correção do spread na fonte | Tratamento de setembro confirmado; retorno da contestação não descrito | Investigar se houver acompanhamento de ajustes posteriores |
| Contrato de custos Orbe–Tarvo | Valores comerciais ausentes; comissão sem desconto de custo confirmada | Não necessário para a comissão e notas do case |

Os exemplos já presentes nos arquivos dispensam pedidos genéricos de novas transações. A duplicata concreta não exige escolha entre valores conflitantes. Os nove estornos de agosto têm referência contratual com vigência aplicável. A ausência de dados sobre a rotina atual não deve ser confundida com ausência de regra para calcular o fechamento solicitado.

Com a leitura até 9h49, também ficaram confirmados os responsáveis por aprovar condições comerciais e regras de fechamento e a ausência atual de substituto de Helena. O HTML esclarece o arranjo geral de pagamentos; não fixa as condições operacionais específicas da Tarvo. A pergunta sobre classificação dos spreads negativos foi respondida e retirada. O tratamento da Casa do Estudante foi corrigido para devolução separada das divergências contratuais, sem cobrança contra a Orbe pela isenção não comunicada.

As seis lacunas restantes foram consolidadas na mensagem abaixo. Nenhuma pergunta foi enviada ao Slack.

## Histórico das seis perguntas enviadas — respondidas

[financeiro] Turma do Barulho: lemos o case, o data pack, o material “Do Cartão ao Caixa” e as respostas do canal até 9h49. Restaram estas dúvidas:

1. Do recebimento dos arquivos à conclusão do fechamento, qual é a sequência das atividades, quem executa e confere cada etapa e qual registro indica que ela terminou? Quem dá a aprovação final para liberar o fechamento concluído?

2. Como se dividem as funções e frentes de trabalho entre as três pessoas do financeiro? Quais três atividades mais consomem os oito dias úteis do fechamento e quanto tempo cada uma exige, separando trabalho manual, retrabalho e espera por informação do comercial ou de parceiros?

3. Além das regras já esclarecidas no canal, quais decisões ou exceções ainda não documentadas dependem do conhecimento de uma única pessoa? Em quais atividades do fechamento elas aparecem?

4. Na operação da Tarvo, em qual evento o desconto da taxa é efetivado no valor a receber pelo lojista e por qual canal ele vê esse desconto? A nota mensal apenas documenta a taxa já descontada ou gera algum valor adicional a pagar?

5. Qual regra define a data e o valor dos repasses da Tarvo a cada lojista, e onde essas condições ficam registradas? A dúvida é sobre a regra operacional de repasse, sem reabrir a conciliação parcela por parcela neste fechamento.

6. Depois que a Ponte conclui uma contestação, como comunica o resultado e qual documento comprova a correção? Quem na Tarvo confere esse retorno e registra o ajuste no fechamento correspondente?

