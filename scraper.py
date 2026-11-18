import time
import re
from urllib.parse import urljoin
import urllib3
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Desactivamos avisos de certificado SSL por si el entorno escolar/local intercepta HTTPS
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# URL base de la tienda de Pokémon recomendada en el enunciado (ScrapeMe)
BASE_URL = "https://scrapeme.live/shop/"
ROBOTS_URL = "https://scrapeme.live/robots.txt"

# DEFINICIÓN DE USER-AGENT (Ética y buenas prácticas):
# Identificamos nuestro script ante el servidor para no hacer peticiones anónimas
# y evitar bloqueos por parecer un bot malicioso.
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) PracticaScrapingDAM/1.0"
}


def comprobar_robots_txt():
    """
    Revisa el archivo robots.txt del sitio web antes de hacer scraping.
    Cumple con el criterio de ética y legalidad para verificar que '/shop/' no está prohibido.
    """
    print("1. Comprobando archivo robots.txt en:", ROBOTS_URL)
    try:
        respuesta = requests.get(ROBOTS_URL, headers=HEADERS, timeout=10, verify=False)
        if respuesta.status_code == 200:
            print("   -> robots.txt accesible.Contenido:")
            for linea in respuesta.text.strip().splitlines():
                print(f"      {linea}")
            # Verificamos que no exista un 'Disallow: /shop/'
            if "Disallow: /shop" in respuesta.text:
                print("   [AVISO] El robots.txt restringe /shop/.")
                return False
            print("   -> Verificación correcta: el scraping en /shop/ está permitido.\n")
        else:
            print(f"   -> No se encontró restricción en robots.txt (Código {respuesta.status_code}).\n")
        return True
    except Exception as e:
        print(f"   -> No se pudo leer robots.txt ({e}), continuando con precaución.\n")
        return True


def limpiar_precio(texto_precio):
    """
    Convierte un texto como '£63.00' en un número decimal (float) 63.0.
    Justificación: Guardar números reales en el CSV permite filtrar por rangos y
    calcular medias en Pandas/Streamlit sin errores de texto.
    """
    texto_limpio = re.sub(r"[^0-9.]", "", texto_precio)
    return float(texto_limpio) if texto_limpio else 0.0


def limpiar_entero(texto):
    """
    Extrae el número entero de textos como '45 in stock' -> 45.
    """
    coincidencia = re.search(r"\d+", texto)
    return int(coincidencia.group()) if coincidencia else 0


def limpiar_peso(texto_peso):
    """
    Convierte un texto como '15.2 kg' en un número decimal (float) 15.2.
    """
    texto_limpio = re.sub(r"[^0-9.]", "", texto_peso)
    return float(texto_limpio) if texto_limpio else 0.0


def extraer_detalle_pokemon(url_ficha):
    """
    Entra en la ficha individual de cada Pokémon para extraer:
    descripción, existencias (stock), categoría, peso (kg) y SKU.
    """
    try:
        respuesta = requests.get(url_ficha, headers=HEADERS, timeout=10, verify=False)
        if respuesta.status_code != 200:
            return None

        soup = BeautifulSoup(respuesta.text, "html.parser")

        # Descripción corta: usamos el selector de clase específica de WooCommerce
        # porque el contenedor general tiene varios párrafos que podrían mezclarse.
        div_desc = soup.select_one("div.woocommerce-product-details__short-description")
        descripcion = div_desc.get_text(strip=True) if div_desc else "Sin descripción"

        # Existencias (Stock): p.stock contiene textos tipo '45 in stock'
        p_stock = soup.select_one("p.stock")
        stock = limpiar_entero(p_stock.get_text(strip=True)) if p_stock else 0

        # SKU (Identificador único de producto en la tienda)
        span_sku = soup.select_one("span.sku")
        sku = limpiar_entero(span_sku.get_text(strip=True)) if span_sku else 0

        # Categorías: extraemos todas las etiquetas <a> dentro de span.posted_in.
        # Quitamos la categoría genérica 'Pokemon' para quedarnos con el tipo específico (Seed, Flame, etc.)
        enlaces_cat = soup.select("span.posted_in a")
        categorias = [a.get_text(strip=True) for a in enlaces_cat if a.get_text(strip=True).lower() != "pokemon"]
        categoria = categorias[0] if categorias else "General"

        # Peso: está en la tabla de información adicional bajo la fila de peso
        td_peso = soup.select_one("tr.woocommerce-product-attributes-item--weight td")
        peso_kg = limpiar_peso(td_peso.get_text(strip=True)) if td_peso else 0.0

        return {
            "sku": sku,
            "categoria": categoria,
            "stock": stock,
            "peso_kg": peso_kg,
            "descripcion": descripcion,
        }
    except Exception as e:
        print(f"   [Error en ficha {url_ficha}]: {e}")
        return None


