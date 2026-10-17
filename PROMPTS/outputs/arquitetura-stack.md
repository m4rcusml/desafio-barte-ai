# Arquitetura e stack — Tarvo

## Decisões e estado

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
| Ingestão | CSV, XLSX, EML com anexo XLSX e OFX; identificação do arquivo e localização de cada registro |
| Normalização | Datas, valores, unidades de taxa e CNPJs, com conteúdo original preservado |
| Cadastro e contratos | Correspondências confirmadas EC/CNPJ, condições e vigências; ambiguidades viram pendências |
| Apuração | Checkout e remessas com regras explícitas, valores intermediários e arredondamento |
| Fechamento | Divergências, notas propostas, classificação bancária e pendências |
| Validação | Integridade, cobertura dos registros, referências, duplicidades e somas do rastro |
| Exportação | Seis CSVs obrigatórios e manifesto da execução |
| Consultas | Serviços delimitados para resultados, regras, fontes, rastro e indicadores |
| Subagente | Coordenação técnica, investigação de exceções, explicações e preparação de recomendações |
| Integração humana | Registro de decisões com autor, justificativa, fonte e vigência; reprocessamento por nova execução |

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

Saída proposta: identificador da execução, etapas concluídas, validações, resultados disponíveis, arquivos gerados, bloqueios, pendências e resumo com evidências. Conclusão técnica não significa aprovação humana do fechamento.

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
- Alterações inesperadas nos inputs devem ser detectadas. O comportamento de bloqueio global ou fechamento parcial permanece pendente da resposta registrada em `nossas-duvidas.md`; não apresentar isso como regra aprovada.

## Transparência e resultados do subagente

O hospedeiro deve permitir entender o que aconteceu sem exigir conversa contínua: estado das etapas, ferramentas chamadas, regras aplicadas, fontes, resultados e motivos das pendências. A experiência proposta é Helena revisar exceções com evidências e registrar decisões reutilizáveis.

Entregar como funções consultivas iniciais: explicação de um valor e seu rastro; briefing de pendências por responsável; minuta de contestação com operações e valores calculados pelo núcleo. Não somar impactos sobrepostos de comissão, nota, devolução e contestação como se fossem perdas independentes.

Respostas devem referenciar execução, resultados e evidências; sugestões devem ser identificadas. Conteúdo recuperado de arquivos e mensagens é dado de referência, não instrução ao agente. Não expor raciocínio interno do modelo como prova: apresentar justificativa verificável e consultas realizadas. Registrar versão de prompt/modelo e ferramentas, sem credenciais.

## Critérios técnicos de aceite

- Mínimo executa por um comando, sem depender de modelo ou chave de IA.
- Mesmas entradas e regras reproduzem os mesmos resultados financeiros; texto do agente pode variar sem alterar os valores.
- Os seis CSVs respeitam o contrato do desafio e as somas do rastro fecham por resultado.
- Testes cobrem arredondamento negativo, vigências, estornos anteriores à isenção, Atlas sem taxa, duplicata Ponte, negativos excluídos e classificação de provisões.
- O subagente não possui ferramentas de aprovação comercial ou de operação financeira externa.
- Nova competência não exige trocar o algoritmo; evento sem regra conhecida produz pendência, sem inventar condição.
- Dependências, comando real e limitações são documentados após verificação. Esses critérios ainda não constituem resultados de testes executados.

## Definições ainda pendentes

- Sistema hospedeiro, ponto de acionamento e canal de entrega dos resultados/revisões.
- Provedor/modelo e SDK agêntico; nenhuma integração ou contratação escolhida neste documento.
- Versões fixadas, adaptador OFX e interface técnica final.
- Tratamento de variação estrutural, fontes ausentes ou corrigidas, sujeito ao esclarecimento do financeiro e aos limites demonstráveis dos leitores.
