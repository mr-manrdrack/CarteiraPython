"""
CÓDIGO COMPLETO EM PYTHON PARA TODOS OS CÁLCULOS DA MONOGRAFIA
VALUATION DE EMPRESAS DO SETOR DE GAMES NO JAPÃO
SEGA SAMMY, NINTENDO E CAPCOM (2022-2024)
"""

import pandas as pd
import numpy as np
from datetime import datetime

print("=" * 80)
print("MONOGRAFIA - VALUATION DE EMPRESAS DO SETOR DE GAMES NO JAPÃO")
print("Período de Análise: 2022-2024")
print("Data de Mercado: Dezembro 2024")
print("=" * 80)
print()

# ============================================================================
# 1. DADOS DE ENTRADA - TABELA 1: VALUATION RELATIVA (2024)
# ============================================================================

print("=" * 80)
print("TABELA 1 - MÚLTIPLOS DE VALUATION RELATIVA (2024)")
print("=" * 80)

# Dados de mercado (Dezembro 2024)
valuation_relativa = {
    'Empresa': ['SEGA SAMMY', 'NINTENDO', 'CAPCOM'],
    'Ticker': ['6460.T', '7974.T', '9697.T'],
    'Preço (¥)': [3076.00, 9264.00, 3474.00],
    'LPA 2024 (¥)': [150.75, 421.39, 103.71],
    'Market Cap (¥B)': [548.20, 13500.00, 1600.00],
    'Total Equity (¥B)': [357.70, 2607.46, 195.24],
    'EBITDA (¥B)': [58.61, 698.75, 63.56],
    'Net Debt (¥B)': [-49.87, -1881.08, -97.67]  # Negativo = mais caixa
}

df_valuation = pd.DataFrame(valuation_relativa)

# Cálculo de múltiplos
df_valuation['P/L'] = df_valuation['Preço (¥)'] / df_valuation['LPA 2024 (¥)']
df_valuation['P/B'] = df_valuation['Market Cap (¥B)'] / df_valuation['Total Equity (¥B)']
df_valuation['EV (¥B)'] = df_valuation['Market Cap (¥B)'] + df_valuation['Net Debt (¥B)']
df_valuation['EV/EBITDA'] = df_valuation['EV (¥B)'] / df_valuation['EBITDA (¥B)']

print(df_valuation[['Empresa', 'Ticker', 'Preço (¥)', 'P/L', 'P/B', 'EV/EBITDA']].to_string(index=False))
print()
print(f"✓ SEGA SAMMY possui o menor P/L ({df_valuation.loc[0, 'P/L']:.2f})")
print(f"✓ SEGA SAMMY selecionada para análise DCF aprofundada")
print()

# ============================================================================
# 2. DADOS DE ENTRADA - TABELA 2: CRESCIMENTO HISTÓRICO (2022-2024)
# ============================================================================

print("=" * 80)
print("TABELA 2 - CRESCIMENTO FINANCEIRO (2022-2024)")
print("=" * 80)

# Dados históricos
crescimento_data = {
    'Empresa': ['SEGA SAMMY', 'NINTENDO', 'CAPCOM'],
    'Receita 2022 (¥B)': [320.95, 1695.34, 110.05],
    'Receita 2024 (¥B)': [467.90, 1671.87, 152.41],
    'Lucro Líq. 2022 (¥B)': [37.03, 477.69, 32.55],
    'Lucro Líq. 2024 (¥B)': [33.05, 490.60, 43.37]
}

df_crescimento = pd.DataFrame(crescimento_data)

# Cálculo de CAGR (Compound Annual Growth Rate)
# CAGR = (Valor Final / Valor Inicial)^(1/anos) - 1
anos = 2  # 2022 para 2024

df_crescimento['CAGR Receita (%)'] = ((df_crescimento['Receita 2024 (¥B)'] / 
                                       df_crescimento['Receita 2022 (¥B)']) ** (1/anos) - 1) * 100

