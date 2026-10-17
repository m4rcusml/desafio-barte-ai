"""Regressões de contrato, consulta, múltiplos lotes e execução empacotada."""
import csv
import io
import json
import shutil
import sys
import tempfile
import unittest
import zipfile
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from src.agent.consultant import TarvoConsultant
from src.engines.checkout_engine import processar_checkout
from src.graph import build_closing_graph, NativeStateGraph
import src.graph as graph_module
from src.state import ClosingState
from src.outputs.execution_store import preparar_execucao
from src.router.validation import validar_classificacao
from src.utils import configurar_saida_utf8, sha256_file

ROOT = Path(__file__).resolve().parents[1]


class TestContratosSemRegra(unittest.TestCase):
    def processar(self, taxa="0.025", vigencia="2026-01-01", tipo="1", original=""):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            taxas = base / "taxas.csv"
            taxas.write_text("cnpj;lojista;ec_orbe;vigencia;credito_a_vista\n"
                             f"12345678000100;Sintetico;9999999999;{vigencia};{taxa}\n", encoding="utf-8")
            tx = base / "orbe.csv"
            tx.write_text("id_transacao;data_movimento;cod_estabelecimento;nome_estabelecimento;tipo_lancamento;modalidade;qtd_parcelas;valor_bruto;taxa_aplicada_pct;valor_taxa;valor_liquido;bandeira;id_referencia;data_venda_original\n"
                          f"QA1;2026-10-10;9999999999;Sintetico;{tipo};1;1;1000.00;2.5;25.00;975.00;1;;{original}\n", encoding="utf-8")
            return processar_checkout([tx], taxas, competencia="2026-10")

    def test_fora_da_vigencia_bloqueia_e_preserva_taxa_observada(self):
        for vigencia in ("2026-11-01-apd", "2026-09-30-ate", "2026-11-01"):
            with self.subTest(vigencia=vigencia):
                result = self.processar(vigencia=vigencia)
                self.assertEqual(result.comissoes, [])
                pend = result.pendencias[0]
                self.assertEqual(pend.tipo, "CONTRATO_FORA_DA_VIGENCIA")
                self.assertEqual(pend.valor_brl, Decimal("25.00"))
                self.assertEqual(sum(r.valor for r in pend.rastro_itens), pend.valor_brl)

    def test_vigencia_invalida_nao_escolhe_primeiro_contrato(self):
        for vigencia in ("", "SEM DATA", "2026-13-01"):
            with self.subTest(vigencia=vigencia):
                result = self.processar(vigencia=vigencia)
                self.assertFalse(result.comissoes)
                self.assertEqual(result.pendencias[0].tipo, "VIGENCIA_CONTRATUAL_INVALIDA")

    def test_taxa_ausente_ou_invalida_nao_vira_zero(self):
        for taxa in ("", "invalida", "NaN", "Infinity", "-1", "padrão"):
            with self.subTest(taxa=taxa):
                result = self.processar(taxa=taxa)
                self.assertFalse(result.comissoes)
                self.assertEqual(result.pendencias[0].tipo, "TAXA_CONTRATUAL_AUSENTE_OU_INVALIDA")

    def test_zero_explicito_continua_isencao_valida(self):
        result = self.processar(taxa="0")
        self.assertFalse(result.pendencias)
        self.assertEqual(result.comissoes[0].comissao_brl, Decimal("0.00"))

    def test_estorno_valida_vigencia_da_venda_original(self):
        result = self.processar(vigencia="2026-10-01-apd", tipo="2", original="2026-09-30")
        self.assertFalse(result.comissoes)
        self.assertEqual(result.pendencias[0].tipo, "CONTRATO_FORA_DA_VIGENCIA")


class TestClassificacaoTipada(unittest.TestCase):
    def test_campos_invalidos_rejeitados_sem_inventar_confianca(self):
        valid = {"domain": "EXTRATO_AURORA", "confidence": 0.99, "is_delayed_batch": False}
        for changes in ({"domain": "INVENTADO"}, {"confidence": 1.5}, {"confidence": -1},
                        {"confidence": float("nan")}, {"confidence": True},
                        {"is_delayed_batch": "false"}, {"is_delayed_batch": 0}):
            with self.subTest(changes=changes):
                self.assertIsNone(validar_classificacao(dict(valid, **changes), "MOCK"))
        self.assertFalse(validar_classificacao(valid, "MOCK")["is_delayed_batch"])
        self.assertIsNone(validar_classificacao({"domain": "EXTRATO_AURORA"}, "MOCK"))


