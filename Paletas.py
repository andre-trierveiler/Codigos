# -*- coding: utf-8 -*-
"""
Created on Tue Oct  7 00:52:53 2025

@author: andre
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta


import seaborn as sns
import matplotlib.pyplot as plt

#python -m streamlit run C:\Users\andre\Paletas.py --server.address localhost --server.port 8525


st.set_page_config(page_title="DataViz - Paletas Sicredi", layout="wide")

# ======================================================
# 🎨 Paletas de cores customizadas
# ======================================================
PALETA_SICREDI = [
    "#008542",  # verde institucional
    "#00A859",  # verde claro
    "#66BB6A",  # folha média
    "#A5D6A7",  # folha clara
    "#C8E6C9",  # verde pastel claro
    "#6BBF59",  # musgo
    "#4CAF50",  # padrão positivo
    "#81C784",  # variação suave
    "#388E3C",  # escuro
    "#2E7D32",  # profundo
    "#B9F6CA",  # quase branco
    "#43A047"   # intermediário
]

cores_sicredi1 = ['#3FA110','#46D7FF','#FF6400', '#E60050','#FFC000','#730028','#8D8D8D','#D0F7A6']
cores_sicredi2= ['#8cc770','#66C5CC', '#F6CF71', "#F67397", '#90e7ff','#ffa266', "#F49AC2" , '#ab667e', '#bbbbbb', '#e3faca']
cores_sicredi8  = ['#3FA110', '#FF6400','#46D7FF',  '#E60050','#FFCD00','#5A3C1E','#146E37', '#5A645A','#323C32']
cores_sicredi9 = ['#9fd088', '#ffb280', '#a2ebff', '#f280a8', '#ffe680', '#ac9e8e', '#8ab69b', '#acb2ac', '#989e98']
cores_sicredi10 = ['#2E7C0C', '#CC5200', '#33A9CC', '#B0003F', '#E6B800', '#4A3320', '#0F562B', '#4B554B', '#262E26']
cores_sicredi11 = ['#5C8E56', '#C4793A', '#75BFD1', '#C2537A', '#E5C65C', '#7C624B', '#3B6E4A', '#6E766E', '#474E47']
cores_sicredi12 = ['#4D8C3F', '#E37A2E', '#69B4C8', '#D34B73', '#E5B72E', '#7A5A38', '#2E5E3A', '#666C66', '#3A3F3A']
cores_sicredi14 = ['#146E37', '#2E8C28', '#3FA110', '#74C356', '#A3DA85']
tons_azul = ['#0F3073', '#A0DAF8', '#5BC5F2']
tons_verde4 = ['#146E37','#3FA110','#D7E6CB',  '#63C733']    
tons_verde3 = [ "#2C7520", "#3FA110", "#63C733", "#97DA85", "#C2EFC2", "#E8F8E8"]

paleta_corporativa = ["#3FA110",  # verde institucional — base
    "#FF6400",  # laranja — energia, destaque
    "#46D7FF",  # azul claro — inovação, tecnologia
    "#E60050",  # magenta — intensidade
    "#FFCD00",  # amarelo — otimismo / destaque secundário
    "#5A3C1E",  # marrom — solidez / base neutra
    "#146E37",  # verde escuro — variação de profundidade
    "#5A645A",  # cinza médio — neutro
    "#323C32"   # cinza escuro — equilíbrio visual
    ]

paleta_triade = [    "#3FA110",  # verde institucional — confiança
    "#46D7FF",  # azul claro — estabilidade / técnica
    "#E60050"   # magenta — energia / atenção
    ]

paleta_verde = [    "#3FA110",  # verde institucional
    "#6BCF4F",  # verde médio (50% mistura com branco)
    "#9EEA85",  # verde claro pastel
    "#C8F7B5",  # verde quase menta
    "#E6FADF"   # verde extremamente suave / fundo
    ]

paleta_pastel_institucional = [    
    "#8AD666",
    #'#3FA110',
    "#FFA866",
    "#8BE5FF",
    "#F67397",
    "#FFE066",
    "#A18874",
    "#6CB480",
    "#9EA89E",
    "#7B857B"
]


import matplotlib.colors as mcolors

def suavizar_paleta(paleta, fator=0.3):
    """Mistura cada cor da paleta com branco (fator 0–1)."""
    novas = []
    for cor in paleta:
        r, g, b = mcolors.to_rgb(cor)
        r = r + (1 - r) * fator
        g = g + (1 - g) * fator
        b = b + (1 - b) * fator
        novas.append(mcolors.to_hex((r, g, b)))
    return novas





#PALETA_SICREDI = cores_sicredi16

#import matplotlib.colors as mcolors
# ======================================================
# 🎛️ Barra lateral — opções visuais
# ======================================================
st.sidebar.header("🎨 Configurações visuais")

modo = st.sidebar.selectbox("Tema visual", ["Claro", "Escuro"], index=0)




todas_paletas = {
    "Paleta Corporativa": paleta_corporativa,
    "Paleta Tríade": paleta_triade,
    "Paleta Verde": paleta_verde,
    "Pastel Institucional": paleta_pastel_institucional,
    "Sicredi": PALETA_SICREDI,
    "Sicredi 1": cores_sicredi1,
    "Sicredi 2": cores_sicredi2,
    "Sicredi 8": cores_sicredi8,
    "Sicredi 9": cores_sicredi9,
    "Sicredi 10": cores_sicredi10,
    "Sicredi 11": cores_sicredi11,
    "Sicredi 12": cores_sicredi12,
    "Sicredi 14": cores_sicredi14,
    "Tons Azul": tons_azul,
    "Tons Verde 4": tons_verde4,
    'tons_verde3':tons_verde3 ,    
}


paleta_opcao = st.sidebar.selectbox(
    "Paleta de cores",
    list(todas_paletas.keys()),
    index=list(todas_paletas.keys()).index("Sicredi") if "Sicredi" in todas_paletas else 0
)

cores = todas_paletas[paleta_opcao]

pastel_suave = suavizar_paleta(cores, fator=0.4)


# Template conforme o modo
template = "plotly_dark" if modo == "Escuro" else "plotly_white"



# ============================================================
# 🎨 ESTILO GLOBAL — FONTE + CORES DE TÍTULOS
# ============================================================

st.markdown("""
            
<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&family=Liberation+Serif:wght@700&family=Open+Sans:wght@400;600&display=swap" rel="stylesheet">

<style>
/* Fonte global */
html, body, [class*="css"]  {
    font-family: 'Liberation Serif'
}

/* Cor e estilo dos títulos */
h1, h2, h3, h4, h5, h6 {
    color: #323C32 !important;          /* Verde institucional */
    font-family: 'Source Sans Pro', serif !important;  /* Fonte elegante */
    font-weight: 700 !important;         /* Negrito */
}

/* Subtítulos ou textos secundários */
p, span, label {
    color: #323C32 !important;           /* Cinza institucional */
    font-family: 'Liberation Serif', sans-serif !important;
}

