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
#import businessdays as bzd



#python -m streamlit run C:\Users\andre_trierveiler\EstrtuturaStreamLit_old.py --server.address localhost --server.port 8510

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





# Processamento Inicial - Carregando DataFrames
def carregar_dados_iniciais():
    # Cadastro Geral de Todos os fundos Anbima
    df_cadastro = pd.DataFrame() 
    size = 1000
    pages = 50
    for i in range(1,pages):
        fundos_http = f'{url}feed/fundos/v2/fundos?page={i}&size=1000' #tamanho máximo 1000, 32 paginas totais
        fundos = requests.get(fundos_http, headers=headers3)
        try:
            fundos_json = fundos.json()
        except ValueError:
            headers3 = conectar('wRGlvlj1bOW3', 'l4riAuRd0CUL','wRGlvlj1bOW3:l4riAuRd0CUL', url)
            fundos_json = fundos.json()
            i = i-1
        df = pd.json_normalize(fundos_json['content'])
        df['page'] = i
        df_cadastro = pd.concat([df_cadastro,df])
        if len(df) < 1000:
            break
    df_cadastro = df_cadastro.reset_index(drop=True)
    
    # Lista conjuntos de Fundos Padrão
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

    combined_dict = {k: [v1, v2] for k, v1, v2 in zip(keys, values1, values2)}     

    df_fundos = pd.DataFrame({
        'Fundo A': ['Fundo 1', 'Fundo 2'],
        'Fundo B': ['Fundo 3', 'Fundo 4']
    })
    
    df_indices = pd.DataFrame({
        'Indicador1': [1, 2, 3],
        'Indicador2': [4, 5, 6],
        'Indicador3': [7, 8, 9]
    })
    return df_fundos, df_indices

df_fundos, df_indices = carregar_dados_iniciais()

# Função de Processamento de Dados
def processar_dados(data_inicial, data_final, lista_fundos, indicador):
    st.write(f"Processando dados de {data_inicial} a {data_final} para o fundo {lista_fundos} e indicador {indicador}")
    # Processamento personalizado
    dados_processados = df_indices[indicador]
    return dados_processados

# Menus de Entrada
st.sidebar.header('Parâmetros de Entrada')

# Data Inicial e Final
data_inicial = st.sidebar.date_input('Data Inicial', datetime.date(2023, 1, 1))
data_final = st.sidebar.date_input('Data Final', datetime.date(2024, 1, 1))

# Lista Fundos Padrão
lista_fundos_dict = {
    "Lista 1": ['Fundo A', 'Fundo B'],
    "Lista 2": ['Fundo C', 'Fundo D'],
    "Lista 3": ['Fundo E', 'Fundo F']
}
lista_fundos_nome = st.sidebar.selectbox('Selecione a Lista de Fundos', list(lista_fundos_dict.keys()))
fundo_selecionado = st.sidebar.selectbox('Selecione o Fundo', lista_fundos_dict[lista_fundos_nome])

# Indicador
indicador_selecionado = st.sidebar.selectbox('Selecione o Indicador', df_indices.columns)

# Checkbox para Baixar Regulamento
baixar_regulamento = st.sidebar.checkbox('Baixar Regulamento')

# Botão "Rodar"
if st.sidebar.button('Rodar'):
    dados_processados = processar_dados(data_inicial, data_final, fundo_selecionado, indicador_selecionado)
    if baixar_regulamento:
        st.sidebar.download_button('Clique para baixar o regulamento', data="Aqui vai o regulamento", file_name='regulamento.pdf')

# Links de Visualizações
st.sidebar.subheader('Páginas de Visualização')

pagina_selecionada = st.sidebar.selectbox('Selecione a Página', 
                                          ['Comparativos de Classes', 
                                           'Rentabilidade', 
                                           'Patrimônio Líquido e Captação', 
                                           'Performance', 
                                           'Volatilidade', 
                                           'Histórico de Carteiras'])

# Exibir Páginas de Visualização separadamente
if pagina_selecionada == 'Comparativos de Classes':
    st.header("Comparativos de Classes")
    st.write("Exibir comparativos aqui...")  # Personalize a exibição

elif pagina_selecionada == 'Rentabilidade':
    st.header("Rentabilidade")
    st.write("Exibir rentabilidade aqui...")  # Personalize a exibição

elif pagina_selecionada == 'Patrimônio Líquido e Captação':
    st.header("Patrimônio Líquido e Captação")
    st.write("Exibir patrimônio líquido e captação aqui...")  # Personalize a exibição

elif pagina_selecionada == 'Performance':
    st.header("Performance")
    st.write("Exibir performance aqui...")  # Personalize a exibição

elif pagina_selecionada == 'Volatilidade':
    st.header("Volatilidade")
    st.write("Exibir volatilidade aqui...")  # Personalize a exibição

elif pagina_selecionada == 'Histórico de Carteiras':
    st.header("Histórico de Carteiras")
    st.write("Exibir histórico de carteiras aqui...")  # Personalize a exibição
