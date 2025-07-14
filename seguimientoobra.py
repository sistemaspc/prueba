import streamlit as st
import pandas as pd
import io
from datetime import datetime

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

            # Panel interactivo
            st.subheader("🔎 Consulta por Obra, Material y Artículo")

            ots = sorted(df_entradas['oth_numero'].dropna().astype(str).unique())
            ot_selected = st.selectbox("Selecciona O.T.", options=ots)

            obra_match = df_entradas[df_entradas['oth_numero'].astype(str) == ot_selected]['oth_nombre'].dropna().unique()
            obra_nombre = obra_match[0] if len(obra_match) > 0 else "Sin nombre"
            st.text(f"Nombre de la Obra: {obra_nombre}")

            materiales = pd.concat([
                df_entradas[df_entradas['oth_numero'].astype(str) == ot_selected]['gra_nombre'],
                df_salidas[df_salidas['oth_numero'].astype(str) == ot_selected]['gra_nombre']
            ]).dropna().unique()
            material_selected = st.selectbox("Selecciona Material", options=sorted(materiales))

            articulos = pd.concat([
                df_entradas[(df_entradas['oth_numero'].astype(str) == ot_selected) & (df_entradas['gra_nombre'] == material_selected)]['art_nombre'],
                df_salidas[(df_salidas['oth_numero'].astype(str) == ot_selected) & (df_salidas['gra_nombre'] == material_selected)]['art_nombre']
            ]).dropna().unique()
            articulo_selected = st.selectbox("Selecciona Artículo", options=sorted(articulos))

            if st.button("🔍 Ver Movimientos"):

                df_e = df_entradas[
                    (df_entradas['oth_numero'].astype(str) == ot_selected) &
                    (df_entradas['gra_nombre'] == material_selected) &
                    (df_entradas['art_nombre'] == articulo_selected)
                ].copy()

                df_s = df_salidas[
                    (df_salidas['oth_numero'].astype(str) == ot_selected) &
                    (df_salidas['gra_nombre'] == material_selected) &
                    (df_salidas['art_nombre'] == articulo_selected)
                ].copy()

                df_e['enh_fecha'] = pd.to_datetime(df_e['enh_fecha'], errors='coerce')
                df_s['sah_fecha'] = pd.to_datetime(df_s['sah_fecha'], errors='coerce')

                df_e = df_e.sort_values('enh_fecha')
                df_s = df_s.sort_values('sah_fecha')

                salidas_pendientes = df_s[['sah_fecha', 'sad_cantidad', 'sad_precio_unitario']].copy()
                salidas_pendientes['consumido'] = 0

                resultados = []
                total_bodega = 0
                precio_promedio = df_s['sad_precio_unitario'].mean() if not df_s.empty else 0

                for idx, entrada in df_e.iterrows():
                    lote_fecha = entrada['enh_fecha']
                    cantidad_lote = entrada['end_cantidad']
                    restante = cantidad_lote
                    fecha_agotado = None
                    costo_total_lote = 0

                    for i, salida in salidas_pendientes.iterrows():
                        disponible_salida = salida['sad_cantidad'] - salida['consumido']
                        if disponible_salida <= 0:
                            continue

                        consumo = min(restante, disponible_salida)
                        salidas_pendientes.at[i, 'consumido'] += consumo
                        restante -= consumo
                        costo_total_lote += consumo * salida['sad_precio_unitario']

                        if restante == 0:
                            fecha_agotado = salida['sah_fecha']
                            break

                    if restante == 0 and fecha_agotado:
                        dias = (fecha_agotado - lote_fecha).days
                        estado = f"{dias} días"
                    else:
                        estado = f"Disponible {round(restante, 2)}"

                    valor_lote = 0 if restante == 0 else round(restante * precio_promedio, 2)
                    total_bodega += valor_lote

                    resultados.append({
                        'Material': material_selected,
                        'Artículo': articulo_selected,
                        'Código': entrada['art_codigo'],
                        'Fecha de entrada': lote_fecha.strftime('%Y-%m-%d') if pd.notnull(lote_fecha) else '',
                        'Cantidad del lote': cantidad_lote,
                        'Estado': estado,
                        'Costo del lote': costo_total_lote,
                        'Valor en bodega': 0 if valor_lote == 0 else valor_lote
                    })

                df_resultado = pd.DataFrame(resultados)

                entradas = df_e[['enh_fecha', 'gra_nombre', 'art_nombre', 'end_cantidad', 'enh_tipo_movim']].copy()
                entradas['Tipo'] = 'Entrada'
                salidas = df_s[['sah_fecha', 'gra_nombre', 'art_nombre', 'sad_cantidad', 'sah_tipo_movim']].copy()
                salidas.columns = ['enh_fecha', 'gra_nombre', 'art_nombre', 'end_cantidad', 'enh_tipo_movim']
                salidas['Tipo'] = 'Salida'

                movimientos = pd.concat([entradas, salidas])
                movimientos['enh_fecha'] = pd.to_datetime(movimientos['enh_fecha']).dt.strftime('%Y-%m-%d')
                movimientos = movimientos.rename(columns={
                    'enh_fecha': 'Fecha',
                    'gra_nombre': 'Material',
                    'art_nombre': 'Artículo',
                    'end_cantidad': 'Cantidad',
                    'enh_tipo_movim': 'Subtipo'
                }).sort_values('Fecha')

                st.write("📦 Análisis por Lotes:")
                st.dataframe(df_resultado)

                st.write("📈 Movimientos Detallados:")
                st.dataframe(movimientos)

                # Exportar a Excel
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_resultado.to_excel(writer, sheet_name='Lotes', index=False)
                    movimientos.to_excel(writer, sheet_name='Movimientos', index=False)
                output.seek(0)

                nombre_archivo = f"analisis_{obra_nombre.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                st.download_button(label="📥 Descargar Excel", data=output, file_name=nombre_archivo, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        else:
            st.error("❌ Los archivos no contienen las columnas requeridas. Verifica nombres como 'oth_numero', 'cco_codigo', 'art_nombre', etc.")

    except Exception as e:
        st.exception(f"Error al procesar los archivos: {e}")

else:
    st.warning("⬅️ Carga los tres archivos para continuar (salidas, entradas y obras)")
