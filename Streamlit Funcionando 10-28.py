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
init_notebook_mode(all_interactive=True)


#from itables import init_notebook_mode
#from itables import show 

#python -m streamlit run C:\Users\andre_trierveiler\EstrtuturaStreamLit.py
#python -m streamlit run C:\Users\andre_trierveiler\EstrtuturaStreamLit.py --server.address localhost --server.port 8505 

#import businessdays as bzd


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

# Busca Indicores Anbima
def buscar_dados_ima(data_inicial, data_final, headers = headers, url = url):
    #inicializa df para armazenar dados
    df_ima_res = pd.DataFrame()
    url = f'{url}feed/precos-indices/v1/indices/resultados-ima'
    
    # Conexao
    headers = headers
    
    # Convertendo as strings de data em objetos datetime
    #data_inicial = datetime.strptime(data_inicial, '%Y-%m-%d')
   # data_final = datetime.strptime(data_final, '%Y-%m-%d')
    
    
    # Loop para buscar dados dia a dia
    data_atual = data_inicial
    while data_atual <= data_final:
        params = {
            'data': data_atual.strftime('%Y-%m-%d')
        }
        
        # Fazendo a requisição GET para a data específica
        response = requests.get(url, headers=headers, params=params)
        
        # Verificando se a requisição foi bem-sucedida
        if response.status_code == 200:
            dados_json = pd.DataFrame(response.json()) # Recebe a resposta como JSON
            df_ima_res  = pd.concat([df_ima_res ,dados_json], ignore_index=True)
        data_atual = data_atual + timedelta(days=1)   
    
    df_ima_res = df_ima_res.pivot(index='data_referencia', columns='indice', values='variacao_diaria')
    return df_ima_res 


def df_cadastro_geral(headers = headers, atualiza = 0):
    df_cadastro = pd.DataFrame() 
    if atualiza == 1 :
        size = 1000
        pages = 50
        for i in range(1,pages):
            fundos_http = f'{url}feed/fundos/v2/fundos?page={i}&size={size}' #tamanho máximo 1000, 32 paginas totais
            fundos = requests.get(fundos_http, headers=headers)
            try:
                fundos_json = fundos.json()
            except ValueError:
                headers = conectar('wRGlvlj1bOW3', 'l4riAuRd0CUL','wRGlvlj1bOW3:l4riAuRd0CUL', url)
                fundos_json = fundos.json()
                i = i-1
            df = pd.json_normalize(fundos_json['content'])
            df['page'] = i
            df_cadastro = pd.concat([df_cadastro,df])
            if len(df) < size:
                break
        df_cadastro = df_cadastro.reset_index(drop=True)
    else:    
        df_cadastro = pd.read_csv('df_cadastro.csv')
        df_cadastro['identificador_fundo'] = df_cadastro['identificador_fundo'].astype(str).str.zfill(14)
    return df_cadastro



# Define listas pre-feitas/padrão de fundos
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


# Funções Genericas
def list_names(*args):
     return [name for name in args]

def create_dict(*args):
    import inspect
    # Pegar o nome das variáveis das listas
    frame = inspect.currentframe().f_back
    names = {id(value): key for key, value in frame.f_locals.items()}
    
    # Criar o dicionário com as listas
    return {names[id(lst)]: lst for lst in args}

lista_fundos= create_dict(IRFM, IRFM1, IMAB)


def extrair_json(http, headers = headers):
    request = requests.get(http, headers=headers)
    try:
        df = request.json()
        return df
    except ValueError:
        print('Erro')
        print(http)
        headers = conectar('wRGlvlj1bOW3', 'l4riAuRd0CUL','wRGlvlj1bOW3:l4riAuRd0CUL', url)    

