import csv, os
import argparse
from scrapper import execute_scrapper

CATEGORIAS_VALIDAS = {
    'amanides_i_entrants': 'https://www.receptes.cat/cat/Amanides+i+plats+freds',
    'sopes_i_cremes':      'https://www.receptes.cat/cat/Sopes+i+cremes',
    'arrossos_i_pasta':    'https://www.receptes.cat/cat/Arrossos+i+pastes',
    'llegums_i_verdures':  'https://www.receptes.cat/cat/Llegums+i+verdures',
    'carns':               'https://www.receptes.cat/cat/Carns',
    'peixos_i_mariscos':   'https://www.receptes.cat/cat/Peixos+i+mariscos',
    'ous_i_lactics':       'https://www.receptes.cat/cat/Ous+i+l%C3%A0ctics',
    'postres_i_dolcos':    'https://www.receptes.cat/cat/Postres+i+dol%C3%A7os',
    'salses':              'https://www.receptes.cat/cat/Salses',
    'begudes':             'https://www.receptes.cat/cat/Begudes',
    'altres':              'https://www.receptes.cat/cat/Altres',
}

CSV_PATH_BASE = 'dataset/recull_receptes_cat'
FIELDNAMES = ['id', 'nom_recepta', 'categoria', 'tipus_plat', 'estacio',
        'dificultat', 'racions', 'temps', 'ingredients',
        'utensilis', 'elaboracio', 'url']

parser = argparse.ArgumentParser()
parser.add_argument(
    '--categoria',
    nargs='+',
    help=f'Categories a scrapejar. Valors vàlids: {", ".join(CATEGORIAS_VALIDAS.keys())}'
)
args = parser.parse_args()

os.makedirs("dataset", exist_ok=True)


def procesar_csv(csv_path, url_categoria_filtro):
    urls_existentes = set()
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                urls_existentes.add(row.get('url', ''))
        print(f"Nombre de receptes ja guardades a {csv_path}: {len(urls_existentes)}.")

    escribir_header = not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0
    with open(csv_path, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if escribir_header:
            writer.writeheader()
        total = execute_scrapper(writer, f, urls_existentes, url_categoria_filtro)

    print(f'CSV generat correctament: {csv_path}')
    print(f'Total de receptes (noves + existents): {total + len(urls_existentes)}')


if args.categoria:
    categorias_a_procesar = []
    for cat in args.categoria:
        if cat in CATEGORIAS_VALIDAS:
            categorias_a_procesar.append(cat)
        else:
            print(f"La categoria '{cat}' no és vàlida, no es pot scrapejar.")

    if not categorias_a_procesar:
        print("No s'ha proporcionat cap categoria vàlida. Sortint.")
        exit(1)

    for cat in categorias_a_procesar:
        csv_path = f'{CSV_PATH_BASE}_{cat}.csv'
        url_categoria = CATEGORIAS_VALIDAS[cat]
        print(f"\n=== Processant categoria: {cat} ===")
        procesar_csv(csv_path, url_categoria)
else:
    procesar_csv(f'{CSV_PATH_BASE}.csv', None)