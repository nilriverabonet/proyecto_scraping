import time
import urllib3
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Desactivamos avisos de certificado SSL en la consola
urllib3.disable_warnings()

# 1. ÉTICA Y LEGALIDAD: Definimos User-Agent para identificarnos ante el servidor
HEADERS = {"User-Agent": "Mozilla/5.0 (PracticaScrapingDAM)"}
sesion = requests.Session()
sesion.headers.update(HEADERS)
sesion.verify = False

# Comprobamos robots.txt antes de hacer scraping para verificar que /shop/ está permitido
robots = sesion.get("https://scrapeme.live/robots.txt")
print("1. Comprobando robots.txt:")
print(robots.text.strip())

lista_pokemons = []

# 2. EXTRACCIÓN CON BEAUTIFULSOUP: Recorremos las 2 primeras páginas (32 Pokémon)
for pagina in range(1, 3):
    url = f"https://scrapeme.live/shop/page/{pagina}/"
    print(f"\n2. Extrayendo página {pagina}: {url}")

    respuesta = sesion.get(url)
    soup = BeautifulSoup(respuesta.text, "html.parser")

    # Usamos find_all("li", class_="product") porque en esta tienda WooCommerce
    # cada tarjeta de Pokémon está dentro de una etiqueta <li> con la clase "product".
    productos = soup.find_all("li", class_="product")

    for prod in productos:
        # Extraemos nombre, precio y enlace de la tarjeta principal
        nombre = prod.find("h2", class_="woocommerce-loop-product__title").text
        texto_precio = prod.find("span", class_="price").text
        enlace = prod.find("a")["href"].replace("../", "")
        url_ficha = "https://scrapeme.live/shop/" + enlace

        # Pausa ética (rate limiting) para no saturar el servidor con peticiones seguidas
        time.sleep(0.2)

        # Entramos en la ficha del Pokémon para extraer stock, peso, categoría y descripción
        resp_ficha = sesion.get(url_ficha)
        soup_ficha = BeautifulSoup(resp_ficha.text, "html.parser")

        descripcion = soup_ficha.find("div", class_="woocommerce-product-details__short-description").text.strip()
        texto_stock = soup_ficha.find("p", class_="stock").text
        texto_peso = soup_ficha.find("td", class_="woocommerce-product-attributes-item__value").text

        # En categorías aparecen ['Pokemon', 'Seed']; cogemos la última [-1] porque
        # 'Pokemon' es común a todos y la segunda es el tipo real de cada uno.
        enlaces_cat = soup_ficha.find("span", class_="posted_in").find_all("a")
        categoria = enlaces_cat[-1].text

        # 3. LIMPIEZA DE DATOS EN PYTHON:
        # Quitamos símbolos ('£', ' in stock', ' kg') y convertimos texto a número (float / int)
        # para poder hacer cálculos matemáticos y filtros numéricos en Pandas y Streamlit.
        precio = float(texto_precio.replace("£", ""))
        stock = int(texto_stock.replace(" in stock", ""))
        peso = float(texto_peso.replace(" kg", ""))

        lista_pokemons.append({
            "nombre": nombre,
            "categoria": categoria,
            "precio_gbp": precio,
            "stock": stock,
            "peso_kg": peso,
            "descripcion": descripcion
        })

# 4. GUARDAR EN CSV CON PANDAS
df = pd.DataFrame(lista_pokemons)
df.to_csv("pokemons.csv", index=False, encoding="utf-8")
print(f"\n3. ¡Completado! Se han guardado {len(df)} Pokémon limpios en 'pokemons.csv'.")
