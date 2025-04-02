import streamlit as st
import pandas as pd
import json

import base64
import requests
import warnings



 
warnings.simplefilter('ignore')
 
producao_url = 'https://api.anbima.com.br/'
sandbox_url = 'https://api-sandbox.anbima.com.br/'
id_url = 'https://api.anbima.com.br/oauth/access-token'
 
### Define se dados vem de ambiente de producao ou sandbox ###
producao = True
oculta_nulos =True
 
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

codigo_fundo = 'F0000252743'
fundos_det_http = f'{url}feed/fundos/v2/fundos/{codigo_fundo}'
fundos_det = requests.get(fundos_det_http, headers=headers3)
try:
    fundos_det_json = fundos_det.json()
except ValueError:
    print('Erro')
    print(codigo_fundo)
    headers3 = conectar('wRGlvlj1bOW3', 'l4riAuRd0CUL','wRGlvlj1bOW3:l4riAuRd0CUL', url)
#dados_cadastrais = pd.json_normalize(fundos_det_json['dados-cadastrais'])
fundo_det_cadastro = pd.json_normalize(fundos_det_json)
#json_cadastro_total = json_cadastro_total.append(fundos_det_json)

    
###########################################################
# Carregar o arquivo JSON (adicione o caminho correto do arquivo)
file_path = 'fundo.json'
with open(file_path, 'r', encoding='utf-8') as file:
    fundo_data = json.load(file)
    
fundo_data = fundos_det_json

# Função para exibir informações simples (nomes de campos em negrito) em formato de texto
def exibir_informacoes_texto(dataframe):
    for index, row in dataframe.iterrows():
        for col in dataframe.columns:
            if not isinstance(row[col], (list, dict)):  # Exibir apenas campos simples
               if row[col] is None or str(row[col]).lower() in ['none', 'não disponível', 'nao disponível', 'não se aplica', 'nao se aplica']:
                   if oculta_nulos == True:
                    continue
               st.write(f"**{col}**: {row[col]}")  # Nome do campo em negrito
        st.write("---")

def exibir_informacoes_dict2(dicionario):
    for chave, valor in dicionario.items():
        if valor is None:
            valor = "Não disponível"
        if isinstance(valor,  list):
            st.subheader(chave)
            exibir_informacoes_texto(pd.DataFrame(valor))
        else:
            st.write(f"**{chave}:** {valor}")
    st.write("---")    
    
def exibir_informacoes_dict(dicionario):
    for chave, valor in dicionario.items():
        # Ignorar valores nulos ou irrelevantes
        if valor is None or str(valor).lower() in ['none', 'não disponível', 'nao disponível', 'não se aplica', 'nao se aplica']:
            continue

        # Se o valor for uma lista, exibir cada item
        if isinstance(valor, list):
            if len(valor) > 0:
                st.subheader(f"{chave} (Lista)")
                for item in valor:
                    if isinstance(item, dict):
                        exibir_informacoes_dict(item)  # Chamada recursiva se o item for um dicionário
                    else:
                        st.write(f"- {item}")
        # Se o valor for um dicionário, exibir o conteúdo
        elif isinstance(valor, dict):
            st.subheader(f"{chave} (Detalhes)")
            exibir_informacoes_dict(valor)  # Chamada recursiva para o dicionário

        # Caso contrário, exibir como chave-valor
        else:
            st.write(f"**{chave}:** {valor}")
    st.write("---")
    
# Função para exibir informações de cada classe, incluindo benchmarks, sufixos, etc.
def exibir_detalhes_classe(classe_nome, classe_info, prestadores_info, sufixos_info, benchmarks_info):
    with st.expander(f"Classe: {classe_nome}"):
        st.subheader("Informações da Classe")
        exibir_informacoes_texto(classe_info)
        
        if 'prestadores_subclasse' in row:              
            st.subheader("Prestadores da Subclasse")
            for prestador in row['Prestadores da Classe']:
                exibir_informacoes_texto(prestadores_info)

        st.subheader("Sufixos da Classe")
        exibir_informacoes_texto(sufixos_info)

        st.subheader("Benchmarks da Classe")
        exibir_informacoes_texto(benchmarks_info)
        

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
    pdf_url = documentos_df.url[0]
    conteudo_pdf = baixar_pdf(pdf_url, headers3)

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
            st.subheader("Sufixos da Class")
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
            for prestadores_classe in classe['prestadores_classe']:
                exibir_informacoes_dict(prestadores_classe)      
                

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




pdf_url = 'https://api.anbima.com.br/feed/fundos/v2/fundos/F0000405272/documentos/F0000405272_Regulamento.pdf'

    



# Headers para autenticação
headers3 = conectar('wRGlvlj1bOW3', 'l4riAuRd0CUL', 'wRGlvlj1bOW3:l4riAuRd0CUL', url)

# Baixar o PDF
