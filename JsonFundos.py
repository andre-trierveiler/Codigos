# -*- coding: utf-8 -*-
"""
Created on Sat Feb  8 18:21:16 2025

@author: andre_trierveiler
"""


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




#### Atualizar Cadastro Total de Fundos ######
autaliza_cadastro = 1
if autaliza_cadastro == 1:
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
    df_cadastro = df_cadastro[df_cadastro['data_encerramento_fundo'].isnull()].reset_index(drop=True)
    df_cadastro.to_csv('cadastro_fundos.csv', index=False)
else:
    df_cadastro = pd.read_csv('cadastro_fundos.csv')
    
    
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

fundo_data = json_fundo(codigo_fundo, headers3)
fundo_data_b = json_fundo('F0000252743', headers3) 

# Função para salvar dicionários em DataFrames
def save_dict_to_dataframes(data, parent_key='', extra_fields=None):
    if extra_fields is None:
        extra_fields = {}

    if isinstance(data, dict):
        # Adicionar campos extras se existirem
        data.update(extra_fields)

        # Criar um DataFrame para o nível atual do dicionário
        df = pd.DataFrame([data])
        
        # Reordenar colunas para que os campos extras fiquem no início
        columns_order = [col for col in ["codigo_fundo", "nome_comercial_fundo", "codigo_classe", "nome_comercial_classe"] if col in df.columns] + [col for col in df.columns if col not in ["codigo_fundo", "nome_comercial_fundo", "codigo_classe", "nome_comercial_classe"]]
        df = df[columns_order]
        
        dataframes[parent_key] = df
        
        # Verificar se os campos extras estão presentes
        for key in ["codigo_fundo", "nome_comercial_fundo", "codigo_classe", "nome_comercial_classe"]:
            if key in data:
                extra_fields[key] = data[key]
        
        for key, value in data.items():
            new_key = f"{parent_key}_{key}" if parent_key else key
            save_dict_to_dataframes(value, new_key, extra_fields)
    elif isinstance(data, list):
        # Se o item for uma lista, armazenar todos os dicionários da lista em um mesmo DataFrame
        list_data = []
        for item in data:
            if isinstance(item, dict):
                item.update(extra_fields)
                list_data.append(item)
                save_dict_to_dataframes(item, parent_key, extra_fields)
            else:
                list_data.append({parent_key: item})
        df = pd.DataFrame(list_data)
        
        # Reordenar colunas para que os campos extras fiquem no início
        columns_order = [col for col in ["codigo_fundo", "nome_comercial_fundo", "codigo_classe", "nome_comercial_classe"] if col in df.columns] + [col for col in df.columns if col not in ["codigo_fundo", "nome_comercial_fundo", "codigo_classe", "nome_comercial_classe"]]
        df = df[columns_order]
        
        dataframes[parent_key] = df
        
dataframes = {}
save_dict_to_dataframes(fundo_data, parent_key='fundos')
save_dict_to_dataframes(fundo_data_b, parent_key='fundos')    


#####################################################################################################
#####################################################################################################
#####################################################################################################
#####################################################################################################
#####################################################################################################
# Função para salvar dicionários em DataFrames