/* Títulos dos gráficos (plotly ou matplotlib renderizados em markdown) */
.plotly-title {
    color: #323C32 !important;
    font-family: 'Liberation Serif', serif !important;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 🧭 EXEMPLO DE USO
# ============================================================
st.title("Indicadores de Performance")
st.subheader("Evolução do Patrimônio e Rentabilidade")
st.write("Todos os títulos e textos agora seguem o padrão institucional definido.")




# ======================================================
# 🧩 Dados de exemplo
# ======================================================
cats12 = [f"Categoria {i+1}" for i in range(12)]
vals12 = np.random.randint(10, 100, size=12)

cats3 = ["Categoria A", "Categoria B", "Categoria C"]
vals3 = np.random.randint(10, 100, size=3)

cats5 = ["Cat 1", "Cat 2", "Cat 3", "Cat 4", "Cat 5"]
vals5 = np.random.randint(20, 120, size=5)

dates = pd.date_range(datetime.now() - timedelta(days=30), periods=30)
df_line12 = pd.DataFrame({
    "Data": np.tile(dates, 12),
    "Valor": np.random.randint(50, 200, 30 * 12),
    "Categoria": np.repeat(cats12, 30)
})
df_line3 = pd.DataFrame({
    "Data": np.tile(dates, 3),
    "Valor": np.random.randint(50, 200, 30 * 3),
    "Categoria": np.repeat(cats3, 30)
})
df_bar3 = df_line3.copy()

df_bar5 = pd.DataFrame({
    "Data": np.tile(dates, 5),
    "Valor": np.random.randint(50, 250, 30 * 5),
    "Categoria": np.repeat(cats5, 30)
})

# ======================================================
# 🥯 Gráficos de Rosca
# ======================================================
st.header("🥯 Gráficos de Rosca")

col1, col2 = st.columns(2)

with col1:
    st.subheader("12 Categorias")
    fig1 = px.pie(
        names=cats12,
        values=vals12,
        hole=0.55,
        color_discrete_sequence=cores,
        template=template
    )
    # 🔸 mostra apenas valores fora da rosca
    fig1.update_traces(
        textinfo="value",
        textposition="outside",
        textfont_size=14,
        pull=[0.02] * 12,
        showlegend=True
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("3 Categorias")
    fig2 = px.pie(
        names=cats3,
        values=vals3,
        hole=0.55,
        color_discrete_sequence=cores,
        template=template
    )
    fig2.update_traces(
        textinfo="value",
        textposition="outside",
        textfont_size=16,
        pull=[0.04] * 3,
        showlegend=True
    )
    st.plotly_chart(fig2, use_container_width=True)
    
# ======================================================
# 📈 Gráficos de Linha
# ======================================================
st.header("📈 Gráficos de Linha")

col3, col4 = st.columns(2)

with col3:
    st.subheader("12 Categorias")
    fig3 = px.line(
        df_line12, x="Data", y="Valor", color="Categoria",
        color_discrete_sequence=cores, template=template
    )
    fig3.update_traces(line=dict(width=1.8))  # 🔸 linha mais fina
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("3 Categorias")
    fig4 = px.line(
        df_line3, x="Data", y="Valor", color="Categoria",
        color_discrete_sequence=cores, template=template
    )
    fig4.update_traces(line=dict(width=1.8))  # 🔸 linha mais fina
    st.plotly_chart(fig4, use_container_width=True)

# ======================================================
# 📊 Gráficos de Barras
# ======================================================
st.header("📊 Gráficos de Barra")

st.subheader("3 Categorias (por Data)")
fig5 = px.bar(
    df_bar3, x="Data", y="Valor", color="Categoria", barmode="group",
    color_discrete_sequence=cores, template=template
)
st.plotly_chart(fig5, use_container_width=True)

st.subheader("5 Categorias (por Data)")
fig6 = px.bar(
    df_bar5, x="Data", y="Valor", color="Categoria", barmode="group",
    color_discrete_sequence=cores, template=template
)
st.plotly_chart(fig6, use_container_width=True)

def teste():
    # ======================================================
    # 💹 Gráfico de Rentabilidade (Investimento vs CDI) com Span e Destaque opcionais
    # ======================================================
    st.header("💹 Rentabilidade Acumulada — Investimento vs CDI")
    
    # Gera 200 dias de dados simulados
    np.random.seed(42)
    dias = 200
    datas = pd.date_range(datetime.now() - timedelta(days=dias), periods=dias)
    
    # Simulação de retornos diários (em %)
    ret_invest = np.random.normal(loc=0.05, scale=0.4, size=dias) / 100
    ret_cdi = np.full(dias, 0.038 / 252)  # CDI ~ 3.8% ao ano
    
    # Rentabilidade acumulada (base 100)
    base = 100
    serie_invest = base * (1 + pd.Series(ret_invest)).cumprod()
    serie_cdi = base * (1 + pd.Series(ret_cdi)).cumprod()
    
    df_rent = pd.DataFrame({
        "Data": datas,
        "Investimento": serie_invest,
        "CDI": serie_cdi
    })
    df_rent_long = df_rent.melt(id_vars="Data", var_name="Ativo", value_name="Índice (Base 100)")
    
    # ======================================================
    # 🎛️ Menu lateral: parâmetros de SPAN e DESTAQUE
    # ======================================================
    st.sidebar.header("⚙️ Parâmetros do Gráfico de Rentabilidade")
    
    # ----- Opções gerais -----
    exibir_span = st.sidebar.checkbox("Mostrar faixa (span)", value=True)
    exibir_destaque = st.sidebar.checkbox("Mostrar destaque (seta)", value=True)
    
    # ----- Configurações do Span -----
    if exibir_span:
        st.sidebar.subheader("🩶 Faixa (Span)")
        data_min, data_max = df_rent["Data"].min(), df_rent["Data"].max()
        span_inicio = st.sidebar.date_input("Data inicial do Span", value=data_min)
        span_fim = st.sidebar.date_input("Data final do Span", value=data_max)
        texto_span = st.sidebar.text_input("Texto do Span", "span 1")
    
    # ----- Configurações do Destaque -----
    if exibir_destaque:
        st.sidebar.subheader("📍 Destaque (Anotação)")
        data_destaque = st.sidebar.date_input("Data do Destaque", value=df_rent["Data"].iloc[150])
        texto_destaque = st.sidebar.text_input("Texto do Destaque", "Destaque 1")
    
    # ======================================================
    # 📈 Gráfico base
    # ======================================================
    fig_rent = px.line(
        df_rent_long, x="Data", y="Índice (Base 100)", color="Ativo",
        color_discrete_sequence=cores,
        template=template
    )
    
    # Linhas finas + CDI pontilhado
    fig_rent.update_traces(line=dict(width=1.5))
    fig_rent.update_traces(
        selector=dict(name="CDI"),
        line=dict(dash="dot", width=1.2)
    )
    
    # ======================================================
    # 🩶 SPAN (opcional)
    # ======================================================
    if exibir_span and span_inicio < span_fim:
        fig_rent.add_vrect(
            x0=span_inicio,
            x1=span_fim,
            fillcolor="rgba(200,200,200,0.3)",
            layer="below",
            line_width=0,
            annotation_text=texto_span,
            annotation_position="top left",
            annotation_font_size=12,
            annotation_font_color="#555"
        )
    
    # ======================================================
    # 📍 DESTAQUE (opcional)
    # ======================================================
    if exibir_destaque:
        df_rent["diff"] = abs(df_rent["Data"] - pd.to_datetime(data_destaque))
        ponto_ref = df_rent.loc[df_rent["diff"].idxmin()]
        x_dest = ponto_ref["Data"]
        y_dest = ponto_ref["Investimento"]
    
        fig_rent.add_annotation(
            x=x_dest,
            y=y_dest,
            text=texto_destaque,
            showarrow=True,
            arrowhead=2,
            ax=-40,
            ay=-60,
            font=dict(color="#333", size=12),
            arrowcolor="#666",
            bgcolor=None,        # sem caixa
            bordercolor=None,    # sem borda
            borderwidth=0
        )
    
    # ======================================================
    # Layout final com linhas-guia verticais
    # ======================================================
    fig_rent.update_layout(
        hovermode="x unified",
        yaxis_title="Índice (Base 100)",
        legend_title_text="",
        margin=dict(l=40, r=20, t=50, b=40),
        xaxis=dict(
            showgrid=True,                   # ativa linhas verticais
            gridcolor="rgba(120,120,120,0.2)",  # cor cinza clara
            gridwidth=1,
            showline=False,
            zeroline=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(180,180,180,0.15)",
            gridwidth=1,
            zeroline=False
        )
    )
    
    st.plotly_chart(fig_rent, use_container_width=True)


# ======================================================
# 🖋️ Fonte e tamanho da fonte
# ======================================================
st.sidebar.header("🖋️ Configuração de Fonte")

fonte_opcao = st.sidebar.selectbox(
    "Fonte dos textos",
    ["Arial", "Roboto", "Open Sans", "Lato", "Montserrat", "Poppins","Source Sans Pro",
    "Nunito", "Raleway", "Inter", "Times New Roman", "Courier New"],
    index=1
)
#Source Sans Pro

tamanho_fonte = st.sidebar.slider(
    "Tamanho da fonte (geral)",
    min_value=8,
    max_value=24,
    value=12,
    step=1
)



# ======================================================
# 💹 Rentabilidade com múltiplos Spans e Destaques
# ======================================================
st.header("💹 Rentabilidade Acumulada — Investimento vs CDI")

# Simulação de dados
np.random.seed(42)
dias = 200
datas = pd.date_range(datetime.now() - timedelta(days=dias), periods=dias)
ret_invest = np.random.normal(loc=0.05, scale=0.4, size=dias) / 100
ret_cdi = np.full(dias, 0.038 / 252)
base = 100
serie_invest = base * (1 + pd.Series(ret_invest)).cumprod()
serie_cdi = base * (1 + pd.Series(ret_cdi)).cumprod()
df_rent = pd.DataFrame({"Data": datas, "Investimento": serie_invest, "CDI": serie_cdi})
df_rent_long = df_rent.melt(id_vars="Data", var_name="Ativo", value_name="Índice (Base 100)")

# ======================================================
# 🎛️ Menu lateral: múltiplos spans e destaques
# ======================================================
st.sidebar.header("⚙️ Parâmetros do Gráfico de Rentabilidade")

# ---- SPANS ----
exibir_span = st.sidebar.checkbox("Mostrar faixas (spans)", value=True)
num_spans = 0
if exibir_span:
    num_spans = st.sidebar.number_input("Quantidade de spans", 0, 5, 1)
    spans = []
    st.sidebar.markdown("### 🩶 Configuração das Faixas")
    for i in range(int(num_spans)):
        st.sidebar.markdown(f"**Faixa {i+1}**")
        x0 = st.sidebar.date_input(f"Data inicial {i+1}", df_rent["Data"].iloc[40+i*20])
        x1 = st.sidebar.date_input(f"Data final {i+1}", df_rent["Data"].iloc[60+i*20])
        texto = st.sidebar.text_input(f"Texto do Span {i+1}", f"Span {i+1}")
        spans.append({"x0": x0, "x1": x1, "texto": texto})

# ---- DESTAQUES ----
exibir_destaques = st.sidebar.checkbox("Mostrar destaques (setas)", value=True)
num_destaques = 0
if exibir_destaques:
    num_destaques = st.sidebar.number_input("Quantidade de destaques", 0, 5, 1)
    destaques = []
    st.sidebar.markdown("### 📍 Configuração dos Destaques")
    for i in range(int(num_destaques)):
        data_dest = st.sidebar.date_input(f"Data do Destaque {i+1}", df_rent["Data"].iloc[100+i*20])
        texto_dest = st.sidebar.text_input(f"Texto do Destaque {i+1}", f"Destaque {i+1}")
        destaques.append({"data": data_dest, "texto": texto_dest})

# ======================================================
# 📈 Gráfico base
# ======================================================
fig_rent = px.line(
    df_rent_long, x="Data", y="Índice (Base 100)", color="Ativo",
    color_discrete_sequence=cores, template=template
)

fig_rent.update_traces(line=dict(width=1.5))
fig_rent.update_traces(selector=dict(name="CDI"), line=dict(dash="dot", width=1.2))

# ======================================================
# 🩶 Adiciona múltiplos SPANS
# ======================================================
if exibir_span and num_spans > 0:
    for sp in spans:
        if sp["x0"] < sp["x1"]:
            fig_rent.add_vrect(
                x0=sp["x0"],
                x1=sp["x1"],
                fillcolor="rgba(200,200,200,0.3)",
                layer="below",
                line_width=0,
                annotation_text=sp["texto"],
                annotation_position="top left",
                annotation_font_size=12,
                annotation_font_color="#555"
            )
# ======================================================
# 📍 Adiciona múltiplos DESTAQUES com escolha de série
# ======================================================
if exibir_destaques and num_destaques > 0:
    for i, d in enumerate(destaques):
        st.sidebar.markdown(f"**Série do Destaque {i+1}**")
        serie_opcao = st.sidebar.selectbox(
            f"Selecionar série do Destaque {i+1}",
            options=df_rent.columns[1:-1],  # ['Investimento', 'CDI']
            index=0,
            key=f"serie_destaque_{i}"
        )

        # encontra o ponto mais próximo na série escolhida
        df_rent["diff"] = abs(df_rent["Data"] - pd.to_datetime(d["data"]))
        ponto = df_rent.loc[df_rent["diff"].idxmin()]
        x_dest = ponto["Data"]
        y_dest = ponto[serie_opcao]  # agora usa a série escolhida!

        # adiciona anotação
        fig_rent.add_annotation(
            x=x_dest,
            y=y_dest,
            text=d["texto"],
            showarrow=True,
            arrowhead=2,
            ax=-40,
            ay=-60,
            font=dict(color="#333", size=12, family=fonte_opcao),
            arrowcolor="#666",
            bgcolor=None,
            bordercolor=None,
            borderwidth=0
        )

# ======================================================
# 📐 Layout com linhas-guia verticais
# ======================================================
cor_grade_x = "rgba(120,120,120,0.2)" if template == "plotly_white" else "rgba(200,200,200,0.1)"
fig_rent.update_layout(
    hovermode="x unified",
    yaxis_title="Índice (Base 100)",
    legend_title_text="",
    margin=dict(l=40, r=20, t=50, b=40),
    xaxis=dict(showgrid=True, gridcolor=cor_grade_x, gridwidth=1),
    yaxis=dict(showgrid=True, gridcolor="rgba(180,180,180,0.15)", gridwidth=1)
)

# Aplica ao layout
fig_rent.update_layout(
    font=dict(
        family=fonte_opcao,
        size=tamanho_fonte,
        color="#333" if template == "plotly_white" else "#EEE"
    )
)

# ======================================================
# 🏷️ Comentário institucional (rodapé)
# ======================================================
fig_rent.add_annotation(    text="Elaboração: Sicredi Asset. Bloomberg",
    xref="paper",  # posição relativa ao layout, não aos dados
    yref="paper",
    x=0,           # canto esquerdo
    y=-0.15,       # abaixo do eixo X
    showarrow=False,    font=dict(        family=fonte_opcao,        size=10,        color="#555" if template == "plotly_white" else "#BBB" ),
    align="left")

st.plotly_chart(fig_rent, use_container_width=True)

# ======================================================
# 💾 Botão para salvar o gráfico em HTML
# ======================================================
from io import BytesIO

# Cria um arquivo HTML interativo em memória
html_bytes = fig_rent.to_html(full_html=True, include_plotlyjs="cdn").encode("utf-8")

st.download_button(label="💾 Baixar gráfico em HTML", data=html_bytes, file_name="grafico_rentabilidade.html", mime="text/html")

# ============================================================
# 🔧 DADOS EXEMPLO
# ============================================================
np.random.seed(42)

# Barras empilhadas - 5 categorias, 4 instâncias
df_barra5 = pd.DataFrame({
    "Instância": np.repeat(["Q1", "Q2", "Q3", "Q4"], 5),
    "Categoria": ["A", "B", "C", "D", "E"] * 4,
    "Valor": np.random.randint(10, 100, 20)
})

# Barras empilhadas - 3 categorias, 4 instâncias
df_barra3 = pd.DataFrame({
    "Instância": np.repeat(["Q1", "Q2", "Q3", "Q4"], 3),
    "Categoria": ["A", "B", "C"] * 4,
    "Valor": np.random.randint(20, 80, 12)
})

# Linhas - 4 categorias
datas = pd.date_range("2023-01-01", periods=24, freq="M")
df_linhas = pd.DataFrame({
    "Data": np.tile(datas, 4),
    "Categoria": np.repeat(["Fundo A", "Fundo B", "Fundo C", "Benchmark"], len(datas)),
    "Valor": np.concatenate([
        np.linspace(100, 140, len(datas)) + np.random.normal(0, 2, len(datas)),
        np.linspace(100, 125, len(datas)) + np.random.normal(0, 3, len(datas)),
        np.linspace(100, 160, len(datas)) + np.random.normal(0, 4, len(datas)),
        np.linspace(100, 130, len(datas))  # benchmark — linha pontilhada
    ])
})

# Área não empilhada
df_area = pd.DataFrame({
    "Data": np.tile(datas, 3),
    "Categoria": np.repeat(["Segmento A", "Segmento B", "Segmento C"], len(datas)),
    "Valor": np.concatenate([
        np.linspace(50, 120, len(datas)) + np.random.normal(0, 3, len(datas)),
        np.linspace(30, 90, len(datas)) + np.random.normal(0, 3, len(datas)),
        np.linspace(20, 70, len(datas)) + np.random.normal(0, 3, len(datas))
    ])
})

# Área empilhada
df_area_emp = df_area.copy()
df_area_emp["Valor"] = df_area_emp["Valor"] / 2 + 20  # normaliza valores

# ============================================================
# 📊 GRÁFICOS
# ============================================================

# 1️⃣ Barras empilhadas (5 categorias)
col5, col6 = st.columns(2)
with col5:
    fig_barra5 = px.bar(df_barra5, x="Instância", y="Valor", color="Categoria",
        color_discrete_sequence=cores, template=template,
        title="Barras Empilhadas — 5 Categorias")
    fig_barra5.update_layout(barmode="stack")
    st.plotly_chart(fig_barra5, use_container_width=True)

with col6:
    fig_barra3 = px.bar(df_barra3, x="Instância", y="Valor", color="Categoria",
        color_discrete_sequence=cores, template=template,
        title="Barras Empilhadas — 3 Categorias")
    fig_barra3.update_layout(barmode="stack")
    st.plotly_chart(fig_barra3, use_container_width=True)

# 3️⃣ Linhas (4 categorias, uma pontilhada)
fig_linhas = px.line( df_linhas, x="Data", y="Valor", color="Categoria",
    color_discrete_sequence=cores, template=template,
    title="Gráfico de Linhas — Tendência de Retorno")
fig_linhas.for_each_trace(lambda t: t.update(line=dict(dash="dot")) if t.name == "Benchmark" else ())

# 4️⃣ Área não empilhada (com transparência)
fig_area = px.area(df_area, x="Data", y="Valor", color="Categoria",
    color_discrete_sequence=cores, template=template,
    title="Gráfico de Área (Não Empilhada)")
fig_area.update_traces(opacity=0.5, stackgroup=None,  fill='tozeroy')


# ============================================================
# 💡 Exemplo de exibição (Streamlit)
# ============================================================

st.plotly_chart(fig_linhas, use_container_width=True)
st.plotly_chart(fig_area, use_container_width=True)

# 4️⃣ Área empilhada 2 
fig_area = px.area(df_area, x="Data", y="Valor", color="Categoria",
    color_discrete_sequence=cores, template=template,
    title="Gráfico de Área empilhada II)")
fig_area.update_traces(opacity=0.5, stackgroup='one')
st.plotly_chart(fig_area, use_container_width=True)

# 4️⃣ Área empilhada 100%
fig_area = px.area(df_area, x="Data", y="Valor", color="Categoria",
    color_discrete_sequence=cores, template=template,
    title="Gráfico de Área empilhada 100%)")
fig_area.update_traces(stackgroup='one', groupnorm='percent', opacity=0.8)
fig_area.update_yaxes(title="% do Total", range=[0, 100])
st.plotly_chart(fig_area, use_container_width=True)


# 1️⃣ Barras lado a lado (3 categorias)
fig_barra3 = px.bar(
    df_barra3,
    x="Instância",
    y="Valor",
    color="Categoria",
    barmode="group",
    color_discrete_sequence=cores,
    template=template,
    title="Barras Lado a Lado — 3 Categorias"
)
st.plotly_chart(fig_barra3, use_container_width=True)

# 2️⃣ Barras lado a lado (5 categorias)
fig_barra5 = px.bar(
    df_barra5,
    x="Instância",
    y="Valor",
    color="Categoria",
    barmode="group",
    color_discrete_sequence=cores,
    template=template,
    title="Barras Lado a Lado — 5 Categorias"
)
st.plotly_chart(fig_barra5, use_container_width=True)

# 3️⃣ Barras horizontais
fig_horizontal = px.bar(
    df_barra5,
    x="Valor",
    y="Categoria",
    orientation="h",
    color="Instância",
    color_discrete_sequence=cores,
    template=template,
    title="Barras Horizontais — 5 Categorias"
)
fig_horizontal.update_layout(showlegend=False)
st.plotly_chart(fig_horizontal, use_container_width=True)

# 4️⃣ Gráfico de cascata (Waterfall)
fig_cascata = go.Figure(go.Waterfall(
    name="Fluxo de Resultados",
    orientation="v",
    measure=["relative", "relative", "relative", "relative", "total"],
    x=["Receita", "Custos", "Despesas", "Impostos", "Lucro Líquido"],
    textposition="outside",
    text=["+400", "-250", "-100", "-30", "20"],
    y=[400, -250, -100, -30, 20],
    connector={"line": {"color": "#3FA110"}},
    increasing={"marker": {"color": "#3FA110"}},
    decreasing={"marker": {"color": "#E60050"}},
    totals={"marker": {"color": "#46D7FF"}}
))
fig_cascata.update_layout(template=template, title="Gráfico de Cascata — Fluxo Financeiro")
st.plotly_chart(fig_cascata, use_container_width=True)




# ============================================================
# 📊 DATAFRAME ÚNICO PARA TESTE DE PALETAS
# ============================================================
# Simula uma estrutura hierárquica: Categoria → Subcategoria
categorias = ["Renda Fixa", "Multimercado", "Ações", "Câmbio", "Crédito"]
subcategorias = ["Conservador", "Moderado", "Arrojado"]

dados = []
for cat in categorias:
    for sub in subcategorias:
        for i in range(4):  # 4 observações por subcategoria
            dados.append({
                "Categoria": cat,
                "Subcategoria": sub,
                "Instância": f"Q{i+1}",
                "Valor": np.random.randint(50, 150),
                "Score_X": np.random.uniform(0, 1),
                "Score_Y": np.random.uniform(0, 1)
            })

df_paleta = pd.DataFrame(dados)

# ============================================================
# 🌞 1️⃣ GRÁFICO RADIAL (SUNBURST)
# ============================================================
fig_radial = px.sunburst(
    df_paleta,
    path=["Categoria", "Subcategoria"],
    values="Valor",
    color="Categoria",
    color_discrete_sequence=cores,
    template=template,
    title="🎯 Sunburst — Distribuição por Categoria e Subcategoria"
)
fig_radial.update_traces(insidetextorientation='radial')

# ============================================================
# 🌡️ 2️⃣ HEATMAP (MATRIZ DE MÉTRICAS)
# ============================================================
# Cria uma tabela cruzando categorias e subcategorias
heat_data = df_paleta.groupby(["Categoria", "Subcategoria"])["Valor"].mean().reset_index()
heat_pivot = heat_data.pivot(index="Subcategoria", columns="Categoria", values="Valor")

fig_heatmap = px.imshow(
    heat_pivot,
    color_continuous_scale=cores,
    template=template,
    title="🌡️ Heatmap — Média de Valor por Categoria/Subcategoria"
)
fig_heatmap.update_xaxes(side="top")

# ============================================================
# 🎯 3️⃣ SCATTER — (AVALIAÇÃO DE CONTRASTE E DISTRIBUIÇÃO)
# ============================================================
fig_scatter = px.scatter(
    df_paleta,
    x="Score_X",
    y="Score_Y",
    color="Categoria",
    size="Valor",
    hover_data=["Subcategoria", "Instância"],
    color_discrete_sequence=cores,
    template=template,
    title="🎨 Scatter — Avaliação de Contraste e Identificação de Cores"
)
fig_scatter.update_traces(marker=dict(opacity=0.8, line=dict(width=0.5, color="white")))

# ============================================================
# 💡 VISUALIZAÇÃO (em Streamlit ou Jupyter)
# ============================================================
st.plotly_chart(fig_radial, use_container_width=True)
st.plotly_chart(fig_heatmap, use_container_width=True)
st.plotly_chart(fig_scatter, use_container_width=True)


# ============================================================
# ⚙️ CONFIGURAÇÕES
# ============================================================
np.random.seed(42)
template = "plotly_white"



# ============================================================
# 🧩 DATAFRAME ÚNICO
# ============================================================
n = 200
df_color = pd.DataFrame({
    "x": np.random.uniform(0, 10, n),
    "y": np.random.uniform(0, 10, n),
    "z": np.random.uniform(0, 10, n),
    "Categoria": np.random.choice(["Fundo A", "Fundo B", "Fundo C", "Fundo D", "Fundo E"], n),
    "Intensidade": np.random.randint(20, 200, n),
    "Score1": np.random.normal(0, 1, n).cumsum(),
    "Score2": np.random.normal(0, 1, n).cumsum()
})

# ============================================================
# 🌈 1️⃣ SCATTER 3D — “Espaço cromático”
# ============================================================
fig_scatter3d = px.scatter_3d(
    df_color, x="x", y="y", z="z",
    color="Categoria", size="Intensidade",
    color_discrete_sequence=cores,
    opacity=0.8,
    template=template,
    title="🧭 Scatter 3D — Profundidade e Volume da Paleta"
)
fig_scatter3d.update_traces(marker=dict(line=dict(width=0.5, color="white")))

# ============================================================
# 🔮 2️⃣ DENSITY HEATMAP — “Calor cromático”
# ============================================================
fig_density = px.density_heatmap(
    df_color, x="x", y="y", z="Intensidade",
    color_continuous_scale=cores,
    nbinsx=20, nbinsy=20,
    template=template,
    title="🔥 Density Heatmap — Energia e Calor Cromático"
)
fig_density.update_layout(
    coloraxis_colorbar=dict(title="Intensidade"),
    xaxis_showgrid=False, yaxis_showgrid=False
)

# ============================================================
# 🌀 3️⃣ RADIAL BAR — “Ritmo e hierarquia visual”
# ============================================================
df_radial = (
    df_color.groupby("Categoria", as_index=False)
    .agg({"Intensidade": "mean"})
    .sort_values("Intensidade", ascending=False)
)
df_radial["Ângulo"] = np.linspace(0, 360, len(df_radial))

fig_radial = px.bar_polar(
    df_radial,
    r="Intensidade",
    theta="Categoria",
    color="Categoria",
    color_discrete_sequence=cores,
    template=template,
    title="🌀 Radial Bar — Ritmo e Peso Visual das Cores"
)
fig_radial.update_layout(
    polar=dict(bgcolor="rgba(0,0,0,0)"),
    showlegend=False
)

# ============================================================
# 💡 EXIBIÇÃO
# ============================================================
st.plotly_chart(fig_scatter3d, use_container_width=True)
st.plotly_chart(fig_density, use_container_width=True)
st.plotly_chart(fig_radial, use_container_width=True)



# ============================================================
# 💡 TERMOMETRO
# ============================================================
# ============================================================
# ⚙️ CONFIGURAÇÕES
# ============================================================
st.subheader("🔰 Velocímetro de Risco — Compacto e Colorido")

nivel_atual =65
nivel_maximo = 85

# ============================================================
# 📊 VELOCÍMETRO
# ============================================================
fig = go.Figure(go.Indicator(
    mode="gauge",
    value=nivel_atual,
    title={"text": "<b>Nível de Risco</b>", "font": {"size": 18, "color": "#323C32"}},
    gauge={
        "axis": {
            "range": [0, 100],
            "tickwidth": 0,
            "visible": False
        },
        "bar": {"color": "#3FA110", "thickness": 0.35},
        "bgcolor": "white",
        "borderwidth": 0,
        "steps": [
            {"range": [0, 50], "color": "#8EE17E"},   # verde mais vivo
            {"range": [50, 80], "color": "#FFE066"},  # amarelo vibrante
            {"range": [80, 100], "color": "#FF6B6B"}  # vermelho mais forte
        ],
        "threshold": {
            "line": {"color": "#E60050", "width": 4},
            "thickness": 0.75,
            "value": nivel_maximo
        }
    },
    domain={'x': [0, 1], 'y': [0, 1]}
))

# ============================================================
# 🧾 LEGENDA INFERIOR DIREITA
# ============================================================
fig.add_annotation(
    x=0.88, y=0.22,
    text=f"""
    <b style='color:#3FA110'>⬤ Atual</b>: {nivel_atual}<br>
    <b style='color:#E60050'>▲ Máximo</b>: {nivel_maximo}<br>
    """,
    showarrow=False,
    xanchor="left", yanchor="bottom",
    align="right",
    font=dict(size=13, color="#323C32")
)
# ============================================================
# ✨ ESTILO FINAL
# ============================================================
fig.update_layout(
    template="plotly_white",
    height=280,
    margin=dict(t=40, b=0, l=0, r=0),
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(family="Liberation Serif", color="#323C32")
)

# Remove números automáticos
fig.update_traces(number={'font': {'size': 1, 'color': "white"}})

st.plotly_chart(fig, use_container_width=True)

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ============================================================
# ⚙️ DADOS EXEMPLO
# ============================================================
np.random.seed(42)
categorias = ["Renda Fixa", "Multimercado", "Ações", "Câmbio", "Crédito"]
dados = []
for cat in categorias:
    for i in range(40):
        valor = np.random.normal(loc=np.random.uniform(60, 100), scale=5)
        dados.append({"Categoria": cat, "Valor": valor})

df_box = pd.DataFrame(dados)

# ============================================================
# 🎨 PALETA E TEMPLATE
# ============================================================

template = "plotly_white"

# ============================================================
# 📊 BOX + DISPERSÃO HORIZONTAL
# ============================================================
fig = px.box(
    df_box, 
    y="Categoria", x="Valor",
    orientation="h",
    color="Categoria",
    color_discrete_sequence=cores,
    template=template,
    points=False  # desativar pontos padrão do boxplot
)

# adiciona dispersão (pontos individuais) de forma elegante
fig.add_trace(px.strip(
    df_box,
    y="Categoria", x="Valor",
    orientation="h",
    color="Categoria",
    color_discrete_sequence=cores
).data[0])

# ============================================================
# 💅 AJUSTES ESTÉTICOS
# ============================================================
fig.update_traces(
    jitter=0.25,                # leve espalhamento horizontal
    marker=dict(size=6, opacity=0.4, line=dict(width=0.5, color="white")),
    boxmean=True,               # mostra média dentro da box
    width=0.6
)

fig.update_layout(
    title=dict(
        text="📊 Distribuição de Risco — Boxplot Horizontal",
        x=0.5, xanchor="center", font=dict(size=20, color="#323C32", family="Liberation Serif")
    ),
    xaxis=dict(
        title="Valor",
        showgrid=True,
        gridcolor="rgba(0,0,0,0.05)",
        zeroline=False
    ),
    yaxis=dict(
        title="Categoria",
        showgrid=False
    ),
    paper_bgcolor="white",
    plot_bgcolor="white",
    font=dict(family="Liberation Serif", color="#323C32"),
    height=450,
    showlegend=False
)

# contorno leve e sombra simulada
fig.update_xaxes(showline=True, linewidth=1, linecolor="rgba(0,0,0,0.15)")
fig.update_yaxes(showline=False)

# ============================================================
# 🚀 EXIBIÇÃO
# ============================================================
st.plotly_chart(fig, use_container_width=True)


# ============================================================
# 🎨 TÍTULO STREAMLIT
# ============================================================
st.title("📊 Infográfico de Barras — Fundo 100% sombreado")
# ============================================================
# ⚙️ DADOS
# ============================================================
categorias = ["Mercury", "Saturn", "Pluto", "Mars"]
#cores = ["#F77E7E", "#D66BFF", "#70B7FF", "#83E1C4"]

valores_jupiter = [15, 44, 61, 39]
valores_venus = [57, 88, 13, 56]
valores_earth = [24, 44, 81, 69]
planetas = ["Jupiter", "Venus", "Earth"]
valores = [valores_jupiter, valores_venus, valores_earth]

subtitulos = [
    "Jupiter doesn’t have a solid surface",
    "Venus has extremely high temperatures",
    "Earth is the third planet from the Sun"
]

# ============================================================
# 🧱 FIGURA
# ============================================================
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9
})

