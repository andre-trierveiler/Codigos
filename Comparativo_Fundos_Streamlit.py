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
import teradata
import indices_performance as pfm


#from itables import init_notebook_mode
#from itables import show 

#python -m streamlit run C:\Users\andre_trierveiler\Comparativo_Fundos_Streamlit.py
#python -m streamlit run C:\Users\andre_trierveiler\Comparativo_Fundos_Streamlit.py --server.address localhost --server.port 8505 
#python -m streamlit run C:\Users\andre_trierveiler\Comparativo_Fundos_Streamlit.py --server.address localhost --server.port 8522 

#import businessdays as bzd

color_map = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52']

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

def conectar_teradata():
    ## Conexao teradata "convencional" - usada para gravar iserir os dados do df na tabela original do teradata(agragando dados novos sem sobrepor ##
    Exec = teradata.UdaExec(appName="TESTE", version="1.0", logConsole=False)
    session = Exec.connect(method="odbc", system="teradbAWS.sicredi.net",
            username="P_USR_DL_GESTAO_RECURSOS", password="JAW0b71329aadade35365afc6X", Authentication="TDNEGO");
    return session



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

RISCO = []

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


lista_fundos= create_dict(IRFM, IRFM1, IMAB, outros, IMAB5, CDI)


def rearrange_columns(df, first_column_name):
    # Verificar se a coluna especificada existe no DataFrame
    if first_column_name not in df.columns:
        raise ValueError(f"A coluna '{first_column_name}' não existe no DataFrame.")
    
    # Reorganizar as colunas
    columns = [first_column_name] + [col for col in df.columns if col != first_column_name]
    df_return = df[columns]
    
    return df_return

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

        
# Função para fazer o download do PDF com headers de autenticação
def baixar_pdf(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        # O conteúdo do PDF está no formato binário
        return response.content
    else:
        st.error(f"Erro ao acessar o PDF. Status Code: {response.status_code}")
        return None
    

def carrega_indicadores2(data_inicial, data_final):
    
    #session = conectar_teradata()
    Exec = teradata.UdaExec(appName="TESTE", version="1.0", logConsole=False)
    session = Exec.connect(method="odbc", system="teradbAWS.sicredi.net",
            username="P_USR_DL_GESTAO_RECURSOS", password="JAW0b71329aadade35365afc6X", Authentication="TDNEGO");
    
    select = f"""select * from (
    SELECT DATA as data_competencia, trim(INDICE) as indice, VARIACAO_DIARIA/100 as variacao_diaria  FROM DL_GESTAO_RECURSOS.ANBIMA_indices
    UNION
    SELECT DATA as data_competencia, trim(CODINDEX) AS indice, case when codindex = 'CDI' then VALOR/3000 else  VALOR/LAG(VALOR, 1) OVER (PARTITION BY CODINDEX ORDER BY DATA)-1 end AS variacao_diaria 
    FROM DL_GESTAO_RECURSOS.IDX_INDEX
    WHERE CODINDEX in ('BETAIMA5',	'BOLSAAL',	'BRENT',	'CDI',	'DOL',	'DOLREFER',	'DXY',	'EURO',	'IBOVESPA',	'IDI',	'IHFA',	'IMESTRAT',	'INDESSCO',	'INDPETR4',	'ISE',	'ISE CDI',	'ISE CDI1',	'IVBX-2',	'PRTIPCA',	'SFFC',	'SP ESG',	'SP500',	'STFRFCP',	'TRESUR10',	'WTI')
    and VALOR <> 0
    ) tab where data_competencia between '{(data_inicial+timedelta(days=-10)).strftime('%Y-%m-%d')}' and '{data_final.strftime('%Y-%m-%d')}'
    """

    df_indicadores = pd.read_sql(select, session) 
    df_indicadores.data_competencia = pd.to_datetime(df_indicadores.data_competencia , format='%Y-%m-%d')
    df_indicadores = df_indicadores.sort_values(by='indice')
    return df_indicadores

def carrega_indicadores(data_inicial, data_final):
    df_indicadores = ['CDI','IRFM']
    return df_indicadores

# Processamento Inicial - Carregando DataFrames
def carregar_dados_iniciais():
    
    df_indices = carrega_indicadores(pd.to_datetime('2024-10-23'), pd.to_datetime('2024-10-23'))    
    return  df_indices

if 'df_indices' not in st.session_state:
    st.session_state.df_indices = carregar_dados_iniciais()


def processar_regulamentos(lista_fundos):

    headers = conectar('wRGlvlj1bOW3', 'l4riAuRd0CUL','wRGlvlj1bOW3:l4riAuRd0CUL', url)  
    st.write("Processando dados cadastro Geral")
    df_cadastro = df_cadastro_geral()
    lista = df_cadastro[['codigo_fundo','nome_comercial_fundo','identificador_fundo']][df_cadastro['identificador_fundo'].isin(lista_fundos)].reset_index(drop=True)
    
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
        st.write(fundo_det_cadastro['nome_comercial_fundo'])
              
        df_documentos =  pd.json_normalize(fundos_det_json, record_path=['documentos'], meta=['codigo_fundo'], sep=' : ')
        pdf_url = df_documentos.url[0]
        conteudo_pdf = baixar_pdf(pdf_url, headers)
        #.write(conteudo_pdf)
        if conteudo_pdf:
            st.download_button(label="Baixar Regulamento PDF", data=conteudo_pdf, file_name=f'Regulamento_Fundo_{codigo_fundo}.pdf', mime='application/pdf')
            with open(f'Regulamento_Fundo_{codigo_fundo}.pdf', "wb") as f:
                f.write(conteudo_pdf)
            open_pdf_js = """
                <script>
                    function openPDF() {
                            const link = document.createElement('a');
                            link.href = f'Regulamento_Fundo_{codigo_fundo}.pdf';
                            link.target = '_blank';
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                            }
                    window.onload = openPDF;
                </script>
            """
            st.markdown(open_pdf_js, unsafe_allow_html=True)

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
        
       
        df_documentos =  pd.json_normalize(fundos_det_json, record_path=['documentos'], meta=['codigo_fundo'], sep=' : ')
        pdf_url = df_documentos.url[0]
        conteudo_pdf = baixar_pdf(pdf_url, headers)
        #.write(conteudo_pdf)
        if conteudo_pdf:
            #st.download_button(label="Baixar Regulamento PDF", data=conteudo_pdf, file_name=f'Regulamento_Fundo_{codigo_fundo}.pdf', mime='application/pdf')
            with open(f'Regulamento_Fundo_{codigo_fundo}.pdf', "wb") as f:
                f.write(conteudo_pdf)
            open_pdf_js = """
                <script>
                    function openPDF() {
                            const link = document.createElement('a');
                            link.href = f'Regulamento_Fundo_{codigo_fundo}.pdf';
                            link.target = '_blank';
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                            }
                    window.onload = openPDF;
                </script>
            """
            st.markdown(open_pdf_js, unsafe_allow_html=True)
        
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
    
    if destaque_sicredi == True:               
        fundo_sicredi = df_fundos_classes.loc[df_fundos_classes['nome_comercial_classe'].str.contains('SICREDI')].reset_index().nome_comercial_classe[0]
        color_map = {nome_comercial_classe: '#64C832' if 'SICREDI' in nome_comercial_classe  else 'rgba(128, 128, 128, 0.25)' for nome_comercial_classe in df_fundos_classes['nome_comercial_classe'].unique()}
        color_map2 = {nome_comercial_classe: '#64C832' if 'SICREDI' in nome_comercial_classe  else 'rgba(128, 128, 128, 0.5)' for nome_comercial_classe in df_fundos_classes['nome_comercial_classe'].unique()}

    else:
        #fundo_sicredi = df_fundos_classes.loc[df_fundos_classes['nome_comercial_classe'].str.contains('SICREDI')].reset_index().nome_comercial_classe[0]
        color_list = px.colors.qualitative.Plotly
        color_map = {}
        color_index = 0
        sicredi = 0
        for nome_comercial_classe in df_fundos_classes['nome_comercial_classe'].unique():
                if 'SICREDI' in nome_comercial_classe and sicredi==0:
                    color_map[nome_comercial_classe] = '#64C832'  # Cor específica para SICREDI
                    sicredi=1
                else:
                    color_map[nome_comercial_classe] = color_list[color_index % len(color_list)]
                    color_index += 1
        color_map2 = color_map           
        
        # = {nome_comercial_classe: '#64C832' if 'SICREDI' in nome_comercial_classe 
        #             else color_list[df_fundos_classes['nome_comercial_classe'].unique().index % len(color_list)] 
        #                             for nome_comercial_classe in df_fundos_classes['nome_comercial_classe'].unique()}
        #color_map2 = {nome_comercial_classe: '#64C832' if 'SICREDI' in nome_comercial_classe  else 'rgba(128, 128, 128, 0.5)' for nome_comercial_classe in df_fundos_classes['nome_comercial_classe'].unique()}

        

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
    patrimonio_inicial = df_hist_classe_sub.groupby('nome_comercial_classe').apply(lambda x: x.loc[x['data_competencia'].idxmin(), 'valor_patrimonio_liquido']).to_dict() 
    df_hist_classe_sub['captacao_acumulada_pl'] = df_hist_classe_sub.apply( lambda row: row['captacao_acumulada'] / patrimonio_inicial[row['nome_comercial_classe']], axis=1 )
    df_hist_classe_sub['resgate_acumulado_pl'] = df_hist_classe_sub.apply( lambda row: row['resgate_acumulado'] / patrimonio_inicial[row['nome_comercial_classe']], axis=1 )
    df_hist_classe_sub['captacao_liquida_acumulada_pl'] = df_hist_classe_sub['captacao_acumulada_pl'] -df_hist_classe_sub['resgate_acumulado_pl']
    num_cotistas_inicial = df_hist_classe_sub.groupby('nome_comercial_classe').apply(lambda x: x.loc[x['data_competencia'].idxmin(), 'numero_cotistas']).to_dict() 
    df_hist_classe_sub['evolucao_num_cotistas'] = df_hist_classe_sub.apply( lambda row: row['numero_cotistas'] / num_cotistas_inicial[row['nome_comercial_classe']], axis=1 )-1
    ticket_medio_inicial = df_hist_classe_sub.groupby('nome_comercial_classe').apply(lambda x: x.loc[x['data_competencia'].idxmin(), 'ticket_medio']).to_dict() 
    df_hist_classe_sub['evolucao_ticket_medio'] = df_hist_classe_sub.apply( lambda row: row['ticket_medio'] / ticket_medio_inicial[row['nome_comercial_classe']], axis=1 )-1
    patrimonio_total = df_hist_classe_sub.groupby('data_competencia')['valor_patrimonio_liquido'].sum()
    df_hist_classe_sub['percetual_patrimonio_total'] = df_hist_classe_sub['valor_patrimonio_liquido']/df_hist_classe_sub['data_competencia'].map(patrimonio_total)  
    captacao_total = df_hist_classe_sub.groupby('data_competencia')['captacao_liquida_acumulada'].sum()
    df_hist_classe_sub['percetual_captacao_total'] = df_hist_classe_sub['captacao_liquida_acumulada']/df_hist_classe_sub['data_competencia'].map(captacao_total)  
    num_cotistas_total = df_hist_classe_sub.groupby('data_competencia')['numero_cotistas'].sum()
    df_hist_classe_sub['percetual_captacao_total'] = df_hist_classe_sub['numero_cotistas']/df_hist_classe_sub['data_competencia'].map(num_cotistas_total) 
    
    #color_map, color_map2, df_hist_classe_sub
    st.session_state.write_cache = []
    
    ####### Dataframe de Retornos ##########
    df_returns = df_hist_classe_sub.sort_values('nome_fantasia', ascending=True) .pivot(index='data_competencia', columns='nome_fantasia', values='valor_cota')
    
    
    returns = df_returns.pct_change().dropna()
    returns_ano = returns.resample('Y').agg(lambda x: (x + 1).prod()- 1)
    df = returns_ano
    list(df.columns.values)
    df['data_referencia'] = df.index
    df = pd.melt(df, id_vars=['data_referencia'], value_vars=list(df.columns.values),
            var_name='nome_fantasia', value_name='return')
    st.write(f"Concluio")    
    return color_map, color_map2, df_hist_classe_sub, returns \
          , df_fundo_geral, df_fundo_taxa_g, df_fundo_classe_g, df_classe_geral
        





##########                             #######  
########## Configurações do Streamlite #######
##########                             #######  



# Menus de Entrada
st.sidebar.header('Parâmetros de Entrada')

# Data Inicial e Final
data_inicial = st.sidebar.date_input('Data Inicial', datetime.date(2024, 1, 1))
data_final = st.sidebar.date_input('Data Final', datetime.datetime.now())

# Lista Fundos Padrão
lista_fundos_nome = st.sidebar.selectbox('Selecione a Lista de Fundos', list(lista_fundos.keys()))
fundo_selecionado = lista_fundos[lista_fundos_nome]

# Indicador
#indicador_padrao= "CDI"  # Substitua pelo valor padrão desejado
indicador_lista = st.session_state.df_indices['indice'].unique()
indicador_selecionado = st.sidebar.selectbox('Selecione o Indicador', indicador_lista)
indicador_tipo = st.sidebar.selectbox('Tipo de Indicador', ['Percentual','Indice+','Indice+ a.a.','Absoluto'])
#if indicador_padrao in indicador_lista:
#indicador_selecionado = st.sidebar.multiselect('Selecione o Indicador', df_indices.columns)
#indicador_selecionado = st.sidebar.selectbox('Selecione o Indicador', indicador_lista)
#indicador_selecionado = 'DOL'

# Checkbox para Baixar Regulamento
baixar_regulamento = st.sidebar.checkbox('Baixar Regulamento')
destaque_sicredi = st.sidebar.checkbox('Destaca Fundos Sicredi')

# Botão "Rodar"
if st.sidebar.button('Rodar'):
    st.session_state.color_map_fundos, st.session_state.color_map2, st.session_state.df_hist_classe_sub, \
    st.session_state.returns , \
    st.session_state.df_fundo_geral, st.session_state.df_fundo_taxa_g, st.session_state.df_fundo_classe_g, \
    st.session_state.df_classe_geral   = processar_dados(data_inicial, data_final, fundo_selecionado, indicador_selecionado)
    st.session_state.df_indicadores = carrega_indicadores(data_inicial, data_final)
    
    st.session_state.df_indicadores_filtro =   st.session_state.df_indicadores[ st.session_state.df_indicadores['indice'] == indicador_selecionado]
    st.session_state.df_indicadores_filtro =  st.session_state.df_indicadores_filtro.pivot_table(index='data_competencia', columns='indice', values='variacao_diaria', aggfunc='sum')

    st.session_state.df_returns = pd.merge(st.session_state.returns,st.session_state.df_indicadores_filtro, on='data_competencia', how='inner')
    st.session_state.returns_mes = st.session_state.df_returns.resample('M').agg(lambda x: (x + 1).prod()- 1)
    st.session_state.returns_semana = st.session_state.df_returns.resample('W').agg(lambda x: (x + 1).prod()- 1)
    st.session_state.returns_ano = st.session_state.df_returns.resample('Y').agg(lambda x: (x + 1).prod()- 1)
    st.session_state.returns_total = st.session_state.df_returns.agg(lambda x: (x + 1).prod()- 1)
    st.session_state.return_acum = (1 + st.session_state.df_returns).cumprod()
    #st.session_state.return_acum_semana = (1 + st.session_state.returns_semana).cumprod()
    #st.session_state.return_acum_mes = (1 + st.session_state.returns_mes).cumprod()
    

# Botão "Rodar"
if st.sidebar.button('Rodar Indicadores'): 
    st.session_state.df_indicadores = carrega_indicadores(data_inicial, data_final)
    st.write(data_inicial)
    st.session_state.df_indicadores_filtro =   st.session_state.df_indicadores[ st.session_state.df_indicadores['indice'] == indicador_selecionado]
    st.session_state.df_indicadores_filtro =  st.session_state.df_indicadores_filtro.pivot_table(index='data_competencia', columns='indice', values='variacao_diaria', aggfunc='sum')

    st.session_state.df_returns = pd.merge(st.session_state.returns,st.session_state.df_indicadores_filtro, on='data_competencia', how='inner')
    st.session_state.returns_mes = st.session_state.df_returns.resample('M').agg(lambda x: (x + 1).prod()- 1)
    st.session_state.returns_semana = st.session_state.df_returns.resample('W').agg(lambda x: (x + 1).prod()- 1)
    st.session_state.returns_ano = st.session_state.df_returns.resample('Y').agg(lambda x: (x + 1).prod()- 1)
    st.session_state.returns_total = st.session_state.df_returns.agg(lambda x: (x + 1).prod()- 1)
    st.session_state.return_acum = (1 + st.session_state.df_returns).cumprod()     




num_colunas= 5    
height_screening = 4200
# Links de Visualizações
st.sidebar.subheader('Páginas de Visualização')

pagina_selecionada = st.sidebar.selectbox('Selecione a Página', 
                                          ['Comparativos de Classes', 'Comparativos de Fundos',
                                           'Rentabilidade', 
                                           'Patrimônio Líquido e Captação', 'Sensibilidade do Passivo','Performance', 
                                           'Regulamento e Documentação', 'Patrimônio Líquido e Captação II',
                                           
                                           'Volatilidade', 
                                           'Histórico de Carteiras','TESTE','Comparativos de Classes III',
                                            'Comparativos de Classes IV','Comparativos Fundos',])


# Exibir Páginas de Visualização separadamente
if pagina_selecionada == 'Comparativos de Classes':
    st.header("Comparativos de Classes I")
      # Personalize a exibição
    df_fundo_geral = st.session_state.df_fundo_geral
    df_fundo_classe_g = st.session_state.df_fundo_classe_g
    df_fundo_taxa_g = st.session_state.df_fundo_taxa_g
    df_classe_geral = st.session_state.df_classe_geral
    df_classe_geral = rearrange_columns(df_classe_geral, 'nome_comercial_classe')
    
    opt.column_filters = 'footer'
    opt.fixedColumns = {"leftColumns": num_colunas}
    opt.classes = ["display", "nowrap"]
    
    html_table = to_html_datatable(
            df_classe_geral,
            #dom="Plfrtip",
            layout={ "top1": "searchPanes", "top2": "searchBuilder"},
            
            select={"style": "multi"},
            searchPanes={"layout": f"columns-{num_colunas}", "cascadePanes": True,"dtOpts": {"select": {"style": "single"}}, "collapsed": True ,
                         "columns": [i for i, col in enumerate(df_classe_geral.columns) if col not in ['taxa_adicionais','taxa_performance.informacoes_adicionais']]
                         }, # {"style": "single"}
            options={"fixedColumns": {"leftColumns": 1}, "scrollX": True,"scrollY": "400px","pageLength": 50, "columnDefs": {"width": "10px", "targets": 0},
                     "dom": 'Bfrtip',  "buttons": ["copyHtml5", "csvHtml5", "excelHtml5"]},
            buttons=["copyHtml5", "csvHtml5", "excelHtml5","pageLength"],
        )   # adjust manually
    
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
    html(html_table,height=height_screening)



elif pagina_selecionada == 'Comparativos de Fundos':
    st.header("Comparativos de Fundos")
      # Personalize a exibição
    df_fundo_geral = st.session_state.df_fundo_geral
    df_fundo_classe_g = st.session_state.df_fundo_classe_g
    df_fundo_taxa_g = st.session_state.df_fundo_taxa_g
    df_classe_geral = st.session_state.df_classe_geral
    df_fundo_geral = rearrange_columns(df_fundo_geral, 'nome_comercial_fundo')
    
    opt.column_filters = 'footer'
    opt.fixedColumns = {"leftColumns": num_colunas}
    opt.classes = ["display", "nowrap"]
    
    html_table = to_html_datatable(
            df_fundo_geral,
            #dom="Plfrtip",
            layout={ "top1": "searchPanes", "top2": "searchBuilder"},
            
            select={"style": "multi"},
            searchPanes={"layout": f"columns-{num_colunas}", "cascadePanes": True,"dtOpts": {"select": {"style": "single"}}, "collapsed": True ,
                         "columns": [i for i, col in enumerate(df_classe_geral.columns) if col not in ['taxa_adicionais','taxa_performance.informacoes_adicionais']]
                         }, # {"style": "single"}
            options={"fixedColumns": {"leftColumns": 1}, "scrollX": True,"scrollY": "400px","pageLength": 50, "columnDefs": {"width": "10px", "targets": 0},
                     "dom": 'Bfrtip',  "buttons": ["copyHtml5", "csvHtml5", "excelHtml5"]},
            buttons=["copyHtml5", "csvHtml5", "excelHtml5","pageLength"],
        )   # adjust manually
    
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
    html(html_table,height=height_screening)    

elif pagina_selecionada == 'Comparativos de Classes III':
    st.header("Comparativos de Classes III")
      # Personalize a exibição
    df_fundo_geral = st.session_state.df_fundo_geral
    df_fundo_classe_g = st.session_state.df_fundo_classe_g
    df_fundo_taxa_g = st.session_state.df_fundo_taxa_g
    df_classe_geral = st.session_state.df_classe_geral
    
    #df_classe_geral = df_classe_geral.loc[:, ~df_classe_geral.columns.str.contains('data')]
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
        fit_columns_on_grid_load=False)
    


