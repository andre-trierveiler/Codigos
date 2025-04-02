# -*- coding: utf-8 -*-
"""
Created on Sat Feb  8 14:22:08 2025

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
autaliza_cadastro = 0
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




lista_tipos = df_cadastro['tipo_fundo'].unique()
tipo_padrao = "FIF"  # Substitua pelo valor padrão desejado

# Definir o valor padrão no menu suspenso
if tipo_padrao in lista_tipos:
    tipo = st.selectbox("Selecione o tipo de fundo:", list(lista_tipos), index=list(lista_tipos).index(tipo_padrao))
else:
    tipo = st.selectbox("Selecione o tipo de fundo:", list(lista_tipos))

df_lista =   df_cadastro[df_cadastro['tipo_fundo'] == tipo][['razao_social_fundo','codigo_fundo']]
dict_lista = df_lista.to_dict(orient='records')
fundos_lista = dict_lista

# Criar dicionário para mapear nome comercial ao código do fundo
nome_para_codigo = {fundo['razao_social_fundo']: fundo['codigo_fundo'] for fundo in fundos_lista}

# Dropdown para selecionar o fundo (exibe o nome comercial)
nome_selecionado = st.selectbox("Selecione o fundo:", list(nome_para_codigo.keys()))

# Obter o codigo_fundo correspondente ao nome selecionado
codigo_fundo = nome_para_codigo[nome_selecionado]


fundos_det_http = f'{url}feed/fundos/v2/fundos/{codigo_fundo}'
fundos_det = requests.get(fundos_det_http, headers=headers3)



try:
    headers3 = conectar('wRGlvlj1bOW3', 'l4riAuRd0CUL','wRGlvlj1bOW3:l4riAuRd0CUL', url)
    fundos_det_json = fundos_det.json()
except ValueError:
    print('Erro')
    print(codigo_fundo)
    headers3 = conectar('wRGlvlj1bOW3', 'l4riAuRd0CUL','wRGlvlj1bOW3:l4riAuRd0CUL', url)

fundo_det_cadastro = pd.json_normalize(fundos_det_json)

fundo_data = fundos_det_json

# Marca se quer ocular nulos
oculta_nulos= st.checkbox('Ocultar Campos Nulos')
if oculta_nulos == True:
    lista_nd = ['none', 'não disponível', 'nao disponível', 'não se aplica', 'nao se aplica', None]
else:
    lista_nd = ['aaaaaaaaaaaaaaaaaaaasdasd']   
    
# Função para exibir informações simples (nomes de campos em negrito) em formato de texto
def exibir_informacoes_texto(dataframe):
    for index, row in dataframe.iterrows():
        for col in dataframe.columns:
            if not isinstance(row[col], (list, dict)):  # Exibir apenas campos simples
               if row[col] in lista_nd or str(row[col]).lower() in lista_nd:
                   if oculta_nulos == True:
                    continue
               st.write(f"**{col}**: {row[col]}".replace('_', ' ').title())  # Nome do campo em negrito
        st.write("---")
 
    
def exibir_informacoes_dict(dicionario, exibir_como_tabela=['nd']):
    if isinstance(dicionario, dict):
        teste = pd.json_normalize(dicionario)
        st.table(teste)
        
    #for chave, valor in dicionario.items():
    #    
    #    if not isinstance(valor, (list, dict)):
    #        #st.write(f"**{chave}:** {valor}".replace('_', ' ').title())
    #st.write("***************************")
    
    for chave, valor in dicionario.items():
        # Se o valor for uma lista e deve ser exibido como tabela
        if isinstance(valor, list):
                st.subheader(f"{chave} (Tabela)".replace('_', ' ').title())
                st.table(pd.DataFrame(valor))  # Exibir a lista como tabela usando DataFrame

        elif isinstance(valor, dict):
            st.subheader(f"{chave} (Detalhes)".replace('_', ' ').title())
            exibir_informacoes_dict(valor, exibir_como_tabela)  # Chamada recursiva para o dicionário

        # Caso contrário, exibir como chave-valor
        else:
            continue
        
  
        
nome_comercial_fundo = fundo_data['nome_comercial_fundo'][0]  # Pegando o valor do nome_comercial_fundo
st.title(f"{nome_comercial_fundo}")
   



st.header("Classes e SubClasses")
for classe in fundo_data['classes']:
    classe_nome = classe['nome_comercial_classe']
    with st.expander(f"Classe: {classe_nome} - teste"):
         st.subheader("Informações da Classe")
         exibir_informacoes_dict(classe, exibir_como_tabela=['prestadores_classe','faixas_escalonamento','taxas_entrada_saida_classe'])
for classe in fundo_data['classes']:
    if classe['subclasses'] != None:   
        for subclasse in classe['subclasses']:
            if subclasse['nome_comercial_subclasse'] != None:   
                subclasse_nome = subclasse['nome_comercial_subclasse']
                with st.expander(f"SubClasse: {subclasse_nome} - teste"):
                     st.subheader("Informações da SubClasse")
                     exibir_informacoes_dict(subclasse, exibir_como_tabela=['prestadores_subclasse','faixas_escalonamento','taxas_entrada_saida_subclasse'])

    


#############################################################################################################
#############################################################################################################
#############################################################################################################
#############################################################################################################
#############################################################################################################
#############################################################################################################
#############################################################################################################
#############################################################################################################
#############################################################################################################
     
dataframes = {}
def save_dict_to_dataframes(data, parent_key=''):
    if isinstance(data, dict):
        # Criar um DataFrame para o nível atual do dicionário
        df = pd.DataFrame([data])
        dataframes[parent_key] = df
        
        for key, value in data.items():
            new_key = f"{parent_key}_{key}" if parent_key else key
            save_dict_to_dataframes(value, new_key)
    elif isinstance(data, list):
        # Se o item for uma lista, armazenar todos os dicionários da lista em um mesmo DataFrame
        list_data = []
        for item in data:
            if isinstance(item, dict):
                list_data.append(item)
            else:
                list_data.append({parent_key: item})
        df = pd.DataFrame(list_data)
        dataframes[parent_key] = df
   
dataframes = {}  
save_dict_to_dataframes(fundo_data) 



def dict_df(dicionario, parent_key=''):
    if isinstance(dicionario, dict):
        #teste = pd.json_normalize(dicionario)
        df = pd.DataFrame([dicionario])
        dataframes[parent_key] = df
        
    
    #for chave, valor in dicionario.items():
    #    # Se o valor for uma lista e deve ser exibido como tabela
    #    if isinstance(valor, list):
    #                list_data = []
    #                for item in valor:
    #                    if isinstance(item, dict):
    #                        list_data.append(item)
    #                    else:
    #                        list_data.append({parent_key: item})
    #                        
    #                df = pd.DataFrame(list_data)
    #                dataframes[parent_key] = df
    #                dict(valor)
    #    
    #    elif isinstance(valor, dict):
    #        dict(valor, parent_key='')
    #
    #    # Caso contrário, exibir como chave-valor
    #    else:
    #        continue
        
dataframes = {}  
dict_df(fundo_data, 'Fundo')        

def dict_to_dataframes(dicionario, parent_key='Fundos', level=1):      
    if isinstance(dicionario, dict) and level==1:
        # Criar um DataFrame para o nível atual do dicionário
        df = pd.DataFrame([dicionario])
        dataframes[parent_key] = df
              
        for chave, valor in dicionario.items():
            nova_chave = f"{parent_key}_{chave}" if parent_key else chave
            save_dict_to_dataframes(valor, nova_chave)
        
    if isinstance(dicionario, list):
            list_data = []
            for item in valor:
                if isinstance(item, dict):
                    list_data.append(item)
                else:
                    list_data.append({parent_key: item})
            df = pd.DataFrame(list_data)
            dataframes[parent_key] = df     
            #i=1
            #for item in valor:
            #    i=1+1
            #    if isinstance(item, dict):
            #       dict_to_dataframes(item, parent_key='teste' + "_" + str(i), level=2)          
                    
#dataframes = {}  
#dict_to_dataframes(fundo_data, level=1)






