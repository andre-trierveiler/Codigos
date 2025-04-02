# -*- coding: utf-8 -*-
"""
Created on Sat Sep 28 14:42:04 2024

@author: andre_trierveiler
"""

"""
Created on Fri Jan 27 16:36:59 2023

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
import businessdays as bzd

warnings.simplefilter('ignore')

producao_url = 'https://api.anbima.com.br/'
sandbox_url = 'https://api-sandbox.anbima.com.br/'
id_url = "https://api.anbima.com.br/oauth/access-token"

### Define se dados vem de ambiente de producao ou sandbox ###
producao = False

if producao:
  url = producao_url
  client_id = "wRGlvlj1bOW3"
  client_secret = "l4riAuRd0CUL"
  client_credentials = "wRGlvlj1bOW3:l4riAuRd0CUL"

else:
  url = sandbox_url
  client_id = "nZqmOGEuh6bg"
  client_secret = "BMXhChrji7ca"
  client_credentials = "nZqmOGEuh6bg:BMXhChrji7ca"


client_credentials = client_credentials.encode('ascii')
senhabytes = base64.b64encode(client_credentials)
senha = base64.b64decode(senhabytes)


def conectar(client_id, client_secret, client_credentials, url=url):
    client_credentials = client_credentials.encode('ascii')
    senhabytes = base64.b64encode(client_credentials)
    senha = base64.b64decode(senhabytes)

    body = {"grant_type": "client_credentials" }

    headers = {
            'content-type': 'application/json',
            'Authorization': 'Basic d1JHbHZsajFiT1czOmw0cmlBdVJkMENVTA=='}
     
    request = requests.post(id_url, headers=headers, json=body, allow_redirects=True)
    informacoes = request.json()
    token = informacoes['access_token']  
    
    return { "content-type": "application/json",
            "client_id": f"{client_id}",
            "access_token": f"{token}"}

### Header Sandbox ###   
headers2 = conectar('nZqmOGEuh6bg', 'BMXhChrji7ca','nZqmOGEuh6bg:BMXhChrji7ca', url)

####  Header produção###
headers3 = conectar('wRGlvlj1bOW3', 'l4riAuRd0CUL','wRGlvlj1bOW3:l4riAuRd0CUL', url)


"""
headers = {
            'content-type': 'application/json',
            'Authorization': 'Basic d1JHbHZsajFiT1czOmw0cmlBdVJkMENVTA=='}
