"""
Orquestrador de Triagem Tripla (Jev -> Gemini Flash -> Heurística Local).
Garante classificação semântica inteligente sem nunca travar o pipeline.
"""

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List

from .jev_client import JevClient
from .gemini_client import GeminiFlashClient
from .deepseek_client import DeepSeekClient
from .heuristic_matcher import HeuristicMatcher


class TriTierRouter:
    """
    Roteador híbrido multi-tier:
    1. Tier 1: Jev (TypeSafe AI) - sub-500ms, System One tipado.
    2. Tier 2: Gemini Flash (Google GenAI) - Raciocínio semântico contextual.
    3. Tier 3: DeepSeek V1 Flash - Fallback semântico de alta eficiência e baixo custo.
    4. Tier 4: Heurística Local (0ms, 100% offline, zero dependências).
    """

    def __init__(self):
        self.jev = JevClient()
        self.gemini = GeminiFlashClient()
        self.deepseek = DeepSeekClient()
        self.heuristic = HeuristicMatcher()

    def classify(self, filepath: Path) -> Dict[str, Any]:
        sample_text = ""
        try:
            # Amostra inicial dos primeiros 2KB
            if filepath.suffix in (".csv", ".txt", ".eml", ".ofx"):
                with open(filepath, mode="r", encoding="utf-8", errors="ignore") as f:
                    sample_text = f.read(2048)
        except Exception:
            sample_text = ""

        # Tier 1: Jev (TypeSafe AI)
        if self.jev.is_available():
            res_jev = self.jev.classify_file(filepath.name, sample_text)
            if res_jev and res_jev.get("confidence", 0) >= 0.90:
                res_jev["caminho"] = str(filepath)
                res_jev["nome"] = filepath.name
                res_jev["extensao"] = filepath.suffix
                return res_jev

        # Tier 2: Gemini Flash
        if self.gemini.is_available():
            res_gem = self.gemini.classify_file(filepath.name, sample_text)
            if res_gem and res_gem.get("confidence", 0) >= 0.85:
                res_gem["caminho"] = str(filepath)
                res_gem["nome"] = filepath.name
                res_gem["extensao"] = filepath.suffix
                return res_gem

        # Tier 3: DeepSeek V1 Flash
        if self.deepseek.is_available():
            res_ds = self.deepseek.classify_file(filepath.name, sample_text)
            if res_ds and res_ds.get("confidence", 0) >= 0.85:
                res_ds["caminho"] = str(filepath)
                res_ds["nome"] = filepath.name
                res_ds["extensao"] = filepath.suffix
                return res_ds

        # Tier 4: Heurística Local (Garantia de 100% de disponibilidade)
        res_heu = self.heuristic.classify_file(filepath, sample_text)
        res_heu["caminho"] = str(filepath)
        res_heu["nome"] = filepath.name
        res_heu["extensao"] = filepath.suffix
        return res_heu

    def scan_directory(self, target_dir: Path) -> List[Dict[str, Any]]:
        """Varre o diretório e classifica todos os arquivos candidatos."""
        classified_files = []
        for item in sorted(target_dir.iterdir()):
            if item.is_file() and item.suffix.lower() in (".csv", ".xlsx", ".eml", ".ofx"):
                info = self.classify(item)
                classified_files.append(info)
        return classified_files