elif pagina_selecionada == 'Comparativos de Classes IV':
    st.header("Comparativos de Classes III")
      # Personalize a exibição
    df_fundo_geral = st.session_state.df_fundo_geral
    df_fundo_classe_g = st.session_state.df_fundo_classe_g
    df_fundo_taxa_g = st.session_state.df_fundo_taxa_g
    df_classe_geral = st.session_state.df_classe_geral
    viz_spec = r"""{"config":[{"config":{"defaultAggregated":false,"geoms":["bar"],"coordSystem":"generic","limit":-1,"timezoneDisplayOffset":0},"encodings":{"dimensions":[{"fid":"codigo_classe","name":"codigo_classe","basename":"codigo_classe","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"identificador_classe","name":"identificador_classe","basename":"identificador_classe","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"nome_comercial_classe","name":"nome_comercial_classe","basename":"nome_comercial_classe","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"data_inicio_atividade_classe","name":"data_inicio_atividade_classe","basename":"data_inicio_atividade_classe","semanticType":"temporal","analyticType":"dimension","offset":0},{"fid":"tributacao_perseguida","name":"tributacao_perseguida","basename":"tributacao_perseguida","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"alavancado","name":"alavancado","basename":"alavancado","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"credito_privado","name":"credito_privado","basename":"credito_privado","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"investimento_exterior","name":"investimento_exterior","basename":"investimento_exterior","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"foco_atuacao","name":"foco_atuacao","basename":"foco_atuacao","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"fundo_esg","name":"fundo_esg","basename":"fundo_esg","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"forma_condominio","name":"forma_condominio","basename":"forma_condominio","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"entidade_investimento_fins_tributarios","name":"entidade_investimento_fins_tributarios","basename":"entidade_investimento_fins_tributarios","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"infraestrutura","name":"infraestrutura","basename":"infraestrutura","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"responsabilidade_limitada","name":"responsabilidade_limitada","basename":"responsabilidade_limitada","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"categoria_cvm","name":"categoria_cvm","basename":"categoria_cvm","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"composicao","name":"composicao","basename":"composicao","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"tipo_anbima","name":"tipo_anbima","basename":"tipo_anbima","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"nivel1_categoria","name":"nivel1_categoria","basename":"nivel1_categoria","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"nivel2_categoria","name":"nivel2_categoria","basename":"nivel2_categoria","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"nivel3_subcategoria","name":"nivel3_subcategoria","basename":"nivel3_subcategoria","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"95_por_cento_fundo_isento","name":"95_por_cento_fundo_isento","basename":"95_por_cento_fundo_isento","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"subclasses","name":"subclasses","basename":"subclasses","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"taxa_performance","name":"taxa_performance","basename":"taxa_performance","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"perfil_complementar.codigo_b3","name":"perfil_complementar.codigo_b3","basename":"perfil_complementar.codigo_b3","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"perfil_complementar.restricao_investimento","name":"perfil_complementar.restricao_investimento","basename":"perfil_complementar.restricao_investimento","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"perfil_complementar.tipo_investidor","name":"perfil_complementar.tipo_investidor","basename":"perfil_complementar.tipo_investidor","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"perfil_complementar.aplicacao_automatica","name":"perfil_complementar.aplicacao_automatica","basename":"perfil_complementar.aplicacao_automatica","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"perfil_complementar.plano_previdencia","name":"perfil_complementar.plano_previdencia","basename":"perfil_complementar.plano_previdencia","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"perfil_complementar.periodicidade_envio_pl_cota","name":"perfil_complementar.periodicidade_envio_pl_cota","basename":"perfil_complementar.periodicidade_envio_pl_cota","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"perfil_complementar.calculo_cota","name":"perfil_complementar.calculo_cota","basename":"perfil_complementar.calculo_cota","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"valores_minimos_movimentacao_classe.indicador_prazo_emissao_cota","name":"valores_minimos_movimentacao_classe.indicador_prazo_emissao_cota","basename":"valores_minimos_movimentacao_classe.indicador_prazo_emissao_cota","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"valores_minimos_movimentacao_classe.prazo_emissao_cota","name":"valores_minimos_movimentacao_classe.prazo_emissao_cota","basename":"valores_minimos_movimentacao_classe.prazo_emissao_cota","semanticType":"quantitative","analyticType":"dimension","offset":0},{"fid":"valores_minimos_movimentacao_classe.indicador_prazo_conversao_resgate","name":"valores_minimos_movimentacao_classe.indicador_prazo_conversao_resgate","basename":"valores_minimos_movimentacao_classe.indicador_prazo_conversao_resgate","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"valores_minimos_movimentacao_classe.prazo_conversao_resgate","name":"valores_minimos_movimentacao_classe.prazo_conversao_resgate","basename":"valores_minimos_movimentacao_classe.prazo_conversao_resgate","semanticType":"quantitative","analyticType":"dimension","offset":0},{"fid":"valores_minimos_movimentacao_classe.indicador_prazo_pagamento_resgate","name":"valores_minimos_movimentacao_classe.indicador_prazo_pagamento_resgate","basename":"valores_minimos_movimentacao_classe.indicador_prazo_pagamento_resgate","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"valores_minimos_movimentacao_classe.prazo_pagamento_resgate","name":"valores_minimos_movimentacao_classe.prazo_pagamento_resgate","basename":"valores_minimos_movimentacao_classe.prazo_pagamento_resgate","semanticType":"quantitative","analyticType":"dimension","offset":0},{"fid":"valores_minimos_movimentacao_classe.regra_adicional_pagamento_resgate","name":"valores_minimos_movimentacao_classe.regra_adicional_pagamento_resgate","basename":"valores_minimos_movimentacao_classe.regra_adicional_pagamento_resgate","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"valores_minimos_movimentacao_classe.data_atualizacao","name":"valores_minimos_movimentacao_classe.data_atualizacao","basename":"valores_minimos_movimentacao_classe.data_atualizacao","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"taxa_tipo","name":"taxa_tipo","basename":"taxa_tipo","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"taxa_perfil","name":"taxa_perfil","basename":"taxa_perfil","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"taxa_vl_monetario","name":"taxa_vl_monetario","basename":"taxa_vl_monetario","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"taxa_vl_fixo","name":"taxa_vl_fixo","basename":"taxa_vl_fixo","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"taxa_vl_maxima","name":"taxa_vl_maxima","basename":"taxa_vl_maxima","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"taxa_adicionais","name":"taxa_adicionais","basename":"taxa_adicionais","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"sufixo","name":"sufixo","basename":"sufixo","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"benchmark","name":"benchmark","basename":"benchmark","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"tipo_fundo","name":"tipo_fundo","basename":"tipo_fundo","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"atributo_fundo","name":"atributo_fundo","basename":"atributo_fundo","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"administrador","name":"administrador","basename":"administrador","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"gestor","name":"gestor","basename":"gestor","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"gw_mea_key_fid","name":"Measure names","analyticType":"dimension","semanticType":"nominal"}],"measures":[{"fid":"percentual_permitido_credito_privado","name":"percentual_permitido_credito_privado","basename":"percentual_permitido_credito_privado","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"percentual_permitido_investimento_exterior","name":"percentual_permitido_investimento_exterior","basename":"percentual_permitido_investimento_exterior","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"valores_minimos_movimentacao_classe.dias_carencia_inicial","name":"valores_minimos_movimentacao_classe.dias_carencia_inicial","basename":"valores_minimos_movimentacao_classe.dias_carencia_inicial","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"valores_minimos_movimentacao_classe.dias_carencia_ciclica","name":"valores_minimos_movimentacao_classe.dias_carencia_ciclica","basename":"valores_minimos_movimentacao_classe.dias_carencia_ciclica","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"valores_minimos_movimentacao_classe.valor_minimo_aplicacao_inicial","name":"valores_minimos_movimentacao_classe.valor_minimo_aplicacao_inicial","basename":"valores_minimos_movimentacao_classe.valor_minimo_aplicacao_inicial","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"valores_minimos_movimentacao_classe.valor_minimo_aplicacao_subsequente","name":"valores_minimos_movimentacao_classe.valor_minimo_aplicacao_subsequente","basename":"valores_minimos_movimentacao_classe.valor_minimo_aplicacao_subsequente","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"valores_minimos_movimentacao_classe.valor_minimo_resgate","name":"valores_minimos_movimentacao_classe.valor_minimo_resgate","basename":"valores_minimos_movimentacao_classe.valor_minimo_resgate","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"valores_minimos_movimentacao_classe.valor_minimo_permanencia","name":"valores_minimos_movimentacao_classe.valor_minimo_permanencia","basename":"valores_minimos_movimentacao_classe.valor_minimo_permanencia","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"taxa_percentual","name":"taxa_percentual","basename":"taxa_percentual","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"taxa_vl_piso","name":"taxa_vl_piso","basename":"taxa_vl_piso","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"taxa_perc_maxima","name":"taxa_perc_maxima","basename":"taxa_perc_maxima","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"gw_count_fid","name":"Row count","analyticType":"measure","semanticType":"quantitative","aggName":"sum","computed":true,"expression":{"op":"one","params":[],"as":"gw_count_fid"}},{"fid":"gw_mea_val_fid","name":"Measure values","analyticType":"measure","semanticType":"quantitative","aggName":"sum"}],"rows":[{"fid":"administrador","name":"administrador","basename":"administrador","semanticType":"nominal","analyticType":"dimension","offset":0}],"columns":[{"fid":"taxa_percentual","name":"taxa_percentual","basename":"taxa_percentual","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"percentual_permitido_investimento_exterior","name":"percentual_permitido_investimento_exterior","basename":"percentual_permitido_investimento_exterior","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"percentual_permitido_credito_privado","name":"percentual_permitido_credito_privado","basename":"percentual_permitido_credito_privado","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0}],"color":[],"opacity":[],"size":[],"shape":[],"radius":[],"theta":[],"longitude":[],"latitude":[],"geoId":[],"details":[],"filters":[],"text":[]},"layout":{"showActions":false,"showTableSummary":false,"stack":"none","interactiveScale":false,"zeroScale":true,"size":{"mode":"auto","width":320,"height":200},"format":{},"geoKey":"name","resolve":{"x":false,"y":false,"color":false,"opacity":false,"shape":false,"size":false}},"visId":"gw_xpZB","name":"Chart 1"}],"chart_map":{},"workflow_list":[{"workflow":[{"type":"view","query":[{"op":"raw","fields":["administrador","taxa_percentual","percentual_permitido_investimento_exterior","percentual_permitido_credito_privado"]}]}]}],"version":"0.4.9.1"}"""
    pyg_html = pyg.to_html(df_classe_geral, spec=viz_spec)
    st.components.v1.html(pyg_html, height=600)
    #pyg_app = StreamlitRenderer(df_classe_geral)
    #pyg_app.explorer(vis_spec=viz_spec)
    
   
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

