# Memória do plano e comparação com a main — 17/10/2026

## Referência e sincronização

Pedido do usuário: sincronizar com a main, guardar o planejamento e comparar com o desenvolvimento atual. Atualização por fast-forward de `f8c222e` para `1a62692`, após `git fetch origin main` (8 commits). Sem commit/push nesta revisão. Os arquivos locais de pitch e `apresentacao/` foram preservados. `PROMPTS/MOMENTOS.md` local colidia com o arquivo adicionado na main: cópia integral em `MOMENTOS-local-pre-sync-2026-10-17.md`, com SHA-256 conferido antes da substituição.

Esta memória registra o plano anterior como referência e o que foi observado na revisão; não declara aprovação de Helena. O código e os CSVs oficiais não foram alterados nesta atividade. Novas afirmações em documentação remota não substituem automaticamente regras confirmadas do usuário.

## Planejamento a preservar

- Objetivo: nível extra, fechamento completo de setembro/2026, rastreabilidade, pendências explicadas e competência parametrizada para outubro.
- Núcleo determinístico Python; apresentação escolhida: subagente acoplável ao sistema da empresa. CLI faz parte do mínimo reproduzível; MCP e executável empacotado não eram frentes concorrentes escolhidas.
- Antes de investir na camada agêntica, demonstrar um comando que lê fontes e gera checkout por lojista com rastro e somas verificadas.
- Marcus: ingestão, normalização, cadastro, contratos e comissões. Raphael: bancos, notas, pendências, rastro e validação. Carlos: camada agêntica, transparência e integração. Revisão conjunta; essa divisão não autoriza delegação a agentes nem mensagens externas.
- Seis saídas em `saida/`, delimitador `;`, decimal com ponto, datas ISO, CNPJ de 14 dígitos, origens de negócio/linha física e soma de contribuições por `id_saida`.
- Valores com Decimal/ROUND_HALF_UP por linha. Checkout pela taxa contratada, estornos pela vigência da venda original e reversões anulando antecipação referenciada; Bridge muda em 15/09. Casa isenta set–dez, com devolução separada e sem cobrança à Orbe pelo acordo não comunicado. Atlas sem faturar até decisão comercial.
- Remessa: 50% do spread realizado, arredondado por operação; competência pela contratação; nota única para Ponte. Duplicata concreta 0162 conta uma vez; quatro negativos conhecidos excluídos/contestados. Não generalizar essas decisões a eventos novos. Tolerância delegada à equipe, com justificativa.
- Bancos: contrapartida do movimento; baixar provisões anteriores sem reconhecer receita/despesa novamente. Origem desconhecida permanece pendente; contas ambíguas precisam de justificativa.
- `06` é complemento conhecido de setembro, 14 movimentos, 13 referências, sete lojistas. Não substitui o `01`. Diferença isolada de bandeira nos sete pares foi esclarecida: preservar como evidência, sem pendência nem contestação.
- Preservar fontes e versões de execução; repetição idêntica conta uma vez. ID conflitante sem precedência confirmada exige bloqueio localizado. Ajuste não herda aprovação anterior.
- Continuar partes independentes quando fonte/regra falta; distinguir apurado/provisório/bloqueado de aprovação. Layout desconhecido não é adaptado silenciosamente. Completude mensal não é presumida.
- Não executar pagamentos, devoluções, emissão fiscal, lançamentos ERP ou contestações externas. Não calcular lucro/custo financeiro sem dados. Helena revisa e aprova; taxa/cadastro dependem primeiro do comercial.
- Pendências anteriores: Atlas; precedência em conflitos; escolha/justificativa da tolerância; contas ambíguas; hospedeiro/modelo/SDK/canal de revisão; protocolo geral de ajustes e completude. A análise pontual do `06` já estava encerrada e não bloqueava o núcleo.

Fontes do plano: `AGENTS.md`, `HIPOTESES.md` e `PROMPTS/outputs/arquitetura-stack.md` no commit `f8c222e`; checkpoint e feedback permanecem planos/evidências de orientação. A referência por commit preserva a versão anterior mesmo onde a main modificou a documentação.

## O que passou a existir

