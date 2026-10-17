# Tarvo — contexto do problema e operação atual

Este documento resume o caso fictício do Desafio Barte AI. Descreve o negócio e as regras conhecidas; não define arquitetura ou implementação. Dados, empresas, pessoas e CNPJs do data pack são sintéticos.

## Negócio e participantes

A Tarvo Pagamentos é uma subadquirente voltada à educação internacional: agências de intercâmbio, escolas de idiomas e operadoras de turismo estudantil. Tem cerca de 25 lojistas ativos. O aluno compra do lojista; o lojista é o cliente empresarial da Tarvo. A Tarvo oferece checkout pela adquirente Orbe e remessas internacionais pela Ponte Câmbio. O comercial negocia condições; o financeiro apura receitas, confere movimentos e prepara o faturamento e o fechamento.

A operação cresceu três vezes em um ano. O financeiro tem três pessoas e o fechamento leva oito dias úteis. Os arquivos são conferidos manualmente, sobretudo no Excel. Uma pessoa mantém a planilha de taxas e concentra regras não documentadas; sua ausência compromete o fechamento. Cobranças indevidas já foram descobertas apenas após reclamação de lojista.

Composição confirmada por Helena em resposta à Turma do Barulho, copiada pelo usuário em 17/10/2026: **Bia** cuida do checkout e mantém a planilha de taxas; **Caio** cuida dos bancos e das remessas; **Helena** confere, aprova, decide exceções e fala com comercial, Orbe e Ponte. As condições comerciais, correspondências de nomes/EC/CNPJ, critérios de contestação e provisões estavam concentrados em Helena; sua ausência impede aplicar essas regras.

## Checkout: recebimento de alunos

O aluno paga por cartão ou Pix, pela estrutura Tarvo/Orbe. A Orbe registra pagamentos e demais movimentos, com estabelecimento, modalidade, parcelas, valor bruto, taxa aplicada, valor da taxa e valor líquido. Os extratos mostram recebimentos da Orbe e repasses; os materiais não descrevem todo o percurso de custódia, liquidação e transferência dos recursos.

A Orbe desconta a taxa quando paga e liquida o líquido. O lojista vê o desconto no extrato de repasse enviado pela Tarvo. A nota documenta a taxa já descontada e não gera cobrança adicional.

Pela regra, os repasses ocorrem duas vezes por mês, perto dos dias 10 e 24, pelo que a Orbe já liquidou. A regra consta do contrato de adesão de cada lojista, em pasta do comercial. Em esclarecimento posterior, Helena confirmou a exceção prática: quando um lojista pressiona, Bia às vezes paga antes da liquidação Orbe usando a conta garantida do Aurora. Essa exceção não está documentada, não tem limite definido e depende de quem executa. Isso esclarece a aparente contradição entre as respostas anteriores. Não equiparar automaticamente esse pagamento antecipado às operações de antecipação tarifadas no relatório da Orbe.

As taxas contratadas variam por lojista, modalidade e vigência: débito, crédito à vista, crédito de 2–6 parcelas, crédito de 7–12 parcelas, Pix e antecipação. MDR é a taxa sobre o pagamento. Antecipação permite receber antes valores futuros, mediante taxa.

Regras confirmadas pelo financeiro:

- **Comissão faturável:** valor bruto × taxa contratada, transação por transação. `valor_taxa` informa o que a Orbe cobrou; não substitui o contrato. O case não detalha custos suficientes para calcular lucro líquido.
- **Divergência:** diferença entre taxa aplicada e contratada. Cobrança a maior é analisada pelo financeiro, que trata a devolução ao lojista e a cobrança à Orbe; não há devolução automática.
- **Estorno:** devolve a taxa e reduz a comissão no mês do estorno, usando a taxa contratada na data da venda original. Venda de agosto estornada em setembro afeta setembro; agosto não é reaberto.
- **Antecipação:** sua comissão integra o checkout. Reversão anula a taxa da antecipação referenciada.
- **Bridge:** há condições até 14/09/2026 e novas condições a partir de 15/09/2026; a vigência precisa ser respeitada.
- **Casa do Estudante:** MDR e antecipação zerados de setembro a dezembro/2026 por acordo comercial. Remessa segue normal. A Orbe não foi avisada e cobrou conforme a planilha. Conforme esclarecimento do financeiro em 17/10 às 9h44, não há valor a cobrar da Orbe por essa isenção não comunicada: registrar separadamente das divergências contratuais, com o valor a devolver ao lojista, como pendência de Helena com o comercial. Estorno de venda anterior à isenção usa a taxa vigente na data da venda original.
- **Rota Global:** não houve alteração contratual em 2026; aumento aplicado pela Orbe não comprova reajuste válido.
- **Atlas:** começou a transacionar em 10/09, mas não há contrato vigente assinado nem taxa confirmada. Não faturar até confirmação comercial; a presença na aba antiga não confirma a condição atual.

