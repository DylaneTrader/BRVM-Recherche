# Revue de littérature : de combien un backtest naïf surestime-t-il une stratégie sur la BRVM ?

Date : 2026-10-23. État : brouillon, en attente de validation.

Question posée : un moteur de backtest n'est qu'un outil. La question de recherche est l'écart entre la performance d'une stratégie simulée naïvement et celle qu'elle aurait réellement obtenue sur la BRVM, et la part de cet écart due à chaque contrainte :

- le délai d'exécution ;
- la limite de variation de ±7,5 % par séance ;
- les séances sans échange ;
- les frais ;
- le traitement des dividendes et des divisions du nominal.

Lecture : toutes les références ci-dessous ont été retrouvées par recherche en ligne (notice bibliographique et résumé). Aucun texte complet n'a été lu pendant cette phase. Les résultats attribués à chaque article sont ceux de son résumé ou de sa notice ; ils seront vérifiés sur le texte complet avant d'être cités dans l'article.

**Précision sur le délai.** Deux délais se distinguent sur la BRVM. L'**exécution** : un signal calculé sur la clôture de J ne peut être exécuté qu'en J+1 au plus tôt (c'est la règle de l'application). Le **règlement-livraison** : le Dépositaire central / Banque de règlement est passé de J+3 à J+2 le 4 décembre 2025, après approbation de son conseil d'administration le 21 octobre 2025 ; il était en J+7 à la fin des années 1990 et en J+3 depuis 2007. Le règlement-livraison retarde la disponibilité des espèces et des titres, donc le réinvestissement ; l'exécution retarde le prix obtenu. L'étude devra mesurer les deux effets séparément, avec un cycle qui a changé pendant la période.

## 1. L'écart entre le papier et la réalité

Perold (1988) définit l'« implementation shortfall » : l'écart entre la performance d'un portefeuille théorique (« sur le papier ») et celle du portefeuille réellement échangé. D'après les sources secondaires consultées, cet écart comprend, au-delà des frais, le coût des ordres retardés ou non exécutés ; le texte reste à lire. C'est la mesure que l'étude cherche, décomposée par contrainte.

## 2. Le biais de sélection : essayer beaucoup de stratégies

- White (2000) propose le « Reality Check » : tester si la meilleure de nombreuses spécifications bat vraiment un modèle de référence.
- Sullivan, Timmermann et White (1999) l'appliquent aux règles techniques de Brock, Lakonishok et LeBaron (1992), sur cent ans de données du Dow Jones.
- Harvey, Liu et Zhu (2016) montrent qu'avec les centaines de facteurs testés, un nouveau facteur devrait franchir un t de Student supérieur à 3.
- Harvey et Liu (2015) en tirent une décote du ratio de Sharpe d'un backtest selon le nombre d'essais. La décote n'est pas linéaire, et la règle empirique d'une décote de 50 % est jugée fausse.
- Bailey et López de Prado (2014) proposent le ratio de Sharpe dégonflé, qui corrige à la fois le biais de sélection et la non-normalité des rendements.
- Bailey, Borwein, López de Prado et Zhu (2017) définissent la probabilité de surapprentissage d'un backtest (PBO), estimée par validation croisée combinatoire, et jugent la simple mise de côté d'un échantillon peu fiable pour les backtests.

Ce biais ne dépend pas des contraintes de marché, mais il s'y ajoute : un backtest naïf est à la fois trop optimiste sur l'exécution et sélectionné parmi d'autres.

## 3. Les frais et la liquidité

- **Estimer les coûts sans données de carnet.** Lesmond, Ogden et Trzcinka (1999) estiment les coûts de transaction à partir de la seule fréquence des rendements nuls. De 1963 à 1990, ils trouvent des coûts aller-retour d'environ 1,2 % pour les plus grandes capitalisations et 10,3 % pour les plus petites. Lesmond (2005) étend ces mesures aux marchés émergents : les coûts de liquidité y vont d'environ 1 % (Taïwan) à plus de 47 % (Russie), et les mesures fondées sur les prix comparent mieux les pays que celles fondées sur le volume.
- **Les coûts effacent une partie des anomalies.** Korajczyk et Sadka (2004) calculent la taille de fonds au-delà de laquelle le momentum cesse d'être rentable, une fois l'impact sur les prix pris en compte ; les stratégies équipondérées, les meilleures avant frais, sont les pires après. Novy-Marx et Velikov (2016) trouvent que la plupart des anomalies dont la rotation mensuelle est inférieure à 50 % restent rentables nettes de frais si les échanges sont conçus pour limiter les coûts, et peu des autres.
- **Sur les marchés frontières.** de Groot, Pang et Swinkels (2012), sur plus de 1 400 titres de 24 marchés frontières de 1997 à 2008, trouvent que les effets valeur et momentum subsistent avec des hypothèses de coûts prudentes.

