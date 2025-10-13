import yfinance as yf
import pandas as pd
import numpy as np
import io
import requests
import zipfile
import matplotlib.pyplot as plt

# ==============================
# 1. Configuração
# ==============================
tickers = ["PETR4.SA", "SMFT3.SA", "ITUB4.SA"]
anos_desejados = [2021, 2022, 2023, 2024]

def safe_get(df, key):
    try:
        return float(df.get(key, 0))
    except Exception:
        return 0.0

# ==============================
# 2. Coleta dos dados da CVM
# ==============================
def coletar_dados_cvm(nome_empresa):
    """
    Baixa e extrai os dados DFP da CVM (2021–2024)
    Retorna DataFrames de BPA (Ativo), BPP (Passivo) e DRE.
    """
    anos = [2021, 2022, 2023, 2024]
    base_url = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/dfp_cia_aberta_{}.zip"

    dfs_bpa, dfs_bpp, dfs_dre = [], [], []

    for ano in anos:
        url = base_url.format(ano)
        print(f"📥 Baixando {url}...")

        try:
            response = requests.get(url)
            response.raise_for_status()
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                for nome_arquivo in z.namelist():
                    nome_lower = nome_arquivo.lower()
                    if "bpa_con" in nome_lower:  # Ativo
                        with z.open(nome_arquivo) as f:
                            df = pd.read_csv(f, sep=";", encoding="latin1", low_memory=False)
                            dfs_bpa.append(df)
                    elif "bpp_con" in nome_lower:  # Passivo
                        with z.open(nome_arquivo) as f:
                            df = pd.read_csv(f, sep=";", encoding="latin1", low_memory=False)
                            dfs_bpp.append(df)
                    elif "dre_con" in nome_lower:  # DRE
                        with z.open(nome_arquivo) as f:
                            df = pd.read_csv(f, sep=";", encoding="latin1", low_memory=False)
                            dfs_dre.append(df)
        except Exception as e:
            print(f"⚠️ Erro ao processar {ano}: {e}")

    def combinar_filtrar(dfs):
        if not dfs:
            return pd.DataFrame()
        df = pd.concat(dfs, ignore_index=True)
        cols = [c.upper().strip() for c in df.columns]
        df.columns = cols
        if "DENOM_CIA" in df.columns:
            df = df[df["DENOM_CIA"].str.contains(nome_empresa, case=False, na=False)]
        return df

    return combinar_filtrar(dfs_bpa), combinar_filtrar(dfs_bpp), combinar_filtrar(dfs_dre)

# ==============================
# 3. Função aprimorada de extração de valores
# ==============================
def obter_valor(df, termo, ano):
    """Busca o valor de uma conta específica no ano informado."""
    if df.empty:
        return 0.0

    col_data = "DT_REFER" if "DT_REFER" in df.columns else "DT_FIM_EXERC"
    col_valor = "VL_CONTA" if "VL_CONTA" in df.columns else "VALOR"
    col_cd = "CD_CONTA" if "CD_CONTA" in df.columns else None
    col_ds = "DS_CONTA" if "DS_CONTA" in df.columns else None

    # Mantém apenas contas fixas (S)
    if "ST_CONTA_FIXA" in df.columns:
        df = df[df["ST_CONTA_FIXA"].astype(str).str.upper().eq("S")]

    # Filtro: por código ou descrição
    if any(c.isdigit() for c in termo):
        filtro = df[
            df[col_data].astype(str).str.contains(str(ano))
            & df[col_cd].astype(str).str.startswith(termo[:4])
        ]
    else:
        filtro = df[
            df[col_data].astype(str).str.contains(str(ano))
            & df[col_ds].astype(str).str.contains(termo, case=False, na=False)
        ]

    if not filtro.empty:
        try:
            valor_raw = str(filtro[col_valor].iloc[0]).replace(".", "").replace(",", ".")
            valor = float(valor_raw)
            return valor * 1000  # converte de mil para reais
        except Exception:
            return 0.0
    return 0.0

# ==============================
# 4. Cálculos e integração
# ==============================
resultados = []

