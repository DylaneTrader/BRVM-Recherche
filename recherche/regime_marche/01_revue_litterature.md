# Revue de littérature : régime de marché de la BRVM par les moyennes mobiles

Date : 2026-10-22. État : brouillon, en attente de validation.

Objet de l'étude : la méthode de régime de l'application (`mm_50_200_filtre`) classe chaque séance d'un indice en six états à partir de trois comparaisons : prix et MM200, MM50 et MM200, prix et MM50. Chaque comparaison est filtrée par une bande de 1 % et trois séances de confirmation. S'y ajoute la participation MM200, c'est-à-dire la part des titres au-dessus de leur propre MM200. La revue rassemble ce que la littérature dit des questions que pose cette méthode : comment définir un régime, ce que valent les moyennes mobiles pour le repérer, ce qui suit un régime, et ce qui est connu de la BRVM.

Lecture : toutes les références ci-dessous ont été retrouvées par recherche en ligne (notice bibliographique et résumé). Aucun texte complet n'a été lu pendant cette phase. Les résultats attribués à chaque article sont ceux de son résumé ou de sa notice ; ils seront vérifiés sur le texte complet avant d'être cités dans l'article.

## 1. Définir et dater un marché haussier ou baissier

Deux familles de méthodes coexistent.

**Les règles de datation** repèrent des sommets et des creux, puis appellent phase haussière (ou baissière) le mouvement d'un creux à un sommet (ou l'inverse). Elles descendent de l'algorithme de Bry et Boschan (1971), conçu pour dater les cycles économiques. Pagan et Sossounov (2003) l'adaptent aux cours boursiers : durées minimales d'une phase et d'un cycle, et censure des extrémités de la série. Ils montrent par simulation qu'une simple marche aléatoire reproduit aussi bien les caractéristiques des phases observées que des modèles plus riches. Gonzalez, Powell, Shi et Wilson (2005) appliquent une procédure de ce type à deux siècles de données américaines. Les phases haussières et baissières y diffèrent nettement et durablement par leur rendement moyen : ils y voient des régimes de rendement distincts. Lunde et Timmermann (2004) définissent les phases comme des mouvements entre creux et sommets locaux. Ils modélisent la probabilité qu'une phase se termine en fonction de son âge et de variables d'état comme les taux d'intérêt, et rejettent la marche aléatoire pour les deux types de phase.

**Les modèles à changement de régime** traitent l'état du marché comme une variable cachée qui suit une chaîne de Markov (Hamilton, 1989). Maheu et McCurdy (2000) en tirent deux états sur plus de 160 ans de rendements mensuels : un état de rendement élevé et stable (haussier) et un état de rendement faible et volatil (baissier). Rydén, Teräsvirta et Åsbrink (1998) montrent qu'un modèle de Markov caché à mélange de lois normales reproduit la plupart des faits stylisés des rendements quotidiens. Shu, Yu et Mulvey (2024) proposent un modèle « à sauts » qui pénalise les changements d'état. Il limite les bascules trop fréquentes du modèle de Markov caché et, sur les indices américain, allemand et japonais de 1990 à 2023, réduit la volatilité et la perte maximale d'une stratégie qui sort du marché dans les états défavorables, frais et délais d'exécution compris.

**La comparaison des deux familles.** Kole et van Dijk (2017) confrontent les règles de datation et les modèles de Markov. Les règles sont préférables pour identifier l'état du marché sur l'échantillon. Les modèles de Markov sont préférables pour le prévoir hors échantillon, et la variance des rendements est un ingrédient essentiel de la prévision.

Ce qui est établi : les phases haussières et baissières existent, diffèrent par leur rendement et leur volatilité, et peuvent être datées de façon reproductible. Ce qui est contesté : leur durée a-t-elle un pouvoir prédictif (Pagan et Sossounov contre Lunde et Timmermann) ? Ce qui manque : une méthode à moyennes mobiles et plusieurs états intermédiaires, comme celle de l'application, n'est comparée nulle part à une datation de référence.

## 2. Les moyennes mobiles pour repérer la tendance

Brock, Lakonishok et LeBaron (1992) testent des règles de moyennes mobiles et de cassure de range sur le Dow Jones de 1897 à 1986. Les rendements qui suivent un signal d'achat sont plus élevés et moins volatils que ceux qui suivent un signal de vente, et cela ne s'explique ni par une marche aléatoire, ni par un AR(1), ni par des modèles GARCH-M ou EGARCH. L'application leur attribue sa bande de 1 % ; les réglages exacts de l'étude (longueurs des moyennes, bande) restent à vérifier sur le texte complet.

