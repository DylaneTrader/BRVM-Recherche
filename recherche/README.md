# Travaux de recherche

Études sur le marché de la BRVM, destinées à être publiées. Chacune vit dans son dossier, avec son code, ses résultats et son article. Le dossier a quitté `DylaneTrader/brvm-app` pour `DylaneTrader/Scraper-BRVM`, puis, le 01/11/2026, ce dépôt dédié à la recherche (`DylaneTrader/BRVM-Recherche`). Il ne lit que les données de Scraper-BRVM.

| Dossier | Travail | État |
|---|---|---|
| [`fear_greed/`](fear_greed/README.md) | Indice de sentiment Fear & Greed BRVM : construction et validation | Article rédigé (Prix de la Recherche des 30 ans de la BRVM) |
| [`regime_marche/`](regime_marche/README.md) | Régime de marché par les moyennes mobiles et participation des titres | Phase 2 : revue de littérature, en attente de validation |
| [`score_risque/`](score_risque/README.md) | Score de risque des titres et régimes de volatilité | Phase 2 : revue de littérature, en attente de validation |
| [`saisonnalite_volumes/`](saisonnalite_volumes/README.md) | Saisonnalité des volumes échangés | Phase 1 : pertinence, en attente de validation |
| [`backtest_naif/`](backtest_naif/README.md) | De combien un backtest naïf surestime-t-il une stratégie sur la BRVM ? | Phase 2 : revue de littérature, en attente de validation |
| [`ratios_reglementaires/`](ratios_reglementaires/README.md) | Prévision probabiliste et stress des ratios réglementaires (portefeuille actions ; FCP à quatre classes d'actifs) | Phase 2 : revue de littérature, en attente de validation |
| [`black_litterman/`](black_litterman/README.md) | Le modèle Black-Litterman sur la BRVM : a priori d'équilibre, vues et rotation, face aux parts égales | Phase 2 : revue de littérature, en attente de validation (phase 1 validée) |
| `detachement_dividende/` | Comportement des cours autour du détachement du dividende | Sujet retenu, phase 1 à venir |
| `commun/` | Code partagé : accès aux données, règles de marché, mise en forme Word | |

## Procédure

Chaque étude suit cinq phases, chacune validée avant la suivante : pertinence du sujet, revue de littérature, hypothèses figées avant tout calcul, code et rédaction, relectures. Le détail, les livrables et leurs modèles sont dans la skill [`.claude/skills/recherche-brvm/`](../.claude/skills/recherche-brvm/SKILL.md). `fear_greed/`, commencée avant cette procédure, en est à la phase des relectures.

## Principes

- **Indépendance.** Le code de recherche n'importe rien de Scraper-BRVM (`scraper/`, `quant/`, `lecture_donnees.py`…) ni de BRVM app : il n'en lit que les données. Les règles de traitement des données sont réécrites dans `commun/marche.py`, et chaque indice dans le dossier de son étude. Une méthode n'entre dans `quant/` ou dans une application qu'une fois publiée.
- **Données tirées de GitHub, à un commit figé.** `sources.json` désigne le dépôt, le commit et les seuls fichiers lus. `commun/depot.py` les extrait dans `.donnees/` (ignoré par git) au premier calcul. Un même commit donne toujours les mêmes résultats, quel que soit le jour d'exécution. Une seule source, `brvm` : le dépôt de données `DylaneTrader/Scraper-BRVM` (données au 29/10/2026). Toutes les études, `fear_greed/` compris, la lisent depuis le 01/11/2026 ; auparavant, les données venaient de `DylaneTrader/brvm-app` (commit `ca9470c`, données au 07/10/2026).
- **Chiffres traçables.** Chaque étude écrit ses nombres dans `sortie/chiffres.json`. L'article les cite par leur clé. Un chiffre absent fait échouer la construction du document, comme un renvoi inconnu ou un tiret cadratin.

## Collecte des données

Le dépôt de données `DylaneTrader/Scraper-BRVM` reçoit chaque jour ouvré, après la clôture, les données collectées par GitHub Actions (`.github/workflows/scrape-daily.yml`) :

- cours, volumes et indices de la cote de la BRVM, diffusés par SikaFinance ;
- avis de paiement de dividendes de la BRVM (brvm.org), complétés par SikaFinance.

Toutes les requêtes passent par `scraper/conformite.py` :

- **robots.txt** : le fichier de chaque domaine est lu avant la première requête et interprété selon la RFC 9309. Une adresse interdite n'est jamais demandée.
- **Délai entre deux requêtes** au même domaine : le Crawl-delay du site, avec au moins 0,5 s. La BRVM impose 10 s.
- **Journal** : chaque exécution l'écrit dans `data/sources_conformite.json`, avec par domaine les requêtes faites et les adresses refusées.

Sitemaps : celui de SikaFinance est déclaré dans son robots.txt et liste la page de cotation de chaque titre. La BRVM n'en publie pas.

## Installer et exécuter

```bash
python -m venv recherche/.venv
recherche/.venv/Scripts/python.exe -m pip install -r recherche/requirements.txt
```

Accès aux données :

- **Dépôt privé** : il faut un jeton GitHub en lecture dans la variable `GITHUB_TOKEN`.
- **Hors ligne** : un clone de Scraper-BRVM placé à côté de ce dépôt (`../Scraper-BRVM`) est lu sans réseau ni jeton quand il contient le commit figé ; `RECHERCHE_SOURCE_BRVM` peut désigner un clone situé ailleurs. Le commit figé y est extrait, pas l'état du dossier de travail.

Les commandes de chaque étude sont dans son README.