elif pagina_selecionada == 'Regulamento e Documentação':
    st.header("Histórico de Carteiras")
    headers = conectar('wRGlvlj1bOW3', 'l4riAuRd0CUL','wRGlvlj1bOW3:l4riAuRd0CUL', url)  
    st.write("Processando dados cadastro Geral")
    df_cadastro = df_cadastro_geral()
    lista = df_cadastro[['codigo_fundo','nome_comercial_fundo','identificador_fundo']][df_cadastro['identificador_fundo'].isin(fundo_selecionado)].reset_index(drop=True)
    
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
              
        df_documentos =  pd.json_normalize(fundos_det_json, record_path=['documentos'], meta=['codigo_fundo'], sep=' : ')
        st.write(fundo_det_cadastro['nome_comercial_fundo'][0])
        st.dataframe(df_documentos)
        pdf_url = df_documentos.url[0]
        conteudo_pdf = baixar_pdf(pdf_url, headers)
        #.write(conteudo_pdf)
        if conteudo_pdf:
            st.download_button(label="Baixar Regulamento PDF", data=conteudo_pdf, file_name=f'Regulamento_Fundo_{codigo_fundo}.pdf', mime='application/pdf')
            with open('Regulamento.pdf', "wb") as f:
                f.write(conteudo_pdf)
            open_pdf_js = """
                <script>
                    function openPDF() {
                            const link = document.createElement('a');
                            link.href = 'Regulamento.pdf';
                            link.target = '_blank';
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                            }
                    window.onload = openPDF;
                </script>
            """
            st.markdown(open_pdf_js, unsafe_allow_html=True)
            
            download_js = f"""
                <script>
                    function downloadPDF() {{
                        const link = document.createElement('a');
                        link.href = 'Regulamento.pdf';
                        link.download = 'Regulamento_Fundo_{codigo_fundo}.pdf';
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                    }}
                    window.onload = downloadPDF;
                </script>
            """
        
            # Exiba o JavaScript no Streamlit
            st.markdown(download_js, unsafe_allow_html=True)
        
