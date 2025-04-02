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
producao = True

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
request = requests.post('https://api.anbima.com.br/oauth/access-token', headers=headers, json=body, allow_redirects=True)
informacoes = request.json()
token = informacoes['access_token']  
"""

df_cadastro2 = pd.DataFrame() 
size = 1000
pages = 50
for i in range(1,pages):
    fundos_http = f'https://api.anbima.com.br/feed/fundos/v1/fundos?page={i}&size=1000' #tamanho máximo 1000, 32 paginas totais
    fundos = requests.get(fundos_http, headers=headers3)
    fundos_json = fundos.json()
    df = pd.json_normalize(fundos_json['content'])
    df['page'] = i
    df_cadastro2 = pd.concat([df_cadastro,df])
    if len(df) < 10:
        break
df_cadastro2 = df_cadastro2.reset_index(drop=True)

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

cnpjs = ['55574437000120']

lista = df_cadastro[['codigo_fundo','nome_fantasia']][df_cadastro['cnpj_fundo'].isin(cnpjs)].reset_index(drop=True)
#lista = df_cadastro[['codigo_fundo','nome_fantasia']][df_cadastro['situacao_atual'] == 'A'].reset_index(drop=True)

#df_dados_cadastrais = pd.DataFrame() 
df_movimentacao = pd.DataFrame()
df_prestadores = pd.DataFrame()
df_cota = pd.DataFrame()
df_documentos = pd.DataFrame()
df_taxas = pd.DataFrame()
df_taxas_historico = pd.DataFrame()

abre_regulamento = False

teste = requests.get('https://api.anbima.com.br/feed/fundos/v1/fundos-instituicao/01181521000155', headers=headers3)
teste_json = teste.json()
df_teste = pd.json_normalize(fundos_json['content'])

codigo_fundo = '330213'
fundos_det_http = f'https://api.anbima.com.br/feed/fundos/v1/fundos/{codigo_fundo}'
fundos_det = requests.get(fundos_det_http, headers=headers3)
fundos_det_json = fundos_det.json()
#dados_cadastrais = pd.json_normalize(fundos_det_json['dados-cadastrais']) 
n=0
q = 0
i= 0
for i in range(24899,lista.shape[0]):
    
    #nome_fantasia = lista.nome_fantasia[lista['codigo_fundo'] == codigo_fundo].reset_index(drop=True)[0]
    nome_fantasia = lista.loc[i, 'nome_fantasia']
    codigo_fundo = lista.loc[i, 'codigo_fundo']
    #print(nome_fantasia, codigo_fundo)
    fundos_det_http = f'https://api.anbima.com.br/feed/fundos/v1/fundos/{codigo_fundo}'
    
    fundos_det = requests.get(fundos_det_http, headers=headers3)
    try:
        fundos_det_json = fundos_det.json()
        print(i)
    except ValueError:
        print('Erro')
        print(i)
        print(codigo_fundo)
        headers3 = conectar('wRGlvlj1bOW3', 'l4riAuRd0CUL','wRGlvlj1bOW3:l4riAuRd0CUL', url)
        #i=i-1
    if fundos_det_json['dados-cadastrais']['situacao_atual'] == 'A':
        if fundos_det_json['dados-cadastrais']['fundo_adaptado_icvm_175'] == 'S':
            dados_cadastrais = pd.json_normalize(fundos_det_json['dados-cadastrais'])
            #teste = pd.json_normalize(fundos_det_json['dados-cadastrais'])
            #dados_cadastrais['codigo_fundo'] = codigo_fundo
            df_dados_cadastrais = pd.concat([ df_dados_cadastrais,dados_cadastrais ])
            n= n + 1
            print('n')
    
    
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

lista = df_cadastro[['codigo_fundo','nome_comercial_fundo']][df_cadastro['identificador_fundo'].isin(cnpjs)].reset_index(drop=True)