df_crescimento['CAGR Lucro (%)'] = ((df_crescimento['Lucro Líq. 2024 (¥B)'] / 
                                     df_crescimento['Lucro Líq. 2022 (¥B)']) ** (1/anos) - 1) * 100

print(df_crescimento[['Empresa', 'CAGR Receita (%)', 'CAGR Lucro (%)', 
                      'Receita 2022 (¥B)', 'Receita 2024 (¥B)']].to_string(index=False))
print()

# ============================================================================
# 3. VALUATION ABSOLUTA - SEGA SAMMY
# ============================================================================

print("=" * 80)
print("VALUATION ABSOLUTA - SEGA SAMMY HOLDINGS INC. (6460.T)")
print("=" * 80)
print()

# ============================================================================
# 3.1 TABELA 3 - FLUXOS DE CAIXA HISTÓRICOS (2022-2024)
# ============================================================================

print("TABELA 3 - FLUXOS DE CAIXA HISTÓRICOS (2022-2024)")
print("-" * 80)

fcf_historico = {
    'Ano': [2022, 2023, 2024],
    'Receita (¥B)': [320.95, 389.64, 467.90],
    'Lucro Operacional (¥B)': [32.04, 46.79, 57.87],
    'Taxa IR (%)': [2.82, 2.43, 15.03],
    'D&A (¥B)': [13.72, 12.85, 16.02],
    'CAPEX (¥B)': [11.86, 10.82, 11.12]
}

df_fcf = pd.DataFrame(fcf_historico)

# Cálculo do NOPAT (Net Operating Profit After Tax)
df_fcf['NOPAT (¥B)'] = df_fcf['Lucro Operacional (¥B)'] * (1 - df_fcf['Taxa IR (%)'] / 100)

# Cálculo do FCF (Free Cash Flow)
# FCF = NOPAT + D&A - CAPEX - Variações Capital Giro
# Simplificado: FCF = NOPAT + D&A - CAPEX (assumindo ΔCG mínimo)
df_fcf['FCF (¥B)'] = df_fcf['NOPAT (¥B)'] + df_fcf['D&A (¥B)'] - df_fcf['CAPEX (¥B)']

print(df_fcf[['Ano', 'Receita (¥B)', 'Lucro Operacional (¥B)', 
              'NOPAT (¥B)', 'D&A (¥B)', 'CAPEX (¥B)', 'FCF (¥B)']].to_string(index=False))

# Média de FCF para base de projeção
fcf_medio = df_fcf['FCF (¥B)'].mean()
print()
print(f"Média FCF (2022-2024): ¥{fcf_medio:.2f}B")
print(f"Crescimento FCF: {df_fcf.loc[0, 'FCF (¥B)']:.2f}B → {df_fcf.loc[2, 'FCF (¥B)']:.2f}B")
print(f"Variação: +{((df_fcf.loc[2, 'FCF (¥B)'] / df_fcf.loc[0, 'FCF (¥B)']) - 1) * 100:.1f}%")
print()

# ============================================================================
# 3.2 TABELA 4 - ESTRUTURA DE CAPITAL (2024)
# ============================================================================

print("TABELA 4 - ESTRUTURA DE CAPITAL - SEGA SAMMY (2024)")
print("-" * 80)

# Dados de capital
total_debt = 161.84  # ¥B
total_equity = 357.70  # ¥B
cash = 211.72  # ¥B
interest_expense = 0.76  # ¥B (dado do balanço)

# Cálculos
total_capital = total_debt + total_equity
debt_weight = total_debt / total_capital
equity_weight = total_equity / total_capital
net_debt = total_debt - cash
cost_of_debt_pre_tax = (interest_expense / total_debt) * 100
tax_rate = 0.30  # 30% IR corporativo Japão
cost_of_debt_after_tax = cost_of_debt_pre_tax * (1 - tax_rate)
interest_coverage = df_fcf.loc[2, 'Lucro Operacional (¥B)'] / interest_expense

