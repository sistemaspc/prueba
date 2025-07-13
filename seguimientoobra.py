import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Seguimiento de Obra PCM", layout="wide")

st.markdown("## 📝 Seguimiento de Obra PCM")
st.markdown("Este es un prototipo para visualizar datos de seguimiento de obra desde archivos locales.")

# Sección para cargar archivos
st.sidebar.header("📁 Cargar Archivos Excel")

uploaded_entradas = st.sidebar.file_uploader("📥 Subir archivo de ENTRADAS", type=["xlsx"], key="entradas")
uploaded_salidas = st.sidebar.file_uploader("📤 Subir archivo de SALIDAS", type=["xlsx"], key="salidas")
uploaded_obras = st.sidebar.file_uploader("📂 Subir archivo de OBRAS", type=["xlsx"], key="obras")

# Validación de carga
if uploaded_entradas is None or uploaded_salidas is None or uploaded_obras is None:
    st.error("❌ No se encontraron los tres archivos requeridos (entradas, salidas y obras). Súbelos desde la barra lateral.")
else:
    try:
        df_entradas = pd.read_excel(uploaded_entradas)
        df_salidas = pd.read_excel(uploaded_salidas)
        df_obras = pd.read_excel(uploaded_obras)

        # Verifica las columnas esperadas en obras
        if 'cco_codigo' not in df_obras.columns or 'oth_nombre' not in df_obras.columns:
            st.error("❌ El archivo de obras debe tener las columnas: 'cco_codigo' y 'oth_nombre'.")
        else:
            # Unir las obras a las salidas
            df_salidas = df_salidas.merge(df_obras[['cco_codigo', 'oth_nombre']], how='left', on='cco_codigo')

            st.success("✅ Archivos cargados correctamente.")

            # Mostrar vista previa
            with st.expander("🔍 Vista previa de las Entradas"):
                st.dataframe(df_entradas.head(10), use_container_width=True)

            with st.expander("🔍 Vista previa de las Salidas (ya incluye 'oth_nombre')"):
                st.dataframe(df_salidas.head(10), use_container_width=True)

            with st.expander("📑 Vista previa de Obras"):
                st.dataframe(df_obras.head(10), use_container_width=True)

            # Gráfico de ejemplo por obra
            st.markdown("### 📊 Consumo por Obra (basado en salidas)")
            if 'oth_nombre' in df_salidas.columns:
                consumo_por_obra = df_salidas['oth_nombre'].value_counts().reset_index()
                consumo_por_obra.columns = ['Obra', 'Cantidad']
                fig = px.bar(consumo_por_obra, x='Obra', y='Cantidad', title="Cantidad de salidas por obra")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No se puede generar el gráfico porque falta 'oth_nombre'.")

    except Exception as e:
        st.error(f"⚠️ Error al procesar los archivos: {e}")
