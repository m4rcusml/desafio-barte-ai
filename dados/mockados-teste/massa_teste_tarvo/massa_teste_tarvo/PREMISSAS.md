# Premissas do gabarito

Estas são as regras que o gabarito segue. A origem de cada uma está marcada assim:

- **[DOC]**: está escrito nos documentos do case ou no e-mail da Ponte.
- **[DECIDIDO]**: o time decidiu.
- **[PROPOSTA]**: proposta aprovada pelo Raphael em 17/10, ainda sem confirmação da Helena.
- **[VALIDADO]**: caso de classificação validado pelo Raphael em 17/10.
- **[ABERTO]**: o time ainda não decidiu. No gabarito, essas linhas vêm marcadas na coluna `regra_em_aberto`.

Se a Helena responder diferente de alguma [PROPOSTA], é só mudar a regra no `gabarito.py` e rodar de novo.

## Checkout

| # | Regra | Origem |
|---|---|---|
| R1 | **Comissão de checkout:** `comissao_brl` = soma do `valor_taxa` da Orbe (o que foi de fato cobrado), contando vendas, estornos, antecipações e reversões dos arquivos 01 e 06. A coluna extra `comissao_contratada_brl` traz a alternativa (bruto × taxa contratada). | [ABERTO] |
| R2 | **Taxa vigente:** escolhida pela data da venda. No estorno vale a `data_venda_original`; na reversão de antecipação, a data da antecipação. | [DECIDIDO] |
| R3 | **Divergência:** existe quando a % aplicada é diferente da % contratada, e vale `diferenca_brl = bruto × (aplicada − contratada) / 100`, arredondado. Só 2 linhas (Pix de R$ 1,00 e R$ 3,50) mudam se a comparação for feita em reais com tolerância de R$ 0,01. | [ABERTO] |
| R4 | **Estorno de venda divergente:** gera uma linha de divergência com sinal negativo, que anula a da venda. Só 2 linhas. | [ABERTO] |
| – | **Arredondamento:** a Orbe trunca a taxa no centavo (29,708 vira 29,70). Isso não é divergência. As contas do gabarito arredondam meio centavo para cima. | observado no arquivo real |
| – | **Ajustes tardios:** o arquivo 06 entra no fechamento de setembro, junto com o 01. | [DOC] aviso da banca |
| – | **Reversão de antecipação:** abate a taxa de antecipação inteira. | premissa (pergunta à Helena) |

## Remessa

| # | Regra | Origem |
|---|---|---|
| R5 | **Comissão:** 50% do Spread R$ realizado, somado por lojista, casando pelo CNPJ do relatório. | [DOC] e-mail |
| R6 | **"APROVADO C/ RESSALVA":** entra normal. | [DOC] e-mail |
| R7 | **Nº Operação repetido ("reprocessada"):** conta uma vez só e gera pendência para contestar com a Ponte. | [PROPOSTA] |
| R8 | **Spread negativo:** fica fora da comissão e fora das divergências, e vira pendência. | [PROPOSTA] |
| R9 | **Spread em branco ou "padrão":** vale 1,5%. | [PROPOSTA] |
| R10 | **Divergência de remessa:** compara o spread contratado com o realizado, operação por operação. O spread realizado é a coluna Spread %, arredondada a 0,01 p.p. (1,5004% conta como 1,50%). `diferenca_brl` = Spread R$ − Valor R$ × spread contratado. | [PROPOSTA] |
| – | **Rodapé da Ponte:** "Total de operações" e "Spread total R$" incluem a operação duplicada e as negativas, então não servem como total. | observado no arquivo real |

## Cadastro de lojista

| # | Regra | Origem |
|---|---|---|
| R11 | **EC fora da tabela vigente:** o nome da Orbe é normalizado (sem acento, pontuação, "LTDA", "E", "DE" etc.). Se ficar igual ao nome da tabela vigente ou à razão social da aba antiga de um CNPJ que está na tabela vigente, casa. A comissão é calculada e abre pendência `CADASTRO_EC_PENDENTE`. | [PROPOSTA] |
| R12 | **Lojista sem contrato vigente ou sem casamento exato:** vira pendência sem comissão, divergência ou nota de checkout. Os tipos são `LOJISTA_SEM_CONTRATO_VIGENTE` e `LOJISTA_AMBIGUO`. Nome parecido não basta. | [PROPOSTA] |

## Notas

| # | Regra | Origem |
|---|---|---|
| R13 | **Checkout:** uma nota por lojista com comissão > 0. O tomador é o lojista e o valor é o da R1. | [PROPOSTA] |
| R14 | **Remessa:** uma nota de intermediação para a Ponte Câmbio (CNPJ 75374179000146), no valor de 50% do spread realizado total. | [DOC] e-mail |

O total da nota da Ponte (7.654,19) difere em 1 centavo da soma das comissões de remessa por lojista (7.654,20), porque cada uma é arredondada separadamente.

## Lançamentos (R15)

- **Aurora:** `ref_origem` é o número da linha física do arquivo, então o primeiro lançamento é L9. SALDO ANTERIOR, SALDO FINAL e o aviso do rodapé não são lançamentos.
- **Meridiano:** `ref_origem` é o FITID.
- **Classificação:** todos os lançamentos saem por REGRA com confiança 1, exceto a devolução de PIX, que fica HUMANO sem conta e com confiança 0.

| Lançamento | Conta |
|---|---|
| TED RECEBIDA … ORBE | 1.1.03.001 |
| PIX ENVIADO + lojista | 2.1.01.001 |
| PIX ENVIADO CONTABILIDADE | 4.2.06 |
| TRANSF P/ MERIDIANO, TED RECEBIDA TARVO MESMA TITULARIDADE | 1.1.09.001 (a de 30/09 em trânsito também, sem pendência) |
| PIX RECEB + lojista (Meridiano), TED ENVIADA PONTE LIQ OPERACOES | 2.1.02.001 |
| TAR… / TARIFA… | 4.2.01 |
| Condomínio / AWS / Google / Seguro | 4.2.02 / 4.2.03 / 4.2.04 / 4.2.05 |
| ISS / PIS / COFINS / IRRF | 2.1.03.003 / .001 / .002 / .004 |
| Folha 08/2026 / INSS / FGTS | 2.1.04.001 [VALIDADO] / 2.1.04.002 / 2.1.04.003 |
| Aplicação e resgate CDB / Rendimento / IOF | 1.1.02.001 / 3.2.01 / 4.3.01 |
| Repasse comissão Ponte 08/2026 | 1.1.03.002 [VALIDADO] |
| PIX RECEBIDO SEM IDENTIFICACAO | 1.1.09.002 + pendência [VALIDADO] |
| DEVOLUCAO PIX - lojista | HUMANO, sem conta + pendência [VALIDADO] |

## Pendências e quem decide

| Tipo | Quem decide | Valor em `valor_brl` |
|---|---|---|
| LOJISTA_SEM_CONTRATO_VIGENTE, LOJISTA_AMBIGUO | Comercial | Soma da `valor_taxa` cobrada do EC |
| CADASTRO_EC_PENDENTE | Financeiro | Soma da `valor_taxa` (a comissão que depende do casamento por nome) |
| OPERACAO_DUPLICADA, SPREAD_NEGATIVO | Financeiro | 50% do spread da operação (o impacto na comissão) |
| CREDITO_NAO_IDENTIFICADO, LANCAMENTO_SEM_REGRA | Financeiro | Valor do lançamento |
