"""Contrato comum das classificações retornadas pelos modelos opcionais."""
import math

DOMINIOS = frozenset({
    "ORBE_FECHAMENTO_PRINCIPAL", "ORBE_AJUSTES_TARDIOS", "TABELA_TAXAS_CONTRATUAIS",
    "EMAIL_PONTE_CAMBIO", "PLANO_CONTAS_FENIX", "EXTRATO_AURORA", "EXTRATO_MERIDIANO", "DESCONHECIDO",
})


def validar_classificacao(parsed, method):
    if not isinstance(parsed, dict):
        return None
    domain, confidence, delayed = parsed.get("domain"), parsed.get("confidence"), parsed.get("is_delayed_batch")
    if not isinstance(domain, str) or domain not in DOMINIOS:
        return None
    if type(confidence) not in (int, float) or not math.isfinite(confidence) or not 0 <= confidence <= 1:
        return None
    if type(delayed) is not bool or not isinstance(parsed.get("reason", ""), str):
        return None
    return {
        "domain": domain, "confidence": float(confidence), "is_delayed_batch": delayed,
        "delayed_prob": float(confidence) if delayed else 0.0,
        "method": method, "reason": parsed.get("reason", ""),
    }
