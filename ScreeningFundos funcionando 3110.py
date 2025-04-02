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



#def load_spydata(file):
#    with open(file, 'rb') as f:
#        data = pickle.load(f)
#    return load_dictionary(data)[0]
#file_path = 'Dataset_Fundos_175_ANBIMAFEED.spydata'

#data = load_spydata(file_path)

#warnings.filterwarnings("ignore", message="Warning .spydata files can contain malicious code!")
#def load_spydata(file):
#    with open(file, 'rb') as f:
#        try:
##            data = pickle.load(f)
#            return load_dictionary(data)[0]
#        except pickle.UnpicklingError:
#            st.error("Erro ao deserializar o arquivo. O arquivo pode estar corrompido.")
#            return None

#file_path = 'Dataset_Fundos_175_ANBIMAFEED.spydata'
#data = load_spydata(file_path)

#if 'df_classe_geral' in data:
#    df = data['nome_do_dataframe']

        
#st.session_state.df_fundo_geral = pd.read_csv('df_fundo_geral.csv', low_memory=False)
#df_sub_performance_g = pd.read_csv('df_sub_performance_g.csv', low_memory=False)
#df_sub_entrada_saida_g = pd.read_csv('df_sub_entrada_saida_g.csv', low_memory=False)
#df_subclasse_geral = pd.read_csv('df_subclasse_geral.csv', low_memory=False)
#df_classe_entrada_saida_g = pd.read_csv('df_classe_entrada_saida_g.csv', low_memory=False)
#df_classe_taxas_g = pd.read_csv('df_classe_taxas_g.csv', low_memory=False)
#df_classe_geral = pd.read_csv('df_classe_geral.csv', low_memory=False)



