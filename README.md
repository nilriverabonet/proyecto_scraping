# Práctica de Web Scraping con BeautifulSoup, Pandas y Streamlit (Tienda Pokémon - ScrapeMe)

Proyecto de extracción, limpieza y visualización interactiva de datos realizado sobre la web de pruebas **[ScrapeMe - Pokémon Shop](https://scrapeme.live/shop/)**.

---

## 📋 Descripción del Proyecto

El proyecto se divide en dos partes principales siguiendo el enunciado de la práctica:

1. **Parte 1 (`scraper.py`) — Web Scraping y Almacenamiento en CSV:**
   - Comprueba automáticamente el archivo `robots.txt` del servidor antes de iniciar.
   - Realiza peticiones HTTP identificándose mediante cabecera `User-Agent` y aplicando pausas (`time.sleep`) para respetar el servidor (*rate limiting*).
   - Recorre la paginación del catálogo y entra en la ficha de cada Pokémon con **BeautifulSoup** para extraer y limpiar datos de distintos tipos:
     - **Texto:** Nombre, categoría/tipo y descripción.
     - **Numéricos limpiados en Python:** Precio en libras `£` (`float`), Existencias/Stock (`int`) y Peso en `kg` (`float`).
   - Almacena el conjunto de datos limpio en `pokemons.csv` utilizando **Pandas**.

2. **Parte 2 (`app.py`) — Análisis y Dashboard Interactivo con Streamlit:**
   - Carga `pokemons.csv` mediante **Pandas**.
   - Incluye filtros interactivos en la barra lateral por categoría/tipo y por rango de precios (`£`).
   - Muestra indicadores clave (KPIs), tabla interactiva de resultados filtrados y **2 gráficos con interpretación y análisis crítico** (precio medio por categoría con `groupby` y correlación entre stock y precio con `.corr()`).

---

## 🚀 Instalación y Ejecución

```powershell
# 1. Crear y activar el entorno virtual (si se clona desde cero)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Parte 1: Ejecutar el Web Scraping (genera pokemons.csv)
python scraper.py

# 4. Parte 2: Iniciar el Dashboard en Streamlit
streamlit run app.py
```

---

## 📁 Estructura del Proyecto

```text
proyecto scraping/
├── scraper.py                 # Parte 1: Script de Web Scraping con BeautifulSoup y Pandas
├── pokemons.csv               # Datos extraídos y limpios (generado por scraper.py)
├── app.py                     # Parte 2: Dashboard interactivo de análisis con Streamlit
├── explicacion_proyecto.txt   # Guía explicativa paso a paso + preguntas de defensa en clase
├── iniciar.txt                # Chuleta rápida de comandos para iniciar el proyecto
├── requirements.txt           # Librerías necesarias del proyecto
├── .gitignore                 # Archivos excluidos de Git (.venv, .vscode, __pycache__)
└── README.md                  # Documentación principal para GitHub
```
