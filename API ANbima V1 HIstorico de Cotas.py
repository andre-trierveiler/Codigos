# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 09:21:33 2025

@author: andre_trierveiler
"""

import streamlit as st
import pandas as pd
import datetime
from bs4 import BeautifulSoup
import base64
import requests
import pandas as pd
import webbrowser
import warnings
import datetime
from datetime import datetime as dt
from datetime import timedelta
import datetime
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
from st_aggrid import AgGrid, GridOptionsBuilder
from itables import to_html_datatable
from streamlit.components.v1 import html
import itables.options as opt
from itables import init_notebook_mode
import pygwalker as pyg
from pygwalker.api.streamlit import StreamlitRenderer
init_notebook_mode(all_interactive=True)
import teradata
import indices_performance as pfm




color_map = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52']

# Definições gerais do streamlit
st.set_page_config(layout="wide")

# Conexões 
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
####  Header produção###
headers = conectar('wRGlvlj1bOW3', 'l4riAuRd0CUL','wRGlvlj1bOW3:l4riAuRd0CUL', url)

### Header Sandbox ###   
headers2 = conectar('nZqmOGEuh6bg', 'BMXhChrji7ca','nZqmOGEuh6bg:BMXhChrji7ca', url)



# Define listas pre-feitas/padrão de fundos
IRFM = ['16844885000145','07111384000169','04128704000103','08080680000102','18000606000192','10590141000165','02201164000102',
'14508605000100','14120511000151','09093749000103','37307534000175','10396381000123','07104761000132','13081159000120','31145851000156']

IRFM1 = ['18466245000174','11328882000135','11484558000106','10740670000106','12265822000183','08703063000116','19196599000109']

IMAB = ['16844890000158','07861554000122','07442078000105','08980715000160','13482675000166','05104498000156','10824344000179','10740658000193',
'10646895000190','10577516000157','02935723000108','04215425000179','10474513000198','08927393000195','32292548000149','11180605000128','14504578000190',
'04385278000185','11087118000115','16403465000123','09326708000101']

outros = ['16844890000158','07861554000122','07442078000105','08980715000160','13482675000166','05104498000156','10824344000179','10740658000193','10646895000190',
'10577516000157','02935723000108','04215425000179','10474513000198','08927393000195','32292548000149','11180605000128','14504578000190','04385278000185',
'11087118000115','16403465000123','09326708000101'],

IMAB5 = ['03543447000103', '20216216000104', '20216216000104', '29241758000101', '11060913000110', '41283495000190']

EUA = ['39255695000198','18079540000178', '30036235000102', '37306507000188', '24633818000100']

CDI = ['21743480000150','35292588000189', '13077418000149','20734931000120', '14508643000155','03737206000197','23215097000155','21170347000152','24634187000143']

RISCO2 = ['24634152000104','26344729000179','09498697000147','52095439000149','35828684000107','28851728000146',
'37319496000170','29726133000121','32397723000162','35940266000107','00400490000113','20458815000126','27928186000108','11451974000108',
'16938231000180','23951048000180','36620364000111','34172497000147','32666303000134','19736757000176','08773805000180','10320188000109',
'38537660000189','26549933000126','34867766000190','08875020000118','57338802000123','47684408000193','07160694000173']

RISCO = ['24634152000104','26344729000179','09498697000147'
         ,'35828684000107'
,'37319496000170','29726133000121','32397723000162','35940266000107','00400490000113'
,'20458815000126','27928186000108','11451974000108'
,'34867766000190','08875020000118'
,'19736757000176','08773805000180','10320188000109','07160694000173'
]

def extrair_json(http, headers = headers):
    request = requests.get(http, headers=headers)
    try:
        df = request.json()
        return df
    except ValueError:
        print('Erro')
        print(http)
        headers = conectar('wRGlvlj1bOW3', 'l4riAuRd0CUL','wRGlvlj1bOW3:l4riAuRd0CUL', url)    

df_hist_classe_sub = pd.DataFrame()  
lista_classe_sub = ['C0000528528','C0000335118']
for codigo_classe in lista_classe_sub:      
    classe_hist_http = f'{url}feed/fundos/v2/fundos/{codigo_classe}/serie-historica?size=50000&data-inicio=2019-01-01&data-fim=2025-01-01'
    request = requests.get(classe_hist_http, headers=headers)
    if request.status_code in [403,404]:
        print(request.status_code)
    else: 
        json_hist_classe = extrair_json(classe_hist_http)
        temp_hist_classe = pd.json_normalize(json_hist_classe['content'])
        df_hist_classe_sub = pd.concat([df_hist_classe_sub, temp_hist_classe], ignore_index=True)

df_hist_bck =  df_hist_classe_sub
df_hist_classe_sub.data_competencia= pd.to_datetime(df_hist_classe_sub.data_competencia, format='%Y-%m-%d')
df_hist_bck = df_hist_classe_sub

df_returns = df_hist_classe_sub.sort_values('codigo_classe', ascending=True) .pivot(index='data_competencia', columns='codigo_classe', values='valor_cota')
returns = df_returns.pct_change()


data_inicial = st.sidebar.date_input('Data Inicial', datetime.date(2017, 1, 1))
data_final = st.sidebar.date_input('Data Final', datetime.datetime.now()-1)

# Busca Indicores Anbima
def buscar_dados_ima(data_inicial, data_final, headers = headers, url = url):
    #inicializa df para armazenar dados
    df_ima_res = pd.DataFrame()
    url = f'{url}feed/precos-indices/v1/indices/resultados-ima'
    
    # Conexao
    headers = headers
    
    # Convertendo as strings de data em objetos datetime
    #data_inicial = datetime.strptime(data_inicial, '%Y-%m-%d')
   # data_final = datetime.strptime(data_final, '%Y-%m-%d')
    
    
    # Loop para buscar dados dia a dia
    data_atual = data_inicial
    while data_atual <= data_final:
        params = {
            'data': data_atual.strftime('%Y-%m-%d')
        }
        
        # Fazendo a requisição GET para a data específica
        response = requests.get(url, headers=headers, params=params)
        
        # Verificando se a requisição foi bem-sucedida
        if response.status_code == 200:
            dados_json = pd.DataFrame(response.json()) # Recebe a resposta como JSON
            df_ima_res  = pd.concat([df_ima_res ,dados_json], ignore_index=True)
        data_atual = data_atual + timedelta(days=1)   
    
    df_ima_res = df_ima_res.pivot(index='data_referencia', columns='indice', values='variacao_diaria')
    return df_ima_res 

