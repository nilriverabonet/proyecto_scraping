# Práctica de Web Scraping con BeautifulSoup, Pandas y Streamlit (Tienda Pokémon - ScrapeMe)

Proyecto de extracción, limpieza y visualización interactiva de datos realizado sobre la web de pruebas **[ScrapeMe - Pokémon Shop](https://scrapeme.live/shop/)**.

---

## 📋 Descripción del Proyecto

El proyecto se divide en dos partes principales siguiendo el enunciado de la práctica:

1. **Parte 1 (`scraper.py`) — Web Scraping y Almacenamiento en CSV:**
   - Comprueba automáticamente el archivo `robots.txt` del servidor antes de iniciar.
   - Realiza peticiones HTTP identificándose mediante cabecera `User-Agent` y aplicando pausas (`time.sleep`) para respetar el servidor (*rate limiting*).
   - Recorre la paginación del catálogo y entra en la ficha de cada Pokémon con **BeautifulSoup** para extraer datos de distintos tipos:
     - **Texto:** Nombre, categoría/tipo, descripción, URL de la imagen y enlace de la ficha.
     - **Numéricos limpiados en Python:** SKU (`int`), Precio en libras `£` (`float`), Existencias/Stock (`int`) y Peso en `kg` (`float`).
   - Almacena el conjunto de datos limpio en `pokemons.csv` utilizando **Pandas**.

2. **Parte 2 (`app.py`) — Análisis y Dashboard Interactivo con Streamlit:**
   - Carga `pokemons.csv` mediante **Pandas**.
   - Incluye filtros interactivos en la barra lateral: búsqueda por nombre, selector múltiple de categorías, rango de precios (`£`) y rango de existencias (`stock`).
   - Muestra indicadores clave (KPIs), tabla interactiva con vista previa de la imagen de cada Pokémon y **4 gráficos con interpretación y análisis crítico** (comparativa de precios, precio medio por categoría y correlación entre stock/peso y precio).

---

## 🚀 Instalación y Ejecución

1. **Instalar dependencias** (si no usas el entorno virtual `.venv` ya configurado):

```bash
pip install -r requirements.txt
```

2. **Paso 1 — Ejecutar el Web Scraping** (genera el archivo `pokemons.csv`):

```bash
.\.venv\bin\python.exe scraper.py
```

3. **Paso 2 — Iniciar el Dashboard en Streamlit**:

```bash
.\.venv\bin\python.exe -m streamlit run app.py
```

---

## 📁 Estructura del Proyecto

```text
proyecto scraping/
├── scraper.py                 # Parte 1: Script de Web Scraping con BeautifulSoup y Pandas
├── pokemons.csv               # Datos extraídos y limpios (generado por scraper.py)
├── app.py                     # Parte 2: Dashboard interactivo de análisis con Streamlit
├── explicacion_proyecto.txt   # Guía explicativa paso a paso + preguntas de defensa en clase
├── requirements.txt           # Librerías necesarias del proyecto
├── .gitignore                 # Archivos excluidos de Git (.venv, __pycache__)
└── README.md                  # Documentación principal para GitHub
```