for ticker in tickers:
    print(f"\n📊 Coletando dados de {ticker}...")

    nome_empresa = "PETRO" if "PETR" in ticker else "ITAÚ" if "ITUB" in ticker else "SMARTFIT"

    # Yahoo
    t = yf.Ticker(ticker)
    balanco = t.balance_sheet
    dre = t.financials
    if not balanco.empty:
        balanco = balanco.T
        balanco.index = balanco.index.year
    if not dre.empty:
        dre = dre.T
        dre.index = dre.index.year

    # CVM
    bpa, bpp, df_dre = coletar_dados_cvm(nome_empresa)

    for ano in anos_desejados:
        ativo_circ = passivo_circ = estoques = fornecedores = ativo_total = receita = cpv = np.nan

        # Yahoo
        if not balanco.empty and ano in balanco.index:
            ativo_circ = safe_get(balanco.loc[ano], "Total Current Assets")
            passivo_circ = safe_get(balanco.loc[ano], "Total Current Liabilities")
            estoques = safe_get(balanco.loc[ano], "Inventory")
            fornecedores = safe_get(balanco.loc[ano], "Accounts Payable")
            ativo_total = safe_get(balanco.loc[ano], "Total Assets")
        if not dre.empty and ano in dre.index:
            receita = safe_get(dre.loc[ano], "Total Revenue")
            cpv = safe_get(dre.loc[ano], "Cost Of Revenue")

        # CVM fallback com códigos + nomes
        if np.isnan(ativo_circ) or ativo_circ == 0:
            ativo_circ = obter_valor(bpa, "1.01", ano) or obter_valor(bpa, "ATIVO CIRCULANTE", ano)
        if np.isnan(passivo_circ) or passivo_circ == 0:
            passivo_circ = obter_valor(bpp, "2.01", ano) or obter_valor(bpp, "PASSIVO CIRCULANTE", ano)
        if np.isnan(estoques) or estoques == 0:
            estoques = obter_valor(bpa, "1.02.04", ano) or obter_valor(bpa, "ESTOQUES", ano)
        if np.isnan(fornecedores) or fornecedores == 0:
            fornecedores = obter_valor(bpp, "2.01.02", ano) or obter_valor(bpp, "FORNECEDORES", ano)
        if np.isnan(ativo_total) or ativo_total == 0:
            ativo_total = obter_valor(bpa, "1", ano) or obter_valor(bpa, "ATIVO TOTAL", ano)
        if np.isnan(receita) or receita == 0:
            receita = obter_valor(df_dre, "3.01", ano) or obter_valor(df_dre, "RECEITA", ano)
        if np.isnan(cpv) or cpv == 0:
            cpv = obter_valor(df_dre, "3.02", ano) or obter_valor(df_dre, "CUSTO", ano)

        # Indicadores
        if passivo_circ > 0:
            liquidez_corrente = ativo_circ / passivo_circ
            liquidez_seca = (ativo_circ - estoques) / passivo_circ
        else:
            liquidez_corrente = liquidez_seca = np.nan

        giro_ativo = receita / ativo_total if ativo_total > 0 else np.nan
        prazo_medio_pagamento = (fornecedores / cpv) * 365 if cpv > 0 else np.nan

        resultados.append({
            "Empresa": ticker,
            "Ano": ano,
            "Liquidez Corrente": "Não disponível" if np.isnan(liquidez_corrente) else round(liquidez_corrente, 2),
            "Liquidez Seca": "Não disponível" if np.isnan(liquidez_seca) else round(liquidez_seca, 2),
            "Giro do Ativo": "Não disponível" if np.isnan(giro_ativo) else round(giro_ativo, 2),
            "Prazo Médio de Pagamento (dias)": "Não disponível" if np.isnan(prazo_medio_pagamento) else round(prazo_medio_pagamento, 2)
        })

# ==============================
# 5. Exibir resultados
# ==============================
tabela = pd.DataFrame(resultados)
tabela = tabela.sort_values(by=["Empresa", "Ano"]).reset_index(drop=True)

print("\n📊 Indicadores Financeiros (2021–2024)\n")
print(tabela.to_string(index=False))
tabela.to_excel("indicadores_financeiros.xlsx", index=False)
print("\n✅ Resultados salvos em 'indicadores_financeiros.xlsx'.")

# ==============================
# 6. Gráfico comparativo
# ==============================
try:
    for indicador in ["Liquidez Corrente", "Giro do Ativo", "Prazo Médio de Pagamento (dias)"]:
        plt.figure(figsize=(8, 5))
        df_plot = tabela[tabela[indicador] != "Não disponível"]
        df_plot = df_plot.astype({"Ano": int, indicador: float})
        for emp in df_plot["Empresa"].unique():
            plt.plot(df_plot[df_plot["Empresa"] == emp]["Ano"],
                     df_plot[df_plot["Empresa"] == emp][indicador],
                     marker="o", label=emp)
        plt.title(f"{indicador} (2021–2024)")
        plt.xlabel("Ano")
        plt.ylabel(indicador)
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.tight_layout()
        plt.show()
except Exception:
    print("\n(Matplotlib não disponível — gráficos desativados)")

