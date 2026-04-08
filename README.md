# Recull de receptes  de Receptes.cat 

Scraper en Python que recopila receptes del lloc [receptes.cat](https://www.receptes.cat/) i les guarda en format CSV pel seu posterior anàlisis.

## Descripció

Aquest projecte es realitaza dins el context de la assignatura **Tipologia i cicle de vida de les dades** del [Máster en Ciència de Dades de la Universitat Oberta de Catalunya](https://www.uoc.edu/ca/estudis/masters/master-universitari-data-science).

Aquest dataset és una recopilació de dades estructurades que conté informació de receptes extretes de la xarxa social de cuina en català Receptes.cat. El conjunt de les dades inclou milers de receptes escrites en català; cada recepta conté informació tècnica de la recepta (nom del plat, categoria culinària, ingredients, temps de preparació, dificultat, elaboració).

Amb la informació disponible, es permet als usuaris replicar una recepta. Fent un anàlisis global, es podrien veure les tendències de la cuina contemporània.


## Membres de l'equip

L'activitat s'ha realitzat conjuntament, els integrants són:
- **Berta Serra Aguilera** 
- **Martí Serra Aguilera**

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

