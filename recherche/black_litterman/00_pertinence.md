# Pertinence : le modèle Black-Litterman sur la BRVM

Date : 2026-11-01. Données au commit `be980d48` de `DylaneTrader/Scraper-BRVM` (`recherche/sources.json`, données au 29/10/2026).

## Question proposée

Sujet de l'utilisateur : le modèle Black-Litterman sur la BRVM.

Reformulation proposée : **une allocation Black-Litterman fait-elle mieux, nette des frais et exécutée de façon réaliste, que les parts égales et que la pondération par la capitalisation flottante sur les actions de la BRVM ? Et d'où vient l'écart : de l'a priori, des vues, ou de la rotation ?**

La question sépare trois choses que le tableau de bord confond : l'a priori (neutre aujourd'hui, d'équilibre dans le modèle original), les vues (Prophet aujourd'hui) et la mise en œuvre (rééquilibrage mensuel complet, d'où la rotation).

## Données disponibles

| Table | Période | Titres ou séries | Observations | Trous et défauts connus |
|---|---|---|---|---|
| `data/actions/*_historique.csv` | 02/01/2008 au 29/10/2026 | 48 actions ; 42 cotées avant 2019, 28 avant 2010 | médiane de 1 447 séances avec cours par titre | séances sans échange (lignes absentes), cours figés, divisions du nominal à ajuster (`commun/marche.py`) |
| `data/indices/*_historique.csv` | depuis 2008 | BRVMC, BRVM30, indices sectoriels | | volumes de BRVMC vides avant août 2014 |
| `data/Composition_flottante.xlsx` | depuis 2008 | poids de chaque titre dans la capitalisation flottante | 4 803 dates | feuille de vérification sur 1 756 dates seulement ; à contrôler avant de s'en servir comme a priori |
| `data/dividendes/dividendes.csv` | | dividendes par titre | | dates de détachement manquantes ou fausses (`brvm-data-quality`) |

Observations réellement indépendantes : une allocation mensuelle sur 18 ans fait environ 220 rééquilibrages, mais les écarts de performance entre deux stratégies sont autocorrélés ; à l'échelle des cycles de marché, il n'y en a que quelques-uns. L'univers utile à une date donnée (titres assez liquides pour être achetés) compte de 20 à 40 titres selon le seuil.

**La capitalisation flottante quotidienne est la pièce rare** : elle permet l'a priori d'équilibre du modèle original (rendements implicites par optimisation inverse), que l'implémentation actuelle remplace par un a priori neutre.

## Littérature : premier balayage

- Marchés développés : le modèle est très étudié depuis Black et Litterman (1992) ; les évaluations hors échantillon sont partagées, et les parts égales restent difficiles à battre (DeMiguel, Garlappi et Uppal, 2009).
- Marchés émergents et frontières : quelques applications (Amérique latine, Corée, Vietnam), surtout avec des vues d'analystes ; en Afrique, des mémoires sur Johannesburg et Nairobi.
- BRVM : aucune application du modèle trouvée. Les études d'efficience de la BRVM, partagées, disent ce que des vues fondées sur les cours passés peuvent espérer.

Détail et références : `01_revue_litterature.md`.

## Puissance statistique

- Effet minimal détectable : avec environ 18 ans de rendements mensuels et une volatilité de l'écart entre deux stratégies de l'ordre de 8 à 10 % par an, un écart de rendement annuel inférieur à 4 ou 5 points ne se distinguera pas du hasard au seuil de 5 %. Le test de différence des ratios de Sharpe de Ledoit et Wolf (2008), ou un bootstrap par blocs, est à prévoir ; la référence sera vérifiée en phase 2.
- Nombre de tests : prévoir peu de variantes (a priori neutre ou d'équilibre, deux ou trois sources de vues, avec ou sans bande de non-rééquilibrage), soit une dizaine de comparaisons, avec la correction de Holm et un ratio de Sharpe dégonflé (voir `../backtest_naif/`).

## Changements de fonctionnement du marché sur la période

| Date | Changement | Effet possible sur l'étude |
|---|---|---|
| 2008 à 2026 | Introductions en bourse (Orange CI, Sonatel déjà dominante, nouvelles cotations) | l'univers et la concentration changent ; les poids d'équilibre aussi |
| 04/12/2025 | Règlement-livraison passé de J+3 à J+2 | effet faible sur une allocation mensuelle |
| à dater | Barème de frais, limite de variation, horaires de cotation | les frais pèsent directement sur une stratégie à forte rotation |

## Apport attendu

Pour les gérants de la place (OPCVM, SGI) : savoir si un outil répandu ailleurs vaut quelque chose sur un marché où la capitalisation est très concentrée et où les échanges sont rares. Pour les chercheurs : une première application documentée du modèle sur la BRVM, avec une mise en œuvre réaliste et une décomposition de l'écart, ce que les études sur les marchés frontières font rarement.

## Avis

**Poursuivre, recadré** sur la question ci-dessus. Trois réserves :

1. **Le résultat exploratoire est déjà connu.** L'évaluation du tableau de bord (Reporting, 01/11/2026) a été vue avant les hypothèses. Pour ne pas s'y ajuster, figer en phase 3 les variantes testées avant tout calcul, et garder la période 2019-2026 comme confirmation, l'estimation des réglages se faisant sur 2008-2018.
2. **Les vues ne doivent pas être le sujet principal.** Tester la valeur de Prophet est une autre question ; l'étude doit comparer des vues simples et documentées (momentum, valeur par le rendement du dividende, vues nulles) pour isoler l'apport du cadre.
3. **La liquidité limite l'univers.** Le seuil de liquidité et la participation au volume se fixent d'avance.

## Questions à l'utilisateur

1. La question recadrée vous convient-elle, ou voulez-vous étudier d'abord la valeur des vues Prophet ?
2. Quelles références voulez-vous comme témoins : parts égales seulement, ou aussi la capitalisation flottante (l'équivalent d'un fonds indiciel BRVMC) ?
3. Acceptez-vous la séparation 2008-2018 pour les réglages et 2019-2026 pour la confirmation ?
