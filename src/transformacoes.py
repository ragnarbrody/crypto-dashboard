"""Transformações de dados."""
import pandas as pd


def normalizar_base100(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converte cada moeda para base 100 no primeiro dia 
    (para ter uma leitura mais justas de moedas com valores muito diferentes).
    """
    df = df.copy()
    df["preco_norm"] = df.groupby("moeda")["preco"].transform(
        lambda s: s / s.iloc[0] * 100
    )
    return df