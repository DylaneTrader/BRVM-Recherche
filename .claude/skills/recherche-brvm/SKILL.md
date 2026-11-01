---
name: recherche-brvm
description: >
  Conduire un travail de recherche destiné à publication sur la BRVM, dans
  recherche/, en cinq phases validées une à une par l'utilisateur :
  pertinence du sujet (données, littérature, puissance statistique, avis
  poursuivre, recadrer ou abandonner), revue de littérature aux références
  vérifiées, hypothèses figées avant tout calcul, code et rédaction, puis
  relectures et corrections. Fixe les livrables de chaque phase, les
  conventions de recherche/ (indépendance vis-à-vis du code du dépôt et de
  toute application, données à un commit figé, chiffres cités par clé depuis sortie/chiffres.json, Word en
  Times New Roman, aucun tiret cadratin) et renvoie vers les skills quant.
  À UTILISER dès que l'utilisateur propose un sujet de recherche ou d'article,
  demande la pertinence d'un sujet, une revue de littérature, une critique
  d'hypothèses, le code ou la rédaction d'une étude dans recherche/, ou
  revient sur une étude existante (fear_greed, score_risque…).
---

# Conduire une recherche sur la BRVM

> **Une phase ne commence que lorsque l'utilisateur a validé la précédente.
> Les hypothèses sont figées avant le premier calcul.**

La procédure protège deux choses : le temps de l'utilisateur (un sujet sans
données suffisantes s'arrête en phase 1, pas après le code) et la crédibilité
de l'article (des hypothèses posées après avoir vu les résultats ne prouvent
rien, surtout sur 18 ans de données et une cinquantaine de titres).

---

## 0. Avant de commencer