elif pagina_selecionada == 'TESTE2':
    st.header("Histórico de Carteiras")
    st.write("Exibir histórico de carteiras aqui...") 
    dt2 = (data_inicial+timedelta(days=-10)).strftime('%Y-%m-%d') # Personalize a exibição
    select = f"""select * from (
    SELECT DATA as data_competencia, INDICE as indice, VARIACAO_DIARIA/100 as variacao_diaria  FROM DL_GESTAO_RECURSOS.ANBIMA_indices
    UNION
    SELECT DATA as data_competencia, CODINDEX AS indice, case when codindex = 'CDI' then VALOR/3000 else  VALOR/LAG(VALOR, 1) OVER (PARTITION BY CODINDEX ORDER BY DATA)-1 end AS variacao_diaria 
    FROM DL_GESTAO_RECURSOS.IDX_INDEX
    WHERE CODINDEX in ('BETAIMA5',	'BOLSAAL',	'BRENT',	'CDI',	'DOL',	'DOLREFER',	'DXY',	'EURO',	'IBOVESPA',	'IDI',	'IHFA',	'IMESTRAT',	'INDESSCO',	'INDPETR4',	'ISE',	'ISE CDI',	'ISE CDI1',	'IVBX-2',	'PRTIPCA',	'SFFC',	'SP ESG',	'SP500',	'STFRFCP',	'TRESUR10',	'WTI')
    and VALOR <> 0
    ) tab where data_competencia between '{(data_inicial+timedelta(days=-10)).strftime('%Y-%m-%d')}' and '{data_final.strftime('%Y-%m-%d')}'
    """
    Exec = teradata.UdaExec(appName="TESTE", version="1.0", logConsole=False)
    session = Exec.connect(method="odbc", system="teradbAWS.sicredi.net",
            username="P_USR_DL_GESTAO_RECURSOS", password="JAW0b71329aadade35365afc6X", Authentication="TDNEGO");
    st.session_state.df_indicadores = pd.read_sql(select, session) 
    #df_indicadores.data_competencia = pd.to_datetime(df_indicadores.data_competencia , format='%Y-%m-%d')
    #st.session_state.df_indicadores_filtro =   st.session_state.df_indicadores[ st.session_state.df_indicadores['indice'] == indicador_selecionado]
    #st.session_state.df_indicadores_filtro =  st.session_state.df_indicadores_filtro.pivot_table(index='data_competencia', columns='indice', values='variacao_diaria', aggfunc='sum')
    df_indicadores = st.session_state.df_indicadores
    df_indicadores_filtro =  df_indicadores[ st.session_state.df_indicadores['indice'] == indicador_selecionado]
    df_indicadores_filtro =  df_indicadores_filtro.pivot_table(index='data_competencia', columns='indice', values='variacao_diaria', aggfunc='sum')
    df_indicadores2 = st.session_state.df_indicadores_filtro
    returns = st.session_state.returns
    return_acum = st.session_state.return_acum
    df_returns =  st.session_state.df_returns
    #df_indicadores_filtro =  st.session_state.df_indicadores_filtro
    st.write(select)
    st.dataframe(df_indicadores2
                 )
    st.dataframe(df_returns
                 )
    st.dataframe(returns
                 )
    
