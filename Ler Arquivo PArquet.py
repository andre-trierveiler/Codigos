# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 15:50:10 2025

@author: andre_trierveiler
"""
from enum import Enum
import pandas as pd, numpy as np, math

class path(Enum):
    DRIVE = r"\\nas03\\gestao_recursos\\Dados\\dataset\\"
    LOCAL = r"\\nas03\\gestao_recursos\\Dados\\dataset\\"


data_referencia = pd.to_datetime('2024-01-02')    
df = pd.read_parquet(path.LOCAL.value+'\\indices', filters=[('data_referencia', '>=', data_referencia),('data_referencia', '<=', data_referencia)])
df = df.rename(columns={'data_referencia': 'data_competencia', 'value': 'value', 'variable': 'indice'})
df = df.pivot(index='data_competencia', columns='indice', values='value')
df = df.pct_change()
df = df.reset_index()
df = pd.melt(df, id_vars=['data_competencia'], value_vars=df.columns, 
                    var_name='indice', value_name='variacao_diaria')
indices = df.pivot_table(columns='variable',values='value',index='data_referencia')
indices = indices[['IMA-B','IMA-S','IRF-M','IHFA','CDI']]

indices = indices.pct_change().dropna()

def rentabilidade_acumulada(df, dias=252):
    return (1 + df).rolling(window=dias).apply(lambda x: x.prod(), raw=True) - 1

# Calculando a rentabilidade acumulada para cada coluna
rentabilidade_acumulada_252 = returns.apply(rentabilidade_acumulada)
rentabilidade_acumulada_252.to_clipboard(decimal=',')
