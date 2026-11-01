# Le modèle Black-Litterman sur la BRVM

Le modèle de Black et Litterman combine un a priori (les rendements que suppose l'équilibre du marché) et des vues de l'investisseur pour produire des rendements espérés, puis une allocation. L'étude demande s'il apporte une valeur réelle sur la BRVM, marché étroit, concentré et peu liquide, une fois les frais, l'exécution en J+1 et la limite de ±7,5 % pris en compte, et face à la référence la plus difficile à battre : les parts égales.

Origine : le tableau de bord et le simulateur de `DylaneTrader/Reporting` allouent par Black-Litterman sur des vues Prophet (code de Scraper-BRVM, `quant/portfolio.py`). Une évaluation exploratoire dans le moteur de BRVM app (`Reporting/brvm/dashboard/evaluation/`, 01/11/2026) a donné 17 % par an contre 29 % pour les parts égales, avec une rotation de 6,9 fois le portefeuille par an. Ce résultat motive l'étude ; il ne la remplace pas, et les hypothèses devront être posées sans s'y ajuster (voir `00_pertinence.md`).

État : phase 1 (pertinence) et phase 2 (premier brouillon de revue de littérature) remises, en attente de validation. Suivi : [`JOURNAL.md`](JOURNAL.md).

Conventions, à suivre comme dans [`../fear_greed/`](../fear_greed/README.md) :

- données lues par `commun/depot.py`, au commit de `../sources.json` ;
- règles de marché de `commun/marche.py` ;
- aucun import de Scraper-BRVM ni de BRVM app : le modèle est réécrit dans ce dossier ;
- article construit avec `commun/mise_en_forme.py` ;
- chiffres écrits dans `sortie/chiffres.json`.
