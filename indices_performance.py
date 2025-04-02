# -*- coding: utf-8 -*-
"""
Created on Sat Nov  2 11:18:14 2024

@author: andre_trierveiler
"""


from bs4 import BeautifulSoup
import base64
import requests
import pandas as pd
import webbrowser
import warnings
import datetime
from datetime import datetime as dt
from datetime import timedelta
import numpy as np
from scipy.stats import linregress
import matplotlib.dates as mdates
import matplotlib.ticker as mtick
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objs as go
import plotly.offline as py
import plotly
#import qgrid
import itable
import pandasql as sqldf
from pandasql import sqldf
#import businessdays as bzd
from statsmodels.tsa.stattools import grangercausalitytests

def treynor_ratio(returns, benchmark_returns, media = False):
    """
    Calcula o Índice de Treynor para um investimento em relação a um benchmark.

    Argumentos:
    returns (pd.Series): Série dos retornos diários do investimento.
    benchmark_returns (pd.Series): Série dos retornos diários do benchmark.

    Retorna:
    float: Índice de Treynor do investimento em relação ao benchmark.
    """

    # Casamento de datas
    common_dates = returns.index.intersection(benchmark_returns.index)
    returns = returns.loc[common_dates]
    benchmark_returns = benchmark_returns.loc[common_dates]
    
    if media == True:  
        excess_returns = returns - benchmark_returns
        beta, _, _, _, _ = linregress(benchmark_returns, excess_returns)
    else:
        N = len(returns)
    
        excess_returns = (returns - benchmark_returns)
        mean_excess_return = (np.sum(excess_returns)+1)**(252/N)-1
        beta, _, _, _, _ = linregress(benchmark_returns, excess_returns)
        


    treynor_ratio = mean_excess_return / beta

    return treynor_ratio

def sharpe_ratio(returns, risk_free_rates, media = False):
    """
    Calcula o Índice de Sharpe para um investimento.

    Argumentos:
    returns (pd.Series): Série dos retornos diários do investimento.
    risk_free_rates (pd.Series): Série das taxas de retorno diário do ativo livre de risco.

    Retorna:
    float: Índice de Sharpe do investimento.
    """

    # Casamento de datas
    common_dates = returns.index.intersection(risk_free_rates.index)
    returns = returns.loc[common_dates]
    risk_free_rates = risk_free_rates.loc[common_dates]

    if media == True:
        excess_returns = (returns - risk_free_rates)
        mean_excess_return = np.mean(excess_returns)
        std_excess_return = np.std(excess_returns)
    else:
        N = len(returns)
    
        excess_returns = (returns - risk_free_rates)
        mean_excess_return = (np.sum(excess_returns)+1)**(252/N)-1
        std_excess_return = np.std(excess_returns) * np.sqrt(252)

    sharpe_ratio = mean_excess_return / std_excess_return

    return sharpe_ratio

def sortino_ratio(returns, benchmark_rates, media = False):
    """
    Calcula o Índice de Sharpe para um investimento.

    Argumentos:
    returns (pd.Series): Série dos retornos diários do investimento.
    risk_free_rates (pd.Series): Série das taxas de retorno diário do ativo livre de risco.

    Retorna:
    float: Índice de Sharpe do investimento.
    """

    # Casamento de datas
    common_dates = returns.index.intersection(benchmark_rates.index)
    returns = returns.loc[common_dates]
    benchmark_rates = benchmark_rates.loc[common_dates]
    
    if media == True:
        excess_returns = (returns - benchmark_rates)
        mean_excess_return = np.mean(excess_returns)
        negative_returns = np.array([ret if ret < 0 else 0 for ret in excess_returns])
        downside_deviation = np.std(negative_returns)
        #std_excess_return = np.std(excess_returns)
    else:
        N = len(returns)
        excess_returns = (returns - benchmark_rates)
        mean_excess_return = (np.sum(excess_returns)+1)**(252/N)-1
        negative_returns = np.array([ret if ret < 0 else 0 for ret in excess_returns])
        downside_deviation = np.std(negative_returns)* np.sqrt(252)


    sortino_ratio = mean_excess_return / downside_deviation 

    return sortino_ratio

def sortino_ratio_mod(returns, benchmark_rates, media = False):
    """
    Calcula o Índice de Sharpe para um investimento.

    Argumentos:
    returns (pd.Series): Série dos retornos diários do investimento.
    risk_free_rates (pd.Series): Série das taxas de retorno diário do ativo livre de risco.

    Retorna:
    float: Índice de Sharpe do investimento.
    """

    # Casamento de datas
    common_dates = returns.index.intersection(benchmark_rates.index)
    returns = returns.loc[common_dates]
    benchmark_rates = benchmark_rates.loc[common_dates]
    
    if media == True:
        excess_returns = (returns - benchmark_rates)
        mean_excess_return = np.mean(excess_returns)
        negative_returns = np.array([ret if ret < 0 else 0 for ret in excess_returns])
        downside_deviation = np.std(negative_returns)
        #std_excess_return = np.std(excess_returns)
    else:
        N = len(returns)
        excess_returns = (returns - benchmark_rates)
        mean_excess_return = (np.sum(excess_returns)+1)**(252/N)-1
        negative_returns = np.array([ret if ret < 0 else 0 for ret in excess_returns])
        downside_deviation = np.std(negative_returns)* np.sqrt(252)


    sortino_ratio = mean_excess_return / downside_deviation 

    return sortino_ratio

def tracking_error(returns, benchmark_returns):
    """
    Calcula o Tracking Error entre um investimento e um benchmark.

    Argumentos:
    returns (pd.Series): Série dos retornos diários do investimento.
    benchmark_returns (pd.Series): Série dos retornos diários do benchmark.

    Retorna:
    float: Tracking Error entre o investimento e o benchmark.
    """

    # Casamento de datas
    common_dates = returns.index.intersection(benchmark_returns.index)
    returns = returns.loc[common_dates]
    benchmark_returns = benchmark_returns.loc[common_dates]

    excess_returns = returns - benchmark_returns
    tracking_error = np.std(excess_returns)

    return tracking_error


def indice_sharpe_movel_multi(retornos_df, taxas_livres_de_risco=None, janela=0, janela_minima=1):
    """
    Calcula o Índice de Sharpe em uma janela móvel para múltiplos investimentos.

    Argumentos:
    retornos_df (pd.DataFrame): DataFrame com as datas como índice e os valores de retorno de n investimentos em cada coluna.
    taxas_livres_de_risco (pd.Series, opcional): Série das taxas de retorno diário do ativo livre de risco. Se não for fornecida, considera zero.
    janela (int): Período da janela móvel em dias.
    janela_minima (int): Número mínimo de dados para começar a calcular o Índice de Sharpe.

    Retorna:
    pd.DataFrame: DataFrame contendo o Índice de Sharpe em janela móvel para cada investimento.
    """

    # Casamento de datas
    if taxas_livres_de_risco is None:
        taxas_livres_de_risco = pd.Series(0, index=retornos_df.index)
    else:
        datas_comuns = retornos_df.index.intersection(taxas_livres_de_risco.index)
        retornos_df = retornos_df.loc[datas_comuns]
        taxas_livres_de_risco = taxas_livres_de_risco.loc[datas_comuns]

    sharpe_movel = pd.DataFrame(index=retornos_df.index)

    for col in retornos_df.columns:
        col_sharpe = []

        if janela == 0:
            # Calcular o índice global para o período completo
            retornos_excedentes = retornos_df[col] - taxas_livres_de_risco
            media_retorno_excedente = np.mean(retornos_excedentes)
            desvio_padrao_retorno_excedente = np.std(retornos_excedentes)
            indice_sharpe = media_retorno_excedente / desvio_padrao_retorno_excedente
            col_sharpe.append(indice_sharpe)
            index_dates = [retornos_df.index[-1]]
        else:
            for i in range(len(retornos_df)):
                # Ajustar a janela para os períodos iniciais
                if i < janela_minima - 1:
                    continue
                elif i < janela - 1:
                    janela_retornos = retornos_df[col].iloc[:i+1]
                    janela_taxas_livres_de_risco = taxas_livres_de_risco.iloc[:i+1]
                    retornos_excedentes = janela_retornos - janela_taxas_livres_de_risco
                    media_retorno_excedente = np.mean(retornos_excedentes)
                    desvio_padrao_retorno_excedente = np.std(retornos_excedentes)
                    indice_sharpe = media_retorno_excedente / desvio_padrao_retorno_excedente
                    col_sharpe.append(indice_sharpe)
                else:
                    janela_retornos = retornos_df[col].iloc[i-janela+1:i+1]
                    janela_taxas_livres_de_risco = taxas_livres_de_risco.iloc[i-janela+1:i+1]
                    retornos_excedentes = janela_retornos - janela_taxas_livres_de_risco
                    media_retorno_excedente = np.mean(retornos_excedentes)
                    desvio_padrao_retorno_excedente = np.std(retornos_excedentes)
                    indice_sharpe = media_retorno_excedente / desvio_padrao_retorno_excedente
                    col_sharpe.append(indice_sharpe)

            index_dates = retornos_df.index[janela_minima-1:]

        col_sharpe_df = pd.DataFrame(col_sharpe, index=index_dates, columns=[col])
        sharpe_movel = sharpe_movel.join(col_sharpe_df, how='outer')

    if janela == 0:
        return sharpe_movel.tail(1)
    
    return sharpe_movel.dropna()

