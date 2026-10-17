"""
Cliente Jev (TypeSafe AI) - Decisões Semânticas Tipadas (System One).
Executa chamadas não-autoregressivas rápidas com probabilidades calibradas.
"""

from __future__ import annotations
import os
import json
import urllib.request
import urllib.error
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class NoulResult:
    value: bool
    prob: float


@dataclass
class ChoiceResult:
    value: str
    score: float
    probabilities: Dict[str, float]


class JevClient:
    """
    Cliente para Jev (TypeSafe AI).
    Se TYPE_SAFE_API_KEY / JEV_API_KEY estiver configurada, faz a inferência online.
    Se não houver chave ou houver falha de rede, devolve None para permitir fallback para Gemini Flash.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("JEV_API_KEY") or os.getenv("TYPESAFE_API_KEY")
        self.api_url = os.getenv("JEV_API_URL", "https://api.typesafe.ai/v1/decide")
        self.model = os.getenv("JEV_MODEL", "jev-1")

    def is_available(self) -> bool:
        return bool(self.api_key)

    def classify_file(self, filename: str, sample_text: str) -> Optional[Dict[str, Any]]:
        """
        Classifica um arquivo usando primitivas tipadas Jev (Choice e Noul).
        """
        if not self.is_available():
            return None

        payload = {
            "model": self.model,
            "context": f"Filename: {filename}\nSample:\n{sample_text[:1500]}",
            "questions": {
                "pipeline_domain": {
                    "type": "choice",
                    "options": [
                        "ORBE_FECHAMENTO_PRINCIPAL",
                        "ORBE_AJUSTES_TARDIOS",
                        "TABELA_TAXAS_CONTRATUAIS",
                        "EMAIL_PONTE_CAMBIO",
                        "PLANO_CONTAS_FENIX",
                        "EXTRATO_AURORA",
                        "EXTRATO_MERIDIANO",
                        "DESCONHECIDO",
                    ],
                },
                "is_delayed_batch": {
                    "type": "noul",
                    "question": "O lote representa estornos tardios, reversões ou movimentações retroativas?",
                },
            },
        }

        try:
            req = urllib.request.Request(
                self.api_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                    "User-Agent": "Tarvo-Closing-Agent/1.0",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                choice_res = data.get("answers", {}).get("pipeline_domain", {})
                noul_res = data.get("answers", {}).get("is_delayed_batch", {})
                return {
                    "domain": choice_res.get("value"),
                    "confidence": float(choice_res.get("score", 0.0)),
                    "is_delayed_batch": bool(noul_res.get("value", False)),
                    "delayed_prob": float(noul_res.get("prob", 0.0)),
                    "method": "JEV",
                }
        except urllib.error.HTTPError as e:
            e.close()
            return None
        except Exception:
            # Falha de conexão ou timeout: delega silenciosamente para Gemini Flash
            return None