elif pagina_selecionada == 'Rentabilidade':
    height=850
    width=1050
    st.header("Rentabilidade")
    #returns = st.session_state.df_returns
    returns = st.session_state.df_returns
    return_acum = st.session_state.return_acum
    returns_mes = st.session_state.returns_mes
    color_map = st.session_state.color_map_fundos
    # Retornoo Fundos + Indice
    fig = px.line(return_acum
                       , title='Rentabilidade Acumulada',color_discrete_map=color_map
                       , height=height
                       , width=width)
    st.plotly_chart(fig)
    fig2 = px.scatter(returns_mes*100                       
                       , title='Retornos Mensais', color_discrete_map=color_map
                       , height=height
                       , width=width)
    fig2.update_traces(marker=dict(size=10))
    st.plotly_chart(fig2)
    # Grafico Risco Retorno Absoluto
    N = len(return_acum)
    return_anualizado = return_acum.iloc[-1,] ** (252 / N) - 1
       
    
    dev_pad_ano = returns.std() * np.sqrt(252)
    
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
               , height=height
               , width=width)
               
    st.plotly_chart(fig3)
    
    # retorno Indice +
    return_acum_ind = return_acum.sub(return_acum[indicador_selecionado], axis=0).drop(columns=[indicador_selecionado])
    fig = px.line(return_acum_ind
                       , title='Rentabilidade Acumulada (' + indicador_selecionado + ' +)', color_discrete_map=color_map
                       , height=height
                       , width=width)
    st.plotly_chart(fig)    
    
    # Grafico Risco Indice +
    N = len(return_acum_ind)
    return_anualizado =(return_acum_ind.iloc[-1,] +1 )** (252/ N) - 1
    
    dev_pad_ano = returns.drop(columns=[indicador_selecionado]).std() * np.sqrt(252) 
    
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
               , height=height
               , width=width)    
    st.plotly_chart(fig3)    
    
    return_acum_ind = return_acum -1
    return_acum_ind = return_acum_ind.div(return_acum_ind[indicador_selecionado], axis=0).drop(columns=[indicador_selecionado])
    fig = px.line(return_acum_ind
                       , title='Rentabilidade Acumulada (%' + indicador_selecionado + ')', color_discrete_map=color_map
                       , height=height
                       , width=width)
    st.plotly_chart(fig)
    