def save_dict_to_dataframes(data, parent_key='', extra_fields=None):
    if extra_fields is None:
        extra_fields = {}

    if isinstance(data, dict):
        # Adicionar campos extras se existirem
        data.update(extra_fields)

        # Criar um DataFrame para o nível atual do dicionário
        df = pd.DataFrame([data])
        
        # Reordenar colunas para que os campos extras fiquem no início
        columns_order = [col for col in ["codigo_fundo", "nome_comercial_fundo", "codigo_classe", "nome_comercial_classe"] if col in df.columns] + [col for col in df.columns if col not in ["codigo_fundo", "nome_comercial_fundo", "codigo_classe", "nome_comercial_classe"]]
        df = df[columns_order]

        if parent_key in dataframes:
            # Se o DataFrame existir, fazer append dos novos dados
            pd.concat([dataframes[parent_key], df], ignore_index=True)
        else:
            # Caso contrário, criar o DataFrame
            dataframes[parent_key] = df
        #dataframes[parent_key] = df
        
        # Verificar se os campos extras estão presentes
        for key in ["codigo_fundo", "nome_comercial_fundo", "codigo_classe", "nome_comercial_classe"]:
            if key in data:
                extra_fields[key] = data[key]
        
        for key, value in data.items():
            new_key = f"{parent_key}_{key}" if parent_key else key
            save_dict_to_dataframes(value, new_key, extra_fields)
    elif isinstance(data, list):
        # Se o item for uma lista, armazenar todos os dicionários da lista em um mesmo DataFrame
        list_data = []
        for item in data:
            if isinstance(item, dict):
                item.update(extra_fields)
                list_data.append(item)
                save_dict_to_dataframes(item, parent_key, extra_fields)
            else:
                list_data.append({parent_key: item})
        df = pd.DataFrame(list_data)
        
        # Reordenar colunas para que os campos extras fiquem no início
        columns_order = [col for col in ["codigo_fundo", "nome_comercial_fundo", "codigo_classe", "nome_comercial_classe"] if col in df.columns] + [col for col in df.columns if col not in ["codigo_fundo", "nome_comercial_fundo", "codigo_classe", "nome_comercial_classe"]]
        df = df[columns_order]
        i = 0
        if parent_key in dataframes:
            # Se o DataFrame existir, fazer append dos novos dados
            dataframes[parent_key] = pd.concat([dataframes[parent_key], df], ignore_index=True)
            print(f'teste{i}')
            print(f'{parent_key}')
            i = i+1
        else:
            # Caso contrário, criar o DataFrame
            dataframes[parent_key] = df
            print(f'{parent_key}teste')
        
        
dataframes = {}
save_dict_to_dataframes(fundo_data, parent_key='fundos')
save_dict_to_dataframes(fundo_data_b, parent_key='fundos')


######################################################################################################

def save_dict_to_dataframes2(data, dataframes, parent_key='', extra_fields=None):
    if extra_fields is None:
        extra_fields = {}

    if isinstance(data, dict):
        # Adicionar campos extras se existirem
        data.update(extra_fields)

        # Criar um DataFrame para o nível atual do dicionário
        df = pd.DataFrame([data])
        
        # Reordenar colunas para que os campos extras fiquem no início
        columns_order = [col for col in ["codigo_fundo", "nome_comercial_fundo", "codigo_classe", "nome_comercial_classe"] if col in df.columns] + [col for col in df.columns if col not in ["codigo_fundo", "nome_comercial_fundo", "codigo_classe", "nome_comercial_classe"]]
        df = df[columns_order]
        
        # Append ao DataFrame existente ou criar um novo
        if parent_key in dataframes:
            dataframes[parent_key] = pd.concat([dataframes[parent_key], df], ignore_index=True)
        else:
            dataframes[parent_key] = df
        
        # Verificar se os campos extras estão presentes
        for key in ["codigo_fundo", "nome_comercial_fundo", "codigo_classe", "nome_comercial_classe"]:
            if key in data:
                extra_fields[key] = data[key]
        
        for key, value in data.items():
            new_key = f"{parent_key}_{key}" if parent_key else key
            save_dict_to_dataframes2(value, dataframes, new_key, extra_fields)
    elif isinstance(data, list):
        # Se o item for uma lista, armazenar todos os dicionários da lista em um mesmo DataFrame
        list_data = []
        for item in data:
            if isinstance(item, dict):
                item.update(extra_fields)
                list_data.append(item)
                save_dict_to_dataframes2(item, dataframes, parent_key, extra_fields)
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
            dataframes[parent_key] = df
            
            
dataframes = {}
save_dict_to_dataframes2(fundo_data_b,dataframes = dataframes, parent_key='fundos', extra_fields=None)            
