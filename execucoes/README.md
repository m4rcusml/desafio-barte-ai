# Histórico de execuções

Cada fechamento preserva uma pasta exclusiva por competência:

```text
execucoes/2026-09/EXEC-<data-hora-UTC>-<identificador>/
  entradas/                 fontes brutas usadas no processamento
  codigo/src/               código Python usado, inclusive mudanças locais
  saida/                    seis CSVs, auditoria e histórico de consulta
  captura_entradas.json      hashes das cópias de entrada
  manifesto.json            competência, hashes, regras, código e execução anterior
  aprovacao.json            status declarado vinculado a essa execução
  diferencas.json           diferenças por lojista, nota e pendência
```

O processamento usa as cópias de entrada. A aplicação não sobrescreve pastas
finalizadas. Repetições recebem novos identificadores e mantêm os mesmos CSVs
quando os dados e regras não mudam. Arquivos `.env` não são copiados.

Na primeira migração, saídas antigas ainda sem snapshot são guardadas em
`LEGADO-*`. Essas pastas são identificadas como preservação apenas das saídas:
não se inventam as entradas ou o código histórico que não foram capturados.

As saídas são validadas em uma pasta `.pendente-*` antes da finalização. Falhas
de cálculo não substituem `saida/`; falhas de publicação tentam restaurar ambos
os destinos. Pastas pendentes podem permanecer para investigação. Se um snapshot
foi finalizado e a publicação falhou, ele continua recuperável; a execução informa
erro e os destinos anteriores são restaurados quando o sistema de arquivos permite.

`APROVADO_POR_HELENA` é uma declaração do operador, não uma autenticação de Helena.
O registro inclui identificador, hashes de entradas/saídas, versão das regras e
hash do código. Mudanças exigem revisão da nova execução; a aprovação registrada
na execução antiga permanece intacta. O consultor pode ler uma versão anterior:

```bash
python -m src.agent.consultant --summary --output-dir execucoes/2026-09/<id_execucao>/saida
```

O histórico é local e seus dados gerados ficam fora do Git. Faça cópia de segurança
da pasta inteira; publicar o código no GitHub não envia esse histórico. Essa
preservação não é armazenamento inviolável: quem tem acesso ao disco pode alterar
arquivos. Não há garantia de transação entre volumes, de recuperação automática
após queda de energia ou de publicação simultânea por vários processos.
