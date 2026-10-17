"""
Cliente DeepSeek V1 Flash - Fallback Semântico de Alta Eficiência (Camada 3).
Acionado quando Jev e Gemini estão indisponíveis ou necessitam de validação cruzada.
"""

from __future__ import annotations
import os
import json
import urllib.request
import urllib.error
from typing import Any, Dict, Optional


class DeepSeekClient:
    """
    Cliente REST direto para o DeepSeek V1 Flash / DeepSeek Chat.
    Sem dependências externas pesadas (roda nativamente em Python standard e .exe).
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.api_url = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/chat/completions")
        self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-v1-flash")

    def is_available(self) -> bool:
        return bool(self.api_key)

    def classify_file(self, filename: str, sample_text: str) -> Optional[Dict[str, Any]]:
        if not self.is_available():
            return None

        system_prompt = (
            "Você é um classificador semântico especializado em infraestrutura contábil e financeira da Tarvo Pagamentos. "
            "Sua tarefa é analisar o nome do arquivo e a amostra de dados para classificar estritamente o domínio contábil correspondente. "
            "Responda EXCLUSIVAMENTE um objeto JSON válido."
        )

        user_prompt = f"""Analise o arquivo e classifique seu domínio financeiro:

Arquivo: {filename}
Amostra:
\"\"\"
{sample_text[:1200]}
\"\"\"

Responda APENAS um JSON com o seguinte formato:
{{
  "domain": "ORBE_FECHAMENTO_PRINCIPAL" | "ORBE_AJUSTES_TARDIOS" | "TABELA_TAXAS_CONTRATUAIS" | "EMAIL_PONTE_CAMBIO" | "PLANO_CONTAS_FENIX" | "EXTRATO_AURORA" | "EXTRATO_MERIDIANO" | "DESCONHECIDO",
  "confidence": 0.0 a 1.0,
  "is_delayed_batch": true | false,
  "reason": "breve justificativa técnica"
}}
"""

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.0,
            "response_format": {"type": "json_object"},
        }

        try:
            req = urllib.request.Request(
                self.api_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}",
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=4.0) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                text = res_data["choices"][0]["message"]["content"].strip()
                parsed = json.loads(text)
                return {
                    "domain": parsed.get("domain", "DESCONHECIDO"),
                    "confidence": float(parsed.get("confidence", 0.85)),
                    "is_delayed_batch": bool(parsed.get("is_delayed_batch", False)),
                    "delayed_prob": float(parsed.get("confidence", 0.85)) if parsed.get("is_delayed_batch") else 0.0,
                    "method": "DEEPSEEK_V1_FLASH",
                    "reason": parsed.get("reason", ""),
                }
        except Exception:
            # Fallback seguro para o próximo nível
            return None