elif pagina_selecionada == 'Patrimônio Líquido e Captação':
    
    st.header("Patrimônio Líquido e Captação")
    st.write("Comparativos de PL, Captação, número cotistas e outros")  # Personalize a exibição
    st.session_state.write_cache = []
    df_hist_classe_sub = st.session_state.df_hist_classe_sub
    color_map = st.session_state.color_map_fundos
    
    fig =plot_historico(df_hist_classe_sub, variables=['valor_patrimonio_liquido','numero_cotistas', 'ticket_medio'], title='Patrimonio Líquido, Num. Cotista e Ticket Médio', resample='W')
    st.plotly_chart(fig)
    fig2 = plot_historico(df_hist_classe_sub, variables=['captacao_acumulada','resgate_acumulado','captacao_liquida_acumulada'], title='Captação Acumulada', resample='W')
    st.plotly_chart(fig2)
    fig3 = plot_historico(df_hist_classe_sub, variables=['captacao_movel','resgate_movel','captacao_liquida_movel'], title='Captação e Resgates - Móvel 20du', resample='W')
    st.plotly_chart(fig3)
    fig4 = plot_historico(df_hist_classe_sub, variables=['captacao_pl','resgate_pl','captacao_liquida_pl'], title='Captação e Resgates em %PL - Semanas', resample='W')
    st.plotly_chart(fig4)
    fig5 = plot_historico(df_hist_classe_sub, variables=['captacao_acumulada_pl','resgate_acumulado_pl','captacao_liquida_acumulada_pl','evolucao_num_cotistas','evolucao_ticket_medio'], title='Captação e Resgates em %PL - Semanas', resample='W')
    st.plotly_chart(fig5)
    #fig4 = plot_historico(df_hist_classe_sub, variables=['captacao_pl','resgate_pl','captacao_liquida_pl'], title='Captação e Resgates em %PL - Semanas', resample='W')
    #st.plotly_chart(fig4)    

