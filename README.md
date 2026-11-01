# BRVM Recherche

Travaux de recherche sur la BRVM (Bourse Régionale des Valeurs Mobilières), destinés à publication. Ce dépôt
ne collecte rien : il lit, à un commit figé, les données du dépôt `DylaneTrader/Scraper-BRVM`.

- `recherche/` : les études (Fear & Greed BRVM, régime de marché, score de risque, saisonnalité des volumes,
  backtest naïf, ratios réglementaires), le code partagé (`recherche/commun/`) et la source des données
  (`recherche/sources.json`). Voir [recherche/README.md](recherche/README.md).
- `.claude/skills/recherche-brvm/` : la procédure en cinq phases suivie par chaque étude.

## Installer

Cloner Scraper-BRVM à côté de ce dépôt : les données y sont lues sans réseau ni jeton.

```bash
git clone https://github.com/DylaneTrader/Scraper-BRVM.git
git clone https://github.com/DylaneTrader/BRVM-Recherche.git
cd BRVM-Recherche
python -m venv recherche/.venv
recherche/.venv/Scripts/python.exe -m pip install -r recherche/requirements.txt
```

Sans clone voisin, les données sont téléchargées depuis GitHub avec un jeton en lecture dans `GITHUB_TOKEN`.

## Historique

`recherche/` a été créé dans `DylaneTrader/brvm-app`, puis déplacé dans Scraper-BRVM et enfin ici le
01/11/2026. Son historique antérieur est dans ces deux dépôts.
