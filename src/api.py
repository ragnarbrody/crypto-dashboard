"""Funções de acesso da API CoinGecko."""
import pandas as pd
import requests
import streamlit as st

API_KEY = st.secrets["COINGECKO_API_KEY"]
BASE_URL = "https://api.coingecko.com/api/v3"
HEADERS = {"x-cg-demo-api-key": API_KEY}


@st.cache_data(ttl=400)
def buscar_historico(moeda_id: str, dias: int, vs_currency: str) -> pd.DataFrame:
    """Busca preço e volume histórico de uma moeda."""
    url = f"{BASE_URL}/coins/{moeda_id}/market_chart"
    params = {"vs_currency": vs_currency, "days": dias}
    resposta = requests.get(url, params=params, headers=HEADERS, timeout=10)
    resposta.raise_for_status()
    dados = resposta.json()

    df_preco = pd.DataFrame(dados["prices"], columns=["timestamp", "preco"])
    df_vol = pd.DataFrame(dados["total_volumes"], columns=["timestamp", "volume"])

    df = df_preco.merge(df_vol, on="timestamp", how="left")
    df["data"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df[["data", "preco", "volume"]]


@st.cache_data(ttl=400)
def buscar_comparacao(moeda_ids: list[str], dias: int, vs_currency: str) -> pd.DataFrame:
    """Busca preço de várias moedas e retorna DataFrame longo (data, moeda, preco)."""
    frames = []
    for mid in moeda_ids:
        url = f"{BASE_URL}/coins/{mid}/market_chart"
        params = {"vs_currency": vs_currency, "days": dias}
        resposta = requests.get(url, params=params, headers=HEADERS, timeout=10)
        resposta.raise_for_status()
        dados = resposta.json()["prices"]
        df_m = pd.DataFrame(dados, columns=["timestamp", "preco"])
        df_m["data"] = pd.to_datetime(df_m["timestamp"], unit="ms")
        df_m["moeda"] = mid
        frames.append(df_m[["data", "preco", "moeda"]])
    return pd.concat(frames, ignore_index=True)