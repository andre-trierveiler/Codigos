# -*- coding: utf-8 -*-
"""
Created on Mon Dec 16 17:15:33 2024

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
from datetime import datetime, timedelta


#from itables import init_notebook_mode
#from itables import show 

#python -m streamlit run C:\Users\andre_trierveiler\EstrtuturaStreamLit.py
#python -m streamlit run C:\Users\andre_trierveiler\EstrtuturaStreamLit.py --server.address localhost --server.port 8505 

#import businessdays as bzd

color_map = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52']

# Definições gerais do streamlit
st.set_page_config(layout="wide")

# Conexões 
producao_url = 'https://api.anbima.com.br/'
sandbox_url = 'https://api-sandbox.anbima.com.br/'
id_url = "https://api.anbima.com.br/oauth/access-token"
id_url_sandbox = "https://api-sandbox.anbima.com.br/oauth/access-token"

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

def conectar(client_id, client_secret, client_credentials, url=url, id_url=id_url):
    client_credentials = client_credentials.encode('ascii')
    senhabytes = base64.b64encode(client_credentials)
    senha = base64.b64decode(senhabytes)
    senha_txt = senhabytes.decode('utf-8')
    body = {"grant_type": "client_credentials" }

    headers = {
            'content-type': 'application/json',
            'Authorization': 'Basic ' + senha_txt}
    
    
    request = requests.post(id_url, headers=headers, json=body, allow_redirects=True)
    informacoes = request.json()
    token = informacoes['access_token']  
    
    return { "content-type": "application/json",
            "client_id": f"{client_id}",
            "access_token": f"{token}"}
   

####  Header produção###
#headers = conectar('wRGlvlj1bOW3', 'l4riAuRd0CUL','wRGlvlj1bOW3:l4riAuRd0CUL', url)
headers = conectar('wRGlvlj1bOW3', 'l4riAuRd0CUL','wRGlvlj1bOW3:l4riAuRd0CUL', url, id_url)

### Header Sandbox ###   
#headers2 = conectar('nZqmOGEuh6bg', 'BMXhChrji7ca','nZqmOGEuh6bg:BMXhChrji7ca', url)
headers2 = conectar('nZqmOGEuh6bg', 'BMXhChrji7ca','nZqmOGEuh6bg:BMXhChrji7ca', url, id_url)

def extrair_json(http, headers = headers):
    request = requests.get(http, headers=headers)
    try:
        df = request.json()
        return df
    except ValueError:
        print('Erro')
        print(http)
        print(request.content)
        return 'Erro'
 

df_hist_classe_sub = pd.DataFrame()    
df_hist_segmento = pd.DataFrame()

codigo_classe = 'C0000146757'

data_inicial = '2024-01-01'
data_final = '2024-11-13'



segmento_hist_http = f'{url}feed/fundos/v2/fundos/segmento-investidor/{codigo_classe}/patrimonio-liquido?mes-referencia=7&ano-referencia=2024'

request = requests.get(segmento_hist_http, headers=headers2)
request.status_code
json_hist_segmento = extrair_json(segmento_hist_http, headers2)
temp_hist_segmento = pd.json_normalize(json_hist_segmento['historico_segmento_investidor_fundo'])

historico = json_hist_segmento ['historico_segmento_investidor_fundo'][0]
distribuicao = historico['distribuicao_segmento_investidor']
df = pd.DataFrame(distribuicao)
df['codigo_classe'] = json_hist_segmento['classe']['codigo_classe']
df['nome_comercial'] = json_hist_segmento['classe']['nome_comercial']
df['data_referencia'] = json_hist_segmento['historico_segmento_investidor_fundo'][0]['data_referencia']


def generate_months_years(start_date, end_date):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    current = start
    months_years = []

    while current <= end:
        months_years.append((current.month, current.year))
        # Move to the next month
        if current.month == 12:
            current = datetime(current.year + 1, 1, 1)
        else:
            current = datetime(current.year, current.month + 1, 1)

    return months_years

months_years = generate_months_years(data_inicial, data_final)
df_hist_segmento = pd.DataFrame()   

for month, year in months_years:
    print(month)

    segmento_hist_http = f'https://api.anbima.com.br/feed/fundos/v2/fundos/segmento-investidor/{codigo_classe}/patrimonio-liquido?mes-referencia={month}&ano-referencia={year}'
    request = requests.get(segmento_hist_http, headers=headers2)
    if request.status_code != 200:
        print('Erro')
        continue
    json_hist_segmento = request.json()
        
    temp_hist_segmento = pd.json_normalize(json_hist_segmento['historico_segmento_investidor_fundo'])

    historico = json_hist_segmento ['historico_segmento_investidor_fundo'][0]
    distribuicao = historico['distribuicao_segmento_investidor']
    temp_hist_segmento = pd.DataFrame(distribuicao)
    temp_hist_segmento = temp_hist_segmento[temp_hist_segmento['percentual_patrimonio_liquido'] > 0.001]
    temp_hist_segmento['codigo_classe'] = json_hist_segmento['classe']['codigo_classe']
    temp_hist_segmento['nome_comercial'] = json_hist_segmento['classe']['nome_comercial']
    temp_hist_segmento['data_referencia'] = json_hist_segmento['historico_segmento_investidor_fundo'][0]['data_referencia']
    df_hist_segmento = pd.concat([df_hist_segmento, temp_hist_segmento], ignore_index=True)
    