# Page publique de l'indice

`publier.py` calcule l'indice Fear & Greed BRVM (version révisée de l'article, section 7, définie dans `../indice.py` : la même que la page Overview de BRVM app) sur les données publiques de [brvm-py](https://github.com/DylaneTrader/brvm-py) et écrit un site statique : `index.html` (sans script ni ressource extérieure), `fear_greed.json` et `fear_greed.csv`.

Le workflow `.github/workflows/fear_greed_page.yml` le relance chaque jour de séance et publie le site sur GitHub Pages, à l'adresse `https://dylanetrader.github.io/BRVM-Recherche/`.

Contrôle : au 20/11/2026, la page donne 9,1 (peur extrême ; 16 une semaine plus tôt, 31 un mois plus tôt, 58 un an plus tôt), les valeurs affichées par BRVM app le même jour.

Écart de données assumé : brvm-py ne publie pas l'historique des pondérations du BRVM Composite. Pour réinvestir les dividendes, la page pondère chaque titre par sa capitalisation du jour (cours x nombre de titres actuel). Au 20/11/2026, cela ne change aucun score arrondi.

```bash
pip install pandas numpy "brvm-py @ git+https://github.com/DylaneTrader/brvm-py"
python recherche/fear_greed/page/publier.py --sortie site
```
