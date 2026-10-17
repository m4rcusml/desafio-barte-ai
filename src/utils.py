"""
Funções Utilitárias e Constantes Canônicas (Tarvo Closing Engine).
"""

from __future__ import annotations
import os
import re
from pathlib import Path
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Any, Dict


def load_dotenv_safe(env_path: Optional[Path] = None) -> None:
    """Carrega variáveis do arquivo .env para os.environ sem dependências externas."""
    candidate_paths = []
    if env_path:
        candidate_paths.append(env_path)
    # Procura na pasta src, no cwd e na raiz do repo
    src_dir = Path(__file__).resolve().parent
    candidate_paths.extend([
        src_dir / ".env",
        src_dir.parent / ".env",
        Path.cwd() / ".env",
        Path.cwd() / "src" / ".env",
    ])

    for p in candidate_paths:
        if p.exists() and p.is_file():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if line.startswith("export "):
                            line = line[7:].strip()
                        if "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip("\"'").strip()
                            if k and k not in os.environ:
                                os.environ[k] = v
                break
            except Exception:
                pass


# Carrega automaticamente ao importar
load_dotenv_safe()

# Legendas de codificação numérica para otimização tabular
LEGENDS: Dict[str, Dict[str, int]] = {
    "orbe_tipo_lancamento": {
        "VENDA": 1,
        "ESTORNO": 2,
        "ANTECIPACAO": 3,
        "REVERSAO ANTECIPACAO": 4,
    },
    "orbe_modalidade": {
        "": 0,
        "CREDITO A VISTA": 1,
        "CREDITO PARCELADO": 2,
        "PIX": 3,
        "DEBITO": 4,
    },
    "orbe_bandeira": {
        "": 0,
        "MASTERCARD": 1,
        "ELO": 2,
        "VISA": 3,
        "AMEX": 4,
        "HIPERCARD": 5,
    },
}


def round_half_up(val: Decimal) -> Decimal:
    """Arredonda para 2 casas decimais usando ROUND_HALF_UP (centavo a centavo)."""
    return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def fmt_money_br_to_dot(val: Optional[str]) -> str:
    """Remove separador de milhar e substitui vírgula por ponto (ex: '66.026,00' -> '66026.00')."""
    if val is None:
        return ""
    s = str(val).strip().replace(" ", "").replace(".", "")
    return s.replace(",", ".")


def fmt_date_iso(val: Optional[str]) -> str:
    """Converte datas (DD/MM/AAAA, YYYYMMDD, YYYY-MM-DD) para o padrão ISO AAAA-MM-DD."""
    if not val:
        return ""
    s = str(val).strip()
    if not s:
        return ""
    if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        return s
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", s)
    if m:
        return f"{int(m.group(3)):04d}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    m_ofx = re.match(r"^(\d{4})(\d{2})(\d{2})", s)
    if m_ofx:
        return f"{m_ofx.group(1)}-{m_ofx.group(2)}-{m_ofx.group(3)}"
    return s


def fmt_decimal_dot(val: Optional[str]) -> str:
    """Padroniza valores monetários e percentuais para formato com ponto decimal."""
    if val is None:
        return ""
    s = str(val).strip()
    if not s:
        return ""
    s = s.rstrip("%").strip()
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".")
    elif "," in s:
        s = s.replace(",", ".")
    return s


def fmt_clean_cnpj(val: Optional[str]) -> str:
    """Remove formatação de CNPJ retornando apenas os 14 dígitos numéricos."""
    if not val:
        return ""
    clean = re.sub(r"[.\/\-\s]", "", str(val))
    return clean.zfill(14) if clean.isdigit() and len(clean) == 13 else clean


def fmt_vigencia(val: Optional[str]) -> str:
    """Formata o campo vigência para o padrão AAAA-MM-DD-categoria (apd / ate)."""
    if not val:
        return ""
    s = str(val).strip()
    s_lower = s.lower()
    m_data = re.search(r"(\d{1,2})/(\d{1,2})/(\d{4})", s)
    if not m_data:
        return s
    day, month, year = int(m_data.group(1)), int(m_data.group(2)), int(m_data.group(3))
    iso_date = f"{year:04d}-{month:02d}-{day:02d}"
    if "a partir de" in s_lower or "partir" in s_lower:
        return f"{iso_date}-apd"
    elif "até" in s_lower or "ate" in s_lower:
        return f"{iso_date}-ate"
    return iso_date