Ce résultat a été contesté sur trois points.

- **Le biais de sélection des règles.** Sullivan, Timmermann et White (1999) reprennent les 26 règles de Brock et al. en élargissant leur univers, sur cent ans de données quotidiennes du Dow Jones, avec le test « Reality Check » de White qui corrige la multiplicité des règles essayées. Leurs conclusions précises, notamment hors de l'échantillon d'origine, restent à lire sur le texte complet.
- **La performance réelle.** Zakamulin (2014) teste hors échantillon des règles de moyenne mobile et de momentum, avec des coûts de transaction réalistes. La performance publiée y apparaît fortement surestimée, du fait du biais de sélection et des frictions ignorées.
- **La mise en œuvre.** Faber (2007) popularise la règle des dix mois (environ 200 séances) appliquée à plusieurs classes d'actifs. Il s'agit d'un article de praticien, sans test statistique formel.

Plusieurs travaux expliquent ce que mesurent ces règles. Marshall, Nguyen et Visaltanachoti (2017) montrent que le momentum de série temporelle et les moyennes mobiles sont proches : les signaux du premier coïncident avec un changement de direction de la moyenne mobile, et les moyennes mobiles donnent souvent des signaux plus tôt. Moskowitz, Ooi et Pedersen (2012) documentent la persistance des rendements d'un à douze mois sur 58 contrats à terme, suivie d'un retournement partiel. Han, Yang et Zhou (2013) trouvent qu'une règle de moyenne mobile appliquée à des portefeuilles triés par volatilité bat nettement l'achat-conservation, surtout pour les titres les plus volatils.

Sur les marchés émergents, Fifield, Power et Knipe (2008) testent des règles de moyennes mobiles sur 15 marchés émergents et 3 marchés développés de 1989 à 2003. Les règles y sont plus rentables sur les indices émergents, y compris avec des moyennes longues, ce que les auteurs lisent comme le signe de tendances plus fortes et plus persistantes.

Ce qui est établi : les moyennes mobiles décrivent la tendance et ont, au moins sur certaines périodes, séparé des états de rendement différents. Ce qui est contesté : leur pouvoir hors échantillon, une fois corrigé le biais de sélection et déduits les frais. Ce qui manque : aucune étude retrouvée ne teste ces règles sur la BRVM.

## 3. Ce qui suit un régime

Les résultats précédents portent surtout sur la performance d'une stratégie. Pour l'étude, la question est plutôt celle du contenu informatif d'un état : que se passe-t-il, en moyenne, après une séance classée dans tel régime ?

- **La persistance des états.** Maheu et McCurdy (2000) trouvent que la probabilité de fin d'un marché haussier diminue avec son âge, et que les meilleurs gains surviennent au début des phases haussières. Lunde et Timmermann (2004) trouvent que la hausse des taux d'intérêt réduit la probabilité de fin d'un marché baissier.
- **L'effet de l'état du marché sur d'autres anomalies.** Cooper, Gutierrez et Hameed (2004) montrent que les profits du momentum entre titres dépendent de l'état du marché : environ 0,93 % par mois après des rendements de marché positifs, environ -0,37 % après des rendements négatifs (1929-1995).
- **Les conséquences pour l'allocation.** Ang et Bekaert (2002) modélisent les opportunités d'investissement d'un investisseur américain par un processus à changement de régime : la diversification internationale garde sa valeur malgré les changements de régime.

Ce qui manque : les horizons qui suivent un état se recouvrent, et le nombre d'épisodes indépendants est faible. Aucune des références retrouvées ne traite ce problème pour une classification en six états.

## 4. La participation des titres (largeur du marché)

La participation MM200 de l'application suit une tradition de praticiens : indicateurs de largeur, ligne des hausses et des baisses, part des titres au-dessus de leur moyenne. La revue n'a pas retrouvé d'étude académique publiée qui valide la part des titres au-dessus de leur MM200 comme mesure de la solidité d'une tendance.

Deux pistes ont été repérées, mais ne sont pas citées tant qu'elles ne sont pas lues (voir « À confirmer ») : un article récent du *Journal of Investing* sur les ratios de largeur et la part des titres au-dessus d'une moyenne, et l'ouvrage de praticien de Zweig (1986). Côté BRVM, l'étude Fear & Greed de ce dépôt (`../fear_greed/`, hypothèse H3) a montré qu'une mesure voisine, la part des titres au-dessus de leur MM50, apporte une information propre sur un marché concentré.

