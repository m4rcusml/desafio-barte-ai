# Arquitetura e stack — Tarvo

## Decisões e estado

**O desenvolvimento do sistema ainda não começou.** As análises pontuais das fontes já realizadas não implementam o núcleo. Os ajustes de processamento abaixo são requisitos futuros, não pendências para concluir a investigação do `06`.

- **Decidido pela equipe em 17/10/2026:** apresentação por subagente, conforme instrução explícita do usuário nesta conversa.
- **Decidido:** núcleo de análises e cálculos determinístico em Python; IA para coordenação técnica, investigação, explicação e insights. Decisões comerciais e exceções sem regra permanecem humanas.
- **Prioridade:** mínimo de checkout por lojista com rastro e somas verificadas, executável por um comando, antes do investimento na camada agêntica. O objetivo final é o nível extra.
- **Propostas técnicas abaixo:** desenho a implementar, não inventário de funcionalidades existentes. Provedor/modelo, SDK agêntico e ambiente hospedeiro ainda não definidos.
- MCP e executável não serão desenvolvidos como apresentações concorrentes. Uma interface adicional só entra se necessária à integração escolhida e após o núcleo funcionar.

## Estrutura geral

Aplicação modular em um único projeto Python. O mesmo núcleo atende à execução direta por comando e às chamadas do subagente. Regras financeiras não ficam nos prompts.

Fluxo de dados: arquivos originais → ingestão → normalização e identificação → regras determinísticas → resultados, rastro e pendências → validações → exportação.

Fluxo agêntico: solicitação do sistema hospedeiro → escolha de ferramentas permitidas → execução/consulta do núcleo → investigação com evidências → relatório estruturado ao hospedeiro.

O subagente pode conduzir o processamento técnico sem supervisão contínua. A autonomia para executar etapas não se estende a aprovar contratos, inventar taxas, resolver exceções humanas ou mover dinheiro.

## Componentes

| Componente | Responsabilidade |
|---|---|
| Ingestão | CSV, XLSX, EML com anexo XLSX e OFX; múltiplos arquivos Orbe na competência, identificação do arquivo e localização de cada registro |
| Normalização | Datas, valores, unidades de taxa e CNPJs, com conteúdo original preservado |
| Cadastro e contratos | Correspondências confirmadas EC/CNPJ, condições e vigências; ambiguidades viram pendências |
| Apuração | Checkout e remessas com regras explícitas, valores intermediários e arredondamento |
| Fechamento | Divergências, notas propostas, classificação bancária e pendências |
| Validação | Integridade, cobertura dos registros, referências, duplicidades e somas do rastro |
| Exportação | Seis CSVs obrigatórios e manifesto da execução |
| Consultas | Serviços delimitados para resultados, regras, fontes, rastro e indicadores |
| Subagente | Coordenação técnica, investigação de exceções, explicações e preparação de recomendações |
| Integração humana | Registro de decisões com autor, justificativa, fonte e vigência; reprocessamento por nova execução |
| Controle de dependências | Determinar quais etapas/resultados podem continuar e quais dependem de fonte, condição ou decisão ausente |
| Validação de layout e avisos | Conferir estrutura esperada e registrar incompatibilidades com fonte, motivo, impacto e destinatário |

## Fronteiras da autonomia

| Atividade | Responsável e limite |
|---|---|
| Calcular comissões, diferenças, notas e agregados | Núcleo determinístico; o modelo não é calculadora nem fonte dos números |
| Iniciar apuração e exportar arquivos locais | Ferramentas técnicas com parâmetros validados e caminhos controlados pelo hospedeiro |
| Investigar valores e consultar evidências | Subagente usando consultas delimitadas e identificador de execução |
| Sugerir tratamento de ambiguidade ou redigir contestação | Subagente, identificando a sugestão e suas evidências; sem aplicar/enviar |
| Aprovar condição comercial | Comercial, com registro humano |
| Aprovar regra de fechamento, exceção e resultado final | Helena, com registro humano |
| Pagar, devolver, emitir nota fiscal, lançar no ERP ou enviar contestação | Fora do escopo |

As ferramentas do subagente não expõem SQL livre, terminal ou edição de regras. A interface humana de decisões é separada. O sistema pode registrar logs e gerar arquivos técnicos sem transformar isso em aprovação de negócio.

## Stack

