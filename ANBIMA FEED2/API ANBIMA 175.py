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
    try:
        fundos_json = fundos.json()
        print(i)
    except ValueError:
        headers3 = conectar('wRGlvlj1bOW3', 'l4riAuRd0CUL','wRGlvlj1bOW3:l4riAuRd0CUL', url)
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




df_fundos_det_geral = pd.DataFrame()
df_fundos_classes = pd.DataFrame()
df_fundos_prestadores = pd.DataFrame()
df_fundos_sufixos = pd.DataFrame()
df_fundos_benchmark  = pd.DataFrame()
df_classes_taxa = pd.DataFrame()
df_classes_taxas_entrada_saida = pd.DataFrame()
df_classes_sufixos = pd.DataFrame()
df_classes_prestadores = pd.DataFrame()
df_classes_indices_benchmark = pd.DataFrame()
df_subclasses = pd.DataFrame()
df_subclasses_prestadores = pd.DataFrame()
df_subclasses_taxas = pd.DataFrame()
df_subclasses_taxas_extrada_saida = pd.DataFrame()
df_subclasses_valores_minimos = pd.DataFrame()

abre_regulamento = False

df_cadastro_175 = df_cadastro[df_cadastro['identificador_fundo'].isin(df_dados_cadastrais_555.cnpj_fundo)]
i=0