# Funções de Grafico
def plot_historico(dataframe, variables=[], title='', resample='W'):
    
        variables = variables
        resample = resample
        df_plot_m = df_hist_classe_sub.melt(id_vars=['data_competencia','nome_fantasia'], value_vars=variables)
        df_plot_m.sort_values(by=['data_competencia','nome_fantasia'], inplace=True)
        df_plot_m.sort_values(by=['data_competencia'], inplace=True)
        
        #df_plot_m  = df_plot_m.sort_values(by=['nome_fantasia'], key=lambda x: x != fundo_sicredi)
        #df_plot_m['date_str'] = df_plot_m.data_competencia.dt.strftime('%Y-%m-%d')
        
        #df_plot_m = df_plot_m.set_index('data_competencia').groupby(['nome_fantasia','variable']).resample(resample).ffill()
        #del df_plot_m['nome_fantasia']
        #del df_plot_m['variable']
        df_plot_m = df_plot_m.reset_index(level=None, drop=False, inplace=False, col_level=0, col_fill='')

        fig = px.line(df_plot_m
                       , y='value'
                       , x='data_competencia'
                       #, animation_frame=df_plot_m.date_str
                       #, animation_group="group_by"
                       #, facet_col_wrap=col_wrap       
                       #, facet_col = col
                       , facet_col_wrap=2      
                       , facet_col = 'variable'   
                       , color='nome_fantasia'
                       , color_discrete_map=color_map
                       , hover_name='nome_fantasia'
                       #, labels={'value':'Number of Cases','day_number':"Days Since "+ str(threshold) +"th Case",'date':'Date', 'name':'City'}
                       #, range_y=[0.1, df_plot_m.value.max()+5000]
                       #, range_x = [df_plot_m.date.min(),df_plot_m.date.max()]
                       #, text=df_plot_m[group_by]
                       #, size=1
                       , title=title
                       , height=800
                       , width=1400
                       )
        fig.update_yaxes(matches=None) 
        #fig.update_xaxes(matches=None)
        fig.update_yaxes(showticklabels=True)
        
        return fig

        

# Processamento Inicial - Carregando DataFrames
def carregar_dados_iniciais():
    df_fundos = []
    
    df_indices = buscar_dados_ima(pd.to_datetime('2024-10-23'), pd.to_datetime('2024-10-23'), headers = headers, url = url)

    
    
    return df_fundos, df_indices

df_fundos, df_indices = carregar_dados_iniciais()