estrutura_capital = pd.DataFrame({
    'Métrica': [
        'Total Debt (¥B)',
        'Total Equity (¥B)',
        'Total Capital (¥B)',
        'Debt Weight (%)',
        'Equity Weight (%)',
        'Cash & Equivalents (¥B)',
        'Net Debt (¥B)',
        'Cost of Debt (pré-IR) (%)',
        'Cost of Debt (após-IR) (%)',
        'Interest Coverage Ratio'
    ],
    'Valor': [
        f'{total_debt:.2f}',
        f'{total_equity:.2f}',
        f'{total_capital:.2f}',
        f'{debt_weight * 100:.2f}',
        f'{equity_weight * 100:.2f}',
        f'{cash:.2f}',
        f'{net_debt:.2f}',
        f'{cost_of_debt_pre_tax:.2f}',
        f'{cost_of_debt_after_tax:.2f}',
        f'{interest_coverage:.0f}x'
    ]
})

print(estrutura_capital.to_string(index=False))
print()

# ============================================================================
# 3.3 TABELA 5 - CÁLCULO DO WACC
# ============================================================================

print("TABELA 5 - CÁLCULO DO WACC - SEGA SAMMY")
print("-" * 80)

# Parâmetros macroeconômicos
rf = 0.01  # 1.00% - Taxa livre de risco (JGB 10 anos)
rm = 0.06  # 6.00% - Retorno mercado (Nikkei 225)
beta = 1.20  # Beta empresas games
market_risk_premium = rm - rf

# Cálculo CAPM (Capital Asset Pricing Model)
# Ke = Rf + β(Rm - Rf)
cost_of_equity = rf + beta * market_risk_premium

# Cálculo WACC
# WACC = We × Ke + Wd × Kd × (1 - Tax)
wacc = (equity_weight * cost_of_equity) + (debt_weight * cost_of_debt_after_tax / 100)

wacc_data = pd.DataFrame({
    'Componente': [
        'Risk-Free Rate (Rf)',
        'Market Return (Rm)',
        'Beta (β)',
        'Market Risk Premium (Rm-Rf)',
        'Cost of Equity (Ke) - CAPM',
        'Cost of Debt (após-IR)',
        'Debt Weight (Wd)',
        'Equity Weight (We)',
        '--- WACC ---'
    ],
    'Valor': [
        f'{rf * 100:.2f}%',
        f'{rm * 100:.2f}%',
        f'{beta:.2f}',
        f'{market_risk_premium * 100:.2f}%',
        f'{cost_of_equity * 100:.2f}%',
        f'{cost_of_debt_after_tax:.2f}%',
        f'{debt_weight * 100:.2f}%',
        f'{equity_weight * 100:.2f}%',
        f'{wacc * 100:.2f}%'
    ]
})

print(wacc_data.to_string(index=False))
print()
print("Fórmulas utilizadas:")
print(f"  Ke = Rf + β(Rm - Rf)")
print(f"  Ke = {rf*100:.2f}% + {beta:.2f} × ({rm*100:.2f}% - {rf*100:.2f}%)")
print(f"  Ke = {rf*100:.2f}% + {beta * market_risk_premium * 100:.2f}% = {cost_of_equity*100:.2f}%")
print()
print(f"  WACC = (We × Ke) + (Wd × Kd × (1-IR))")
print(f"  WACC = ({equity_weight*100:.2f}% × {cost_of_equity*100:.2f}%) + ({debt_weight*100:.2f}% × {cost_of_debt_after_tax:.2f}%)")
print(f"  WACC = {equity_weight * cost_of_equity * 100:.2f}% + {debt_weight * cost_of_debt_after_tax / 100:.2f}% = {wacc*100:.2f}%")
print()

# ============================================================================
# 3.4 TABELA 6 - PROJEÇÃO DE FLUXOS DE CAIXA (2025-2029)
# ============================================================================

