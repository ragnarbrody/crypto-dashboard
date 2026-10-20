"""Geração de cores estáveis por moeda."""
import hashlib

from src.config import MOEDAS, PALETA


def cor_por_moeda(moeda_id: str) -> str:
    """
    Gera uma cor estavel a partir do id (mesmo id -> mesma cor sempre).
    se a moeada não estiver na lista, usa um fallback
    """
    chaves = list(MOEDAS.values())
    if moeda_id in chaves:
        return PALETA[chaves.index(moeda_id) % len(PALETA)]
    # fallback: hash determinístico
    h = hashlib.md5(moeda_id.encode()).hexdigest()
    return f"#{h[:6]}"