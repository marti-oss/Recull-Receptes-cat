# Receptes.cat Scrapper

Scraper en Python que recopila receptes del lloc [receptes.cat](https://www.receptes.cat/) i les guarda en format CSV per el seu posterior anàlisis.

## Descripció

Aquest projecte es realitaza dins el context de la assignatura **Tipologia i cicle de vida de les dades** del [Máster en Ciència de Dades de la Universitat Oberta de Catalunya](https://www.uoc.edu/ca/estudis/masters/master-universitari-data-science) amb l'objectiu d'extreure les receptes del portal receptes.cat tot recorrent automàticament les categories, extreu la inforamció detallada de cada recepta i la desa en un fitxer CSV estructurat.

El scraper està dissenyat per ser **resistent a talls de connexió**: escriu cada recepta al CSV immediatament i, en cas de fallada, pot reprende l'execucció sense tornar a descarregar les receptes ja guardades.

## Requisits

- Python 3.13*+
- Dependències:
    - `requests`
    - `beautifulsoup4`

Instal·lació:
```bash
python -m venv venv
source venv/Script/activate #Windows (bash)
pip install -r requirements.txt
```

## Ús

Els comandaments s'executen des de l'arrel del projecte

### Scrapejar totes les categories

```bash
python source/main.py
```

Genera el fitxer `dataset/recull_receptes_cat.csv`amb totes les receptes del portal

### Scrapejar categories concretes

```bash
python source/main --categoria amanides_i_entrants postres_i_dolcos
```

Genera un CSV independent per cada categoria:
- `dataset/recull_receptes_cat_amanides_i_entrants.csv`
- `dataset/recull_receptes_cat_postres_i_dolcos.csv`

Les categories vàlides són:

- `amanides_i_entrants`: Amanides i plats freds
- `sopes_i_cremes`: Sopes i cremes
-  `arrossos_i_pasta`: Arrossos i pastes
-  `llegums_i_verdures`: Llegums i verdures
-  `carns`: Carns
-  `peixos_i_mariscos`: Peixos i mariscos
-  `ous_i_lactics`: Ous i làctics
-  `postres_i_dolcos`: Postres i dolços
-  `salses`: Salses
-  `begudes`: Begudes
-  `altres`: Altres

Els identificadors són **case-sensitive**. Si passes una categoria no vàlida, es mostrarà un avís i s'ignorarà.