def information_ratio_movel_multi(retornos_df, retornos_benchmark, janela=0, janela_minima=21):
    """
    Calcula o Índice de Informação em uma janela móvel para múltiplos investimentos.

    Argumentos:
    retornos_df (pd.DataFrame): DataFrame com as datas como índice e os valores de retorno de n investimentos em cada coluna.
    retornos_benchmark (pd.Series): Série dos retornos diários do benchmark.
    janela (int): Período da janela móvel em dias.
    janela_minima (int): Número mínimo de dados para começar a calcular o Índice de Informação.

    Retorna:
    pd.DataFrame: DataFrame contendo o Índice de Informação em janela móvel para cada investimento.
    """

    # Casamento de datas
    datas_comuns = retornos_df.index.intersection(retornos_benchmark.index)
    retornos_df = retornos_df.loc[datas_comuns]
    retornos_benchmark = retornos_benchmark.loc[datas_comuns]

    informacao_movel = pd.DataFrame(index=retornos_df.index)

    for col in retornos_df.columns:
        col_informacao = []

        if janela == 0:
            # Calcular o índice global para o período completo
            retornos_excedentes = retornos_df[col] - retornos_benchmark
            media_retorno_excedente = np.mean(retornos_excedentes)
            desvio_padrao_retorno_excedente = np.std(retornos_excedentes)
            indice_informacao = media_retorno_excedente / desvio_padrao_retorno_excedente
            col_informacao.append(indice_informacao)
            index_dates = [retornos_df.index[-1]]
        else:
            for i in range(len(retornos_df)):
                # Ajustar a janela para os períodos iniciais
                if i < janela_minima - 1:
                    continue
                elif i < janela - 1:
                    janela_retornos = retornos_df[col].iloc[:i+1]
                    janela_retornos_benchmark = retornos_benchmark.iloc[:i+1]
                    retornos_excedentes = janela_retornos - janela_retornos_benchmark
                    media_retorno_excedente = np.mean(retornos_excedentes)
                    desvio_padrao_retorno_excedente = np.std(retornos_excedentes)
                    indice_informacao = media_retorno_excedente / desvio_padrao_retorno_excedente
                    col_informacao.append(indice_informacao)
                else:
                    janela_retornos = retornos_df[col].iloc[i-janela+1:i+1]
                    janela_retornos_benchmark = retornos_benchmark.iloc[i-janela+1:i+1]
                    retornos_excedentes = janela_retornos - janela_retornos_benchmark
                    media_retorno_excedente = np.mean(retornos_excedentes)
                    desvio_padrao_retorno_excedente = np.std(retornos_excedentes)
                    indice_informacao = media_retorno_excedente / desvio_padrao_retorno_excedente
                    col_informacao.append(indice_informacao)

            index_dates = retornos_df.index[janela_minima-1:]

        col_informacao_df = pd.DataFrame(col_informacao, index=index_dates, columns=[col])
        informacao_movel = informacao_movel.join(col_informacao_df, how='outer')

    if janela == 0:
        return informacao_movel.tail(1)
    
    return informacao_movel.dropna()

def alpha_movel_multi(retornos_df, retornos_benchmark, taxas_livres_de_risco=None, janela=0, janela_minima=1):
    """
    Calcula o Alfa em uma janela móvel para múltiplos investimentos.

    Argumentos:
    retornos_df (pd.DataFrame): DataFrame com as datas como índice e os valores de retorno de n investimentos em cada coluna.
    retornos_benchmark (pd.Series): Série dos retornos diários do benchmark.
    taxas_livres_de_risco (pd.Series, opcional): Série das taxas de retorno diário do ativo livre de risco. Se não for fornecida, considera zero.
    janela (int, opcional): Período da janela móvel em dias. Se 0 ou 1, calcula o Alfa para todo o período.
                             Se maior que 1, calcula o Alfa em janela móvel. Padrão é 0.
    janela_minima (int): Número mínimo de dados para começar a calcular o Alfa.

    Retorna:
    pd.DataFrame: DataFrame contendo o Alfa em janela móvel para cada investimento.
    """

    # Casamento de datas
    if taxas_livres_de_risco is None:
        taxas_livres_de_risco = pd.Series(0, index=retornos_df.index)
    else:
        datas_comuns = retornos_df.index.intersection(taxas_livres_de_risco.index)
        retornos_df = retornos_df.loc[datas_comuns]
        taxas_livres_de_risco = taxas_livres_de_risco.loc[datas_comuns]

    datas_comuns = retornos_df.index.intersection(retornos_benchmark.index)
    retornos_df = retornos_df.loc[datas_comuns]
    retornos_benchmark = retornos_benchmark.loc[datas_comuns]
    taxas_livres_de_risco = taxas_livres_de_risco.loc[datas_comuns]

    alfa_movel = pd.DataFrame(index=retornos_df.index)

    for col in retornos_df.columns:
        col_alfa = []

        if janela == 0:
            # Calcular o índice global para o período completo
            excess_returns = retornos_df[col] - taxas_livres_de_risco - retornos_benchmark
            beta, alfa, _, _, _ = linregress(retornos_benchmark, excess_returns)
            col_alfa.append(alfa)
            index_dates = [retornos_df.index[-1]]
        else:
            for i in range(len(retornos_df)):
                # Ajustar a janela para os períodos iniciais
                if i < janela_minima - 1:
                    continue
                elif i < janela - 1:
                    janela_retornos = retornos_df[col].iloc[:i+1]
                    janela_retornos_benchmark = retornos_benchmark.iloc[:i+1]
                    janela_taxas_livres_de_risco = taxas_livres_de_risco.iloc[:i+1]
                    excess_returns = janela_retornos - janela_taxas_livres_de_risco - janela_retornos_benchmark
                    beta, alfa, _, _, _ = linregress(janela_retornos_benchmark, excess_returns)
                    col_alfa.append(alfa)
                else:
                    janela_retornos = retornos_df[col].iloc[i-janela+1:i+1]
                    janela_retornos_benchmark = retornos_benchmark.iloc[i-janela+1:i+1]
                    janela_taxas_livres_de_risco = taxas_livres_de_risco.iloc[i-janela+1:i+1]
                    excess_returns = janela_retornos - janela_taxas_livres_de_risco - janela_retornos_benchmark
                    beta, alfa, _, _, _ = linregress(janela_retornos_benchmark, excess_returns)
                    col_alfa.append(alfa)

            index_dates = retornos_df.index[janela_minima-1:]

        col_alfa_df = pd.DataFrame(col_alfa, index=index_dates, columns=[col])
        alfa_movel = alfa_movel.join(col_alfa_df, how='outer')

    if janela == 0:
        return alfa_movel.tail(1)
    
    return alfa_movel.dropna()

