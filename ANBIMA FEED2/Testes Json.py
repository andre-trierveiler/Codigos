# -*- coding: utf-8 -*-
"""
Created on Sat Sep 28 16:50:50 2024

@author: andre_trierveiler
"""

import pandas as pd
import json

teste = '''{
    "codigo_fundo": "F0000146757",
    "tipo_identificador_fundo": "CNPJ",
    "identificador_fundo": "07104761000132",
    "tipo_fundo": "FIF",
    "razao_social_fundo": "ITAÚ RENDA FIXA PRÉ LONGO PRAZO FUNDO DE INVESTIMENTO FINANCEIRO DA CLASSE DE INVESTIMENTO EM COTAS RESPONSABILIDADE LIMITADA",
    "nome_comercial_fundo": "ITAÚ RF PRÉ LP FIF CIC RESP LIMITADA",
    "adaptado_rcvm175": "S",
    "moeda": "BRL",
    "atributo": "Monoclasse",
    "data_encerramento_fundo": null,
    "documentos": null,
    "prestadores_fundo": [
        {
            "codigo_tipo_prestador": "ADMINISTRADOR",
            "identificador": "60701190000104",
            "razao_social": "ITAU UNIBANCO SA",
            "nome_comercial": "ITAU UNIBANCO SA",
            "tipo_pessoa": "J",
            "codigo_pais": "BRA",
            "data_inicio_vigencia": "2012-11-28",
            "data_fim_vigencia": null,
            "data_atualizacao": "2024-09-27T08:16:19.169"
        },
        {
            "codigo_tipo_prestador": "GESTOR",
            "identificador": "40430971000196",
            "razao_social": "ITAU UNIBANCO ASSET MANAGEMENT LTDA",
            "nome_comercial": "ITAU UNIBANCO ASSET MANAGEMENT LTDA",
            "tipo_pessoa": "J",
            "codigo_pais": "BRA",
            "data_inicio_vigencia": "2021-10-29",
            "data_fim_vigencia": null,
            "data_atualizacao": "2024-09-27T08:16:19.169"
        }
    ],
    "data_vigencia_fundo": "2024-07-15",
    "classes": [
        {
            "codigo_classe": "C0000146757",
            "tipo_identificador_classe": "CNPJ",
            "identificador_classe": "07104761000132",
            "data_inicio_atividade_classe": "2005-06-23",
            "razao_social_classe": "ITAÚ RENDA FIXA PRÉ LONGO PRAZO FUNDO DE INVESTIMENTO FINANCEIRO DA CLASSE DE INVESTIMENTO EM COTAS RESPONSABILIDADE LIMITADA",
            "nome_comercial_classe": "ITAÚ RF PRÉ LP FIF CIC RESP LIMITADA",
            "tributacao_perseguida": "Longo Prazo",
            "alavancado": "N",
            "credito_privado": "N",
            "percentual_permitido_credito_privado": 50.0,
            "investimento_exterior": "Não se Aplica",
            "percentual_permitido_investimento_exterior": 0.0,
            "foco_atuacao": "Não se Aplica",
            "fundo_esg": "Não",
            "forma_condominio": "Aberto",
            "entidade_investimento_fins_tributarios": "NA",
            "infraestrutura": "N",
            "responsabilidade_limitada": "S",
            "categoria_cvm": "renda fixa",
            "composicao": "CIC",
            "tipo_anbima": "Renda Fixa Indexados",
            "nivel1_categoria": "Renda Fixa",
            "nivel2_categoria": "Indexados",
            "nivel3_subcategoria": "Índices",
            "data_encerramento_classe": null,
            "data_vigencia_classe": "2024-07-15",
            "taxas_classe": [
                {
                    "tipo_taxa": "Global",
                    "perfil_taxa": "Fixa",
                    "unidade_taxa": "Percentual",
                    "valor_monetario": null,
                    "valor_percentual": 1.0,
                    "valor_piso": null,
                    "valor_fixo": null,
                    "valor_taxa_maxima": null,
                    "valor_percentual_taxa_maxima": 1.0,
                    "informacoes_adicionais": null,
                    "data_inicio_vigencia": "2015-10-01",
                    "data_fim_vigencia": null,
                    "faixas_escalonamento": null
                }
            ],
            "prestadores_classe": [
                {
                    "codigo_tipo_prestador": "CONTROLADOR",
                    "identificador": "60701190000104",
                    "razao_social": "ITAU UNIBANCO SA",
                    "nome_comercial": "ITAU UNIBANCO SA",
                    "tipo_pessoa": "J",
                    "codigo_pais": "BRA",
                    "data_inicio_vigencia": "2005-06-23",
                    "data_fim_vigencia": null,
                    "data_atualizacao": "2024-09-27T08:16:47.855"
                },
                {
                    "codigo_tipo_prestador": "CUSTODIANTE",
                    "identificador": "60701190000104",
                    "razao_social": "ITAU UNIBANCO SA",
                    "nome_comercial": "ITAU UNIBANCO SA",
                    "tipo_pessoa": "J",
                    "codigo_pais": "BRA",
                    "data_inicio_vigencia": "2005-06-23",
                    "data_fim_vigencia": null,
                    "data_atualizacao": "2024-09-27T08:16:47.855"
                },
                {
                    "codigo_tipo_prestador": "DISTRIBUIDOR",
                    "identificador": "60701190000104",
                    "razao_social": "ITAU UNIBANCO SA",
                    "nome_comercial": "ITAU UNIBANCO SA",
                    "tipo_pessoa": "J",
                    "codigo_pais": "BRA",
                    "data_inicio_vigencia": "2005-06-23",
                    "data_fim_vigencia": null,
                    "data_atualizacao": "2024-09-27T08:17:05.735"
                }
            ],
            "perfil_complementar": {
                "codigo_b3": null,
                "restricao_investimento": "Não Há Restrição",
                "tipo_investidor": "Geral",
                "aplicacao_automatica": "NA",
                "plano_previdencia": "Não",
                "periodicidade_envio_pl_cota": "Diário",
                "calculo_cota": "Fechamento",
                "data_atualizacao": "2024-09-27T07:21:53.330"
            },
            "taxas_entrada_saida_classe": [
                {
                    "tipo_entrada_saida": "S",
                    "valor_monetario": null,
                    "valor_percentual": null,
                    "data_inicio_vigencia": "2005-06-23",
                    "data_fim_vigencia": null,
                    "data_atualizacao": "2024-09-27T00:00:00.000"
                },
                {
                    "tipo_entrada_saida": "E",
                    "valor_monetario": null,
                    "valor_percentual": null,
                    "data_inicio_vigencia": "2005-06-23",
                    "data_fim_vigencia": null,
                    "data_atualizacao": "2024-09-27T00:00:00.000"
                }
            ],
            "valores_minimos_movimentacao_classe": {
                "data_vigencia": "2024-07-15",
                "indicador_prazo_emissao_cota": null,
                "prazo_emissao_cota": 0,
                "indicador_prazo_conversao_resgate": null,
                "prazo_conversao_resgate": 0,
                "indicador_prazo_pagamento_resgate": null,
                "prazo_pagamento_resgate": 0,
                "regra_adicional_pagamento_resgate": "N",
                "dias_carencia_inicial": null,
                "dias_carencia_ciclica": 0,
                "valor_minimo_aplicacao_inicial": 5000.0,
                "valor_minimo_aplicacao_subsequente": 0.0,
                "valor_minimo_resgate": 0.0,
                "valor_minimo_permanencia": 500.0,
                "data_atualizacao": "2024-09-27T00:00:00.000"
            },
            "indices_benchmark": [
                {
                    "benchmark": "imat",
                    "data_inicio_vigencia": "2015-10-01",
                    "data_fim_vigencia": null,
                    "data_atualizacao": "2024-09-27T08:34:24.398"
                }
            ],
            "sufixos": [
                {
                    "sufixo": "longo prazo",
                    "data_inicio_vigencia": "2018-11-12",
                    "data_fim_vigencia": null,
                    "data_atualizacao": "2024-09-27T08:18:02.416"
                }
            ],
            "subclasses": null,
            "taxa_performance": {
                "perfil_taxa": "FIXA",
                "periodicidade_cobranca": "ND",
                "informacoes_adicionais": null,
                "data_inicio_vigencia": "2015-10-01",
                "data_fim_vigencia": null,
                "detalhes": null
            },
            "data_atualizacao": "2024-09-27T08:18:35.736",
            "95_por_cento_fundo_isento": "N"
        }
    ],
    "data_atualizacao": "2024-09-27T07:18:58.288"
}'''

