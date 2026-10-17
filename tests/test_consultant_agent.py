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


class TestConsultantAgent(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.agent = TarvoConsultant()

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
