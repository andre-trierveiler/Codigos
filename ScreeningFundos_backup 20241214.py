# -*- coding: utf-8 -*-
"""
Created on Sat Dec 14 20:28:52 2024

@author: andre_trierveiler
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 00:28:06 2024

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
import pickle
from spyder_kernels.utils.iofuncs import load_dictionary
import itables.options as opt
from IPython.core.display import HTML
opt.maxBytes = 256 * 1024*70  # 256 KB

#python -m streamlit run C:\Users\andre_trierveiler\ScreeningFundos.py --server.address localhost --server.port 8510 

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


def limpa_df(df):
    cols_to_drop = [col for col in df.columns if df[col].apply(lambda x: isinstance(x, (dict, list))).any()]
    df = df.drop(columns=cols_to_drop)
    return df




def carregar_arquivos():
    st.session_state.df_fundo_geral = pd.read_csv('df_fundo_geral.csv', low_memory=False)
    st.session_state.df_sub_performance_g= pd.read_csv('df_sub_performance_g.csv', low_memory=False)
    st.session_state.df_sub_entrada_saida_g = pd.read_csv('df_sub_entrada_saida_g.csv', low_memory=False)
    st.session_state.df_subclasse_geral = pd.read_csv('df_subclasse_geral.csv', low_memory=False)
    st.session_state.df_classe_entrada_saida_g = pd.read_csv('df_classe_entrada_saida_g.csv', low_memory=False)
    st.session_state.df_classe_taxas_g  = pd.read_csv('df_classe_taxas_g.csv', low_memory=False)
    st.session_state.df_classe_geral  = pd.read_csv('df_classe_geral.csv', low_memory=False)
    st.session_state.df_cadastro  = pd.read_csv('df_cadastro.csv', low_memory=False)
    
    df_classe_prestadores_g = pd.read_csv('df_classe_prestadores_g.csv', low_memory=False)
    df_classe_entrada_saida_g = pd.read_csv('df_classe_entrada_saida_g.csv', low_memory=False)
    df_sub_taxas_g = pd.read_csv('df_sub_taxas_g.csv', low_memory=False)
    
    st.session_state.df_classe_geral = st.session_state.df_classe_geral.sort_values(by='tipo_anbima')

if 'df_sub_performance_g' not in st.session_state:
    carregar_arquivos()

# Menu Selecio Tipo Fundo
df_fundo_geral = st.session_state.df_fundo_geral
df_classe_geral = st.session_state.df_classe_geral 

lista_tipos = df_fundo_geral['tipo_fundo'].unique()
lista_fif = df_classe_geral[df_classe_geral['tipo_fundo'] == 'FIF']['tipo_anbima'].unique()


tipo_padrao = "OFFSHORE"  # Substitua pelo valor padrão desejado
fif_padrao ='Financeiro'

# Definir o valor padrão no menu suspenso
tipo = 'FIF'
if tipo_padrao in lista_tipos:
    tipo = st.sidebar.selectbox("Selecione o tipo de fundo:", list(lista_tipos), index=list(lista_tipos).index(tipo_padrao))
else:
    tipo = st.sidebar.selectbox("Selecione o tipo de fundo:", list(lista_tipos))

if tipo == 'FIF':
    pre_filtro = st.sidebar.selectbox("Pre-Filtro (apenas para FIF):", list(lista_fif))

#df_classe_geral = df_classe_geral[df_classe_geral['tipo_fundo'] == tipo]


minimos= st.sidebar.checkbox('Ocultar Valores Minimos',value=True)
complementar= st.sidebar.checkbox('Ocultar Perfil Complementar',value=True)
performance= st.sidebar.checkbox('Ocultar Taxa Perforamance',value=True)

multi= st.sidebar.checkbox('Seleções Multiplas',value=True)
multi_text = "multi" if multi else "single" 

cascade= st.sidebar.checkbox('Seleções Cascateadas',value=True, disabled=multi)
columns= 3

height = 5950
width = 900


# Links de Visualizações
st.sidebar.subheader('Páginas de Visualização')
pagina_selecionada = st.sidebar.selectbox('Selecione a Página', 
                                          ['Busca Fundos','Compartivo Fundos','Compartivo Fundos II', 'Comparativos de Classes',
                                           'Comparativos de Classes II',
                                           'Comparativos de Classes III',
                                           'Comparativos de Classes IV',
                                           
                                           'Prestadores Classes','Sufixos Classes','Taxas Classe', 'Taxas Entrada/Saída Classes',
                                           'Comparativos Subclasses', 'Taxas Subclasses ','Taxas Entrada/Saída Subclasses','Performance Subclasses ',
                                           'Valores Minimos Subclasses'])


def rearrange_columns(df, first_column_name):
    # Verificar se a coluna especificada existe no DataFrame
    if first_column_name not in df.columns:
        raise ValueError(f"A coluna '{first_column_name}' não existe no DataFrame.")
    
    # Reorganizar as colunas
    columns = [first_column_name] + [col for col in df.columns if col != first_column_name]
    df_return = df[columns]
    
    return df_return

def converter_colunas_data(df):
    for col in df.columns:
        if 'data' in col:
            df[col] = pd.to_datetime(df[col], format='ISO8601')
    return df




if pagina_selecionada == 'Busca Fundos':
    st.header("Busca Por Fundo Especifico")
    df_cadastro = st.session_state.df_cadastro
    df_lista =   df_cadastro[df_cadastro['tipo_fundo'] == tipo][['razao_social_fundo','codigo_fundo']]
    dict_lista = df_lista.to_dict(orient='records')
    fundos_lista = dict_lista
    
    # Criar dicionário para mapear nome comercial ao código do fundo
    nome_para_codigo = {fundo['razao_social_fundo']: fundo['codigo_fundo'] for fundo in fundos_lista}
    
    # Dropdown para selecionar o fundo (exibe o nome comercial)
    nome_selecionado = st.selectbox("Selecione o fundo:", list(nome_para_codigo.keys()))
    
    # Obter o codigo_fundo correspondente ao nome selecionado
    codigo_fundo = nome_para_codigo[nome_selecionado]

    # Marca se quer ocular nulos
    oculta_nulos= st.checkbox('Ocultar Campos Nulos')
    if oculta_nulos == True:
        lista_nd = ['none', 'não disponível', 'nao disponível', 'não se aplica', 'nao se aplica', None]
    else:
        lista_nd = ['aaaaaaaaaaaaaaaaaaaasdasd']   
        
    #codigo_fundo = 'F0000127671'
    fundos_det_http = f'{url}feed/fundos/v2/fundos/{codigo_fundo}'
    fundos_det = requests.get(fundos_det_http, headers=headers)
    try:
        headers = conectar('wRGlvlj1bOW3', 'l4riAuRd0CUL','wRGlvlj1bOW3:l4riAuRd0CUL', url)
        fundos_det_json = fundos_det.json()
    except ValueError:
        print('Erro')
        print(codigo_fundo)
        headers = conectar('wRGlvlj1bOW3', 'l4riAuRd0CUL','wRGlvlj1bOW3:l4riAuRd0CUL', url)
    #dados_cadastrais = pd.json_normalize(fundos_det_json['dados-cadastrais'])
    fundo_det_cadastro = pd.json_normalize(fundos_det_json)
    #json_cadastro_total = json_cadastro_total.append(fundos_det_json)

    fundo_data = fundos_det_json
    
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
    
    def exibir_informacoes_dict2(dicionario):
        for chave, valor in dicionario.items():
            if valor in lista_nd:
                valor = "Não disponível"
            if isinstance(valor,  list):
                st.subheader('Teste')
                #exibir_informacoes_texto(pd.DataFrame(valor))
                st.table(pd.DataFrame(valor))
            else:
                st.write(f"**{chave}:** {valor}".replace('_', ' ').title())
        st.write("---")    
        
    def exibir_informacoes_dict(dicionario, exibir_como_tabela=['prestadores_classe','faixas_escalonamento']):
            
        for chave, valor in dicionario.items():
            # Ignorar valores nulos ou irrelevantes
            if valor in lista_nd or str(valor).lower() in lista_nd:
                continue
            
            if not isinstance(valor, (list, dict)):
                st.write(f"**{chave}:** {valor}".replace('_', ' ').title())
            
        st.write("---")
        
        for chave, valor in dicionario.items():
            # Ignorar valores nulos ou irrelevantes
            if valor in lista_nd or str(valor).lower() in lista_nd:
                continue
            # Se o valor for uma lista e deve ser exibido como tabela
            if isinstance(valor, list) and chave in exibir_como_tabela:
                if len(valor) > 0:
                    st.subheader(f"{chave} (Tabela)".replace('_', ' ').title())
                    st.table(pd.DataFrame(valor))  # Exibir a lista como tabela usando DataFrame
    
            # Se o valor for uma lista e não deve ser exibido como tabela
            elif isinstance(valor, list):
                if len(valor) > 0:
                    st.subheader(f"{chave} (Lista)".replace('_', ' ').title())
                    for item in valor:
                        if isinstance(item, dict):
                            #continue
                            exibir_informacoes_dict(item, exibir_como_tabela=['faixas_escalonamento'])  # Chamada recursiva se o item for um dicionário
                        else:
                            st.write(f"- {item}".replace('_', ' '))
    
            # Se o valor for um dicionário
            elif isinstance(valor, dict):
                st.subheader(f"{chave} (Detalhes)".replace('_', ' ').title())
                exibir_informacoes_dict(valor, exibir_como_tabela)  # Chamada recursiva para o dicionário
    
            # Caso contrário, exibir como chave-valor
            else:
                continue
        #st.write("---")
    
            
    
    # Função para exibir as subclasses em expanders próprios
    def exibir_detalhes_subclasse(subclasse_nome, subclasse_info):
        with st.expander(f"Subclasse: {subclasse_nome}"):
            st.subheader("Informações da Subclasse")
            exibir_informacoes_texto(subclasse_info)
            
        
            if row['prestadores_subclasse'] != None:     
                st.subheader("Prestadores da Subclasse")
                for prestador in row['prestadores_subclasse']:
                    exibir_informacoes_dict(prestador)
            
            if row['taxas_subclasse'] != None:        
                st.subheader("Taxas da Subclasse")
                for taxa in row['taxas_subclasse']:
                    exibir_informacoes_dict(taxa)            
                
    
            if row['taxas_entrada_saida_subclasse'] != None:    
                st.subheader("Taxas Entrada/Saída Subclasse")
                for taxa_entrada_saida in row['taxas_entrada_saida_subclasse']:
                    exibir_informacoes_dict(taxa_entrada_saida)
                
            
            if row['taxa_performance'] != None:
                st.subheader("Taxas Performance Subclasse")
                for taxa_performance in row['taxa_performance']:
                    exibir_informacoes_dict(taxa_performance)        
                    if row['taxa_performance']['detalhes'] != None:
                        for detalhe_performance in row['taxa_performance']['detalhes']:
                            exibir_informacoes_dict(detalhe_performance)  
    
    # Função para fazer o download do PDF com headers de autenticação
    def baixar_pdf(url, headers):
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            # O conteúdo do PDF está no formato binário
            return response.content
        else:
            st.error(f"Erro ao acessar o PDF. Status Code: {response.status_code}")
            return None
    
    # Normalizar os dados principais do JSON
    df_fundo = pd.json_normalize(fundo_data, sep='_')
    prestadores_fundo_df = pd.json_normalize(fundo_data, record_path=['prestadores_fundo'], meta=['codigo_fundo'], sep=' : ')
    documentos_df =  pd.json_normalize(fundo_data, record_path=['documentos'], meta=['codigo_fundo'], sep=' : ')
    classes_df = pd.json_normalize(fundo_data, record_path=['classes'], meta=['codigo_fundo'], sep=' : ')
    indices_benchmark_df = pd.json_normalize(fundo_data, record_path=['classes', 'indices_benchmark'], meta=['codigo_fundo'], sep=' : ')
    sufixos_df = pd.json_normalize(fundo_data, record_path=['classes', 'sufixos'], meta=['codigo_fundo'], sep=' : ')
    subclasses_df = pd.json_normalize(fundo_data, record_path=['classes', 'subclasses'], meta=['codigo_fundo'], sep=' : ')
    
    # Definir o título principal com base no valor de "nome_comercial_fundo"
    nome_comercial_fundo = df_fundo['nome_comercial_fundo'][0]  # Pegando o valor do nome_comercial_fundo
    st.title(f"{nome_comercial_fundo}")
    
    # Exibir "Dados do Fundo" e "Prestadores do Fundo" dentro de expanders
    with st.expander("Informações do Fundo"):
        exibir_informacoes_texto(df_fundo)
    
    with st.expander("Prestadores do Fundo"):
        exibir_informacoes_texto(prestadores_fundo_df)
    
    with st.expander("Documentos do Fundo"):
        exibir_informacoes_texto(documentos_df)
        if hasattr(documentos_df, 'url'):
            pdf_url = documentos_df.url[0]
            conteudo_pdf = baixar_pdf(pdf_url, headers)
        
            if conteudo_pdf:
                st.download_button(label="Baixar Regulamento PDF", data=conteudo_pdf, file_name=f'Regulamento_Fundo_{codigo_fundo}.pdf', mime='application/pdf')
            if conteudo_pdf:
            # Gerar um link para abrir o PDF em uma nova aba
                pdf_display = f'<a href="{pdf_url}" target="_blank">Abrir Regulamento do Fundo em outra aba</a>'
                st.markdown(pdf_display, unsafe_allow_html=True)
         
    # Exibir as informações de cada classe em um único expander
    
    st.header("Classes")
    
            
    def exibir_detalhes_classe3(classe_nome, classe):
        with st.expander(f"Classe: {classe_nome}"):
            st.subheader("Informações da Classe")
            classes_df = pd.json_normalize(classe, max_level=0)
            exibir_informacoes_texto(classes_df)
            
            
            #taxa_performance = classe['taxa_performance']
            if classe['perfil_complementar'] != None:    
                st.subheader('Perfil Complementar')
                exibir_informacoes_dict(classe['perfil_complementar']) 
            
            if classe['indices_benchmark'] != None:          
                st.subheader("Benchmarks da Classe")
                for indices_benchmark in classe['indices_benchmark']:
                    exibir_informacoes_dict(indices_benchmark)
            
            if classe['sufixos'] != None:          
                st.subheader("Sufixos da Classe")
                for sufixos in classe['sufixos']:
                    exibir_informacoes_dict(sufixos)
    
            if classe['taxas_classe'] != None:          
                st.subheader("Taxas da Classe")
                for taxas_classe in classe['taxas_classe']:
                    exibir_informacoes_dict(taxas_classe)
    
            if classe['taxa_performance'] != None:    
                st.subheader('Taxa Performance')
                exibir_informacoes_dict(classe['taxa_performance']) 
                
           
            if classe['valores_minimos_movimentacao_classe'] != None:    
                st.subheader('Valores Mínimos Movimentação')
                exibir_informacoes_dict(classe['valores_minimos_movimentacao_classe']) 
                 
                
            if classe['taxas_entrada_saida_classe'] != None:          
                st.subheader("Taxas Entrada/Saída da Classe")
                for taxas_entrada_saida_classe in classe['taxas_entrada_saida_classe']:
                    exibir_informacoes_dict(taxas_entrada_saida_classe)
    
    
            if classe['prestadores_classe'] != None:          
                st.subheader("Prestadores da Classe")
                st.table(classe['prestadores_classe'])
                #for prestadores_classe in classe['prestadores_classe']:
                    #exibir_informacoes_dict(prestadores_classe) 
                 #   st.table(pd.DataFrame(prestadores_classe))
                    
    
    for classe in fundo_data['classes']:
        classe_nome = classe['nome_comercial_classe']
        exibir_detalhes_classe3(classe_nome, classe)
    
    
    # Exibir as subclasses em expanders próprios
     
    st.header("Subclasses")
    for index, row in subclasses_df.iterrows():
        subclasse_nome = row['nome_comercial_subclasse']
        subclasse_info = pd.DataFrame([row])  # Informações da subclasse
    
        # Exibir todas as informações da subclasse em um expander próprio
        exibir_detalhes_subclasse(subclasse_nome, subclasse_info)
        #mostrar_informacoes_subclasse(row)
        #for taxa in row['taxas_subclasse']:
        #    taxa = subclasse_info
        #    exibir_detalhes_subclasse(subclasse_nome, subclasse_info)
    # Rodando o aplicativo: Para rodar esse código, execute 'streamlit run <nome_arquivo>.py'
    
    
    
    
    st.header("TESTEEEEE")
    for classe in fundo_data['classes']:
        classe_nome = classe['nome_comercial_classe']
        with st.expander(f"Classe: {classe_nome} - teste"):
             st.subheader("Informações da Classe")
             exibir_informacoes_dict(classe, exibir_como_tabela=['prestadores_classe','faixas_escalonamento'])
    for classe in fundo_data['classes']:
        if classe['subclasses'] != None:   
            for subclasse in classe['subclasses']:
                if subclasse['nome_comercial_subclasse'] != None:   
                    subclasse_nome = subclasse['nome_comercial_subclasse']
                    with st.expander(f"SubClasse: {subclasse_nome} - teste"):
                         st.subheader("Informações da SubClasse")
                         exibir_informacoes_dict(subclasse, exibir_como_tabela=['prestadores_subclasse','faixas_escalonamento'])    







# Exibir Páginas de Visualização separadamente
elif pagina_selecionada == 'Compartivo Fundos':
    st.header("Comparativos  Fundos")
      # Personalize a exibição
    df_fundo_geral = st.session_state.df_fundo_geral
    df_fundo_geral = df_fundo_geral.loc[:, ~df_fundo_geral.columns.str.contains('data')]
    df_fundo_geral = rearrange_columns(df_fundo_geral, 'nome_comercial_fundo')
    opt.column_filters = 'footer'
    opt.fixedColumns = {"leftColumns": 3}
    opt.classes = ["display", "nowrap"]

    html_table = to_html_datatable(
            df_fundo_geral,
            #dom="Plfrtip",
            layout={ "top1": "searchPanes", "top2": "searchBuilder"},
            
            select={"style": "multi"},
            searchPanes={"layout": f"columns-{columns}", "cascadePanes": cascade,"dtOpts": {"select": {"style": multi_text}}, "collapsed": True }, # {"style": "single"}
            options={"fixedColumns": {"leftColumns": 1}, "scrollX": True,"scrollY": "400px","pageLength": 50, "columnDefs": {"width": "150px", "targets": 0},
                     "dom": 'Bfrtip',  "buttons": ["copyHtml5", "csvHtml5", "excelHtml5"]},
            buttons=["copyHtml5", "csvHtml5", "excelHtml5","pageLength"],
        )   # adjust manually
    
    # Adicionando estilo CSS
    html_table = f"""
    <style>
        body {{
                font-family: Segoe UI, sans-serif;
                font-size: 12px;
                color: #333333;  # Cinza escuro
            }}
        table {{
            font-family: Segoe UI, sans-serif;
            font-size: 10px;
            "color": "#333333";
            width: 100%
        }}
    </style>
    {html_table}
    """
    html(html_table,height=height)

        
if pagina_selecionada == 'Compartivo Fundos II':   
    st.header("Comparativos  Fundos II")
    df_fundo_geral = st.session_state.df_fundo_geral
    df_fundo_geral = rearrange_columns(df_fundo_geral, 'nome_comercial_fundo')
    opt.column_filters = 'footer'
    opt.fixedColumns = {"leftColumns": 3}
    opt.classes = ["display", "nowrap"]

    html_table = to_html_datatable(
            df_fundo_geral,
            #dom="Plfrtip",
            layout={"top1": "searchBuilder"},
            select=True,
            options={"fixedColumns": {"leftColumns": 1}, "scrollX": True,"scrollY": "400px","pageLength": 25, "columnDefs": {"width": "150px", "targets": 0},
                     "dom": 'Bfrtip',  "buttons": ["copyHtml5", "csvHtml5", "excelHtml5"]},
            buttons=["copyHtml5", "csvHtml5", "excelHtml5","pageLength"],
        )   # adjust manually
    
    # Adicionando estilo CSS
    html_table = f"""
    <style>
        body {{
                font-family: Segoe UI, sans-serif;
                font-size: 12px;
                color: #333333;  # Cinza escuro
            }}
        table {{
            font-family: Segoe UI, sans-serif;
            font-size: 10px;
            "color": "#333333";
            width: 100%
        }}
    </style>
    {html_table}
    """
    html(html_table,height=height)

    
    # Exibir a tabela no Jupyter Notebook

elif pagina_selecionada == 'Comparativos de Classes':
    st.header("Comparativos de Classes")
      # Personalize a exibição
    df_classe_geral = st.session_state.df_classe_geral
    df_classe_geral = df_classe_geral[df_classe_geral['tipo_fundo'] == tipo]
    if tipo == 'FIF':
        df_classe_geral = df_classe_geral[df_classe_geral['tipo_anbima'] == pre_filtro]
    df_classe_geral = rearrange_columns(df_classe_geral, 'nome_comercial_classe')
    df_classe_geral = df_classe_geral.loc[:, ~df_classe_geral.columns.str.contains('data')]
    #df_classe_geral = df_classe_geral.drop(columns=['taxa_adicionais'])
    df_classe_geral = df_classe_geral.drop(columns=['taxa_adicionais','taxa_performance.informacoes_adicionais'])
    df_classe_geral = df_classe_geral.loc[:, ~df_classe_geral.columns.str.match('^Unnamed')]
    
    if minimos == True:
        df_classe_geral = df_classe_geral.loc[:, ~df_classe_geral.columns.str.contains('valores_minimos_movimentacao')]
    if complementar == True:
        df_classe_geral = df_classe_geral.loc[:, ~df_classe_geral.columns.str.contains('perfil_complementar.')]
    if performance == True:
        df_classe_geral = df_classe_geral.loc[:, ~df_classe_geral.columns.str.contains('taxa_performance.')]
        
      # Personalize a exibição
    opt.column_filters = 'footer'
    opt.fixedColumns = {"leftColumns": 3}
    opt.classes = ["display", "nowrap"]

    html_table = to_html_datatable(
            df_classe_geral,
            #dom="Plfrtip",
            layout={ "top1": "searchPanes", "top2": "searchBuilder"},
            
            select={"style": "multi"},
            searchPanes={"layout": f"columns-{columns}", "cascadePanes": cascade,"dtOpts": {"select": {"style": multi_text}}, "collapsed": True ,
                         "columns": [i for i, col in enumerate(df_classe_geral.columns) if col not in ['taxa_adicionais','taxa_performance.informacoes_adicionais']]
                         }, # {"style": "single"}
            options={"fixedColumns": {"leftColumns": 1}, "scrollX": True,"scrollY": "400px","pageLength": 50, "columnDefs": {"width": "10px", "targets": 0},
                     "dom": 'Bfrtip',  "buttons": ["copyHtml5", "csvHtml5", "excelHtml5"]},
            buttons=["copyHtml5", "csvHtml5", "excelHtml5","pageLength"],
        )   # adjust manually
    
    # Adicionando estilo CSS
    html_table = f"""
    <style>
        body {{
                font-family: Segoe UI, sans-serif;
                font-size: 12px;
                color: #333333;  # Cinza escuro
            }}
        table {{
            font-family: Segoe UI, sans-serif;
            font-size: 10px;
            "color": "#333333";
            width: 100%
        }}
    </style>
    {html_table}
    """
    html(html_table,height=height)
    
    
elif pagina_selecionada == 'Comparativos de Classes II':
    st.header("Comparativos de Classes")
      # Personalize a exibição
    df_classe_geral = st.session_state.df_classe_geral
    df_classe_geral = converter_colunas_data(df_classe_geral)
    #df_classe_geral = df_classe_geral.loc[:, ~df_classe_geral.columns.str.contains('data')]
    df_classe_geral = rearrange_columns(df_classe_geral, 'nome_comercial_classe')
    
    #df_classe_geral = df_classe_geral[df_classe_geral['tipo_fundo'] == tipo]
    #if tipo == 'FIF':
    #    df_classe_geral = df_classe_geral[df_classe_geral['tipo_anbima'] == pre_filtro]  
    #if minimos == True:
    #    df_classe_geral = df_classe_geral.loc[:, ~df_classe_geral.columns.str.contains('valores_minimos_movimentacao')]
    #if complementar == True:
    #    df_classe_geral = df_classe_geral.loc[:, ~df_classe_geral.columns.str.contains('perfil_complementar.')]
    #if performance == True:
    #    df_classe_geral = df_classe_geral.loc[:, ~df_classe_geral.columns.str.contains('taxa_performance.')]
        
      # Personalize a exibição
    opt.column_filters = 'footer'
    opt.fixedColumns = {"leftColumns": 3}
    opt.classes = ["display", "nowrap"]

    html_table = to_html_datatable(
            df_classe_geral,
            #dom="Plfrtip",
            layout={ "top1": "searchBuilder"},
            
            select={"style": "multi"},
            options={"fixedColumns": {"leftColumns": 1}, "scrollX": True,"scrollY": "400px","pageLength": 50, "columnDefs": {"width": "10px", "targets": 0},
                     "dom": 'Bfrtip',  "buttons": ["copyHtml5", "csvHtml5", "excelHtml5"]},
            buttons=["copyHtml5", "csvHtml5", "excelHtml5","pageLength"],
        )   # adjust manually
    
    # Adicionando estilo CSS
    html_table = f"""
    <style>
        body {{
                font-family: Segoe UI, sans-serif;
                font-size: 12px;
                color: #333333;  # Cinza escuro
            }}
        table {{
            font-family: Segoe UI, sans-serif;
            font-size: 10px;
            "color": "#333333";
            width: 100%
        }}
    </style>
    {html_table}
    """
    html(html_table,height=height)
    
    
    
elif pagina_selecionada == 'Comparativos de Classes III':
    st.header("Comparativos de Classes")
      # Personalize a exibição

    df_classe_geral = st.session_state.df_classe_geral
    df_classe_geral = rearrange_columns(df_classe_geral, 'nome_comercial_classe')
    gb = GridOptionsBuilder.from_dataframe(df_classe_geral)
    gb.configure_column('nome_comercial_classe', pinned='left')
    gb.configure_side_bar()
    gb.configure_pagination(enabled = True)
    gb.configure_default_column(editable=False, groupable=True, filterable=True)
    for col in df_classe_geral.select_dtypes(include='object').columns:
        gb.configure_column(col, filter='agTextColumnFilter')
    gb.configure_selection(selection_mode='multiple')
    #gb.configure_columns(list('abcde'), editable=True)
    goo = gb.build()
    ag = AgGrid(
        df_classe_geral, 
        gridOptions=goo, 
        fit_columns_on_grid_load=False
    )
    
    
elif pagina_selecionada == 'Comparativos de Classes IV':
    st.header("Comparativos de Classes")
      # Personalize a exibição
    #df_fundo_geral = st.session_state.df_fundo_geral
    #df_fundo_classe_g = st.session_state.df_fundo_classe_g
    #df_fundo_taxa_g = st.session_state.df_fundo_taxa_g
    #df_classe_geral = st.session_state.df_classe_geral
    
    df_classe_geral = df_classe_geral.loc[:, ~df_classe_geral.columns.str.contains('data')]
    df_classe_geral = df_classe_geral.drop(columns=['taxa_adicionais'])
    #df_classe_geral.background_gradient(axis=None, cmap="YlOrRd")
    html(
        to_html_datatable(
            df_classe_geral,select=True,
            layout={"top1": "searchBuilder"},
            buttons=["copyHtml5", "csvHtml5", "excelHtml5"]
        ),height=10060,width=1200,   # adjust manually
    )
    
    
    
elif pagina_selecionada == 'Prestadores Classes':
    st.header("Comparativos de Classes")
    
    df_classe_prestadores_g = st.session_state.df_classe_prestadores_g
    df_classe_prestadores_g= rearrange_columns(df_classe_prestadores_g, 'nome_comercial_classe')
    gb = GridOptionsBuilder.from_dataframe(df_classe_geral)
    gb.configure_column('nome_comercial_classe', pinned='left')
    gb.configure_side_bar()
    gb.configure_pagination(enabled = True)
    gb.configure_default_column(editable=False, groupable=True, filterable=True)
    for col in df_classe_prestadores_g.select_dtypes(include='object').columns:
        gb.configure_column(col, filter='agTextColumnFilter')
    gb.configure_selection(selection_mode='multiple')
    #gb.configure_columns(list('abcde'), editable=True)
    goo = gb.build()
    ag = AgGrid(
        df_classe_prestadores_g, 
        gridOptions=goo, 
        fit_columns_on_grid_load=False
    )
    
    
elif pagina_selecionada == 'Taxas Classes':
    st.header("Comparativos de Classes")
    
    df_classe_taxas_g= st.session_state.df_classe_taxas_g
    df_classe_taxas_g= rearrange_columns(df_classe_taxas_g, 'nome_comercial_classe')
    gb = GridOptionsBuilder.from_dataframe(df_classe_taxas_g)
    gb.configure_column('nome_comercial_classe', pinned='left')
    gb.configure_side_bar()
    gb.configure_pagination(enabled = True)
    gb.configure_default_column(editable=False, groupable=True, filterable=True)
    for col in df_classe_taxas_g.select_dtypes(include='object').columns:
        gb.configure_column(col, filter='agTextColumnFilter')
    gb.configure_selection(selection_mode='multiple')
    #gb.configure_columns(list('abcde'), editable=True)
    goo = gb.build()
    ag = AgGrid(
        df_classe_taxas_g, 
        gridOptions=goo, 
        fit_columns_on_grid_load=False
    )

    
#df_fundos_det_cadastro = limpa_df(df_fundos_det_cadastro)
#df_classes_taxa	= limpa_df(df_classes_taxa)
#df_classes_sufixos	= limpa_df(df_classes_sufixos)
#df_classes_indices_benchmark	= limpa_df(df_classes_indices_benchmark)
#df_fundos_classes = limpa_df(df_fundos_classes)
#df_subclasses = limpa_df(df_subclasses)
#df_subclasses_performance = limpa_df(df_subclasses_performance)
#df_subclasses_taxas = limpa_df(df_subclasses_taxas)
#df_subclasses_valores_minimos = limpa_df(df_subclasses_valores_minimos)
#df_subclasses_taxas_extrada_saida  = limpa_df(df_subclasses_taxas_extrada_saida)


    ###########################################################
    # Carregar o arquivo JSON (adicione o caminho correto do arquivo)
    #file_path = 'fundo.json'
    #with open(file_path, 'r', encoding='utf-8') as file:
#    fundo_data = json.load(file)
    

    







