# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 11:09:51 2024

@author: andre_trierveiler
"""

import base64
import requests
import pandas as pd
import teradataml
from teradataml import create_context, copy_to_sql
import teradata

producao_url = 'https://api.anbima.com.br/'
sandbox_url = 'https://api-sandbox.anbima.com.br/'
id_url = "https://api.anbima.com.br/oauth/access-token"

### Define se dados vem de ambiente de producao ou sandbox ###
producao = False

if producao:
  url = producao_url
  client_id = "wRGlvlj1bOW3"
  client_secret = "l4riAuRd0CUL"
  client_credentials = 'wRGlvlj1bOW3:l4riAuRd0CUL'

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

####  Header Flag ##
#headers = conectar(client_id, client_secret, client_credentials, url)


df_ima = pd.DataFrame()
ima_http= "https://api.anbima.com.br/feed/precos-indices/v1/indices-mais/carteira-teorica-ima?mes=09&ano=2024"


ima_get = requests.get(ima_http, headers=headers3)
ima_json = ima_get.json()
ima_geral = pd.json_normalize(ima_json)
for n in range(0,len(ima_json)):
    indice = ima_geral.indice[n]
    data_inicio = ima_geral.data_inicio[n]
    data_fim = ima_geral.data_fim[n]
    ima_df = pd.json_normalize(ima_json[n]['referencias'])
    ima_df['indice'] = indice
    ima_df['dt_inicio'] = data_inicio
    ima_df['dt_fim'] = data_fim
    print(indice)
    print(ima_df)
    df_ima = pd.concat([df_ima, ima_df])
    
    
df_ima = df_ima.drop(columns ='codigo_isin')
    

### IMA RESULTADOS ###

data_inicial = '2023-01-03'
data_final = '2023-12-28'

#ima_res_http= "https://api.anbima.com.br/feed/precos-indices/v1/indices-mais/resultados-ima"
ima_res_http = f'https://api.anbima.com.br/feed/precos-indices/v1/indices/resultados-ima?data-inicio={data_inicial}&data-fim={data_final}'
#ima_res_http = f'https://api.anbima.com.br/feed/precos-indices/v1/indices/resultados-ima?data={data_inicial}'


ima_res_get = requests.get(ima_res_http, headers=headers3)
ima_res_json = ima_res_get.json()
ima_res = pd.json_normalize(ima_res_json)

for n in range(0,len(ima_json)):
    ima_df = pd.json_normalize(ima_json[n]['componentes'])

    df_ima_res = pd.concat([df_ima, ima_df])
    
df_ima_res = df_ima_res.drop(columns ='codigo_isin')    
##### GRAVA DF NO TERADATA #######



## Conexao teradataml - usada para gravar df em bach##
con = create_context(host = 'TERADBAWS.sicredi.net', username="P_USR_DL_GESTAO_RECURSOS", password="JAW0b71329aadade35365afc6X", database="DL_GESTAO_RECURSOS")

## Conexao teradata "convencional" - usada para gravar fazer o append do df na tabela original do teradata ##
Exec = teradata.UdaExec (appName="TESTE", version="1.0", logConsole=False)
session = Exec.connect(method="odbc", system="teradbAWS.sicredi.net",
        username="P_USR_DL_GESTAO_RECURSOS", password="JAW0b71329aadade35365afc6X", Authentication="TDNEGO");


copy_to_sql(df_ima, table_name = 'ANBIMA_IMAS_PY', if_exists='replace') # this will load the datafrom from your client machine into the Teradata system.

 
session.execute("""
                insert into dl_Gestao_Recursos.anbima_imas
                select py.* from dl_Gestao_Recursos.anbima_imas_py py
                left join dl_Gestao_Recursos.anbima_imas ima on ima.dt_inicial = py.dt_inicio and ima.dt_final = py.dt_fim and ima.titulo = py.tipo_titulo and ima.indice = py.indice
                and ima.dt_vencimento = py.data_vencimento
                where ima.indice is null
                """)
 
session.execute("DROP TABLE DL_GESTAO_RECURSOS.anbima_imas_py") 