print("TABELA 6 - PROJEÇÃO DE FLUXOS DE CAIXA (2025-2029)")
print("-" * 80)

# Premissas
fcf_base = fcf_medio  # Média histórica
growth_rate_explicit = 0.08  # 8% a.a. durante período explícito
anos_projecao = 5

# Criar projeção
anos_futuros = list(range(2025, 2025 + anos_projecao))
fcf_projetado = []
fator_desconto = []
valor_presente = []

for i, ano in enumerate(anos_futuros, start=1):
    # FCF(t) = FCF_base × (1 + g)^t
    fcf_t = fcf_base * ((1 + growth_rate_explicit) ** i)
    fcf_projetado.append(fcf_t)
    
    # DF(t) = 1 / (1 + WACC)^t
    df_t = 1 / ((1 + wacc) ** i)
    fator_desconto.append(df_t)
    
    # PV(t) = FCF(t) × DF(t)
    pv_t = fcf_t * df_t
    valor_presente.append(pv_t)

df_projecao = pd.DataFrame({
    'Ano': anos_futuros,
    'FCF Projetado (¥B)': fcf_projetado,
    'Fator de Desconto': fator_desconto,
    'Valor Presente (¥B)': valor_presente
})

print(df_projecao.to_string(index=False))

valor_explicito_total = sum(valor_presente)
print()
print(f"TOTAL Valor Explícito (Período 2025-2029): ¥{valor_explicito_total:.2f}B")
print()
print("Exemplo de cálculo para 2025:")
print(f"  FCF(2025) = {fcf_base:.2f}B × (1.08)^1 = ¥{fcf_projetado[0]:.2f}B")
print(f"  DF(2025) = 1 / (1.0492)^1 = {fator_desconto[0]:.4f}")
print(f"  PV(2025) = {fcf_projetado[0]:.2f}B × {fator_desconto[0]:.4f} = ¥{valor_presente[0]:.2f}B")
print()

# ============================================================================
# 3.5 TABELA 7 - VALOR TERMINAL (PERPETUIDADE)
# ============================================================================

print("TABELA 7 - VALOR TERMINAL (PERPETUIDADE)")
print("-" * 80)

# Premissas CORRIGIDAS
g_terminal = 0.01  # 1.00% - Taxa de crescimento perpétuo (economia madura Japão)
fcf_ultimo_ano = fcf_projetado[-1]  # 2029

# FCF primeiro ano da perpetuidade (2030)
fcf_perpetuidade = fcf_ultimo_ano * (1 + g_terminal)

# Valor Terminal usando Gordon Growth Model
# TV = FCF(n+1) / (WACC - g)
denominador = wacc - g_terminal
valor_terminal = fcf_perpetuidade / denominador

# Valor presente do valor terminal
# PV(TV) = TV / (1 + WACC)^n
df_terminal = 1 / ((1 + wacc) ** anos_projecao)
pv_valor_terminal = valor_terminal * df_terminal

vt_data = pd.DataFrame({
    'Componente': [
        'FCF ano 2029',
        'Taxa de crescimento (g)',
        'FCF ano 2030 (perpetuidade)',
        'WACC',
        '(WACC - g)',
        'Valor Terminal em 2029',
        'Fator de Desconto (ano 5)',
        '--- PV Valor Terminal ---'
    ],
    'Valor': [
        f'¥{fcf_ultimo_ano:.2f}B',
        f'{g_terminal * 100:.2f}%',
        f'¥{fcf_perpetuidade:.2f}B',
        f'{wacc * 100:.2f}%',
        f'{denominador * 100:.2f}%',
        f'¥{valor_terminal:.2f}B',
        f'{df_terminal:.4f}',
        f'¥{pv_valor_terminal:.2f}B'
    ]
})