def beta_movel_multi(retornos_df, retornos_benchmark, janela=0, janela_minima=1):
    """
    Calcula o Beta em uma janela móvel para múltiplos investimentos.

    Argumentos:
    retornos_df (pd.DataFrame): DataFrame com as datas como índice e os valores de retorno de n investimentos em cada coluna.
    retornos_benchmark (pd.Series): Série dos retornos diários do benchmark.
    janela (int, opcional): Período da janela móvel em dias. Se 0 ou 1, calcula o Beta para todo o período.
                             Se maior que 1, calcula o Beta em janela móvel. Padrão é 0.
    janela_minima (int): Número mínimo de dados para começar a calcular o Beta.

    Retorna:
    pd.DataFrame: DataFrame contendo o Beta em janela móvel para cada investimento.
    """

    # Casamento de datas
    datas_comuns = retornos_df.index.intersection(retornos_benchmark.index)
    retornos_df = retornos_df.loc[datas_comuns]
    retornos_benchmark = retornos_benchmark.loc[datas_comuns]

    beta_movel = pd.DataFrame(index=retornos_df.index)

    for col in retornos_df.columns:
        col_beta = []

        if janela == 0:
            # Calcular o índice global para o período completo
            beta, _, _, _, _ = linregress(retornos_benchmark, retornos_df[col])
            col_beta.append(beta)
            index_dates = [retornos_df.index[-1]]
        else:
            for i in range(len(retornos_df)):
                # Ajustar a janela para os períodos iniciais
                if i < janela_minima - 1:
                    continue
                elif i < janela - 1:
                    janela_retornos = retornos_df[col].iloc[:i+1]
                    janela_retornos_benchmark = retornos_benchmark.iloc[:i+1]
                    beta, _, _, _, _ = linregress(janela_retornos_benchmark, janela_retornos)
                    col_beta.append(beta)
                else:
                    janela_retornos = retornos_df[col].iloc[i-janela+1:i+1]
                    janela_retornos_benchmark = retornos_benchmark.iloc[i-janela+1:i+1]
                    beta, _, _, _, _ = linregress(janela_retornos_benchmark, janela_retornos)
                    col_beta.append(beta)

            index_dates = retornos_df.index[janela_minima-1:]

        col_beta_df = pd.DataFrame(col_beta, index=index_dates, columns=[col])
        beta_movel = beta_movel.join(col_beta_df, how='outer')

    if janela == 0:
        return beta_movel.tail(1)
    
    return beta_movel.dropna()

def tracking_error_movel_multi(retornos_df, retornos_benchmark, janela=0, janela_minima=1):
    """
    Calcula o Tracking Error em uma janela móvel para múltiplos investimentos.

    Argumentos:
    retornos_df (pd.DataFrame): DataFrame com as datas como índice e os valores de retorno de n investimentos em cada coluna.
    retornos_benchmark (pd.Series): Série dos retornos diários do benchmark.
    janela (int, opcional): Período da janela móvel em dias. Se 0 ou 1, calcula o Tracking Error para todo o período.
                             Se maior que 1, calcula o Tracking Error em janela móvel. Padrão é 0.
    janela_minima (int): Número mínimo de dados para começar a calcular o Tracking Error.

    Retorna:
    pd.DataFrame: DataFrame contendo o Tracking Error em janela móvel para cada investimento.
    """

    # Casamento de datas
    datas_comuns = retornos_df.index.intersection(retornos_benchmark.index)
    retornos_df = retornos_df.loc[datas_comuns]
    retornos_benchmark = retornos_benchmark.loc[datas_comuns]

    tracking_error_movel = pd.DataFrame(index=retornos_df.index)

    for col in retornos_df.columns:
        col_tracking_error = []

        if janela == 0:
            # Calcular o índice global para o período completo
            tracking_error_series = np.std(retornos_df[col] - retornos_benchmark)
            col_tracking_error.append(tracking_error_series)
            index_dates = [retornos_df.index[-1]]
        else:
            for i in range(len(retornos_df)):
                # Ajustar a janela para os períodos iniciais
                if i < janela_minima - 1:
                    continue
                elif i < janela - 1:
                    janela_retornos = retornos_df[col].iloc[:i+1]
                    janela_retornos_benchmark = retornos_benchmark.iloc[:i+1]
                    tracking_error_series = np.std(janela_retornos - janela_retornos_benchmark)
                    col_tracking_error.append(tracking_error_series)
                else:
                    janela_retornos = retornos_df[col].iloc[i-janela+1:i+1]
                    janela_retornos_benchmark = retornos_benchmark.iloc[i-janela+1:i+1]
                    tracking_error_series = np.std(janela_retornos - janela_retornos_benchmark)
                    col_tracking_error.append(tracking_error_series)

            index_dates = retornos_df.index[janela_minima-1:]

        col_tracking_error_df = pd.DataFrame(col_tracking_error, index=index_dates, columns=[col])
        tracking_error_movel = tracking_error_movel.join(col_tracking_error_df, how='outer')

    if janela == 0:
        return tracking_error_movel.tail(1)
    
    return tracking_error_movel.dropna()

def treynor_ratio_movel_multi(retornos_df, retornos_benchmark, taxas_livres_de_risco=None, janela=0, janela_minima=1):
 
    """
    Calcula o Índice de Treynor em uma janela móvel para múltiplos investimentos.

    Argumentos:
    retornos_df (pd.DataFrame): DataFrame com as datas como índice e os valores de retorno de n investimentos em cada coluna.
    retornos_benchmark (pd.Series): Série dos retornos diários do benchmark.
    taxas_livres_de_risco (pd.Series, opcional): Série das taxas de retorno diário do ativo livre de risco. Se não for fornecida, considera zero.
    janela (int, opcional): Período da janela móvel em dias. Se 0 ou 1, calcula o Índice de Treynor para todo o período.
                             Se maior que 1, calcula o Índice de Treynor em janela móvel. Padrão é 0.
    janela_minima (int): Número mínimo de dados para começar a calcular o Índice de Treynor.

    Retorna:
    pd.DataFrame: DataFrame contendo o Índice de Treynor em janela móvel para cada investimento.
    """

    # Casamento de datas
    if taxas_livres_de_risco is None:
        taxas_livres_de_risco = pd.Series(0, index=retornos_df.index)
    else:
        datas_comuns = retornos_df.index.intersection(taxas_livres_de_risco.index)
        retornos_df = retornos_df.loc[datas_comuns]
        taxas_livres_de_risco = taxas_livres_de_risco.loc[datas_comuns]

    datas_comuns = retornos_df.index.intersection(retornos_benchmark.index)
    retornos_df = retornos_df.loc[datas_comuns]
    retornos_benchmark = retornos_benchmark.loc[datas_comuns]
    taxas_livres_de_risco = taxas_livres_de_risco.loc[datas_comuns]

    treynor_movel = pd.DataFrame(index=retornos_df.index)

    for col in retornos_df.columns:
        col_treynor = []

        if janela == 0:
            # Calcular o índice global para o período completo
            excess_returns = retornos_df[col] - taxas_livres_de_risco
            excess_returns_mean = excess_returns.mean()
            beta, _, _, _, _ = linregress(retornos_benchmark, retornos_df[col])
            treynor_ratio_series = excess_returns_mean / beta
            col_treynor.append(treynor_ratio_series)
            index_dates = [retornos_df.index[-1]]
        else:
            for i in range(len(retornos_df)):
                # Ajustar a janela para os períodos iniciais
                if i < janela_minima - 1:
                    continue
                elif i < janela - 1:
                    janela_retornos = retornos_df[col].iloc[:i+1]
                    janela_retornos_benchmark = retornos_benchmark.iloc[:i+1]
                    janela_taxas_livres_de_risco = taxas_livres_de_risco.iloc[:i+1]
                    excess_returns = janela_retornos - janela_taxas_livres_de_risco
                    excess_returns_mean = excess_returns.mean()
                    beta, _, _, _, _ = linregress(janela_retornos_benchmark, janela_retornos)
                    treynor_ratio_series = excess_returns_mean / beta
                    col_treynor.append(treynor_ratio_series)
                else:
                    janela_retornos = retornos_df[col].iloc[i-janela+1:i+1]
                    janela_retornos_benchmark = retornos_benchmark.iloc[i-janela+1:i+1]
                    janela_taxas_livres_de_risco = taxas_livres_de_risco.iloc[i-janela+1:i+1]
                    excess_returns = janela_retornos - janela_taxas_livres_de_risco
                    excess_returns_mean = excess_returns.mean()
                    beta, _, _, _, _ = linregress(janela_retornos_benchmark, janela_retornos)
                    treynor_ratio_series = excess_returns_mean / beta
                    col_treynor.append(treynor_ratio_series)

            index_dates = retornos_df.index[janela_minima-1:]

        col_treynor_df = pd.DataFrame(col_treynor, index=index_dates, columns=[col])
        treynor_movel = treynor_movel.join(col_treynor_df, how='outer')

    if janela == 0:
        return treynor_movel.tail(1)
    
    return treynor_movel.dropna()


