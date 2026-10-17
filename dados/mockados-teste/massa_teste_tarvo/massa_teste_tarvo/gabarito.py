"""
Gabarito da massa de teste Tarvo.

Calculado a partir da "verdade" plantada por gerar_massa.py (nao relendo os
arquivos de entrada). As regras estao em PREMISSAS.md; aqui cada regra aparece
com o mesmo codigo (R1..R4 = regras de checkout ainda em aberto).
"""
import csv
import os
import re
from decimal import Decimal as D, ROUND_HALF_UP

import openpyxl
from openpyxl.styles import Font, PatternFill

import gerar_massa as gm

C2 = D("0.01")
ARQ = gm.NOMES
STOP = {"LTDA", "ME", "EIRELI", "SA", "E", "DE", "DA", "DO", "DAS", "DOS"}

# Mapa de contas validado com o Raphael em 17/10 (folha e repasse 08/2026 baixam obrigacao/credito;
# devolucao de PIX fica para uma pessoa; PIX sem identificacao vai para 1.1.09.002 + pendencia)
MAPA_CONTAS = {
    "ORBE_TED": "1.1.03.001", "TARIFA": "4.2.01", "TRANSF_MERIDIANO": "1.1.09.001",
    "TRANSF_MERIDIANO_EM_TRANSITO": "1.1.09.001", "FOLHA": "2.1.04.001", "CONDOMINIO": "4.2.02",
    "REPASSE_LOJISTA": "2.1.01.001", "ISS": "2.1.03.003", "CLOUD": "4.2.03", "SOFTWARE": "4.2.04",
    "PIX_NAO_IDENTIFICADO": "1.1.09.002", "CONTABILIDADE": "4.2.06", "INSS": "2.1.04.002", "FGTS": "2.1.04.003",
    "IRRF": "2.1.03.004", "PIS": "2.1.03.001", "COFINS": "2.1.03.002", "DEVOLUCAO_PIX": None,
    "RECURSO_REMESSA": "2.1.02.001", "LIQ_PONTE": "2.1.02.001", "TRANSF_RECEBIDA": "1.1.09.001",
    "REPASSE_COMISSAO_PONTE": "1.1.03.002", "APLICACAO": "1.1.02.001", "RESGATE": "1.1.02.001", "IOF": "4.3.01",
    "SEGURO": "4.2.05", "RENDIMENTO": "3.2.01",
}


def q2(x):
    return x.quantize(C2, ROUND_HALF_UP)


def num(x):
    """Decimal -> texto com ponto, sem zeros inuteis alem de 2 casas."""
    s = format(x.normalize(), "f")
    if "." not in s:
        s += ".00"
    elif len(s.split(".")[1]) == 1:
        s += "0"
    return s


def norm(s):
    s = gm.sem_acento(s).upper()
    toks = re.sub(r"[^A-Z0-9]+", " ", s).split()
    return " ".join(t for t in toks if t not in STOP)


# --------------------------------------------------------------- identidade
def identificar_lojistas():
    """Aplica a regra 11/12: EC na tabela vigente -> casa; senao, nome normalizado igual
    a razao social (aba antiga) de um CNPJ que esta na tabela vigente -> casa + pendencia de cadastro;
    nome igual so a lojista sem linha vigente -> sem contrato; nenhum igual -> ambiguo."""
    vigentes = {x["cnpj"] for x in gm.LOJISTAS if x["tabela"] and x["aba"] in ("vigente", "ambas")}
    razoes_antigas = {norm(x["razao"]): x for x in gm.LOJISTAS if x["aba"] in ("antigo", "ambas")}
    nomes_vigentes = {norm(x["tabela"]): x for x in gm.LOJISTAS if x["tabela"]}
    ident = {}
    for x in gm.LOJISTAS:
        if not x["checkout"]:
            continue
        if x["ec_tab"]:
            ident[x["k"]] = ("EC", x)
            continue
        cand = None
        for nome in x["orbe"]:
            n = norm(nome)
            cand = nomes_vigentes.get(n) or razoes_antigas.get(n)
            if cand:
                break
        if cand is None:
            ident[x["k"]] = ("AMBIGUO", None)
        elif cand["cnpj"] not in vigentes:
            ident[x["k"]] = ("SEM_CONTRATO", cand)
        else:
            ident[x["k"]] = ("NOME", cand)
    return ident


