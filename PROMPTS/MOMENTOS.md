# Momentos críticos de interação com a IA

Índice de quatro momentos da construção da solução; não substitui o histórico integral das sessões exigido pelo desafio.

O histórico de Marcus, incluindo construção e preparação, está em [marcus/INDICE.txt](marcus/INDICE.txt), com critérios de captura em [marcus/LEIA-ME.txt](marcus/LEIA-ME.txt) e [quatro momentos específicos](marcus/MOMENTOS.md). Os demais integrantes mantêm a responsabilidade por suas próprias sessões.

## 1. Triagem dos arquivos e contingência offline

Pedimos à IA uma triagem para arquivos atípicos e ajustes tardios; ela propôs uma cascata com Jev, Gemini, DeepSeek e heurísticas locais.
Adotamos a separação entre triagem e cálculo determinístico e verificamos o fallback local nos testes, sem tratar isso como prova dos serviços em nuvem.

## 2. Dependência de orquestração que falhou

Pedimos o uso de LangGraph, mas a instalação proposta pela IA encontrou uma dependência que exigia compiladores indisponíveis no ambiente Windows.
Corrigimos o caminho com um executor nativo em Python e verificamos a execução offline, mantendo o uso da biblioteca oficial quando disponível.

## 3. Ajustes tardios e escolha indevida entre registros conflitantes

Ao pedir a incorporação do arquivo 06, recebemos da IA uma proposta de precedência automática entre versões, incompatível com a ausência dessa regra no negócio.
Rejeitamos a escolha automática, exigimos bloqueio dos registros conflitantes com evidências e testamos a deduplicação e a revisão da aprovação após mudanças.

## 4. Classificação, referências e exemplos do pitch corrigidos

Ao pedir classificação e resumo para o pitch, a IA marcou método IA sem chamada a modelo, usou referências bancárias incorretas e inventou IDs e taxas, atribuindo toda a divergência de checkout à Rota.
Exigimos HUMANO/0 nos casos sem regra e conferimos linhas físicas, FITIDs e fontes do pitch: Rota tem 87 divergências e Bridge cinco, com exemplos reais TX88411252, TX88444329 e TX88447044; o índice recebido com cinco momentos foi preservado em [memória](memoria/MOMENTOS-recebido-cd2d849-2026-10-17.txt) e consolidado aqui em quatro para cumprir o regulamento.
