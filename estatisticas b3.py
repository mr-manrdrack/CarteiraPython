import yfinance as yf
import numpy as np
import pandas as pd
import math

# ==============================
# 1. Baixar dados
# ==============================
tickers = ["PETR4.SA", "SMFT3.SA", "ITUB4.SA"]

dados = yf.download(
    tickers, 
    start="2020-01-01", 
    end="2025-01-01", 
    interval="1mo"
)["Close"]

# Baixar dividendos individuais
dividendos = {}
for t in tickers:
    dividendos[t] = yf.Ticker(t).dividends.resample("ME").sum()

dividendos_df = pd.DataFrame(dividendos)

# ==============================
# 2. Calcular retornos incluindo dividendos
# ==============================
retornos = pd.DataFrame()
for t in tickers:
    preco = dados[t]
    div = dividendos_df[t].reindex(preco.index).fillna(0)
    retorno = ((preco - preco.shift(1)) + div) / preco.shift(1)
    retornos[t] = retorno.dropna()

# ==============================
# 3. Funções manuais
# ==============================
def media_manual(vetor):
    return sum(vetor) / len(vetor)

def variancia_manual(vetor):
    m = media_manual(vetor)
    return sum((x - m)**2 for x in vetor) / (len(vetor) - 1)

def desvio_manual(vetor):
    return math.sqrt(variancia_manual(vetor))

def covariancia_manual(v1, v2):
    m1, m2 = media_manual(v1), media_manual(v2)
    return sum((x - m1)*(y - m2) for x, y in zip(v1, v2)) / (len(v1) - 1)

def correlacao_manual(v1, v2):
    return covariancia_manual(v1, v2) / (desvio_manual(v1)*desvio_manual(v2))

def coef_variacional(vetor):
    return desvio_manual(vetor) / media_manual(vetor)

# ==============================
# 4. Estatísticas por ativo
# ==============================
resultados = {}
for col in retornos.columns:
    serie = retornos[col].dropna().tolist()
    resultados[col] = {
        "Retorno Médio Mensal (%)": media_manual(serie) * 100,
        "Variância Mensal": variancia_manual(serie),
        "Desvio-padrão Mensal (%)": desvio_manual(serie) * 100,
        "Coef. Variação (%)": coef_variacional(serie) * 100
    }

analise = pd.DataFrame(resultados).T
print(" Estatísticas individuais (2021-2025) — incluindo dividendos\n")
print(analise)

# ==============================
# 5. Correlações 2 a 2
# ==============================
print("\n Correlações 2 a 2:")
for i in range(len(tickers)):
    for j in range(i+1, len(tickers)):
        serie1 = retornos[tickers[i]].dropna().tolist()
        serie2 = retornos[tickers[j]].dropna().tolist()
        rho = correlacao_manual(serie1, serie2)
        print(f"Correlação {tickers[i]} x {tickers[j]} = {rho:.4f}")

# Correlação média
serie1 = retornos[tickers[0]].dropna().tolist()
serie2 = retornos[tickers[1]].dropna().tolist()
serie3 = retornos[tickers[2]].dropna().tolist()

rho12 = correlacao_manual(serie1, serie2)
rho13 = correlacao_manual(serie1, serie3)
rho23 = correlacao_manual(serie2, serie3)
rho123 = (rho12 + rho13 + rho23) / 3
print(f"\n Correlação média entre os 3 ativos = {rho123:.4f}")

# ==============================
# 6. Retorno esperado da carteira (em R$)
# ==============================
capital_inicial = 100000
pesos = np.array([0.3, 0.3, 0.4])
medias = np.array([media_manual(retornos[col].dropna().tolist()) for col in retornos.columns])

retorno_port = np.dot(pesos, medias)
retorno_reais = capital_inicial * retorno_port

print(f"\n Retorno esperado da carteira = {retorno_port*100:.2f}% ao mês")
print(f" Retorno esperado sobre R$ {capital_inicial:,.2f} = R$ {retorno_reais:,.2f} ao mês")

# ==============================
# 7. CAPM com Betas do Yahoo Finance (base anual)
# ==============================
Rf_ano = 0.1364  # 13,64% ao ano

resultado_capm = {}

# Retorno médio do mercado (IBOVESPA) em base anual
ibov = yf.download("^BVSP", start="2021-01-01", end="2025-01-01", interval="1mo")["Close"]
retorno_mercado = np.log(ibov / ibov.shift(1)).dropna()
Rm_medio_mensal = float(retorno_mercado.mean())
Rm_medio_anual = (1 + Rm_medio_mensal)**12 - 1  # transforma em anual

for ativo in tickers:
    info = yf.Ticker(ativo).info
    beta = info.get("beta", None)

    # Retorno médio observado (mensal e anual)
    Ri_obs_mensal = float(media_manual(retornos[ativo].dropna().tolist()))
    Ri_obs_anual = (1 + Ri_obs_mensal)**12 - 1

    if beta is not None:
        beta = float(beta)
        capm = Rf_ano + beta * (Rm_medio_anual - Rf_ano)
        resultado_capm[ativo] = {
            "Beta (Yahoo)": beta,
            "CAPM (% ao ano)": capm * 100,
            "Retorno Médio Observado (% ao ano)": Ri_obs_anual * 100
        }
    else:
        resultado_capm[ativo] = {
            "Beta (Yahoo)": "N/A",
            "CAPM (% ao ano)": "N/A",
            "Retorno Médio Observado (% ao ano)": Ri_obs_anual * 100
        }

analise_capm = pd.DataFrame(resultado_capm).T
print("\n Análise CAPM (2021-2025) — Base Anual | Rf = 13,64% a.a. | Mercado = IBOVESPA\n")
print(analise_capm)
print("\n Retorno Médio do Mercado (IBOVESPA) anualizado: ", Rm_medio_anual * 100)