def kappa_rolling_mult(retornos_df, retornos_benchmark, p=1, taxas_livres_de_risco=None, janela=0, janela_minima=1):
    """
    Calcula o índice de Kappa de ordem p para um DataFrame de retornos em comparação com um benchmark.

    Argumentos:
    retornos_df (pd.DataFrame): DataFrame com as datas como índice e os valores de retorno de n investimentos em cada coluna.
    retornos_benchmark (pd.Series): Série dos retornos diários do benchmark.
    p (int, opcional): Ordem do índice de Kappa. Padrão é 1.
    taxas_livres_de_risco (pd.Series, opcional): Série das taxas de retorno diário do ativo livre de risco. Se não for fornecida, considera zero.
    janela (int, opcional): Tamanho da janela móvel em dias. Se 0 ou 1, calcula o índice de Kappa para todo o período.
                             Se maior que 1, calcula o índice de Kappa em janela móvel. Padrão é 0.
    janela_minima (int): Número mínimo de dados para começar a calcular o índice de Kappa.

    Retorna:
    pd.DataFrame: DataFrame contendo os valores do índice de Kappa para cada investimento.
    """

    # Casamento de datas
    if taxas_livres_de_risco is None:
        taxas_livres_de_risco = pd.Series(0, index=retornos_df.index)
    else:
        datas_comuns = retornos_df.index.intersection(taxas_livres_de_risco.index)
        retornos_df = retornos_df.loc[datas_comuns]
        taxas_livres_de_risco = taxas_livres_de_risco.loc[datas_comuns]

    datas_comuns = retornos_df.index.intersection(retornos_benchmark.index)
    retornos_df = retornos_df.loc[datas_comuns]
    retornos_benchmark = retornos_benchmark.loc[datas_comuns]
    taxas_livres_de_risco = taxas_livres_de_risco.loc[datas_comuns]

    kappa_movel = pd.DataFrame(index=retornos_df.index)

    for col in retornos_df.columns:
        col_kappa = []

        if janela == 0:
            # Calcular o índice global para o período completo
            excess_returns = retornos_df[col] - taxas_livres_de_risco
            mean_excess_return = excess_returns.mean()
            l_moment_p = np.mean(np.abs(excess_returns) ** p) ** (1 / p)
            kappa = mean_excess_return / l_moment_p
            col_kappa.append(kappa)
            index_dates = [retornos_df.index[-1]]
        else:
            for i in range(len(retornos_df)):
                # Ajustar a janela para os períodos iniciais
                if i < janela_minima - 1:
                    continue
                elif i < janela - 1:
                    janela_retornos = retornos_df[col].iloc[:i+1]
                    janela_retornos_benchmark = retornos_benchmark.iloc[:i+1]
                    janela_taxas_livres_de_risco = taxas_livres_de_risco.iloc[:i+1]
                    excess_returns = janela_retornos - janela_taxas_livres_de_risco
                    mean_excess_return = excess_returns.mean()
                    l_moment_p = np.mean(np.abs(excess_returns) ** p) ** (1 / p)
                    kappa = mean_excess_return / l_moment_p
                    col_kappa.append(kappa)
                else:
                    janela_retornos = retornos_df[col].iloc[i-janela+1:i+1]
                    janela_retornos_benchmark = retornos_benchmark.iloc[i-janela+1:i+1]
                    janela_taxas_livres_de_risco = taxas_livres_de_risco.iloc[i-janela+1:i+1]
                    excess_returns = janela_retornos - janela_taxas_livres_de_risco
                    mean_excess_return = excess_returns.mean()
                    l_moment_p = np.mean(np.abs(excess_returns) ** p) ** (1 / p)
                    kappa = mean_excess_return / l_moment_p
                    col_kappa.append(kappa)

            index_dates = retornos_df.index[janela_minima-1:]

        col_kappa_df = pd.DataFrame(col_kappa, index=index_dates, columns=[col])
        kappa_movel = kappa_movel.join(col_kappa_df, how='outer')

    if janela == 0:
        return kappa_movel.tail(1)
    
    return kappa_movel.dropna()

def volatilidade_rolling_multi(retornos_df, retornos_benchmark, janela=0, janela_minima=1, agregador_retorno=1):
    """
    Calcula a volatilidade dos ativos em relação ao benchmark em uma janela móvel para múltiplos investimentos.

    Argumentos:
    retornos_df (pd.DataFrame): DataFrame com as datas como índice e os valores de retorno de n investimentos em cada coluna.
    retornos_benchmark (pd.Series): Série dos retornos diários do benchmark.
    janela (int, opcional): Período da janela móvel em dias. Se 0 ou 1, calcula a volatilidade para todo o período.
                             Se maior que 1, calcula a volatilidade em janela móvel. Padrão é 0.
    janela_minima (int): Número mínimo de dados para começar a calcular a volatilidade.
    agregador_retorno (int, opcional): Número de dias para agregar os retornos antes de calcular a volatilidade. Padrão é 1 (retornos diários).

    Retorna:
    pd.DataFrame: DataFrame contendo a volatilidade em janela móvel para cada investimento.
    """

    # Casamento de datas
    datas_comuns = retornos_df.index.intersection(retornos_benchmark.index)
    retornos_df = retornos_df.loc[datas_comuns]
    retornos_benchmark = retornos_benchmark.loc[datas_comuns]

    # Agregar retornos se necessário
    if agregador_retorno > 1:
        retornos_df = retornos_df.rolling(agregador_retorno).sum().dropna()/agregador_retorno
        retornos_benchmark = retornos_benchmark.rolling(agregador_retorno).sum().dropna()/agregador_retorno

    volatilidade_movel = pd.DataFrame(index=retornos_df.index)

    for col in retornos_df.columns:
        col_volatilidade = []

        if janela == 0:
            # Calcular a volatilidade global para o período completo
            volatilidade = np.std(retornos_df[col] - retornos_benchmark)
            col_volatilidade.append(volatilidade)
            index_dates = [retornos_df.index[-1]]
        else:
            for i in range(len(retornos_df)):
                # Ajustar a janela para os períodos iniciais
                if i < janela_minima - 1:
                    continue
                elif i < janela - 1:
                    janela_retornos = retornos_df[col].iloc[:i+1]
                    janela_retornos_benchmark = retornos_benchmark.iloc[:i+1]
                    volatilidade = np.std(janela_retornos - janela_retornos_benchmark)
                    col_volatilidade.append(volatilidade)
                else:
                    janela_retornos = retornos_df[col].iloc[i-janela+1:i+1]
                    janela_retornos_benchmark = retornos_benchmark.iloc[i-janela+1:i+1]
                    volatilidade = np.std(janela_retornos - janela_retornos_benchmark)
                    col_volatilidade.append(volatilidade)

            index_dates = retornos_df.index[janela_minima-1:]

        col_volatilidade_df = pd.DataFrame(col_volatilidade, index=index_dates, columns=[col])
        volatilidade_movel = volatilidade_movel.join(col_volatilidade_df, how='outer')

    if janela == 0:
        return volatilidade_movel.tail(1)
    
    return volatilidade_movel.dropna()


def volatilidade_rolling_multi_compound(retornos_df, retornos_benchmark, janela=0, janela_minima=1, agregador_retorno=1):
    """
    Calcula a volatilidade dos ativos em relação ao benchmark em uma janela móvel para múltiplos investimentos.

    Argumentos:
    retornos_df (pd.DataFrame): DataFrame com as datas como índice e os valores de retorno de n investimentos em cada coluna.
    retornos_benchmark (pd.Series): Série dos retornos diários do benchmark.
    janela (int, opcional): Período da janela móvel em dias. Se 0 ou 1, calcula a volatilidade para todo o período.
                             Se maior que 1, calcula a volatilidade em janela móvel. Padrão é 0.
    janela_minima (int): Número mínimo de dados para começar a calcular a volatilidade.
    agregador_retorno (int, opcional): Número de dias para agregar os retornos antes de calcular a volatilidade. Padrão é 1 (retornos diários).

    Retorna:
    pd.DataFrame: DataFrame contendo a volatilidade em janela móvel para cada investimento.
    """

    # Casamento de datas
    datas_comuns = retornos_df.index.intersection(retornos_benchmark.index)
    retornos_df = retornos_df.loc[datas_comuns]
    retornos_benchmark = retornos_benchmark.loc[datas_comuns]

    # Função para agregar retornos
    def agregar_retorno(x):
        return (x + 1).prod() - 1

    volatilidade_movel = pd.DataFrame(index=retornos_df.index)
    janela_minima = max(janela_minima, agregador_retorno)
    
    for col in retornos_df.columns:
        col_volatilidade = []

        if janela == 0:
            # Calcular a volatilidade global para o período completo
            volatilidade = np.std(retornos_df[col] - retornos_benchmark)
            col_volatilidade.append(volatilidade)
            index_dates = [retornos_df.index[-1]]
        else:
            for i in range(len(retornos_df)):
                # Ajustar a janela para os períodos iniciais
                if i < janela_minima - 1:
                    continue
                elif i < janela - 1:
                    janela_retornos = retornos_df[col].iloc[:i+1].rolling(agregador_retorno).apply(agregar_retorno).dropna()
                    janela_retornos_benchmark = retornos_benchmark.iloc[:i+1].rolling(agregador_retorno).apply(agregar_retorno).dropna()
                    if len(janela_retornos) > 0 and len(janela_retornos_benchmark) > 0:
                        volatilidade = np.std(janela_retornos - janela_retornos_benchmark)
                        col_volatilidade.append(volatilidade)
                else:
                    janela_retornos = retornos_df[col].iloc[i-janela+1:i+1].rolling(agregador_retorno).apply(agregar_retorno).dropna()
                    janela_retornos_benchmark = retornos_benchmark.iloc[i-janela+1:i+1].rolling(agregador_retorno).apply(agregar_retorno).dropna()
                    if len(janela_retornos) > 0 and len(janela_retornos_benchmark) > 0:
                        volatilidade = np.std(janela_retornos - janela_retornos_benchmark)
                        col_volatilidade.append(volatilidade)
          
            index_dates = retornos_df.index[janela_minima-1:]

        col_volatilidade_df = pd.DataFrame(col_volatilidade, index=index_dates, columns=[col])
        volatilidade_movel = volatilidade_movel.join(col_volatilidade_df, how='outer')
    
    if janela == 0:
        return volatilidade_movel.tail(1)
    index_dates = retornos_df.index[janela_minima-1:]
    return volatilidade_movel.dropna()
    