| Parte | Tecnologia | Estado e finalidade |
|---|---|---|
| Núcleo | Python | Decidido; versão exata a fixar após verificar o ambiente |
| Aritmética | `decimal.Decimal` e `ROUND_HALF_UP` | Proposta alinhada ao arredondamento confirmado por linha/operação |
| Validação de dados e ferramentas | Pydantic | Proposta; estruturas tipadas e validação explícita de entradas/saídas |
| Persistência | SQLite com `sqlite3` | Proposta; execuções, registros, regras, resultados, rastro e pendências |
| Excel | `openpyxl` | Proposta; abas, células, valores e comentários |
| CSV, e-mail, hashes e configuração | `csv`, `email`, `hashlib` e `json` | Bibliotecas padrão; leitores e configurações sem dependências desnecessárias |
| OFX | Adaptador compatível com o arquivo recebido | Biblioteca/implementação a decidir após verificar o formato; preservar FITID |
| Execução direta | CLI Python | Necessária ao mínimo reproduzível; comando final somente após implementação e teste |
| Subagente | Adaptador de modelo com ferramentas tipadas | Forma escolhida; provedor, modelo, SDK e hospedeiro pendentes |
| Testes | `pytest` | Proposta; regras financeiras, casos de exceção e integração ponta a ponta |
| Distribuição | Repositório e dependências fixadas | Instalação reproduzível; sem obrigação de instalador gráfico ou dashboard |

Não há compromisso de construir Streamlit, uma API web ou infraestrutura externa. A integração inicial proposta é chamada Python ou processo CLI com entrada e saída estruturadas; depende da definição do hospedeiro.

## Contrato com o sistema hospedeiro

Entrada proposta: competência, identificador da solicitação, referências dos arquivos disponíveis e versão das regras/decisões. Arquivos devem ser resolvidos pelo hospedeiro; o modelo não escolhe caminhos arbitrários.

O conjunto de entradas deve admitir vários arquivos da mesma fonte. Para setembro/2026, incluir explicitamente `01_orbe_relatorio_comissoes_set2026.csv` e `06_orbe_ajustes_tardios_set2026.csv`, registrando no manifesto que o segundo é complemento conforme anúncio da organização. Não inferir essa relação apenas do nome, da ordem de chegada ou do hash.

Saída proposta: identificador da execução, etapas concluídas, validações, resultados disponíveis, arquivos gerados, bloqueios, pendências e resumo com evidências. Incluir cobertura das fontes, dependências ausentes, situação de cada resultado e versão de entradas/regras usada. Conclusão técnica não significa aprovação humana do fechamento.

Exemplos de ferramentas a implementar:

```text
executar_apuracao(competencia, conjunto_entradas_id, regras_versao)
validar_execucao(execucao_id)
exportar_resultados(execucao_id)
consultar_resumo(execucao_id)
consultar_resultado(execucao_id, id_saida)
consultar_rastro(execucao_id, id_saida)
listar_pendencias(execucao_id, filtros)
consultar_regra(regra_id)
consultar_indicadores(execucao_id, indicador, filtros)
```

Agregações, comparações e indicadores monetários são calculados por funções do núcleo. O modelo recebe seus resultados e explica. Aplicar limites de chamadas, tempo e retentativas, com registro de falhas; não repetir uma etapa indefinidamente. Falha do modelo não impede a execução direta do fechamento por comando.

## Dados, execução e rastreabilidade

- Guardar arquivos originais e hash, conteúdo bruto e normalizado, referência física e identificador de negócio. A operação e a linha física podem ter identidades diferentes.
- Persistir resultados monetários finais em centavos inteiros e taxas/intermediários em representação decimal exata; evitar ponto flutuante binário nos cálculos.
- Cada contribuição registra origem, regra/versão, vigência, fórmula e arredondamento. O resultado agregado e o rastro derivam das mesmas contribuições.
- Separar contribuições monetárias de evidências não monetárias, como respostas do financeiro e aprovações contratuais.
- Preservar execuções anteriores. Mudança de arquivo, regra ou decisão gera nova execução identificada; repetição não duplica receita nem linhas exportadas.
- Cada registro tem destino explicável: processado, duplicado, excluído por regra ou pendente. Valor desconhecido não é zero.
- Regras têm fonte e vigência. Taxa confirmada para setembro não se torna exceção permanente para todos os meses.
- Alterações inesperadas nos inputs devem ser detectadas e avisadas. O fechamento parcial de partes independentes foi confirmado por Helena; estados, dependências e revisões propostos abaixo implementam esse requisito.