## 4. Le délai d'exécution et l'anticipation

Zakamulin (2018) montre que la performance remarquable d'une stratégie de moyenne mobile publiée auparavant venait d'une simulation qui utilisait une information pas encore disponible : sans ce biais d'anticipation, la stratégie fait à peine mieux que l'achat-conservation. C'est l'erreur la plus simple d'un backtest naïf : décider et exécuter au même cours de clôture.

## 5. La limite de variation

Kim et Rhee (1997), à la bourse de Tokyo, testent trois effets reprochés aux limites de variation : elles reportent la volatilité sur les séances suivantes, retardent la découverte du prix et gênent les échanges. Les trois hypothèses sont confirmées. Pour un backtest, cela signifie qu'un ordre décidé un jour de limite peut ne pas être exécuté, ou l'être plus tard à un autre prix, et que le cours de clôture d'une séance à la limite n'est pas un prix auquel on peut acheter ou vendre la quantité voulue.

## 6. Les séances sans échange

Lo et MacKinlay (1990) montrent que les échanges non synchrones créent une autocorrélation positive des rendements d'un indice. Un backtest qui exécute au cours affiché un jour sans échange suppose une contrepartie qui n'existait pas. Lesmond, Ogden et Trzcinka (1999) font des rendements nuls un indicateur de coût de transaction.

## 7. Les données : survivants, radiations, opérations sur titres

- **Survivants.** Brown, Goetzmann, Ibbotson et Ross (1992) montrent qu'un échantillon limité aux survivants crée une persistance apparente des performances.
- **Radiations.** Shumway (1997) montre que les rendements de radiation manquent pour la plupart des radiations négatives dans la base CRSP depuis 1962, et que leur omission est importante.
- **Qualité des données.** Ince et Porter (2006) montrent que des données de rendement non filtrées (Thomson Datastream) peuvent fausser les conclusions, et que des filtres les rapprochent d'une base de référence.

Pour la BRVM, l'application a ses propres contrôles : divisions du nominal datées par la première séance où le cours est divisé, dividendes au nominal actuel, montants écartés quand ils sont incohérents avec les cours. Un backtest naïf qui prend les cours sans ajustement fait d'une division une chute, et ignore les dividendes ou les crédite à une mauvaise date.

## 8. Sur la BRVM et les marchés frontières

