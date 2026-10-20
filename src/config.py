"""Constantes de configuração: moedas, exibição e paleta de cores."""

MOEDAS = {
    "Bitcoin": "bitcoin",
    "Ethereum": "ethereum",
    "Solana": "solana",
    "Cardano": "cardano",
    "Dogecoin": "dogecoin",
}

MOEDAS_EXIBICAO = {
    "Dólar (US$)": {"codigo": "usd", "simbolo": "US$"},
    "Euro (€)": {"codigo": "eur", "simbolo": "€"},
    "Real (R$)": {"codigo": "brl", "simbolo": "R$"},
}

PALETA = [
    "#f7931a",  # laranja (bitcoin)
    "#627eea",  # azul (ethereum)
    "#00ffa3",  # verde (solana)
    "#0033ad",  # azul escuro (cardano)
    "#c2a633",  # dourado (dogecoin)
]