## 5. Sur la BRVM et les marchés frontières africains

- **Efficience.** Tan Toe, Toe et Zoungrana (2023), sur les données de 1998 à 2020, et Houndalidji, Tchindro et Hounkou (2024), sur 1 618 séances de 2016 à 2022, concluent que la BRVM n'est pas efficiente au sens faible. Les rendements passés y contiennent donc de l'information, ce qui laisse une place à une lecture par la tendance.
- **Volatilité et volume.** N'dri (2007), sur les données quotidiennes de 2002 à 2005, montre que le volume aide à prévoir la volatilité des rendements.
- **Régimes sur un marché africain.** Barngetuny (2026) estime un modèle de Markov à deux états sur l'indice de la bourse de Nairobi de 2005 à 2025. Le régime haussier y a des rendements plus élevés et une volatilité plus faible, et il dure plus longtemps que le régime baissier. Aucune étude comparable n'a été retrouvée sur la BRVM.
- **Échanges non synchrones.** Lo et MacKinlay (1990) montrent que des titres qui ne s'échangent pas chaque jour créent une autocorrélation positive des rendements d'un indice. Sur la BRVM, une part de la persistance des tendances, et donc des régimes, peut venir de ce mécanisme et non du comportement des investisseurs.

Limites : les travaux sur la BRVM portent sur l'efficience ou la volatilité, avec des tests globaux. Aucun ne définit ni ne valide un régime de marché.

## 6. Écart comblé par l'étude

1. **Aucune étude ne caractérise les régimes de marché de la BRVM.** L'étude serait la première à les dater, à décrire leur durée, leur fréquence et ce qui les suit, sur un marché frontière peu liquide et concentré.
2. **La méthode à six états et à filtres n'a jamais été validée.** La littérature valide des règles à deux états (au-dessus ou en dessous d'une moyenne) ou des modèles de Markov. Elle ne dit rien d'une classification intermédiaire (Correction, Rebond, Transitions), ni de l'effet de la bande et de la confirmation sur le nombre de faux signaux.
3. **La comparaison avec les méthodes de référence manque.** Il reste à confronter le régime par moyennes mobiles à une datation de type Pagan et Sossounov et à un modèle de Markov ou à sauts, selon le cadre de Kole et van Dijk (2017).
4. **La participation n'a pas de validation académique.** L'étude peut tester si la participation MM200 change ce qui suit un régime.
5. **La part de la persistance due à l'illiquidité** n'est pas mesurée : séparer l'effet des échanges non synchrones de celui des tendances serait un apport en soi.

## 7. Méthodes recommandées

- **Datation de référence** : algorithme de Pagan et Sossounov (2003), dérivé de Bry et Boschan (1971), pour obtenir des phases haussières et baissières indépendantes de la méthode étudiée.
- **Cadre d'évaluation** : séparer l'identification sur l'échantillon et la prévision hors échantillon, comme Kole et van Dijk (2017), avec un modèle de Markov (Hamilton, 1989 ; Maheu et McCurdy, 2000) et un modèle à sauts (Shu, Yu et Mulvey, 2024) comme concurrents.
- **Inférence sur ce qui suit un régime** : bootstrap sous des modèles nuls (marche aléatoire, AR(1), GARCH), comme Brock et al. (1992). Erreurs types robustes au recouvrement des horizons. Correction du biais de sélection si plusieurs réglages sont comparés (Reality Check, Sullivan, Timmermann et White, 1999).
- **Contrôle de l'illiquidité** : comparer l'indice publié, un indice limité aux titres liquides et des rendements hebdomadaires. Lo et MacKinlay (1990) donnent l'ordre de grandeur de l'autocorrélation due aux échanges non synchrones.
- **Puissance statistique** : compter les épisodes indépendants de chaque régime, pas les séances. Avec une vingtaine d'années de données, certains régimes (Transitions) auront peu d'épisodes : à dire avant tout test.
- **Frais et exécution** : si l'étude évalue une stratégie, l'exécuter en J+1 et déduire les frais, comme le montre Zakamulin (2014).

## Références

