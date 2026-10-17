# Tarvo — documento de leitura da entrega

Revisão técnica de 17/10/2026. Código de referência: main `cd2d849`, com revisão
documental posterior. Dados, empresas e pessoas do case são sintéticos.

## Problema e solução entregue

O financeiro relatou oito dias úteis para fechar o mês, com fontes fragmentadas,
associação manual de cadastros, taxas desatualizadas e decisões concentradas em
Helena. São estimativas do cliente; não medimos ainda redução de prazo ou custo.

A aplicação lê os arquivos recebidos, apura comissões de checkout e remessas,
identifica divergências, propõe notas e contrapartidas bancárias e apresenta
pendências com motivo, responsável e origem. Os cálculos são determinísticos em
Python, com `Decimal` e `ROUND_HALF_UP` por linha. O subagente consultivo explica
os resultados. A aprovação financeira permanece humana e o fechamento real está
`PROVISORIO`, mesmo quando o estado técnico é `CONCLUIDO`.

## Níveis do regulamento

| Nível | Evidência funcional |
|---|---|
| Mínimo | Comissão de checkout por lojista, com rastro |
| Alvo | Mínimo, remessas, divergências por transação, notas propostas e classificação dos dois bancos |
| Extra | Mínimo e alvo, rastro dos resultados, pendências explicadas e outubro parametrizado |

A cobertura foi demonstrada no data pack de setembro (`01 + 06`) e em cenários
sintéticos de outubro. Isso não homologa o gabarito privado da banca, as contas
contábeis nem qualquer layout ou evento futuro. Fontes inválidas, dependências
ausentes e regras desconhecidas exigem diagnóstico e revisão.

## Fluxo e tecnologias verificadas

1. Capturar as fontes e o código em uma execução identificada.
2. Triar os arquivos e validar/normalizar os layouts suportados, preservando a origem.
3. Apurar checkout, remessas e classificação bancária por competência.
4. Conferir a soma do rastro para cada resultado antes da publicação.
5. Preservar a execução em `execucoes/` e publicar os seis CSVs e manifestos.
6. Consultar resumo, lojista, pendências ou composição de um ID no subagente.

O grafo usa LangGraph quando disponível e possui executor nativo em Python.
A triagem possui clientes opcionais Jev, Gemini e DeepSeek, além de heurística
local. A execução sem chaves e as contingências foram testadas; disponibilidade,
qualidade e latência desses serviços externos não foram homologadas. Classificar
um arquivo pela IA não autoriza interpretar arbitrariamente um layout novo ou
escolher uma regra comercial. O núcleo pode funcionar sem chamadas a modelos.

Não há benchmark de latência de produção. Não se promete execução inferior a
0,1 segundo, disponibilidade irrestrita, partidas dobradas completas ou conciliação
de todos os recebíveis. A apresentação verificada usa CLI Python e subagente;
o build do EXE é opcional e não foi validado nesta revisão.

## Regras e escolhas com efeito financeiro

- Checkout: bruto × taxa contratada, por modalidade e vigência; estorno usa a
  vigência da venda original e reversão abate a antecipação referenciada.
- Bridge: condições anteriores até 14/09 e novas a partir de 15/09; não há uma
  única taxa válida para todas as modalidades. Os estornos do 06 usam a venda original.
- Casa do Estudante: isenção de MDR/antecipação de setembro a dezembro. O saldo
  de checkout é `-5.50` por estorno anterior à isenção e não gera nota. A devolução
  de `15396.77` permanece separada, com 118 contribuições no rastro de `PEN-0058`.
  A isenção não comunicada não gera cobrança contra a Orbe.
- Atlas: 57 operações com `7876.05` de taxas observadas ficam pendentes de
  contrato/comercial; esse valor não é receita contratual confirmada.
- Cadastros Kiwi e duas Horizonte: vínculos confirmados pelo financeiro; taxa
  observada ou semelhança de nome não confirma identidade ou contrato.
- Remessa: 50% do spread realizado elegível, arredondado por operação, com
  competência pela contratação e uma única nota proposta para a Ponte.
- Mundo Aberto: 23 cobranças a maior, total `1418.88`, calculadas por
  `valor_me × (taxa_cliente − PTAX × (1 + spread_contratado))`. A participação
  continua pelo realizado; contestação não é dedução automática da nota.
- Tolerância de remessa: excesso `>= 0.01` ponto percentual no motor. O filtro
  posterior de `0.005` p.p. não amplia essa seleção. Justificativa e risco de
  omitir diferenças pequenas estão em P1 de [HIPOTESES.md](HIPOTESES.md).
- Sete diferenças de bandeira do 06: preservar evidência e referência, sem
  pendência ou contestação apenas por bandeira, conforme Helena.
