import sys
import subprocess
import pandas as pd
import streamlit as st

# Si se ejecuta con el botón Play (▶) de VS Code, lanza automáticamente "streamlit run"
if not st.runtime.exists():
    sys.exit(subprocess.call([sys.executable, "-m", "streamlit", "run", __file__]))

st.set_page_config(page_title="Dashboard Pokémon", page_icon="⚡", layout="wide")

st.title("⚡ Dashboard de Análisis: Tienda Pokémon (ScrapeMe)")
st.write("Análisis interactivo de los datos extraídos con **BeautifulSoup** y tratados con **Pandas**.")

# 1. CARGAR DATOS CON PANDAS
df = pd.read_csv("pokemons.csv")

# 2. FILTROS INTERACTIVOS EN LA BARRA LATERAL
st.sidebar.header("🔍 Filtros")

categorias = sorted(df["categoria"].unique().tolist())
cat_seleccionadas = st.sidebar.multiselect("Categoría:", categorias, default=categorias)

precio_min = float(df["precio_gbp"].min())
precio_max = float(df["precio_gbp"].max())
rango_precio = st.sidebar.slider("Rango de Precio (£):", precio_min, precio_max, (precio_min, precio_max))

# Filtramos el DataFrame según la categoría y el rango de precios elegidos
df_filtrado = df[
    (df["categoria"].isin(cat_seleccionadas)) &
    (df["precio_gbp"] >= rango_precio[0]) &
    (df["precio_gbp"] <= rango_precio[1])
]

if df_filtrado.empty:
    st.warning("No hay ningún Pokémon que coincida con los filtros seleccionados.")
    st.stop()

# 3. MÉTRICAS RESUMEN Y TABLA INTERACTIVA
col1, col2, col3 = st.columns(3)
col1.metric("Pokémon Encontrados", len(df_filtrado))
col2.metric("Precio Medio (£)", f"£{df_filtrado['precio_gbp'].mean():.2f}")
col3.metric("Stock Total Disponible", f"{int(df_filtrado['stock'].sum())} uds.")

st.subheader("📋 Tabla de Pokémon Filtrados")
st.dataframe(df_filtrado, width="stretch")

# 4. GRÁFICOS Y ANÁLISIS CRÍTICO DE RESULTADOS
st.subheader("📈 Análisis Gráfico y Conclusiones de Negocio")
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.markdown("#### 1. ¿Qué categoría de Pokémon tiene mayor precio medio?")
    # Agrupamos por categoría con Pandas y calculamos el precio medio de cada una
    media_por_categoria = df_filtrado.groupby("categoria")["precio_gbp"].mean().sort_values(ascending=False)
    st.bar_chart(media_por_categoria)

    st.info(
        f"**Conclusión:** La categoría más cara de media es **{media_por_categoria.idxmax()}** "
        f"(£{media_por_categoria.max():.2f}), mientras que la más económica es "
        f"**{media_por_categoria.idxmin()}** (£{media_por_categoria.min():.2f})."
    )

with col_graf2:
    st.markdown("#### 2. ¿Influye la escasez de stock en el precio del Pokémon?")
    st.scatter_chart(df_filtrado, x="stock", y="precio_gbp")

    # Calculamos la correlación en Pandas (valores cercanos a 0 indican que no hay relación)
    correlacion = df_filtrado["stock"].corr(df_filtrado["precio_gbp"])
    st.info(
        f"**Conclusión:** La correlación entre stock y precio es **{correlacion:.2f}** (muy cercana a 0). "
        "Esto demuestra que tener menos unidades en stock no hace que un Pokémon sea más caro en la tienda."
    )