fig, axs = plt.subplots(1, 3, figsize=(10, 3), sharey=True)
fig.patch.set_facecolor("white")

for i, ax in enumerate(axs):
    # Fundo 100%
    for y, cat in enumerate(categorias):
        ax.barh(cat, 100, color='#F2F2F2', height=0.45, edgecolor="none", zorder=1)
    #F2F2F2
    #'#D9D9D9'
    # Barras reais
    ax.barh(categorias, valores[i], color=cores, height=0.45, edgecolor="none", alpha=0.9, zorder=2)
    
    # Título e subtítulo
    ax.set_title(planetas[i], fontsize=12, fontweight="bold", color="#323C32", pad=10)
    ax.text(0, -0.7, subtitulos[i], fontsize=8, color="#555555", wrap=True)
    
    # Remover eixos e linhas
    ax.set_xlim(0, 100)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Rótulos dos valores
    for y, v in enumerate(valores[i]):
        ax.text(v + 2, y, f"{v}%", va="center", ha="left", fontsize=8, color="#333333", zorder=3)

# ============================================================
# 🧾 LEGENDA
# ============================================================
patches = [
    mpatches.Patch(color=cores[0], label="Mercury is small"),
    mpatches.Patch(color=cores[1], label="Saturn has rings"),
    mpatches.Patch(color=cores[2], label="Pluto is dwarf"),
    mpatches.Patch(color=cores[3], label="Mars is very cold")
]
fig.legend(handles=patches, loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.08),
           frameon=False, fontsize=8)