## Fontes variáveis, fechamento parcial e revisões

### Requisito confirmado

Conforme resposta fornecida pelo usuário em 17/10/2026 e registrada em `nossas-duvidas.md`: mesmas fontes/colunas são o contrato mensal esperado; registros, lojistas e condições variam. Atrasos, ajustes Orbe posteriores e mudanças de layout podem ocorrer. A solução deve avisar, continuar partes independentes e identificar provisórios/bloqueios. Helena libera; para taxa/cadastro, o comercial decide antes.

### Desenho técnico proposto

1. **Inventário de entradas:** registrar fonte esperada, arquivos/versões recebidos, competência declarada, hash, relação entre arquivos quando conhecida e sua evidência, além do estado de leitura. Distinguir arquivo ausente, arquivo inválido e arquivo válido sem movimentos; nenhum deles equivale automaticamente a valor zero. Vários arquivos podem pertencer à mesma fonte/competência.
2. **Contrato de layout por leitor:** validar cabeçalhos, abas necessárias, campos, tipos e unidades. Layout incompatível bloqueia a ingestão afetada com erro localizado e aviso persistido; não tentar correspondência arbitrária de colunas pela IA. Mudança compatível só é aceita por regra explícita do leitor. O mês continua pelas dependências válidas.
3. **Dependências explícitas no Python:** cada cálculo declara fontes, condições e referências necessárias. Bloqueios propagam somente aos resultados dependentes, não ao mês inteiro por padrão. A decisão sobre prontidão é determinística, não opinião do subagente.
4. **Estados por resultado:** `APURADO` quando calculado com suas dependências válidas; `PROVISORIO` quando há valor calculável, mas cobertura/decisão pendente pode alterá-lo; `BLOQUEADO` quando faltam dados ou regra para calcular. Guardar motivo, dependência e responsável. Aprovação é campo separado (`PENDENTE`/`LIBERADO`), com autor, momento e escopo. Uma etapa apurada pode continuar aguardando liberação.
5. **Visão do agregado:** soma apenas das linhas conhecidas não é total completo. Exibir subtotal apurado e cobertura, marcar o agregado provisório ou bloqueado conforme suas dependências. Não preencher a parte desconhecida com zero nem emitir proposta de nota consolidada como definitiva se faltam contribuições necessárias.
6. **Revisão humana:** decisão de taxa/cadastro deve ter evidência do comercial antes da liberação de Helena. Aprovação fica vinculada à versão e aos resultados aprovados. Nova informação não herda automaticamente liberação antiga para resultados alterados.
7. **Arquivo atrasado ou corrigido:** manter a versão anterior; identificar se o novo arquivo é repetição exata, substituição ou ajuste incremental. Hash evita reingestão idêntica, mas hash diferente não prova que é complemento. Sem semântica conhecida, registrar pendência, não somar arquivos indiscriminadamente. Gerar nova execução e demonstrar diferenças; implementar recomputação integral por versão inicialmente, sem exigir mecanismo complexo de execução incremental.
8. **Aviso ao hospedeiro:** persistir alertas estruturados com fonte, falha/alteração, resultados afetados, ação necessária e responsável; retorná-los também na saída estruturada. A entrega do aviso ao usuário depende do canal do hospedeiro ainda a definir. O subagente explica os alertas; não decide ignorá-los ou aprová-los.

Exemplos de dependência: falta do relatório Ponte bloqueia remessas e sua nota, mas não impede checkout com fontes válidas; uma taxa desconhecida afeta o lojista correspondente, sem bloquear os demais. Classificar os extratos pode continuar quando os extratos e o plano de contas estão disponíveis, observadas as pendências específicas de classificação. Disponibilidade dessas partes não demonstra que o fechamento global está completo.

Exportar resultados parciais preservando as colunas obrigatórias; acrescentar situação/cobertura quando aplicável e manifesto por execução com alertas e bloqueios. Uma saída sem linhas calculáveis não deve aparentar total zero aprovado: registrar explicitamente sua ausência de cobertura no manifesto/pendências. Exportações e propostas de notas não equivalem a emissão fiscal nem aprovação.

Não alterar a regra já confirmada de ajustes Ponte no mês em que aparecem. A resposta inicial de Helena não definiu competência, formato ou reabertura para ajustes Orbe em geral. O anúncio posterior do `06` resolve formato, caráter complementar e competência apenas para esse envio, conforme a seção abaixo; reabertura automática continua sem autorização.