class TestConsultasEFontes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.base = Path(cls.tmp.name)
        cls.raw = cls.base / "raw"
        with zipfile.ZipFile(ROOT / "dados/originais/Tarvo_Data_Pack_set2026.zip") as z:
            z.extractall(cls.raw)
        shutil.copyfile(ROOT / "dados/originais/06_orbe_ajustes_tardios_set2026.csv",
                        cls.raw / "06_orbe_ajustes_tardios_set2026.csv")
        cls.output = cls.base / "saida"
        build_closing_graph().invoke({"data_dir": str(cls.raw), "output_dir_local": str(cls.base / "local"),
                                      "output_dir_oficial": str(cls.output), "competencia": "2026-09"})

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_consulta_nome_e_cnpj_identificam_horizonte_correta(self):
        consultant = TarvoConsultant(self.output)
        for query in ("Horizonte Viagens", "78.576.234/0001-79"):
            with self.subTest(query=query):
                self.assertEqual(consultant.explain_lojista(query)["cnpj"], "78576234000179")
        self.assertIn("erro", consultant.explain_lojista("Horizonte"))
        self.assertIn("erro", consultant.explain_lojista(""))

    def test_lojista_bloqueado_consultavel_por_cnpj(self):
        result = TarvoConsultant(self.output).explain_lojista("39566044000119")
        self.assertEqual(result["status"], "BLOQUEADO / EM PENDENCIA")
        self.assertEqual(len(result["pendencias"]), 57)

    def test_competencia_diferente_nao_reetiqueta_dados(self):
        with self.assertRaises(ValueError):
            TarvoConsultant(self.output, competencia="2026-10")
        self.assertEqual(TarvoConsultant(self.output, competencia="2026-09").get_summary()["competencia_iso"], "2026-09")

    def test_tres_lotes_incluidos_no_executor_disponivel_e_nativo(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d)
            inputs = folder / "raw"
            shutil.copytree(self.raw, inputs)
            with (inputs / "01_orbe_relatorio_comissoes_set2026.csv").open(encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f, delimiter=";")
                fields = reader.fieldnames
                sale = next(r for r in reader if r["cod_estabelecimento"] == "1038867654" and r["tipo_lancamento"] == "VENDA")
            sale["id_transacao"] = "QA_NOVA_VENDA_ARQUIVO_ADICIONAL"
            with (inputs / "07_orbe_extra.csv").open("w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fields, delimiter=";"); writer.writeheader(); writer.writerow(sale)
            native = NativeStateGraph(ClosingState)
            nodes = ["ingestao_triagem", "silver_formatters", "guardrail_1", "motores_dominio", "guardrail_2", "emissor_gold"]
            for name in nodes:
                native.add_node(name, getattr(graph_module, "node_" + name))
            native.set_entry_point(nodes[0])
            for a, b in zip(nodes, nodes[1:] + ["__end__"]):
                native.add_edge(a, b)
            totals = []
            for name, graph in (("disponivel", build_closing_graph()), ("nativo", native.compile())):
                state = graph.invoke({"data_dir": str(inputs), "output_dir_local": str(folder/name/"local"),
                                      "output_dir_oficial": str(folder/name/"saida"), "competencia": "2026-09"})
                self.assertTrue(any(r.ref_origem == sale["id_transacao"] for r in state["resultado_checkout"].rastro))
                totals.append(sum(c.comissao_brl for c in state["resultado_checkout"].comissoes))
            self.assertEqual(totals, [Decimal("203889.82"), Decimal("203889.82")])


class TestEmpacotamento(unittest.TestCase):
    def test_saida_redirecionada_cp1252_aceita_unicode(self):
        buffer = io.BytesIO()
        stream = io.TextIOWrapper(buffer, encoding="cp1252")
        with patch("sys.stdout", stream), patch("sys.stderr", stream):
            configurar_saida_utf8()
            print("🚀 Concluído")
            stream.flush()
        self.assertIn("🚀 Concluído", buffer.getvalue().decode("utf-8"))
        stream.detach()

    def test_snapshot_empacotado_tem_fontes_e_identidade_binaria(self):
        with tempfile.TemporaryDirectory() as d:
            folder = Path(d); raw = folder/"raw"; raw.mkdir()
            binary = folder/"fechamento_tarvo.exe"; binary.write_bytes(b"binario sintetico")
            original_ler = graph_module.preparar_execucao.__globals__["_ler"]
            def ler(path):
                return {"commit": "commit-do-build"} if path.name == "tarvo_build.json" else original_ler(path)
            state = {"data_dir": str(raw), "output_dir_oficial": str(folder/"saida"), "competencia": "2026-10"}
            with patch("sys.frozen", True, create=True), patch("sys.executable", str(binary)), patch("src.outputs.execution_store._ler", side_effect=ler):
                preparar_execucao(state)
            self.assertEqual(state["codigo_execucao"]["commit"], "commit-do-build")
            self.assertEqual(state["codigo_execucao"]["sha256_executavel"], sha256_file(binary))
            self.assertTrue((Path(state["execucao_stage"])/"codigo/src/app.py").is_file())
            self.assertGreater(len(state["codigo_execucao"]["arquivos"]), 0)