Cadastro confirmado: EC `1043300981` = Novo Horizonte Intercâmbio; EC `1043396662` = Horizonte Viagens; EC `1038867654` = Kiwi Experience. As duas Horizonte são empresas diferentes. CNPJs e taxas dessas três estão nas respectivas linhas da aba vigente.

## Remessas: pagamentos ao exterior

O lojista utiliza a Tarvo/Ponte para pagar instituições no exterior. A Ponte executa o câmbio e informa número da operação, cliente/CNPJ, contratação, liquidação, moeda, valor em moeda estrangeira, cotação do cliente, PTAX de referência, valor em reais, spread realizado, spread estimado, IOF, compliance e observações.

Spread é a margem cambial da operação. A comissão da Tarvo é **50% do campo “Spread R$” realizado**, não do spread estimado nem uma comissão recalculada pela taxa contratada. A condição contratada serve também para conferir a cobrança ao lojista. IOF é informado separadamente e não deve ser confundido com spread.

Regras confirmadas:

- Spread contratado vazio ou “padrão”: 1,5% sobre a PTAX de referência. Mundo Aberto negociou 1,20% em julho/2026; aplicação superior é divergência a contestar com a Ponte.
- A competência usa a **data de contratação**, mesmo quando a liquidação ocorre em outubro.
- O número da operação é único; repetição não representa duas operações legítimas. Não foi definida a precedência entre registros duplicados conflitantes.
- “APROVADO C/ RESSALVA” não impede inclusão por si só.
- Os spreads negativos questionados foram rejeitados: a trava contratual dura duas horas e essas operações passaram do prazo. Ficam fora da comissão e da nota, com contestação pelo financeiro. Não extrapolar essa explicação para situações novas sem evidência.

O e-mail da Ponte prevê o repasse de setembro em 06/10/2026, condicionado ao recebimento da nota fiscal de intermediação. A Ponte paga a participação à Tarvo; o lojista identifica a origem comercial da comissão.

Após uma contestação, a Ponte responde por e-mail e envia o ajuste como crédito ou débito no relatório do mês seguinte. Helena confere e registra no fechamento do mês em que o ajuste aparece.

## Faturamento

- **Checkout:** uma nota por lojista por mês, pela comissão contratual apurada, incluindo antecipações e abatimentos de estornos/reversões. Resultado zero ou negativo não gera nota. Negativo não passa automaticamente ao mês seguinte; exige tratamento do financeiro com o lojista.
- **Remessa:** uma única nota para a Ponte Câmbio, pelo total da participação mensal da Tarvo; não há nota de remessa por lojista. CNPJ da Ponte no e-mail: `75374179000146`.
- Não há texto padrão obrigatório para discriminação: serviço e competência bastam.

## Bancos, caixa e contabilidade

Aurora é a conta principal; Meridiano é usado nas remessas. Os extratos incluem recebimentos, repasses, despesas, tributos, transferências internas e movimentos não identificados. O plano de contas vem do ERP Fênix.

**Receita apurada, valor a faturar e movimento bancário são conceitos distintos.** Entrada de dinheiro não comprova receita do mês; saída não comprova despesa do mês. Recursos repassados, transferências internas e liquidação de obrigações exigem tratamento próprio.

Fatos confirmados sobre setembro:

