"""
Módulo da Camada Agêntica e Consultiva da Tarvo.
"""

__all__ = ["TarvoConsultant"]


def __getattr__(name: str):
    if name == "TarvoConsultant":
        from .consultant import TarvoConsultant
        return TarvoConsultant
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
