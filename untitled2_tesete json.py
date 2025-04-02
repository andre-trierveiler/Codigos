import pandas as pd
import streamlit as st
import pandas as pd
import json

import base64
import requests
import warnings


#python -m streamlit run C:\Users\andre_trierveiler\Teste_Cadastro_Fundos.py --server.address localhost --server.port 8535

st.set_page_config(page_title="Cadastro de Fundos", layout="wide")
 
warnings.simplefilter('ignore')
 
producao_url = 'https://api.anbima.com.br/'
sandbox_url = 'https://api-sandbox.anbima.com.br/'
id_url = 'https://api.anbima.com.br/oauth/access-token'
 
### Define se dados vem de ambiente de producao ou sandbox ###
producao = True
oculta_nulos =False



    
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




def save_dict_to_dataframes(data, dataframes, parent_key='', extra_fields=None):
    if extra_fields is None:
        extra_fields = {}

    if isinstance(data, dict):
        # Adicionar campos extras se existirem
        combined_data = {**extra_fields, **data}

        # Criar um DataFrame para o nível atual do dicionário
        df = pd.DataFrame([combined_data])
        
        # Reordenar colunas para que os campos extras fiquem no início
        columns_order = [col for col in ["codigo_fundo", "nome_comercial_fundo", "codigo_classe", "nome_comercial_classe"] if col in df.columns] + [col for col in df.columns if col not in ["codigo_fundo", "nome_comercial_fundo", "codigo_classe", "nome_comercial_classe"]]
        df = df[columns_order]
        
        # Append ao DataFrame existente ou criar um novo
        if parent_key in dataframes:
            dataframes[parent_key] = pd.concat([dataframes[parent_key], df], ignore_index=True)
        else:
            dataframes[parent_key] = df.drop_duplicates()
        
        # Verificar se os campos extras estão presentes
        for key in ["codigo_fundo", "nome_comercial_fundo", "codigo_classe", "nome_comercial_classe"]:
            if key in data:
                extra_fields[key] = data[key]
        
        for key, value in data.items():
            new_key = f"{parent_key}_{key}" if parent_key else key
            save_dict_to_dataframes(value, dataframes, new_key, extra_fields)
    elif isinstance(data, list):
        # Se o item for uma lista, armazenar todos os dicionários da lista em um mesmo DataFrame
        list_data = []
        for item in data:
            if isinstance(item, dict):
                combined_item = {**extra_fields, **item}
                list_data.append(combined_item)
                save_dict_to_dataframes(item, dataframes, parent_key, extra_fields)
            else:
                list_data.append({parent_key: item})
        df = pd.DataFrame(list_data)
        
        # Reordenar colunas para que os campos extras fiquem no início
        columns_order = [col for col in ["codigo_fundo", "nome_comercial_fundo", "codigo_classe", "nome_comercial_classe"] if col in df.columns] + [col for col in df.columns if col not in ["codigo_fundo", "nome_comercial_fundo", "codigo_classe", "nome_comercial_classe"]]
        df = df[columns_order]
        
        # Append ao DataFrame existente ou criar um novo
        if parent_key in dataframes:
            dataframes[parent_key] = pd.concat([dataframes[parent_key], df], ignore_index=True)
        else:
            dataframes[parent_key] = df.drop_duplicates()

# Exemplo de uso
dataframes = {}
input_dict1 = {
    "codigo_fundo": "001",
    "nome_comercial_fundo": "Fundo A",
    "detalhes": {
        "codigo_classe": "A1",
        "nome_comercial_classe": "Classe A"
    }
}
input_dict2 = {
    "codigo_fundo": "002",
    "nome_comercial_fundo": "Fundo B",
    "detalhes": {
        "codigo_classe": "B1",
        "nome_comercial_classe": "Classe B"
    }
}


codigo_fundo = 'F0000231908'
# F0000252743
# F0000231908
def json_fundo(codigo_fundo, header):
    fundos_det_http = f'{url}feed/fundos/v2/fundos/{codigo_fundo}'
    fundos_det = requests.get(fundos_det_http, headers=header)
    
    try:
        headers3 = conectar('wRGlvlj1bOW3', 'l4riAuRd0CUL','wRGlvlj1bOW3:l4riAuRd0CUL', url)
        fundos_det_json = fundos_det.json()
    except ValueError:
        print('Erro')
        print(codigo_fundo)
        headers3 = conectar('wRGlvlj1bOW3', 'l4riAuRd0CUL','wRGlvlj1bOW3:l4riAuRd0CUL', url)
    
    fundo_det_cadastro = pd.json_normalize(fundos_det_json)
    
    fundo_data = fundos_det_json    
    return fundo_data

fundo_data = json_fundo('F0000231908', headers3)
fundo_data2 = json_fundo('F0000252743', headers3)

dataframes = {}
save_dict_to_dataframes(fundo_data, dataframes, parent_key='fundos')
save_dict_to_dataframes(fundo_data2, dataframes, parent_key='fundos')

dataframes['fundos_classes'] = [dataframes['fundos_classes']].drop_duplicates()

print(dataframes)