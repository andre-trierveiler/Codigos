# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 23:53:59 2024

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

    
df_fundo_geral = pd.read_csv('df_fundo_geral.csv', low_memory=False)
df_sub_performance_g = pd.read_csv('df_sub_performance_g.csv', low_memory=False)
df_sub_entrada_saida_g = pd.read_csv('df_sub_entrada_saida_g.csv', low_memory=False)
df_subclasse_geral = pd.read_csv('df_subclasse_geral.csv', low_memory=False)
df_classe_entrada_saida_g = pd.read_csv('df_classe_entrada_saida_g.csv', low_memory=False)
df_classe_taxas_g = pd.read_csv('df_classe_taxas_g.csv', low_memory=False)
df_classe_geral = pd.read_csv('df_classe_geral.csv', low_memory=False)


df_fundo_geral = df_fundo_geral
df_fundo_geral = df_fundo_geral[df_fundo_geral['tipo_fundo'] == 'FIP']
lista_tipos = df_fundo_geral['tipo_fundo'].unique()

tipo_padrao = "FIP"  # Substitua pelo valor padrão desejado

# Definir o valor padrão no menu suspenso
if tipo_padrao in lista_tipos:
    tipo = st.sidebar.selectbox("Selecione o tipo de fundo:", list(lista_tipos), index=list(lista_tipos).index(tipo_padrao))
else:
    tipo = st.sidebar.selectbox("Selecione o tipo de fundo:", list(lista_tipos))

df_classe_geral = df_classe_geral[df_classe_geral['tipo_fundo'] == tipo]

#df_lista =   df_cadastro[df_cadastro['tipo_fundo'] == tipo][['razao_social_fundo','codigo_fundo']]
#dict_lista = df_lista.to_dict(orient='records')
#fundos_lista = dict_lista

# Links de Visualizações

multi = True
cascade = True
columns= 3
multi_text = "multi" if multi else "single" 

height = 5950
width = 900

def rearrange_columns(df, first_column_name):
    # Verificar se a coluna especificada existe no DataFrame
    if first_column_name not in df.columns:
        raise ValueError(f"A coluna '{first_column_name}' não existe no DataFrame.")
    
    # Reorganizar as colunas
    columns = [first_column_name] + [col for col in df.columns if col != first_column_name]
    df_return = df[columns]
    
    return df_return


    
      # Personalize a exibição
df_fundo_geral = df_fundo_geral
df_fundo_geral = df_fundo_geral.loc[:, ~df_fundo_geral.columns.str.contains('data')]
df_fundo_geral = rearrange_columns(df_fundo_geral, 'nome_comercial_fundo')
#opt.classes = ["display", "nowrap"]
opt.column_filters = 'footer'
opt.fixedColumns = {"leftColumns": 3}
#opt.searchPanes = {"dtOpts": {"select": {"style": "multi"}}}
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
#html(html_table,height=height,width=width)
with open("tabela.html", "w") as file:
    file.write(html_table)
        
if pagina_selecionada == 'Compartivo Fundosaaaa':   
    st.header("Comparativos  Fundoss")
    df_fundo_geral = df_fundo_geral
    html(to_html_datatable(df_fundo_geral, dom="Plfrtip", columnDefs=[
        {"searchPanes": {"show": True, "header": True, "dtOpts": {"select": {"style": "single"}}}, "targets": [0, 1, 2]}
    ], options={
        "searchPanes": {
            "cascadePanes": True
        },
        "fixedColumns": {
            "leftColumns": 1
        }
    }))
    
    # Exibir a tabela no Jupyter Notebook

elif pagina_selecionada == 'Comparativos de Classes':
    st.header("Comparativos de Classes")
      # Personalize a exibição
    #df_fundo_geral = st.session_state.df_fundo_geral
    #df_fundo_classe_g = st.session_state.df_fundo_classe_g
    #df_fundo_taxa_g = st.session_state.df_fundo_taxa_g
    #df_classe_geral = st.session_state.df_classe_geral
    df_classe_geral = df_classe_geral[df_classe_geral['tipo_fundo'] == tipo]
    df_classe_geral = df_classe_geral.loc[:, ~df_classe_geral.columns.str.contains('data')]
    #df_classe_geral = df_classe_geral.drop(columns=['taxa_adicionais'])
    df_classe_geral = df_classe_geral.drop(columns=['taxa_adicionais','taxa_performance.informacoes_adicionais'])
    #df_classe_geral.background_gradient(axis=None, cmap="YlOrRd")
    opt.classes = ["display", "nowrap"]
    opt.column_filters = 'header'
    opt.searchPanes = {'columns': ['codigo_classe', 'identificador_classe']}
    #df_classe_geral.background_gradient(axis=None, cmap="YlOrRd")
    html(
        to_html_datatable(
            df_classe_geral,
            layout={"top1": "searchPanes"},select=True,
            searchPanes={"layout": "columns-4", "cascadePanes":True},
            
            buttons=["copyHtml5", "csvHtml5", "excelHtml5"]
        ),height=10060,width=1000,   # adjust manually
    )
    
    
elif pagina_selecionada == 'Comparativos de Classes II':
    st.header("Comparativos de Classes")
      # Personalize a exibição
    #df_fundo_geral = st.session_state.df_fundo_geral
    #df_fundo_classe_g = st.session_state.df_fundo_classe_g
    #df_fundo_taxa_g = st.session_state.df_fundo_taxa_g
    #df_classe_geral = st.session_state.df_classe_geral
    
    df_classe_geral = df_classe_geral.loc[:, ~df_classe_geral.columns.str.contains('data')]
    df_classe_geral = df_classe_geral.drop(columns=['taxa_adicionais','taxa_performance.informacoes_adicionais'])
    #df_classe_geral.background_gradient(axis=None, cmap="YlOrRd")
    opt.classes = ["display", "nowrap"]
    opt.column_filters = True
    opt.searchPanes = {'columns': ['codigo_classe', 'identificador_classe','']}
    html(
        to_html_datatable(
            df_classe_geral,select=True,
            layout={"top1": "searchBuilder"},
            buttons=["copyHtml5", "csvHtml5", "excelHtml5"]
        ),height=10060,width=1000   # adjust manually
       
    )
    
    
    
elif pagina_selecionada == 'Comparativos de Classes III':
    st.header("Comparativos de Classes")
      # Personalize a exibição
    #df_fundo_geral = st.session_state.df_fundo_geral
    #df_fundo_classe_g = st.session_state.df_fundo_classe_g
    #df_fundo_taxa_g = st.session_state.df_fundo_taxa_g
    #df_classe_geral = st.session_state.df_classe_geral
    df_classe_geral = df_classe_geral[df_classe_geral['tipo_fundo'] == tipo]
    df_classe_geral = df_classe_geral.loc[:, ~df_classe_geral.columns.str.contains('data')]
    df_classe_geral = df_classe_geral.drop(columns=['taxa_adicionais'])
    #df_classe_geral.background_gradient(axis=None, cmap="YlOrRd")
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





