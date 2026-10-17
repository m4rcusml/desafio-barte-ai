# Hipóteses, premissas e confirmações — Tarvo

Registro atualizado com o [Checkpoint 1 enviado em 17/10/2026](PROMPTS/outputs/checkpoint-1.txt), seu [feedback](PROMPTS/outputs/checkpoint-1-feedback.txt) e as respostas documentadas em [duvidas-slack.md](PROMPTS/outputs/duvidas-slack.md) e [nossas-duvidas.md](PROMPTS/outputs/nossas-duvidas.md). O checkpoint registra intenção de desenvolvimento, não funcionalidades implementadas. O feedback reconhece a leitura da causa raiz, mas não homologa limites, contas contábeis ou resultados numéricos.

O feedback orienta considerar premissas que alteram o fechamento e exclui a hipótese de caixa das entregas. Para cada premissa de cálculo/classificação, registrar as linhas afetadas e a diferença entre os tratamentos possíveis, quando houver dados. P1 e P2 permanecem propostas; P3 fica apenas como histórico fora de escopo. Uma terceira premissa de fechamento, se necessária, deve surgir de ambiguidade concreta dos dados, sem reclassificar regra já confirmada como hipótese.

## Hipóteses de causa raiz

| ID | Hipótese e evidência | Situação e limite |
|---|---|---|
| H1 | Cadastros, taxas, vigências e exceções fragmentados geram associação manual e retrabalho. Helena confirmou conhecimento concentrado; faltam ECs na planilha e há condições desatualizadas. Checkout leva cerca de três dias, metade de associação e metade de retrabalho, segundo o financeiro. | Sustentada pelos relatos e arquivos. Não implica ausência completa de cadastro: existe uma planilha, mas ela é incompleta e desatualizada. Tempos são estimativas do cliente. |
| H2 | A conferência atual não detecta sistematicamente diferenças contratuais antes de afetarem lojistas. Há reclamação por cobrança indevida e casos como Rota, Bridge e Mundo Aberto. | Sustentada pelas ocorrências; não afirmar que ninguém confere, pois existe conferência manual. |
| H3 | Repasses anteriores à liquidação contribuem para a necessidade de financiamento. | O uso da conta garantida para esses adiantamentos foi confirmado. Participação no saldo negativo e custo não quantificados; ver P3. Reconhecimento de receita por competência não é causa direta de saída de caixa. |

## Premissas propostas no Checkpoint 1

### P1 — Tolerância de divergência de remessa

- **Proposta:** avaliar inicialmente 0,01 ponto percentual, verificando também o impacto monetário. É limite de diferença entre taxas, não de R$ 0,01. Na representação fracionária de taxas, equivale a 0,0001.
- **Situação:** o financeiro delegou a escolha e a justificativa aos participantes; não homologou esse limite. A fronteira exata do filtro e seu efeito monetário ainda precisam ser documentados antes de aplicá-lo.
- **Validação necessária:** medir operações e valores incluídos/excluídos e verificar se diferenças relevantes seriam omitidas. Não tomar os totais propostos por outros participantes como gabarito.
- **Se inadequada:** recalibrar e regenerar as divergências. Não alterar por isso a comissão, cuja base confirmada é o spread realizado elegível.
- **Fonte:** pergunta e resposta do item 9 de `duvidas-slack.md`.

### P2 — Contrapartida de movimentos sem identificação suficiente

- **Proposta:** usar contrapartida transitória compatível com o plano, quando disponível, mantendo pendência e sem reconhecer receita indevidamente.
- **Situação:** proposta contábil da equipe; nenhuma conta específica foi homologada para todos os casos. A regra confirmada é classificar a contrapartida do movimento e baixar valores já registrados.
- **Validação necessária:** selecionar uma conta existente e apropriada no plano, documentando o motivo por movimento. Não inventar origem de Pix ou motivo de devolução; ausência de informação não equivale a receita zero comprovada.
- **Se inadequada:** revisar as contas e reprocessar os lançamentos afetados, preservando fontes e histórico.
- **Fontes:** itens 8, 10 e 12 de `duvidas-slack.md`.

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
| Casa do Estudante | MDR e antecipação zero de setembro a dezembro; devolução separada com Helena/comercial, sem cobrança à Orbe por isenção não comunicada. Estornos anteriores respeitam taxa original. | Atualização de 17/10 às 9h44 |
| Rotina, esforço e responsáveis | Bia: checkout/taxas; Caio: bancos/remessas; Helena: revisão, exceções e aprovação. Estimativa: 3 dias checkout, 2 remessa, 2 bancos e 1 notas/revisão. Controle por “ok” e data. | Resposta para Turma do Barulho |
| Desconto, repasses e ajustes Ponte | Taxa descontada na liquidação; nota documenta, sem nova cobrança. Repasse regular do já liquidado e exceção por conta garantida. Ponte responde por e-mail e ajusta relatório posterior; Helena confere. | Resposta e complemento para Turma do Barulho |

## Lacunas que permanecem

- Formato e natureza incremental/substitutiva dos ajustes posteriores da Orbe e procedimento para revisar período já aprovado. A resposta sobre variação de inputs não definiu esses detalhes.
- Contrato/taxa vigente da Atlas: bloqueio de faturamento já definido, percentual não conhecido.
- Precedência para duplicidades futuras com valores conflitantes. O par concreto `PC-0926-0162` tem dados financeiros iguais e difere apenas na observação; não há conflito financeiro a resolver nesse caso.
- Agenda detalhada de recebíveis e custos Orbe–Tarvo/conta garantida: não necessários à comissão definida no case, mas necessários a análises financeiras adicionais.
- Contas específicas para casos bancários ambíguos e decisões sobre valores sem origem ou devolução sem motivo identificado.

Os nove estornos de agosto analisados têm vigências contratuais aplicáveis nos arquivos, conforme `nossas-duvidas.md`; não registrar falta de histórico como bloqueio desses casos. Arredondamento, valor integral da contestação e rotina operacional já receberam resposta.

## Confirmação posterior — inputs e fechamento parcial

Helena confirmou mesmas fontes e colunas como estrutura mensal esperada, com mudança de registros, lojistas e condições. Atrasos, ajustes posteriores da Orbe e alterações inesperadas de layout acontecem e devem gerar aviso. Concluir partes independentes, marcar provisórios e explicitar bloqueios/motivos. A liberação cabe a Helena; taxa/cadastro passam antes pelo comercial.

Fonte e transcrição: [nossas-duvidas.md](PROMPTS/outputs/nossas-duvidas.md), resposta fornecida pelo usuário em 17/10/2026, sem horário ou permalink. Esses comportamentos passam a ser requisitos confirmados, não novas premissas. A escolha de dependências, estados e mecanismos de reprocessamento é proposta técnica documentada em [arquitetura-stack.md](PROMPTS/outputs/arquitetura-stack.md).