def correlacao_rolling_multi(retornos_df, retornos_benchmark, janela=0, janela_minima=1):
    """
    Calcula a correlação entre os retornos dos ativos e os retornos do benchmark em uma janela móvel para múltiplos investimentos.

    Argumentos:
    retornos_df (pd.DataFrame): DataFrame com as datas como índice e os valores de retorno de n investimentos em cada coluna.
    retornos_benchmark (pd.Series): Série dos retornos diários do benchmark.
    janela (int, opcional): Período da janela móvel em dias. Se 0 ou 1, calcula a correlação para todo o período.
                             Se maior que 1, calcula a correlação em janela móvel. Padrão é 0.
    janela_minima (int): Número mínimo de dados para começar a calcular a correlação.

    Retorna:
    pd.DataFrame: DataFrame contendo a correlação em janela móvel para cada investimento.
    """

    # Casamento de datas
    datas_comuns = retornos_df.index.intersection(retornos_benchmark.index)
    retornos_df = retornos_df.loc[datas_comuns]
    retornos_benchmark = retornos_benchmark.loc[datas_comuns]

    correlacao_movel = pd.DataFrame(index=retornos_df.index)

    for col in retornos_df.columns:
        col_correlacao = []

        if janela == 0:
            # Calcular a correlação global para o período completo
            correlacao = retornos_df[col].corr(retornos_benchmark)
            col_correlacao.append(correlacao)
            index_dates = [retornos_df.index[-1]]
        else:
            for i in range(len(retornos_df)):
                # Ajustar a janela para os períodos iniciais
                if i < janela_minima - 1:
                    continue
                elif i < janela - 1:
                    janela_retornos = retornos_df[col].iloc[:i+1]
                    janela_retornos_benchmark = retornos_benchmark.iloc[:i+1]
                    correlacao = janela_retornos.corr(janela_retornos_benchmark)
                    col_correlacao.append(correlacao)
                else:
                    janela_retornos = retornos_df[col].iloc[i-janela+1:i+1]
                    janela_retornos_benchmark = retornos_benchmark.iloc[i-janela+1:i+1]
                    correlacao = janela_retornos.corr(janela_retornos_benchmark)
                    col_correlacao.append(correlacao)

            index_dates = retornos_df.index[janela_minima-1:]

        col_correlacao_df = pd.DataFrame(col_correlacao, index=index_dates, columns=[col])
        correlacao_movel = correlacao_movel.join(col_correlacao_df, how='outer')

    if janela == 0:
        return correlacao_movel.tail(1)
    
    return correlacao_movel.dropna()

def correlacao_media_rolling_multi(retornos_df, janela=0, janela_minima=1):
    """
    Calcula a correlação do retorno de cada um dos ativos contra o retorno médio dos demais ativos em uma janela móvel para múltiplos investimentos.

    Argumentos:
    retornos_df (pd.DataFrame): DataFrame com as datas como índice e os valores de retorno de n investimentos em cada coluna.
    janela (int, opcional): Período da janela móvel em dias. Se 0 ou 1, calcula a correlação para todo o período.
                             Se maior que 1, calcula a correlação em janela móvel. Padrão é 0.
    janela_minima (int): Número mínimo de dados para começar a calcular a correlação.

    Retorna:
    pd.DataFrame: DataFrame contendo a correlação em janela móvel para cada investimento.
    """

    correlacao_movel = pd.DataFrame(index=retornos_df.index)

    for col in retornos_df.columns:
        col_correlacao = []

        if janela == 0:
            # Calcular a correlação global para o período completo
            media_retorno_outros = retornos_df.drop(columns=[col]).mean(axis=1)
            correlacao = retornos_df[col].corr(media_retorno_outros)
            col_correlacao.append(correlacao)
            index_dates = [retornos_df.index[-1]]
        else:
            for i in range(len(retornos_df)):
                # Ajustar a janela para os períodos iniciais
                if i < janela_minima - 1:
                    continue
                elif i < janela - 1:
                    janela_retornos = retornos_df.iloc[:i+1]
                    media_retorno_outros = janela_retornos.drop(columns=[col]).mean(axis=1)
                    correlacao = janela_retornos[col].corr(media_retorno_outros)
                    col_correlacao.append(correlacao)
                else:
                    janela_retornos = retornos_df.iloc[i-janela+1:i+1]
                    media_retorno_outros = janela_retornos.drop(columns=[col]).mean(axis=1)
                    correlacao = janela_retornos[col].corr(media_retorno_outros)
                    col_correlacao.append(correlacao)

            index_dates = retornos_df.index[janela_minima-1:]

        col_correlacao_df = pd.DataFrame(col_correlacao, index=index_dates, columns=[col])
        correlacao_movel = correlacao_movel.join(col_correlacao_df, how='outer')

    if janela == 0:
        return correlacao_movel.tail(1)
    
    return correlacao_movel.dropna()

def calculate_var(retornos_df, confidence_level=0.95, janela=0, janela_minima=1):
    """
    Calcula o Value at Risk (VaR) para um DataFrame de retornos em uma janela móvel.

    Argumentos:
    retornos_df (pd.DataFrame): DataFrame com as datas como índice e os valores de retorno de n investimentos em cada coluna.
    confidence_level (float, opcional): Nível de confiança para o cálculo do VaR. Padrão é 0.95 (95%).
    janela (int, opcional): Tamanho da janela móvel em dias. Se 0 ou 1, calcula o VaR para todo o período.
                             Se maior que 1, calcula o VaR em janela móvel. Padrão é 0.
    janela_minima (int): Número mínimo de dados para começar a calcular o VaR.

    Retorna:
    pd.DataFrame: DataFrame contendo os valores do VaR para cada investimento.
    """

    var_movel = pd.DataFrame(index=retornos_df.index)
    z_score = np.abs(np.percentile(np.random.normal(0, 1, 100000), (1 - confidence_level) * 100))

    for col in retornos_df.columns:
        col_var = []

        if janela == 0:
            # Calcular o VaR global para o período completo
            mean_return = retornos_df[col].mean()
            std_return = retornos_df[col].std()
            var = -(mean_return - z_score * std_return)
            col_var.append(var)
            index_dates = [retornos_df.index[-1]]
        else:
            for i in range(len(retornos_df)):
                # Ajustar a janela para os períodos iniciais
                if i < janela_minima - 1:
                    continue
                elif i < janela - 1:
                    janela_retornos = retornos_df[col].iloc[:i+1]
                    mean_return = janela_retornos.mean()
                    std_return = janela_retornos.std()
                    var = -(mean_return - z_score * std_return)
                    col_var.append(var)
                else:
                    janela_retornos = retornos_df[col].iloc[i-janela+1:i+1]
                    mean_return = janela_retornos.mean()
                    std_return = janela_retornos.std()
                    var = -(mean_return - z_score * std_return)
                    col_var.append(var)

            index_dates = retornos_df.index[janela_minima-1:]

        col_var_df = pd.DataFrame(col_var, index=index_dates, columns=[col])
        var_movel = var_movel.join(col_var_df, how='outer')

    if janela == 0:
        return var_movel.tail(1)
    
    return var_movel.dropna().applymap(lambda x: -abs(x))