# Função de Processamento de Dados
def processar_dados(data_inicial, data_final, lista_fundos, indicador):
    st.write(f"Processando dados de {data_inicial} a {data_final} para o fundo {lista_fundos} e indicador {indicador}")
    # Processamento personalizado
    
    headers = conectar('wRGlvlj1bOW3', 'l4riAuRd0CUL','wRGlvlj1bOW3:l4riAuRd0CUL', url)  
    st.write(f"Processando dados cadastro Geral")
    df_cadastro = df_cadastro_geral()
    lista = df_cadastro[['codigo_fundo','nome_comercial_fundo','identificador_fundo']][df_cadastro['identificador_fundo'].isin(lista_fundos)].reset_index(drop=True)
    
    df_fundos_det_cadastro = pd.DataFrame()
    df_fundos_classes = pd.DataFrame()
    df_fundos_prestadores = pd.DataFrame()
    df_fundos_sufixos = pd.DataFrame()
    df_fundos_benchmark  = pd.DataFrame()
    df_fundos_documentos  = pd.DataFrame()
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
    df_subclasses_performance = pd.DataFrame()
    
    st.write(f"Processando dados de dados de cadastro dos fundos")
    for codigo_fundo in lista.codigo_fundo:

        fundos_det_http = f'{url}feed/fundos/v2/fundos/{codigo_fundo}'
        fundos_det = requests.get(fundos_det_http, headers=headers)
        try:
            fundos_det_json = fundos_det.json()
    
        except ValueError:
            print('Erro')
    
            print(codigo_fundo)
            headers = conectar('wRGlvlj1bOW3', 'l4riAuRd0CUL','wRGlvlj1bOW3:l4riAuRd0CUL', url)
        #dados_cadastrais = pd.json_normalize(fundos_det_json['dados-cadastrais'])
        fundo_det_cadastro = pd.json_normalize(fundos_det_json)
        #json_cadastro_total = json_cadastro_total.append(fundos_det_json)
        df_fundos_det_cadastro = pd.concat([df_fundos_det_cadastro,fundo_det_cadastro], ignore_index=True)
        
        fundos_det_classes = pd.json_normalize(fundos_det_json['classes'])
        fundos_det_classes['codigo_fundo'] = codigo_fundo
        df_fundos_classes = pd.concat([df_fundos_classes, fundos_det_classes], ignore_index=True)
    
        fundos_det_prestadores = pd.json_normalize(fundos_det_json['prestadores_fundo'])
        fundos_det_prestadores['codigo_fundo'] = codigo_fundo
        df_fundos_prestadores = pd.concat([df_fundos_prestadores, fundos_det_prestadores], ignore_index=True)
        
        fundos_det_documentos = pd.json_normalize(fundos_det_json['documentos'])
        fundos_det_documentos['codigo_fundo'] = codigo_fundo

        
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
        det_performance_sub = []
        det_performance_sub_df = pd.DataFrame()
        
        
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
                if classe['subclasses'] != None:
                    print(classe['codigo_classe'])
                    print(type(subclasses))
                    #subclasses_temp = pd.DataFrame(classe['subclasses'])
                    subclasses_temp = pd.json_normalize(classe['subclasses'])
                    subclasses_temp['codigo_fundo'] = codigo_fundo
                    subclasses_temp['codigo_classe'] = classe['codigo_classe']
                    subclasses.append(subclasses_temp)      
                    subclasses = pd.concat(subclasses, ignore_index=True)
                    df_subclasses = pd.concat([df_subclasses,subclasses], ignore_index=True)
                    
                    for subclasse in classe['subclasses']:
                        if 'prestadores_subclasse' in subclasse:
                            prestadores_sub_temp = pd.DataFrame(subclasse['prestadores_subclasse'])
                            prestadores_sub_temp['codigo_fundo'] = codigo_fundo
                            prestadores_sub_temp['codigo_classe'] = classe['codigo_classe']
                            prestadores_sub_temp['codigo_subclasse'] = subclasse['codigo_subclasse']
                            prestadores_sub.append(prestadores_sub_temp)  
                            
                       
                        if 'taxas_subclasse' in subclasse:
                            taxas_sub_temp = pd.DataFrame(subclasse['taxas_subclasse'])
                            taxas_sub_temp['codigo_fundo'] = codigo_fundo
                            taxas_sub_temp['codigo_classe'] = classe['codigo_classe']
                            taxas_sub_temp['codigo_subclasse'] = subclasse['codigo_subclasse']
                            taxas_sub.append(taxas_sub_temp)  
                            
                            
                        if 'taxas_entrada_saida_subclasse' in subclasse:
                            taxas_entrada_saida_sub_temp = pd.DataFrame(subclasse['taxas_entrada_saida_subclasse'])
                            taxas_entrada_saida_sub_temp['codigo_fundo'] = codigo_fundo
                            taxas_entrada_saida_sub_temp['codigo_classe'] = classe['codigo_classe']
                            taxas_entrada_saida_sub_temp['codigo_subclasse'] = subclasse['codigo_subclasse']
                            taxas_entrada_saida_sub.append(taxas_entrada_saida_sub_temp)  
                            
                               
                        if 'taxa_performance' in subclasse: 
                          if subclasse['taxa_performance'] != None:
                            if subclasse['taxa_performance']['detalhes'] != None:
                                det_performance_sub_temp = pd.DataFrame(subclasse['taxa_performance']['detalhes'])
                                det_performance_sub_temp['codigo_classe'] = classe['codigo_classe']
                                det_performance_sub_temp['codigo_fundo'] = codigo_fundo
                                det_performance_sub_temp['codigo_subclasse'] = subclasse['codigo_subclasse']
                                det_performance_sub.append(det_performance_sub_temp) 
                                det_performance_sub_df = pd.concat(det_performance_sub, ignore_index=True)
                    prestadores_sub = pd.concat(prestadores_sub, ignore_index=True) 
                    taxas_sub = pd.concat(taxas_sub, ignore_index=True)
                    taxas_entrada_saida_sub = pd.concat(taxas_entrada_saida_sub, ignore_index=True)
                    
                    df_subclasses_prestadores = pd.concat([df_subclasses_prestadores,prestadores_sub], ignore_index=True)
                    df_subclasses_taxas = pd.concat([df_subclasses_taxas,taxas_sub], ignore_index=True)
                    df_subclasses_performance = pd.concat([df_subclasses_performance,det_performance_sub_df], ignore_index=True)
                    
    
                    
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

    if df_subclasses.empty:
        lista_classe_sub =  df_fundos_classes['codigo_classe']
    else: 
        lista_classe_sub = pd.concat([df_fundos_classes['codigo_classe'], df_subclasses['codigo_subclasse']], ignore_index=True)
    
    st.write(f"Processando dados historicos dos fundos")
    df_pl_classe_sub = pd.DataFrame()
    df_hist_classe_sub = pd.DataFrame()    
    
    for codigo_classe in lista_classe_sub:      
        classe_hist_http = f'{url}feed/fundos/v2/fundos/{codigo_classe}/serie-historica?size=1000&data-inicio={data_inicial}&data-fim={data_final}'
        request = requests.get(classe_hist_http, headers=headers)
        if request.status_code in [403,404]:
            print(request.status_code)
        else: 
            json_hist_classe = extrair_json(classe_hist_http)
            temp_hist_classe = pd.json_normalize(json_hist_classe['content'])
            df_hist_classe_sub = pd.concat([df_hist_classe_sub, temp_hist_classe], ignore_index=True)

    df_hist_bck =  df_hist_classe_sub
    df_hist_classe_sub.data_competencia= pd.to_datetime(df_hist_classe_sub.data_competencia, format='%Y-%m-%d')
    
    def limpa_df(df):
        cols_to_drop = [col for col in df.columns if df[col].apply(lambda x: isinstance(x, (dict, list))).any()]
        df = df.drop(columns=cols_to_drop)
        return df
    

    df_fundos_det_cadastro_l = limpa_df(df_fundos_det_cadastro)
    df_fundos_classes_l = limpa_df(df_fundos_classes)
    df_fundos_prestadores_l = limpa_df(df_fundos_prestadores)
    df_fundos_sufixos_l = limpa_df(df_fundos_sufixos)
    df_fundos_benchmark_l  = limpa_df(df_fundos_benchmark)
    df_fundos_documentos_l  = limpa_df(df_fundos_documentos)
    df_classes_taxa_l = limpa_df(df_classes_taxa)
    df_classes_taxas_entrada_saida_l = limpa_df(df_classes_taxas_entrada_saida)
    df_classes_sufixos_l = limpa_df(df_classes_sufixos)
    df_classes_prestadores_l = limpa_df(df_classes_prestadores)
    df_classes_indices_benchmark_l = limpa_df(df_classes_indices_benchmark)
    df_subclasses_l = limpa_df(df_subclasses)
    df_subclasses_prestadores_l = limpa_df(df_subclasses_prestadores)
    df_subclasses_taxas_l = limpa_df(df_subclasses_taxas)
    df_subclasses_taxas_extrada_saida_l =limpa_df(df_subclasses_taxas_extrada_saida)
    df_subclasses_valores_minimos_l = limpa_df(df_subclasses_valores_minimos)
    df_subclasses_performance_l = limpa_df(df_subclasses_performance)
    df_hist_classe_sub = limpa_df(df_hist_classe_sub)    

    
    #DATAFRAMES PARA CADASTRO
    select = """  SELECT fundo.*
        , adm.razao_social as administrador
        , gestor.razao_social as gestor

        FROM df_fundos_det_cadastro_l fundo
        left join df_fundos_prestadores adm on fundo.codigo_fundo = adm.codigo_fundo and 	adm.codigo_tipo_prestador = 'ADMINISTRADOR'
        left join df_fundos_prestadores gestor on fundo.codigo_fundo = gestor.codigo_fundo and 	gestor.codigo_tipo_prestador = 'GESTOR'
       """
    df_fundo_geral = sqldf(select, locals())

    select = """  
        SELECT
         fundo.nome_comercial_fundo
        , classe.*

        FROM df_fundos_det_cadastro_l fundo
        left join df_fundos_classes_l classe on fundo.codigo_fundo = classe.codigo_fundo 
        """
    df_fundo_classe_g = sqldf(select, locals())
    
    select = """  
        SELECT
         classe.nome_comercial_classe
        , taxa.*

        FROM df_fundos_classes_l classe
        left join df_classes_taxa_l taxa on classe.codigo_classe = taxa.codigo_classe
        """
    df_fundo_taxa_g = sqldf(select, locals())

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

        
        , classe.subclasses
        , classe.taxa_performance
        
        
        , classe."perfil_complementar.codigo_b3"
        , classe."perfil_complementar.restricao_investimento"
        , classe."perfil_complementar.tipo_investidor"
        , classe."perfil_complementar.aplicacao_automatica"
        , classe."perfil_complementar.plano_previdencia"
        , classe."perfil_complementar.periodicidade_envio_pl_cota"
        , classe."perfil_complementar.calculo_cota"
        
        
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
        , fundo.tipo_fundo
        , fundo.atributo as atributo_fundo
        , fundo.administrador
        , fundo.gestor
        FROM df_fundos_classes_l classe
        left join df_classes_taxa_l taxa on classe.codigo_classe = taxa.codigo_classe
        left join df_classes_sufixos_l suf on classe.codigo_classe = suf.codigo_classe
        left join df_classes_indices_benchmark_l benc on classe.codigo_classe = benc.codigo_classe
        left join df_fundo_geral fundo on fundo.codigo_fundo = classe.codigo_fundo
        """
    df_classe_geral = sqldf(select, locals())    
    
    df_classe_geral.data_inicio_atividade_classe = pd.to_datetime(df_classe_geral.data_inicio_atividade_classe, format='ISO8601')
    #df_classe_geral.data_atualizacao = pd.to_datetime(df_hist_classe_sub.data_atualizacao,  format='ISO8601')
    
    select = """
        SELECT 
         classe.nome_comercial_classe
        , fundo.nome_comercial_fundo
        , hist.*
     
        FROM df_hist_classe_sub hist
        left join df_fundos_det_cadastro_l fundo on fundo.codigo_fundo = hist.codigo_fundo
        left join df_fundos_classes_l classe on classe.codigo_classe = hist.codigo_classe
       """
    df_hist_classe_sub = sqldf(select, locals())
    
    
    df_hist_classe_sub = df_hist_classe_sub.sort_values(by='data_competencia',ascending=True)
    df_hist_classe_sub = df_hist_classe_sub.reset_index(drop=True)
    df_hist_classe_sub['nome_fantasia'] = df_hist_classe_sub['nome_comercial_classe']
    
    fundo_sicredi = df_fundos_classes.loc[df_fundos_classes['nome_comercial_classe'].str.contains('SICREDI')].reset_index().nome_comercial_classe[0]
    color_map = {nome_comercial_classe: '#64C832' if 'SICREDI' in nome_comercial_classe  else 'rgba(128, 128, 128, 0.25)' for nome_comercial_classe in df_fundos_classes['nome_comercial_classe'].unique()}
    color_map2 = {nome_comercial_classe: '#64C832' if 'SICREDI' in nome_comercial_classe  else 'rgba(128, 128, 128, 0.5)' for nome_comercial_classe in df_fundos_classes['nome_comercial_classe'].unique()}

    ##### Analise de Passivo ######
    janela_movel = 20 #define a janela para a soma movel da captação/resgate
    janela_movel_pl = 1 #define a janela para a soma movel da captação/resgate em percentual do PL
    
    df_hist_classe_sub.data_competencia = pd.to_datetime(df_hist_classe_sub.data_competencia, format='ISO8601')
    df_hist_classe_sub.data_atualizacao = pd.to_datetime(df_hist_classe_sub.data_atualizacao,  format='ISO8601')
    
    #### Novos campospara analise ####
    
    df_hist_classe_sub['ticket_medio'] = df_hist_classe_sub.valor_patrimonio_liquido/df_hist_classe_sub.numero_cotistas
    df_hist_classe_sub['captacao_acumulada'] = df_hist_classe_sub.groupby('codigo_fundo').valor_volume_total_aplicacoes.rolling(555000, min_periods=1).sum().fillna(0).reset_index(0,drop=True)  
    df_hist_classe_sub['resgate_acumulado'] = df_hist_classe_sub.groupby('codigo_fundo').valor_volume_total_resgates.rolling(555000, min_periods=1).sum().fillna(0).reset_index(0,drop=True)
    df_hist_classe_sub['captacao_liquida_acumulada'] = df_hist_classe_sub['captacao_acumulada'] -df_hist_classe_sub['resgate_acumulado']  
    df_hist_classe_sub['captacao_movel'] = df_hist_classe_sub.groupby('codigo_fundo').valor_volume_total_aplicacoes.rolling(janela_movel).sum().fillna(0).shift(1).reset_index(0,drop=True)  
    df_hist_classe_sub['resgate_movel'] = df_hist_classe_sub.groupby('codigo_fundo').valor_volume_total_resgates.rolling(janela_movel).sum().shift(1).reset_index(0,drop=True)
    df_hist_classe_sub['captacao_liquida_movel'] = df_hist_classe_sub['captacao_movel'] -df_hist_classe_sub['resgate_movel']  
    df_hist_classe_sub['captacao_liquida'] = df_hist_classe_sub['valor_volume_total_aplicacoes'] -df_hist_classe_sub['valor_volume_total_resgates']
    df_hist_classe_sub['captacao_pl'] = df_hist_classe_sub.valor_volume_total_aplicacoes/df_hist_classe_sub.valor_patrimonio_liquido
    df_hist_classe_sub['resgate_pl'] = df_hist_classe_sub.valor_volume_total_resgates/df_hist_classe_sub.valor_patrimonio_liquido
    df_hist_classe_sub['captacao_liquida_pl'] = df_hist_classe_sub.captacao_liquida/df_hist_classe_sub.valor_patrimonio_liquido
    df_hist_classe_sub['captacao_pl'] = df_hist_classe_sub.groupby('codigo_fundo').captacao_pl.rolling(janela_movel_pl).mean().fillna(0).reset_index(0,drop=True)
    df_hist_classe_sub['resgate_pl'] =  df_hist_classe_sub.groupby('codigo_fundo').resgate_pl.rolling(janela_movel_pl).mean().fillna(0).reset_index(0,drop=True)
    df_hist_classe_sub['captacao_liquida_pl'] = df_hist_classe_sub.groupby('codigo_fundo').captacao_liquida_pl.rolling(janela_movel_pl).mean().fillna(0).reset_index(0,drop=True)
    
    #color_map, color_map2, df_hist_classe_sub
    st.session_state.write_cache = []
    
    ####### Dataframe de Retornos ##########
    df_returns = df_hist_classe_sub.sort_values('nome_fantasia', ascending=True) .pivot(index='data_competencia', columns='nome_fantasia', values='valor_cota')
    
    
    returns = df_returns.pct_change().dropna()
    returns_mes = returns.resample('M').agg(lambda x: (x + 1).prod()- 1)
    returns_semana = returns.resample('W').agg(lambda x: (x + 1).prod()- 1)
    returns_ano = returns.resample('Y').agg(lambda x: (x + 1).prod()- 1)
    returns_total = returns.agg(lambda x: (x + 1).prod()- 1)
    return_acum = (1 + returns).cumprod()
    return_acum_semana = (1 + returns_semana).cumprod()
    return_acum_mes = (1 + returns_mes).cumprod()
    
    df = returns_ano
    list(df.columns.values)
    df['data_referencia'] = df.index
    df = pd.melt(df, id_vars=['data_referencia'], value_vars=list(df.columns.values),
            var_name='nome_fantasia', value_name='return')
        
    
    return color_map, color_map2, df_hist_classe_sub, returns_mes, return_acum, returns \
          , df_fundo_geral, df_fundo_taxa_g, df_fundo_classe_g, df_classe_geral
        













##########                             #######  
########## Configurações do Streamlite #######
##########                             #######  



# Menus de Entrada
st.sidebar.header('Parâmetros de Entrada')

# Data Inicial e Final
data_inicial = st.sidebar.date_input('Data Inicial', datetime.date(2023, 1, 1))
data_final = st.sidebar.date_input('Data Final', datetime.date(2023, 12, 29))

# Lista Fundos Padrão
lista_fundos_nome = st.sidebar.selectbox('Selecione a Lista de Fundos', list(lista_fundos.keys()))
fundo_selecionado = lista_fundos[lista_fundos_nome]

# Indicador
indicador_selecionado = st.sidebar.selectbox('Selecione o Indicador', df_indices.columns)

# Checkbox para Baixar Regulamento
baixar_regulamento = st.sidebar.checkbox('Baixar Regulamento')
destaque_sicredi = st.sidebar.checkbox('Destaca Fundos Sicredi')

# Botão "Rodar"
if st.sidebar.button('Rodar'):
    st.session_state.color_map, st.session_state.color_map2, st.session_state.df_hist_classe_sub, \
    st.session_state.returns_mes, st.session_state.return_acum, st.session_state.returns , \
    st.session_state.df_fundo_geral, st.session_state.df_fundo_taxa_g, st.session_state.df_fundo_classe_g, \
    st.session_state.df_classe_geral   = processar_dados(data_inicial, data_final, fundo_selecionado, indicador_selecionado)
    #st.session_state.df_hist_classe_sub = processar_dados(data_inicial, data_final, fundo_selecionado, indicador_selecionado)


# Links de Visualizações
st.sidebar.subheader('Páginas de Visualização')

pagina_selecionada = st.sidebar.selectbox('Selecione a Página', 
                                          ['Comparativos de Classes I', 'Comparativos de Classes II','Comparativos Fundos','Comparativos de Classes III'
                                           'Rentabilidade', 
                                           'Patrimônio Líquido e Captação', 
                                           'Performance', 
                                           'Volatilidade', 
                                           'Histórico de Carteiras'])

# Exibir Páginas de Visualização separadamente
if pagina_selecionada == 'Comparativos de Classes I':
    st.header("Comparativos de Classes I")
      # Personalize a exibição
    df_fundo_geral = st.session_state.df_fundo_geral
    df_fundo_classe_g = st.session_state.df_fundo_classe_g
    df_fundo_taxa_g = st.session_state.df_fundo_taxa_g
    df_classe_geral = st.session_state.df_classe_geral

    html(
        to_html_datatable(
            df_classe_geral,
            layout={"top1": "searchPanes"},
            searchPanes={"layout": "columns-5", "cascadePanes": True},
        ),height=1960,  # adjust manually
    )


elif pagina_selecionada == 'Comparativos de Classes II':
    st.header("Comparativos de Classes II")
      # Personalize a exibição
    df_fundo_geral = st.session_state.df_fundo_geral
    df_fundo_classe_g = st.session_state.df_fundo_classe_g
    df_fundo_taxa_g = st.session_state.df_fundo_taxa_g
    df_classe_geral = st.session_state.df_classe_geral
    
    df_classe_geral = df_classe_geral.loc[:, ~df_classe_geral.columns.str.contains('data')]
    #df_classe_geral.background_gradient(axis=None, cmap="YlOrRd")
    html(
        to_html_datatable(
            df_classe_geral,select=True,
            layout={"top1": "searchBuilder"},
            buttons=["copyHtml5", "csvHtml5", "excelHtml5"]
            
        ),height=4960,  # adjust manually
    )    
    
    

elif pagina_selecionada == 'Comparativos de Classes III':
    st.header("Comparativos de Classes II")
      # Personalize a exibição
    df_fundo_geral = st.session_state.df_fundo_geral
    df_fundo_classe_g = st.session_state.df_fundo_classe_g
    df_fundo_taxa_g = st.session_state.df_fundo_taxa_g
    df_classe_geral = st.session_state.df_classe_geral
    
    #df_classe_geral = df_classe_geral.loc[:, ~df_classe_geral.columns.str.contains('data')]
    #df_classe_geral.background_gradient(axis=None, cmap="YlOrRd")
    ag = AgGrid(
        df_classe_geral, 
        gridOptions=go, 
        fit_columns_on_grid_load=True
    )
elif pagina_selecionada == 'Comparativos Fundos':
    st.header("Comparativos de Fundos")
      # Personalize a exibição
    df_fundo_geral = st.session_state.df_fundo_geral
    df_fundo_classe_g = st.session_state.df_fundo_classe_g
    df_fundo_taxa_g = st.session_state.df_fundo_taxa_g
    df_classe_geral = st.session_state.df_classe_geral

    html(
        to_html_datatable(
            df_fundo_geral,
            layout={"top1": "searchPanes"}
        ),height=4960,  # adjust manually
    )        
    
elif pagina_selecionada == 'Rentabilidade':
    st.header("Rentabilidade")
    returns = st.session_state.returns
    return_acum = st.session_state.return_acum
    returns_mes = st.session_state.returns_mes
    color_map = st.session_state.color_map
    
    fig = px.line(return_acum
                       , title='Rentabilidade Acumulada', color_discrete_map=color_map
                       , height=850
                       , width=1300)
    st.plotly_chart(fig)
    fig2 = px.scatter(returns_mes                       
                       , title='Retornos Mensais', color_discrete_map=color_map
                       , height=850
                       , width=1300)
    fig2.update_traces(marker=dict(size=10))
    st.plotly_chart(fig2)

    # Grafico Risco Retorno Absoluto
    N = len(return_acum)
    return_anualizado = return_acum.iloc[-1,] ** (12 / N) - 1
    
    dev_pad_ano = returns.std() * np.sqrt(12)
    
    risco_retorno = pd.DataFrame({'Risco Anualizado' : dev_pad_ano*100,
                  'Retorno Anualizado' : return_anualizado*100})
    
    risco_retorno['Sharpe'] = risco_retorno['Retorno Anualizado']/risco_retorno['Risco Anualizado']
    risco_retorno = risco_retorno.sort_values('Sharpe', ascending=False)
    risco_retorno['size'] = 2
    fig3 = px.scatter(risco_retorno
               , x = 'Risco Anualizado'
               , y = 'Retorno Anualizado'
               , title= 'Risco x Retorno'
               , color =  risco_retorno.index, color_discrete_map=color_map, size='size'
               , height=800
               , width=1050)    
    st.plotly_chart(fig3)
    
    
elif pagina_selecionada == 'Patrimônio Líquido e Captação':
    
    st.header("Patrimônio Líquido e Captação")
    st.write("Comparativos de PL, Captação, número cotistas e outros")  # Personalize a exibição
    st.session_state.write_cache = []
    df_hist_classe_sub = st.session_state.df_hist_classe_sub
    color_map = st.session_state.color_map
    
    fig =plot_historico(df_hist_classe_sub, variables=['valor_patrimonio_liquido','numero_cotistas', 'ticket_medio'], title='Patrimonio Líquido, Num. Cotista e Ticket Médio', resample='W')
    st.plotly_chart(fig)
    fig2 = plot_historico(df_hist_classe_sub, variables=['captacao_acumulada','resgate_acumulado','captacao_liquida_acumulada'], title='Captação Acumulada', resample='W')
    st.plotly_chart(fig2)
    fig3 = plot_historico(df_hist_classe_sub, variables=['captacao_movel','resgate_movel','captacao_liquida_movel'], title='Captação e Resgates - Móvel 20du', resample='W')
    st.plotly_chart(fig3)
    fig4 = plot_historico(df_hist_classe_sub, variables=['captacao_pl','resgate_pl','captacao_liquida_pl'], title='Captação e Resgates em %PL - Semanas', resample='W')
    st.plotly_chart(fig4)
    
    

elif pagina_selecionada == 'Performance':
    st.header("Performance")
    st.write("Exibir performance aqui...")  # Personalize a exibição

elif pagina_selecionada == 'Volatilidade':
    st.header("Volatilidade")
    st.write("Exibir volatilidade aqui...")  # Personalize a exibição

elif pagina_selecionada == 'Histórico de Carteiras':
    st.header("Histórico de Carteiras")
    st.write("Exibir histórico de carteiras aqui...")  # Personalize a exibição
