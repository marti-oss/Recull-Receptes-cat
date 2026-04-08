import requests
import time                                                                                                                                                                         
from bs4 import BeautifulSoup, Tag, NavigableString
from urllib.parse import urljoin
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
import re
import random

url = 'https://www.receptes.cat/'
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.79 Safari/537.36"
}


def obtener_html(url):
    res = requests.get(url,headers=HEADERS)
    if 200 != res.status_code: 
        return None
    return res.text

def obtener_soup(html):
    return BeautifulSoup(html, "html.parser")

def extraer_categorias(soup):
    categorias = []
    enlaces = soup.find_all("a")
    for enlace in enlaces:
        href = enlace.get("href")
        texto = enlace.get_text(strip=True)

        if href and href.startswith("/cat/"):
            categorias.append((texto, urljoin(url,href)))
    return categorias

def extraer_recetas(soup_categoria):
    recetas = []
    urls_vistas = set()

    # Es busca els elements que tinguin un referencia amb '/recepta' i l'lement sigui de tipus 'h2'
    enlaces = soup_categoria.select("h2 a[href^='/recepta']")


    for enlace in enlaces:
        href = enlace.get("href")
        texto = enlace.get_text(strip=True)

        if href and href.startswith("/recepta"):
            url_completa = urljoin(url, href)

            if url_completa not in urls_vistas:
                recetas.append((texto, url_completa))
                urls_vistas.add(url_completa)

    return recetas

def extraer_paginas_categoria(soup):
    paginas = []
    urls_vistas = set()

    enlaces = soup.find_all("a")

    for enlace in enlaces:
        href = enlace.get("href")
        texto = enlace.get_text(strip=True)

        if not href:
            continue

        # Es busquen el enllaços que porten a altres pàgines
        if "page=" in href:
            url_completa = urljoin(url, href)

            if url_completa not in urls_vistas:
                paginas.append((texto, url_completa))
                urls_vistas.add(url_completa)

    return paginas

def construir_url_pagina(url_base_paginacion, numero_pagina):
    partes = urlparse(url_base_paginacion)
    query = parse_qs(partes.query)

    query["page"] = [str(numero_pagina)]

    nueva_query = urlencode(query, doseq=True)

    nueva_url = urlunparse((
        partes.scheme,
        partes.netloc,
        partes.path,
        partes.params,
        nueva_query,
        partes.fragment
    ))

    return nueva_url

def recorrer_categoria(url_categoria):
    html = obtener_html(url_categoria)
    if html is None:
        return []

    soup = obtener_soup(html)

    recetas_totales = []
    urls_vistas = set()

    # Pàgina 1
    recetas_pagina_1 = extraer_recetas(soup)

    for titulo, url in recetas_pagina_1:
        if url not in urls_vistas:
            recetas_totales.append((titulo, url))
            urls_vistas.add(url)

    paginas = extraer_paginas_categoria(soup)

    if not paginas:
        return recetas_totales

    plantilla_paginacion = paginas[0][1]

    numero_pagina = 2

    while True:
        url_pagina = construir_url_pagina(plantilla_paginacion, numero_pagina)

        html_pagina = obtener_html(url_pagina)
        if html_pagina is None:
            break

        soup_pagina = obtener_soup(html_pagina)
        recetas_pagina = extraer_recetas(soup_pagina)

        # Si no hi ha més receptes, no cal continuar
        if not recetas_pagina:
            break

        nuevas = 0
        for titulo, url in recetas_pagina:
            if url not in urls_vistas:
                recetas_totales.append((titulo, url))
                urls_vistas.add(url)
                nuevas += 1

        # Si no hi ha més receptes, no cal continuar
        if nuevas == 0:
            break

        numero_pagina += 1

    return recetas_totales

def limpiar_espacios(texto):
    return re.sub(r"\s+", " ", texto).strip()


def buscar_bloque_metadato(soup, etiqueta):
    nodo_texto = soup.find(string=lambda s: s and etiqueta in limpiar_espacios(s))
    if not nodo_texto:
        return None

    contenedor = nodo_texto.parent
    while contenedor and contenedor.name not in {"div", "p", "span", "li"}:
        contenedor = contenedor.parent

    return contenedor