codigos_fundo = ['F0000236365']
#for codigo_fundo in df_cadastro_175.codigo_fundo:
for codigo_fundo in df_cadastro.codigo_fundo:
    fundos_det_http = f'https://api.anbima.com.br/feed/fundos/v2/fundos/{codigo_fundo}'
    fundos_det = requests.get(fundos_det_http, headers=headers3)
    try:
        fundos_det_json = fundos_det.json()
        print(i)
    except ValueError:
        print('Erro')
        print(i)
        print(codigo_fundo)
        headers3 = conectar('wRGlvlj1bOW3', 'l4riAuRd0CUL','wRGlvlj1bOW3:l4riAuRd0CUL', url)
    #dados_cadastrais = pd.json_normalize(fundos_det_json['dados-cadastrais'])
    fundo_det_getal = pd.json_normalize(fundos_det_json)
    df_fundos_det_geral = pd.concat([df_fundos_det_geral,fundo_det_getal])
    
    fundos_det_classes = pd.json_normalize(fundos_det_json['classes'])
    fundos_det_classes['codigo_fundo'] = codigo_fundo
    df_fundos_classes = pd.concat([df_fundos_classes, fundos_det_classes])

    fundos_det_prestadores = pd.json_normalize(fundos_det_json['prestadores_fundo'])
    fundos_det_prestadores['codigo_fundo'] = codigo_fundo
    df_fundos_prestadores = pd.concat([df_fundos_prestadores, fundos_det_prestadores])
    
    taxas_classe = []
    taxas_entrada_saida_classe = []
    sufixos_classe = []
    prestadores_classe = []
    taxas_classe = []
    indices_benchmark_classe = []
    subclasses = []
    prestadores_sub = []
    taxas_sub = []
    taxas_entrada_saida_sub = []
    
    for classe in fundos_det_json['classes']:
        if 'taxas_classe' in classe:
            taxas_classe_temp = pd.DataFrame(classe['taxas_classe'])
            taxas_classe_temp['codigo_classe'] = classe['codigo_classe']
            taxas_classe_temp['codigo_fundo'] = codigo_fundo
            taxas_classe.append(taxas_classe_temp)
        if 'taxas_entrada_saida_classe' in classe:
            taxas_entrada_saida_classe_temp = pd.DataFrame(classe['taxas_entrada_saida_classe'])
            taxas_entrada_saida_classe_temp['codigo_classe'] = classe['codigo_classe']
            taxas_entrada_saida_classe_temp['codigo_fundo'] = codigo_fundo
            taxas_entrada_saida_classe.append(taxas_entrada_saida_classe_temp)
        if 'sufixos' in classe:
            sufixos_classe_temp = pd.DataFrame(classe['sufixos'])
            sufixos_classe_temp['codigo_classe'] = classe['codigo_classe']
            sufixos_classe_temp['codigo_fundo'] = codigo_fundo
            sufixos_classe.append(sufixos_classe_temp)
        if 'prestadores_classe' in classe:
            prestadores_classe_temp = pd.DataFrame(classe['prestadores_classe'])
            prestadores_classe_temp['codigo_classe'] = classe['codigo_classe']
            prestadores_classe_temp['codigo_fundo'] = codigo_fundo
            prestadores_classe.append(prestadores_classe_temp)
        if 'indices_benchmark' in classe:
            indices_benchmark_classe_temp = pd.DataFrame(classe['indices_benchmark'])
            indices_benchmark_classe_temp['codigo_classe'] = classe['codigo_classe']
            indices_benchmark_classe_temp['codigo_fundo'] = codigo_fundo
            indices_benchmark_classe.append(indices_benchmark_classe_temp)
        if 'subclasses' in classe:
            #subclasses_temp = pd.DataFrame(classe['subclasses'])
            subclasses_temp = pd.json_normalize(classe['subclasses'])
            subclasses_temp['codigo_classe'] = classe['codigo_classe']
            subclasses_temp['codigo_fundo'] = codigo_fundo
            subclasses.append(subclasses_temp)            
            for subclasse in classe['subclasses']:
                if 'prestadores_subclasse' in subclasse:
                    prestadores_sub_temp = pd.DataFrame(subclasse['prestadores_subclasse'])
                    prestadores_sub_temp['codigo_classe'] = classe['codigo_classe']
                    prestadores_sub_temp['codigo_fundo'] = codigo_fundo
                    prestadores_sub_temp['codigo_subclasse'] = subclasse['codigo_subclasse']
                    prestadores_sub.append(prestadores_sub_temp)  
                
                if 'taxas_subclasse' in subclasse:
                    taxas_sub_temp = pd.DataFrame(subclasse['taxas_subclasse'])
                    taxas_sub_temp['codigo_classe'] = classe['codigo_classe']
                    taxas_sub_temp['codigo_fundo'] = codigo_fundo
                    taxas_sub_temp['codigo_subclasse'] = subclasse['codigo_subclasse']
                    taxas_sub.append(taxas_sub_temp)  

                if 'taxas_entrada_saida_subclasse' in subclasse:
                    taxas_entrada_saida_sub_temp = pd.DataFrame(subclasse['taxas_entrada_saida_subclasse'])
                    taxas_entrada_saida_sub_temp['codigo_classe'] = classe['codigo_classe']
                    taxas_entrada_saida_sub_temp['codigo_fundo'] = codigo_fundo
                    taxas_entrada_saida_sub_temp['codigo_subclasse'] = subclasse['codigo_subclasse']
                    taxas_entrada_saida_sub.append(taxas_entrada_saida_sub_temp)  
                       
 #               for taxa_performance in subclasse['taxa_performance']:
 #                    teste = pd.json_normalize(taxa_performance['detalhes'])
 #                    teste = pd.DataFrame(taxa_performance['detalhes'])
 #                    teste = taxa_performance['detalhes']
 
    classes_taxa = pd.concat(taxas_classe, ignore_index=True)
    df_classes_taxa = pd.concat([df_classes_taxa,classes_taxa], ignore_index=True)
    
    taxas_entrada_saida_classe = pd.concat(taxas_entrada_saida_classe, ignore_index=True)
    df_classes_taxas_entrada_saida = pd.concat([df_classes_taxas_entrada_saida,taxas_entrada_saida_classe], ignore_index=True)
    
    sufixos_classe = pd.concat(sufixos_classe, ignore_index=True)
    df_classes_sufixos = pd.concat([ df_classes_sufixos,sufixos_classe], ignore_index=True)
    
    prestadores_classe = pd.concat(prestadores_classe, ignore_index=True)
    df_classes_prestadores = pd.concat([df_classes_prestadores,prestadores_classe], ignore_index=True)
    
    indices_benchmark_classe = pd.concat(indices_benchmark_classe, ignore_index=True)
    df_classes_indices_benchmark = pd.concat([df_classes_indices_benchmark,indices_benchmark_classe], ignore_index=True)

    subclasses = pd.concat(subclasses, ignore_index=True)
    df_subclasses = pd.concat([df_subclasses,subclasses], ignore_index=True)

    prestadores_sub = pd.concat(prestadores_sub, ignore_index=True)
    df_subclasses_prestadores = pd.concat([df_subclasses_prestadores,prestadores_sub], ignore_index=True)

    taxas_sub = pd.concat(taxas_sub, ignore_index=True)
    df_subclasses_taxas = pd.concat([df_subclasses_taxas,taxas_sub], ignore_index=True)

    taxas_entrada_saida_sub = pd.concat(taxas_entrada_saida_sub, ignore_index=True)
    df_subclasses_taxas_extrada_saida = pd.concat([df_subclasses_taxas_extrada_saida,taxas_entrada_saida_sub], ignore_index=True)
                
        
    print(codigo_fundo)
    print(i)
    i = i+1
    
