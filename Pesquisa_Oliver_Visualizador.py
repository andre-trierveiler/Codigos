# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 00:32:57 2025

@author: andre_trierveiler
"""

import streamlit as st
import pandas as pd


#python -m streamlit run C:\Users\andre_trierveiler\Pesquisa_Oliver_Visualizador.py --server.address localhost --server.port 8515


# Carregar o dataframe (substitua pelo método real de carregar seu dataframe)

# Função para calcular a distribuição de respostas



if 'df' not in st.session_state:
    df2 = pd.read_excel(r'\\nas03\\gestao_recursos\\Documentos\\Consultoria Oliver Wyman - 2024\\Pesquisas\\01. Pesquisa de mercado\\02. Resultados\\202407 Dados raw - Pesquisa W&AM de mercado - df.xlsx')
    #df2 = pd.read_excel(r'\\nas03\gestao_recursos\Documentos\Consultoria Oliver Wyman - 2024\Pesquisas\02. Pesquisa interna - Associados PF Legado\02. Resultados\202409 Dados raw - Pesquisa W&AM associados PF Legado.xlsx')
    
    #df2 = df2.drop(columns=['ID'])
    #df2 = df2.drop(columns=['Start time'])
    #df2 = df2.drop(columns=['Completion time'])
    #df2 = df2.drop(columns=['Email'])
    #df2 = df2.drop(columns=['Name'])
    #df2 = df2.drop(columns=['Last modified time'])
    
    # Excluir colunas com mais de 1000 respostas distintas
    df = df2.copy()
    df = df.dropna(axis=1, how='all')
    st.session_state.df = df.copy()
    st.session_state.df2 = df.copy()

  
# Inicializar o estado da sessão para armazenar os filtros
if 'filters' not in st.session_state:
    st.session_state.filters = {column: st.session_state.df[column].astype(str).str.split(';').explode().unique().tolist() for column in st.session_state.df.columns if len(st.session_state.df[column].astype(str).str.split(';').explode().unique()) <= 30}



# Barra lateral para filtros
st.sidebar.title('Filtros')
for column in st.session_state.df.columns:

    if len(st.session_state.df[column].astype(str).str.split(';').explode().unique()) <= 30:
        if f'{column}_filter' not in st.session_state:
            st.session_state[f'{column}_filter'] = st.session_state.df[column].astype(str).str.split(';').explode().unique().tolist()
        st.session_state[f'{column}_filter'] = st.sidebar.multiselect(f'Selecione {column}', st.session_state.df[column].astype(str).str.split(';').explode().unique(), default=st.session_state[f'{column}_filter'])

# Botão para recalcular a distribuição
if st.sidebar.button('Recalcular'):
    def calculate_distribution(filtered_df):
        distribution = {}
        for column in filtered_df.columns:
            # Separar múltiplas respostas e contar cada uma individualmente
            all_responses = filtered_df[column].astype(str).str.split(';').explode()
            distribution[column] = all_responses.value_counts(normalize=True) * 100
        return distribution
    
    st.title('Análise de Resultados da Pesquisa')
    # Atualizar os filtros no estado da sessão
    st.session_state.filters = {column: st.session_state[f'{column}_filter'] for column in st.session_state.df.columns if len(st.session_state.df[column].astype(str).str.split(';').explode().unique()) <= 30}
    
    # Aplicar filtros ao dataframe
    filtered_df = st.session_state.df.copy()
    for column, selected_values in st.session_state.filters.items():
        filtered_df = filtered_df[filtered_df[column].astype(str).str.split(';').explode().isin(selected_values).groupby(level=0).any()]
        #filtered_df = filtered_df[filtered_df[column].astype(str)].str.split(';').explode().isin(selected_values).groupby(level=0).any()
                                  
    # Calcular a distribuição de respostas
    distribution = calculate_distribution(filtered_df)

    # Exibir a distribuição de respostas
    st.header('Distribuição de Respostas')
    for question, dist in distribution.items():
        st.subheader(question)
        if len(dist) > 30:
            st.table(dist.reset_index().rename(columns={'index': 'Resposta', question: 'Percentual'}))
        else:
            st.bar_chart(dist)
else:
    st.write("Por favor, selecione os filtros e clique em 'Recalcular' para ver os resultados.")
   