def extraer_valor_unico_enlace(soup, etiqueta):
    bloque = buscar_bloque_metadato(soup, etiqueta)

    if bloque is None:
        return ""

    # Buscar el bloc que conté l'etiqueta
    nodo_etiqueta = bloque.find(string=lambda s: s and etiqueta in s)
    if nodo_etiqueta is None:
        return ""

    textos = []

    for sibling in nodo_etiqueta.next_siblings:
        if getattr(sibling, "name", None) == "br":
            break

        if isinstance(sibling, NavigableString):
            texto = limpiar_espacios(str(sibling))
            if texto:
                textos.append(texto)

        elif isinstance(sibling, Tag):
            enlaces = sibling.find_all("a")
            if enlaces:
                for a in enlaces:
                    texto = limpiar_espacios(a.get_text(" ", strip=True))
                    if texto:
                        textos.append(texto)
            else:
                texto = limpiar_espacios(sibling.get_text(" ", strip=True))
                if texto:
                    textos.append(texto)

    return textos[0] if textos else ""

def extraer_estaciones(soup):
    bloque = soup.select_one("span.seasons")
    if bloque is None:
        bloque = buscar_bloque_metadato(soup, "Estació:")
        if bloque is None:
            return []

    estaciones = []
    for a in bloque.find_all("a"):
        texto = limpiar_espacios(a.get_text())
        if texto:
            estaciones.append(texto)

    if estaciones:
        return estaciones

    texto_bloque = limpiar_espacios(bloque.get_text(" ", strip=True))
    estaciones_validas = ["primavera", "estiu", "tardor", "hivern"]
    return [e for e in estaciones_validas if re.search(rf"\b{re.escape(e)}\b", texto_bloque, re.I)]


def extraer_raciones(soup):
    h2_ingredients = soup.find("h2", string=lambda s: s and "Ingredients" in s)
    if h2_ingredients is None:
        return None

    nodo = h2_ingredients.find_next_sibling()

    while nodo:
        if isinstance(nodo, Tag) and nodo.name == "h2":
            break

        texto = limpiar_espacios(nodo.get_text(" ", strip=True)) if isinstance(nodo, Tag) else limpiar_espacios(str(nodo))
        match = re.search(r"(\d+)\s*racions?\b", texto, re.I)
        if match:
            return int(match.group(1))

        nodo = nodo.find_next_sibling()

    return None


def extraer_tiempo(soup):
    h2_elaboracio = soup.find("h2", string=lambda s: s and "Elaboració" in s)
    if h2_elaboracio is None:
        return None

    nodo = h2_elaboracio.find_next_sibling()

    while nodo:
        if isinstance(nodo, Tag) and nodo.name == "h2":
            break

        if isinstance(nodo, Tag):
            for img in nodo.find_all("img", alt=True):
                alt = limpiar_espacios(img["alt"])
                match = re.search(r"(\d+)\s*min\.?", alt, re.I)
                if match:
                    return int(match.group(1))

            texto = limpiar_espacios(nodo.get_text(" ", strip=True))
        else:
            texto = limpiar_espacios(str(nodo))

        match = re.search(r"(\d+)\s*min\.?", texto, re.I)
        if match:
            return int(match.group(1))

        match = re.search(r"(\d+)\s*h\b", texto, re.I)
        if match:
            return int(match.group(1)) * 60

        nodo = nodo.find_next_sibling()

    return None

def extraer_bloque_hasta_h2(soup, titulo_h2):
    h2 = soup.find("h2", string=lambda s: s and titulo_h2.lower() in s.lower())
    if not h2:
        return []

    bloques = []
    nodo = h2.find_next_sibling()

    while nodo and nodo.name != "h2":
        texto = limpiar_espacios(nodo.get_text(" ", strip=True))
        if texto:
            bloques.append(texto)
        nodo = nodo.find_next_sibling()

    return bloques

def extraer_id_receta(url):
    m = re.search(r"/recepta(\d+)", url)
    return m.group(1) if m else None