print(vt_data.to_string(index=False))
print()
print("Fórmula Gordon Growth Model:")
print(f"  TV = FCF(2030) / (WACC - g)")
print(f"  TV = ¥{fcf_perpetuidade:.2f}B / ({wacc*100:.2f}% - {g_terminal*100:.2f}%)")
print(f"  TV = ¥{fcf_perpetuidade:.2f}B / {denominador*100:.2f}% = ¥{valor_terminal:.2f}B")
print()
print(f"  PV(TV) = TV / (1 + WACC)^5")
print(f"  PV(TV) = ¥{valor_terminal:.2f}B / (1.0492)^5 = ¥{pv_valor_terminal:.2f}B")
print()
print(f"✓ Validação: g ({g_terminal*100:.1f}%) < WACC ({wacc*100:.2f}%) ✓")
print()

# ============================================================================
# 3.6 TABELA 8 - VALUATION DCF FINAL
# ============================================================================

print("TABELA 8 - VALUATION DCF - SEGA SAMMY")
print("-" * 80)

# Enterprise Value
enterprise_value = valor_explicito_total + pv_valor_terminal

# Equity Value
equity_value = enterprise_value - net_debt

# Shares Outstanding
shares_outstanding = 219.27  # Milhões de ações

# Valor por ação
valor_intrinseco_por_acao = (equity_value * 1000) / shares_outstanding  # Converter B para ¥

# Percentuais
perc_explicito = (valor_explicito_total / enterprise_value) * 100
perc_terminal = (pv_valor_terminal / enterprise_value) * 100

dcf_final = pd.DataFrame({
    'Componente': [
        'Valor Explícito (2025-2029)',
        'Valor Terminal (Perpetuidade)',
        '--- Enterprise Value (EV) ---',
        '(-) Total Debt',
        '(+) Cash & Equivalents',
        '(-) Net Debt',
        '--- Equity Value ---',
        '(÷) Shares Outstanding',
        '--- Valor Intrínseco por Ação ---'
    ],
    'Valor (¥B)': [
        f'{valor_explicito_total:.2f}',
        f'{pv_valor_terminal:.2f}',
        f'{enterprise_value:.2f}',
        f'({total_debt:.2f})',
        f'{cash:.2f}',
        f'({net_debt:.2f})',
        f'{equity_value:.2f}',
        f'{shares_outstanding:.2f}M',
        f'¥{valor_intrinseco_por_acao:.2f}'
    ],
    '% do Total': [
        f'{perc_explicito:.2f}%',
        f'{perc_terminal:.2f}%',
        f'100.00%',
        '',
        '',
        '',
        '',
        '',
        ''
    ]
})

print(dcf_final.to_string(index=False))
print()
print("Cálculos detalhados:")
print(f"  EV = Valor Explícito + Valor Terminal")
print(f"  EV = ¥{valor_explicito_total:.2f}B + ¥{pv_valor_terminal:.2f}B = ¥{enterprise_value:.2f}B")
print()
print(f"  Net Debt = Total Debt - Cash")
print(f"  Net Debt = ¥{total_debt:.2f}B - ¥{cash:.2f}B = ¥{net_debt:.2f}B")
print()
print(f"  Equity Value = EV - Net Debt")
print(f"  Equity Value = ¥{enterprise_value:.2f}B - (¥{net_debt:.2f}B) = ¥{equity_value:.2f}B")
print()
print(f"  Valor por Ação = Equity Value / Shares Outstanding")
print(f"  Valor por Ação = ¥{equity_value:.2f}B × 1000 / {shares_outstanding:.2f}M = ¥{valor_intrinseco_por_acao:.2f}")
print()

# ============================================================================
# 3.7 TABELA 9 - COMPARAÇÃO VALOR INTRÍNSECO vs PREÇO DE MERCADO
# ============================================================================

print("TABELA 9 - COMPARAÇÃO VALOR INTRÍNSECO vs PREÇO DE MERCADO")
print("-" * 80)

preco_mercado = 3076.00  # ¥ (Dezembro 2024)