# ============================================================
# ✨ TÍTULO PRINCIPAL — FONTE 'Source Sans Pro'
# ============================================================
# Aplica a fonte apenas no título geral
plt.suptitle(
    "Bar Graph Infographics",
    fontsize=16,
    fontweight="bold",
    color="#323C32",
    fontfamily="Source Sans Pro",
    fontname = "Source Sans Pro",
    y=1.05
)

plt.tight_layout()

# ============================================================
# 🚀 EXIBIÇÃO STREAMLIT
# ============================================================
st.pyplot(fig)


import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
import matplotlib.dates as mdates

# ============================================================
# 🧭 TÍTULO STREAMLIT
# ============================================================
st.title("📅 Gráfico de Gantt — Estilo corporativo com linha de progresso")

# ============================================================
# ⚙️ DADOS DE EXEMPLO
# ============================================================
dados = {
    "Tarefa": [f"Tarefa #{i:02d}" for i in range(1, 10)],
    "Início": [
        "2025-02-04", "2025-02-05", "2025-02-12", "2025-02-09", "2025-02-04",
        "2025-02-12", "2025-02-07", "2025-02-08", "2025-02-07"
    ],
    "Dias_concluidos": [43, 42, 35, 15, 43, 0, 40, 39, 16],
    "Dias_restantes": [15, 32, 19, 0, 10, 38, 0, 9, 0]
}
df = pd.DataFrame(dados)
df["Início"] = pd.to_datetime(df["Início"])
df["Fim_concluido"] = df["Início"] + pd.to_timedelta(df["Dias_concluidos"], unit="D")
df["Fim_total"] = df["Fim_concluido"] + pd.to_timedelta(df["Dias_restantes"], unit="D")