def gerar(mundo, pasta):
    orbe, ponte, aurora, merid = mundo["orbe"], mundo["ponte"], mundo["aurora"], mundo["merid"]
    ident = identificar_lojistas()
    assert all(v[1] is None or v[1]["k"] == k for k, v in ident.items()), "regra de nome casou lojista errado"

    com, div, notas, lanc, pend, rastro, peg = [], [], [], [], [], [], []

    def r_add(ids, arq, ref, valor, detalhe=""):
        rastro.append(dict(id_saida=ids, arquivo_origem=arq, ref_origem=ref, valor=valor, detalhe=detalhe))

    def arq_orbe(r):
        return ARQ["orbe01"] if r["arq"] == "01" else ARQ["orbe06"]

    # ------------------------------------------------ comissao CHECKOUT (R1 em aberto)
    n = 0
    com_chk = {}
    for x in gm.LOJISTAS:
        if not x["checkout"] or ident[x["k"]][0] not in ("EC", "NOME"):
            continue
        linhas = [r for r in orbe if r["lk"] == x["k"]]
        n += 1
        ids = f"COM-CHK-{n:02d}"
        aplicada = sum(r["vt"] for r in linhas)
        contratada = sum(q2(r["bruto"] * r["ct"] / 100) for r in linhas)
        com.append(dict(id_saida=ids, cnpj=x["cnpj"], lojista=x["razao"], linha_negocio="CHECKOUT",
                        comissao_brl=num(aplicada), comissao_contratada_brl=num(contratada),
                        qtd_linhas_origem=len(linhas), regra_em_aberto="R1",
                        observacao="identificado por nome (EC fora da tabela)" if ident[x["k"]][0] == "NOME" else ""))
        com_chk[x["k"]] = (ids, aplicada, contratada, linhas)
        for r in linhas:
            r_add(ids, arq_orbe(r), r["id"], num(r["vt"]))

    # ------------------------------------------------ comissao REMESSA (50% do spread realizado)
    validas = [o for o in ponte if not o["dup"] and o["spread"] >= 0]
    n = 0
    com_rem = {}
    for x in gm.LOJISTAS:
        ops = [o for o in validas if o["lk"] == x["k"]]
        if not ops:
            continue
        n += 1
        ids = f"COM-REM-{n:02d}"
        total = sum(o["spread"] for o in ops) / 2
        com.append(dict(id_saida=ids, cnpj=x["cnpj"], lojista=x["razao"], linha_negocio="REMESSA",
                        comissao_brl=num(q2(total)), comissao_contratada_brl="", qtd_linhas_origem=len(ops),
                        regra_em_aberto="", observacao=""))
        com_rem[x["k"]] = ops
        for o in ops:
            r_add(ids, ARQ["eml"], o["num"], num(o["spread"] / 2), f"Operações linha {o['linha_xlsx']}")

    # ------------------------------------------------ divergencias CHECKOUT
    n = 0
    for k, (_, _, _, linhas) in com_chk.items():
        x = gm.L[k]
        for r in sorted(linhas, key=lambda r: (r["data"], r["id"])):
            if r["taxa"] == r["ct"]:
                continue
            n += 1
            ids = f"DIV-{n:03d}"
            dif = q2(r["bruto"] * (r["taxa"] - r["ct"]) / 100)
            aberta = "R3" if "R3_CENTAVO" in r["tags"] else ("R4" if "R4_ESTORNO_DIVERGENTE" in r["tags"] else "")
            div.append(dict(id_saida=ids, cnpj=x["cnpj"], linha_negocio="CHECKOUT", ref_origem=r["id"],
                            taxa_contratada_pct=num(r["ct"]), taxa_aplicada_pct=num(r["taxa"]),
                            diferenca_brl=num(dif), arquivo_origem=arq_orbe(r), tipo_lancamento=r["tipo"],
                            data=r["data"].isoformat(), valor_bruto=num(r["bruto"]), regra_em_aberto=aberta))
            r_add(ids, arq_orbe(r), r["id"], num(dif))
    # ------------------------------------------------ divergencias REMESSA (spread contratado x realizado)
    for o in validas:
        x = gm.L[o["lk"]]
        ct = gm.spread_contratado(x)
        aplic = (o["spread_pct"] * 100).quantize(C2, ROUND_HALF_UP)
        if aplic == (ct * 100).quantize(C2):
            continue
        n += 1
        ids = f"DIV-{n:03d}"
        dif = o["spread"] - q2(o["valor"] * ct)
        div.append(dict(id_saida=ids, cnpj=x["cnpj"], linha_negocio="REMESSA", ref_origem=o["num"],
                        taxa_contratada_pct=num((ct * 100).quantize(C2)), taxa_aplicada_pct=num(aplic),
                        diferenca_brl=num(dif), arquivo_origem=ARQ["eml"], tipo_lancamento="REMESSA",
                        data=o["dc"].isoformat(), valor_bruto=num(o["valor"]), regra_em_aberto=""))
        r_add(ids, ARQ["eml"], o["num"], num(dif), f"Operações linha {o['linha_xlsx']}")

    # ------------------------------------------------ notas
    n = 0
    for k, (_, aplicada, contratada, linhas) in com_chk.items():
        if aplicada <= 0:
            continue
        x = gm.L[k]
        n += 1
        ids = f"NF-{n:02d}"
        notas.append(dict(id_saida=ids, tomador_cnpj=x["cnpj"], tomador=x["razao"], linha_negocio="CHECKOUT",
                          valor_brl=num(aplicada),
                          discriminacao="Intermediação de pagamentos (MDR e antecipação) - competência 09/2026",
                          valor_alternativo_R1=num(contratada), regra_em_aberto="R1"))
        for r in linhas:
            r_add(ids, arq_orbe(r), r["id"], num(r["vt"]))
    n += 1
    ids = f"NF-{n:02d}"
    total_rem = sum(o["spread"] for o in validas) / 2
    notas.append(dict(id_saida=ids, tomador_cnpj=gm.PONTE_CNPJ, tomador=gm.PONTE_RAZAO, linha_negocio="REMESSA",
                      valor_brl=num(q2(total_rem)),
                      discriminacao="Intermediação de câmbio - participação de 50% no spread realizado - "
                                    "competência 09/2026",
                      valor_alternativo_R1="", regra_em_aberto=""))
    for o in validas:
        r_add(ids, ARQ["eml"], o["num"], num(o["spread"] / 2), f"Operações linha {o['linha_xlsx']}")

    # ------------------------------------------------ lancamentos
    n = 0
    for banco, evs, arq in [("AURORA", aurora, ARQ["aurora"]), ("MERIDIANO", merid, ARQ["meridiano"])]:
        for e in evs:
            n += 1
            ids = f"LAN-{n:03d}"
            conta = MAPA_CONTAS[e["cat"]]
            desc = e["desc"] if banco == "AURORA" else e["memo"]
            lanc.append(dict(id_saida=ids, banco=banco, ref_origem=e["ref"], data=e["data"].isoformat(),
                             descricao=desc, valor=num(e["valor"]), conta_codigo=conta or "",
                             metodo="REGRA" if conta else "HUMANO", confianca="1" if conta else "0",
                             categoria_gabarito=e["cat"]))
            r_add(ids, arq, e["ref"], num(e["valor"]))

    # ------------------------------------------------ pendencias
    n = 0

    def p_add(tipo, ref, valor, motivo, quem, origem):
        nonlocal n
        n += 1
        ids = f"PEN-{n:02d}"
        pend.append(dict(id_saida=ids, tipo=tipo, ref_origem=ref, valor_brl=num(valor), motivo=motivo,
                         quem_decide=quem))
        for arq, rref, v, det in origem:
            r_add(ids, arq, rref, num(v), det)

    for k, (modo, cand) in ident.items():
        x = gm.L[k]
        linhas = [r for r in orbe if r["lk"] == k]
        tot = sum(r["vt"] for r in linhas)
        orig = [(arq_orbe(r), r["id"], r["vt"], "") for r in linhas]
        nomes = ", ".join(sorted({r["nome"] for r in linhas}))
        if modo == "SEM_CONTRATO":
            p_add("LOJISTA_SEM_CONTRATO_VIGENTE", x["ec"], tot,
                  f"EC {x['ec']} ({nomes}) não está na tabela vigente; só existe na aba 'ANTIGO 2025 - nao usar'. "
                  "Comissão, divergência e nota não calculadas.", "Comercial", orig)
        elif modo == "AMBIGUO":
            p_add("LOJISTA_AMBIGUO", x["ec"], tot,
                  f"EC {x['ec']} ({nomes}) fora da tabela e o nome não bate exatamente com nenhum lojista "
                  "(candidatos: Nova Estrela Intercâmbio, Estrela Viagens). Comissão, divergência e nota não "
                  "calculadas.", "Comercial", orig)
        elif modo == "NOME":
            p_add("CADASTRO_EC_PENDENTE", x["ec"], tot,
                  f"EC {x['ec']} ({nomes}) casado pela razão social com '{x['tabela']}' (CNPJ {x['cnpj']}). "
                  "Comissão calculada; cadastrar o EC na tabela de taxas.", "Financeiro", orig)
    for o in ponte:
        if o["dup"]:
            p_add("OPERACAO_DUPLICADA", o["num"], o["spread"] / 2,
                  f"{o['num']} aparece duas vezes no relatório da Ponte (2ª marcada 'reprocessada'). Contada uma "
                  "vez; o total do rodapé da Ponte inclui a repetida. Contestar com a Ponte em até 5 dias úteis.",
                  "Financeiro", [(ARQ["eml"], o["num"], o["spread"] / 2, f"Operações linha {o['linha_xlsx']}")])
    for o in ponte:
        if not o["dup"] and o["spread"] < 0:
            p_add("SPREAD_NEGATIVO", o["num"], o["spread"] / 2,
                  f"{o['num']} ({o['cliente']}) com spread de R$ {o['spread']} ('{o['obs']}'). Fora da comissão "
                  "até alguém decidir se a Tarvo aceita dividir o prejuízo.", "Financeiro",
                  [(ARQ["eml"], o["num"], o["spread"] / 2, f"Operações linha {o['linha_xlsx']}")])
    for e in aurora:
        if e["cat"] == "PIX_NAO_IDENTIFICADO":
            p_add("CREDITO_NAO_IDENTIFICADO", e["ref"], e["valor"],
                  f"'{e['desc']}' classificado em 1.1.09.002; identificar o pagador.", "Financeiro",
                  [(ARQ["aurora"], e["ref"], e["valor"], "")])
        if e["cat"] == "DEVOLUCAO_PIX":
            p_add("LANCAMENTO_SEM_REGRA", e["ref"], e["valor"],
                  f"'{e['desc']}': crédito de lojista sem explicação; não classificado.", "Financeiro",
                  [(ARQ["aurora"], e["ref"], e["valor"], "")])

    # ------------------------------------------------ mapa de pegadinhas
    peg.extend(pegadinhas(mundo, ident))

    # ------------------------------------------------ escrever
    gpasta = os.path.join(pasta, "gabarito")
    os.makedirs(gpasta, exist_ok=True)
    tabelas = [
        ("comissoes_por_lojista.csv", com, ["id_saida", "cnpj", "lojista", "linha_negocio", "comissao_brl"]),
        ("divergencias_taxa.csv", div, ["id_saida", "cnpj", "linha_negocio", "ref_origem", "taxa_contratada_pct",
                                        "taxa_aplicada_pct", "diferenca_brl"]),
        ("notas_a_emitir.csv", notas, ["id_saida", "tomador_cnpj", "tomador", "linha_negocio", "valor_brl",
                                       "discriminacao"]),
        ("lancamentos_classificados.csv", lanc, ["id_saida", "banco", "ref_origem", "data", "descricao", "valor",
                                                  "conta_codigo", "metodo", "confianca"]),
        ("pendencias.csv", pend, ["id_saida", "tipo", "ref_origem", "valor_brl", "motivo", "quem_decide"]),
        ("rastro.csv", rastro, ["id_saida", "arquivo_origem", "ref_origem", "valor"]),
    ]
    for nome, linhas, obrig in tabelas:
        campos = obrig + [c for c in (linhas[0].keys() if linhas else []) if c not in obrig]
        with open(os.path.join(gpasta, nome), "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=campos, delimiter=";", lineterminator="\n")
            w.writeheader()
            w.writerows(linhas)
    with open(os.path.join(pasta, "mapa_pegadinhas.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["arquivo", "ref_origem", "pegadinha", "o_que_o_gabarito_espera", "regra"],
                           delimiter=";", lineterminator="\n")
        w.writeheader()
        w.writerows(peg)
    escrever_xlsx(os.path.join(pasta, "gabarito.xlsx"), tabelas, peg)
    return dict(com=com, div=div, notas=notas, lanc=lanc, pend=pend, rastro=rastro, peg=peg)


def pegadinhas(mundo, ident):
    out = []
    t = mundo["linhas_tab"]

    def add(arq, ref, peg, esp, regra):
        out.append(dict(arquivo=arq, ref_origem=ref, pegadinha=peg, o_que_o_gabarito_espera=esp, regra=regra))

    T = ARQ["tabela"]
    add(T, f"Taxas vigentes!linhas {t['pontofinal']}-{t['PF2']}", "Mesmo lojista em duas linhas: crédito à vista "
        "2,59% até 14/09 e 2,29% a partir de 15/09", "Taxa escolhida pela data da venda (estorno usa a data da venda "
        "original)", "R2 [DECIDIDO]")
    add(T, f"Taxas vigentes!linha {t['rumonorte']}", "Taxas gravadas como texto '1,49%' em vez de número",
        "Ler como 1,49 etc.; 2-6x contratado é 3,09%", "formato")
    add(T, f"Taxas vigentes!linhas {t['fiorde']} e {t['campusmundi']}", "CNPJ salvo como número: perdeu o zero à "
        "esquerda (13 dígitos)", "Completar com zero à esquerda até 14 dígitos", "formato")
    add(T, "Taxas vigentes!coluna CNPJ", "CNPJ ora com pontuação, ora só dígitos", "Saída sempre com 14 dígitos",
        "formato")
    add(T, f"Taxas vigentes!linhas {t['wombat']} e {t['estrelaviagens']}", "EC Orbe em branco ('EC pendente')",
        "Casar pela razão social da aba antiga (nome normalizado igual) + pendência CADASTRO_EC_PENDENTE",
        "R11 [PROPOSTA]")
    add(T, f"Taxas vigentes!linha {t['novaestrela']}", "EC em branco e a Orbe manda 'ESTRELA INTERCAMBIO', que "
        "lembra 'Nova Estrela Intercâmbio' e 'Estrela Viagens'", "Não casar por aproximação: pendência "
        "LOJISTA_AMBIGUO, sem comissão/divergência/nota de checkout. A remessa dela entra normal (Ponte traz CNPJ)",
        "R12 [PROPOSTA]")
    add(T, "ANTIGO 2025 - nao usar", "Lumen Idiomas só existe na aba antiga, mas tem movimento na Orbe",
        "Pendência LOJISTA_SEM_CONTRATO_VIGENTE; não usar as taxas de 2025", "R12 [PROPOSTA]")
    add(T, f"Taxas vigentes!linha {t['casabrasil']}", "Comentário na célula fala em 'condição especial' não "
        "formalizada", "Seguir a taxa da tabela (todas as linhas desse lojista batem com ela; nenhuma divergência)",
        "alarme falso")
    add(T, f"Taxas vigentes!linha {t['boasvindas']}", "Spread remessa escrito 'padrão'", "Vale 1,5%", "R9 [PROPOSTA]")
    add(T, f"Taxas vigentes!linhas {t['wombat']} e {t['rotalivre']}", "Spread remessa em branco",
        "Vale 1,5% (rodapé: 'spread em branco = padrão')", "R9 [PROPOSTA]")
    add(T, f"Taxas vigentes!linha {t['caminhos']}", "Spread negociado 1,2% mas a Ponte aplica 1,5%",
        "Uma divergência de REMESSA por operação da Caminhos", "R10 [PROPOSTA]")
    add(T, f"Taxas vigentes!linha {t['globoandante']}", "Lojista INATIVO, sem vigência e sem movimento",
        "Não gera comissão, nota nem pendência", "alarme falso")
    add(T, f"Taxas vigentes!linhas {t['polar']} e {t['rotalivre']}", "'só remessa': MDR em branco",
        "Só comissão de REMESSA", "formato")

    O1, O6 = ARQ["orbe01"], ARQ["orbe06"]
    desc = {
        "VIGENCIA_FRONTEIRA": ("Venda à vista Ponto Final em 14/09 (2,59%) ou 15/09 (2,29%)", "Sem divergência",
                               "R2 [DECIDIDO]"),
        "DIVERG_TAXA_ANTIGA": ("Ponto Final cobrada 2,59% depois de 15/09 (Orbe não atualizou a renegociação)",
                               "Divergência CHECKOUT", "R2 [DECIDIDO]"),
        "VIGENCIA_ESTORNO": ("Venda 10/09 a 2,59% estornada em 22/09 (depois da troca de taxa)",
                             "Sem divergência (vale a data da venda); por data do movimento daria alarme falso",
                             "R2 [DECIDIDO]"),
        "DIVERG_TAXA_TEXTO": ("Rumo Norte 2-6x cobrada 3,19% (contratado 3,09%, gravado como texto)",
                              "Divergência CHECKOUT", "formato"),
        "DIVERG_PIX": ("Fiorde Pix cobrado 0,89% (contratado 0,79%)", "Divergência CHECKOUT", ""),
        "R3_CENTAVO": ("Pix de R$ 1,00 / R$ 3,50 cobrado 0,89% (contratado 0,79%): diferença < 1 centavo",
                       "Pelo método % aparece com diferenca_brl 0.00; pelo método em reais não aparece",
                       "R3 [ABERTO]"),
        "DIVERG_DEBITO": ("Cordilheira débito cobrado 1,49% (contratado 1,39%)", "Divergência CHECKOUT", ""),
        "DIVERG_AVISTA": ("Trilha Sul à vista cobrada 2,99% (contratado 2,69%)", "Divergência CHECKOUT", ""),
        "DIVERG_PARCELADO": ("Campus Mundi 2-6x cobrada 3,19% (contratado 2,99%; CNPJ sem zero na planilha)",
                             "Divergência CHECKOUT", ""),
        "DIVERG_CASADO_POR_NOME": ("Wombat (casado por nome) à vista cobrada 2,69% (contratado 2,59%)",
                                   "Divergência CHECKOUT", "R11 [PROPOSTA]"),
        "R4_ESTORNO_DIVERGENTE": ("Estorno de uma venda que já tinha divergência", "Linha de divergência com sinal "
                                  "negativo que anula a da venda", "R4 [ABERTO]"),
        "VENDA_TARDIA": ("Venda que só chegou no arquivo de ajustes tardios", "Entra na comissão de setembro",
                         "aviso da banca"),
        "REVERSAO_ANTECIPACAO": ("Reversão integral de antecipação", "Abate a taxa de antecipação inteira",
                                 "premissa"),
    }
    for r in sorted(mundo["orbe"], key=lambda r: (r["arq"], r["data"], r["id"])):
        for tg in r["tags"]:
            if tg in desc:
                p, e, rg = desc[tg]
                if tg == "REVERSAO_ANTECIPACAO" and r["arq"] == "06":
                    p += " (arquivo de ajustes tardios)"
                add(O1 if r["arq"] == "01" else O6, r["id"], p, e, rg)
    est_06 = [r for r in mundo["orbe"] if r["arq"] == "06" and r["tipo"] == "ESTORNO"]
    add(O6, f"{len(est_06)} estornos", "Ajustes tardios de 30/09 que não estavam no arquivo 01",
        "Somar ao fechamento de setembro (o código deve ler todos os arquivos da Orbe)", "aviso da banca")
    add(O1 + " / " + O6, "estornos", "Bandeira do estorno às vezes diferente da venda original",
        "Ruído do export; ligar estorno à venda pelo id_referencia, não pela bandeira", "alarme falso")
    for x in gm.LOJISTAS:
        if len(x["orbe"]) > 1:
            add(O1, f"EC {x['ec']}", f"Mesmo EC com nomes diferentes: {', '.join(x['orbe'])}",
                "Agrupar pelo EC, não pelo nome", "formato")
    add(O1, "valor_taxa", "A Orbe trunca a taxa no centavo (ex.: 29,708 vira 29,70)",
        "Não é divergência; % aplicada igual à contratada", "alarme falso")

    E = ARQ["eml"]
    for o in mundo["ponte"]:
        lin = f"{o['num']} (linha {o['linha_xlsx']})"
        if o["dup"]:
            add(E, lin, "Operação repetida com Observação 'reprocessada'", "Contar uma vez + pendência "
                "OPERACAO_DUPLICADA", "R7 [PROPOSTA]")
        elif "SPREAD_NEGATIVO" in o["tags"]:
            add(E, lin, "Spread negativo ('Taxa travada no pedido (D-1)')", "Fora da comissão e das divergências; "
                "pendência SPREAD_NEGATIVO", "R8 [PROPOSTA]")
        elif "RESSALVA" in o["tags"]:
            add(E, lin, "Status 'APROVADO C/ RESSALVA'", "Entra normal na comissão", "R6 [DOC]")
        elif "DIVERG_SPREAD" in o["tags"]:
            add(E, lin, "Caminhos: spread realizado 1,5% x contratado 1,2%", "Divergência REMESSA; comissão usa o "
                "spread realizado", "R10 [PROPOSTA]")
    add(E, "rodapé da aba Operações", "'Total de operações' e 'Spread total R$' incluem a duplicada e os negativos",
        "Não usar o rodapé como total; somar as linhas válidas", "formato")
    add(E, "coluna CNPJ Cliente / Cliente", "CNPJ com e sem pontuação; nome cortado em 20 caracteres e com acento",
        "Casar pelo CNPJ", "formato")
    add(E, "anexo", "Relatório vem como xlsx em base64 dentro do .eml", "Extrair o anexo sem limpeza manual",
        "formato")

    A, M = ARQ["aurora"], ARQ["meridiano"]
    for e in mundo["aurora"]:
        if e["cat"] == "CONTABILIDADE":
            add(A, e["ref"], "PIX ENVIADO que não é repasse a lojista", "4.2.06 (não 2.1.01.001)", "R15")
        if e["cat"] == "PIX_NAO_IDENTIFICADO":
            add(A, e["ref"], "PIX recebido sem identificação", "1.1.09.002 + pendência", "R15 [VALIDADO]")
        if e["cat"] == "DEVOLUCAO_PIX":
            add(A, e["ref"], "Devolução de PIX de lojista sem explicação", "HUMANO, sem conta + pendência",
                "R15 [VALIDADO]")
        if e["cat"] == "TRANSF_MERIDIANO_EM_TRANSITO":
            add(A, e["ref"], "Transferência de 30/09 que não chega no Meridiano em setembro",
                "1.1.09.001 normal; sem pendência (se resolve em outubro)", "R15 [PROPOSTA]")
        if e["cat"] == "FOLHA":
            add(A, e["ref"], "Folha 08/2026 paga em setembro", "2.1.04.001 (baixa da obrigação)", "R15 [VALIDADO]")
        if e["cat"] == "REPASSE_LOJISTA" and e["lk"] == "cordilheira":
            add(A, e["ref"], "Nome com 'Õ' mantido e 'Ç' removido pelo banco", "Ainda é repasse a lojista",
                "formato")
    add(A, "L1-L8 e rodapé", "Cabeçalho de 7 linhas, SALDO ANTERIOR, SALDO FINAL e aviso no fim",
        "Não são lançamentos; ref_origem = número da linha física (primeiro lançamento é L9)", "formato")
    for e in mundo["merid"]:
        if e["cat"] == "REPASSE_COMISSAO_PONTE":
            add(M, e["ref"], "Comissão de agosto recebida em setembro", "1.1.03.002 (baixa do a receber), não "
                "receita de setembro", "R15 [VALIDADO]")
    add(M, "cabeçalho", "Declara CHARSET:1252 mas os bytes são UTF-8 com caractere inválido no lugar do acento "
        "(INTERC�MBIO)", "Ler sem quebrar; casar lojista pelo resto do nome", "formato")
    return out


def escrever_xlsx(caminho, tabelas, peg):
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    bold = Font(bold=True)
    fill = PatternFill("solid", fgColor="DDE7F0")
    for nome, linhas, obrig in tabelas + [("mapa_pegadinhas.csv", peg, list(peg[0].keys()))]:
        ws = wb.create_sheet(nome.replace(".csv", "")[:31])
        campos = obrig + [c for c in (linhas[0].keys() if linhas else []) if c not in obrig]
        ws.append(campos)
        for c in ws[1]:
            c.font, c.fill = bold, fill
        for r in linhas:
            vals = []
            for c in campos:
                v = r.get(c, "")
                if isinstance(v, str) and re.fullmatch(r"-?\d+\.\d+", v) and c not in ("ref_origem",):
                    v = float(v)
                vals.append(v)
            ws.append(vals)
        ws.freeze_panes = "A2"
        for col in ws.columns:
            larg = max(len(str(c.value or "")) for c in col[:200])
            ws.column_dimensions[col[0].column_letter].width = min(max(10, larg + 2), 70)
    wb.save(caminho)