diferenca_absoluta = valor_intrinseco_por_acao - preco_mercado
desconto_percentual = ((preco_mercado - valor_intrinseco_por_acao) / valor_intrinseco_por_acao) * 100
upside_potencial = ((valor_intrinseco_por_acao / preco_mercado) - 1) * 100
razao_valuation = valor_intrinseco_por_acao / preco_mercado

comparacao = pd.DataFrame({
    'Métrica': [
        'Valor Intrínseco (DCF)',
        'Preço de Mercado (Dez/2024)',
        'Diferença Absoluta',
        '--- Desconto de Mercado ---',
        'Upside Potencial',
        'Razão de Valuation (VI/PM)'
    ],
    'Valor': [
        f'¥{valor_intrinseco_por_acao:.2f}',
        f'¥{preco_mercado:.2f}',
        f'¥{diferenca_absoluta:.2f}',
        f'{desconto_percentual:.2f}%',
        f'+{upside_potencial:.2f}%',
        f'{razao_valuation:.2f}x'
    ]
})

print(comparacao.to_string(index=False))
print()
print("Fórmula do Desconto:")
print(f"  Desconto % = (Preço Mercado - Valor Intrínseco) / Valor Intrínseco × 100")
print(f"  Desconto % = (¥{preco_mercado:.2f} - ¥{valor_intrinseco_por_acao:.2f}) / ¥{valor_intrinseco_por_acao:.2f} × 100")
print(f"  Desconto % = {desconto_percentual:.2f}%")
print()
print("=" * 80)
print("RECOMENDAÇÃO:COMPRA FORTE")
print("=" * 80)
print(f"A SEGA SAMMY está sendo negociada com desconto de {abs(desconto_percentual):.2f}%")
print(f"em relação ao seu valor justo estimado pelo modelo DCF.")
print(f"Potencial de valorização: +{upside_potencial:.0f}%")
print("=" * 80)
print()

print("Todos os cálculos concluídos com sucesso!")

print("\n" + "=" * 80)
print("TABELA 10 - ANÁLISE DE SENSIBILIDADE (CÓDIGO ADICIONAL)")
print("=" * 80)

# Faixas de variação conforme a Tabela 10 do Word
wacc_range = [0.0392, 0.0442, 0.0492, 0.0542, 0.0592]  # WACC: 3.92% a 5.92%
g_range = [0.005, 0.010, 0.015, 0.020, 0.025]          # g: 0.5% a 2.5%

# Função para recalcular o preço da ação
def calcular_preco_acao(novo_wacc, novo_g):
    # 1. Recalcular Valor Presente do Período Explícito com novo WACC
    pv_explicito_novo = 0
    for i, fcf in enumerate(fcf_projetado, start=1):
        pv_explicito_novo += fcf / ((1 + novo_wacc) ** i)
    
    # 2. Recalcular Valor Terminal com novo WACC e novo g
    fcf_ultimo = fcf_projetado[-1]
    fcf_perp = fcf_ultimo * (1 + novo_g)
    tv_novo = fcf_perp / (novo_wacc - novo_g)
    pv_tv_novo = tv_novo / ((1 + novo_wacc) ** anos_projecao)
    
    # 3. Recalcular Valor da Ação
    ev_novo = pv_explicito_novo + pv_tv_novo
    equity_val_novo = ev_novo - net_debt
    preco_novo = (equity_val_novo * 1000) / shares_outstanding
    return preco_novo

# Gerar a Matriz
print(f"{'WACC \\ g':<10} | {'0.50%':<10} {'1.00%':<10} {'1.50%':<10} {'2.00%':<10} {'2.50%':<10}")
print("-" * 70)

for w in wacc_range:
    row_str = f"{w*100:.2f}%     |"
    for g in g_range:
        preco = calcular_preco_acao(w, g)
        row_str += f" ¥{preco:<9.0f}"
    print(row_str)

print("-" * 70)
print("Obs: Esta tabela recalcula o PV dos fluxos e do valor terminal para cada cenário.")