# ============================================================
# 📅 PARÂMETROS
# ============================================================
data_hoje = pd.to_datetime("2025-03-01")  # linha vertical de referência

cor_concluido = "#46D7FF"   # azul institucional
cor_restante = "#FF8C42"    # laranja
cor_linha = "#E60050"       # linha vertical
fonte_padrao = "DejaVu Sans"

# ============================================================
# 🎨 GRÁFICO
# ============================================================
fig, ax = plt.subplots(figsize=(10, 4))
fig.patch.set_facecolor("white")

# Inverte a ordem das tarefas (para parecer com o exemplo)
df = df.iloc[::-1]

for i, row in enumerate(df.itertuples()):
    # parte concluída
    ax.barh(
        row.Tarefa,
        width=row.Dias_concluidos,
        left=row.Início,
        color=cor_concluido,
        edgecolor="none",
        height=0.4,
        label="Concluído" if i == 0 else "",
        zorder=2
    )
    
    # parte restante
    if row.Dias_restantes > 0:
        ax.barh(
            row.Tarefa,
            width=row.Dias_restantes,
            left=row.Fim_concluido,
            color=cor_restante,
            edgecolor="none",
            height=0.4,
            label="Restante" if i == 0 else "",
            zorder=2
        )

# Linha de referência vertical (data atual)
ax.axvline(data_hoje, color=cor_linha, linewidth=2, zorder=3)

