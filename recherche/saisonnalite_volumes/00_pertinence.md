# Pertinence : saisonnalité des volumes échangés à la BRVM

Date : 2026-10-15. Données au commit `ca9470cc238843900bf6870d054d80d30f5bfa5a` (`recherche/sources.json`, données arrêtées au 2026-10-07).

Cette fiche ne regarde volontairement aucun profil saisonnier (moyenne par mois, par jour ou autour du Ramadan) : ces chiffres viendront après le gel des hypothèses (phase 3).

## Question proposée

**D'origine** : le comportement cyclique ou saisonnier des volumes.

**Reformulée** : l'activité d'échange de la BRVM (valeur échangée, nombre de titres échangés, rotation) suit-elle des régularités de calendrier (mois de l'année, jour de la semaine, fin de mois, saison des dividendes, Ramadan et fêtes à date lunaire), et ces régularités résistent-elles aux transactions de blocs, au passage à la cotation en continu et à la concentration du marché ?

## Données disponibles

| Table | Période | Titres ou séries | Observations | Trous et défauts connus |
|---|---|---|---|---|
| `data/actions/*_historique.csv` (cours, volume en titres, volume en FCFA) | 2008-01-02 au 2026-10-07 | 48 titres (27 en 2008, 48 en 2026) | 4 786 séances ; environ 157 000 lignes titre-séance | Une ligne n'existe que les jours d'échange : 45 % des couples titre-séance possibles en 2008, 77 % en 2015, plus de 90 % depuis 2021. Valeur en FCFA cohérente avec titres × cours (rapport médian 1,00). |
| `data/indices/*_historique.csv` | 2008 à 2026 | BRVMC, BRVM30, indices sectoriels | | Volumes de BRVMC à zéro avant le 2014-08-07 : il faut reconstruire l'activité du marché à partir des titres, ce qui est de toute façon préférable. |
| `data/dividendes/dividendes.csv` | Exercices 2015 à 2025 | 332 lignes | 323 dates de détachement, dont 39 estimées | Pas de dividendes avant l'exercice 2015 : la saison des dividendes n'est mesurable que sur 2016-2026. Les dates estimées sont à contrôler (`brvm-data-quality`). |

**Valeur échangée par an (somme des titres, milliards de FCFA)** : 12,7 en 2008 ; entre 5 et 18 de 2009 à 2012 ; 131 en 2013 ; entre 90 et 180 de 2014 à 2024 ; 273 en 2025 ; 378 sur les neuf premiers mois de 2026.

**Deux défauts majeurs pour ce sujet :**

1. **Transactions de blocs.** En 2013, Sonatel représente 95 % de la valeur échangée, dont une seule séance (2013-04-26) à 40 milliards de FCFA, soit plus de trois fois la valeur de toute l'année 2008. Une moyenne de valeur échangée par mois serait faite par quelques séances. Il faut des mesures robustes (logarithme, médiane, rang, séances de blocs repérées et traitées à part) et le dire dans l'article.
2. **Concentration.** Le premier titre fait entre 60 et 95 % de la valeur échangée jusqu'en 2014, encore 19 à 42 % depuis 2021 ; les cinq premiers entre 41 et 99 %. Une saisonnalité « du marché » peut n'être que celle de Sonatel. Il faut des mesures par titre (rotation, part des titres échangés) et un panel, en plus des agrégats.

Observations réellement indépendantes :

- Pour un **effet mois**, l'unité est l'année : 12 ans homogènes (2014 à 2025, après le passage à la cotation en continu), soit 12 observations par mois, 18 en incluant la période du fixing.
- Pour un **effet jour de la semaine**, environ 2 500 séances depuis 2014, mais fortement autocorrélées (autocorrélation d'ordre 1 du logarithme de la valeur quotidienne : 0,79) : erreurs types de Newey-West indispensables.
- Pour la **saison des dividendes**, 10 saisons (2016 à 2025).
- Pour le **Ramadan**, 18 épisodes. Il recule d'environ 11 jours par an : de septembre en 2008 à février en 2026. Cela permet de le séparer en partie de l'effet mois, ce que la littérature sur marchés à date fixe ne peut pas faire. Atout pour l'étude.

## Littérature : premier balayage

- **Marchés développés et émergents** : les anomalies de calendrier portent surtout sur les rendements ; sur les volumes, les travaux sont moins nombreux et leurs résultats divergent. Exemples trouvés : volume plus faible le lundi et plus élevé le mercredi à Varsovie (Nowak et Olbryś) et en Indonésie (Azmi et Hasmita). Ces deux références restent à lire en entier.
- **Ramadan** : effet sur les rendements assez constant ; effet sur les volumes contesté. Bialkowski, Etebari et Wisniewski (2010, 14 pays) ne trouvent pas de différence de volume ; d'autres études (Koweït, Turquie, un panel de 17 marchés musulmans) trouvent une baisse. Pour la BRVM, la question est neuve : la part de la population musulmane varie fortement selon les huit pays de l'UEMOA.
- **Marchés africains** : Alagidede (2008) documente un effet mois sur les rendements de six marchés africains et prévient que la liquidité et les coûts empêchent de l'exploiter. Rien trouvé sur la saisonnalité des volumes.
- **BRVM** : effet jour de la semaine et effet mois sur les **rendements** (Ben Mrad Douagi, Chaouachi et Sow Mory, 2019 ; Ferrouhi et al., 2021, effet lundi et effet décembre) ; un travail de 2024 sur la volatilité. Sur la liquidité : rotation faible et flottant rare (Bayala et Bama, 2019), effet du passage à la cotation en continu (document RePEc, contenu non consulté). **Aucune étude trouvée sur la saisonnalité des volumes de la BRVM.**

Ces références viennent de résumés ou de pages de présentation ; la phase 2 les vérifiera et les lira.

## Puissance statistique

Calcul approché, à 5 % et 80 % de puissance, à partir de l'écart type des écarts mensuels du logarithme de la valeur échangée à sa moyenne mobile sur 12 mois (0,34 sur 2014-2025). Cet écart type inclut la saisonnalité elle-même : c'est une borne haute, donc une estimation prudente.

- **Un mois donné contre les autres** (12 observations) : effet minimal détectable d'environ 0,29 en logarithme, soit **±33 %** de valeur échangée. Avec correction de Holm sur 12 mois, environ ±45 %. Seuls des effets mensuels forts seront visibles.
- **Saison des dividendes contre le reste de l'année** (environ 4 mois par an sur 10 ans) : environ **±18 %**. Test bien plus puissant, à privilégier.
- **Jour de la semaine** et **Ramadan** : puissance correcte si l'on utilise les séances, sous réserve des erreurs types robustes.
- **Panel par titre** : gain de puissance réel mais limité, car les titres bougent ensemble (même marché, mêmes investisseurs) ; il faut des erreurs types groupées par date.

Nombre de tests envisagés : environ 5 familles (mois, jour, fin de mois, dividendes, Ramadan et fêtes), chacune sur 2 ou 3 mesures de volume. Il faudra limiter les hypothèses principales à 4 ou 5 et corriger pour tests multiples (Holm).

## Changements de fonctionnement du marché sur la période

| Date | Changement | Effet possible sur l'étude |
|---|---|---|
| 2013-09-16 | Passage du fixing à la cotation en continu | Rupture de niveau et de comportement des volumes ; l'échantillon principal commence en 2014. |
| 2013-03 et 2013-04 | Transactions de blocs sur Sonatel | Valeurs extrêmes, à traiter comme des séances exceptionnelles. |
| Depuis 2014 | Introductions en bourse (27 titres en 2008, 48 en 2026), dont de grandes capitalisations | Tendance de fond à retirer avant de chercher une saison. |
| 2020 | Bourse en ligne (étape citée par la BRVM) | Possible changement de la participation des particuliers. |
| À dater | Limite de variation de ±7,5 %, horaires de séance, jours fériés de chaque année, divisions du nominal (sans effet sur la valeur en FCFA, mais avec effet sur le nombre de titres) | À établir en phase 2 à partir des avis de la BRVM. |
| 2025-2026 | Forte hausse des volumes | Un nouveau régime en cours d'année : il pèserait sur les derniers mois s'il n'est pas retiré par la tendance. |

## Apport attendu

- **Pour la littérature** : à notre connaissance, aucune étude sur la saisonnalité des volumes de la BRVM. Le Ramadan, qui se déplace dans le calendrier sur un marché multinational à populations musulmanes inégales, est un cas d'identification que les marchés du Golfe n'offrent pas.
- **Pour la BRVM et les sociétés de gestion et d'intermédiation** : savoir quand la liquidité manque aide à planifier les opérations (introductions, cessions de blocs, rééquilibrages de portefeuille) et à fixer le calendrier des animations de marché.
- **Pour les investisseurs** : choisir le moment d'entrer ou de sortir d'une ligne peu liquide.
- **Pour l'application** : un calendrier de liquidité pourrait compléter le dimensionnement des positions (`position-sizing`), une fois l'étude publiée.

## Avis

**Poursuivre, avec une question recadrée.** Les données suffisent : 12 ans homogènes après la cotation en continu, 48 titres, un Ramadan qui se déplace. Mais trois conditions :

1. mesurer l'activité de façon robuste aux transactions de blocs et à la concentration (logarithme, médiane, nombre de titres échangés, rotation par titre), et non par la seule valeur échangée totale ;
2. retenir comme hypothèses principales les effets que la puissance permet de voir (saison des dividendes, jour de la semaine, Ramadan et fêtes, fin d'année) et traiter l'effet de chaque mois comme descriptif ;
3. séparer la période du fixing (2008 à 2013) de la période de cotation en continu (depuis 2014).

**Question recadrée proposée :** « Les volumes de la BRVM suivent-ils un calendrier ? Effets du jour de la semaine, de la saison des dividendes, du Ramadan et de la fin d'année sur l'activité d'échange, 2014-2026, mesurée de façon robuste aux transactions de blocs. »

## Questions à l'utilisateur

1. Validez-vous la question recadrée, ou souhaitez-vous garder l'effet de chaque mois comme hypothèse principale (au prix d'une faible puissance) ?
2. La période du fixing (2008 à 2013) : en annexe comme comparaison, ou écartée ?
3. Souhaitez-vous traiter les volumes en nombre de titres (sensibles aux divisions du nominal) en plus de la valeur en FCFA ? Je propose la valeur en FCFA et la rotation (titres échangés rapportés aux titres en circulation, si les données le permettent).
4. Faut-il étendre la phase 2 aux effets sur les rendements (littérature BRVM déjà existante), ou s'en tenir aux volumes ?
