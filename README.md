# Receptes.cat Scrapper

Scraper en Python que recopila receptes del lloc [receptes.cat](https://www.receptes.cat/) i les guarda en format CSV per el seu posterior anàlisis.

## Descripció

Aquest projecte extreu les receptes del portal receptes.cat tot recorrent automàticament les categories, extreu la inforamció detallada de cada recepta i la desa en un fitxer CSV estructurat.

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
