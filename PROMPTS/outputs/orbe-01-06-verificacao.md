# Cruzamento Orbe `01 + 06` — 17/10/2026

Conferência executada em Python sobre os bytes originais baixados do Drive. O `01` foi lido diretamente do `Tarvo_Data_Pack_set2026.zip`; o `06` foi baixado separadamente. Fontes preservadas em `dados/originais/`. [ZIP no Drive](https://drive.google.com/file/d/1L8grvom49rmnNpMAC-YzDjW3e2X3h5sa/view) e [06 no Drive](https://drive.google.com/file/d/1JFUOwyEUaQK_HkYGEJ54JbWdxwIGHgEN/view).

**Estado do projeto:** o desenvolvimento do sistema de fechamento ainda não começou. Esta foi uma análise pontual das fontes em Python; não constitui implementação do núcleo ou validação dos CSVs finais. O script auxiliar e o JSON foram removidos a pedido do usuário após a consolidação das evidências neste relatório. Não há comando de reprodução dessa análise mantido no repositório.

Cabeçalho é linha 1; `L<n>` indica linha física, conferida pela contagem de linhas dos arquivos (1.944 e 15, incluindo cabeçalhos). Leitura em UTF-8 com tratamento de BOM; comparação dos valores com `Decimal`, sem ponto flutuante binário.

### Identificação das fontes analisadas

| Fonte | SHA-256 |
|---|---|
| `01` | `fdbc2bad2dd38dde8bf3af9d5c1f21116f0eae8d71d6a5a16b0dfd82de3cc7ec` |
| `06` | `b1cfd183945fb194e05cfbe9455ab364c31b676427e6653562f6821f57240292` |
| `zip` | `3fd12a7c4eabd04c3223631129fc68eb0d8c6da28fe312e9201a43187789f84f` |

O hash de `01` corresponde aos bytes do CSV dentro do ZIP; o hash de `zip` identifica o pacote completo. Os hashes identificam as versões analisadas, sem provar completude mensal.

## Resultados verificados

- Cabeçalhos iguais. `01`: 1.943 registros; `06`: 14 registros. Total: **1.957 IDs distintos e não vazios**. Nenhuma repetição de ID dentro dos arquivos ou entre eles; portanto, nenhum conflito de conteúdo sob o mesmo ID.
- Todos os 10 estornos e as 3 reversões do `06` têm uma referência única no `01`, com tipo esperado (venda ou antecipação). Não há referência ausente ou ambígua nesses 13 ajustes.
- EC, modalidade, parcelas, taxa aplicada e data original conferem nos 13 pares. Os valores de bruto, taxa e líquido de cada ajuste são exatamente o oposto dos valores da operação referenciada; as três somas por par são zero. Os sinais são coerentes e nenhuma anulação supera o bruto original.
- Não há outro registro em `01 + 06` que referencie essas 13 operações. Nenhuma referência preenchida é compartilhada por dois movimentos no conjunto. Isso afasta anulação repetida identificável por `id_referencia` nestes arquivos, sem provar inexistência de registros omitidos ou duplicação com IDs/referências incorretos.
- Bridge: `TX88447044 → TX88425142` (13/09) e `TX88447070 → TX88424537` (12/09), confirmando vigência anterior a 15/09.
- Reversões: `AN88447152 → AN88446397`, `AN88447178 → AN88446748` e `AN88447194 → AN88446551`; as antecipações estão no `01`, sem outra reversão referenciada no conjunto.
- A venda Kiwi `TX88447225` é nova no conjunto, EC `1038867654`, bruto R$ 5.480,00, crédito em 3 parcelas. Não é uma repetição de ID do `01`.

## Evidências dos 13 vínculos

Em todos os pares abaixo, EC, modalidade, parcelas, taxa aplicada e data original conferem. Os três valores exibidos são os da operação original; o ajuste contém os mesmos valores com sinal negativo. Portanto, bruto, taxa e líquido somam individualmente 0.00 por par. Não foi encontrado outro movimento com a mesma referência no conjunto.

| Ajuste / linha `06` | Referência / linha `01` | Data original | Bruto original | Taxa original | Líquido original |
|---|---|---|---|---|---|
| `TX88446992` / L2 | `TX88431689` / L1130 | 18/09/2026 | 1147,05 | 29,70 | 1117,35 |
| `TX88447011` / L3 | `TX88413573` / L140 | 03/09/2026 | 420,77 | 6,26 | 414,51 |
| `TX88447030` / L4 | `TX88438558` / L1578 | 25/09/2026 | 562,44 | 14,00 | 548,44 |
| `TX88447044` / L5 | `TX88425142` / L849 | 13/09/2026 | 1982,10 | 63,22 | 1918,88 |
| `TX88447057` / L6 | `TX88430977` / L1148 | 18/09/2026 | 3898,29 | 124,35 | 3773,94 |
| `TX88447070` / L7 | `TX88424537` / L754 | 12/09/2026 | 2603,31 | 83,04 | 2520,27 |
| `TX88447087` / L8 | `TX88422829` / L719 | 11/09/2026 | 8647,36 | 327,73 | 8319,63 |
| `TX88447093` / L9 | `TX88416714` / L370 | 06/09/2026 | 2620,34 | 70,48 | 2549,86 |
| `TX88447109` / L10 | `TX88428997` / L1045 | 16/09/2026 | 2747,67 | 87,65 | 2660,02 |
| `TX88447140` / L11 | `TX88432148` / L1239 | 19/09/2026 | 2366,18 | 61,28 | 2304,90 |
| `AN88447152` / L12 | `AN88446397` / L1442 | 22/09/2026 | 46080,41 | 967,68 | 45112,73 |
| `AN88447178` / L13 | `AN88446748` / L1810 | 29/09/2026 | 41690,09 | 875,49 | 40814,60 |
| `AN88447194` / L14 | `AN88446551` / L1533 | 24/09/2026 | 36583,37 | 768,25 | 35815,12 |

## Inconsistência concreta: bandeira em sete pares

| Estorno / linha `06` | Venda original / linha `01` | Bandeira na venda | Bandeira no estorno |
|---|---|---|---|
| `TX88447011` / L3 | `TX88413573` / L140 | AMEX | VISA |
| `TX88447030` / L4 | `TX88438558` / L1578 | ELO | VISA |
| `TX88447044` / L5 | `TX88425142` / L849 | HIPERCARD | ELO |
| `TX88447057` / L6 | `TX88430977` / L1148 | AMEX | ELO |
| `TX88447070` / L7 | `TX88424537` / L754 | ELO | VISA |
| `TX88447093` / L9 | `TX88416714` / L370 | VISA | AMEX |
| `TX88447109` / L10 | `TX88428997` / L1045 | VISA | ELO |

Há também variações de nome em seis desses pares, com EC igual em todos:

| Estorno | Nome na venda | Nome no estorno |
|---|---|---|
| `TX88447030` | MUNDO ABERTO INTERCAMBIO | Mundo Aberto |
| `TX88447044` | ESCOLA BRIDGE IDIOMAS | BRIDGE IDIOMAS |
| `TX88447057` | EDUABROAD | EDU ABROAD CONSULTORIA |
| `TX88447070` | ESCOLA BRIDGE IDIOMAS | BRIDGE IDIOMAS |
| `TX88447093` | MAPLE STUDY | MAPLE STUDY ASSESSORIA |
| `TX88447109` | EDUABROAD | EDU ABROAD CONSULTORIA |

Preservar os dois textos originais e associar pelo EC confirmado, sem sobrescrever fontes. Variação de nome não comprova troca de lojista.

**Interpretação e proposta técnica:** os IDs de referência únicos, ECs, datas e valores opostos sustentam o vínculo observado. As regras contratuais confirmadas não usam bandeira como dimensão da taxa; a diferença de bandeira, isoladamente, não altera a fórmula nem justifica excluir automaticamente o estorno. Isso não confirma que a bandeira divergente seja válida. Registrar pendência de qualidade com os sete pares, manter ambas as evidências e submeter a conferência a Helena, sem corrigir silenciosamente nem declarar os dados integralmente consistentes. Quando o desenvolvimento começar, o tratamento proposto é aplicar as regras conhecidas e manter a pendência na revisão humana. A análise das fontes está concluída; a resposta de Helena permanece pendente.

**Pergunta enviada pelo usuário à Helena, aguardando resposta:** “Helena, no complemento `06`, estes sete estornos têm bandeira diferente da venda apontada por `id_referencia` (tabela acima), embora EC, data original, modalidade, parcelas, taxa aplicada e os valores opostos confiram. Podemos manter esses vínculos para setembro e registrar a diferença de bandeira como erro de informação a corrigir com a Orbe? Se algum vínculo estiver incorreto, qual referência deve ser usada?”

O envio foi confirmado pelo usuário nesta conversa; não foram fornecidos horário ou permalink da mensagem. O texto acima registra o conteúdo da pergunta, sem representar resposta ou aprovação de Helena.

Não é necessário perguntar onde estão as 13 operações, qual envio prevalece por ID duplicado, nem se os ajustes são integrais em valor bruto: esses pontos foram conferidos. Semântica de futuros arquivos, reabertura de período aprovado e completude do mês continuam sem protocolo geral, mas não foram demonstrados como bloqueios deste complemento.

## Limites

Conferência de IDs, referências e campos das fontes; não apura comissão pela tabela contratada, divergência contratual, total por lojista nem efeito nas notas. Igualdade de `valor_taxa` com o oposto da operação original não transforma esse campo na comissão faturável. Os 1.957 IDs não equivalem a 1.957 contribuições elegíveis: Atlas e outras regras continuam exigindo seus tratamentos. Deduplicação de produção, decisões humanas, reprocessamento e geração/validação dos seis CSVs são requisitos para o desenvolvimento futuro. Não são pendências desta análise nem funcionalidades existentes. A pendência atual desta investigação é registrar a resposta de Helena quando chegar.