| Frente | Observado na main | Avaliação desta revisão |
|---|---|---|
| Ingestão | Formatadores CSV, XLSX por XML/ZIP, EML com XLSX e OFX; roteador de arquivos | Implementada para o pacote concreto; contrato de layout e múltiplos arquivos ainda limitados |
| Checkout | Motor Python/Decimal, contratos, Bridge, Casa, Atlas, 01 + 06 | Execução demonstrada; generalização e integridade de referências incompletas |
| Remessas | Participação por operação, deduplicação, negativos, divergências e nota Ponte | Implementada para o caso; conflitos, vigência/competência e base das divergências exigem revisão |
| Bancos | Regras de classificação, referências Aurora/FITID, pendências e trânsito | 184 movimentos exportados; não equivale a homologação das contas |
| Saídas | Seis CSVs, rastro expandido e manifestos JSON/Markdown | Reprodução exata demonstrada; somas consistentes internamente |
| Mínimo por comando | `src/app.py --data-dir ...`, funcionamento offline | Atendido para o conjunto recebido em ambiente isolado; README tem caminho específico de outro ambiente |
| Subagente | Grafo sequencial, adaptadores de triagem LLM e fallback local | Há orquestração; não identifiquei integração com hospedeiro nem ferramentas consultivas de explicação/revisão propostas |
| Executável | Script `src/build_exe.py` | Frente adicional à decisão anterior; build não verificado nesta revisão |
| Outubro/fechamento parcial | Campo de competência e status no estado | Não atende ainda: competência fixa, fontes obrigatórias no fluxo e sem estados por resultado |

## Evidências executadas

Ambiente: Python 3.14.7. Fontes originais extraídas sem edição do ZIP versionado para `work/revisao-main-2026-10-17/entrada/`, com cópia do `06` original. Execução a partir de pasta isolada para preservar `saida/` versionada. Chaves dos três provedores vazias no processo para verificar o caminho offline.

Comando efetivamente executado a partir de `work/revisao-main-2026-10-17/`:

```powershell
$env:PYTHONIOENCODING = 'utf-8'
$env:JEV_API_KEY = ''
$env:GEMINI_API_KEY = ''
$env:DEEPSEEK_API_KEY = ''
python ../../src/app.py --data-dir entrada
```

O processo gerou 35 comissões, 115 divergências, 21 notas propostas, 184 lançamentos, 190 pendências e 4.508 linhas de rastro. Os seis CSVs ficaram idênticos byte a byte aos versionados. Verificação das somas por ID nas cinco categorias: 545 resultados, sem diferenças. Isso prova consistência das somas com os valores exportados; não prova correção de todas as regras ou origem de cada evidência.

Saída monetária reproduzida pelo código atual: checkout R$ 203.735,34; remessas R$ 39.543,42. São resultados técnicos provisórios, não totais financeiros homologados nesta revisão.

Teste do efeito do complemento no motor: checkout apenas `01` = R$ 207.039,73; `01 + 06` = R$ 203.735,34; diferença = −R$ 3.304,39. Maple e Oxford permanecem positivos no cálculo atual. O detalhe dos sete lojistas e hashes está em `verificacao-main-2026-10-17.json`.

Teste negativo de repetição do arquivo: `processar_checkout([01, 06, 06], taxas)` produziu R$ 200.430,95, repetindo o abatimento de R$ 3.304,39. A falha é contar novamente a mesma entrada fornecida ao motor; não significa que rodar novamente a mesma CLI acumule receita, pois a exportação sobrescreve arquivos.

`python -m unittest discover -s tests -v`: 15 testes, 9 passaram e 6 deram erro. O teste Aurora depende de `C:/Users/marcus/Documents/Tarvo_Data_Pack_set2026`; os demais erros dependem de intermediários ausentes em `dados_formatados/` da raiz. A CLI isolada gera intermediários em sua própria pasta, por isso não corrige essas dependências da suíte. Parte dos testes aprovados lê saídas já versionadas; não é validação integral do pipeline a partir dos originais. Além disso, um teste exige indevidamente sete pendências por bandeira.

Logs e script auxiliar locais: `work/revisao-main-2026-10-17/cli.log`, `testes.log`, `verificar.py`, `verificacao.json`. `work/` é ignorado pelo Git; o JSON resumido foi preservado nesta pasta de memória.

## Diferenças e riscos prioritários

