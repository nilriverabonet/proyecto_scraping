import sys
import subprocess
from pathlib import Path
import pandas as pd
import streamlit as st

# Si el usuario ejecuta "python app.py" o pulsa el botón Play (▶) de VS Code,
# lanzamos automáticamente "streamlit run app.py" sin mostrar ningún error ni warning.
if not st.runtime.exists():
    ruta_app = str(Path(__file__).resolve())
    sys.exit(subprocess.call([sys.executable, "-m", "streamlit", "run", ruta_app]))

# Configuración básica de la página de Streamlit
st.set_page_config(
    page_title="Dashboard Tienda Pokémon - ScrapeMe",
    page_icon="⚡",
    layout="wide"
)

ARCHIVO_CSV = Path(__file__).resolve().parent / "pokemons.csv"


@st.cache_data
def cargar_datos():
    """
    Lee el archivo CSV generado por scraper.py utilizando Pandas.
    Usamos @st.cache_data para no recargar el archivo del disco en cada clic.
    """
    if not ARCHIVO_CSV.exists():
        return None
    return pd.read_csv(ARCHIVO_CSV)


# --- TÍTULO Y DESCRIPCIÓN ---
st.title("⚡ Dashboard de Análisis: Tienda Pokémon (ScrapeMe)")
st.markdown(
    "Aplicación interactiva creada con **Streamlit** y **Pandas** para explorar, filtrar "
    "y analizar los datos extraídos mediante **Web Scraping con BeautifulSoup** desde `scrapeme.live/shop/`."
)

df = cargar_datos()

if df is None or df.empty:
    st.error("⚠️ No se encontró el archivo `pokemons.csv`. Ejecuta primero `python scraper.py` para extraer los datos.")
    st.stop()

# --- BARRA LATERAL: FILTROS INTERACTIVOS ---
st.sidebar.header("🔍 Filtros de Búsqueda")

# 1. Filtro por texto (nombre del Pokémon)
busqueda_nombre = st.sidebar.text_input("Buscar Pokémon por nombre:", "")

# 2. Filtro por Categoría
todas_categorias = sorted(df["categoria"].dropna().unique().tolist())
categorias_seleccionadas = st.sidebar.multiselect(
    "Categoría / Tipo:",
    options=todas_categorias,
    default=todas_categorias
)

# 3. Filtro por Rango de Precio (£)
precio_min = float(df["precio_gbp"].min())
precio_max = float(df["precio_gbp"].max())
rango_precio = st.sidebar.slider(
    "Rango de Precio (£):",
    min_value=precio_min,
    max_value=precio_max,
    value=(precio_min, precio_max)
)

# 4. Filtro por Rango de Stock (Existencias)
stock_min = int(df["stock"].min())
stock_max = int(df["stock"].max())
rango_stock = st.sidebar.slider(
    "Rango de Existencias (Stock):",
    min_value=stock_min,
    max_value=stock_max,
    value=(stock_min, stock_max)
)

# --- APLICACIÓN DE FILTROS CON PANDAS ---
df_filtrado = df[
    (df["categoria"].isin(categorias_seleccionadas)) &
    (df["precio_gbp"] >= rango_precio[0]) &
    (df["precio_gbp"] <= rango_precio[1]) &
    (df["stock"] >= rango_stock[0]) &
    (df["stock"] <= rango_stock[1])
].copy()

if busqueda_nombre:
    df_filtrado = df_filtrado[
        df_filtrado["nombre"].str.contains(busqueda_nombre, case=False, na=False)
    ]

# --- MÉTRICAS RESUMEN (KPIs) ---
st.subheader("📊 Resumen de los Datos Filtrados")
col1, col2, col3, col4 = st.columns(4)

if not df_filtrado.empty:
    col1.metric("Pokémon Encontrados", len(df_filtrado))
    col2.metric("Precio Medio", f"£{df_filtrado['precio_gbp'].mean():.2f}")
    col3.metric("Stock Total Disponible", f"{int(df_filtrado['stock'].sum())} uds.")
    col4.metric("Peso Medio", f"{df_filtrado['peso_kg'].mean():.1f} kg")
else:
    st.warning("No hay ningún Pokémon que coincida con los filtros seleccionados.")
    st.stop()

st.divider()

# --- TABLA INTERACTIVA DE RESULTADOS ---
st.subheader("📋 Catálogo Interactivo de Pokémon")
st.caption("Puedes ordenar cualquier columna haciendo clic sobre su encabezado.")

