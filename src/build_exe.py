"""
Script para Compilação e Geração do Executável (.exe) via PyInstaller.
"""

from __future__ import annotations
import subprocess
import sys
from pathlib import Path


def build_executable():
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

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--name=fechamento_tarvo",
        f"--distpath={dist_dir}",
        f"--paths={src_dir.parent}",
        str(app_py),
    ]

    print("Executando:", " ".join(cmd))
    subprocess.run(cmd, check=True)
    print("\n✓ Executável compilado com sucesso em:", dist_dir / "fechamento_tarvo.exe")


if __name__ == "__main__":
    build_executable()