def omega_index_rolling(returns_df, benchmark_returns=None, risk_free_rate=None, threshold=0, window=0, min_periods=1):
    """
    Calcula o Índice de Omega em uma janela móvel para cada ativo.

    Argumentos:
    returns_df (pd.DataFrame): DataFrame com as datas como índice e os valores de retorno de n investimentos em cada coluna.
    benchmark_returns (pd.Series, opcional): Série dos retornos diários do benchmark. Se None, usa retornos absolutos.
    risk_free_rate (pd.Series, opcional): Série da taxa livre de risco diária.
    threshold (float): Retorno limite para calcular o Índice de Omega. Padrão é 0.
    window (int): Período da janela móvel em dias. Se 0, calcula o Índice Omega para todo o período.
    min_periods (int): Número mínimo de dados necessários para começar o cálculo.

    Retorna:
    pd.DataFrame: DataFrame contendo o Índice de Omega em janela móvel para cada ativo.
    """
    omega_index_df = pd.DataFrame(index=returns_df.index)

    for col in returns_df.columns:
        rolling_omega = returns_df[col].rolling(window=window, min_periods=min_periods).apply(
            lambda x: (x[x > threshold].sum() / -x[x < threshold].sum()) if -x[x < threshold].sum() != 0 else np.inf,
            raw=True
        )
        omega_index_df[col] = rolling_omega

    return omega_index_df

def calmar_index_rolling(returns_df, benchmark_returns=None, risk_free_rate=None, window=0, min_periods=1):
    """
    Calcula o Índice de Calmar em uma janela móvel para cada ativo.

    Argumentos:
    returns_df (pd.DataFrame): DataFrame com as datas como índice e os valores de retorno de n investimentos em cada coluna.
    benchmark_returns (pd.Series, opcional): Série dos retornos diários do benchmark. Se None, usa retornos absolutos.
    risk_free_rate (pd.Series, opcional): Série da taxa livre de risco diária. Não utilizado neste cálculo.
    window (int): Período da janela móvel em dias. Se 0, calcula o Índice Calmar para todo o período.
    min_periods (int): Número mínimo de dados necessários para começar o cálculo.

    Retorna:
    pd.DataFrame: DataFrame contendo o Índice de Calmar em janela móvel para cada ativo.
    """
    # Cálculo dos retornos acumulados
    cumulative_returns = (1 + returns_df).cumprod()

    if benchmark_returns is not None:
        cumulative_benchmark = (1 + benchmark_returns).cumprod()
        returns = cumulative_returns / cumulative_benchmark - 1
    else:
        returns = cumulative_returns

    # Cálculo do drawdown máximo
    max_drawdown = (returns / returns.cummax() - 1).rolling(window=window, min_periods=min_periods).min()
    
    # Retorno anualizado em janela móvel
    annualized_return = returns_df.rolling(window=window, min_periods=min_periods).mean() * 252

    calmar_index = annualized_return / abs(max_drawdown)
    return calmar_index

def calculate_redemption_elasticity(returns_df, redemptions_df, window=5, lag=1):
    """
    Calcula a elasticidade dos resgates em janelas móveis, com a possibilidade de incluir um lag entre as janelas.

    Argumentos:
    returns_df (pd.DataFrame): DataFrame com os retornos diários dos fundos.
    redemptions_df (pd.DataFrame): DataFrame com os resgates diários dos fundos.
    window (int): Tamanho da janela móvel em dias.
    lag (int): Número de dias de lag entre a janela de retorno e a janela de resgates.

    Retorna:
    pd.DataFrame: DataFrame contendo a elasticidade dos resgates em janelas móveis para cada fundo.
    """
    elasticity_df = pd.DataFrame(index=returns_df.index)

    for col in returns_df.columns:
        # Calcula a média de retornos em janela móvel
        rolling_returns = returns_df[col].rolling(window=window).mean()

        # Calcula a média de resgates em janela móvel
        rolling_redemptions = redemptions_df[col].rolling(window=window).mean()

        # Desloca os retornos pela quantidade de dias especificada no lag
        rolling_returns_lagged = rolling_returns.shift(lag)

        # Calcula a elasticidade: (ΔResgates / Resgates) / (ΔRetornos / Retornos)
        elasticity = (rolling_redemptions.pct_change() / rolling_returns_lagged.pct_change()).fillna(0)
        
        # Armazena a elasticidade no DataFrame
        elasticity_df[col] = elasticity

    return elasticity_df

def calculate_redemption_elasticity(returns_df, redemptions_df, window=30, lag=30):
    """
    Calcula a elasticidade dos resgates em janelas móveis, com a possibilidade de incluir um lag entre as janelas.

    Argumentos:
    returns_df (pd.DataFrame): DataFrame com os retornos diários dos fundos.
    redemptions_df (pd.DataFrame): DataFrame com os resgates diários dos fundos.
    window (int): Tamanho da janela móvel em dias.
    lag (int): Número de dias de lag entre a janela de retorno e a janela de resgates.

    Retorna:
    pd.DataFrame: DataFrame contendo a elasticidade dos resgates em janelas móveis para cada fundo.
    """
    elasticity_df = pd.DataFrame(index=returns_df.index)

    for col in returns_df.columns:
        # Calcula a média de retornos em janela móvel
        rolling_returns = returns_df[col].rolling(window=window).mean()

        # Calcula a média de resgates em janela móvel
        rolling_redemptions = redemptions_df[col].rolling(window=window).mean()

        # Desloca os retornos pela quantidade de dias especificada no lag
        rolling_returns_lagged = rolling_returns.shift(lag)

        # Calcula a elasticidade: (ΔResgates / Resgates) / (ΔRetornos / Retornos)
        elasticity = (rolling_redemptions.pct_change() / rolling_returns_lagged.pct_change()).fillna(0)
        
        # Armazena a elasticidade no DataFrame
        elasticity_df[col] = elasticity

    return elasticity_df

def optimal_window_for_correlation(returns_df, capital_inflows_df, min_window=1, max_window=30, lag= 30):
    """
    Identifica a janela de retornos que gera a maior correlação com as captações.

    Argumentos:
    returns_df (pd.DataFrame): DataFrame com os retornos diários.
    capital_inflows_df (pd.DataFrame): DataFrame com as captações diárias.
    min_window (int): Tamanho mínimo da janela a ser testada.
    max_window (int): Tamanho máximo da janela a ser testada.

    Retorna:
    dict: Dicionário contendo a melhor janela e a correlação correspondente para cada ativo.
    """
    best_windows = {}

    for col in returns_df.columns:
        best_corr = -1  # Inicializa com uma correlação negativa
        best_window = min_window

        for window in range(min_window, max_window + 1):
            # Calcula a média dos retornos em janela móvel
            rolling_returns = returns_df[col].rolling(window=window).mean()
            
            # Desloca os retornos para frente (lag) para comparar com as captações futuras
            performance_lagged = rolling_returns.shift(lag)
            
            # Calcula a correlação com as captações
            correlation = performance_lagged.corr(capital_inflows_df[col])
            
            # Verifica se esta é a melhor correlação encontrada
            if correlation > best_corr:
                best_corr = correlation
                best_window = window

        # Armazena a melhor janela e correlação para o ativo
        best_windows[col] = {'Best Window': best_window, 'Correlation': best_corr}

    return best_windows

def analyze_negative_performance_vs_redemptions(returns_df, redemptions_df, window=5, lag = 30):
    """
    Analisa a correlação entre a performance negativa passada e os resgates futuros.

    Argumentos:
    returns_df (pd.DataFrame): DataFrame com os retornos diários.
    redemptions_df (pd.DataFrame): DataFrame com os resgates diários.
    window (int): Número de dias de lag para analisar o impacto da performance negativa.

    Retorna:
    pd.DataFrame: DataFrame com as correlações entre os retornos negativos e os resgates.
    """
    # Calcula a média dos retornos em janela móvel
    rolling_returns = returns_df.rolling(window=window).mean()
    
    # Mantém apenas as médias de retorno negativas
    #if negativo == True:
    #performance = rolling_returns[rolling_returns < 0]
    #else:
    performance = rolling_returns
    # Desloca os retornos negativos para frente (lag) para comparar com os resgates futuros
    performance_lagged = performance.shift(lag)
    
    # Calcula a correlação com os resgates
    correlation_results = performance_lagged.corrwith(redemptions_df)

    return correlation_results

