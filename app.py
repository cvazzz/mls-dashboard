import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import tempfile
import os

st.set_page_config(page_title="Dashboard de Métricas MLS", layout="wide")
st.title("📊 Dashboard Interactivo - Analista de Métricas MLS")

# Leer archivo
uploaded_file = "Reto Analista de Metricas.xlsx"
df = pd.read_excel(uploaded_file)
df.columns = df.columns.str.strip()
df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True)

# Limpiar columnas numéricas
columnas_numericas = [
    "Seguidores", "Alcance", "Interacciones", "Engagement Rate",
    "Cantidad de Posts", "Crecimiento de Seguidores (%)", "CTR"
]
for col in columnas_numericas:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Cálculo adicional
df['Interacciones por 1000 seguidores'] = df['Interacciones'] / df['Seguidores'] * 1000

# Filtros
st.sidebar.header("🎯 Filtros")
plataformas = df['Plataforma'].unique()
plataformas_seleccionadas = st.sidebar.multiselect("Selecciona plataformas", options=plataformas, default=plataformas)

min_date = df['Fecha'].min().date()
max_date = df['Fecha'].max().date()
rango_fecha = st.sidebar.slider("Rango de fechas", min_value=min_date, max_value=max_date, value=(min_date, max_date))

fecha_inicio = pd.to_datetime(rango_fecha[0])
fecha_fin = pd.to_datetime(rango_fecha[1])

df_filtrado = df[
    (df['Plataforma'].isin(plataformas_seleccionadas)) &
    (df['Fecha'] >= fecha_inicio) & 
    (df['Fecha'] <= fecha_fin)
]

# KPIs
st.markdown("### 📌 Indicadores Clave")
col1, col2, col3 = st.columns(3)
col1.metric("👥 Seguidores promedio", f"{df_filtrado['Seguidores'].mean():,.0f}")
col2.metric("📣 Alcance promedio", f"{df_filtrado['Alcance'].mean():,.0f}")
col3.metric("🤝 Engagement promedio", f"{df_filtrado['Engagement Rate'].mean():.2%}")

# Función para exportar gráfico
def guardar_grafico(fig, nombre_archivo):
    temp_path = os.path.join(tempfile.gettempdir(), nombre_archivo)
    fig.write_image(temp_path, format="png")
    return temp_path

graficos_paths = []

# Gráfico 1
st.subheader("📈 Seguidores por Plataforma")
fig1 = px.line(df_filtrado, x="Fecha", y="Seguidores", color="Plataforma", markers=True)
st.plotly_chart(fig1, use_container_width=True)


# Gráfico 2
st.subheader("❤️ Engagement Rate por Plataforma")
fig2 = px.line(df_filtrado, x="Fecha", y="Engagement Rate", color="Plataforma", markers=True)
st.plotly_chart(fig2, use_container_width=True)


# Gráfico 3
st.subheader("🔁 Interacciones por 1000 Seguidores")
fig3 = px.bar(df_filtrado, x="Fecha", y="Interacciones por 1000 seguidores", color="Plataforma", barmode="group")
st.plotly_chart(fig3, use_container_width=True)


# Gráfico 4
st.subheader("🗓️ Publicaciones por Mes")
df_filtrado['Mes'] = df_filtrado['Fecha'].dt.to_period('M').astype(str)
posts_mensuales = df_filtrado.groupby(['Mes', 'Plataforma'])['Cantidad de Posts'].sum().reset_index()
fig4 = px.bar(posts_mensuales, x="Mes", y="Cantidad de Posts", color="Plataforma", barmode="group")
st.plotly_chart(fig4, use_container_width=True)


# Gráfico 5
st.subheader("📊 Crecimiento de Seguidores (%)")
df['Crecimiento de Seguidores (%)'] = pd.to_numeric(df['Crecimiento de Seguidores (%)'], errors='coerce')
crecimiento_data = df_filtrado.dropna(subset=['Crecimiento de Seguidores (%)'])
fig5 = px.line(crecimiento_data, x="Fecha", y="Crecimiento de Seguidores (%)", color="Plataforma", markers=True)
st.plotly_chart(fig5, use_container_width=True)


# Tabla
st.subheader("📋 Datos filtrados")
st.dataframe(df_filtrado)

