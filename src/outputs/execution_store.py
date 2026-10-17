"""Snapshots por execução; publicação das saídas somente após validação."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

from ..utils import sha256_file


def _json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _ler(path):
    return json.loads(path.read_text(encoding="utf-8"))


def _renomear(origem, destino, substituir=True):
    # Antivírus/indexadores do Windows podem manter um handle por instantes.
    for tentativa in range(6):
        try:
            (os.replace if substituir else os.rename)(origem, destino)
            return
        except PermissionError:
            if tentativa == 5:
                raise
            time.sleep(0.05 * (tentativa + 1))


def preparar_execucao(state):
    competencia = state.get("competencia", "2026-09")
    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", competencia):
        raise ValueError("Competência inválida; use AAAA-MM.")
    origem = Path(state["data_dir"]).resolve()
    if not origem.is_dir():
        raise FileNotFoundError(f"Pasta de entrada não encontrada: {origem}")
    raiz = Path(state.get("execucoes_dir") or Path(state["output_dir_oficial"]).resolve().parent / "execucoes")
    periodo = raiz / competencia
    periodo.mkdir(parents=True, exist_ok=True)
    identificador = datetime.now(timezone.utc).strftime("EXEC-%Y%m%dT%H%M%S%fZ-") + uuid4().hex[:12]
    stage = periodo / (".pendente-" + identificador)
    stage.mkdir()
    (stage / "entradas").mkdir()
    (stage / "saida").mkdir()
    state["id_execucao"] = identificador
    state["execucao_stage"] = str(stage)
    state["execucao_dir"] = str(periodo / identificador)
    state["data_dir_original"] = str(origem)

    # Somente fontes candidatas ao processamento; nunca copia .env/credenciais.
    captura = []
    for source in sorted(origem.iterdir()):
        if source.is_file() and (
            source.suffix.lower() in (".csv", ".xlsx", ".eml", ".ofx") or source.name == "00_LEIA-ME.md"
        ):
            antes = sha256_file(source)
            target = stage / "entradas" / source.name
            shutil.copyfile(source, target)
            if antes != sha256_file(target) or antes != sha256_file(source):
                raise ValueError(f"Entrada mudou durante a captura: {source.name}")
            captura.append({"arquivo": source.name, "sha256": antes})
    _json(stage / "captura_entradas.json", captura)

    repo = Path(__file__).resolve().parents[2]
    arquivos_codigo = []
    for source in sorted((repo / "src").rglob("*.py")):
        rel = source.relative_to(repo)
        target = stage / "codigo" / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        arquivos_codigo.append((rel.as_posix(), sha256_file(target)))
    if not arquivos_codigo:
        raise ValueError("Fontes de execução não encontrados; snapshot de código não pode ficar vazio.")
    executavel_hash = None
    if getattr(sys, "frozen", False):
        info = _ler(repo / "tarvo_build.json")
        commit = info.get("commit")
        executavel_hash = sha256_file(sys.executable)
    else:
        try:
            commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True,
                                    text=True, check=True, timeout=10).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            commit = None
    identidade_codigo = {"fontes": arquivos_codigo, "executavel": executavel_hash}
    state["codigo_execucao"] = {
        "commit": commit,
        "sha256_fontes": hashlib.sha256(json.dumps(identidade_codigo).encode()).hexdigest(),
        "sha256_executavel": executavel_hash,
        "arquivos": arquivos_codigo,
        "observacao": "A cópia em codigo/ registra também alterações locais ainda sem commit.",
    }

    # Histórico da competência independe de qual mês está atualmente em saida/.
    candidatos = []
    for path in periodo.glob("EXEC-*/manifesto.json"):
        candidatos.append((_ler(path), path.parent))
    escolhido = max(candidatos, key=lambda x: x[0]["id_execucao"], default=None)
    anterior, anterior_dir = escolhido if escolhido else (None, None)
    if anterior is None:
        path = Path(state["output_dir_oficial"]) / "auditoria_execucao.json"
        if path.exists():
            loaded = _ler(path)
            if loaded.get("competencia") == competencia:
                anterior = loaded
                if not anterior.get("execucao_dir"):
                    # Primeira migração: preserva as saídas existentes sem inventar
                    # entradas/código que não foram capturados naquela execução.
                    legado = periodo / ("LEGADO-" + identificador)
                    legado.mkdir()
                    shutil.copytree(path.parent, legado / "saida")
                    anterior = dict(anterior, execucao_dir=str(legado),
                                    tipo_preservacao="LEGADO_SOMENTE_SAIDAS",
                                    limitacao="Entradas e código da execução legada não foram capturados.")
                    _json(legado / "manifesto.json", anterior)
                    anterior_dir = legado
    state["manifesto_anterior"] = anterior
    state["execucao_anterior_dir"] = str(anterior_dir) if anterior_dir else None
    return stage / "entradas"


def diferencas_detalhadas(anterior_dir, atual_dir):
    specs = {
        "comissoes_por_lojista.csv": (["cnpj", "linha_negocio"], "comissao_brl"),
        "notas_a_emitir.csv": (["tomador_cnpj", "linha_negocio"], "valor_brl"),
        "pendencias.csv": (["tipo", "ref_origem", "quem_decide"], "valor_brl"),
    }
    resultado = {}
    for nome, (keys, valor) in specs.items():
        def agrupar(pasta):
            itens = {}
            if pasta is not None and (pasta / nome).exists():
                with (pasta / nome).open(encoding="utf-8", newline="") as f:
                    for row in csv.DictReader(f, delimiter=";"):
                        key = tuple(row[k] for k in keys)
                        itens[key] = itens.get(key, Decimal(0)) + Decimal(row[valor])
            return itens
        antigos, atuais = agrupar(anterior_dir), agrupar(atual_dir)
        resultado[nome] = [dict(zip(keys, key), anterior=f"{antigos.get(key, 0):.2f}",
                                atual=f"{atuais.get(key, 0):.2f}",
                                diferenca=f"{atuais.get(key, 0) - antigos.get(key, 0):.2f}")
                           for key in sorted(antigos.keys() | atuais.keys())
                           if antigos.get(key) != atuais.get(key)]
    return resultado


def _descartar_temporario(path, parent):
    # Limpeza restrita a uma pasta temporária criada por esta publicação.
    if path.parent.resolve() != parent.resolve() or not path.name.startswith(".tarvo-"):
        raise ValueError("Pasta temporária fora do destino de publicação.")
    if path.exists():
        shutil.rmtree(path)


def publicar_snapshot(source, destinos):
    """Troca cada diretório e restaura todos os destinos se uma troca falhar.

    O manifesto no arquivo preservado é a referência imutável. Não se promete
    transação do sistema de arquivos entre volumes nem proteção contra queda de energia.
    """
    preparados, trocados = [], []
    sucesso = False
    try:
        for dest in destinos:
            dest = dest.resolve()
            dest.parent.mkdir(parents=True, exist_ok=True)
            token = uuid4().hex
            novo = dest.parent / (".tarvo-publicacao-" + token)
            backup = dest.parent / (".tarvo-backup-" + token)
            preparados.append((dest, novo, backup))
            if dest.exists():
                shutil.copytree(dest, novo)
            else:
                novo.mkdir()
            for item in source.iterdir():
                if item.is_file():
                    shutil.copyfile(item, novo / item.name)
        for dest, novo, backup in preparados:
            existia = dest.exists()
            if existia:
                _renomear(dest, backup)
            trocados.append((dest, backup, existia))
            _renomear(novo, dest)
        sucesso = True
    except Exception:
        for dest, backup, existia in reversed(trocados):
            if dest.exists():
                # Move a publicação incompleta para uma pasta temporária antes de removê-la.
                descarte = dest.parent / (".tarvo-descarte-" + uuid4().hex)
                _renomear(dest, descarte)
                _descartar_temporario(descarte, dest.parent)
            if existia:
                _renomear(backup, dest)
        raise
    finally:
        for dest, novo, backup in preparados:
            _descartar_temporario(novo, dest.parent)
            # Não remove um backup ainda necessário caso a restauração também falhe.
            if sucesso:
                _descartar_temporario(backup, dest.parent)


def finalizar_execucao(state, manifesto, destinos):
    stage, final = Path(state["execucao_stage"]), Path(state["execucao_dir"])
    if final.exists():
        raise FileExistsError(f"Execução já preservada: {final}")
    for item in _ler(stage / "captura_entradas.json"):
        if sha256_file(stage / "entradas" / item["arquivo"]) != item["sha256"]:
            raise ValueError(f"Captura original alterada: {item['arquivo']}")
    for item in manifesto["arquivos_entrada"]:
        if sha256_file(stage / "entradas" / item["arquivo"]) != item["sha256"]:
            raise ValueError(f"Entrada do snapshot alterada: {item['arquivo']}")
    for item in manifesto["arquivos_saida"]:
        if sha256_file(stage / "saida" / item["arquivo"]) != item["sha256"]:
            raise ValueError(f"Saída do snapshot alterada: {item['arquivo']}")
    anterior = state.get("manifesto_anterior") or {}
    anterior_dir = Path(state["execucao_anterior_dir"]) / "saida" if state.get("execucao_anterior_dir") else None
    diff = diferencas_detalhadas(anterior_dir, stage / "saida")
    _json(stage / "diferencas.json", {
        "id_execucao": manifesto["id_execucao"],
        "id_execucao_anterior": anterior.get("id_execucao"),
        "base_comparacao_disponivel": anterior_dir is not None,
        "alteracoes": diff,
    })
    _json(stage / "manifesto.json", manifesto)
    _json(stage / "aprovacao.json", {
        "id_execucao": manifesto["id_execucao"],
        "status": manifesto["status_aprovacao"],
        "hash_entradas": manifesto["hash_entradas_combinado"],
        "hash_saidas": manifesto["hash_saidas_combinado"],
        "versao_regras": manifesto["versao_regras"],
        "sha256_codigo": manifesto["codigo_execucao"]["sha256_fontes"],
        "origem": "Status declarado pelo operador; não autentica identidade nem decisão de Helena.",
    })
    # Uma renomeação publica o snapshot completo; snapshots existentes não são editados.
    _renomear(stage, final, substituir=False)
    publicar_snapshot(final / "saida", destinos)
