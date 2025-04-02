# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 01:05:01 2025

@author: andre_trierveiler
"""

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd


#python C:\Users\andre_trierveiler\Pesquisa_Oliver_Dash.py


# Carregar o dataframe (substitua pelo método real de carregar seu dataframe)
df = pd.read_excel('202409 Dados raw - Pesquisa W&AM associados PF Legado.xlsx')
df = df.drop(columns=['ID'])
df = df.drop(columns=['Start time'])
df = df.drop(columns=['Completion time'])
df = df.drop(columns=['Email'])
df = df.drop(columns=['Name'])
df = df.drop(columns=['Last modified time'])

# Função para calcular a distribuição de respostas
def calculate_distribution(filtered_df):
    distribution = {}
    for column in filtered_df.columns:
        # Separar múltiplas respostas e contar cada uma individualmente
        all_responses = filtered_df[column].str.split(';').explode()
        distribution[column] = all_responses.value_counts(normalize=True) * 100
    return distribution

# Inicializar o aplicativo Dash
app = dash.Dash(__name__)

# Layout do aplicativo
app.layout = html.Div([
    html.H1('Análise de Resultados da Pesquisa'),

    html.Div([
        html.H3('Filtros'),
        html.Div([
            dcc.Dropdown(
                id={'type': 'filter-dropdown', 'index': i},
                options=[{'label': val, 'value': val} for val in df[col].str.split(';').explode().unique()],
                multi=True,
                value=df[col].str.split(';').explode().unique().tolist()
            )
            for i, col in enumerate(df.columns)
        ])
    ]),

    html.Button('Recalcular', id='recalculate-button'),

    html.Div(id='distribution-output')
])

# Callback para atualizar a distribuição com base nos filtros
@app.callback(
    Output('distribution-output', 'children'),
    [Input({'type': 'filter-dropdown', 'index': dash.dependencies.ALL}, 'value'),
     Input('recalculate-button', 'n_clicks')]
)
def update_distribution(filter_values, n_clicks):
    if n_clicks is None:
        return "Por favor, selecione os filtros e clique em 'Recalcular' para ver os resultados."

    # Aplicar filtros ao dataframe
    filtered_df = df.copy()
    for i, selected_values in enumerate(filter_values):
        column = df.columns[i]
        filtered_df = filtered_df[filtered_df[column].str.split(';').explode().isin(selected_values).groupby(level=0).any()]

    # Calcular a distribuição de respostas
    distribution = calculate_distribution(filtered_df)

    # Gerar a saída para a distribuição
    output = []
    for question, dist in distribution.items():
        output.append(html.H3(question))
        output.append(dcc.Graph(
            figure={
                'data': [{'x': dist.index, 'y': dist.values, 'type': 'bar'}],
                'layout': {'title': question}
            }
        ))

    return output

# Executar o aplicativo
if __name__ == '__main__':
    app.run_server(debug=True)