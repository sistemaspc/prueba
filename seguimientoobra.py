import streamlit as st
import pandas as pd

st.title("📦 Seguimiento de Obra - PCM Ingeniería")

# Cargar archivos
st.sidebar.header("🔽 Subir Archivos Excel")

salidas_file = st.sidebar.file_uploader("Sube archivo de SALIDAS", type=["xlsx"], key="salidas")
entradas_file = st.sidebar.file_uploader("Sube archivo de ENTRADAS", type=["xlsx"], key="entradas")
obras_file   = st.sidebar.file_uploader("Sube archivo de OBRAS", type=["xlsx"], key="obras")

# Verifica si todos los archivos fueron cargados
if salidas_file and entradas_file and obras_file:
    try:
        df_salidas = pd.read_excel(salidas_file)
        df_entradas = pd.read_excel(entradas_file)
        df_obras = pd.read_excel(obras_file)

        st.success("✅ Archivos cargados correctamente")

        # Validación básica de columnas necesarias
        columnas_salidas = {'oth_numero', 'cco_codigo', 'art_nombre', 'sad_cantidad'}
        columnas_entradas = {'oth_numero', 'art_nombre', 'end_cantidad'}
        columnas_obras = {'oth_numero', 'oth_nombre', 'cco_codigo'}

        if columnas_salidas.issubset(df_salidas.columns) and \
           columnas_entradas.issubset(df_entradas.columns) and \
           columnas_obras.issubset(df_obras.columns):

            st.subheader("📊 Resumen de Datos")

            st.write("### Obras disponibles:")
            st.dataframe(df_obras[['oth_numero', 'oth_nombre', 'cco_codigo']].drop_duplicates())

            st.write("### Top materiales con más salidas:")
            top_materiales = df_salidas.groupby('art_nombre')['sad_cantidad'].sum().sort_values(ascending=False).head(10)
            st.bar_chart(top_materiales)

            st.write("### Entradas totales por material:")
            entradas_sum = df_entradas.groupby('art_nombre')['end_cantidad'].sum().sort_values(ascending=False).head(10)
            st.bar_chart(entradas_sum)

        else:
            st.error("❌ Los archivos no contienen las columnas requeridas. Verifica nombres como 'oth_numero', 'cco_codigo', 'art_nombre', etc.")

    except Exception as e:
        st.exception(f"Error al procesar los archivos: {e}")

else:
    st.warning("⬅️ Carga los tres archivos para continuar (salidas, entradas y obras)")