- Folha, ISS, INSS, FGTS e DARFs pagos no mês pertencem a agosto e já estavam provisionados.
- O recebimento da Ponte em 04/09 é spread de agosto já registrado como comissão a receber.
- Pix de R$ 7.350 sem origem identificada: não é receita até identificação.
- Devolução de R$ 12.400, Mundo Aberto: repasse que voltou, ainda sem motivo conhecido.
- Transferência de R$ 300.000: saiu do Aurora em 30/09 e chegou ao Meridiano em 01/10.

O financeiro esclareceu os fatos, mas deixou a proposta dos lançamentos e o tratamento das pendências para os participantes justificarem; não confirmou contas contábeis específicas para esses casos.

## Fontes e rotina atual

| Fonte | Conteúdo e particularidades |
|---|---|
| `01_orbe_relatorio_comissoes_set2026.csv` | 1.943 registros: 1.840 vendas, 59 estornos, 38 antecipações e 6 reversões; 22 ECs distintos |
| `02_tabela_taxas_contratadas.xlsx` | Cadastro, taxas, vigências e comentários; tipos misturados, ECs ausentes e aba “ANTIGO 2025 - nao usar” |
| `03_email_ponte_cambio_relatorio_set2026.eml` | Condições do repasse e XLSX anexado com abas Operações e Resumo |
| `04_plano_de_contas_fenix_erp.csv` | Hierarquia e contas disponíveis no ERP |
| `05a_extrato_banco_aurora_cc4471_set2026.csv` | Conta principal; cabeçalhos, saldo anterior e movimentos |
| `05b_extrato_banco_meridiano_cc90233_set2026.ofx` | Conta de remessas; 100 transações identificadas por FITID |

A rotina descrita envolve baixar relatórios, abrir anexos, consultar taxas, identificar lojistas, conferir vigências e movimentos, apurar comissões, investigar divergências, preparar notas e classificar extratos. Nomes inconsistentes, contratos incompletos, acordos não comunicados, duplicidades e diferenças entre competência e caixa exigem investigação e conhecimento humano.

Sequência confirmada: baixar Orbe, e-mail Ponte e extratos → casar transações Orbe com taxas e apurar checkout por lojista → apurar remessa → classificar extratos no ERP → montar notas. Bia e Caio executam; Helena confere e aprova. O único registro de conclusão é uma aba de controle na mesma planilha, com “ok” e data por etapa.

Distribuição aproximada dos oito dias: checkout, 3 dias (metade de associação manual de nomes/EC/CNPJ e metade de retrabalho por planilha desatualizada); remessa, 2 dias (principalmente espera por Ponte e comercial); classificação bancária, 2 dias (quase tudo manual, linha por linha); último dia para notas e revisão de Helena. Esses tempos são estimativas do financeiro, não medições independentes.

## Lacunas conhecidas

Até a verificação feita no dia 16/10, faltam especificações completas de arredondamento, histórico contratual necessário a certos estornos, precedência de duplicidades conflitantes, fluxo de liquidação/repasse, custos da adquirência, procedimentos fiscais e lançamentos efetivamente realizados no ERP.

As revisões de 17/10 documentadas em `PROMPTS/outputs/duvidas-slack.md` e `PROMPTS/outputs/nossas-duvidas.md` complementam esse retrato inicial, incluindo arredondamento, rotina, responsáveis, esforço, desconto da taxa, calendário aproximado de repasses e retorno de contestações. A relação entre repasses do já liquidado e uso da conta garantida foi esclarecida: o primeiro é a regra; o segundo financia exceções práticas sob pressão de lojistas, sem documentação ou limite definido.

## Referências

- [Instruções do case](https://docs.google.com/document/d/1GwHs0lgLWXdw-jIrPyYAxyJ_xEJJxViE/edit) e `00_LEIA-ME.md` do data pack.
- [Checkout e divergências](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792191465288839).
- [Estornos](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792191877776469).
- [Cadastros e Atlas](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792192601377449).
- [Notas fiscais](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792193219408319).
- [Remessas](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792193429257939).
- [Condições especiais e bancos](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792193803331999).
- [Casa do Estudante: devolução separada, sem cobrança à Orbe pela isenção não comunicada](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792241097683849).
- [Dúvida de divergência e tolerância ainda aberta na consulta](https://bartehackathonai.slack.com/archives/C0CA0S5D37B/p1792194771073879).
