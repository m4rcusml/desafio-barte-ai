# Verificação de entrega mínima, alvo e extra — 17/10/2026

Versão avaliada: `aa5289a` da main. O commit posterior à revisão anterior ampliou a identificação de serviços de contabilidade; foi incorporado por fast-forward. Nenhuma correção de implementação foi feita nesta auditoria.

Fonte oficial lida pelo conector Google Drive: [instruções dos participantes](https://docs.google.com/document/d/1GwHs0lgLWXdw-jIrPyYAxyJ_xEJJxViE). Cópia textual da consulta em `instrucoes-oficiais-consulta-2026-10-17.txt`. Regras específicas complementares: AGENTS.md e HIPOTESES.md, com as confirmações de Helena ali registradas.

## Parecer

| Nível | Exigência oficial | Situação |
|---|---|---|
| Mínimo | Comissão de checkout por lojista, com rastro | **Atendido para o data pack de setembro recebido, incluindo o 06** |
| Alvo | Comissão das duas linhas, divergências de taxa, notas a emitir e lançamentos classificados | **Parcial: todos os tipos de saída existem, mas há erro confirmado nas divergências de remessa e validação contábil ainda incompleta** |
| Extra | Rastro completo de todos os números, pendências explicadas e execução de outubro sem retrabalho | **Não atendido integralmente: há falhas concretas de origem/pendências, repetição de entradas e competência fixa** |

Essa classificação é uma avaliação técnica dos critérios oficiais com as evidências disponíveis; não é homologação da banca nem aprovação financeira de Helena. Falha de generalização para eventos novos não apaga a evidência de checkout correto no conjunto atual. Por outro lado, presença de todos os arquivos não demonstra correção do alvo.

## Mínimo: evidência favorável

- CLI executada offline a partir das fontes originais extraídas do ZIP, com cópia do complemento 06, sem limpeza manual. Resultados em pasta isolada; arquivos oficiais preservados.
- 21 linhas de checkout por CNPJ; o bloqueio Atlas não gera comissão/nota. Casa tem abatimento anterior à isenção.
- Recálculo independente das contribuições, sem chamar o motor financeiro, usando movimentos Orbe brutos, cadastro/taxas normalizados, vigência da venda para estornos e reversão da comissão original referenciada: **R$ 203.735,34**, sem diferenças por lojista.
- Contribuições de comissão conferidas por valor, ID de transação e nome do arquivo original 01/06: nenhuma diferença encontrada.
- Notas positivas de checkout conferem com o recálculo; valores zero/negativos não geram nota.

Limite da independência: o recálculo utilizou a tabela de taxas normalizada pelo leitor existente e mapeamentos confirmados; não constitui confronto com o gabarito privado da organização nem validação de todos os layouts futuros. A execução da CLI requer as demais fontes no fluxo atual, embora o critério mínimo se restrinja ao checkout.

## Alvo: entregáveis presentes, correção parcial

| Item | Verificação | Parecer |
|---|---|---|
| Comissão checkout | Recálculo por linha e comparação por lojista sem diferenças | Atendido no conjunto atual |
| Comissão remessa | 50% do spread realizado, arredondado por operação, operação repetida contada uma vez e quatro negativos conhecidos excluídos; **R$ 39.543,42**, sem diferenças por cliente | Atendido no conjunto atual |
| Notas propostas | 20 notas checkout positivas + nota única Ponte; valores/tomadores conferem com as comissões recalculadas | Atendido no conjunto atual |
| Divergências | 115 linhas exportadas; **23 divergências de remessa com valor incorreto** | Não atendido integralmente |
| Bancos | 184 registros, contas existentes e que aceitam lançamento; datas ISO, métodos e confiança válidos | Implementado e formalmente válido; mérito contábil de cada movimento não homologado nesta auditoria |

**Erro monetário comprovado nas remessas:** o motor usa `valor_brl × diferença de spread`, mas a condição contratual é sobre PTAX. Recálculo por operação:

```text
cotação contratada = PTAX × (1 + spread contratado / 100)
excesso = valor em moeda estrangeira × (cotação cliente − cotação contratada)
arredondar o excesso por operação, ROUND_HALF_UP
```

Para as mesmas 23 operações: CSV = **R$ 1.440,14**; recálculo = **R$ 1.418,88**; excesso no CSV = **R$ 21,26**. Confirmação independente adicional pelo spread realizado menos spread contratual sobre ME × PTAX produz o mesmo R$ 1.418,88. Não usar o percentual `spread_pct` arredondado como substituto da cotação exata para essa prova: ele perde precisão.

O README/dossiê menciona R$ 1.418,88, mas isso não corrige o CSV. Corrigir o motor em `src/engines/cambio_engine.py:207` e regenerar divergências, rastro e manifestos. A participação e a nota Ponte continuam pelo spread realizado elegível; não deduzir a contestação desses valores.

## Extra: o que impede declarar atendimento

1. **Outubro exige alteração do código:** competência fixa em `src/app.py:97`, discriminações de setembro fixas, motores sem filtro de competência e isenção Casa sem limite temporal aplicado. Trocar arquivos não basta para demonstrar outubro correto.
2. **Origem incorreta em sete rastros:** `PEN-0176` a `PEN-0182` apontam o arquivo 01, mas suas transações pertencem ao 06. Os vínculos das comissões de checkout conferiram; o problema identificado é nestas pendências. Rastro Ponte aponta intermediário normalizado, e falta cadeia explícita até a linha do anexo original.
3. **Sete alarmes falsos:** `DIVERGENCIA_CADASTRO_BANDEIRA` pede correção/decisão apesar da orientação expressa de preservar como evidência sem pendência nem contestação. O teste que exige essas pendências também precisa mudar. As instruções oficiais dizem que alarmes falsos contam contra.
4. **Repetição não é neutralizada:** fornecer o 06 duas vezes ao motor altera novamente o checkout em −R$ 3.304,39. Conflito Orbe é somado apesar da pendência; duplicata Ponte conflitante preserva automaticamente a primeira contribuição. Isso viola os limites confirmados de repetição e conflito.
5. **Pendências não cobrem todas as situações necessárias:** faltam tratamento de agregado negativo checkout, bloqueio de dependências com dados/regra ausentes, cobertura por resultado e tratamento seguro de eventos novos. Motivo e responsável existem nas 190 linhas atuais, mas sua simples presença não demonstra que a lista é correta/completa.
6. **Versões e revisão:** exportação sobrescreve resultados/manifestos e não mantém identidade por execução/regra. Status de aprovação é parâmetro, sem vínculo a decisão humana evidenciada. Essas são lacunas do plano operacional confirmado; não são exigência de uma tecnologia específica como SQLite, LangGraph ou modelo de IA.

As somas do rastro fecham para os **545 resultados**, mas consistência interna não valida uma fórmula financeira incorreta nem um arquivo de origem errado.

## Requisitos transversais de entrega

| Requisito oficial | Estado local |
|---|---|
| `README.md`, `HIPOTESES.md`, `PROMPTS/`, `saida/`, `src/` | Presentes |
| Seis CSVs com colunas obrigatórias | Presentes; colunas extras de rastro são permitidas |
| CNPJs de 14 dígitos; datas ISO; métodos válidos; confiança 0–1; IDs únicos nas cinco saídas | Sem violações encontradas nas verificações executadas |
| Somas de rastro por resultado | Sem diferenças encontradas nas cinco categorias |
| Instruções de execução do zero | Comando funcional demonstrado, mas README ainda tem caminho específico de outro ambiente e afirmações não comprovadas |
| Limitações e premissas | Documentadas, porém com contradições entre planejamento, README, dossiê e MOMENTOS |
| Histórico de todas as sessões de IA, de construção e preparação | Não comprovado: há resumos e registros pontuais; não localizei export/transcript/link que cubra todas as sessões |
| `PROMPTS/MOMENTOS.md`, 2–4 momentos e pelo menos um erro da IA | Há quatro momentos e erros descritos; relatos sobre precedência/aprovação contradizem regras e código. Exigem revisão factual |
| Repositório público e link no thread até 18h30 | Não verificado; esta auditoria não enviou nada |
| Pitch e link no thread até 19h | Há base e roteiro locais, ainda com placeholders/contexto anterior à implementação; envio e versão final não verificados |

Não é necessário implementar uma UI, contratar um modelo, compilar um EXE ou usar LangGraph para cumprir os níveis oficiais. O subagente continua sendo a apresentação escolhida pela equipe, mas não deve ser confundido com uma exigência textual adicional da tabela de níveis.

## Prioridade para completar a entrega

1. Preservar o mínimo já demonstrado; corrigir a base das divergências de remessa e revisar classificações/contrapartidas com justificativa para fechar o alvo.
2. Remover pendências indevidas de bandeira, corrigir origens, deduplicar e bloquear conflitos sem precedência autorizada.
3. Parametrizar competência, datas e vigências; demonstrar execução com entradas de outubro e ausência de contaminação de setembro. Continuar partes independentes e preservar versões.
4. Tornar a suíte reproduzível e alinhada às regras: a revisão anterior encontrou 9 aprovações/6 erros por caminhos/intermediários e um teste que exige os falsos alarmes de bandeira. Não repetir a afirmação de 15/15 no README sem nova evidência.
5. Reunir históricos integrais de IA, corrigir alegações de homologação, alinhar o pitch aos números verificados e confirmar publicação/envio no canal autorizado pela equipe.

## Evidências locais

- `auditoria-niveis-2026-10-17.json`: comparações por saída, referências incorretas e 23 diferenças monetárias detalhadas.
- `verificacao-main-2026-10-17.json`: reprodução dos seis CSVs, efeito do 06 por lojista e teste de repetição da revisão anterior.
- `work/revisao-main-2026-10-17/auditar_niveis.py`, `auditoria-niveis.log`, `cli.log`: script e execução local, sob diretório ignorado pelo Git. Nesta auditoria, a CLI foi repetida com o commit `aa5289a`.
- Nenhuma implementação financeira ou saída oficial foi corrigida nesta verificação; os resultados divergentes permanecem visíveis para correção posterior.