- Le règlement général de la BRVM fixe la limite de variation des cours.
- Le règlement-livraison est passé de J+3 à J+2 le 4 décembre 2025 (voir l'introduction).
- La BRVM est jugée inefficiente au sens faible par Tan Toe, Toe et Zoungrana (2023) et Houndalidji, Tchindro et Hounkou (2024), références vérifiées dans la revue du régime de marché (`../regime_marche/`) : des stratégies simples y ont donc une chance d'être rentables avant frais.
- Fifield, Power et Knipe (2008) trouvent les règles de moyennes mobiles plus rentables sur les marchés émergents (même revue).

Aucune étude retrouvée ne mesure, sur la BRVM ou sur un autre marché africain, l'effet des contraintes de marché sur la performance simulée d'une stratégie.

## 9. Écart comblé par l'étude

1. **Aucune étude ne décompose l'écart entre backtest naïf et backtest réaliste par contrainte**, et l'ordre dans lequel on ajoute les contraintes change la part attribuée à chacune.
2. **La limite de variation et les séances sans échange** sont étudiées pour leurs effets sur les prix, pas pour leur effet sur la performance simulée d'une stratégie.
3. **Le changement du cycle de règlement-livraison** (J+3 puis J+2) n'a pas été étudié pour son effet sur la rotation possible d'une stratégie.
4. **Sur un marché frontière d'Afrique de l'Ouest**, rien n'a été publié.

## 10. Méthodes recommandées

- **Décomposition** : partir du backtest naïf et ajouter une contrainte à la fois, dans tous les ordres possibles, puis attribuer à chaque contrainte sa contribution moyenne (décomposition de type Shapley), pour que le résultat ne dépende pas de l'ordre choisi.
- **Plusieurs familles de stratégies** : tendance, retour à la moyenne, allocation, rotations faible et forte, puisque l'effet des frais dépend de la rotation (Novy-Marx et Velikov, 2016).
- **Coûts** : barème réel des frais de la BRVM, plus un coût de liquidité estimé à partir des rendements nuls (Lesmond et al., 1999 ; Lesmond, 2005) ; sensibilité aux hypothèses.
- **Exécution** : J+1 au plus tôt, les seuls jours d'échange, avec une participation maximale au volume ; ordres non exécutés aux séances à la limite (Kim et Rhee, 1997).
- **Règlement-livraison** : espèces et titres disponibles en J+3 avant le 4 décembre 2025, en J+2 ensuite.
- **Données** : cours ajustés des divisions, dividendes crédités à la date de paiement, titres radiés gardés (Brown et al., 1992 ; Shumway, 1997).
- **Inférence** : ratio de Sharpe dégonflé et probabilité de surapprentissage pour les stratégies sélectionnées (Bailey et López de Prado, 2014 ; Bailey et al., 2017), décote de Harvey et Liu (2015) ; écart naïf moins réaliste estimé par bootstrap.

## Références

| Référence complète | DOI ou lien | Lu | Ce qu'elle apporte à l'étude |
|---|---|---|---|
| Bailey, D. H., Borwein, J. M., López de Prado, M. et Zhu, Q. J. (2017). « The probability of backtest overfitting ». *Journal of Computational Finance*, 20(4). | https://doi.org/10.21314/JCF.2016.322 | Résumé | Probabilité de surapprentissage d'un backtest |
| Bailey, D. H. et López de Prado, M. (2014). « The deflated Sharpe ratio: correcting for selection bias, backtest overfitting, and non-normality ». *Journal of Portfolio Management*, 40(5), 94-107. | https://doi.org/10.3905/jpm.2014.40.5.094 | Résumé | Ratio de Sharpe dégonflé |
| Brown, S. J., Goetzmann, W., Ibbotson, R. G. et Ross, S. A. (1992). « Survivorship bias in performance studies ». *Review of Financial Studies*, 5(4), 553-580. | https://doi.org/10.1093/rfs/5.4.553 | Résumé | Biais du survivant |
| DC/BR, Dépositaire central / Banque de règlement (2025). Passage du cycle de règlement-livraison de J+3 à J+2, approuvé le 21 octobre 2025, effectif le 4 décembre 2025. Communiqué relayé par la presse financière. | https://www.african-markets.com/fr/bourse/brvm/apres-la-bourse-du-nigeria-la-brvm-bascule-a-son-tour-au-reglement-livraison-t-2-des-le-4-decembre-2025 | Article de presse | Changement du cycle de règlement pendant la période |
| de Groot, W., Pang, J. et Swinkels, L. (2012). « The cross-section of stock returns in frontier emerging markets ». *Journal of Empirical Finance*, 19(5), 796-818. | https://doi.org/10.1016/j.jempfin.2012.08.007 | Résumé | Anomalies et frais sur les marchés frontières |
| Harvey, C. R. et Liu, Y. (2015). « Backtesting ». *Journal of Portfolio Management*, 41(1), 13-28. | https://people.duke.edu/~charvey/Research/Published_Papers/P120_Backtesting.PDF | Résumé | Décote du Sharpe selon le nombre d'essais |
| Harvey, C. R., Liu, Y. et Zhu, H. (2016). « ... and the cross-section of expected returns ». *Review of Financial Studies*, 29(1), 5-68. | https://doi.org/10.1093/rfs/hhv059 | Résumé | Tests multiples, seuil de t > 3 |
| Ince, O. S. et Porter, R. B. (2006). « Individual equity return data from Thomson Datastream: handle with care! ». *Journal of Financial Research*, 29(4), 463-479. | https://doi.org/10.1111/j.1475-6803.2006.00189.x | Résumé | Erreurs de données et filtres |
| Kim, K. A. et Rhee, S. G. (1997). « Price limit performance: evidence from the Tokyo Stock Exchange ». *Journal of Finance*, 52(2), 885-901. | https://doi.org/10.1111/j.1540-6261.1997.tb04827.x | Résumé | Effets des limites de variation |
| Korajczyk, R. A. et Sadka, R. (2004). « Are momentum profits robust to trading costs? ». *Journal of Finance*, 59(3), 1039-1082. | https://doi.org/10.1111/j.1540-6261.2004.00656.x | Résumé | Taille de fonds et coûts d'impact |
| Lesmond, D. A. (2005). « Liquidity of emerging markets ». *Journal of Financial Economics*, 77(2), 411-452. | https://doi.org/10.1016/j.jfineco.2004.01.005 | Résumé | Coûts de liquidité des marchés émergents |
| Lesmond, D. A., Ogden, J. P. et Trzcinka, C. A. (1999). « A new estimate of transaction costs ». *Review of Financial Studies*, 12(5), 1113-1141. | https://ideas.repec.org/a/oup/rfinst/v12y1999i5p1113-41.html | Résumé | Coûts estimés par les rendements nuls |
| Lo, A. W. et MacKinlay, A. C. (1990). « An econometric analysis of nonsynchronous trading ». *Journal of Econometrics*, 45(1-2), 181-211. | https://ideas.repec.org/a/eee/econom/v45y1990i1-2p181-211.html | Résumé | Séances sans échange |
| Novy-Marx, R. et Velikov, M. (2016). « A taxonomy of anomalies and their trading costs ». *Review of Financial Studies*, 29(1), 104-147. | https://doi.org/10.1093/rfs/hhv063 | Résumé | Rotation et frais |
| Perold, A. F. (1988). « The implementation shortfall: paper versus reality ». *Journal of Portfolio Management*, 14(3), 4-9. | https://www.proquest.com/docview/195579087 (notice) | Notice | Écart entre portefeuille théorique et réel |
| Shumway, T. (1997). « The delisting bias in CRSP data ». *Journal of Finance*, 52(1), 327-340. | https://ideas.repec.org/a/bla/jfinan/v52y1997i1p327-40.html | Résumé | Rendements de radiation manquants |
| Sullivan, R., Timmermann, A. et White, H. (1999). « Data-snooping, technical trading rule performance, and the bootstrap ». *Journal of Finance*, 54(5), 1647-1691. | https://doi.org/10.1111/0022-1082.00163 | Résumé | Biais de sélection des règles techniques |
| White, H. (2000). « A reality check for data snooping ». *Econometrica*, 68(5), 1097-1126. | https://doi.org/10.1111/1468-0262.00152 | Résumé | Test de la meilleure spécification |
| Zakamulin, V. (2018). « Revisiting the profitability of market timing with moving averages ». *International Review of Finance*, 18(2), 317-327. | https://doi.org/10.1111/irfi.12132 | Résumé | Biais d'anticipation dans un backtest publié |

Références communes avec la revue du régime de marché, déjà vérifiées : Brock, Lakonishok et LeBaron (1992) ; Fifield, Power et Knipe (2008) ; Tan Toe, Toe et Zoungrana (2023) ; Houndalidji, Tchindro et Hounkou (2024). Le règlement général de la BRVM (2022), articles 35 et 65, est cité avec son lien dans l'article Fear & Greed (`../fear_greed/article.py`).

Détails à vérifier : pages de Kim et Rhee (885-899 ou 885-901) et de Harvey, Liu et Zhu (5-68 ou 5-72) ; année de Bailey et al. (2016 ou 2017).

## À confirmer

Références repérées mais pas encore vérifiées ou pas encore lues ; elles ne sont pas citées.

- Adcock, Ye, Yin et al. (2019), *Journal of the Operational Research Society* : limites de variation et retard de la découverte du prix sur les actions chinoises. DOI non retrouvé.
- Qi (2023), *PLoS ONE* : limites de variation sur le marché ChiNext après la réforme de 2020. https://ideas.repec.org/a/plo/pone00/0287548.html
- Les textes officiels du DC/BR et de l'AMF-UMOA sur le passage à J+2 (vus seulement dans la presse).
- Le barème des commissions de la BRVM, du DC/BR et de l'AMF-UMOA, et les courtages des SGI : à relever dans les textes en vigueur pour l'étude.