json_data= json.loads(teste)


codigo_fundo = json_data['codigo_fundo']
data_vigencia_fundo = json_data['data_vigencia_fundo']

# Criar dataframe para o dicionário principal
df_principal = pd.DataFrame({'codigo_fundo': [codigo_fundo],
                             'data_vigencia_fundo': [data_vigencia_fundo]})

# Extrair informações das classes
classes = json_data['classes']
df_classes = pd.DataFrame()
for classe in classes:
    codigo_classe = classe['codigo_classe']
    data_vigencia_classe = classe['data_vigencia_classe']
    indice_benchmark = classe['indices_benchmark']
    # Criar dataframe para cada classe
    df_classe = pd.DataFrame({'codigo_classe': [codigo_classe],
                              'data_vigencia_classe': [data_vigencia_classe]})
    
    df_classes = pd.concat([df_classes,df_classe])

taxas_classe = pd.json_normalize(json_data, 'classes', ['taxas_classe'], errors='ignore', record_prefix='taxas_')
# Extrair informações dos prestadores de fundo
prestadores_fundo = json_data['prestadores_fundo']
df_prestadores_fundo = pd.DataFrame(prestadores_fundo)

# Extrair informações dos prestadores de classe
prestadores_classe = []
for classe in classes:
    prestadores_classe += classe['prestadores_classe']
df_prestadores_classe = pd.DataFrame(prestadores_classe)