1. Lire `recherche/README.md` : principes, accès aux données, installation.
2. Lire le README de l'étude si elle existe déjà, et son `JOURNAL.md`, pour
   savoir à quelle phase elle en est. Une étude commencée hors procédure
   (c'est le cas de `fear_greed/`) reprend à la phase où elle se trouve, sans
   refaire les phases précédentes.
3. Pour tout calcul, charger **`brvm-quant`** puis les skills quant utiles
   (§ 6). Leurs règles de marché valent ici, mais le code de recherche ne les
   importe pas : il passe par `recherche/commun/`.

---

## 1. Les cinq phases

Chaque phase produit un fichier dans le dossier de l'étude
(`recherche/<etude>/`), se termine par un message à l'utilisateur qui résume
le livrable et pose les questions ouvertes, puis **s'arrête** jusqu'à sa
validation. La validation, avec sa date et les corrections demandées, est
notée dans `JOURNAL.md` (modèle : `references/journal.md`).

| Phase | Livrable | Ce que l'utilisateur valide |
|---|---|---|
| 1. Pertinence | `00_pertinence.md` | Poursuivre, recadrer ou abandonner ; la question de recherche |
| 2. Revue de littérature | `01_revue_litterature.md` | Les références retenues, ce que l'étude apporte de neuf |
| 3. Hypothèses | `02_hypotheses.md` | Les hypothèses, leurs tests, seuils et critères de rejet, figés |
| 4. Code et rédaction | code, `sortie/`, article Word | Lecture complète |
| 5. Relectures | corrections, `JOURNAL.md` | Chaque série de corrections |

### Phase 1 : pertinence

Modèle : `references/pertinence.md`. Répondre, chiffres à l'appui :

- **Données** : quelles tables de `data/`, depuis quand, combien de titres et
  de séances, trous connus (volumes de BRVMC vides avant août 2014, presse
  limitée à un an, dates de détachement manquantes…). Compter sur les données
  au commit de `recherche/sources.json`, pas de mémoire. Lancer
  `brvm-data-quality` sur les tables concernées si un doute existe.
- **Littérature** : le sujet est-il étudié ailleurs, sur d'autres marchés
  frontières africains, sur la BRVM ? Premier balayage seulement ; la revue
  complète est la phase 2.
- **Puissance statistique** : combien d'observations indépendantes l'étude
  aura réellement (18 ans font 18 cycles annuels, pas 4 800), quel effet
  minimal on peut espérer détecter, combien de tests on prévoit.
- **Changements de fonctionnement du marché** sur la période (cotation,
  horaires, limites de variation, frais) qui pourraient se confondre avec
  l'effet étudié. Les dater ou dire qu'ils restent à dater.
- **Apport** : ce que l'étude dirait de neuf, et pour qui.
- **Avis** : poursuivre, recadrer (avec la question recadrée) ou abandonner.

### Phase 2 : revue de littérature

Modèle : `references/revue_litterature.md`.

- **Aucune référence citée de mémoire.** Chaque référence est retrouvée
  (recherche web, Consensus, Elicit, SciSpace, Google Scholar) et porte son
  DOI ou un lien consulté. Une référence introuvable ne figure pas dans la
  revue ; elle peut être signalée à part, comme « à confirmer ».
- Indiquer pour chacune ce qui a été lu : texte complet ou résumé seul.
  Ne jamais attribuer à un article un résultat lu ailleurs.
- Organiser par question (pas par auteur) : ce qui est établi, ce qui est
  contesté, ce qui manque sur la BRVM et les marchés frontières.
- Terminer par l'**écart** que l'étude comble et les **méthodes** que la
  littérature recommande pour le mesurer.
- Une fois la revue validée et mise au propre, ses références alimentent la
  bibliographie de l'article.

### Phase 3 : hypothèses

Modèle : `references/hypotheses.md`. L'utilisateur fournit ses hypothèses ;
les critiquer franchement puis proposer une reformulation :

- testable et réfutable, avec la variable mesurée, l'échantillon et la période ;
- reliée à la littérature validée en phase 2 ;
- test statistique choisi d'avance, seuil, correction pour tests multiples
  (Holm ou Benjamini-Hochberg selon le nombre de tests), erreurs types
  robustes à l'autocorrélation et à l'hétéroscédasticité si besoin ;
- ce qui ferait **rejeter** l'hypothèse, écrit avant le calcul ;
- les analyses de robustesse prévues (sous-périodes, titres liquides seuls,
  autre fréquence) et le nombre total d'essais.

Une fois validées, les hypothèses ne changent plus. Toute analyse ajoutée
ensuite est **exploratoire** et présentée comme telle dans l'article.

### Phase 4 : code et rédaction

Suivre la structure de `recherche/fear_greed/` (§ 2). Ordre de travail :

1. `donnees.py` puis `etude.py` : calculs, tableaux, figures, `chiffres.json`.
2. Relire les résultats **avant** d'écrire : un résultat surprenant se vérifie
   (données, alignement des dates, ajustement des divisions) avant d'être
   interprété.
3. `article.py` : l'article, construit avec `commun/mise_en_forme.py`.
4. Présenter à l'utilisateur les résultats par hypothèse (confirmée, rejetée,
   non concluante), y compris les hypothèses rejetées, puis le document.

### Phase 5 : relectures

Les retours de l'utilisateur portent sur le texte, le code ou les deux.
Pour chacun : corriger, relancer `etude.py` si un chiffre peut changer,
reconstruire l'article, puis consigner dans `JOURNAL.md` ce qui a changé.
Si une correction remet en cause une hypothèse figée, le dire et demander
avant d'agir.

---

## 2. Organisation d'une étude

```
recherche/<etude>/
  README.md                 # question, état, commandes pour reproduire
  JOURNAL.md                # phases, validations, corrections
  00_pertinence.md
  01_revue_litterature.md
  02_hypotheses.md
  donnees.py                # lecture et préparation, via commun/
  etude.py                  # calculs, tableaux, figures, chiffres.json
  figures.py                # si les figures sont nombreuses
  article.py                # document Word
  sortie/                   # CSV, PNG, chiffres.json
```

Ajouter l'étude au tableau de `recherche/README.md` dès la phase 1, avec son
état (« Phase 1 : pertinence », …).

---

## 3. Conventions de recherche/ (non négociables)