### Complemento Orbe `06` — aplicação concreta e mudanças necessárias

**Fonte:** anúncio da organização fornecido pelo usuário em 17/10/2026 (sem permalink da mensagem) e leitura do [arquivo 06](https://drive.google.com/file/d/1JFUOwyEUaQK_HkYGEJ54JbWdxwIGHgEN/view). São ajustes de setembro omitidos do relatório, no mesmo formato do `01`, obrigatórios para a entrega das 18h30. Isso confirma o conjunto `01 + 06` para esta entrega, sem estabelecer protocolo para qualquer outro ajuste ou provar completude do mês.

O `06` contém 14 movimentos de 30/09: 10 estornos, 3 reversões de antecipação e 1 venda. Afeta Dublin, Maple, Mundo Aberto, Bridge, Edu Abroad, Oxford e Kiwi. As duas vendas originais dos estornos Bridge são de 12 e 13/09; as três reversões apontam antecipações de Oxford (duas) e Maple (uma); a venda adicional é da Kiwi. O cruzamento com o `01` foi executado em 17/10 e está no [relatório com evidências](orbe-01-06-verificacao.md): 1.957 IDs únicos não vazios, sem duplicatas/conflitos sob o mesmo ID; as 13 referências são únicas, encontradas no `01`, com tipo esperado e sem outra anulação referenciada no conjunto. EC, data original, modalidade, parcelas e taxa aplicada conferem; bruto, taxa e líquido se anulam exatamente. Há sete diferenças de bandeira e seis variações de nome. Apuração contratual e efeito nas notas permanecem por executar. O script auxiliar e o JSON da análise foram removidos, com evidências consolidadas no relatório e sem comando de reprodução mantido. O desenho abaixo é requisito para desenvolvimento futuro.

1. **Ingestão e identidade:** validar o layout de ambos e usar o mesmo leitor, preservando arquivo, hash, linha física, conteúdo original, `id_transacao` e `id_referencia`. O ID de negócio serve para comparação entre arquivos; a identidade física deve preservar todas as ocorrências. Hash de arquivo sozinho não detecta sobreposição parcial.
2. **Repetição e conflito:** contar uma só contribuição para repetição idêntica, com evidência das ocorrências descartadas. Mesmo ID com conteúdo divergente exige diagnóstico dos campos e pendência; não implementar precedência automática por nome ou chegada. Não descartar silenciosamente diferenças aparentemente não financeiras sem critério explícito. Conflitos bloqueiam apenas resultados dependentes.
3. **Referências e cálculo:** conferir as 13 referências de estornos/reversões no conjunto e verificar anulações já registradas. Estornos usam a vigência da venda original, incluindo Bridge antes de 15/09; ausência da venda não é bloqueio automático se os campos e contratos disponíveis bastarem. Reversões devem identificar e anular a comissão da antecipação referenciada, com controle para não anulá-la duas vezes. Referência insuficiente, valor inconsistente ou alcance ambíguo gera pendência localizada. Manter cálculo contratual, sinais e arredondamento por linha; não substituir comissão por `valor_taxa`.
4. **Nova execução:** recomputar o conjunto completo com as mesmas versões de regras, preservando entradas e resultados anteriores. Gerar diferenças por lojista entre execução apenas com `01` e execução com `01 + 06`, isolando mudanças de regras caso também ocorram. Diferença de comissão deve fechar com as contribuições efetivamente incluídas, removidas ou alteradas no rastro.
5. **Dependências e revisão:** regenerar comissões, divergências, notas propostas, pendências e rastro afetados. Verificar os totais de Maple e Oxford após os abatimentos; não presumir nota negativa. Aplicar a regra de não gerar nota zero/negativa e encaminhar negativo ao financeiro. Remessas e classificação bancária continuam por suas fontes; se reexportadas na nova execução, identificar as versões usadas, sem inventar movimentos vinculados ao `06`. Resultados alterados aguardam revisão de Helena e não herdam aprovação anterior.
6. **Validação e cobertura:** verificar que cada uma das 14 linhas tem destino explicado e que repetir a execução não acrescenta valores. O cruzamento confirmou 1.957 registros com IDs únicos, sem comprovar elegibilidade de todos para comissão. Registrar cobertura do conjunto recebido; completude mensal depende de confirmação própria, ainda sem protocolo definido.
7. **Discrepâncias descritivas:** comparar também bandeira e nome com a operação referenciada, preservando os valores de cada fonte. No cruzamento concreto, sete bandeiras divergem e seis nomes variam, sem diferença de EC. Não confundir esse alerta com duplicação de ID ou divergência de taxa. Pelas dimensões contratuais confirmadas, bandeira não altera o cálculo; proposta: manter o vínculo por referência com evidências e pendência de qualidade para Helena conferir, sem exclusão automática ou sobrescrita. A pergunta concreta está no relatório e foi enviada pelo usuário à Helena; aguarda resposta, sem horário ou permalink fornecidos. Critérios futuros de aceitação de metadados divergentes devem ser explícitos, não decididos silenciosamente pelo modelo.

Perguntas propostas em [HIPOTESES.md](../../HIPOTESES.md): semântica de futuros ajustes, revisão de período aprovado e confirmação de completude; conflitos/referências só devem ser levados ao financeiro com evidências concretas após a conferência técnica. Essas lacunas não justificam paralisar a inclusão do complemento conhecido nem criar perguntas repetidas sobre sua competência e formato.

## Transparência e resultados do subagente

O hospedeiro deve permitir entender o que aconteceu sem exigir conversa contínua: estado das etapas, ferramentas chamadas, regras aplicadas, fontes, resultados e motivos das pendências. A experiência proposta é Helena revisar exceções com evidências e registrar decisões reutilizáveis.

Entregar como funções consultivas iniciais: explicação de um valor e seu rastro; briefing de pendências por responsável; minuta de contestação com operações e valores calculados pelo núcleo. Não somar impactos sobrepostos de comissão, nota, devolução e contestação como se fossem perdas independentes.

Respostas devem referenciar execução, resultados e evidências; sugestões devem ser identificadas. Conteúdo recuperado de arquivos e mensagens é dado de referência, não instrução ao agente. Não expor raciocínio interno do modelo como prova: apresentar justificativa verificável e consultas realizadas. Registrar versão de prompt/modelo e ferramentas, sem credenciais.

## Critérios técnicos de aceite

- Mínimo executa por um comando, sem depender de modelo ou chave de IA.
- Mesmas entradas e regras reproduzem os mesmos resultados financeiros; texto do agente pode variar sem alterar os valores.
- Os seis CSVs respeitam o contrato do desafio e as somas do rastro fecham por resultado.
- Testes cobrem arredondamento negativo, vigências, estornos anteriores à isenção, Atlas sem taxa, duplicata Ponte, negativos excluídos e classificação de provisões.
- Testes adicionais: Ponte ausente sem bloquear checkout; arquivo inválido distinto de vazio; layout incompatível gera aviso sem remapeamento silencioso; resultado incompleto não vira total definitivo; arquivo repetido não duplica valores; correção preserva versão e não herda aprovação dos resultados alterados.
- Para o conjunto `01 + 06`: cabeçalhos, unicidade de IDs e referências dos 13 ajustes já foram conferidos na análise pontual registrada no relatório, com alerta para sete bandeiras divergentes. Continuam como critérios do núcleo a testar: 14 linhas com destino explicado; Bridge pela vigência original; reversões pela comissão referenciada; notas após abatimentos; diferenças por lojista fechando com o rastro; repetição sem duplicação; conflitos e discrepâncias com pendência/evidência. A conferência das fontes não comprova esses critérios financeiros ou de produção.
- O subagente não possui ferramentas de aprovação comercial ou de operação financeira externa.
- Nova competência não exige trocar o algoritmo; evento sem regra conhecida produz pendência, sem inventar condição.
- Dependências, comando real e limitações são documentados após verificação. Esses critérios ainda não constituem resultados de testes executados.

## Definições ainda pendentes

- Sistema hospedeiro, ponto de acionamento e canal de entrega dos resultados/revisões.
- Provedor/modelo e SDK agêntico; nenhuma integração ou contratação escolhida neste documento.
- Versões fixadas, adaptador OFX e interface técnica final.
- Semântica dos demais ajustes Orbe (complemento/substituição e competência quando não declarada), tratamento de conflitos, revisão de períodos aprovados e critério de completude das fontes. O `06` está confirmado como complemento de setembro, no formato do `01`; isso não resolve as regras gerais. Layouts suportados pelos leitores e canal do hospedeiro para avisos e aprovações ainda precisam ser implementados/definidos. A diretriz de continuar partes independentes e explicitar provisórios/bloqueios já foi confirmada.