1. **Duplicatas e conflitos Orbe:** `src/engines/checkout_engine.py` percorre todas as linhas, sem deduplicar/bloquear o ID conflitante. O guardrail detecta colisões entre 01/06, mas o grafo acrescenta pendência depois de somar ambas. A repetição foi demonstrada no teste acima. O mapa de ingestão também guarda um único caminho por domínio (`src/graph.py:42`), sem inventário de vários complementos.
2. **Sete pendências indevidas de bandeira:** `checkout_engine.py:338` cria `DIVERGENCIA_CADASTRO_BANDEIRA`, contrário à confirmação preservada em AGENTS/HIPOTESES. São sete das 190 pendências; o teste atual reforça o comportamento incorreto. Nomes/bandeiras originais e relações deveriam ser evidência, sem decisão adicional por essa diferença isolada.
3. **Outubro não parametrizado:** `src/app.py:97` fixa `2026-09`. Os motores não filtram competência, a isenção Casa não testa limite set–dez e há nomes/discriminação de setembro fixos. Não há demonstração de processamento correto de outubro.
4. **Fechamento parcial e guardrails:** `src/graph.py:123` e `:146` exigem taxas/Orbe/Ponte por acesso direto ao dicionário; bancos também são obrigatórios. Relatório de erros críticos é armazenado, mas não controla bloqueio de resultados dependentes. Faltam estado/cobertura por resultado e avisos que permitam continuar frentes independentes.
5. **Execuções e revisão:** CSVs e manifestos são escritos com modo `w` (`generator.py:512`), sem histórico por execução. O manifesto atual não contém hashes de entrada nem identidade de execução/regra, apesar de o README prometer hashes. Status de aprovação é argumento de CLI, sem evidência/autor/escopo vinculado à versão. Não há comparação persistida entre execuções nem invalidação de aprovação por resultado.
6. **Referências e vigências:** reversões usam a taxa vigente na data do movimento (`checkout_engine.py:296`), sem buscar/anular a comissão exata referenciada. O motor não verifica em geral EC, valor, tipo e anulação anterior da referência. Isso pode coincidir no conjunto atual e falhar em condições novas. Contrato sem vigência aplicável pode cair no primeiro cadastro, e taxa inválida/vazia pode virar zero.
7. **Remessas:** conflitos duplicados preservam a primeira operação no total e descartam a seguinte, sem bloquear o valor ambíguo. Negativos novos são excluídos automaticamente por sinal (`cambio_engine.py:166`), generalizando a decisão dos quatro conhecidos. O excesso é calculado sobre `valor_brl` (`:207`), enquanto a regra exige a base PTAX de referência: revisar contra valor em moeda estrangeira × PTAX, sem homologar esse total de contestação. Limiar de 0,01 ponto percentual foi codificado, mas continua faltando conciliar justificativa/documentação. Não há filtro por data de contratação no motor.
8. **Rastro:** comissões/notas têm contribuições detalhadas, mas rastro de divergências/pendências é em parte cópia do valor final. Divergências de checkout recebem sempre arquivo 01 e pendências do 06 podem ser atribuídas ao 01. Ponte aponta intermediário formatado. Fechar somas não assegura referência física correta nem preservação integral de duplicatas/exclusões.
9. **Apresentação e alegações:** o produto implementado é sobretudo um pipeline com triagem semântica opcional; não há evidência de subagente acoplado, revisão humana persistente ou consultas de explicação propostas. README diz “homologada”, “outubro sem retrabalho” e “15 testes ... 100%”, acima das evidências locais. AGENTS/arquitetura ainda diziam que desenvolvimento não havia começado. MOMENTOS remoto afirma precedência Last-Write-Wins e deslocamento pós-aprovação, mas o código não implementa essas políticas e a regra geral não está confirmada no contexto fornecido; não adotar automaticamente essas alegações.

## Próxima ordem recomendada (não executada nesta sincronização)

1. Corrigir duplicatas/conflitos, bandeiras e referências; tornar a suíte reproduzível a partir de fontes/fixtures e testar os riscos financeiros.
2. Revisar divergências de remessa e contas bancárias propostas; documentar tolerância, distinguir fatos de decisões da equipe e resolver contradições documentais.
3. Parametrizar competência/vigências, persistir versões e cobertura, tratar fontes ausentes e layouts inválidos por dependência.
4. Integrar o subagente escolhido com explicações baseadas em ferramentas/evidências e canal de revisão; alinhar README/pitch ao que foi demonstrado. Totais só devem virar resultados homologados após revisão apropriada.

Conclusão da comparação: houve avanço substancial de planejamento para implementação executável do caso de setembro. O mínimo básico foi reproduzido, mas a prontidão para nível extra, outubro e operação governada ainda não está comprovada.
