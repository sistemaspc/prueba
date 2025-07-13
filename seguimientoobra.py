# app.py

import streamlit as st
import pandas as pd
import plotly.express as px

# Título
st.markdown("<h1 style='font-size: 36px;'>📋 Seguimiento de Obra PCM</h1>", unsafe_allow_html=True)
st.markdown("Sube los archivos locales de entradas, salidas y obras para visualizar los datos.")

# Subida de archivos
st.sidebar.markdown("### 📤 Carga tus archivos")
archivo_entradas = st.sidebar.file_uploader("Sube el archivo de ENTRADAS (.xlsx)", type=["xlsx"], key="entradas")
archivo_salidas = st.sidebar.file_uploader("Sube el archivo de SALIDAS (.xlsx)", type=["xlsx"], key="salidas")
archivo_obras = st.sidebar.file_uploader("Sube el archivo de OBRAS (.xlsx)", type=["xlsx"], key="obras")

# Validación: si los 3 archivos están cargados
if archivo_entradas and archivo_salidas and archivo_obras:

    # Cargar archivos
    entradas = pd.read_excel(archivo_entradas)
    salidas = pd.read_excel(archivo_salidas)
    obras = pd.read_excel(archivo_obras)

    # Normalizar nombres de columnas
    entradas.columns = entradas.columns.str.lower().str.strip()
    salidas.columns = salidas.columns.str.lower().str.strip()
    obras.columns = obras.columns.str.lower().str.strip()

    # Validar existencia de columna 'oth_numero' en todos los archivos
    columnas_requeridas = ['oth_numero']
    for df_nombre, df in zip(['Entradas', 'Salidas', 'Obras'], [entradas, salidas, obras]):
        for col in columnas_requeridas:
            if col not in df.columns:
                st.error(f"❌ La columna '{col}' no está en el archivo de {df_nombre}. Verifica los nombres de columna.")
                st.stop()

    # Hacer merge con obras
    entradas = entradas.merge(obras, on='oth_numero', how='left')
    salidas = salidas.merge(obras, on='oth_numero', how='left')

    # Selección de vista
    tipo_vista = st.radio("Selecciona tipo de vista", ["Entradas", "Salidas"])
    datos = entradas if tipo_vista == "Entradas" else salidas

    # Filtro de O.T.
    ot_unicas = datos['oth_numero'].dropna().unique()
    ot_seleccionada = st.selectbox("Selecciona una Orden de Trabajo (O.T.)", ot_unicas)

    # Mostrar datos
    df_filtrado = datos[datos['oth_numero'] == ot_seleccionada]

    if df_filtrado.empty:
        st.warning("No se encontraron datos para la O.T. seleccionada.")
    else:
        nombre_obra = df_filtrado['oth_nombre'].iloc[0] if 'oth_nombre' in df_filtrado.columns else "Desconocida"
        st.subheader(f"📌 Datos para O.T. {ot_seleccionada} - {nombre_obra}")

        columnas_a_mostrar = ['fecha', 'material', 'articulo', 'cantidad', 'oth_numero']
        if 'oth_nombre' in df_filtrado.columns:
            columnas_a_mostrar.append('oth_nombre')

        st.dataframe(df_filtrado[columnas_a_mostrar])

        resumen = df_filtrado.groupby('articulo')['cantidad'].sum().reset_index()
        fig = px.bar(resumen, x='articulo', y='cantidad', title='Total por artículo')
        st.plotly_chart(fig)

else:
    st.info("📂 Por favor, sube los tres archivos para comenzar: Entradas, Salidas y Obras.")
