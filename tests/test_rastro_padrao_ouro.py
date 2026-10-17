"""
Testes Unitários do Padrão Ouro de Auditabilidade e Rastro Universal.
"""

from __future__ import annotations
import csv
import json
import shutil
import sys
import tempfile
import unittest
import zipfile
from decimal import Decimal
from pathlib import Path

repo_root = Path(__file__).resolve().parent.parent
if str(repo_root) not in sys.path:
    sys.path.insert(0, str(repo_root))

from src.graph import build_closing_graph


class TestRastroPadraoOuro(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._tmpdir = tempfile.TemporaryDirectory()
        tmp_path = Path(cls._tmpdir.name)
        cls.repo_root = Path(__file__).resolve().parent.parent
        zip_path = cls.repo_root / "dados" / "originais" / "Tarvo_Data_Pack_set2026.zip"
        f06_orig = cls.repo_root / "dados" / "originais" / "06_orbe_ajustes_tardios_set2026.csv"

        cls.raw_dir = tmp_path / "raw_set2026"
        cls.raw_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(cls.raw_dir)
        shutil.copy(f06_orig, cls.raw_dir / f06_orig.name)

        cls.saida_dir = tmp_path / "saida_reproduzida"
        cls.local_dir = tmp_path / "fechamento-completo"
        graph = build_closing_graph()
        graph.invoke({
            "data_dir": str(cls.raw_dir),
            "output_dir_local": str(cls.local_dir),
            "output_dir_oficial": str(cls.saida_dir),
            "status_aprovacao": "PROVISORIO",
            "competencia": "2026-09",
        })

    @classmethod
    def tearDownClass(cls):
        cls._tmpdir.cleanup()

    def test_rastro_csv_headers_and_columns(self):
        """Verifica se o rastro.csv contém as 4 colunas obrigatórias seguidas das colunas de auditoria."""
        rastro_path = self.saida_dir / "rastro.csv"
        self.assertTrue(rastro_path.exists())

        with open(rastro_path, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=";")
            header = next(reader)
            self.assertEqual(header[:4], ["id_saida", "arquivo_origem", "ref_origem", "valor"])
            self.assertEqual(header[4:], ["regra_aplicada", "taxa_contratada_aplicada", "detalhe_calculo"])

    def test_regressao_setembro_2026_valores_verificados(self):
        """Verifica os totais de regressão de setembro/2026 (Checkout R$ 203.735,34, Remessa R$ 39.543,42, Div Remessa R$ 1.418,88)."""
        with open(self.saida_dir / "comissoes_por_lojista.csv", mode="r", encoding="utf-8") as f:
            com_rows = list(csv.DictReader(f, delimiter=";"))
        tot_chk = sum(Decimal(r["comissao_brl"]) for r in com_rows if r["linha_negocio"] == "CHECKOUT")
        tot_rem = sum(Decimal(r["comissao_brl"]) for r in com_rows if r["linha_negocio"] == "REMESSA")
        self.assertEqual(tot_chk, Decimal("203735.34"))
        self.assertEqual(tot_rem, Decimal("39543.42"))

        with open(self.saida_dir / "divergencias_taxa.csv", mode="r", encoding="utf-8") as f:
            div_rows = list(csv.DictReader(f, delimiter=";"))
        tot_div_rem = sum(Decimal(r["diferenca_brl"]) for r in div_rows if r["linha_negocio"] == "REMESSA")
        tot_div_chk = sum(Decimal(r["diferenca_brl"]) for r in div_rows if r["linha_negocio"] == "CHECKOUT")
        self.assertEqual(tot_div_rem, Decimal("1418.88"))
        self.assertEqual(tot_div_chk, Decimal("1576.23"))

    def test_prova_real_matematica_todos_os_ids(self):
        """Verifica centavo a centavo que sum(rastro) == valor reportado para COM, NF, DIV, LAN e PEN."""
        somas_rastro: dict[str, Decimal] = {}
        with open(self.saida_dir / "rastro.csv", mode="r", encoding="utf-8") as f:
            for row in csv.DictReader(f, delimiter=";"):
                sid = row["id_saida"]
                somas_rastro[sid] = somas_rastro.get(sid, Decimal("0.00")) + Decimal(row["valor"])

        pares_arquivos = [
            ("comissoes_por_lojista.csv", "comissao_brl"),
            ("notas_a_emitir.csv", "valor_brl"),
            ("divergencias_taxa.csv", "diferenca_brl"),
            ("lancamentos_classificados.csv", "valor"),
            ("pendencias.csv", "valor_brl"),
        ]
        for fname, col_val in pares_arquivos:
            with open(self.saida_dir / fname, mode="r", encoding="utf-8") as f:
                for row in csv.DictReader(f, delimiter=";"):
                    sid = row["id_saida"]
                    esperado = Decimal(row[col_val])
                    obtido = somas_rastro.get(sid, Decimal("0.00"))
                    self.assertEqual(
                        esperado,
                        obtido,
                        msg=f"Divergência em {fname} ({sid}): esperado {esperado}, rastro somou {obtido}",
                    )

    def test_casa_do_estudante_118_contribuicoes_orbe_sem_vinculo_aurora(self):
        """Verifica que a pendência consolidada da Casa tem 118 linhas Orbe reais no rastro e nenhum vínculo com Aurora."""
        with open(self.saida_dir / "pendencias.csv", mode="r", encoding="utf-8") as f:
            pends = list(csv.DictReader(f, delimiter=";"))
        pen_casa = next(p for p in pends if p["tipo"] == "ISENCAO_NAO_AVISADA")
        self.assertEqual(Decimal(pen_casa["valor_brl"]), Decimal("15396.77"))

        with open(self.saida_dir / "rastro.csv", mode="r", encoding="utf-8") as f:
            rastro_casa = [r for r in csv.DictReader(f, delimiter=";") if r["id_saida"] == pen_casa["id_saida"]]

        self.assertEqual(len(rastro_casa), 118)
        self.assertEqual(sum(Decimal(r["valor"]) for r in rastro_casa), Decimal("15396.77"))
        for r in rastro_casa:
            self.assertEqual(r["arquivo_origem"], "01_orbe_relatorio_comissoes_set2026.csv")
            self.assertNotIn("aurora", r["arquivo_origem"].lower())
            self.assertTrue(r["ref_origem"].startswith(("TX", "AN")))

    def test_rastreabilidade_100_porcento_ate_arquivos_originais_brutos(self):
        """Verifica que todas as referências do rastro.csv existem fisicamente nos arquivos originais brutos."""
        # 1. IDs brutos Orbe 01 e 06
        orbe_01_ids = set()
        with open(self.raw_dir / "01_orbe_relatorio_comissoes_set2026.csv", "r", encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter=";"):
                orbe_01_ids.add(r["id_transacao"].strip())

        orbe_06_ids = set()
        with open(self.raw_dir / "06_orbe_ajustes_tardios_set2026.csv", "r", encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter=";"):
                orbe_06_ids.add(r["id_transacao"].strip())

        # 2. Linhas físicas Aurora 05a
        with open(self.raw_dir / "05a_extrato_banco_aurora_cc4471_set2026.csv", "r", encoding="utf-8") as f:
            aurora_total_lines = sum(1 for _ in f)
        aurora_valid_refs = {f"L{i}" for i in range(1, aurora_total_lines + 1)}

        # 3. FITIDs Meridiano 05b
        ofx_text = (self.raw_dir / "05b_extrato_banco_meridiano_cc90233_set2026.ofx").read_text(encoding="latin1")

        with open(self.saida_dir / "rastro.csv", "r", encoding="utf-8") as f:
            for r in csv.DictReader(f, delimiter=";"):
                arq = r["arquivo_origem"]
                ref = r["ref_origem"]
                if arq == "01_orbe_relatorio_comissoes_set2026.csv":
                    self.assertIn(ref, orbe_01_ids, f"Ref {ref} ausente no arquivo bruto 01")
                elif arq == "06_orbe_ajustes_tardios_set2026.csv":
                    self.assertIn(ref, orbe_06_ids, f"Ref {ref} ausente no arquivo bruto 06")
                elif arq == "05a_extrato_banco_aurora_cc4471_set2026.csv":
                    self.assertIn(ref, aurora_valid_refs, f"Linha física {ref} inválida no extrato Aurora")
                elif arq == "05b_extrato_banco_meridiano_cc90233_set2026.ofx":
                    self.assertIn(ref, ofx_text, f"FITID {ref} ausente no extrato Meridiano")
                elif arq == "03_email_ponte_cambio_relatorio_set2026.eml":
                    self.assertTrue(ref.startswith("PC-0926-"), f"Operação Ponte {ref} inválida")

    def test_repeticao_idempotente_e_governanca_aprovacao_em_mudanca(self):
        """Verifica hashes, comparação entre execuções e revogação de aprovação quando dados mudam."""
        with tempfile.TemporaryDirectory() as tmp_exec:
            root_p = Path(tmp_exec)
            in_dir = root_p / "inputs"
            out_dir = root_p / "saida"
            loc_dir = root_p / "fechamento-completo"
            shutil.copytree(self.raw_dir, in_dir)

            graph = build_closing_graph()

            # Execução 1: aprovada por Helena
            s1 = graph.invoke({
                "data_dir": str(in_dir),
                "output_dir_local": str(loc_dir),
                "output_dir_oficial": str(out_dir),
                "status_aprovacao": "APROVADO_POR_HELENA",
                "competencia": "2026-09",
            })
            self.assertEqual(s1["status_aprovacao"], "APROVADO_POR_HELENA")
            self.assertEqual(s1["estado_tecnico"], "CONCLUIDO")

            # Execução 2: repetição idempotente com mesmas entradas -> mantém aprovação e confirma saidas_identicas=True
            s2 = graph.invoke({
                "data_dir": str(in_dir),
                "output_dir_local": str(loc_dir),
                "output_dir_oficial": str(out_dir),
                "status_aprovacao": "APROVADO_POR_HELENA",
                "competencia": "2026-09",
            })
            comp2 = s2["comparacao_execucao_anterior"]
            self.assertTrue(comp2["execucao_anterior_encontrada"])
            self.assertTrue(comp2["entradas_identicas"])
            self.assertTrue(comp2["saidas_identicas"])
            self.assertEqual(comp2["diferencas_metricas"], {})
            self.assertEqual(s2["status_aprovacao"], "APROVADO_POR_HELENA")

            # Execução 3: altera arquivo 06 adicionando nova venda -> resultados mudam, NÃO herda aprovação anterior!
            f06 = in_dir / "06_orbe_ajustes_tardios_set2026.csv"
            with open(f06, "a", encoding="utf-8", newline="") as fa:
                w = csv.writer(fa, delimiter=";")
                w.writerow([
                    "TX88999999", "30/09/2026", "1014537966", "DUBLIN HUB INTERCAMBIO",
                    "VENDA", "CREDITO A VISTA", "1", "VISA", "1000,00", "2,59", "25,90", "974,10", "", "",
                ])

            s3 = graph.invoke({
                "data_dir": str(in_dir),
                "output_dir_local": str(loc_dir),
                "output_dir_oficial": str(out_dir),
                "status_aprovacao": "APROVADO_POR_HELENA",
                "competencia": "2026-09",
            })
            comp3 = s3["comparacao_execucao_anterior"]
            self.assertFalse(comp3["entradas_identicas"])
            self.assertFalse(comp3["saidas_identicas"])
            self.assertTrue(comp3["heranca_aprovacao_bloqueada"])
            self.assertEqual(s3["status_aprovacao"], "REABERTO_PARA_REVISAO")
            self.assertIn("total_comissao_brl", comp3["diferencas_metricas"])


if __name__ == "__main__":
    unittest.main()