def granger_causality_test(returns_df, redemptions_df, window=30, max_lag=30):
    """
    Realiza o Teste de Causalidade de Granger entre a performance em janelas móveis e os resgates.

    Argumentos:
    returns_df (pd.DataFrame): DataFrame com os retornos diários dos fundos.
    redemptions_df (pd.DataFrame): DataFrame com os resgates diários dos fundos.
    max_lag (int): Máximo número de lags a serem testados no Teste de Granger.
    window (int): Tamanho da janela móvel em dias para calcular a performance.

    Retorna:
    dict: Resultados do Teste de Granger para cada fundo, incluindo p-valores para diferentes lags.
    """
    results = {}

    for col in returns_df.columns:
        # Calcula a média de retornos em janela móvel
        rolling_returns = returns_df[col].rolling(window=window).mean()

        # Prepara os dados para o teste de Granger
        data = pd.concat([rolling_returns, redemptions_df[col]], axis=1).dropna()
        data.columns = ['Performance', 'Redemptions']

        # Realiza o Teste de Granger
        test_result = grangercausalitytests(data, maxlag=max_lag, verbose=False)

        # Armazena os p-valores para cada lag
        p_values = {lag: round(test_result[lag][0]['ssr_ftest'][1], 4) for lag in range(1, max_lag + 1)}
        results[col] = p_values

    return results

def calculate_investment_metrics(returns_df, benchmark_returns, risk_free_rate, window=0):
    """
    Calcula diversos índices de performance de investimentos para o período todo ou em janela móvel.

    Argumentos:
    returns_df (pd.DataFrame): DataFrame com as datas como índice e os valores de retorno de n investimentos em cada coluna.
    benchmark_returns (pd.Series): Série dos retornos diários do benchmark.
    risk_free_rate (float or pd.Series): Taxa de retorno livre de risco (fixa ou uma série de valores diários).
    window (int, opcional): Período da janela móvel em dias. Se 0 ou 1, calcula os índices para todo o período.
                             Se maior que 1, calcula os índices em janela móvel. Padrão é 0.

    Retorna:
    pd.DataFrame: DataFrame contendo os valores dos índices para cada investimento, com a data de referência e o nome do índice.
    """
    # Casamento de datas
    common_dates = returns_df.index.intersection(benchmark_returns.index)
    if isinstance(risk_free_rate, pd.Series):
        common_dates = common_dates.intersection(risk_free_rate.index)

    returns_df = returns_df.loc[common_dates].dropna(how='any')  # Remove linhas com valores faltantes
    benchmark_returns = benchmark_returns.loc[common_dates]
    if isinstance(risk_free_rate, pd.Series):
        risk_free_rate = risk_free_rate.loc[common_dates]

    metrics = []

    if window <= 1:
        for col in returns_df.columns:
            if isinstance(risk_free_rate, pd.Series):
                excess_returns = returns_df[col] - risk_free_rate
            else:
                excess_returns = returns_df[col] - risk_free_rate

            mean_excess_return = excess_returns.mean()
            std_excess_return = excess_returns.std()

            sharpe_ratio = mean_excess_return / std_excess_return

            beta, alpha, _, _, _ = linregress(benchmark_returns, returns_df[col])
            treynor_ratio = mean_excess_return / beta

            tracking_error = np.std(returns_df[col] - benchmark_returns)
            information_ratio = mean_excess_return / tracking_error

            volatility = returns_df[col].std()

            metrics.append((returns_df.index[-1], 'Sharpe Ratio', col, sharpe_ratio))
            metrics.append((returns_df.index[-1], 'Treynor Ratio', col, treynor_ratio))
            metrics.append((returns_df.index[-1], 'Information Ratio', col, information_ratio))
            metrics.append((returns_df.index[-1], 'Tracking Error', col, tracking_error))
            metrics.append((returns_df.index[-1], 'Beta', col, beta))
            metrics.append((returns_df.index[-1], 'Alpha', col, alpha))
            metrics.append((returns_df.index[-1], 'Volatility', col, volatility))
    else:
        for col in returns_df.columns:
            for i in range(len(returns_df) - window + 1):
                window_start = i
                window_end = i + window
                returns_window = returns_df[col].iloc[window_start:window_end]
                benchmark_returns_window = benchmark_returns.iloc[window_start:window_end]

                if isinstance(risk_free_rate, pd.Series):
                    risk_free_rate_window = risk_free_rate.iloc[window_start:window_end]
                else:
                    risk_free_rate_window = risk_free_rate

                excess_returns = returns_window - risk_free_rate_window
                mean_excess_return = excess_returns.mean()
                std_excess_return = excess_returns.std()

                sharpe_ratio = mean_excess_return / std_excess_return

                beta, alpha, _, _, _ = linregress(benchmark_returns_window, returns_window)
                treynor_ratio = mean_excess_return / beta

                tracking_error = np.std(returns_window - benchmark_returns_window)
                information_ratio = mean_excess_return / tracking_error

                volatility = returns_window.std()

                reference_date = returns_df.index[window_end - 1]

                metrics.append((reference_date, 'Sharpe Ratio', col, sharpe_ratio))
                metrics.append((reference_date, 'Treynor Ratio', col, treynor_ratio))
                metrics.append((reference_date, 'Information Ratio', col, information_ratio))
                metrics.append((reference_date, 'Tracking Error', col, tracking_error))
                metrics.append((reference_date, 'Beta', col, beta))
                metrics.append((reference_date, 'Alpha', col, alpha))
                metrics.append((reference_date, 'Volatility', col, volatility))

    metrics_df = pd.DataFrame(metrics, columns=['Date', 'Metric', 'Investment', 'Value'])
    metrics_pivot = metrics_df.pivot_table(index=['Date', 'Metric'], columns='Investment', values='Value').reset_index()

    return metrics_pivot

def calculate_investment_metrics_pivot(returns_df, benchmark_returns, risk_free_rate, window=0):
    """
    Calcula diversos índices de performance de investimentos para o período todo ou em janela móvel.

    Argumentos:
    returns_df (pd.DataFrame): DataFrame com as datas como índice e os valores de retorno de n investimentos em cada coluna.
    benchmark_returns (pd.Series): Série dos retornos diários do benchmark.
    risk_free_rate (float or pd.Series): Taxa de retorno livre de risco (fixa ou uma série de valores diários).
    window (int, opcional): Período da janela móvel em dias. Se 0 ou 1, calcula os índices para todo o período.
                             Se maior que 1, calcula os índices em janela móvel. Padrão é 0.

    Retorna:
    pd.DataFrame: DataFrame contendo os valores dos índices para cada investimento, com a data de referência e o nome do índice.
    """
    # Casamento de datas
    common_dates = returns_df.index.intersection(benchmark_returns.index)
    if isinstance(risk_free_rate, pd.Series):
        common_dates = common_dates.intersection(risk_free_rate.index)

    returns_df = returns_df.loc[common_dates].dropna(how='any')  # Remove linhas com valores faltantes
    benchmark_returns = benchmark_returns.loc[common_dates]
    if isinstance(risk_free_rate, pd.Series):
        risk_free_rate = risk_free_rate.loc[common_dates]

    metrics = []

    if window <= 1:
        for col in returns_df.columns:
            if isinstance(risk_free_rate, pd.Series):
                excess_returns = returns_df[col] - risk_free_rate
            else:
                excess_returns = returns_df[col] - risk_free_rate

            mean_excess_return = excess_returns.mean()
            std_excess_return = excess_returns.std()

            sharpe_ratio = mean_excess_return / std_excess_return

            beta, alpha, _, _, _ = linregress(benchmark_returns, returns_df[col])
            treynor_ratio = mean_excess_return / beta

            tracking_error = np.std(returns_df[col] - benchmark_returns)
            information_ratio = mean_excess_return / tracking_error

            metrics.append((returns_df.index[-1], 'Sharpe Ratio', col, sharpe_ratio))
            metrics.append((returns_df.index[-1], 'Treynor Ratio', col, treynor_ratio))
            metrics.append((returns_df.index[-1], 'Information Ratio', col, information_ratio))
            metrics.append((returns_df.index[-1], 'Tracking Error', col, tracking_error))
            metrics.append((returns_df.index[-1], 'Beta', col, beta))
            metrics.append((returns_df.index[-1], 'Alpha', col, alpha))
    else:
        for col in returns_df.columns:
            for i in range(len(returns_df) - window + 1):
                window_start = i
                window_end = i + window
                returns_window = returns_df[col].iloc[window_start:window_end]
                benchmark_returns_window = benchmark_returns.iloc[window_start:window_end]

                if isinstance(risk_free_rate, pd.Series):
                    risk_free_rate_window = risk_free_rate.iloc[window_start:window_end]
                else:
                    risk_free_rate_window = risk_free_rate

                excess_returns = returns_window - risk_free_rate_window
                mean_excess_return = excess_returns.mean()
                std_excess_return = excess_returns.std()

                sharpe_ratio = mean_excess_return / std_excess_return

                beta, alpha, _, _, _ = linregress(benchmark_returns_window, returns_window)
                treynor_ratio = mean_excess_return / beta

                tracking_error = np.std(returns_window - benchmark_returns_window)
                information_ratio = mean_excess_return / tracking_error

                reference_date = returns_df.index[window_end - 1]

                metrics.append((reference_date, 'Sharpe Ratio', col, sharpe_ratio))
                metrics.append((reference_date, 'Treynor Ratio', col, treynor_ratio))
                metrics.append((reference_date, 'Information Ratio', col, information_ratio))
                metrics.append((reference_date, 'Tracking Error', col, tracking_error))
                metrics.append((reference_date, 'Beta', col, beta))
                metrics.append((reference_date, 'Alpha', col, alpha))

    metrics_df = pd.DataFrame(metrics, columns=['Date', 'Metric', 'Investment', 'Value'])
    metrics_pivot = metrics_df.pivot_table(index=['Date', 'Metric'], columns='Investment', values='Value').reset_index()

    return metrics_pivot

