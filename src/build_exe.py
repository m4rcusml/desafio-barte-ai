"""
Script para Compilação e Geração do Executável (.exe) via PyInstaller.
"""

from __future__ import annotations
import subprocess
import sys
import os
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.utils import configurar_saida_utf8, VERSAO_REGRAS


def build_executable():
    configurar_saida_utf8()
    src_dir = Path(__file__).resolve().parent
    app_py = src_dir / "app.py"
    dist_dir = src_dir.parent / "dist"

    print("=" * 70)
    print("🔨 COMPILANDO AGENTE TARVO PARA EXECUTÁVEL AUTÔNOMO (.EXE)")
    print(f"Origem : {app_py}")
    print(f"Destino: {dist_dir}")
    print("=" * 70)

    # Verifica se pyinstaller está disponível
    try:
        import PyInstaller
    except ImportError:
        print("Instalando PyInstaller...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)

    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=src_dir.parent,
                                capture_output=True, text=True, check=True, timeout=10).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        commit = None
    build_info = Path.cwd() / "build" / "tarvo_build.json"
    build_info.parent.mkdir(parents=True, exist_ok=True)
    build_info.write_text(json.dumps({"commit": commit, "versao_regras": VERSAO_REGRAS}), encoding="utf-8")
    # Embute apenas fontes Python; nunca inclui .env, credenciais ou dados financeiros.
    recursos = [f"--add-data={build_info}{os.pathsep}."]
    for source in sorted(src_dir.rglob("*.py")):
        destino = Path("src") / source.relative_to(src_dir).parent
        recursos.append(f"--add-data={source}{os.pathsep}{destino}")
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--name=fechamento_tarvo",
        f"--distpath={dist_dir}",
        f"--paths={src_dir.parent}",
        *recursos,
        str(app_py),
    ]

    print("Executando:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    print("\n✓ Executável compilado com sucesso em:", dist_dir / "fechamento_tarvo.exe")


if __name__ == "__main__":
    build_executable()
