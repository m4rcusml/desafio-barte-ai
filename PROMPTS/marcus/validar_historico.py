"""Confere hashes, cobertura e fidelidade dos registros exportados."""
from pathlib import Path
import json
import re
import os
from collections import Counter
from exportar_historico import digest, redact, render_transcript, prepare_private_references, PRIVATE_REFERENCES, KEYS

dest = Path(__file__).resolve().parent
manifest = json.loads((dest / 'manifesto.json').read_text(encoding='utf-8'))
home = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
allowed = {s['id'] for s in manifest['sessoes']}
files = {p.name: p for folder in ('sessions', 'archived_sessions') for p in (home / folder).rglob('*.jsonl')}
snapshots = {s['id']: files[s['fonte']].read_bytes()[:s['bytes_fonte_capturados']] for s in manifest['sessoes']}
prepare_private_references(list(snapshots.values()), allowed)
total = 0
assert not list(dest.rglob('*.jsonl')), 'O pacote deve conter transcripts somente em TXT.'
for session in manifest['sessoes']:
    assert len(session['arquivos']) == 1 and session['arquivos'][0]['caminho'].endswith('.txt')
    for artifact in session['arquivos']:
        p = dest / artifact['caminho']
        assert digest(p.read_bytes()) == artifact['sha256'], p
        assert p.stat().st_size == artifact['bytes'], p
    source = snapshots[session['id']]
    assert digest(source) == session['sha256_fonte_no_corte'], session['id']
    expected = []
    for line_no, line in enumerate(source.splitlines(), 1):
        record = json.loads(line)
        p = record.get('payload', {})
        kind = p.get('type')
        if record.get('type') != 'response_item' or kind not in KEYS:
            continue
        if kind == 'message' and (p.get('role') not in ('user', 'assistant') or p.get('phase') == 'analysis' or p.get('channel') == 'analysis'):
            continue
        clean = redact({k: p[k] for k in KEYS[kind] if k in p}, allowed, Counter())
        expected.append({'linha_origem': line_no, 'timestamp': record.get('timestamp'), 'item': clean})
    counts = Counter(r['item'].get('role', r['item']['type']) for r in expected)
    assert dict(counts) == session['contagens'], session['id']
    total += len(expected)
    for record in expected:
        assert record['item']['type'] in KEYS
        assert 'encrypted_content' not in record['item']
        assert record['item'].get('role') not in ('system', 'developer')
    text = (dest / session['arquivos'][0]['caminho']).read_bytes().decode('utf-8')
    rendered = render_transcript(session['titulo'], session['id'], session['inicio_utc'], manifest['captura_utc'], expected)
    assert text == rendered, session['id']
    # Metadados de conversas pessoais alheias que apareceram em resultados de listagem.
    for unrelated in PRIVATE_REFERENCES:
        assert unrelated not in text, session['id']
assert manifest['sessoes_projeto'] == 9 and manifest['sessoes_preparacao'] == 2
assert len(re.findall(r'^## [1-4]\. ', (dest.parent/'MOMENTOS.md').read_text(encoding='utf-8'), re.M)) == 4
result = {'resultado': 'APROVADO', 'sessoes': len(allowed), 'registros_conferidos_com_fonte': total, 'arquivos_de_conversa': len(allowed), 'formato_transcripts': 'TXT',
          'captura_utc': manifest['captura_utc'], 'sha256_manifesto': digest((dest/'manifesto.json').read_bytes()),
          'verificacoes': ['hashes_dos_exports', 'hashes_das_fontes_no_corte', 'todas_as_mensagens_e_ferramentas_exportaveis',
                           'igualdade_integral_do_txt_com_renderizacao_da_fonte_redigida', 'ausencia_de_exports_jsonl',
                           'ausencia_de_metadados_de_chats_pessoais_alheios_verificados', 'quatro_momentos_no_indice_geral']}
(dest / 'VALIDACAO.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='')
print(json.dumps(result, ensure_ascii=False))