df_cadastro = df_cadastro.reset_index(drop=True)
df_fundos_det_geral
df_fundos_classes
df_fundos_benchmark
df_classes_taxas
df_classes_sufixos
df_classes_taxas_entrada_saida
df_ classes_prestadores
df_classes_indices_benchmark
   
###ABR SUBVALORE DENTRO DE
##taxas_classe = pd.json_normalize(json_data, 'classes', ['taxas_classe'], errors='ignore', record_prefix='taxas_')
# COLOCAR A COLUNA CODIGO_FUNDO SEMPRE NA FRENTE#####
#colunas = ['nova_coluna'] + colunas[:-1]



codigo_fundo = 'F0000782386'
codigo_classe = 'C0000782386'
codigo_subclasse = 'S0000782386'
data_inicial = '2023-01-01'
data_final = '2023-12-31'
mes_ref = '09'
ano_ref = '2024'

### Historido alterações fundo -- Esse é bem chato de extrair a informação!!!
hist_cad_fundo_http = f'https://api-sandbox.anbima.com.br/beta/feed/fundos/v2/fundos/{codigo_fundo}/historico'

### Detalhes classe e subclasse - Não parece haver mais detalhamento que nas abertura que conseguimos apartir do "detalhe fundo" ja extraido - avaliar!!!

det_classe_http = f'https://api-sandbox.anbima.com.br/beta/feed/fundos/v2/fundos/{codigo_classe}'
det_subclasse_http = f'https://api-sandbox.anbima.com.br/beta/feed/fundos/v2/fundos/{codigo_subclasse}'

### Seggmento investidor = PL por segmento classe e subclasse
pl_classe_http = f'https://api-sandbox.anbima.com.br/beta/feed/fundos/v2/fundos/segmento-investidor/{codigo_classe}/patrimonio-liquido?mes-referencia={mes_ref}&ano-referencia={ano_ref}'
pl_subclasse_http = f'https://api-sandbox.anbima.com.br/beta/feed/fundos/v2/fundos/segmento-investidor/{codigo_subclasse}/patrimonio-liquido?mes-referencia={mes_ref}&ano-referencia={ano_ref}'

### Serie historica classe e subclasse
hist_classe_http= f'https://api-sandbox.anbima.com.br/beta/feed/fundos/v2/fundos/{codigo_classe}/serie-historica?size=1000&data-inicio={data_inicial}&data-fim={data_final}'
hist_subclasse_http = f'https://api-sandbox.anbima.com.br/beta/feed/fundos/v2/fundos/{codigo_subclasse}/serie-historica?size=1000&data-inicio={data_inicial}&data-fim={data_final}'


def extrair_json(http, headers = headers3):
    request = requests.get(http, headers=headers)
    try:
        df = request.json()
        return df
    except ValueError:
        print('Erro')
        print(http)
        headers3 = conectar('wRGlvlj1bOW3', 'l4riAuRd0CUL','wRGlvlj1bOW3:l4riAuRd0CUL', url)
        
df_hist_cad_fundo = extrair_json(hist_cad_fundo_http)
df_det_classe = extrair_json(det_classe_http)
df_det_subclasse = extrair_json(det_subclasse_http)

df_pl_classe = extrair_json(pl_classe_http)
df_pl_subclasse = extrair_json(pl_subclasse_http)

df_hist_classe = extrair_json(hist_classe_http)
df_hist_subclasse = extrair_json(hist_subclasse_http)









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