# ============================================================
# ✨ ESTILO
# ============================================================
ax.xaxis_date()
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d-%b"))
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
plt.xticks(rotation=45, ha="right", fontsize=8)
ax.set_yticks(range(len(df)))
ax.set_yticklabels(df["Tarefa"], fontsize=9)
ax.tick_params(axis="y", length=0)
ax.grid(axis="x", linestyle="--", color="lightgray", alpha=0.5)
ax.set_axisbelow(True)
ax.set_title("Progresso das Tarefas", fontsize=14, fontweight="bold", fontfamily="Source Sans Pro", color="#323C32", pad=10)
ax.set_xlabel("")
ax.set_ylabel("")

# remove moldura e deixar visual limpo
for spine in ["top", "right", "left", "bottom"]:
    ax.spines[spine].set_visible(False)

# Legenda
ax.legend(loc="upper right", frameon=False, fontsize=8)

plt.tight_layout()
st.pyplot(fig)



import matplotlib.patches as mpatches


# ============================================================
# 🧭 TÍTULO
# ============================================================
st.title("📊 Infográfico de Barras Segmentadas — Estilo Corporativo")

# ============================================================
# ⚙️ DADOS
# ============================================================
planetas = ["Venus", "Saturn", "Jupiter", "Mars"]
descricoes = [
    "Venus is a hot planet",
    "Saturn is the ringed planet",
    "Jupiter is a big planet",
    "Mars is made of basalt"
]
percentuais = [74, 96, 66, 78]

# Cada barra é composta por 4 segmentos (poderiam representar períodos ou componentes)
segmentos = np.array([
    [20, 25, 15, 14],
    [30, 32, 20, 14],
    [22, 20, 15, 9],
    [25, 28, 15, 10]
])

# ============================================================
# 🎨 CORES E ESTILO
# ============================================================
cores_segmentos = ["#70B7FF", "#B9A6FF", "#A2E8C3", "#F5A6B8"]
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9
})

fig, ax = plt.subplots(figsize=(8, 3.5))
fig.patch.set_facecolor("white")

# ============================================================
# 📊 CONSTRUÇÃO DAS BARRAS
# ============================================================
y_pos = np.arange(len(planetas))

for i, (nome, desc, seg, pct) in enumerate(zip(planetas, descricoes, segmentos, percentuais)):
    esquerda = 0
    for s, cor in zip(seg, cores):
        ax.barh(i, s, left=esquerda, color=cor, height=0.4, edgecolor="none")
        esquerda += s

    # marcador circular no final da barra
    ax.plot(esquerda, i, "o", color="#323C32", markersize=4)

    # texto percentual à direita
    ax.text(esquerda + 3, i, f"{pct}%", va="center", ha="left", fontsize=9, color="#323C32", fontweight="bold")

    # título e descrição à esquerda
    ax.text(-15, i + 0.1, nome, fontsize=10, fontweight="bold", color="#323C32", ha="right")
    ax.text(-15, i - 0.25, desc, fontsize=8, color="#555555", ha="right")

# ============================================================
# ✨ ESTILO DO EIXO
# ============================================================
ax.set_xlim(-25, 110)
ax.set_ylim(-1, len(planetas))
ax.axis("off")

# ============================================================
# 🧾 LEGENDA INFERIOR
# ============================================================
legenda = [
    mpatches.Patch(color=cores_segmentos[0], label="2XXX"),
    mpatches.Patch(color=cores_segmentos[1], label="2XXX"),
    mpatches.Patch(color=cores_segmentos[2], label="2XXX"),
    mpatches.Patch(color=cores_segmentos[3], label="2XXX"),
]
fig.legend(handles=legenda, loc="lower center", ncol=4, bbox_to_anchor=(0.5, -0.1),
           frameon=False, fontsize=8)

# ============================================================
# 🪶 TÍTULO PRINCIPAL
# ============================================================
plt.suptitle(
    "Bar Graph Infographics",
    fontsize=14,
    fontweight="bold",
    color="#524939",
    fontfamily="Source Sans Pro",
    y=1.05
)
plt.suptitle("Distribuição de Indicadores", fontsize=13, fontfamily="Liberation Serif", color="#323C32")

plt.tight_layout()
st.pyplot(fig)



st.title("📊 Gráfico de Barras Radiais — Versão Compacta")

# ============================================================
# ⚙️ DADOS
# ============================================================
instituicoes = ["Fremontia Academy", "Jefferson Institute", "Thelonius College"]
valores = [95, 75, 50]
#cores = ["#46D7FF", "#FFCD00", "#E60050"]

# ============================================================
# 🧮 FUNÇÃO DE DESENHO
# ============================================================
def radial_donut(valores, cores, labels, tamanho=(4, 4)):  # 👈 menor figura
    fig, ax = plt.subplots(figsize=tamanho, subplot_kw={"projection": "polar"})
    ax.set_theta_direction(-1)
    ax.set_theta_offset(np.pi / 2.0)
    ax.set_facecolor("white")

    # 🌀 ajuste da espessura dos anéis
    for i, (valor, cor, label) in enumerate(zip(valores, cores, labels)):
        raio_externo = 0.95 - i * 0.22   # 👈 anéis mais próximos
        raio_interno = raio_externo - 0.18
        theta = np.linspace(0, 2 * np.pi * valor / 100, 100)

        # Barra do donut
        ax.bar(
            x=0,
            height=raio_externo - raio_interno,
            width=2 * np.pi * valor / 100,
            bottom=raio_interno,
            color=cor,
            edgecolor="none"
        )

        # Texto percentual
        angulo_texto = np.deg2rad(valor * 1.8)
        ax.text(
            angulo_texto,
            (raio_externo + raio_interno) / 2,
            f"{valor}%",
            color="#323C32",
            fontsize=10,
            fontweight="bold",
            ha="center",
            va="center"
        )

    # 🎨 estilo limpo
    ax.set_ylim(0, 1.1)
    ax.set_yticks([])
    ax.set_xticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    # 🧾 legenda
    plt.legend(labels, loc="lower center", bbox_to_anchor=(0.5, -0.15),
               ncol=3, frameon=False, fontsize=8)

    # título
    plt.title(
        "Níveis de Desempenho por Instituição",
        fontsize=12,
        fontweight="bold",
        fontfamily="Source Sans Pro",
        color="#323C32",
        pad=10
    )

    plt.tight_layout()
    return fig

