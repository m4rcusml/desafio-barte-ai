"""
Testes Unitários do Padrão Ouro de Auditabilidade e Rastro Universal.
"""

from __future__ import annotations
import csv
import json
import unittest
from decimal import Decimal
from pathlib import Path


class TestRastroPadraoOuro(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parent.parent
        cls.saida_dir = cls.repo_root / "saida"

    def test_rastro_csv_headers_and_columns(self):
        """Verifica se o rastro.csv contém as 4 colunas obrigatórias seguidas das colunas de auditoria."""
        rastro_path = self.saida_dir / "rastro.csv"
        self.assertTrue(rastro_path.exists())

        with open(rastro_path, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=";")
            header = next(reader)
            self.assertEqual(header[:4], ["id_saida", "arquivo_origem", "ref_origem", "valor"])
            self.assertEqual(header[4:], ["regra_aplicada", "taxa_contratada_aplicada", "detalhe_calculo"])

    def test_prova_real_matematica_comissoes(self):
        """Verifica centavo a centavo que sum(rastro) == comissoes_por_lojista.csv para cada COM-XXXX."""
        somas_rastro: dict[str, Decimal] = {}
        with open(self.saida_dir / "rastro.csv", mode="r", encoding="utf-8") as f:
            for row in csv.DictReader(f, delimiter=";"):
                sid = row["id_saida"]
                if sid.startswith("COM-"):
                    somas_rastro[sid] = somas_rastro.get(sid, Decimal("0.00")) + Decimal(row["valor"])

        with open(self.saida_dir / "comissoes_por_lojista.csv", mode="r", encoding="utf-8") as f:
            for row in csv.DictReader(f, delimiter=";"):
                sid = row["id_saida"]
                esperado = Decimal(row["comissao_brl"])
                obtido = somas_rastro.get(sid, Decimal("0.00"))
                self.assertAlmostEqual(
                    float(esperado),
                    float(obtido),
                    places=2,
                    msg=f"Divergência na comissão {sid}: esperado {esperado}, rastro somou {obtido}",
                )

    def test_prova_real_matematica_notas(self):
        """Verifica centavo a centavo que sum(rastro) == notas_a_emitir.csv para cada NF-XXXX."""
        somas_rastro: dict[str, Decimal] = {}
        with open(self.saida_dir / "rastro.csv", mode="r", encoding="utf-8") as f:
            for row in csv.DictReader(f, delimiter=";"):
                sid = row["id_saida"]
                if sid.startswith("NF-"):
                    somas_rastro[sid] = somas_rastro.get(sid, Decimal("0.00")) + Decimal(row["valor"])

        with open(self.saida_dir / "notas_a_emitir.csv", mode="r", encoding="utf-8") as f:
            for row in csv.DictReader(f, delimiter=";"):
                sid = row["id_saida"]
                esperado = Decimal(row["valor_brl"])
                obtido = somas_rastro.get(sid, Decimal("0.00"))
                self.assertAlmostEqual(
                    float(esperado),
                    float(obtido),
                    places=2,
                    msg=f"Divergência na nota {sid}: esperado {esperado}, rastro somou {obtido}",
                )

    def test_prova_real_matematica_divergencias(self):
        """Verifica centavo a centavo que sum(rastro) == divergencias_taxa.csv para cada DIV-XXXX."""
        somas_rastro: dict[str, Decimal] = {}
        with open(self.saida_dir / "rastro.csv", mode="r", encoding="utf-8") as f:
            for row in csv.DictReader(f, delimiter=";"):
                sid = row["id_saida"]
                if sid.startswith("DIV-"):
                    somas_rastro[sid] = somas_rastro.get(sid, Decimal("0.00")) + Decimal(row["valor"])

        with open(self.saida_dir / "divergencias_taxa.csv", mode="r", encoding="utf-8") as f:
            for row in csv.DictReader(f, delimiter=";"):
                sid = row["id_saida"]
                esperado = Decimal(row["diferenca_brl"])
                obtido = somas_rastro.get(sid, Decimal("0.00"))
                self.assertAlmostEqual(
                    float(esperado),
                    float(obtido),
                    places=2,
                    msg=f"Divergência na divergência {sid}: esperado {esperado}, rastro somou {obtido}",
                )

    def test_manifesto_execucao_json_e_md_gerados(self):
        """Verifica a integridade dos manifestos de auditoria gerados."""
        manifesto_json = self.saida_dir / "auditoria_execucao.json"
        manifesto_md = self.saida_dir / "auditoria_execucao.md"
        self.assertTrue(manifesto_json.exists())
        self.assertTrue(manifesto_md.exists())

        with open(manifesto_json, mode="r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertTrue(data.get("prova_real_rastro_valida"))
            self.assertEqual(len(data.get("erros_conciliacao", [])), 0)
            self.assertGreater(data.get("total_ids_auditados", 0), 100)


if __name__ == "__main__":
    unittest.main()
