# -*- coding: utf-8 -*-
"""
Created on Tue Oct  7 02:40:43 2025

@author: andre
"""

# app.py
import dash
from dash import dcc, html, dash_table
import plotly.graph_objs as go
import pandas as pd

# =====================
# Inicialização do app
# =====================
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# =====================
# Dados placeholders
# =====================
rentabilidade_mes = "100,86% do CDI"
rentabilidade_ano = "129,10% do CDI"
rentabilidade_total = "138,08% do CDI"

dados_contribuicao_mes = pd.DataFrame({
    "Classe": ["Renda Variável", "Caixa e Custos", "Câmbio", "Juros Internacional", "Crédito", "Juros Local"],
    "Retorno (%)": [1.11, 0.47, 0.41, 0.17, 0.13, -0.05]
})

dados_contribuicao_ano = pd.DataFrame({
    "Classe": ["Caixa e Custos", "Renda Variável", "Juros Internacional", "Câmbio", "Juros Local"],
    "Retorno (%)": [7.21, 2.49, 1.31, 0.73, 0.62]
})

dados_retorno_mensal = pd.DataFrame({
    "Ano": [2025, 2024, 2023],
    "Jan": [0.65, 3.46, 1.31],
    "Fev": [0.41, -0.73, 2.14],
    "Mar": [2.05, -0.25, 0.82],
    "Abr": [1.29, 2.67, 0.91],
    "Mai": [1.74, 2.54, 0.65],
    "Jun": [1.15, 1.34, -0.83],
    "Jul": [2.10, 2.09, 0.42],
    "Ago": [1.23, 0.64, 0.28],
    "Set": [0.95, 0.55, -0.22],
    "Out": [None, None, None],
    "Nov": [None, None, None],
    "Dez": [None, None, None],
    "Ano %": [10.86, 15.37, 13.18],
    "CDI %": [10.78, 12.45, 12.53]
})

# =====================
# Gráficos
# =====================

# Gráfico de contribuição no mês
fig_mes = go.Figure(go.Bar(
    x=dados_contribuicao_mes["Retorno (%)"],
    y=dados_contribuicao_mes["Classe"],
    orientation='h',
    marker_color='#3FA110'
))
fig_mes.update_layout(
    height=300,
    margin=dict(l=0, r=0, t=30, b=0),
    xaxis_title="Nominal em %",
    template="simple_white"
)

# Gráfico de contribuição no ano
fig_ano = go.Figure(go.Bar(
    x=dados_contribuicao_ano["Retorno (%)"],
    y=dados_contribuicao_ano["Classe"],
    orientation='h',
    marker_color='#FF6400'
))
fig_ano.update_layout(
    height=300,
    margin=dict(l=0, r=0, t=30, b=0),
    xaxis_title="Nominal em %",
    template="simple_white"
)

# Retorno acumulado
fig_retorno = go.Figure()
fig_retorno.add_trace(go.Scatter(
    x=pd.date_range(start='2021-01-01', periods=45, freq='ME'),
    y=[i * 1.8 for i in range(45)],
    mode='lines',
    name='Fundo',
    line=dict(color='#3FA110', width=3)
))
fig_retorno.add_trace(go.Scatter(
    x=pd.date_range(start='2021-01-01', periods=45, freq='ME'),
    y=[i * 1.3 for i in range(45)],
    mode='lines',
    name='CDI',
    line=dict(color='gray', width=2, dash='dot')
))
fig_retorno.update_layout(
    template="simple_white",
    title="Retorno Acumulado",
    height=400,
    legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
)

 # ==================================
# Gráfico Termômetro de Risco
# ==================================
nivel_risco = 6  # valor de 1 a 10 (pode ser ajustado dinamicamente depois)

