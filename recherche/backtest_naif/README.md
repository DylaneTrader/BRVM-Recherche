# De combien un backtest naïf surestime-t-il une stratégie sur la BRVM ?

Un moteur de backtest est un outil, pas un résultat. L'étude mesure l'écart entre la performance simulée naïvement et la performance réaliste d'une stratégie sur la BRVM, et la part de chaque contrainte : délai d'exécution (J+1) et de règlement-livraison (J+3, puis J+2 depuis le 4 décembre 2025), limite de variation de ±7,5 %, séances sans échange, frais, dividendes et divisions du nominal.

Le moteur est réécrit dans `recherche/` ; `quant/backtest.py` de Scraper-BRVM (le même que celui de BRVM app) sert de contrôle, sans être importé.

État : phase 2, revue de littérature remise ([`01_revue_litterature.md`](01_revue_litterature.md)), en attente de validation. Suivi : [`JOURNAL.md`](JOURNAL.md).

Conventions, à suivre comme dans [`../fear_greed/`](../fear_greed/README.md) : données lues par `commun/depot.py`, règles de marché de `commun/marche.py`, article construit avec `commun/mise_en_forme.py`, chiffres écrits dans `sortie/chiffres.json`.
