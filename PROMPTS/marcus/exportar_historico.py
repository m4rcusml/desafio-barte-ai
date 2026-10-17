"""Exporta conversas locais do projeto, sem resumir mensagens ou resultados.

Uso, na raiz do repositório: python PROMPTS/marcus/exportar_historico.py
Lê somente os rollouts locais. Não altera nem publica sessões.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

DEST = Path(__file__).resolve().parent
ROOT = DEST.parents[1]
CURRENT = '01a14b99-6b50-70c2-b7be-5e96706e3c37'
PROJECT_ID = 'e3ae646f-4dab-4e42-9cfb-c0756a95232d'
EXTRAS = {'01a136e9-24f6-7d81-855d-fdc5cbe9dde4', '01a14a66-ebc6-7ce3-8f57-53c1fd1be043'}
KEYS = {
    'message': ('type', 'id', 'role', 'status', 'phase', 'content'),
    'function_call': ('type', 'id', 'status', 'call_id', 'name', 'namespace', 'arguments'),
    'function_call_output': ('type', 'id', 'call_id', 'output'),
    'custom_tool_call': ('type', 'id', 'status', 'call_id', 'name', 'input'),
    'custom_tool_call_output': ('type', 'id', 'call_id', 'output'),
}
PRIVATE_REFERENCES: set[str] = set()
PATTERNS = [
    ('email', re.compile(r'(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b'), '[EMAIL_REMOVIDO]'),
    ('credencial', re.compile(r'\b(?:sk-(?:proj-)?[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|AIza[A-Za-z0-9_-]{30,})\b'), '[CREDENCIAL_REMOVIDA]'),
    ('token_jwt', re.compile(r'\beyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{10,}\b'), '[TOKEN_REMOVIDO]'),
    ('autorizacao', re.compile(r'(?i)(?<=Bearer )[A-Za-z0-9_./+=-]{20,}'), '[TOKEN_REMOVIDO]'),
]


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normal_path(value: str) -> str:
    return value.replace('\\', '/').removeprefix('//?/').rstrip('/').lower()


def collect_private_references(value, allowed: set[str]):
    if isinstance(value, dict):
        if value.get('kind') in ('codex', 'chatgpt') and 'title' in value and 'id' in value and value['id'] not in allowed:
            title = value.get('title')
            if isinstance(title, str) and len(title) >= 6:
                PRIVATE_REFERENCES.add(title)
        for child in value.values():
            collect_private_references(child, allowed)
    elif isinstance(value, list):
        for child in value:
            collect_private_references(child, allowed)
    elif isinstance(value, str) and value.lstrip().startswith(('{', '[')):
        try:
            child = json.loads(value)
        except (ValueError, RecursionError):
            return
        if isinstance(child, (dict, list)):
            collect_private_references(child, allowed)


def prepare_private_references(snapshots: list[bytes], allowed: set[str]):
    PRIVATE_REFERENCES.clear()
    for snapshot in snapshots:
        for line in snapshot.splitlines():
            event = json.loads(line)
            item = event.get('payload', {})
            if event.get('type') != 'response_item' or item.get('type') not in KEYS:
                continue
            if item.get('type') == 'message' and item.get('role') not in ('user', 'assistant'):
                continue
            collect_private_references({k: item[k] for k in KEYS[item['type']] if k in item}, allowed)


def redact(value, allowed: set[str], changes: Counter):
    if isinstance(value, dict):
        if value.get('kind') in ('codex', 'chatgpt') and 'title' in value and 'id' in value and value['id'] not in allowed:
            changes['metadados_pessoais_de_chat_alheio'] += 1
            return {'redacao': '[METADADOS_DE_CHAT_ALHEIO_REMOVIDOS]'}
        if 'projectId' in value and 'label' in value and 'path' in value and value['projectId'] != PROJECT_ID:
            changes['metadados_pessoais_de_outro_projeto'] += 1
            return {'redacao': '[METADADOS_DE_OUTRO_PROJETO_REMOVIDOS]'}
        return {k: redact(v, allowed, changes) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v, allowed, changes) for v in value]
    if not isinstance(value, str):
        return value
    # Saídas de ferramentas podem conter JSON serializado dentro de texto.
    if value.lstrip().startswith(('{', '[')):
        try:
            parsed = json.loads(value)
        except (ValueError, RecursionError):
            pass
        else:
            if isinstance(parsed, (dict, list)):
                before = sum(changes.values())
                clean = redact(parsed, allowed, changes)
                if sum(changes.values()) != before:
                    value = json.dumps(clean, ensure_ascii=False)
    for reference in sorted(PRIVATE_REFERENCES, key=lambda v: (-len(v), v)):
        count = value.count(reference)
        if count:
            value = value.replace(reference, '[REFERENCIA_PESSOAL_ALHEIA_REMOVIDA]')
            changes['referencia_pessoal_alheia'] += count
    for category, pattern, replacement in PATTERNS:
        value, count = pattern.subn(replacement, value)
        changes[category] += count
    # Credenciais atribuídas a variáveis com nomes explícitos; exemplos continuam.
    assignment = re.compile(r'''(?i)((?:[A-Z_]*API_KEY|access_token|refresh_token|client_secret|password|senha)["']?\s*[:=]\s*["']?)([A-Za-z0-9_+/.=-]{20,})''')
    def replace_assignment(match):
        token = match[2]
        if re.search(r'(?i)sua_chave|your_|example|exemplo|placeholder|os\.getenv|environ|REMOVID', token):
            return match[0]
        changes['credencial_atribuida'] += 1
        return match[1] + '[CREDENCIAL_REMOVIDA]'
    return assignment.sub(replace_assignment, value)


def text_of(value) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts = []
        for item in value:
            if isinstance(item, dict) and item.get('type') in ('input_text', 'output_text', 'text'):
                parts.append(item.get('text', ''))
            else:
                parts.append(json.dumps(item, ensure_ascii=False, indent=2))
        return '\n\n'.join(parts)
    return json.dumps(value, ensure_ascii=False, indent=2)


def render_transcript(title: str, sid: str, started: str, captured: str, records: list[dict]) -> str:
    text = [f"CHAT: {title}\nID: {sid}\nInício UTC: {started}\nCaptura UTC: {captured}\nFormato: conteúdo das mensagens e ferramentas, em ordem; não é resumo.\n"]
    for record in records:
        item = record['item']
        kind = item['type']
        label = item.get('role', kind)
        if item.get('phase'):
            label += ' / ' + item['phase']
        text.append(f"\n{'='*72}\nLINHA DE ORIGEM {record['linha_origem']} | {record['timestamp']} | {label}\n{'='*72}\n")
        if kind == 'message':
            text.append(text_of(item.get('content', [])))
        else:
            text.append(text_of({k: v for k, v in item.items() if k != 'type'}))
    return '\n'.join(text) + '\n'


def main():
    home = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
    catalog = json.loads((DEST / 'catalogo.json').read_text(encoding='utf-8'))
    known = {row['id']: row for row in catalog}
    sources = []
    automatic = 0
    for folder in ('sessions', 'archived_sessions'):
        for path in sorted((home / folder).rglob('*.jsonl')):
            with path.open(encoding='utf-8') as f:
                first = f.readline()
            try:
                meta = json.loads(first).get('payload', {})
            except ValueError:
                continue
            cwd = normal_path(str(meta.get('cwd', '')))
            associated = cwd == normal_path(str(ROOT)) or cwd.startswith(normal_path(str(ROOT)) + '/')
            sid = meta.get('id')
            if not (associated or sid in known):
                continue
            if not isinstance(meta.get('source'), str):
                automatic += 1
                continue
            sources.append((path, meta))
    ids = [m['id'] for _, m in sources]
    assert len(ids) == len(set(ids)), 'Há múltiplos arquivos por sessão; revise antes de exportar.'
    assert set(known) <= set(ids), f'Sessões não encontradas: {set(known)-set(ids)}'
    allowed = set(ids)
    snapshots = {}
    incomplete = {}
    for path, meta in sources:
        raw = path.read_bytes()
        end = raw.rfind(b'\n') + 1
        snapshots[meta['id']] = raw[:end]
        incomplete[meta['id']] = len(raw) - end
    prepare_private_references(list(snapshots.values()), allowed)
    generated = datetime.now(timezone.utc).isoformat()
    sessions = []
    redactions = []
    (DEST / 'sessoes').mkdir(exist_ok=True)
    for path, meta in sorted(sources, key=lambda pair: pair[1]['timestamp']):
        sid = meta['id']
        info = known.get(sid, {'title': sid})
        captured = snapshots[sid]
        records = []
        counts = Counter()
        excluded = Counter()
        total_source_lines = 0
        for line_no, line in enumerate(captured.splitlines(), 1):
            total_source_lines += 1
            event = json.loads(line)
            p = event.get('payload', {})
            kind = p.get('type')
            if event.get('type') != 'response_item' or kind not in KEYS:
                excluded['eventos_internos_ou_redundantes'] += 1
                continue
            if kind == 'message' and (p.get('role') not in ('user', 'assistant') or p.get('phase') == 'analysis' or p.get('channel') == 'analysis'):
                excluded['mensagens_internas_do_aplicativo'] += 1
                continue
            selected = {k: p[k] for k in KEYS[kind] if k in p}
            changes = Counter()
            clean = redact(selected, allowed, changes)
            meaningful_changes = {k: v for k, v in changes.items() if v}
            if meaningful_changes:
                redactions.append({'sessao': sid, 'linha_origem': line_no, 'categorias': meaningful_changes})
            record = {'linha_origem': line_no, 'timestamp': event.get('timestamp'), 'item': clean}
            records.append(record)
            counts[p.get('role') if kind == 'message' else kind] += 1
        assert records, sid
        stem = f"{meta['timestamp'][:10]}--{sid}"
        txt_path = DEST / 'sessoes' / (stem + '.txt')
        rendered = render_transcript(info['title'], sid, meta['timestamp'], generated, records)
        txt_path.write_text(rendered, encoding='utf-8', newline='')
        assert txt_path.read_bytes() == rendered.encode('utf-8')
        sessions.append({'id': sid, 'titulo': info['title'], 'escopo': 'preparacao_complementar' if sid in EXTRAS else 'projeto', 'chat_atual': sid == CURRENT,
                         'inicio_utc': meta['timestamp'], 'ultimo_item_exportado_utc': records[-1]['timestamp'], 'fonte': path.name,
                         'sha256_fonte_no_corte': digest(captured), 'bytes_fonte_capturados': len(captured), 'linhas_fonte_capturadas': total_source_lines,
                         'bytes_finais_incompletos_nao_capturados': incomplete[sid], 'contagens': dict(counts), 'eventos_fora_da_conversa': dict(excluded),
                         'arquivos': [{'caminho': txt_path.relative_to(DEST).as_posix(), 'sha256': digest(txt_path.read_bytes()), 'bytes': txt_path.stat().st_size}]})
    current = next(s for s in sessions if s['chat_atual'])
    current_records = (DEST / current['arquivos'][0]['caminho']).read_text(encoding='utf-8')
    assert 'o pitch ficará para outra pessoa finalizar' in current_records, 'A solicitação atual não foi capturada.'
    manifest = {'captura_utc': generated, 'responsavel': 'Marcus', 'tipo': 'exportacao_das_conversas_locais_disponiveis_sem_resumo',
                'sessoes_projeto': sum(s['escopo']=='projeto' for s in sessions), 'sessoes_preparacao': sum(s['escopo']!='projeto' for s in sessions),
                'sessoes_automaticas_internas_nao_exportadas': automatic, 'recorte_atual': 'O chat atual é uma captura até o último item persistido indicado; continua aberto.',
                'sessoes': sessions, 'redacoes': redactions}
    (DEST / 'manifesto.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='')
    index = ['HISTÓRICO DE MARCUS — ÍNDICE', f'Captura UTC: {generated}', '']
    for s in sessions:
        index += [f"{s['titulo']} [{s['escopo']}]", f"ID: {s['id']}", f"Texto: {s['arquivos'][0]['caminho']}", f"Contagens: {json.dumps(s['contagens'],ensure_ascii=False)}", '']
    (DEST / 'INDICE.txt').write_text('\n'.join(index), encoding='utf-8')
    print(json.dumps({'sessoes': len(sessions), 'projeto': manifest['sessoes_projeto'], 'preparacao': manifest['sessoes_preparacao'],
                      'registros': sum(sum(s['contagens'].values()) for s in sessions), 'registros_com_redacao': len(redactions), 'captura_utc': generated}, ensure_ascii=False))


if __name__ == '__main__':
    main()