def hacer_scraping(num_paginas=3):
    """
    Recorre las páginas del catálogo de ScrapeMe, extrae los datos básicos y de detalle
    de cada Pokémon y aplica retardos (rate limiting) con time.sleep().
    """
    lista_pokemons = []

    print(f"2. Iniciando extracción de {num_paginas} páginas de ScrapeMe (Tienda Pokémon)...")

    for pagina in range(1, num_paginas + 1):
        url_pagina = f"{BASE_URL}page/{pagina}/"
        print(f"   -> Leyendo página {pagina}: {url_pagina}")

        respuesta = requests.get(url_pagina, headers=HEADERS, timeout=10, verify=False)
        if respuesta.status_code != 200:
            print(f"   [Aviso] No se pudo cargar la página {pagina}.")
            break

        soup = BeautifulSoup(respuesta.text, "html.parser")

        # Seleccionamos cada tarjeta de producto con 'li.product' porque en WooCommerce
        # cada artículo del listado se estructura dentro de un elemento <li> con clase 'product'.
        productos = soup.select("li.product")

        for prod in productos:
            # Nombre del Pokémon
            titulo_tag = prod.select_one("h2.woocommerce-loop-product__title")
            nombre = titulo_tag.get_text(strip=True) if titulo_tag else "Desconocido"

            # Precio limpio convertido a float
            precio_tag = prod.select_one("span.price")
            precio = limpiar_precio(precio_tag.get_text(strip=True)) if precio_tag else 0.0

            # Enlace a la ficha del Pokémon (convertido a URL absoluta con urljoin)
            enlace_tag = prod.select_one("a.woocommerce-LoopProduct-link")
            href = enlace_tag["href"] if enlace_tag and enlace_tag.has_attr("href") else ""
            url_ficha = urljoin(url_pagina, href)

            # Imagen del Pokémon (convertida a URL absoluta)
            img_tag = prod.select_one("img")
            src = img_tag["src"] if img_tag and img_tag.has_attr("src") else ""
            imagen_url = urljoin(url_pagina, src)

            # Pausa ética (Rate Limiting) antes de pedir la ficha individual para no saturar el servidor
            time.sleep(0.2)

            detalle = extraer_detalle_pokemon(url_ficha)
            if detalle:
                lista_pokemons.append({
                    "sku": detalle["sku"],
                    "nombre": nombre,
                    "categoria": detalle["categoria"],
                    "precio_gbp": precio,
                    "stock": detalle["stock"],
                    "peso_kg": detalle["peso_kg"],
                    "descripcion": detalle["descripcion"],
                    "imagen_url": imagen_url,
                    "url_ficha": url_ficha
                })

        # Pausa entre páginas del catálogo
        time.sleep(0.5)

    return lista_pokemons


def guardar_csv(datos, nombre_archivo="pokemons.csv"):
    """
    Convierte la lista de diccionarios en un DataFrame de Pandas,
    asegura la limpieza y tipos de datos, y lo guarda en un archivo CSV.
    """
    df = pd.DataFrame(datos)

    # Eliminamos posibles duplicados por nombre y ordenamos por precio
    df = df.drop_duplicates(subset=["nombre"]).reset_index(drop=True)

    # Guardamos en CSV con codificación utf-8 para conservar tildes y caracteres especiales
    df.to_csv(nombre_archivo, index=False, encoding="utf-8")
    print(f"\n3. ¡Extracción completada con éxito! Se han guardado {len(df)} Pokémon en '{nombre_archivo}'.")
    return df


if __name__ == "__main__":
    if comprobar_robots_txt():
        datos_extraidos = hacer_scraping(num_paginas=3)
        if datos_extraidos:
            guardar_csv(datos_extraidos, "pokemons.csv")
