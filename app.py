import streamlit as st
import pandas as pd
import numpy as np
import io

# Configuración de la página
st.set_page_config(
    page_title="Analizador de Datasets",
    page_icon="📊",
    layout="wide"
)

# Título principal
st.title("📊 Analizador de Datasets CSV")
st.markdown("---")

# Inicializar session state para almacenar el dataset
if 'df' not in st.session_state:
    st.session_state.df = None

# Sidebar para navegación
st.sidebar.title("🔧 Herramientas")
menu = st.sidebar.selectbox(
    "Selecciona una función:",
    ["Cargar Datos", "Exploración Básica", "Selección de Datos", "Filtrado de Datos"]
)

# SECCIÓN 1: CARGA DE DATOS
if menu == "Cargar Datos":
    st.header("📂 Carga de Archivos CSV")
    
    uploaded_file = st.file_uploader(
        "Selecciona un archivo CSV", 
        type=['csv'],
        help="Arrastra y suelta tu archivo CSV aquí"
    )
    
    if uploaded_file is not None:
        try:
            # Opciones de carga
            col1, col2 = st.columns(2)
            
            with col1:
                separator = st.selectbox("Separador:", [',', ';', '\t', '|'], index=0)
                encoding = st.selectbox("Codificación:", ['utf-8', 'latin-1', 'cp1252'], index=0)
            
            with col2:
                header_row = st.number_input("Fila de encabezados:", min_value=0, value=0)
                skip_rows = st.number_input("Filas a omitir:", min_value=0, value=0)
            
            # Cargar datos
            if st.button("🚀 Cargar Dataset"):
                try:
                    df = pd.read_csv(
                        uploaded_file, 
                        sep=separator,
                        encoding=encoding,
                        header=header_row if header_row >= 0 else None,
                        skiprows=skip_rows
                    )
                    
                    st.session_state.df = df
                    st.success(f"✅ Dataset cargado exitosamente: {df.shape[0]} filas, {df.shape[1]} columnas")
                    
                    # Vista previa
                    st.subheader("Vista Previa del Dataset")
                    st.dataframe(df.head(), use_container_width=True)
                    
                except Exception as e:
                    st.error(f"❌ Error al cargar el archivo: {str(e)}")
                    
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    else:
        st.info("👆 Por favor, sube un archivo CSV para comenzar")

# SECCIÓN 2: EXPLORACIÓN BÁSICA
elif menu == "Exploración Básica":
    st.header("🔍 Exploración Básica del Dataset")
    
    if st.session_state.df is not None:
        df = st.session_state.df
        
        # Pestañas para organizar la información
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Primeras/Últimas Filas", "📋 Información Básica", "📊 Descripción Estadística", "🏗️ Estructura"])
        
        with tab1:
            st.subheader("Visualización de Filas")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Primeras N filas:**")
                n_head = st.number_input("Número de filas (inicio):", min_value=1, max_value=len(df), value=5, key="head")
                st.dataframe(df.head(n_head), use_container_width=True)
            
            with col2:
                st.write("**Últimas N filas:**")
                n_tail = st.number_input("Número de filas (final):", min_value=1, max_value=len(df), value=5, key="tail")
                st.dataframe(df.tail(n_tail), use_container_width=True)
        
        with tab2:
            st.subheader("Información General del Dataset")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Número de Filas", df.shape[0])
                st.metric("Número de Columnas", df.shape[1])
            
            with col2:
                st.metric("Celdas Totales", df.shape[0] * df.shape[1])
                st.metric("Valores Nulos", df.isnull().sum().sum())
            
            with col3:
                memory_usage = df.memory_usage(deep=True).sum() / 1024**2
                st.metric("Uso de Memoria", f"{memory_usage:.2f} MB")
                st.metric("Duplicados", df.duplicated().sum())
            
            # Información detallada de tipos de datos
            st.subheader("Tipos de Datos por Columna")
            info_df = pd.DataFrame({
                'Columna': df.columns,
                'Tipo de Dato': df.dtypes.astype(str),
                'Valores No Nulos': df.count(),
                'Valores Nulos': df.isnull().sum(),
                '% Nulos': (df.isnull().sum() / len(df) * 100).round(2)
            })
            st.dataframe(info_df, use_container_width=True)
        
        with tab3:
            st.subheader("Descripción Estadística")
            
            # Seleccionar solo columnas numéricas para describe()
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            
            if len(numeric_columns) > 0:
                st.write("**Estadísticas para Columnas Numéricas:**")
                st.dataframe(df[numeric_columns].describe(), use_container_width=True)
            else:
                st.info("No se encontraron columnas numéricas para análisis estadístico")
            
            # Información adicional para columnas categóricas
            categorical_columns = df.select_dtypes(include=['object']).columns
            if len(categorical_columns) > 0:
                st.write("**Información para Columnas Categóricas:**")
                cat_info = []
                for col in categorical_columns:
                    cat_info.append({
                        'Columna': col,
                        'Valores Únicos': df[col].nunique(),
                        'Valor Más Frecuente': df[col].mode().iloc[0] if not df[col].mode().empty else 'N/A',
                        'Frecuencia Máxima': df[col].value_counts().iloc[0] if not df[col].empty else 0
                    })
                st.dataframe(pd.DataFrame(cat_info), use_container_width=True)
        
        with tab4:
            st.subheader("Estructura del Dataset")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Lista de Columnas:**")
                columns_df = pd.DataFrame({
                    'Índice': range(len(df.columns)),
                    'Nombre de la Columna': df.columns,
                    'Tipo': df.dtypes.astype(str)
                })
                st.dataframe(columns_df, use_container_width=True)
            
            with col2:
                st.write("**Forma del Dataset:**")
                st.write(f"**Dimensiones:** {df.shape}")
                st.write(f"**Filas:** {df.shape[0]:,}")
                st.write(f"**Columnas:** {df.shape[1]:,}")
                
                # Resumen de tipos de datos
                st.write("**Resumen de Tipos de Datos:**")
                type_counts = df.dtypes.value_counts()
                for dtype, count in type_counts.items():
                    st.write(f"- {dtype}: {count} columnas")
    
    else:
        st.warning("⚠️ Primero debes cargar un dataset en la sección 'Cargar Datos'")

