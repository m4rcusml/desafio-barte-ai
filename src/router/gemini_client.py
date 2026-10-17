"""
Cliente Gemini Flash - Fallback Semântico de Raciocínio (Camada 2).
Acionado quando o Jev não está disponível ou retorna confiança incerta.
"""

from __future__ import annotations
import os
import json
import urllib.request
import urllib.error
from typing import Any, Dict, Optional
from .validation import validar_classificacao


class GeminiFlashClient:
    """
    Cliente REST direto para o Google Gemini Flash.
    Não requer dependências externas pesadas (roda em qualquer ambiente Python / .exe).
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

    def is_available(self) -> bool:
        return bool(self.api_key)

    def classify_file(self, filename: str, sample_text: str) -> Optional[Dict[str, Any]]:
        if not self.is_available():
            return None

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

        prompt = f"""Você é um classificador de infraestrutura financeira da Tarvo Pagamentos.
Analise o nome do arquivo e a amostra de dados para classificar a qual domínio do fechamento ele pertence.

Arquivo: {filename}
Amostra:
\"\"\"
{sample_text[:1200]}
\"\"\"

Responda APENAS um JSON válido no seguinte formato:
{{
  "domain": "ORBE_FECHAMENTO_PRINCIPAL" | "ORBE_AJUSTES_TARDIOS" | "TABELA_TAXAS_CONTRATUAIS" | "EMAIL_PONTE_CAMBIO" | "PLANO_CONTAS_FENIX" | "EXTRATO_AURORA" | "EXTRATO_MERIDIANO" | "DESCONHECIDO",
  "confidence": 0.0 a 1.0,
  "is_delayed_batch": true | false,
  "reason": "breve justificativa"
}}
"""

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.0, "responseMimeType": "application/json"},
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=15.0) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                text = res_data["candidates"][0]["content"]["parts"][0]["text"].strip()
                parsed = json.loads(text)
                return validar_classificacao(parsed, "GEMINI_FLASH")
        except urllib.error.HTTPError as e:
            e.close()
            return None
        except Exception:
            # Fallback para classificador heurístico local
            return None