- **Indépendance** : `recherche/` (dépôt BRVM-Recherche) n'importe rien de Scraper-BRVM (`scraper/`,
  `quant/`, `lecture_donnees.py`…) ni de BRVM app ; il n'en lit que les
  données, au commit figé. Les règles de marché sont dans
  `commun/marche.py` ; s'il en manque une, l'y ajouter.
- **Données à un commit figé** : `recherche/sources.json` fixe le commit et
  les chemins lus ; `commun/depot.py` les extrait. La source unique, `brvm`,
  est le dépôt de données Scraper-BRVM. Avancer ce commit change
  tous les résultats : ne le faire qu'avec l'accord de l'utilisateur, et pas
  pendant les relectures d'une étude.
- **Chiffres traçables** : tout nombre du texte vient de
  `sortie/chiffres.json` par sa clé (`{p:cle:1}`, `{n:cle:2}`…). Aucun
  nombre saisi à la main dans `article.py`.
- **Document** : Word, Times New Roman, en français, encodage UTF-8. Le
  tiret cadratin est interdit (la construction échoue s'il en reste) ;
  utiliser une virgule, des parenthèses, un deux-points ou une reformulation.
- **Graphiques** : charte de `trading-visualization`.
- **Usage de l'IA** : chaque étude publiée a sa déclaration, sur le modèle de
  `fear_greed/declaration_ia.py`.

---

## 4. Contraintes BRVM à rappeler dans toute étude

Détaillées dans `brvm-quant` ; les signaler dès la phase 1 quand elles
touchent le sujet : séances sans échange (lignes absentes, cours figés),
limite de variation de ±7,5 %, exécution réaliste en J+1, frais, divisions du
nominal, dividendes au nominal actuel, faible nombre de titres, forte
concentration de la capitalisation.

---

## 5. Ce que la skill ne fait pas

- Elle n'automatise pas une étude : chaque phase attend une validation. Une
  tâche planifiée ne convient qu'à une note récurrente, pas à une étude.
- Elle n'écrit jamais dans `data/`.
- Elle ne fait pas entrer une méthode dans `quant/` ni dans BRVM app : cela
  se décide après publication, dans un travail séparé.

---

## 6. Skills à charger selon le sujet

Ces skills (sauf celle-ci) sont dans le dépôt de données DylaneTrader/Scraper-BRVM,
avec les données qu'elles lisent : y ouvrir la session de calcul, ou cloner les deux
dépôts côte à côte.

| Besoin | Skill |
|---|---|
| Socle, données, contraintes de marché | `brvm-quant` (toujours) |
| Qualité des cours, dividendes, divisions | `brvm-data-quality`, `ohlcv-processing` |
| Stratégie et backtest | `strategy-framework`, `vectorbt`, `walk-forward-validation` |
| Performance et risque | `portfolio-analytics`, `risk-management` |
| Volatilité, régimes | `volatility-modeling`, `regime-detection` |
| Corrélations | `correlation-analysis` |
| Graphiques | `trading-visualization` |

---

## 7. Sujets retenus

| Sujet | Dossier prévu | Points de vigilance connus |
|---|---|---|
| Saisonnalité des volumes | `saisonnalite_volumes/` | Volumes de BRVMC vides avant août 2014 (reconstruire depuis les titres) ; saison des dividendes ; Ramadan (calendrier lunaire) ; tests multiples sur mois et jours |
| Surestimation des backtests naïfs | `backtest_naif/` | Exécution en J+1, règlement-livraison en J+3 puis J+2 depuis le 4 décembre 2025 ; réécrire le moteur dans recherche/ ; mesurer l'effet de chaque contrainte séparément ; comparer à `quant/backtest.py` comme contrôle, sans l'importer |
| Ratios réglementaires d'un fonds | `ratios_reglementaires/` | Aucune VL, aucun flux ni position de FCP dans `data/` ; ratios de l'Instruction n° 66/CREPMF/2021 à relever dans le texte et ses circulaires ; flux à modéliser ; régularisation limitée par la liquidité et le ±7,5 % |
| Cours autour du détachement du dividende | `detachement_dividende/` | Dates de détachement manquantes ou fausses (`brvm-data-quality`) ; brut ou net ; fiscalité différente selon le pays ; jours sans échange autour de la date |