# SECCIÓN 3: SELECCIÓN DE DATOS
elif menu == "Selección de Datos":
    st.header("🎯 Selección de Datos")
    
    if st.session_state.df is not None:
        df = st.session_state.df
        
        tab1, tab2 = st.tabs(["📋 Seleccionar Columnas", "🔢 Seleccionar Filas"])
        
        with tab1:
            st.subheader("Selección de Columnas")
            
            # Opción para seleccionar una columna
            st.write("**Seleccionar una columna:**")
            single_column = st.selectbox(
                "Elige una columna:",
                options=df.columns,
                key="single_col"
            )
            
            if st.button("Mostrar Columna Seleccionada"):
                st.write(f"**Columna: {single_column}**")
                col_data = df[single_column]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Primeros 10 valores:**")
                    st.write(col_data.head(10))
                
                with col2:
                    st.write("**Información de la columna:**")
                    st.write(f"- Tipo de dato: {col_data.dtype}")
                    st.write(f"- Valores únicos: {col_data.nunique()}")
                    st.write(f"- Valores nulos: {col_data.isnull().sum()}")
                    if col_data.dtype in ['int64', 'float64']:
                        st.write(f"- Promedio: {col_data.mean():.2f}")
                        st.write(f"- Mediana: {col_data.median():.2f}")
            
            st.markdown("---")
            
            # Opción para seleccionar múltiples columnas
            st.write("**Seleccionar múltiples columnas:**")
            multiple_columns = st.multiselect(
                "Elige las columnas:",
                options=df.columns,
                default=df.columns[:3].tolist(),
                key="multi_col"
            )
            
            if multiple_columns and st.button("Mostrar Columnas Seleccionadas"):
                st.write(f"**Columnas seleccionadas: {', '.join(multiple_columns)}**")
                selected_df = df[multiple_columns]
                st.dataframe(selected_df, use_container_width=True)
                
                # Información adicional
                st.write("**Información de las columnas seleccionadas:**")
                info_selected = pd.DataFrame({
                    'Columna': selected_df.columns,
                    'Tipo': selected_df.dtypes.astype(str),
                    'No Nulos': selected_df.count(),
                    'Únicos': [selected_df[col].nunique() for col in selected_df.columns]
                })
                st.dataframe(info_selected, use_container_width=True)
        
        with tab2:
            st.subheader("Selección de Filas")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Seleccionar rango de filas:**")
                start_row = st.number_input("Fila de inicio:", min_value=0, max_value=len(df)-1, value=0)
                end_row = st.number_input("Fila final:", min_value=start_row+1, max_value=len(df), value=min(10, len(df)))
                
                if st.button("Mostrar Rango de Filas"):
                    selected_rows = df.iloc[start_row:end_row]
                    st.write(f"**Filas {start_row} a {end_row-1}:**")
                    st.dataframe(selected_rows, use_container_width=True)
            
            with col2:
                st.write("**Seleccionar filas específicas:**")
                specific_rows = st.text_input(
                    "Índices de filas (separados por coma):",
                    placeholder="0,5,10,15"
                )
                
                if specific_rows and st.button("Mostrar Filas Específicas"):
                    try:
                        row_indices = [int(x.strip()) for x in specific_rows.split(',')]
                        row_indices = [i for i in row_indices if 0 <= i < len(df)]
                        
                        if row_indices:
                            selected_rows = df.iloc[row_indices]
                            st.write(f"**Filas con índices: {row_indices}**")
                            st.dataframe(selected_rows, use_container_width=True)
                        else:
                            st.error("No se encontraron índices válidos")
                    except ValueError:
                        st.error("Por favor, ingresa índices válidos separados por comas")
    
    else:
        st.warning("⚠️ Primero debes cargar un dataset en la sección 'Cargar Datos'")

