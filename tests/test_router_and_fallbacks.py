"""
Testes Unitários do Roteador Multi-Tier e Cadeia de Fallback (Jev -> Gemini -> DeepSeek -> Heurística).
"""

from __future__ import annotations
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.router.triage import TriTierRouter
from src.router.jev_client import JevClient
from src.router.gemini_client import GeminiFlashClient
from src.router.deepseek_client import DeepSeekClient
from src.router.heuristic_matcher import HeuristicMatcher


class TestRouterAndFallbacks(unittest.TestCase):

    def setUp(self):
        self.router = TriTierRouter()

    def test_heuristic_fallback_classifies_correctly(self):
        """Verifica se o fallback offline classifica todos os padrões de arquivos do fechamento."""
        matcher = HeuristicMatcher()
        
        # 1. Orbe Principal
        res = matcher.classify_file(Path("01_orbe_relatorio_comissoes_set2026.csv"), "")
        self.assertEqual(res["domain"], "ORBE_FECHAMENTO_PRINCIPAL")
        self.assertFalse(res["is_delayed_batch"])
        
        # 2. Orbe Tardios
        res06 = matcher.classify_file(Path("06_orbe_ajustes_tardios_set2026.csv"), "")
        self.assertEqual(res06["domain"], "ORBE_AJUSTES_TARDIOS")
        self.assertTrue(res06["is_delayed_batch"])
        
        # 3. Tabela de Taxas
        res_taxas = matcher.classify_file(Path("02_tabela_taxas_contratadas.xlsx"), "")
        self.assertEqual(res_taxas["domain"], "TABELA_TAXAS_CONTRATUAIS")
        
        # 4. Ponte Câmbio
        res_ponte = matcher.classify_file(Path("03_email_ponte_cambio_relatorio_set2026.eml"), "")
        self.assertEqual(res_ponte["domain"], "EMAIL_PONTE_CAMBIO")
        
        # 5. Aurora
        res_aurora = matcher.classify_file(Path("05a_extrato_banco_aurora_cc4471_set2026.csv"), "")
        self.assertEqual(res_aurora["domain"], "EXTRATO_AURORA")
        
        # 6. Meridiano
        res_meridiano = matcher.classify_file(Path("05b_extrato_banco_meridiano_cc90233_set2026.ofx"), "")
        self.assertEqual(res_meridiano["domain"], "EXTRATO_MERIDIANO")

    def test_deepseek_client_initialization_and_availability(self):
        """Verifica a inicialização e disponibilidade do cliente DeepSeek V1 Flash."""
        client = DeepSeekClient()
        expected_model = os.getenv("DEEPSEEK_MODEL", "deepseek-v1-flash")
        self.assertEqual(client.model, expected_model)
        self.assertIn("deepseek.com", client.api_url)
        # Sem chave de API no ambiente, is_available deve retornar False de forma graciosa
        if not client.api_key:
            self.assertFalse(client.is_available())
            self.assertIsNone(client.classify_file("arquivo.csv", "amostra"))

    def test_deepseek_fallback_called_when_jev_and_gemini_unavailable(self):
        """Testa se o DeepSeek V1 Flash é acionado quando Jev e Gemini falham ou não estão disponíveis."""
        router = TriTierRouter()
        router.jev.is_available = MagicMock(return_value=False)
        router.gemini.is_available = MagicMock(return_value=False)
        router.deepseek.is_available = MagicMock(return_value=True)
        router.deepseek.classify_file = MagicMock(return_value={
            "domain": "ORBE_FECHAMENTO_PRINCIPAL",
            "confidence": 0.95,
            "is_delayed_batch": False,
            "delayed_prob": 0.0,
            "method": "DEEPSEEK_V1_FLASH",
            "reason": "Classificação via DeepSeek V1 Flash mock",
        })

        res = router.classify(Path("01_orbe_relatorio_comissoes_set2026.csv"))
        self.assertEqual(res["domain"], "ORBE_FECHAMENTO_PRINCIPAL")
        self.assertEqual(res["method"], "DEEPSEEK_V1_FLASH")
        router.deepseek.classify_file.assert_called_once()

    def test_cascade_falls_through_to_heuristics_when_all_llms_fail(self):
        """Testa se o roteador cai com segurança na heurística local quando todos os LLMs falham."""
        router = TriTierRouter()
        router.jev.is_available = MagicMock(return_value=True)
        router.jev.classify_file = MagicMock(return_value=None)
        router.gemini.is_available = MagicMock(return_value=True)
        router.gemini.classify_file = MagicMock(return_value=None)
        router.deepseek.is_available = MagicMock(return_value=True)
        router.deepseek.classify_file = MagicMock(return_value=None)

        res = router.classify(Path("06_orbe_ajustes_tardios_set2026.csv"))
        self.assertEqual(res["domain"], "ORBE_AJUSTES_TARDIOS")
        self.assertEqual(res["method"], "HEURISTICA")
        self.assertTrue(res["is_delayed_batch"])


if __name__ == "__main__":
    unittest.main()
