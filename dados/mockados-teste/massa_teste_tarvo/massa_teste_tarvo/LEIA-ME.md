# Massa de teste + gabarito (case Tarvo, setembro/2026)

São arquivos fictícios no mesmo formato do data pack, com lojistas inventados, para rodar a solução e comparar com o gabarito.

## O que tem aqui

```
entrada/              os 7 arquivos, mesmos nomes e formatos do data pack (incluindo o 06 de ajustes tardios)
gabarito/             as 6 saídas esperadas, no formato de saida/ (CSV ;, ponto decimal, datas AAAA-MM-DD)
gabarito.xlsx         as mesmas 6 saídas + o mapa de pegadinhas, em abas, para ler sem código
mapa_pegadinhas.csv   onde está cada pegadinha e o que o gabarito espera dela
PREMISSAS.md          as regras que o gabarito segue (e quais ainda estão em aberto)
gerar_massa.py        gera tudo de novo (sempre igual: semente fixa)
gabarito.py           o cálculo do gabarito; mudou uma regra, muda aqui e roda de novo
```

## Como usar

1. Rodar a solução de vocês apontando para `entrada/` no lugar do data pack real.
2. Comparar a `saida/` gerada com `gabarito/`.

Na comparação:

- **Ignorar o `id_saida`.** Cada um numera do seu jeito. A comparação é pela chave de cada arquivo:

  | Arquivo | Chave |
  |---|---|
  | comissoes_por_lojista | `cnpj` + `linha_negocio` |
  | divergencias_taxa | `ref_origem` |
  | notas_a_emitir | `tomador_cnpj` + `linha_negocio` |
  | lancamentos_classificados | `banco` + `ref_origem` (comparar `conta_codigo`) |
  | pendencias | `tipo` + `ref_origem` |

- **Tolerância de R$ 0,01 por número.** O rastro da remessa tem meio centavo, porque é 50% do spread de cada operação.
- **Linhas com `regra_em_aberto` preenchido (R1, R3, R4):** diferença ali não é bug, é regra ainda não decidida (ver PREMISSAS.md).
- **Colunas extras do gabarito** (`comissao_contratada_brl`, `categoria_gabarito` etc.) são só informativas.
- **`metodo` e `confianca`:** não precisam bater. O que importa é a conta.

## Números de referência

| Saída | Esperado |
|---|---|
| Comissão CHECKOUT | 13 lojistas, R$ 28.712,34 (pela alternativa R1, contratada: R$ 28.625,68) |
| Comissão REMESSA | 9 lojistas, nota da Ponte de R$ 7.654,19 (33 operações válidas, 1 duplicada e 2 negativas fora) |
| Divergências | 22 de checkout (R$ 87,85, sendo 2 linhas R3 e 2 linhas R4) e 4 de remessa (R$ 378,05) |
| Notas | 14 (13 de checkout + 1 para a Ponte), total R$ 36.366,53 |
| Lançamentos | 105 (61 Aurora + 44 Meridiano), 1 HUMANO |
| Pendências | 9 |

Para gerar de novo: `python3 gerar_massa.py` (precisa de `openpyxl`).