request = requests.post('https://api-sandbox.anbima.com.br/oauth/access-token', headers=headers, json=body, allow_redirects=True)
informacoes = request.json()
token = informacoes['access_token']  
"""


df_cadastro = pd.DataFrame() 
size = 1000
pages = 50
for i in range(1,pages):
    fundos_http = f'https://api-sandbox.anbima.com.br/beta/feed/fundos/v2/fundos?page={i}&size=1000' #tamanho máximo 1000, 32 paginas totais
    fundos = requests.get(fundos_http, headers=headers3)
    fundos_json = fundos.json()
    df = pd.json_normalize(fundos_json['content'])
    df['page'] = i
    df_cadastro = pd.concat([df_cadastro,df])
    if len(df) < 1000:
        break
df_cadastro = df_cadastro.reset_index(drop=True)

cnpjs = ['16844890000158',
'07861554000122',
'07442078000105',
'08980715000160',
'13482675000166',
'05104498000156',
'10824344000179',
'10740658000193',
'10646895000190',
'10577516000157',
'02935723000108',
'04215425000179',
'10474513000198',
'08927393000195',
'32292548000149',
'11180605000128',
'14504578000190',
'04385278000185',
'11087118000115',
'16403465000123',
'09326708000101']

#lista = df_cadastro[['codigo_fundo','nome_comercial_fundo']][df_cadastro['identificador_fundo'].isin(cnpjs)].reset_index(drop=True)



 
  #  for classe in fundos_det_json['classes']:
  #      
  #      taxas_classe = pd.json_normalize(fundos_det_json, 'classes', ['taxas_classe'], errors='ignore', record_prefix='subtaxas_')
  #      taxas_classe['codigo_fundo'] = codigo_fundo
  #      df_classes_taxa = pd.concat([df_classes_taxa, taxas_classe])
    
    fundos_det_prestadores =  pd.json_normalize(fundos_det_json['prestadores_fundo'])
    fundos_det_prestadores['codigo_fundo'] = codigo_fundo
    df_fundos_prestadores = pd.concat([df_fundos_prestadores, fundos_det_prestadores])
    
    fundos_det_sufixos =  pd.json_normalize(fundos_det_classes['sufixos'][0])
    fundos_det_sufixos['codigo_fundo'] = codigo_fundo
    df_fundo_sufixos = pd.concat([df_fundos_sufixos,fundos_det_sufixos])
    
    fundos_det_benchmark =  pd.json_normalize(fundos_det_classes['indices_benchmark'][0])
    fundos_det_benchmark['codigo_fundo'] = codigo_fundo
    df_fundos_benchmark = pd.concat([df_fundos_benchmark,fundos_det_benchmark])

df = pd.json_normalize(data, 'dados', ['id', 'nome'])
# COLOCAR A COLUNA CODIGO_FUNDO SEMPRE NA FRENTE#####
#colunas = ['nova_coluna'] + colunas[:-1]
codigo_fundo = 'F0000236365'
data_inicial = '2023-01-01'
data_final = '2023-12-31'
df_fundos_hist = pd.DataFrame()
fundos_hist_http = f'https://api-sandbox.anbima.com.br/feed/fundos/v2/fundos/{codigo_fundo}/serie-historica?data-inicio={data_inicial}&data-fim={data_final}'
fundos_hist = requests.get(fundos_hist_http, headers=headers3)
fundos_hist_json = fundos_hist.json()
fundos_hist = pd.json_normalize(fundos_hist_json['serie_historica'])
fundos_hist['codigo_fundo'] = codigo_fundo
fundos_hist['nome_fantasia'] = nome_fantasia
df_fundos_hist = pd.concat([df_fundos_hist, fundos_hist])
df_fundos_hist.data_referencia = pd.to_datetime(df_fundos_hist.data_referencia, format='%Y-%m-%d')    
df_hist_bck =  df_fundos_hist


"""
for codigo_fundo in lista.codigo_fundo:
    nome_fantasia = lista.nome_fantasia[lista['codigo_fundo'] == codigo_fundo].reset_index(drop=True)[0]
    #print(nome_fantasia, codigo_fundo)
    fundos_det_http = f'https://api-sandbox.anbima.com.br/beta/feed/fundos/v2/fundos/{codigo_fundo}'

    
    fundos_det = requests.get(fundos_det_http, headers=headers3)
    fundos_det_json = fundos_det.json()
    dados_cadastrais = pd.json_normalize(fundos_det_json['dados-cadastrais'])
    teste = pd.json_normalize(fundos_det_json['dados-cadastrais'])
    #dados_cadastrais['codigo_fundo'] = codigo_fundo
    df_dados_cadastrais = pd.concat([ df_dados_cadastrais,dados_cadastrais ])
    
    
    movimentacao = pd.json_normalize(fundos_det_json['movimentacao'])
    movimentacao['codigo_fundo'] = codigo_fundo
    movimentacao ['nome_fantasia'] = nome_fantasia
    df_movimentacao = pd.concat([ df_movimentacao,movimentacao ]) 
    
    prestadores = pd.json_normalize(fundos_det_json['prestadores'])
    prestadores['gestores_principal'] = pd.json_normalize(prestadores.gestores[0][0]).nome[0]
    prestadores['codigo_fundo'] = codigo_fundo
    prestadores['nome_fantasia'] = nome_fantasia
    df_prestadores = pd.concat([df_prestadores ,prestadores ]) 
    
    cota =  pd.json_normalize(fundos_det_json['serie_historica'])
    cota['codigo_fundo'] = codigo_fundo
    cota['nome_fantasia'] = nome_fantasia
    df_cota = pd.concat([df_cota ,cota ])
    
    taxas = pd.json_normalize(fundos_det_json['taxas'])
    taxas['codigo_fundo'] = codigo_fundo
    taxas['nome_fantasia'] = nome_fantasia
    df_taxas = pd.concat([df_taxas ,taxas ]) 
    
    documentos = pd.json_normalize(fundos_det_json['documentos'])
    documentos['codigo_fundo'] = codigo_fundo
    documentos['nome_fantasia'] = nome_fantasia
    df_documentos  = pd.concat([df_documentos, documentos]) 
    if abre_regulamento is True:
        webbrowser.open(documentos.url[0],new=2)   
        
    taxas_historico = pd.json_normalize(fundos_det_json['historico_taxas'])
    taxas_historico['codigo_fundo'] = codigo_fundo
    taxas_historico['nome_fantasia'] = nome_fantasia
    df_taxas_historico = pd.concat([df_taxas_historico, taxas_historico])
    
teste = pd.merge(df_dados_cadastrais,df_cota, on='codigo_fundo')
"""