# SECCIÓN 4: FILTRADO DE DATOS
elif menu == "Filtrado de Datos":
    st.header("🔍 Filtrado de Datos")
    
    if st.session_state.df is not None:
        df = st.session_state.df
        
        st.subheader("Filtrar Filas con Condiciones")
        
        # Seleccionar columna para filtrar
        filter_column = st.selectbox(
            "Selecciona la columna para filtrar:",
            options=df.columns
        )
        
        # Determinar el tipo de dato de la columna
        column_dtype = df[filter_column].dtype
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Seleccionar operador
            if column_dtype in ['int64', 'float64']:
                operators = ['>', '<', '>=', '<=', '==', '!=']
            else:
                operators = ['==', '!=', 'contiene', 'comienza con', 'termina con']
            
            operator = st.selectbox("Operador:", operators)
        
        with col2:
            # Input para el valor
            if column_dtype in ['int64', 'float64']:
                if column_dtype == 'int64':
                    filter_value = st.number_input("Valor:", value=int(df[filter_column].median()))
                else:
                    filter_value = st.number_input("Valor:", value=float(df[filter_column].median()))
            else:
                # Para strings, mostrar algunos valores únicos como referencia
                unique_values = df[filter_column].dropna().unique()[:10]
                st.write(f"Valores de ejemplo: {', '.join(map(str, unique_values))}")
                filter_value = st.text_input("Valor:")
        
        with col3:
            st.write("**Información de la columna:**")
            st.write(f"Tipo: {column_dtype}")
            st.write(f"Valores únicos: {df[filter_column].nunique()}")
            if column_dtype in ['int64', 'float64']:
                st.write(f"Min: {df[filter_column].min()}")
                st.write(f"Max: {df[filter_column].max()}")
        
        # Aplicar filtro
        if st.button("🔍 Aplicar Filtro"):
            try:
                # Aplicar el filtro según el operador
                if operator == '>':
                    filtered_df = df[df[filter_column] > filter_value]
                elif operator == '<':
                    filtered_df = df[df[filter_column] < filter_value]
                elif operator == '>=':
                    filtered_df = df[df[filter_column] >= filter_value]
                elif operator == '<=':
                    filtered_df = df[df[filter_column] <= filter_value]
                elif operator == '==':
                    filtered_df = df[df[filter_column] == filter_value]
                elif operator == '!=':
                    filtered_df = df[df[filter_column] != filter_value]
                elif operator == 'contiene':
                    filtered_df = df[df[filter_column].astype(str).str.contains(str(filter_value), na=False)]
                elif operator == 'comienza con':
                    filtered_df = df[df[filter_column].astype(str).str.startswith(str(filter_value), na=False)]
                elif operator == 'termina con':
                    filtered_df = df[df[filter_column].astype(str).str.endswith(str(filter_value), na=False)]
                
                # Mostrar resultados
                if len(filtered_df) > 0:
                    st.success(f"✅ Filtro aplicado: {len(filtered_df)} filas encontradas de {len(df)} totales")
                    
                    # Mostrar estadísticas del filtro
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Filas Originales", len(df))
                    with col2:
                        st.metric("Filas Filtradas", len(filtered_df))
                    with col3:
                        percentage = (len(filtered_df) / len(df)) * 100
                        st.metric("Porcentaje", f"{percentage:.1f}%")
                    
                    # Mostrar datos filtrados
                    st.subheader("Datos Filtrados")
                    st.dataframe(filtered_df, use_container_width=True)
                    
                    # Opción para descargar datos filtrados
                    csv_filtered = filtered_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Descargar datos filtrados (CSV)",
                        data=csv_filtered,
                        file_name=f"datos_filtrados_{filter_column}_{operator}_{filter_value}.csv",
                        mime="text/csv"
                    )
                else:
                    st.warning("⚠️ No se encontraron filas que cumplan con la condición especificada")
                    
            except Exception as e:
                st.error(f"❌ Error al aplicar el filtro: {str(e)}")
        
        # Sección de filtros múltiples
        st.markdown("---")
        st.subheader("🔗 Filtros Múltiples (Avanzado)")
        
        with st.expander("Crear múltiples condiciones"):
            st.write("Próximamente: Filtros con múltiples condiciones usando AND/OR")
            st.info("Esta funcionalidad permitirá combinar múltiples filtros para análisis más complejos")
    
    else:
        st.warning("⚠️ Primero debes cargar un dataset en la sección 'Cargar Datos'")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>🚀 Aplicación de Análisis de Datasets | Construida con Streamlit, Pandas y NumPy</p>
    </div>
    """, 
    unsafe_allow_html=True
)