def carregar_arquivos():
    st.session_state.df_fundo_geral = pd.read_csv('df_fundo_geral.csv', low_memory=False)
    st.session_state.df_sub_performance_g= pd.read_csv('df_sub_performance_g.csv', low_memory=False)
    st.session_state.df_sub_entrada_saida_g = pd.read_csv('df_sub_entrada_saida_g.csv', low_memory=False)
    st.session_state.df_subclasse_geral = pd.read_csv('df_subclasse_geral.csv', low_memory=False)
    st.session_state.df_classe_entrada_saida_g = pd.read_csv('df_classe_entrada_saida_g.csv', low_memory=False)
    st.session_state.df_classe_taxas_g  = pd.read_csv('df_classe_taxas_g.csv', low_memory=False)
    st.session_state.df_classe_geral  = pd.read_csv('df_classe_geral.csv', low_memory=False)
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
                                          ['Busca Fundos''Compartivo Fundos','Compartivo Fundos II', 'Comparativos de Classes',
                                           'Comparativos de Classes II',
                                           'Comparativos de Classes III',
                                           'Comparativos de Classes IV',
                                           'Comparativos Subclasses',
                                           'Prestadores Classes','Sufixos Classes','Taxas Classe', 'Taxas Entrada/Saída Classes',
                                           'Prestadores Fundos','Sufixos Fundos',
                                           'Pertadores Subclasses','Taxas Subclasses ','Taxas Entrada/Saída Subclasses','Performance Subclasses ',
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

# Exibir Páginas de Visualização separadamente
if pagina_selecionada == 'Compartivo Fundos':
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


    
#DATAFRAMES PARA CADASTRO
select = """  SELECT fundo.*
    , adm.razao_social as administrador
    , gestor.razao_social as gestor

    FROM df_fundos_det_cadastro fundo
    left join df_fundos_prestadores adm on fundo.codigo_fundo = adm.codigo_fundo and 	adm.codigo_tipo_prestador = 'ADMINISTRADOR'
    left join df_fundos_prestadores gestor on fundo.codigo_fundo = gestor.codigo_fundo and 	gestor.codigo_tipo_prestador = 'GESTOR'
   """
#df_fundo_geral = sqldf(select, locals())    
#df_fundo_geral	= limpa_df(df_fundo_geral)

select = """  
    SELECT
     classe.codigo_classe
    , classe.identificador_classe
    , classe.nome_comercial_classe
    , classe.data_inicio_atividade_classe
    , classe.tributacao_perseguida
    , classe.alavancado
    , classe.credito_privado
    , classe.percentual_permitido_credito_privado
    , classe.investimento_exterior
    , classe.percentual_permitido_investimento_exterior
    , classe.foco_atuacao
    , classe.fundo_esg
    , classe.forma_condominio
    , classe.entidade_investimento_fins_tributarios
    , classe.infraestrutura
    , classe.responsabilidade_limitada
    , classe.categoria_cvm
    , classe.composicao
    , classe.tipo_anbima
    , classe.nivel1_categoria
    , classe.nivel2_categoria
    , classe.nivel3_subcategoria

    , classe."95_por_cento_fundo_isento"
    , classe.data_inicio_atividade_classe
    , classe.data_vigencia_classe
    , classe.data_encerramento_classe
    , classe.taxa_performance


    , classe."perfil_complementar.codigo_b3"
    , classe."perfil_complementar.restricao_investimento"
    , classe."perfil_complementar.tipo_investidor"
    , classe."perfil_complementar.aplicacao_automatica"
    , classe."perfil_complementar.plano_previdencia"
    , classe."perfil_complementar.periodicidade_envio_pl_cota"
    , classe."perfil_complementar.calculo_cota"
    , classe."perfil_complementar.data_atualizacao"


    , classe."valores_minimos_movimentacao_classe.indicador_prazo_emissao_cota"
    , classe."valores_minimos_movimentacao_classe.prazo_emissao_cota"
    , classe."valores_minimos_movimentacao_classe.indicador_prazo_conversao_resgate"
    , classe."valores_minimos_movimentacao_classe.prazo_conversao_resgate"
    , classe."valores_minimos_movimentacao_classe.indicador_prazo_pagamento_resgate"
    , classe."valores_minimos_movimentacao_classe.prazo_pagamento_resgate"
    , classe."valores_minimos_movimentacao_classe.regra_adicional_pagamento_resgate"
    , classe."valores_minimos_movimentacao_classe.dias_carencia_inicial"
    , classe."valores_minimos_movimentacao_classe.dias_carencia_ciclica"
    , classe."valores_minimos_movimentacao_classe.valor_minimo_aplicacao_inicial"
    , classe."valores_minimos_movimentacao_classe.valor_minimo_aplicacao_subsequente"
    , classe."valores_minimos_movimentacao_classe.valor_minimo_resgate"
    , classe."valores_minimos_movimentacao_classe.valor_minimo_permanencia"
    , classe."valores_minimos_movimentacao_classe.data_atualizacao"
    , classe."taxa_performance.perfil_taxa"
    , classe."taxa_performance.periodicidade_cobranca"
    , classe."taxa_performance.informacoes_adicionais"
    , classe."taxa_performance.data_inicio_vigencia"
    , classe."taxa_performance.data_fim_vigencia"
    , taxa.tipo_taxa as taxa_tipo
    , taxa.perfil_taxa as taxa_perfil
    , taxa.valor_percentual as taxa_percentual
    , taxa.valor_monetario as taxa_vl_monetario
    , taxa.valor_piso as taxa_vl_piso
    , taxa.valor_fixo as taxa_vl_fixo
    , taxa.valor_taxa_maxima as taxa_vl_maxima
    , taxa.valor_percentual_taxa_maxima as taxa_perc_maxima
    , taxa.	informacoes_adicionais as taxa_adicionais
    , suf.sufixo
    , benc.benchmark
    , fundo.codigo_fundo
    , fundo.nome_comercial_fundo
    , fundo.identificador_fundo 
    , fundo.tipo_fundo
    , fundo.atributo as atributo_fundo
    , fundo.data_vigencia_fundo
    , fundo.data_encerramento_fundo
    , fundo.administrador
    , fundo.gestor
    , fundo.adaptado_rcvm175
    , fundo.moeda
    FROM df_fundos_classes classe
    left join df_classes_taxa taxa on classe.codigo_classe = taxa.codigo_classe
    left join df_classes_sufixos suf on classe.codigo_classe = suf.codigo_classe
    left join df_classes_indices_benchmark benc on classe.codigo_classe = benc.codigo_classe
    left join df_fundo_geral fundo on fundo.codigo_fundo = classe.codigo_fundo
    """
#df_classe_geral = sqldf(select, locals())


select = """  
    SELECT
    classe.codigo_classe
    , classe.nome_comercial_classe
    , fundo.codigo_fundo
    , fundo.nome_comercial_fundo
    , fundo.identificador_fundo
    , fundo.gestor
    , fundo.administrador
    , fundo.tipo_fundo
    , prestadores.*
    from df_classes_perstadores prestadores
    left join df_fundo_classes classe on classe.codigo_classe = prestadores.codigo_classe
    left join df_fundo_geral fundo on fundo.codigo_fundo = classe.codigo_fundo
    
    """
#df_classe_prestadores_g = sqldf(select, locals())


select = """  
    SELECT
    classe.codigo_classe
    , classe.nome_comercial_classe
    , fundo.codigo_fundo
    , fundo.nome_comercial_fundo
    , fundo.identificador_fundo
    , fundo.gestor
    , fundo.administrador
    , fundo.tipo_fundo
    , taxas.*
    from df_classes_taxa taxas
    left join df_fundos_classes classe on classe.codigo_classe = taxas.codigo_classe
    left join df_fundo_geral fundo on fundo.codigo_fundo = classe.codigo_fundo
    
    """
#df_classe_taxas_g = sqldf(select, locals())

select = """  
    SELECT
    classe.codigo_classe
    , classe.nome_comercial_classe
    , fundo.codigo_fundo
    , fundo.nome_comercial_fundo
    , fundo.identificador_fundo
    , fundo.gestor
    , fundo.administrador
    , fundo.tipo_fundo
    , taxas.*
    from df_classes_taxas_entrada_saida taxas
    left join df_fundos_classes classe on classe.codigo_classe = taxas.codigo_classe
    left join df_fundo_geral fundo on fundo.codigo_fundo = classe.codigo_fundo
    
    """
#df_classe_entrada_saida_g = sqldf(select, locals())


select = """  
    SELECT
    sub.*
    , classe.nome_comercial_classe
    , fundo.codigo_fundo
    , fundo.nome_comercial_fundo
    , fundo.identificador_fundo 
    , fundo.tipo_fundo
    , fundo.atributo as atributo_fundo
    , fundo.data_vigencia_fundo
    , fundo.data_encerramento_fundo
    , fundo.administrador
    , fundo.gestor
    , fundo.adaptado_rcvm175
    , fundo.moeda
    from df_subclasses sub
    left join df_fundos_classes classe on classe.codigo_classe = sub.codigo_classe
    left join df_fundo_geral fundo on fundo.codigo_fundo = classe.codigo_fundo
    
    """
#df_subclasse_geral= sqldf(select, locals())



select = """  
    SELECT
    sub.codigo_subclasse
    , sub.nome_comercial_subclasse
    , classe.codigo_classe
    , classe.nome_comercial_classe
    , fundo.codigo_fundo
    , fundo.nome_comercial_fundo
    , fundo.identificador_fundo
    , fundo.gestor
    , fundo.administrador
    , fundo.tipo_fundo
    , perf.*
    from df_subclasses perf
    left join df_subclasses sub on sub.codigo_subclasse = perf.codigo_subclasse
    left join df_fundos_classes classe on classe.codigo_classe = sub.codigo_classe
    left join df_fundo_geral fundo on fundo.codigo_fundo = classe.codigo_fundo
    
    """
#df_sub_performance_g= sqldf(select, locals())


select = """  
    SELECT
    sub.codigo_subclasse
    , sub.nome_comercial_subclasse
    , classe.codigo_classe
    , classe.nome_comercial_classe
    , fundo.codigo_fundo
    , fundo.nome_comercial_fundo
    , fundo.identificador_fundo
    , fundo.gestor
    , fundo.administrador
    , fundo.tipo_fundo
    , taxas.*
    from df_subclasses_taxas taxas
    left join df_subclasses sub on sub.codigo_subclasse = taxas.codigo_subclasse
    left join df_fundos_classes classe on classe.codigo_classe = sub.codigo_classe
    left join df_fundo_geral fundo on fundo.codigo_fundo = classe.codigo_fundo
    
    """
#df_sub_taxas_g= sqldf(select, locals())


select = """  
    SELECT
    sub.codigo_subclasse
    , sub.nome_comercial_subclasse
    , classe.codigo_classe
    , classe.nome_comercial_classe
    , fundo.codigo_fundo
    , fundo.nome_comercial_fundo
    , fundo.identificador_fundo
    , fundo.gestor
    , fundo.administrador
    , fundo.tipo_fundo
    , taxas.*
    from df_subclasses_taxas_extrada_saida taxas
    left join df_subclasses sub on sub.codigo_subclasse = taxas.codigo_subclasse
    left join df_fundos_classes classe on classe.codigo_classe = sub.codigo_classe
    left join df_fundo_geral fundo on fundo.codigo_fundo = classe.codigo_fundo
    
    """
#df_sub_entrada_saida_g= sqldf(select, locals())




#df_fundo_geral.to_csv('df_fundo_geral.csv', index=False)
#df_sub_performance_g.to_csv('df_sub_performance_g.csv', index=False)
#df_sub_entrada_saida_g.to_csv('df_sub_entrada_saida_g.csv', index=False)
#df_subclasse_geral.to_csv('df_subclasse_geral.csv', index=False)
#df_classe_entrada_saida_g.to_csv('df_classe_entrada_saida_g.csv', index=False)
#df_classe_taxas_g.to_csv('df_classe_taxas_g.csv', index=False)
#df_classe_geral.to_csv('df_classe_geral.csv', index=False)