def extraer_detalles_receta(url_receta):
    html = obtener_html(url_receta)
    if html is None:
        return None

    soup = obtener_soup(html)

    receta = {
        "id": "",
        "nom_recepta": "",
        "categoria": "",
        "tipo_plato": "",
        "estacion": [],
        "dificultad": "",
        "raciones": None,
        "tiempo": None,
        "ingredientes": [],
        "utensilios": [],
        "elaboracion": "",
        "url": url_receta,
    }

    receta["id"] = extraer_id_receta(url_receta)

    nom_recepta = soup.find("h1")
    if nom_recepta:
        receta["nom_recepta"] = limpiar_espacios(nom_recepta.get_text())

    lineas = [limpiar_espacios(x) for x in soup.get_text("\n").split("\n")]
    lineas = [x for x in lineas if x]

    receta["categoria"] = extraer_valor_unico_enlace(soup, "Categoria:")
    receta["tipo_plato"] = extraer_valor_unico_enlace(soup, "Tipus de plat:")
    receta["estacion"] = extraer_estaciones(soup)
    receta["dificultad"] = extraer_valor_unico_enlace(soup, "Dificultat:")
    receta["raciones"] = extraer_raciones(soup)
    receta["tiempo"] = extraer_tiempo(soup)

    h2_ingredientes = soup.find("h2", string=lambda s: s and "Ingredients" in s)
    if h2_ingredientes:
        ul = h2_ingredientes.find_next("ul")
        if ul:
            for li in ul.find_all("li"):
                texto = limpiar_espacios(li.get_text(" ", strip=True))
                texto = texto.replace("[Veure recepta]", "").strip()
                if texto:
                    receta["ingredientes"].append(texto)

    receta["utensilios"] = extraer_bloque_hasta_h2(soup, "Utensilis")

    bloques_elaboracion = extraer_bloque_hasta_h2(soup, "Elaboració")

    bloques_limpios = []
    for bloque in bloques_elaboracion:
        if re.search(r"\b\d+\s*racions?\b", bloque, re.IGNORECASE):
            continue
        if re.search(r"\b\d+\s*min\.?\b", bloque, re.IGNORECASE):
            continue
        bloques_limpios.append(bloque)

    receta["elaboracion"] = " ".join(bloques_limpios)

    return receta

def normalizar_receta_para_csv(receta):
    return {
        'id': receta.get('id', ''),
        'nom_recepta': receta.get('nom_recepta', ''),
        'categoria': receta.get('categoria', ''),
        'tipus_plat': receta.get('tipo_plato', ''),
        'estacio': ' | '.join(receta.get('estacion', [])),
        'dificultat': receta.get('dificultad', ''),
        'racions': receta.get('raciones', ''),
        'temps': receta.get('tiempo', ''),
        'ingredients': ' | '.join(receta.get('ingredientes', [])),
        'utensilis': ' | '.join(receta.get('utensilios', [])),
        'elaboracio': receta.get('elaboracion', ''),
        'url': receta.get('url', ''),
    }


def execute_scrapper(writer, file_handle, urls_ya_scrapeadas, url_categoria_filtro=None):
    nuevas = 0

    if url_categoria_filtro is not None:
        # Scrapejar només una categoria concreta
        categorias = [(url_categoria_filtro, url_categoria_filtro)]
    else:
        # Extreure totes les categories
        html = obtener_html(url)
        if html == None:
            return nuevas

        soup = obtener_soup(html)
        print(f"Títol de la pàgina: {soup.title.text}")

        categorias = extraer_categorias(soup)
        print(categorias)

    for nombre_categoria, url_categoria in categorias:
        html_categoria = obtener_html(url_categoria)
        soup_categoria = obtener_soup(html_categoria)
        print(f"Títol de la pàgina: {soup_categoria.title.text}")

        recetas_totales = recorrer_categoria(url_categoria)
        for nombre_receta, url_receta in recetas_totales:
            if url_receta in urls_ya_scrapeadas:
                print(f"Skip (ja existeix): {nombre_receta}")                                                                                                                   
                continue
            detalle = extraer_detalles_receta(url_receta)
            fila = normalizar_receta_para_csv(detalle)
            writer.writerow(fila)                                                                                                                                                   
            file_handle.flush()
            urls_ya_scrapeadas.add(url_receta)
            nuevas += 1
        time.sleep(random.uniform(15,30))


    print(f'Total de receptes úniques extretes: {nuevas}')
    return nuevas