# ============================================================
# 🚀 EXIBIÇÃO STREAMLIT
# ============================================================
fig = radial_donut(valores, cores, instituicoes)
st.pyplot(fig)




# ============================================================
# 🎨 TÍTULO STREAMLIT
# ============================================================
st.title("📈 Gráfico de Densidade — Estilo ggplot2")

# ============================================================
# ⚙️ DADOS DE EXEMPLO
# ============================================================
np.random.seed(42)
n = 500
# Distribuições diferentes para simular faixas de renda, por exemplo
dados = pd.DataFrame({
    "probs": np.concatenate([
        np.random.beta(2, 8, n),   # distribuição mais concentrada à esquerda
        np.random.beta(4, 2, n)    # distribuição mais espalhada
    ]),
    "faixa": ["<=50K"] * n + [">50K"] * n
})

# ============================================================
# 🎨 ESTILO DO PLOT
# ============================================================
sns.set_style("whitegrid")
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 9,
    "axes.edgecolor": "#CCCCCC",
    "axes.linewidth": 0.6
})

fig, ax = plt.subplots(figsize=(8, 3.5))

# ============================================================
# 📊 GRÁFICO DE DENSIDADE
# ============================================================
sns.kdeplot(
    data=dados,
    x="probs",
    hue="faixa",
    fill=True,
    common_norm=False,
    alpha=0.5,
    linewidth=1.2,
    palette=["#F4A6A6", "#A6D8F4"],
    ax=ax
)

# ============================================================
# 💅 AJUSTES VISUAIS
# ============================================================
ax.set_title("Distribuição de Probabilidades por Faixa", fontsize=13, fontweight="bold", color="#323C32", pad=10)
ax.set_xlabel("probs", fontsize=9)
ax.set_ylabel("density", fontsize=9)
ax.legend(title="faixa", frameon=True, facecolor="white", edgecolor="#CCCCCC")

# Linhas e grades sutis
ax.grid(True, linestyle="--", alpha=0.2)
for spine in ["top", "right"]:
    ax.spines[spine].set_visible(False)

plt.tight_layout()
st.pyplot(fig)


# ============================================================
# 🎨 TÍTULO STREAMLIT
# ============================================================
st.title("📊 Gráfico Minimalista — Linhas Horizontais e Pontos-Chave")

# ============================================================
# ⚙️ DADOS DE EXEMPLO
# ============================================================
np.random.seed(42)
categorias = ["Renda Fixa", "Multimercado", "Ações", "Câmbio", "Crédito Privado"]
dados = {cat: np.random.normal(loc=np.random.uniform(70, 120), scale=10, size=10) for cat in categorias}

# ============================================================
# 📊 GRÁFICO
# ============================================================
fig, ax = plt.subplots(figsize=(8, 3.5))
fig.patch.set_facecolor("white")

# ============================================================
# 🎨 ESCALA FIXA (para todas as linhas)
# ============================================================
x_min, x_max = 50, 150
y_positions = np.arange(len(categorias))[::-1]

# offset para o texto da categoria (esquerda)
offset_texto = -10

# ============================================================
# 🧮 DESENHO DAS LINHAS E PONTOS
# ============================================================
for i, cat in enumerate(categorias):
    serie = dados[cat]
    y = y_positions[i]

    minimo = np.min(serie)
    maximo = np.max(serie)
    media = np.mean(serie)
    inicial = serie[0]
    final = serie[-1]

    # linha base (toda no mesmo range)
    ax.plot([x_min, x_max], [y, y], color="#E0E0E0", linewidth=1.3, zorder=1)

    # marcadores principais
    ax.scatter(minimo, y, color="#E60050", s=30, zorder=2, label="Mínimo" if i == 0 else "")
    ax.scatter(maximo, y, color="#3FA110", s=30, zorder=2, label="Máximo" if i == 0 else "")
    ax.scatter(media, y, color="#46D7FF", s=35, zorder=2, label="Média" if i == 0 else "")
    ax.scatter(inicial, y, color="#FF6400", s=25, zorder=2, label="Inicial" if i == 0 else "")
    ax.scatter(final, y, color="#5A645A", s=25, zorder=2, label="Final" if i == 0 else "")

    # texto fixo da categoria (alinhado no canto esquerdo)
    ax.text(offset_texto, y, cat, ha="right", va="center", fontsize=9, color="#333333")

# ============================================================
# 🧾 ESTILO GLOBAL
# ============================================================
ax.set_xlim(50, x_max + 5)
ax.set_ylim(-0.5, len(categorias) - 0.5)
ax.set_yticks([])
ax.set_xlabel("")
ax.set_ylabel("")
ax.grid(False)

for spine in ["top", "right", "left", "bottom"]:
    ax.spines[spine].set_visible(False)

# legenda
ax.legend(loc="lower center", ncol=5, bbox_to_anchor=(0.5, -0.2),
          frameon=False, fontsize=8)

# título
plt.title(
    "Indicadores por Categoria — Mínimo, Máximo, Média, Inicial e Final",
    fontsize=12,  fontfamily="Source Sans Pro", color="#323C32", pad=10
)

plt.tight_layout()
st.pyplot(fig)



# ============================================================
# 🎨 TÍTULO STREAMLIT
# ============================================================
st.title("📊 Infográfico de Barras — Estilo Moderno e Minimalista")

# ============================================================
# ⚙️ DADOS
# ============================================================
itens = [
    "Earth is the only planet that harbors life",
    "Mercury is the smallest planet of them all",
    "It’s the biggest planet in the Solar System",
    "Neptune is the farthest planet from the Sun"
]
valores = [40, 62, 23, 82]
cores = ["#F77E7E", "#B58CF2", "#5BC5F2", "#6DDDC1"]

# ============================================================
# 📊 GRÁFICO
# ============================================================
fig, ax = plt.subplots(figsize=(8, 3.5))
fig.patch.set_facecolor("white")

# posições verticais (de cima para baixo)
y_pos = np.arange(len(itens))[::-1]

# ============================================================
# 🎨 ESTILO DE BARRAS
# ============================================================
for i, (texto, valor, cor) in enumerate(zip(itens, valores, cores)):
    y = y_pos[i]
    
    # barra colorida
    ax.barh(y, valor, color=cor, height=0.4, edgecolor="none", alpha=0.9)
    
    # fundo cinza claro (100%)
    ax.barh(y, 100, color="#F0F0F0", height=0.4, zorder=0)
    
    # texto da categoria (esquerda)
    ax.text(-2, y, texto, ha="right", va="center", fontsize=9, color="#333333", wrap=True)
    
    # valor percentual (direita)
    ax.text(valor + 2, y, f"{valor}%", ha="left", va="center", fontsize=10, fontweight="bold", color="#323C32")

# ============================================================
# ✨ ESTILO GLOBAL
# ============================================================
ax.set_xlim(-10, 115)
ax.set_ylim(-0.5, len(itens) - 0.5)
ax.set_yticks([])
ax.set_xticks([])
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.spines["bottom"].set_visible(False)
ax.grid(False)

plt.title(
    "Bar Graph Infographics",
    fontsize=14,
    fontweight="bold",
    fontfamily="Source Sans Pro",
    color="#323C32",
    pad=10
)

plt.tight_layout()
st.pyplot(fig)




# ============================================================
# 🎨 TÍTULO STREAMLIT
# ============================================================
st.title("📊 Gráfico de Barras Horizontais — Valores Positivos e Negativos")

# ============================================================
# ⚙️ DADOS DE EXEMPLO
# ============================================================
categorias = ["Renda Fixa", "Multimercado", "Ações", "Câmbio", "Crédito Privado", "Exterior"]
valores = [12, -8, 15, -10, 6, -4]

# Cores para positivos e negativos
cores = ["#3FA110" if v >= 0 else "#E60050" for v in valores]

# ============================================================
# 📊 GRÁFICO
# ============================================================
fig, ax = plt.subplots(figsize=(8, 3.5))
fig.patch.set_facecolor("white")

y_pos = np.arange(len(categorias))[::-1]

# Barras horizontais (positivas e negativas)
ax.barh(y_pos, valores, color=cores, height=0.45, edgecolor="none", alpha=0.9)

# Linha vertical de referência no zero
ax.axvline(0, color="#CCCCCC", linewidth=1)