st.dataframe(
    df_filtrado[["imagen_url", "sku", "nombre", "categoria", "precio_gbp", "stock", "peso_kg", "descripcion"]],
    column_config={
        "imagen_url": st.column_config.ImageColumn("Imagen", width="small"),
        "sku": "SKU",
        "nombre": "Nombre",
        "categoria": "Categoría",
        "precio_gbp": st.column_config.NumberColumn("Precio (£)", format="£%.2f"),
        "stock": st.column_config.NumberColumn("Stock (uds.)"),
        "peso_kg": st.column_config.NumberColumn("Peso (kg)", format="%.1f kg"),
        "descripcion": "Descripción"
    },
    hide_index=True,
    width="stretch"
)

st.divider()

# --- VISUALIZACIÓN GRÁFICA Y ANÁLISIS CRÍTICO ---
st.subheader("📈 Análisis Visual y Preguntas de Negocio")

col_graf1, col_graf2 = st.columns(2)

# Gráfico 1: Comparativa de precios por Pokémon
with col_graf1:
    st.markdown("#### 1. ¿Cuáles son los Pokémon más caros de la selección?")
    df_top_precios = df_filtrado.sort_values(by="precio_gbp", ascending=False).head(15)
    st.bar_chart(df_top_precios.set_index("nombre")["precio_gbp"], color="#FF4B4B")

    poke_mas_caro = df_filtrado.loc[df_filtrado["precio_gbp"].idxmax()]
    poke_mas_barato = df_filtrado.loc[df_filtrado["precio_gbp"].idxmin()]
    st.info(
        f"**Conclusión:** Dentro del filtro actual, el Pokémon más caro es **{poke_mas_caro['nombre']}** "
        f"(£{poke_mas_caro['precio_gbp']:.2f}) y el más económico es **{poke_mas_barato['nombre']}** "
        f"(£{poke_mas_barato['precio_gbp']:.2f})."
    )

# Gráfico 2: Precio promedio por Categoría
with col_graf2:
    st.markdown("#### 2. ¿Qué categoría de Pokémon tiene mayor precio medio?")
    precio_por_categoria = (
        df_filtrado.groupby("categoria")["precio_gbp"]
        .mean()
        .round(2)
        .sort_values(ascending=False)
    )
    st.bar_chart(precio_por_categoria, color="#1C83E1")

    cat_cara = precio_por_categoria.index[0]
    valor_cat_cara = precio_por_categoria.iloc[0]
    st.info(
        f"**Conclusión:** La categoría **{cat_cara}** lidera el precio promedio con **£{valor_cat_cara:.2f}**, "
        "lo que indica que los Pokémon de este tipo se cotizan más alto en la tienda."
    )

st.divider()

# Gráfico 3: Relación entre Stock / Peso y Precio (Análisis de correlación)
col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    st.markdown("#### 3. ¿Influye la escasez de stock en el precio del Pokémon?")
    st.scatter_chart(df_filtrado, x="stock", y="precio_gbp", color="#00C07F")

    corr_stock_precio = df_filtrado["stock"].corr(df_filtrado["precio_gbp"])
    if pd.isna(corr_stock_precio):
        texto_corr_stock = "No hay suficientes datos para calcular la correlación."
    elif abs(corr_stock_precio) < 0.25:
        texto_corr_stock = (
            f"La correlación entre stock y precio es débil (**{corr_stock_precio:.2f}**). "
            "Esto demuestra que la tienda fija los precios de forma independiente a las unidades restantes en almacén."
        )
    elif corr_stock_precio < 0:
        texto_corr_stock = (
            f"Existe una correlación negativa (**{corr_stock_precio:.2f}**): "
            "los Pokémon con menos unidades en stock tienden a tener un precio más elevado."
        )
    else:
        texto_corr_stock = (
            f"Existe una correlación positiva (**{corr_stock_precio:.2f}**): "
            "los Pokémon con mayor stock también presentan precios altos."
        )
    st.info(f"**Interpretación:** {texto_corr_stock}")

with col_graf4:
    st.markdown("#### 4. ¿Los Pokémon más pesados (evolucionados) son más caros?")
    st.scatter_chart(df_filtrado, x="peso_kg", y="precio_gbp", color="#FFA500")

    corr_peso_precio = df_filtrado["peso_kg"].corr(df_filtrado["precio_gbp"])
    if pd.isna(corr_peso_precio):
        texto_corr_peso = "No hay suficientes datos para calcular la correlación."
    elif abs(corr_peso_precio) < 0.25:
        texto_corr_peso = (
            f"La correlación entre peso y precio es baja (**{corr_peso_precio:.2f}**). "
            "El tamaño físico del Pokémon no determina directamente su coste en la tienda."
        )
    else:
        texto_corr_peso = (
            f"Se observa una correlación de **{corr_peso_precio:.2f}** entre el peso en kg y el precio en libras."
        )
    st.info(f"**Interpretación:** {texto_corr_peso}")