fig_risco = go.Figure(go.Indicator(
    mode="gauge+number",
    value=nivel_risco,
    number={'suffix': " / 10"},
    title={'text': "Nível de Risco", 'font': {'size': 20}},
    gauge={
        'axis': {'range': [0, 10], 'tickwidth': 1, 'tickcolor': "darkgray"},
        'bar': {'color': "#323C32", 'thickness': 0.25},
        'bgcolor': "white",
        'borderwidth': 1,
        'bordercolor': "gray",
        'steps': [
            {'range': [0, 3], 'color': "#3FA110"},   # verde: baixo risco
            {'range': [3, 7], 'color': "#FFCD00"},   # amarelo: risco moderado
            {'range': [7, 10], 'color': "#E60050"}   # vermelho: alto risco
        ],
        'threshold': {
            'line': {'color': "black", 'width': 4},
            'thickness': 0.8,
            'value': nivel_risco
        }
    }
))
fig_risco.update_layout(
    margin=dict(l=20, r=20, t=40, b=0),
    height=300,
    template="simple_white"
)

# =====================
# Layout principal
# =====================
app.layout = html.Div([
    html.Div([
        html.H2("Itaú Institucional Optimus Titan MM FICFI", style={"color": "#323C32"}),
        html.P("23 de Agosto de 2025", style={"color": "gray"}),
    ], style={"textAlign": "left", "marginBottom": "20px"}),

    # Cards superiores
    html.Div([
        html.Div([
            html.H3("100,86% do CDI", style={"color": "#3FA110"}),
            html.P("Rentabilidade no mês")
        ], className="card"),

        html.Div([
            html.H3("129,10% do CDI", style={"color": "#3FA110"}),
            html.P("Rentabilidade no ano")
        ], className="card"),

        html.Div([
            html.H3("138,08% do CDI", style={"color": "#3FA110"}),
            html.P("Rentabilidade desde o início do fundo")
        ], className="card"),
    ], style={
        "display": "flex", "justifyContent": "space-around", "marginBottom": "40px"
    }),

    # Análise de Retorno
    html.Div([
        html.H4("Análise de Retorno", style={"color": "#323C32"}),
        html.Div([
            html.Div([
                html.H5("Contribuição no retorno no mês"),
                dcc.Graph(figure=fig_mes, config={'displayModeBar': False})
            ], style={"width": "48%", "display": "inline-block"}),

            html.Div([
                html.H5("Contribuição no retorno no ano"),
                dcc.Graph(figure=fig_ano, config={'displayModeBar': False})
            ], style={"width": "48%", "display": "inline-block", "float": "right"})
        ], style={"backgroundColor": "#F0F8F8", "padding": "15px", "borderRadius": "10px"})
    ], style={"marginBottom": "40px"}),

    # Retorno Acumulado
    html.Div([
        html.H4("Retorno Acumulado", style={"color": "#323C32"}),
        dcc.Graph(figure=fig_retorno, config={'displayModeBar': False})
    ], style={"marginBottom": "40px"}),

    # Retorno Mensal
    html.Div([
        html.H4("Retorno Mensal", style={"color": "#323C32"}),
        dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in dados_retorno_mensal.columns],
            data=dados_retorno_mensal.to_dict("records"),
            style_table={'overflowX': 'auto'},
            style_header={'backgroundColor': '#3FA110', 'color': 'white', 'fontWeight': 'bold'},
            style_cell={'textAlign': 'center', 'padding': '6px'},
            style_data_conditional=[
                {'if': {'row_index': 'odd'}, 'backgroundColor': '#F9F9F9'}
            ]
        )
    ]),
    
    # Termômetro de Risco
    html.Div([
        html.H4("Termômetro de Risco", style={"color": "#323C32"}),
        dcc.Graph(figure=fig_risco, config={'displayModeBar': False})
        ], style={"marginBottom": "40px"})
    
    
], style={
    "margin": "50px auto",
    "width": "90%",
    "fontFamily": "Arial"
})
    



# =====================
# Executar o app
# =====================
if __name__ == '__main__':
    app.run(debug=True)
