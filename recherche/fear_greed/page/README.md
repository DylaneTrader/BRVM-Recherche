# Page publique de l'indice

`publier.py` calcule l'indice Fear & Greed BRVM (version initiale de l'article, v2, définie dans `../indice.py`) sur les données publiques de [brvm-py](https://github.com/DylaneTrader/brvm-py) et écrit un site statique : `index.html` (sans script ni ressource extérieure), `fear_greed.json` et `fear_greed.csv`.

Le workflow `.github/workflows/fear_greed_page.yml` le relance chaque jour de séance et publie le site sur GitHub Pages, à l'adresse `https://dylanetrader.github.io/BRVM-Recherche/`.

Contrôle : au 29/10/2026, la page donne 19,6 (peur extrême), soit la valeur du score v2 recalculé sur les données de Scraper-BRVM au 29/10/2026 citée dans `../README.md`.

```bash
pip install pandas numpy "brvm-py @ git+https://github.com/DylaneTrader/brvm-py"
python recherche/fear_greed/page/publier.py --sortie site
```
