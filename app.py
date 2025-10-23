import streamlit as st
import pandas as pd 
import numpy as np
import plotly.express as px
import re 
import plotly.graph_objects as go

# CONFIGURACIÓN INICIAL Y TÍTULO

st.set_page_config(
    page_title="Análisis Calidad-Precio Vehículos 2025", 
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🚗" 
)

# Título principal 
st.title("🚗 Análisis Comparativo de la Relación Calidad-Precio en Vehículos 🚀")
st.markdown("---") 
st.markdown("Por **Angel Pastrano** y **Valeria Barreto** | Mercado Global 2025")


st.sidebar.title("🛠️ Navegación")
opciones_menu = {
    "Introducción": "📚 Introducción",
    "Top 10 Modelos": "🥇 Top 10 Modelos",
    "Comparativa por Marcas": "🏭 Comparativa por Marcas",
    "Análisis por Combustible": "⛽ Análisis por Combustible",
    "Conclusiones": "📝 Conclusiones"
}

opcion_seleccionada = st.sidebar.radio(
    "Selecciona una sección:", 
    list(opciones_menu.keys()),
    format_func=lambda x: opciones_menu[x] 
)
st.sidebar.markdown("---") 


# CARGA DE DATOS 

try:
    
    data_carros = pd.read_csv('Cars Datasets 2025.csv', encoding='latin-1') 
    
except FileNotFoundError:
    st.error("❌ Error: Archivo 'Cars Datasets 2025.csv' no encontrado. Asegúrate de que el archivo esté en la misma carpeta.")
    data_carros = pd.DataFrame()
    
if not data_carros.empty:

    # Funciones de Limpieza 
    def clean_and_avg_price(price_str):
        if pd.isna(price_str):
            return np.nan
        price_clean = re.sub(r'[$, ]|approx', '', str(price_str))
        if "-" in price_clean:
            prices = [float(p) for p in price_clean.split('-') if p]
            return np.mean(prices) if prices else np.nan
        try:
            return float(price_clean)
        except ValueError:
            return np.nan

    def extract_first_number(text):
        if pd.isna(text):
            return np.nan
        match = re.search(r'^\d+\.?\d*', str(text))
        return float(match.group(0)) if match else np.nan

    # Aplicar las funciones de limpieza 
    data_qpr = data_carros.copy()
    
    try:
        data_qpr['Price_Avg'] = data_qpr['Cars Prices'].apply(clean_and_avg_price) 
        data_qpr['HP_Clean'] = data_qpr['HorsePower'].apply(extract_first_number) 
        data_qpr['Speed_Clean'] = data_qpr['Total Speed'].apply(extract_first_number) 
        data_qpr['Accel_Clean'] = data_qpr['Performance(0 - 100 )KM/H'].apply(extract_first_number) 
        
    except KeyError as e:
        st.error(f"❌ Error de columna: {e}. Por favor, verifique el nombre de la columna en su archivo CSV. Nombres de columnas disponibles: {data_carros.columns.tolist()}")
        data_carros = pd.DataFrame() 
        
if not data_carros.empty:
    
    # Filtrar datos válidos
    data_qpr = data_qpr.dropna(subset=['Price_Avg', 'HP_Clean', 'Speed_Clean', 'Accel_Clean'])
    data_qpr = data_qpr[data_qpr['Price_Avg'] > 0]
    
    # Cálculo del Índice de Calidad y QPR
    data_qpr['Quality_Index'] = data_qpr['HP_Clean'] + data_qpr['Speed_Clean'] - (10 * data_qpr['Accel_Clean'])
    data_qpr['QPR'] = (data_qpr['Quality_Index'] / data_qpr['Price_Avg']) * 1000

    
    # Clasificación de Motorización
    data_qpr['Motorizacion'] = data_qpr['Fuel Types'].apply(lambda x: 
                                                             "Fósil" if x in ["Petrol", "Diesel"] else
                                                             "Híbrido" if x in ["Hybrid", "plug in hyrbrid"] else
                                                             "Eléctrico" if x == "Electric" else "Otro/No Clasificado") 