| Référence complète | DOI ou lien | Lu | Ce qu'elle apporte à l'étude |
|---|---|---|---|
| Ang, A. et Bekaert, G. (2002). « International asset allocation with regime shifts ». *Review of Financial Studies*, 15(4), 1137-1187. | https://ideas.repec.org/a/oup/rfinst/v15y2002i4p1137-1187.html | Résumé | Conséquences des régimes pour l'allocation |
| Barngetuny, J. (2026). « Modelling bullish and bearish market regimes at the Nairobi Securities Exchange: a Markov regime-switching approach ». *International Journal of Finance and Accounting*, 5(1), 275-298. | https://doi.org/10.37284/ijfa.5.1.5092 | Résumé | Seule application retrouvée sur un marché africain |
| Brock, W., Lakonishok, J. et LeBaron, B. (1992). « Simple technical trading rules and the stochastic properties of stock returns ». *Journal of Finance*, 47(5), 1731-1764. | https://ideas.repec.org/a/bla/jfinan/v47y1992i5p1731-64.html | Résumé | Moyennes 50 et 200 jours, bande de 1 %, bootstrap sous modèles nuls |
| Bry, G. et Boschan, C. (1971). *Cyclical Analysis of Time Series: Selected Procedures and Computer Programs*. NBER Technical Paper 20, Columbia University Press. | https://ideas.repec.org/b/nbr/nberbk/bry_71-1.html | Table des matières | Algorithme de datation des sommets et des creux |
| Cooper, M. J., Gutierrez, R. C. et Hameed, A. (2004). « Market states and momentum ». *Journal of Finance*, 59(3), 1345-1365. | https://doi.org/10.1111/j.1540-6261.2004.00665.x | Résumé | L'état du marché conditionne d'autres effets |
| Faber, M. T. (2007). « A quantitative approach to tactical asset allocation ». *Journal of Wealth Management*, 9(4). | https://ritholtz.com/2012/01/revisiting-quant-approach-to-tactical-asset-allocation (mise à jour de l'auteur) | Résumé | Règle des dix mois ; article de praticien |
| Fifield, S. G. M., Power, D. M. et Knipe, D. G. S. (2008). « The performance of moving average rules in emerging stock markets ». *Applied Financial Economics*, 18(19), 1515-1532. | https://doi.org/10.1080/09603100701720302 | Résumé | Moyennes mobiles plus rentables sur les marchés émergents |
| Gonzalez, L., Powell, J. G., Shi, J. et Wilson, A. (2005). « Two centuries of bull and bear market cycles ». *International Review of Economics and Finance*, 14(4), 469-486. | https://ideas.repec.org/a/eee/reveco/v14y2005i4p469-486.html | Résumé | Datation par points de retournement ; régimes de rendement distincts |
| Hamilton, J. D. (1989). « A new approach to the economic analysis of nonstationary time series and the business cycle ». *Econometrica*, 57(2), 357-384. | https://ideas.repec.org/a/ecm/emetrp/v57y1989i2p357-84.html | Résumé | Modèle à changement de régime markovien |
| Han, Y., Yang, K. et Zhou, G. (2013). « A new anomaly: the cross-sectional profitability of technical analysis ». *Journal of Financial and Quantitative Analysis*, 48(5), 1433-1461. | https://ideas.repec.org/a/cup/jfinqa/v48y2013i05p1433-1461_00.html | Résumé | Moyennes mobiles et volatilité des titres |
| Houndalidji, Y. H. E., Tchindro, G. R. et Hounkou, C. E. (2024). « The efficiency of BRVM tested by the facts: analysis of past share prices ». *Journal of Financial Risk Management*, 13(4), 769-797. | https://dspace.uac.bj/handle/123456789/14539 | Résumé | Inefficience faible de la BRVM, 2016-2022 |
| Kole, E. et van Dijk, D. (2017). « How to identify and forecast bull and bear markets? ». *Journal of Applied Econometrics*, 32(1), 120-139. | https://doi.org/10.1002/jae.2511 | Résumé | Règles pour identifier, Markov pour prévoir ; cadre d'évaluation |
| Lo, A. W. et MacKinlay, A. C. (1990). « An econometric analysis of nonsynchronous trading ». *Journal of Econometrics*, 45(1-2), 181-211. | https://ideas.repec.org/a/eee/econom/v45y1990i1-2p181-211.html | Résumé | Autocorrélation mécanique d'un indice peu liquide |
| Lunde, A. et Timmermann, A. (2004). « Duration dependence in stock prices: an analysis of bull and bear markets ». *Journal of Business & Economic Statistics*, 22(3), 253-273. | https://cepr.org/publications/DP4104 (version de travail) | Résumé | Datation par seuils ; dépendance à la durée |
| Maheu, J. M. et McCurdy, T. H. (2000). « Identifying bull and bear markets in stock returns ». *Journal of Business & Economic Statistics*, 18(1), 100-112. | https://doi.org/10.2307/1392140 | Résumé | Deux états de Markov ; dépendance à la durée |
| Marshall, B. R., Nguyen, N. H. et Visaltanachoti, N. (2017). « Time series momentum and moving average trading rules ». *Quantitative Finance*, 17(3), 405-421. | https://doi.org/10.1080/14697688.2016.1205209 | Résumé | Lien entre moyennes mobiles et momentum de série temporelle |
| Moskowitz, T. J., Ooi, Y. H. et Pedersen, L. H. (2012). « Time series momentum ». *Journal of Financial Economics*, 104(2), 228-250. | https://doi.org/10.1016/j.jfineco.2011.11.003 | Résumé | Persistance des tendances d'un à douze mois |
| N'dri, K. L. (2007). « An empirical study of the relation between stock return volatility and trading volume in the BRVM ». *African Journal of Business Management*, 1(5), 107-112. | https://academicjournals.org/journal/AJBM/article-abstract/7B75A0417552 | Résumé | Volume et volatilité sur la BRVM |
| Pagan, A. R. et Sossounov, K. A. (2003). « A simple framework for analysing bull and bear markets ». *Journal of Applied Econometrics*, 18(1), 23-46. | https://eprints.qut.edu.au/8045 | Résumé | Algorithme de datation de référence |
| Rydén, T., Teräsvirta, T. et Åsbrink, S. (1998). « Stylized facts of daily return series and the hidden Markov model ». *Journal of Applied Econometrics*, 13(3), 217-244. | https://ideas.repec.org/a/jae/japmet/v13y1998i3p217-244.html | Résumé | Modèle de Markov caché sur données quotidiennes |
| Shu, Y., Yu, C. et Mulvey, J. M. (2024). « Downside risk reduction using regime-switching signals: a statistical jump model approach ». *Journal of Asset Management*, 25(5), 493-507. | https://doi.org/10.1057/s41260-024-00376-x | Résumé | Modèle à sauts : des régimes persistants |
| Sullivan, R., Timmermann, A. et White, H. (1999). « Data-snooping, technical trading rule performance, and the bootstrap ». *Journal of Finance*, 54(5), 1647-1691. | https://doi.org/10.1111/0022-1082.00163 | Résumé | Correction du biais de sélection des règles |
| Tan Toe, D. L., Toe, M. et Zoungrana, T. D. (2023). « Investigating the weak and semi-strong forms of informational efficiency on the West African Economic and Monetary Union's stock exchange (BRVM) through returns predictability tests ». *SN Business & Economics*, 3(9). | https://doi.org/10.1007/s43546-023-00550-0 | Résumé | Inefficience faible de la BRVM, 1998-2020 |
| Zakamulin, V. (2014). « The real-life performance of market timing with moving average and time-series momentum rules ». *Journal of Asset Management*, 15(4). | https://doi.org/10.1057/jam.2014.25 | Résumé | Performance surestimée ; frais et biais de sélection |

Pages à vérifier sur le texte complet : Faber (2007) et Zakamulin (2014), dont les notices consultées ne donnent pas les pages.

## À confirmer

Références repérées mais pas encore vérifiées ou pas encore lues ; elles ne sont pas citées.

- Zweig, M. (1986). *Winning on Wall Street*. Warner Books. Ouvrage de praticien sur la largeur du marché ; édition et contenu à vérifier.
- Yu, Webb et Lin (2025), *Journal of Investing*, 34(2) : ratios de largeur, TRIN et part des titres au-dessus d'une moyenne mobile. Notice vue, résultats non lus.
- Nystrup, P., Lindström, E. et Madsen, H. : estimation des modèles de Markov caché par pénalisation des sauts. Revue et DOI non retrouvés.
- Cruz, Nicolau et Rodrigues (2021), *Asia-Pacific Financial Markets* : durée des marchés haussiers dans 18 économies développées et émergentes. Notice non consultée.
- Zakamulin, V. (2017). *Market Timing with Moving Averages: The Anatomy and Performance of Trading Rules*. Palgrave Macmillan. Ouvrage, édition à vérifier.
