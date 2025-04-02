# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 11:28:53 2024

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

#DATAFRAMES PARA CADASTRO
df_fundo_geral = limpa_df(df_fundo_geral)


df_fundos_det_cadastro	= limpa_df(df_fundos_det_cadastro)
df_fundos_prestadores	= limpa_df(df_fundos_prestadores)
df_fundos_classes	= limpa_df(df_fundos_classes)
df_classes_taxa = limpa_df(df_classes_taxa)
df_classes_indices_benchmark = limpa_df(df_classes_indices_benchmark)

df_classes_taxas_entrada_saida = limpa_df(df_classes_taxas_entrada_saida)
df_classes_indices_benchmark = limpa_df(df_classes_indices_benchmark)
df_subclasses = limpa_df(df_subclasses)
df_subclasses_performance = limpa_df(df_subclasses_performance)
df_subclasses_taxas = limpa_df(df_subclasses_taxas)
df_subclasses_taxas_extrada_saida = limpa_df(df_subclasses_taxas_extrada_saida)



select = """  SELECT fundo.*
    , adm.razao_social as administrador
    , gestor.razao_social as gestor

    FROM df_fundos_det_cadastro fundo
    left join df_fundos_prestadores adm on fundo.codigo_fundo = adm.codigo_fundo and 	adm.codigo_tipo_prestador = 'ADMINISTRADOR'
    left join df_fundos_prestadores gestor on fundo.codigo_fundo = gestor.codigo_fundo and 	gestor.codigo_tipo_prestador = 'GESTOR'
   """
df_fundo_geral = sqldf(select, locals())    
df_fundo_geral	= limpa_df(df_fundo_geral)

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
df_classe_geral = sqldf(select, locals())
df_classe_geral	= limpa_df(df_classe_geral)

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
    from df_classes_prestadores prestadores
    left join df_fundos_classes classe on classe.codigo_classe = prestadores.codigo_classe
    left join df_fundo_geral fundo on fundo.codigo_fundo = classe.codigo_fundo
    
    """
df_classe_prestadores_g = sqldf(select, locals())
df_classe_prestadores_g	= limpa_df(df_classe_prestadores_g)

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
df_classe_taxas_g = sqldf(select, locals())
df_classe_taxas_g	= limpa_df(df_classe_taxas_g)

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
df_classe_entrada_saida_g = sqldf(select, locals())
df_classe_entrada_saida_g = limpa_df(df_classe_entrada_saida_g)

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
df_subclasse_geral= sqldf(select, locals())
df_subclasse_geral = limpa_df(df_subclasse_geral)


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
    from df_subclasses_performance perf
    left join df_subclasses sub on sub.codigo_subclasse = perf.codigo_subclasse
    left join df_fundos_classes classe on classe.codigo_classe = sub.codigo_classe
    left join df_fundo_geral fundo on fundo.codigo_fundo = classe.codigo_fundo
    
    """
df_sub_performance_g= sqldf(select, locals())
df_sub_performance_g = limpa_df(df_sub_performance_g)


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
df_sub_taxas_g= sqldf(select, locals())
df_sub_taxas_g = limpa_df(df_sub_taxas_g)


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
df_sub_entrada_saida_g= sqldf(select, locals())
df_sub_entrada_saida_g = limpa_df(df_sub_entrada_saida_g)



#df_fundo_geral.to_csv('df_fundo_geral.csv', index=False)
#df_sub_performance_g.to_csv('df_sub_performance_g.csv', index=False)
#df_sub_entrada_saida_g.to_csv('df_sub_entrada_saida_g.csv', index=False)
#df_subclasse_geral.to_csv('df_subclasse_geral.csv', index=False)
#df_classe_entrada_saida_g.to_csv('df_classe_entrada_saida_g.csv', index=False)
#df_classe_taxas_g.to_csv('df_classe_taxas_g.csv', index=False)
#df_classe_geral.to_csv('df_classe_geral.csv', index=False)

df_classe_prestadores_g.to_csv('df_classe_prestadores_g.csv', index=False)
df_classe_entrada_saida_g.to_csv('df_classe_entrada_saida_g.csv', index=False)
df_sub_taxas_g.to_csv('df_sub_taxas_g.csv', index=False)