if opcion_seleccionada == "Introducción":
    
    st.header("📚 Introducción")
    st.markdown("""
    En el mercado automotriz de hoy, tomar una buena decisión de compra no se trata solo de ver qué coche tiene el precio más bajo, ni tampoco el que tiene más caballos. Se trata de encontrar el punto perfecto entre el precio y lo que el coche realmente ofrece. ¿Estamos pagando por el valor real o solo por el nombre de la marca?
    
    Este estudio se centra en responder esa pregunta usando una métrica clave: la **Relación Calidad-Precio (QPR)**. El QPR no es más que una forma de medir, de manera justa y objetiva, cuántos puntos de rendimiento técnico (potencia, velocidad, eficiencia, etc.) recibes por cada unidad de dinero invertida.
    
    ---
    
    ### 📊 Métricas Clave del Dataset
    """)
    
    total_carros = data_qpr.shape[0]
    precio_promedio = data_qpr['Price_Avg'].mean()
    qpr_max = data_qpr['QPR'].max()
    
    col1, col2, col3 = st.columns(3)
    
    col1.metric("Total Modelos Analizados", f"{total_carros} 🏎️")
    col2.metric("Precio Promedio", f"${precio_promedio:,.0f} 💲")
    col3.metric("QPR Máximo (Mejor Valor)", f"{qpr_max:.2f} Pts/1k USD ⭐")
    
elif opcion_seleccionada == "Top 10 Modelos" and not data_carros.empty:
    st.header("🥇 Top 10 Mejores Carros Calidad/Precio")
    
    top_10_qpr = data_qpr.sort_values('QPR', ascending=False).head(10)[
        ['Company Names', 'Cars Names', 'Motorizacion', 'Price_Avg', 'Quality_Index', 'QPR']
    ].copy() 
    
    # Renombrar columnas para la tabla
    top_10_qpr.columns = [
        "Fabricante", 
        "Modelo", 
        "Motorización", 
        "Precio Promedio (USD)", 
        "Índice de Calidad", 
        "Relación QPR (Puntos/1k USD)"
    ]
    
    st.dataframe(
        top_10_qpr, 
        column_config={
            "Precio Promedio (USD)": st.column_config.NumberColumn(
                "Precio Promedio (USD)", format="$%d"
            ),
            "Relación QPR (Puntos/1k USD)": st.column_config.ProgressColumn(
                "Relación QPR (Puntos/1k USD)",
                format="%.2f",
                min_value=0,
                max_value=top_10_qpr['Relación QPR (Puntos/1k USD)'].max(),
            ),
        },
        hide_index=True, 
        use_container_width=True
    )
    
    fig = px.bar(top_10_qpr.sort_values('Relación QPR (Puntos/1k USD)'), 
                 x='Relación QPR (Puntos/1k USD)', 
                 y='Modelo', 
                 orientation='h', 
                 color='Motorización',
                 
                 template='plotly_dark', 
                 color_discrete_map={
                     "Fósil": "#FC8D59",
                     "Híbrido": "#99D594",
                     "Eléctrico": "#3288BD",
                     "Otro/No Clasificado": "#FEE08B"
                 },
                 title="📈 Top 10: Relación Calidad-Precio (QPR)")
    st.plotly_chart(fig, use_container_width=True)

elif opcion_seleccionada == "Comparativa por Marcas" and not data_carros.empty:
    st.header("🏭 Comparativa por Marcas")
    
    # Código Comparativa por Marcas
    brand_qpr = data_qpr.groupby('Company Names').agg(
        Modelos=('QPR', 'size'), 
        QPR_Promedio=('QPR', 'mean'), 
        Precio_Promedio_USD=('Price_Avg', 'mean')
    )
    brand_qpr = brand_qpr[brand_qpr['Modelos'] >= 2].sort_values('QPR_Promedio', ascending=False).head(10)
    brand_qpr = brand_qpr.reset_index().rename(columns={'Company Names': 'Fabricante'}) 
    
    # Personalizar la presentación de la tabla
    st.dataframe(
        brand_qpr.set_index('Fabricante'),
        column_config={
            "QPR_Promedio": st.column_config.ProgressColumn(
                "QPR Promedio (Pts/1k USD)",
                format="%.2f",
                min_value=brand_qpr['QPR_Promedio'].min(),
                max_value=brand_qpr['QPR_Promedio'].max(),
            ),
            "Precio_Promedio_USD": st.column_config.NumberColumn(
                "Precio Promedio (USD)", format="$%d"
            ),
        },
        use_container_width=True
    )
    
    # Gráfico Comparativa por Marcas
    fig = px.bar(brand_qpr.sort_values('QPR_Promedio'), 
                 x='QPR_Promedio', 
                 y='Fabricante', 
                 orientation='h',
                 template='plotly_dark',
                 color_discrete_sequence=px.colors.sequential.Sunsetdark,
                 title="📊 Top 10 Marcas por QPR Promedio")
    st.plotly_chart(fig, use_container_width=True)

