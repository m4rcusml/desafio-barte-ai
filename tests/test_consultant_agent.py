"""
Testes Unitários do Subagente Consultivo Tarvo (src/agent/consultant.py).
"""

from __future__ import annotations
import sys
import unittest
from decimal import Decimal
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.agent.consultant import TarvoConsultant
from src.graph import build_closing_graph


class TestConsultantAgent(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        import shutil
        import tempfile
        import zipfile
        cls._tmpdir = tempfile.TemporaryDirectory()
        tmp_path = Path(cls._tmpdir.name)
        repo_root = Path(__file__).resolve().parent.parent
        zip_path = repo_root / "dados" / "originais" / "Tarvo_Data_Pack_set2026.zip"
        f06_orig = repo_root / "dados" / "originais" / "06_orbe_ajustes_tardios_set2026.csv"

        raw_dir = tmp_path / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(raw_dir)
        shutil.copy(f06_orig, raw_dir / f06_orig.name)

        out_dir = tmp_path / "saida"
        loc_dir = tmp_path / "fechamento-completo"
        graph = build_closing_graph()
        graph.invoke({
            "data_dir": str(raw_dir),
            "output_dir_local": str(loc_dir),
            "output_dir_oficial": str(out_dir),
            "status_aprovacao": "PROVISORIO",
            "competencia": "2026-09",
        })
        cls.agent = TarvoConsultant(output_dir=out_dir)

    @classmethod
    def tearDownClass(cls):
        cls._tmpdir.cleanup()

    def test_summary_returns_valid_metrics(self):
        """Verifica se o sumário executivo retorna dados coerentes e status provisório."""
        summary = self.agent.get_summary()
        self.assertEqual(summary["competencia"], "09/2026")
        self.assertIn("PROVISORIO", summary["status"])
        metricas = summary["metricas"]
        self.assertGreater(int(metricas["qtd_comissoes"]), 0)
        self.assertGreater(int(metricas["qtd_notas"]), 0)
        self.assertGreater(int(metricas["qtd_vinculos_rastro"]), 0)
        self.assertIn("Helena", str(summary["pendencias_por_decisor"]))

    def test_explain_lojista_bridge(self):
        """Verifica se o consultor explica as regras e vigências de Bridge Idiomas."""
        res = self.agent.explain_lojista("Bridge")
        self.assertIn("Escola Bridge de Idiomas", res["lojista"])
        self.assertEqual(res["cnpj"], "22224579000109")
        self.assertGreater(len(res["regras_aplicadas"]), 0)
        # Deve ter regras pré e pós 15/09
        regras_str = " ".join(res["regras_aplicadas"])
        self.assertIn("15/09", regras_str)

    def test_explain_id_rastro_audit(self):
        """Verifica a auditoria 1-para-1 de um ID de saída."""
        res = self.agent.explain_id("NF-0021")
        self.assertEqual(res["id_saida"], "NF-0021")
        self.assertGreater(res["qtd_linhas_vinculadas"], 0)
        self.assertEqual(res["arquivo_origem"], "03_email_ponte_cambio_relatorio_set2026.eml")

    def test_guardrails_prevent_autonomous_actions(self):
        """Verifica se tentativas de aprovação ou operações financeiras externas disparam exceção."""
        with self.assertRaises(PermissionError):
            self.agent.approve_exception("PEN-0001", "Helena")

        with self.assertRaises(PermissionError):
            self.agent.execute_payment("Destinatario", Decimal("1000.00"))

        with self.assertRaises(PermissionError):
            self.agent.emit_invoice_external("NF-0001")


if __name__ == "__main__":
    unittest.main()
