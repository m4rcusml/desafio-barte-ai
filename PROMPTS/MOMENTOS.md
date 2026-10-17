# Momentos críticos de interação com a IA

Índice de momentos da construção da solução; não substitui o histórico integral das sessões exigido pelo desafio.

## 1. Triagem dos arquivos e contingência offline

Pedimos à IA uma triagem para arquivos atípicos e ajustes tardios; ela propôs uma cascata com Jev, Gemini, DeepSeek e heurísticas locais.
Adotamos a separação entre triagem e cálculo determinístico e verificamos o fallback local nos testes, sem tratar isso como prova dos serviços em nuvem.

## 2. Dependência de orquestração que falhou

Pedimos o uso de LangGraph, mas a instalação proposta pela IA encontrou uma dependência que exigia compiladores indisponíveis no ambiente Windows.
Corrigimos o caminho com um executor nativo em Python e verificamos a execução offline, mantendo o uso da biblioteca oficial quando disponível.

## 3. Ajustes tardios e escolha indevida entre registros conflitantes

Ao pedir a incorporação do arquivo 06, recebemos da IA uma proposta de precedência automática entre versões, incompatível com a ausência dessa regra no negócio.
Rejeitamos a escolha automática, exigimos bloqueio dos registros conflitantes com evidências e testamos a deduplicação e a revisão da aprovação após mudanças.

## 4. Classificação sem IA real e referências bancárias incorretas

Pedimos a classificação dos extratos e a IA atribuiu método IA sem chamada a modelo, além de usar índices do intermediário no lugar das linhas físicas do Aurora.
Exigimos método HUMANO nos casos sem regra, confiança zero e pendência, e verificamos as linhas físicas e os FITIDs; no reteste de outubro, corrigimos também os nomes fixos de setembro e adicionamos teste com extratos renomeados.

## 5. Alucinação de IDs e taxas no resumo do pitch vs. totais corretos

Pedimos à IA um resumo dos resultados para o pitch. Os totais estavam certos, mas ela inventou IDs de transação no exemplo da Bridge e atribuiu toda a divergência de checkout à Rota Global com uma taxa (2,29%) que não existe na planilha.
Conferimos linha a linha nos arquivos originais e corrigimos: a divergência real é Rota (87 transações) + Bridge (5 vendas após o contrato novo), e usamos no exemplo da Bridge transações com rastro auditado nas linhas originais (TX88411252 na L11 do 01, TX88444329 e o estorno real TX88447044 na L5 do 06).