elif opcion_seleccionada == "Análisis por Combustible" and not data_carros.empty:
    st.header("⛽ Análisis por Combustible")
    
    # Código Análisis por Combustible
    fuel_qpr = data_qpr.groupby('Motorizacion').agg(
        Modelos=('QPR', 'size'), 
        QPR_Promedio=('QPR', 'mean'),
        Precio_Promedio=('Price_Avg', 'mean')
    ).sort_values('QPR_Promedio', ascending=False)
    
    # Presentar una tabla con estilos
    st.dataframe(
        fuel_qpr,
        column_config={
            "QPR_Promedio": st.column_config.ProgressColumn(
                "QPR Promedio (Pts/1k USD)",
                format="%.2f",
                min_value=fuel_qpr['QPR_Promedio'].min(),
                max_value=fuel_qpr['QPR_Promedio'].max(),
            ),
             "Precio_Promedio": st.column_config.NumberColumn(
                "Precio Promedio (USD)", format="$%d"
            ),
        },
        use_container_width=True
    )
    
    # Gráfico Análisis por Combustible 
    fig_radar = go.Figure()
    
    # Normalizar los datos para el radar (escala 0 a 1)
    df_radar = fuel_qpr.reset_index().set_index('Motorizacion')
    df_radar_norm = (df_radar - df_radar.min()) / (df_radar.max() - df_radar.min())
    
    categorias = ['QPR_Promedio', 'Precio_Promedio', 'Modelos']
    
    for motor in df_radar_norm.index:
        fig_radar.add_trace(go.Scatterpolar(
            r=df_radar_norm.loc[motor, categorias].values.tolist(),
            theta=categorias,
            fill='toself',
            name=motor
        ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1.05]
            )),
        title="Impacto Relativo de la Motorización (Normalizado)",
        template='plotly_dark',
        showlegend=True
    )
    
    st.plotly_chart(fig_radar, use_container_width=True)
    
elif opcion_seleccionada == "Conclusiones":
    # contenido de Conclusiones
    st.header("📝 Conclusiones y Recomendaciones")
    st.markdown("""
    [El Ganador del Valor QRP
    Vimos claramente que tener el QPR más alto no es cosa de marcas de lujo. Los modelos que ganan son los que te dan más caballos, velocidad y calidad por cada euro/dólar que pagas. Esto prueba que el valor está en la ingeniería inteligente, no solo en el precio.
    
    **La Marca Estándar es la Jefa:**
    Las marcas que ganan en el QPR Promedio (las más consistentes) son las que tienen su proceso de producción súper optimizado. Saben meter buen equipamiento sin que el precio se dispare.
    
    **El Balance de la Motorización:**
    La tecnología de motorización que se llevó el mejor QPR promedio **(e.g., Híbrido)** ha encontrado el punto perfecto. Son lo suficientemente nuevas para ser eficientes, pero sus precios ya no están por las nubes.
    
    **No Pagues Demás:**
    Si quieres el mejor valor, ignora la publicidad y mira la tabla del Top 10 de QPR. Esos modelos son los que te van a dar el mejor coche por tu dinero.
    
    **Revisa la Tecnología:**
    Si vas a cambiar a un coche [ej: Híbrido o Eléctrico], compara su QPR con los de gasolina. Asegúrate de que estás pagando por beneficios reales y no solo por la moda. La tecnología ganadora es la que, en promedio, te da el mejor rendimiento.]
    """)    