def volatilidade_rolling_multi(retornos_df, retornos_benchmark, janela=0, janela_minima=1, agregador_retorno=1):
    """
    Calcula a volatilidade dos ativos em relação ao benchmark em uma janela móvel para múltiplos investimentos.

    Argumentos:
    retornos_df (pd.DataFrame): DataFrame com as datas como índice e os valores de retorno de n investimentos em cada coluna.
    retornos_benchmark (pd.Series): Série dos retornos diários do benchmark.
    janela (int, opcional): Período da janela móvel em dias. Se 0 ou 1, calcula a volatilidade para todo o período.
                             Se maior que 1, calcula a volatilidade em janela móvel. Padrão é 0.
    janela_minima (int): Número mínimo de dados para começar a calcular a volatilidade.
    agregador_retorno (int, opcional): Número de dias para agregar os retornos antes de calcular a volatilidade. Padrão é 1 (retornos diários).

    Retorna:
    pd.DataFrame: DataFrame contendo a volatilidade em janela móvel para cada investimento.
    """

    # Casamento de datas
    datas_comuns = retornos_df.index.intersection(retornos_benchmark.index)
    retornos_df = retornos_df.loc[datas_comuns]
    retornos_benchmark = retornos_benchmark.loc[datas_comuns]

    # Agregar retornos se necessário
    if agregador_retorno > 1:
        retornos_df = retornos_df.rolling(agregador_retorno).sum().dropna()/agregador_retorno
        retornos_benchmark = retornos_benchmark.rolling(agregador_retorno).sum().dropna()/agregador_retorno

    volatilidade_movel = pd.DataFrame(index=retornos_df.index)

    for col in retornos_df.columns:
        col_volatilidade = []

        if janela == 0:
            # Calcular a volatilidade global para o período completo
            volatilidade = np.std(retornos_df[col] - retornos_benchmark)
            col_volatilidade.append(volatilidade)
            index_dates = [retornos_df.index[-1]]
        else:
            for i in range(len(retornos_df)):
                # Ajustar a janela para os períodos iniciais
                if i < janela_minima - 1:
                    continue
                elif i < janela - 1:
                    janela_retornos = retornos_df[col].iloc[:i+1]
                    janela_retornos_benchmark = retornos_benchmark.iloc[:i+1]
                    volatilidade = np.std(janela_retornos - janela_retornos_benchmark)
                    col_volatilidade.append(volatilidade)
                else:
                    janela_retornos = retornos_df[col].iloc[i-janela+1:i+1]
                    janela_retornos_benchmark = retornos_benchmark.iloc[i-janela+1:i+1]
                    volatilidade = np.std(janela_retornos - janela_retornos_benchmark)
                    col_volatilidade.append(volatilidade)

            index_dates = retornos_df.index[janela_minima-1:]

        col_volatilidade_df = pd.DataFrame(col_volatilidade, index=index_dates, columns=[col])
        volatilidade_movel = volatilidade_movel.join(col_volatilidade_df, how='outer')

    if janela == 0:
        return volatilidade_movel.tail(1)
    
    return volatilidade_movel.dropna()


def correlacao_rolling_multi(retornos_df, retornos_benchmark, janela=0, janela_minima=1):
    """
    Calcula a correlação entre os retornos dos ativos e os retornos do benchmark em uma janela móvel para múltiplos investimentos.

    Argumentos:
    retornos_df (pd.DataFrame): DataFrame com as datas como índice e os valores de retorno de n investimentos em cada coluna.
    retornos_benchmark (pd.Series): Série dos retornos diários do benchmark.
    janela (int, opcional): Período da janela móvel em dias. Se 0 ou 1, calcula a correlação para todo o período.
                             Se maior que 1, calcula a correlação em janela móvel. Padrão é 0.
    janela_minima (int): Número mínimo de dados para começar a calcular a correlação.

    Retorna:
    pd.DataFrame: DataFrame contendo a correlação em janela móvel para cada investimento.
    """

    # Casamento de datas
    datas_comuns = retornos_df.index.intersection(retornos_benchmark.index)
    retornos_df = retornos_df.loc[datas_comuns]
    retornos_benchmark = retornos_benchmark.loc[datas_comuns]

    correlacao_movel = pd.DataFrame(index=retornos_df.index)

    for col in retornos_df.columns:
        col_correlacao = []

        if janela == 0:
            # Calcular a correlação global para o período completo
            correlacao = retornos_df[col].corr(retornos_benchmark)
            col_correlacao.append(correlacao)
            index_dates = [retornos_df.index[-1]]
        else:
            for i in range(len(retornos_df)):
                # Ajustar a janela para os períodos iniciais
                if i < janela_minima - 1:
                    continue
                elif i < janela - 1:
                    janela_retornos = retornos_df[col].iloc[:i+1]
                    janela_retornos_benchmark = retornos_benchmark.iloc[:i+1]
                    correlacao = janela_retornos.corr(janela_retornos_benchmark)
                    col_correlacao.append(correlacao)
                else:
                    janela_retornos = retornos_df[col].iloc[i-janela+1:i+1]
                    janela_retornos_benchmark = retornos_benchmark.iloc[i-janela+1:i+1]
                    correlacao = janela_retornos.corr(janela_retornos_benchmark)
                    col_correlacao.append(correlacao)

            index_dates = retornos_df.index[janela_minima-1:]

        col_correlacao_df = pd.DataFrame(col_correlacao, index=index_dates, columns=[col])
        correlacao_movel = correlacao_movel.join(col_correlacao_df, how='outer')

    if janela == 0:
        return correlacao_movel.tail(1)
    
    return correlacao_movel.dropna()


def correlacao_media_rolling_multi(retornos_df, janela=0, janela_minima=1):
    """
    Calcula a correlação do retorno de cada um dos ativos contra o retorno médio dos demais ativos em uma janela móvel para múltiplos investimentos.

    Argumentos:
    retornos_df (pd.DataFrame): DataFrame com as datas como índice e os valores de retorno de n investimentos em cada coluna.
    janela (int, opcional): Período da janela móvel em dias. Se 0 ou 1, calcula a correlação para todo o período.
                             Se maior que 1, calcula a correlação em janela móvel. Padrão é 0.
    janela_minima (int): Número mínimo de dados para começar a calcular a correlação.

    Retorna:
    pd.DataFrame: DataFrame contendo a correlação em janela móvel para cada investimento.
    """

    correlacao_movel = pd.DataFrame(index=retornos_df.index)

    for col in retornos_df.columns:
        col_correlacao = []

        if janela == 0:
            # Calcular a correlação global para o período completo
            media_retorno_outros = retornos_df.drop(columns=[col]).mean(axis=1)
            correlacao = retornos_df[col].corr(media_retorno_outros)
            col_correlacao.append(correlacao)
            index_dates = [retornos_df.index[-1]]
        else:
            for i in range(len(retornos_df)):
                # Ajustar a janela para os períodos iniciais
                if i < janela_minima - 1:
                    continue
                elif i < janela - 1:
                    janela_retornos = retornos_df.iloc[:i+1]
                    media_retorno_outros = janela_retornos.drop(columns=[col]).mean(axis=1)
                    correlacao = janela_retornos[col].corr(media_retorno_outros)
                    col_correlacao.append(correlacao)
                else:
                    janela_retornos = retornos_df.iloc[i-janela+1:i+1]
                    media_retorno_outros = janela_retornos.drop(columns=[col]).mean(axis=1)
                    correlacao = janela_retornos[col].corr(media_retorno_outros)
                    col_correlacao.append(correlacao)

            index_dates = retornos_df.index[janela_minima-1:]

        col_correlacao_df = pd.DataFrame(col_correlacao, index=index_dates, columns=[col])
        correlacao_movel = correlacao_movel.join(col_correlacao_df, how='outer')

    if janela == 0:
        return correlacao_movel.tail(1)
    
    return correlacao_movel.dropna()