- Cópias idênticas contam uma vez; IDs conflitantes bloqueiam todas as versões.
  Na Ponte, conflitos são registrados como `OPERACAO_DUPLICADA` com descrição
  explícita do bloqueio; na Orbe, como `DUPLICIDADE_CONFLITANTE`.

## Classificação bancária e decisão humana

Os 184 movimentos são classificados em contas existentes do plano Fênix. Baixas
de folha/tributos de agosto e recebimento Ponte já registrado não reconhecem
novamente receita ou despesa. Despesas correntes entram no mês conforme os fatos
confirmados. As contas específicas são propostas da equipe.

| Aurora | Valor | Conta proposta | Método/confiança | Pendência |
|---|---:|---|---|---|
| L34 | -112220.15 | 2.1.01.001 | REGRA/1.00 | Repasse Atlas sujeito a revisão |
| L50 | 7350.00 | 1.1.09.002 | REGRA/1.00 | Crédito sem origem |
| L60 | -137081.62 | 2.1.01.001 | REGRA/1.00 | Repasse Atlas sujeito a revisão |
| L65 | 12400.00 | 2.1.01.001 | REGRA/1.00 | Devolução de repasse sem causa |
| L92 | -300000.00 | 1.1.09.001 | REGRA/1.00 | Transferência em trânsito |

`REGRA/1.00` descreve a aplicação da regra proposta, sem aprovar a origem ou a
operação pendente. L65 recompõe obrigação de repasse; L34/L60 baixam obrigação
de repasse, mantendo investigação do contrato e autorização. Sem regra conhecida,
o sistema usa transitória `1.1.09.002`, `HUMANO/0.00` e pendência. P2 de
`HIPOTESES.md` explica as alternativas e seus impactos.

## Resultados reproduzidos — setembro/2026

| Arquivo em saida/ | Registros | Resultado |
|---|---:|---|
| comissoes_por_lojista.csv | 35 | Checkout 203735.34; remessas 39543.42 |
| divergencias_taxa.csv | 115 | Checkout 1576.23; remessas 1418.88 |
| notas_a_emitir.csv | 21 | 20 checkout + 1 Ponte; total 243284.26 |
| lancamentos_classificados.csv | 184 | 84 Aurora + 100 Meridiano; classificação proposta |
| pendencias.csv | 68 | Motivo e responsável, com rastro |
| rastro.csv | 4503 | Somas conferidas para 423 resultados |

Notas superam comissões em `5.50` porque o saldo negativo da Casa não gera nota.
Valores de pendências se sobrepõem a outras visões e não podem ser somados a
notas/divergências como ganho financeiro único. Soma correta do rastro comprova
consistência, sem substituir validação das fórmulas e decisões de negócio.

## Execução e governança

Na raiz do repositório, com Python 3.14 usado nesta verificação:

```bash
python -m zipfile -e dados/originais/Tarvo_Data_Pack_set2026.zip dados/entrada
python -c "import shutil; shutil.copyfile('dados/originais/06_orbe_ajustes_tardios_set2026.csv', 'dados/entrada/06_orbe_ajustes_tardios_set2026.csv')"
python src/app.py --data-dir dados/entrada --competencia 2026-09
python -m src.agent.consultant --summary --competencia 2026-09
python -m unittest discover -s tests -v
```

Para outubro, apontar `--data-dir` para suas fontes e usar `--competencia 2026-10`.
O complemento 06 é obrigatório especificamente para setembro. Sua ausência gera
fechamento parcial e pendência, enquanto partes independentes continuam.

Cada execução preserva entradas, código, resultados, hashes, versão das regras,
comparação e aprovação declarada. Mudanças não herdam a aprovação antiga; a
execução anterior permanece preservada. `APROVADO_POR_HELENA` é declaração do
operador, sem autenticação de Helena. Consulte [execucoes/README.md](execucoes/README.md)
para limites de backup, concorrência, falhas e armazenamento local.

## Entrega geral e limitações restantes

Os 40 testes cobrem setembro, outubro sintético, conflitos, fontes incompletas,
preservação de versões e proteção de publicação. A aprovação financeira real
continua provisória. O subagente não paga, emite nota fiscal, lança no ERP ou
aprova contratos/exceções.

O roteiro local foi atualizado com os números verificados. O deck remoto exige
sincronização editorial própria; editar este repositório não altera suas notas.
Ainda é necessário reunir o histórico integral das sessões de IA e confirmar
postagens/checkpoints e horários exigidos. `PROMPTS/MOMENTOS.md` registra quatro
intervenções, mas não substitui os históricos integrais. Não há alegação de
entrega geral completa nem de homologação pela banca.

Evidências da revisão: [relatório de revalidação](PROMPTS/memoria/revalidacao-main-cd2d849-2026-10-17.txt).
Registros antigos em `PROMPTS/` preservam seu contexto histórico.