# ============================================================
# 💬 RÓTULOS E TEXTO
# ============================================================
for i, (cat, val) in enumerate(zip(categorias, valores)):
    y = y_pos[i]
    # Categoria alinhada à esquerda
    ax.text(-max(abs(np.array(valores))) * 1.2, y, cat, ha="left", va="center",
            fontsize=9, color="#333333", fontweight="bold")
    # Valor ao final da barra
    offset = 1 if val >= 0 else -1
    ax.text(val + offset, y, f"{val:+}%", ha="left" if val >= 0 else "right",
            va="center", fontsize=9, color="#323C32", fontweight="bold")

# ============================================================
# 🧾 ESTÉTICA GLOBAL
# ============================================================
ax.set_xlim(-20, 20)
ax.set_yticks([])
ax.set_xticks([-20, -10, 0, 10, 20])
ax.set_xticklabels(["-20%", "-10%", "0%", "10%", "20%"], fontsize=8, color="#666666")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.spines["bottom"].set_visible(False)
ax.grid(False)

# título
plt.title(
    "Variação Percentual por Categoria",
    fontsize=13,
    fontweight="bold",
    fontfamily="Source Sans Pro",
    color="#323C32",
    pad=10
)

plt.tight_layout()
st.pyplot(fig)





st.title("📊 Gráfico de Cascata — Estilo Elegante Sicredi")

# ============================================================
# ⚙️ DADOS DE EXEMPLO
# ============================================================
etapas = ["Receita Bruta", "Descontos", "Custos", "Despesas", "Impostos", "Lucro Líquido"]
valores = [500, -80, -150, -70, -50, 150]  # positivos e negativos

# ============================================================
# 🧮 CÁLCULOS DA CASCATA
# ============================================================
total = 0
base = [0]
for v in valores[:-1]:
    total += v
    base.append(total)

# cores institucionais: verde para ganhos, laranja para perdas
cores = ["#3FA110" if v >= 0 else "#FF6400" for v in valores]

# ============================================================
# 📊 CONSTRUÇÃO DO GRÁFICO
# ============================================================
fig, ax = plt.subplots(figsize=(8, 4))
fig.patch.set_facecolor("white")

# barras
for i in range(len(valores)):
    ax.bar(
        etapas[i],
        valores[i],
        bottom=base[i],
        color=cores[i],
        width=0.6,
        edgecolor="none",
        alpha=0.9,
        zorder=3
    )

# linha de conexão entre as barras
for i in range(len(valores) - 1):
    x0, x1 = i, i + 1
    y0 = base[i] + valores[i]
    y1 = base[i + 1]
    ax.plot([x0, x1], [y0, y1], color="#AAAAAA", linewidth=1.2, zorder=2)

# ============================================================
# ✍️ RÓTULOS DOS VALORES
# ============================================================
for i in range(len(valores)):
    y = base[i] + valores[i] / 2
    ax.text(
        i, y, f"{valores[i]:+}",
        ha="center", va="center",
        fontsize=9, color="white" if abs(valores[i]) > 50 else "#323C32",
        fontweight="bold"
    )

# total final destacado
ax.text(len(valores) - 1, base[-1] + valores[-1] + 10, "Lucro Final", 
        ha="center", va="bottom", fontsize=10, fontweight="bold", color="#3FA110")

# ============================================================
# 💅 ESTÉTICA GLOBAL
# ============================================================
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)
ax.spines["bottom"].set_visible(False)
ax.grid(axis="y", color="#EEEEEE", linestyle="--", alpha=0.6)
ax.set_axisbelow(True)
ax.set_ylabel("")
ax.set_xlabel("")
ax.tick_params(axis='x', labelrotation=20)
ax.set_title(
    "Composição do Resultado Financeiro",
    fontsize=13,
    fontweight="bold",
    fontfamily="Source Sans Pro",
    color="#323C32",
    pad=10
)

plt.tight_layout()
st.pyplot(fig)

st.title("📊 Boxplot Horizontal — Outliers verdes e elegantes")

# ============================================================
# ⚙️ DADOS DE EXEMPLO
# ============================================================
np.random.seed(42)
categorias = ["Renda Fixa", "Multimercado", "Ações", "Câmbio", "Crédito Privado"]
dados = [np.random.normal(loc=np.random.uniform(5, 15), scale=np.random.uniform(1, 3), size=80) for _ in categorias]
df = pd.DataFrame(dados, index=categorias).T

# ============================================================
# 🎨 GRÁFICO
# ============================================================
fig, ax = plt.subplots(figsize=(8, 4))
fig.patch.set_facecolor("white")

# Paleta institucional suave
cores = ["#C8E6C9", "#A5D6A7", "#81C784", "#4CAF50", "#3FA110"]

# Boxplot horizontal com estilo refinado
bplot = ax.boxplot(
    [df[c] for c in categorias],
    vert=False,
    patch_artist=True,
    medianprops=dict(color="#1C1C1C", linewidth=1.4),
    boxprops=dict(linewidth=0, alpha=0.9),
    whiskerprops=dict(color="#AAAAAA", linewidth=1),
    capprops=dict(color="#AAAAAA", linewidth=1),
    # 🎯 OUTLIERS personalizados
    flierprops=dict(
        marker="o", 
        markersize=5, 
        markerfacecolor="#3FA110",  # verde Sicredi
        markeredgecolor="#AAAAAA",  # borda cinza
        alpha=0.8
    )
)

# aplicar as cores nas caixas
for patch, cor in zip(bplot["boxes"], cores):
    patch.set_facecolor(cor)

# ============================================================
# 💬 ESTILO E LAYOUT
# ============================================================
ax.set_yticklabels(categorias, fontsize=9, color="#333333", fontweight="bold")
ax.set_xlabel("Retorno (%)", fontsize=9, color="#333333")
ax.set_title(
    "Distribuição de Retornos por Categoria",
    fontsize=13,
    fontweight="bold",
    fontfamily="Source Sans Pro",
    color="#1C1C1C",
    pad=10
)

for spine in ["top", "right", "left"]:
    ax.spines[spine].set_visible(False)

ax.grid(axis="x", linestyle="--", color="#E0E0E0", alpha=0.6)
ax.set_axisbelow(True)

plt.tight_layout()
st.pyplot(fig)




# ============================================================
# 🎨 TÍTULO
# ============================================================
st.title("📊 Hourly Rate — Full-Time vs Part-Time Roles")

# ============================================================
# ⚙️ DADOS EXEMPLO
# ============================================================
np.random.seed(42)
categorias = ["F", "P"]
dados = []

for cat in categorias:
    base = 35 if cat == "F" else 20
    scale = 8 if cat == "F" else 5
    valores = np.random.normal(loc=base, scale=scale, size=60)
    dados.extend([{"Role": cat, "Hourly Rate": v} for v in valores])

# adiciona um outlier visual (sem exagero)
dados.append({"Role": "F", "Hourly Rate": 130})

df = pd.DataFrame(dados)

# ============================================================
# 🎨 ESTILO GERAL
# ============================================================
sns.set_style("whitegrid")
plt.rcParams.update({
    "font.family": "Liberation Serif",
    "axes.edgecolor": "#CCCCCC",
    "axes.linewidth": 0.6
})

# Paleta institucional
cores = {"F": "#46D7FF", "P": "#FF6400"}

# ============================================================
# 📊 GRÁFICO
# ============================================================
fig, ax = plt.subplots(figsize=(8, 4.5))
fig.patch.set_facecolor("white")

# Pontos individuais (strip)
sns.stripplot(
    data=df, x="Hourly Rate", y="Role",
    hue="Role", palette=cores,
    alpha=0.7, size=6, jitter=0.25, ax=ax
)

# Boxplot translúcido (sem bordas)
sns.boxplot(
    data=df, x="Hourly Rate", y="Role",
    hue="Role", palette=cores,
    boxprops=dict(alpha=0.15, linewidth=0),
    showcaps=True, fliersize=0, width=0.4,
    saturation=1, ax=ax
)

# ============================================================
# 💅 AJUSTES ESTÉTICOS
# ============================================================
ax.set_title("Hourly Rate for Full and Part-Time Roles", fontsize=13,
             fontweight="bold", fontfamily="Source Sans Pro", color="#1C1C1C", pad=15)

ax.set_xlabel("Hourly Rate", fontsize=9, color="#333333")
ax.set_ylabel("")
ax.legend().remove()

# grades e limites
ax.grid(True, axis="x", linestyle="--", color="#E0E0E0", alpha=0.6)
ax.set_axisbelow(True)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_visible(False)

# formatação eixo X
ax.set_xlim(0, 140)
ax.set_xticks(np.arange(0, 145, 10))
ax.tick_params(axis="x", labelsize=8, colors="#555555")

plt.tight_layout()
st.pyplot(fig)