elif pagina_selecionada == 'Patrimônio Líquido e Captação II':
    
    st.header("Patrimônio Líquido e Captação")
    st.write("Comparativos de PL, Captação, número cotistas e outros")  # Personalize a exibição
    st.session_state.write_cache = []
    df_hist_classe_sub = st.session_state.df_hist_classe_sub
    color_map = st.session_state.color_map
    vis_spec = r"""{"config":[{"config":{"defaultAggregated":true,"geoms":["bar"],"coordSystem":"generic","limit":-1,"timezoneDisplayOffset":0},"encodings":{"dimensions":[{"fid":"nome_comercial_classe","name":"nome_comercial_classe","basename":"nome_comercial_classe","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"nome_comercial_fundo","name":"nome_comercial_fundo","basename":"nome_comercial_fundo","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"codigo_fundo","name":"codigo_fundo","basename":"codigo_fundo","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"codigo_classe","name":"codigo_classe","basename":"codigo_classe","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"codigo_subclasse","name":"codigo_subclasse","basename":"codigo_subclasse","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"codigo_moeda","name":"codigo_moeda","basename":"codigo_moeda","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"data_competencia","name":"data_competencia","basename":"data_competencia","semanticType":"temporal","analyticType":"dimension","offset":0},{"fid":"data_atualizacao","name":"data_atualizacao","basename":"data_atualizacao","semanticType":"temporal","analyticType":"dimension","offset":0},{"fid":"nome_fantasia","name":"nome_fantasia","basename":"nome_fantasia","semanticType":"nominal","analyticType":"dimension","offset":0},{"fid":"gw_mea_key_fid","name":"Measure names","analyticType":"dimension","semanticType":"nominal"}],"measures":[{"fid":"valor_patrimonio_liquido","name":"valor_patrimonio_liquido","basename":"valor_patrimonio_liquido","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"valor_cota","name":"valor_cota","basename":"valor_cota","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"valor_volume_total_aplicacoes","name":"valor_volume_total_aplicacoes","basename":"valor_volume_total_aplicacoes","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"valor_volume_total_resgates","name":"valor_volume_total_resgates","basename":"valor_volume_total_resgates","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"valor_volume_total_resgate_ir","name":"valor_volume_total_resgate_ir","basename":"valor_volume_total_resgate_ir","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"numero_cotistas","name":"numero_cotistas","basename":"numero_cotistas","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"ticket_medio","name":"ticket_medio","basename":"ticket_medio","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"captacao_acumulada","name":"captacao_acumulada","basename":"captacao_acumulada","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"resgate_acumulado","name":"resgate_acumulado","basename":"resgate_acumulado","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"captacao_liquida_acumulada","name":"captacao_liquida_acumulada","basename":"captacao_liquida_acumulada","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"captacao_movel","name":"captacao_movel","basename":"captacao_movel","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"resgate_movel","name":"resgate_movel","basename":"resgate_movel","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"captacao_liquida_movel","name":"captacao_liquida_movel","basename":"captacao_liquida_movel","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"captacao_liquida","name":"captacao_liquida","basename":"captacao_liquida","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"captacao_pl","name":"captacao_pl","basename":"captacao_pl","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"resgate_pl","name":"resgate_pl","basename":"resgate_pl","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"captacao_liquida_pl","name":"captacao_liquida_pl","basename":"captacao_liquida_pl","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0},{"fid":"gw_count_fid","name":"Row count","analyticType":"measure","semanticType":"quantitative","aggName":"sum","computed":true,"expression":{"op":"one","params":[],"as":"gw_count_fid"}},{"fid":"gw_mea_val_fid","name":"Measure values","analyticType":"measure","semanticType":"quantitative","aggName":"sum"}],"rows":[{"fid":"valor_patrimonio_liquido","name":"valor_patrimonio_liquido","basename":"valor_patrimonio_liquido","analyticType":"measure","semanticType":"quantitative","aggName":"sum","offset":0}],"columns":[{"fid":"data_competencia","name":"data_competencia","basename":"data_competencia","semanticType":"temporal","analyticType":"dimension","offset":0}],"color":[{"fid":"nome_comercial_classe","name":"nome_comercial_classe","basename":"nome_comercial_classe","semanticType":"nominal","analyticType":"dimension","offset":0}],"opacity":[],"size":[],"shape":[],"radius":[],"theta":[],"longitude":[],"latitude":[],"geoId":[],"details":[],"filters":[],"text":[]},"layout":{"showActions":false,"showTableSummary":false,"stack":"normalize","interactiveScale":false,"zeroScale":true,"size":{"mode":"fixed","width":799,"height":519},"format":{},"geoKey":"name","resolve":{"x":false,"y":false,"color":false,"opacity":false,"shape":false,"size":false}},"visId":"gw_XPXj","name":"Chart 1"}],"chart_map":{},"workflow_list":[{"workflow":[{"type":"view","query":[{"op":"aggregate","groupBy":["data_competencia","nome_comercial_classe"],"measures":[{"field":"valor_patrimonio_liquido","agg":"sum","asFieldKey":"valor_patrimonio_liquido_sum"}]}]}]}],"version":"0.4.9.1"}"""
    pyg_html = pyg.to_html(df_hist_classe_sub , spec=vis_spec)
    st.components.v1.html(pyg_html, height=1100)
    
    #pyg_app = StreamlitRenderer(df_hist_classe_sub)
    #pyg_app.explorer()
    
    

