"""Preservação recuperável, vínculo da aprovação e proteção da última saída."""
import csv
import json
import os
import shutil
import tempfile
import unittest
import zipfile
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from src.graph import build_closing_graph
from src.agent.consultant import TarvoConsultant
from src.utils import sha256_file


class TestExecutionStore(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.raw = self.base / "raw"
        self.raw.mkdir()
        repo = Path(__file__).resolve().parents[1]
        with zipfile.ZipFile(repo / "dados/originais/Tarvo_Data_Pack_set2026.zip") as z:
            z.extractall(self.raw)
        shutil.copyfile(repo / "dados/originais/06_orbe_ajustes_tardios_set2026.csv",
                        self.raw / "06_orbe_ajustes_tardios_set2026.csv")
        self.out = self.base / "saida"
        self.local = self.base / "local"

    def estado(self, **kwargs):
        state = dict(data_dir=str(self.raw), output_dir_local=str(self.local),
                     output_dir_oficial=str(self.out), competencia="2026-09",
                     status_aprovacao="PROVISORIO")
        state.update(kwargs)
        return state

    def run_state(self, **kwargs):
        return build_closing_graph().invoke(self.estado(**kwargs))

    def ler(self, path):
        return json.loads(path.read_text(encoding="utf-8"))

    def hashes(self, folder):
        return {p.relative_to(folder).as_posix(): sha256_file(p) for p in folder.rglob("*") if p.is_file()}

    def alterar_venda(self):
        with (self.raw / "06_orbe_ajustes_tardios_set2026.csv").open("a", encoding="utf-8", newline="") as f:
            csv.writer(f, delimiter=";").writerow([
                "TX_NOVA_VERSAO", "30/09/2026", "1014537966", "DUBLIN HUB INTERCAMBIO",
                "VENDA", "CREDITO A VISTA", "1", "VISA", "1000,00", "2,59", "25,90", "974,10", "", "",
            ])

    def test_versoes_aprovacoes_e_diff_sao_preservados(self):
        first = self.run_state(status_aprovacao="APROVADO_POR_HELENA")  # declaração humana simulada
        archived = Path(first["execucao_dir"])
        original_hashes = self.hashes(archived)
        self.assertEqual(archived.parent, self.base / "execucoes/2026-09")
        approval = self.ler(archived / "aprovacao.json")
        self.assertEqual(approval["id_execucao"], first["id_execucao"])
        self.assertEqual(approval["status"], "APROVADO_POR_HELENA")
        self.assertTrue((archived / "codigo/src/graph.py").is_file())
        self.assertEqual(set(self.hashes(archived / "entradas")), set(self.hashes(self.raw)))

        second = self.run_state(status_aprovacao="APROVADO_POR_HELENA")
        self.assertNotEqual(first["id_execucao"], second["id_execucao"])
        self.assertTrue(second["comparacao_execucao_anterior"]["saidas_identicas"])
        self.assertEqual(self.hashes(archived), original_hashes)

        self.alterar_venda()
        third = self.run_state(status_aprovacao="APROVADO_POR_HELENA")
        self.assertEqual(third["status_aprovacao"], "REABERTO_PARA_REVISAO")
        self.assertEqual(self.hashes(archived), original_hashes)
        self.assertNotEqual(sha256_file(self.raw / "06_orbe_ajustes_tardios_set2026.csv"),
                            sha256_file(archived / "entradas/06_orbe_ajustes_tardios_set2026.csv"))
        diff = self.ler(Path(third["execucao_dir"]) / "diferencas.json")
        com = diff["alteracoes"]["comissoes_por_lojista.csv"]
        notas = diff["alteracoes"]["notas_a_emitir.csv"]
        self.assertEqual(sum(Decimal(r["diferenca"]) for r in com), Decimal("25.90"))
        self.assertEqual(sum(Decimal(r["diferenca"]) for r in notas), Decimal("25.90"))
        self.assertEqual(self.ler(archived / "aprovacao.json"), approval)
        self.assertEqual(TarvoConsultant(archived / "saida").get_summary()["status_aprovacao"], "APROVADO_POR_HELENA")
        self.assertEqual(TarvoConsultant(Path(third["execucao_dir"]) / "saida").get_summary()["status_aprovacao"], "REABERTO_PARA_REVISAO")

    def test_codigo_alterado_reabre_mesmo_com_resultados_identicos(self):
        self.run_state(status_aprovacao="APROVADO_POR_HELENA")
        from src.outputs.execution_store import preparar_execucao
        def capturar_codigo_modificado(state):
            inputs = preparar_execucao(state)
            state["codigo_execucao"]["sha256_fontes"] = "codigo-diferente-simulado"
            return inputs
        with patch("src.graph.preparar_execucao", side_effect=capturar_codigo_modificado):
            changed = self.run_state(status_aprovacao="APROVADO_POR_HELENA")
        self.assertTrue(changed["comparacao_execucao_anterior"]["saidas_identicas"])
        self.assertFalse(changed["comparacao_execucao_anterior"]["codigo_identico"])
        self.assertEqual(changed["status_aprovacao"], "REABERTO_PARA_REVISAO")

    def test_mudanca_de_regras_sem_mudar_valores_reabre_revisao(self):
        self.run_state(status_aprovacao="APROVADO_POR_HELENA")
        altered = self.run_state(status_aprovacao="APROVADO_POR_HELENA", versao_regras="regra-revisada")
        self.assertTrue(altered["comparacao_execucao_anterior"]["saidas_identicas"])
        self.assertFalse(altered["comparacao_execucao_anterior"]["regras_identicas"])
        self.assertEqual(altered["status_aprovacao"], "REABERTO_PARA_REVISAO")

    def test_migracao_preserva_saidas_legadas_sem_inventar_fontes(self):
        self.run_state()
        path = self.out / "auditoria_execucao.json"
        old = self.ler(path)
        old.pop("execucao_dir")
        path.write_text(json.dumps(old), encoding="utf-8")
        originais = self.hashes(self.out)
        new_root = self.base / "historico-migrado"
        self.run_state(execucoes_dir=str(new_root))
        legado = next((new_root / "2026-09").glob("LEGADO-*"))
        self.assertEqual(self.hashes(legado / "saida"), originais)
        self.assertEqual(self.ler(legado / "manifesto.json")["tipo_preservacao"], "LEGADO_SOMENTE_SAIDAS")
        self.assertFalse((legado / "entradas").exists())

    def test_sem_06_nao_registra_aprovacao_para_fechamento_parcial(self):
        approved = self.run_state(status_aprovacao="APROVADO_POR_HELENA")
        (self.raw / "06_orbe_ajustes_tardios_set2026.csv").unlink()
        partial = self.run_state(status_aprovacao="APROVADO_POR_HELENA")
        self.assertEqual(partial["estado_tecnico"], "PARCIAL_COM_BLOQUEIOS")
        self.assertEqual(partial["status_aprovacao"], "REABERTO_PARA_REVISAO")
        self.assertEqual(self.ler(Path(approved["execucao_dir"]) / "aprovacao.json")["status"], "APROVADO_POR_HELENA")

    def test_aprovacao_da_competencia_e_encontrada_apos_outro_mes(self):
        first = self.run_state(status_aprovacao="APROVADO_POR_HELENA")
        self.run_state(competencia="2026-10")
        self.alterar_venda()
        changed = self.run_state()
        self.assertEqual(changed["comparacao_execucao_anterior"]["id_execucao_anterior"], first["id_execucao"])
        self.assertEqual(changed["status_aprovacao"], "REABERTO_PARA_REVISAO")

    def test_falha_na_prova_real_nao_substitui_ultima_saida(self):
        first = self.run_state()
        before = self.hashes(self.out)
        previous = self.hashes(Path(first["execucao_dir"]))
        with patch("src.outputs.generator.validar_prova_real", return_value={
            "valido": False, "erros": ["erro financeiro simulado"], "total_ids_validados": 423,
        }):
            with self.assertRaisesRegex(ValueError, "Prova real inválida"):
                self.run_state()
        self.assertEqual(before, self.hashes(self.out))
        self.assertEqual(previous, self.hashes(Path(first["execucao_dir"])))

    def test_falha_na_publicacao_restaura_ambos_os_destinos(self):
        self.run_state()
        before_out, before_local = self.hashes(self.out), self.hashes(self.local)
        self.alterar_venda()
        replace = os.replace
        def falhar_segundo_destino(source, target):
            if Path(source).name.startswith(".tarvo-publicacao-") and Path(target) == self.out:
                raise OSError("falha simulada no segundo destino")
            return replace(source, target)
        with patch("src.outputs.execution_store.os.replace", side_effect=falhar_segundo_destino):
            with self.assertRaisesRegex(OSError, "falha simulada"):
                self.run_state()
        self.assertEqual(self.hashes(self.out), before_out)
        self.assertEqual(self.hashes(self.local), before_local)

    def test_processamento_usa_snapshot_e_nao_entrada_alterada_depois(self):
        from src.graph import node_ingestao_triagem
        from src.outputs.execution_store import preparar_execucao
        state = self.estado()
        inputs = preparar_execucao(state)
        self.alterar_venda()
        # O nó recebe o snapshot já capturado nesta verificação controlada.
        with patch("src.graph.preparar_execucao", return_value=inputs):
            classified = node_ingestao_triagem(state)
        self.assertTrue(all(Path(f["caminho"]).parent == inputs for f in classified["arquivos_descobertos"]))
        self.assertNotIn("TX_NOVA_VERSAO", (inputs / "06_orbe_ajustes_tardios_set2026.csv").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
