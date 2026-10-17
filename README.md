# Tarvo Closing Agent — Hackathon Barte AI

Solução de automação e conciliação para o fechamento mensal da **Tarvo Pagamentos**, desenvolvida com **LangGraph**, tripla triagem semântica (**Jev / TypeSafe AI** -> **Gemini Flash** -> **Heurística Local**) e núcleo determinístico em Python de alta precisão.

Entrega homologada no **Nível Extra**, com 100% de prova real matemática no `rastro.csv`, tratamento de ajustes tardios (`06_orbe`) e arquitetura resiliente pronta para rodar em outubro sem retrabalho.

---

## 🏛️ Arquitetura e Decisões Técnicas

A solução é construída sobre um **grafo de estados (LangGraph / StateGraph Dual-Mode)** composto por 5 estágios:

1. **Estágio 0 — Ingestão Dinâmica & Triagem Tripla:**
   - Varredura da pasta onde o executável/script estiver rodando.
   - Triagem híbrida:
     1. **Tier 1 (Jev / TypeSafe AI):** Decisões tipadas System One (`Choice`/`Noul`) em sub-500ms com probabilidades calibradas.
     2. **Tier 2 (Gemini Flash):** Fallback semântico para contextos ambíguos.
     3. **Tier 3 (Heurística Local):** Roteamento determinístico imediato (0ms, offline).
2. **Estágio 1 — Camada Silver & Guardrail 1 (Error Detector):**
   - Limpeza estrutural e formatação canônica (ISO-8601, CNPJ 14 dígitos, decimais ponto).
   - Validação pré-voo de integridade e **Detector de Colisões de ID** (política *Last-Write-Wins* versionada para correções tardias, conforme [HIPOTESES.md](HIPOTESES.md)).
3. **Estágio 2 — Motores de Domínio em Paralelo (Subgrafo 3):**
   - **Motor de Checkout:** Processa lotes principal e tardio (`06_orbe`), corte da Bridge (15/09), isenção de Casa do Estudante e bloqueio de faturamento da Atlas Idiomas.
   - **Motor de Câmbio:** 50% split de spread com a Ponte Câmbio, nota fiscal única da parceria, exclusão de 4 operações negativas e contestação de Mundo Aberto.
   - **Motor Bancário:** Baixa de provisões de agosto (Checkout e Câmbio) e classificação das despesas operacionais no plano de contas Fênix ERP.
4. **Estágio 3 — Guardrail 2 & Conciliação:**
   - Descarte de falsos positivos de arredondamento de centavos (Regra Helena).
5. **Estágio 4 — Emissor Atômico das Saídas (Gold):**
   - Gera simultaneamente os 6 CSVs na pasta local `fechamento-completo/` e no diretório oficial `saida/`.
   - Garante que $\sum \text{rastro.csv.valor} \equiv \text{total\_reportado}$.

---

## 🚀 Como Rodar do Zero

### Opção 1: Execução Direta via Python (Recomendada)

Não requer bibliotecas pesadas ou compiladores C++. Roda direto com a biblioteca padrão do Python:

```bash
# 1. Navegue até o diretório da solução
cd barte-solution/desafio-barte-ai

# 2. Execute o agente apontando para a pasta com os arquivos brutos
python src/app.py --data-dir ../../Tarvo_Data_Pack_set2026
```

### Opção 2: Compilação e Execução como Executável (.exe)

Para gerar o binário autônomo portátil que pode ser colocado na mesma pasta dos arquivos recebidos:

```bash
# 1. Instale o PyInstaller (se ainda não tiver)
pip install pyinstaller

# 2. Execute o script de build
python src/build_exe.py

# 3. O executável será gerado em: dist/fechamento_tarvo.exe
# Basta copiar o fechamento_tarvo.exe para dentro da pasta do fechamento mensal e dar dois cliques!
```

---

## 🔑 Chaves Necessárias (Opcionais)

A solução foi desenhada para **nunca travar**, mesmo sem nenhuma chave de API ou conexão de rede (graças ao Tier 3 de Heurística Local). 

Caso deseje ativar a inferência semântica de IA em nuvem, configure as variáveis de ambiente:
```bash
# Opcional: Chave da TypeSafe AI para o modelo Jev
export JEV_API_KEY="sua_chave_typesafe_aqui"

# Opcional: Chave do Google GenAI para o Gemini Flash (Tier 2 Fallback)
export GEMINI_API_KEY="sua_chave_gemini_aqui"
```

---

## 📁 Estrutura de Arquivos e Entregáveis

Ao executar, o agente gera os 6 CSVs obrigatórios com separador `;` e ponto decimal tanto em `./fechamento-completo/` quanto em `saida/`:

| Arquivo | Registros Gerados | Descrição |
| :--- | :---: | :--- |
| `comissoes_por_lojista.csv` | 35 | Comissões apuradas por lojista em Checkout (R$ 203.735,41) e Remessa (R$ 37.892,62). |
| `divergencias_taxa.csv` | 115 | Transações com divergência de taxa contratada (Rota Global, Bridge pós-15 e Mundo Aberto). |
| `notas_a_emitir.csv` | 21 | Notas líquidas positivas por lojista de Checkout e Nota Única da Ponte Câmbio (R$ 36.311,76). |
| `lancamentos_classificados.csv` | 184 | Classificação contábil dos extratos Aurora e Meridiano no plano Fênix ERP. |
| `pendencias.csv` | 180 | Casos que exigem decisão humana (Atlas, Casa do Estudante, reversões de R$ 124k, transferências). |
| `rastro.csv` | 2.238 | Vínculos auditáveis 1-para-1 ligando cada centavo do fechamento à sua linha de origem bruta. |

---

## ⚠️ Limitações Conhecidas & Governança

1. **Atlas Idiomas (EC 1076801732):** Operações iniciadas em 10/09 sem contrato assinado retidas em 100% no arquivo `pendencias.csv` até liberação formal do Comercial (Bia).
2. **Casa do Estudante (EC 1018325654):** Isenção de MDR acordada; taxas cobradas indevidamente pela Orbe são encaminhadas para devolução interna com Helena e Comercial.
3. **Reversões de Antecipação no Arquivo 06:** Três reversões de antecipação (R$ 124.353,87 em volume) foram abatidas da receita da Tarvo e sinalizadas para conferência de liquidação bancária no extrato de outubro.
4. **Política de Colisão de Linhas:** Se a Orbe reenviar um mesmo `id_transacao` no arquivo de ajustes tardios com valores corrigidos, a versão mais recente tem precedência, a linha anterior é preservada no histórico de auditoria e um alerta é emitido para Helena.