elif pagina_selecionada == 'Performance':
    st.header("Performance")
    st.write("Exibir performance aqui...")  # Personalize a exibição
    df_returns = st.session_state.df_returns
    color_map = st.session_state.color_map_fundos
    
    df_benchmark = df_returns[indicador_selecionado]
    df_returns = df_returns.drop(columns=[indicador_selecionado])
    st.write('Sharpe')
    teste = pfm.indice_sharpe_movel_multi(df_returns, df_benchmark, janela = 0, janela_minima=150)
    st.dataframe(teste)
    fig3 = px.bar(teste.T, color_discrete_map=color_map)
    st.plotly_chart(fig3) 
    
    st.write('Informatio Ratio Historico, movel 63du')
    teste = pfm.information_ratio_movel_multi(df_returns, df_benchmark, janela =63, janela_minima=21)
    st.dataframe(teste)
    fig3 = px.line(teste, color_discrete_map=color_map)
    st.plotly_chart(fig3)
    
    st.write('Alpha')
    teste = pfm.alpha_movel_multi(df_returns, df_benchmark,  taxas_livres_de_risco=None, janela=0, janela_minima=100)
    st.dataframe(teste)
  
    st.write('Beta')
    teste = pfm.beta_movel_multi(df_returns, df_benchmark,  janela=0, janela_minima=100)
    st.dataframe(teste)
  
    st.write('Tracking')
    teste = pfm.tracking_error_movel_multi(df_returns, df_benchmark,  janela=30, janela_minima=20)
    st.dataframe(teste)
    fig3 = px.line(teste, color_discrete_map=color_map)
    st.plotly_chart(fig3) 
    
  
    st.write('Traynor')
    teste = pfm.treynor_ratio_movel_multi(df_returns, df_benchmark,taxas_livres_de_risco=None, janela=0, janela_minima=100)
    st.dataframe(teste)
  
    st.write('Kappa p = 1')
    teste = pfm.kappa_rolling_mult(df_returns, df_benchmark, p=1, taxas_livres_de_risco=None, janela=0, janela_minima=1)
    st.dataframe(teste)
  
    st.write('Volatilidade')
    teste = pfm.volatilidade_rolling_multi(df_returns, df_benchmark, janela=120, janela_minima=10, agregador_retorno=1)
    st.dataframe(teste)
    fig3 = px.line(teste,color_discrete_map=color_map)
    st.plotly_chart(fig3)
    
  
    st.write('KCorrelação com, bench')
    teste = pfm.correlacao_rolling_multi(df_returns, df_benchmark, janela=0, janela_minima=1)
    st.dataframe(teste)
    fig3 = px.bar(teste.T, color_discrete_map=color_map)
    st.plotly_chart(fig3)
    
  
    st.write('KCorelçaão com Demnais')
    teste = pfm.correlacao_media_rolling_multi(df_returns, janela=0, janela_minima=1)
    st.dataframe(teste)
  
    st.write('Kappa p = 1')
    teste = pfm.kappa_rolling_mult(df_returns, df_benchmark, p=1, taxas_livres_de_risco=None, janela=0, janela_minima=1)
    st.dataframe(teste)
  
    #st.write('Kappa p = 1')
    #teste = pfm.calculate_kappa(df_returns, df_benchmark, p=1, risk_free_rate=0, window=None)
    #st.dataframe(teste)
  
      
    st.write('Metricas Diversas')
    teste = pfm.calculate_investment_metrics(df_returns, df_benchmark, df_benchmark, window=0)
    st.dataframe(teste)
  
    st.write('Metricas Diversas')
    teste = pfm.calculate_investment_metrics_pivot(df_returns, df_benchmark, df_benchmark, window=0)
    st.dataframe(teste)
  

elif pagina_selecionada == 'Volatilidade':
    st.header("Volatilidade")
    st.write("Exibir volatilidade aqui...")  # Personalize a exibição
    st.session_state.df_hist_classe_sub
    st.session_state.df_returns
    

elif pagina_selecionada == 'Histórico de Carteiras':
    st.header("Histórico de Carteiras")
    st.write("Exibir histórico de carteiras aqui...")  # Personalize a exibição
 
    

 
elif pagina_selecionada == 'Sensibilidade do Passivo':   
    st.header("Sensibilidade Passivo")
    df_returns = st.session_state.df_returns
    return_acum = st.session_state.return_acum
    returns_mes = st.session_state.returns_mes
    df_hist_classe_sub = st.session_state.df_hist_classe_sub
    color_map = st.session_state.color_map_fundos
    
    df_resgates = df_hist_classe_sub.pivot(index='data_competencia', columns='nome_comercial_classe', values='resgate_pl')
    df_resgates = df_resgates.reindex(sorted(df_resgates.columns), axis=1)
    
    df_return_ind = df_returns.sub(df_returns[indicador_selecionado], axis=0).drop(columns=[indicador_selecionado])
    df_return_ind  = pd.melt(df_return_ind)
    df_returns = df_returns.reindex(sorted(df_returns.columns), axis=1)
    df_returns = df_returns.drop(columns=[indicador_selecionado])
    
    st.write('elasticidade dos resgates, janela 30, lag 30 du')    
    elasticity_results = pfm.calculate_redemption_elasticity(df_returns, df_resgates, window=30, lag=30)
    #st.dataframe(elasticity_results)
    fig3 = px.line(elasticity_results)
    st.plotly_chart(fig3) 
    
    st.write('Correlação otima entre captação e rentabilidade, janela maxima 120 du, lag 30 du')  
    best = pfm.optimal_window_for_correlation(df_returns, df_resgates, min_window=10, max_window=160, lag = 30)
    st.dataframe(best)
    
    st.write('Correlação entre captação e rentabilidade, janela 30 du, lag 30 du')  
    analise = pfm.analyze_negative_performance_vs_redemptions(df_returns, df_resgates, window=30, lag = 30)
    st.dataframe(analise)
    
    st.write('Teste de Graner entre retornos e captação, janela 30 du, lag maximo 30 du')  
    graner = pfm.granger_causality_test(df_returns, df_resgates, window=30, max_lag=60)
    st.dataframe(graner)