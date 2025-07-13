import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Seguimiento de Obra PCM", layout="wide")

st.title("🗒️ Seguimiento de Obra PCM")
st.markdown("Este es un prototipo para visualizar datos de seguimiento de obra desde archivos locales.")

# --- Sección de carga de archivos ---
st.subheader("📂 Carga de archivos")

col1, col2, col3 = st.columns(3)

with col1:
    entradas_file = st.file_uploader("Sube el archivo de **entradas**", type=["xlsx"], key="entradas")
with col2:
    salidas_file = st.file_uploader("Sube el archivo de **salidas**", type=["xlsx"], key="salidas")
with col3:
    obras_file = st.file_uploader("Sube el archivo de **obras**", type=["xlsx"], key="obras")

# --- Validación de archivos cargados ---
if not entradas_file or not salidas_file or not obras_file:
    st.error("⚠️ Debes subir los tres archivos: entradas, salidas y obras para continuar.")
    st.stop()

# --- Lectura de archivos cargados ---
entradas_df = pd.read_excel(entradas_file)
salidas_df = pd.read_excel(salidas_file)
obras_df = pd.read_excel(obras_file)

# --- Validación básica de columnas esperadas ---
col_entradas = {'fecha', 'material', 'cantidad', 'oth_numero'}
col_salidas = {'fecha', 'material', 'cantidad', 'oth_numero'}
col_obras = {'oth_numero', 'oth_nombre', 'cco_codigo'}

if not col_entradas.issubset(set(entradas_df.columns)) or \
   not col_salidas.issubset(set(salidas_df.columns)) or \
   not col_obras.issubset(set(obras_df.columns)):
    st.error("⚠️ Las columnas de los archivos no coinciden con lo esperado.")
    st.stop()

# --- Unificación con nombre de obra ---
entradas_df = entradas_df.merge(obras_df, on='oth_numero', how='left')
salidas_df = salidas_df.merge(obras_df, on='oth_numero', how='left')

# --- Cálculo de resumen por obra ---
resumen_entradas = entradas_df.groupby('oth_nombre')['cantidad'].sum().reset_index(name='Total Entradas')
resumen_salidas = salidas_df.groupby('oth_nombre')['cantidad'].sum().reset_index(name='Total Salidas')

resumen = pd.merge(resumen_entradas, resumen_salidas, on='oth_nombre', how='outer').fillna(0)
resumen['Inventario Actual'] = resumen['Total Entradas'] - resumen['Total Salidas']

st.subheader("📊 Resumen de inventario por obra")
st.dataframe(resumen, use_container_width=True)

# --- Visualización gráfica ---
fig = px.bar(resumen, x="oth_nombre", y="Inventario Actual", title="Inventario Actual por Obra", text_auto=True)
st.plotly_chart(fig, use_container_width=True)
