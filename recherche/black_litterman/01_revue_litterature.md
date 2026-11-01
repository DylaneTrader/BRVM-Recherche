# Revue de littérature : le modèle Black-Litterman sur la BRVM

Date : 2026-11-01. État : premier brouillon, en attente de validation. La phase 1 est validée (2026-11-01) sans changement de la question.

Question de travail (voir `00_pertinence.md`) : une allocation Black-Litterman fait-elle mieux, nette des frais et exécutée de façon réaliste, que les parts égales et que la pondération par la capitalisation flottante sur les actions de la BRVM, et d'où vient l'écart : de l'a priori, des vues ou de la rotation ?

Lecture : toutes les références ci-dessous ont été retrouvées par recherche en ligne le 01/11/2026 (notice bibliographique, résumé ou présentation du texte par une source secondaire). **Aucun texte complet n'a encore été lu.** Les résultats attribués à chaque article sont ceux de son résumé ou de sa notice ; ils seront vérifiés sur le texte complet avant d'être cités dans l'article.

## 1. Le problème que le modèle veut résoudre : l'instabilité de l'optimisation moyenne-variance

- Michaud (1989) qualifie l'optimisation de Markowitz d'« énigme » : l'optimiseur maximise les erreurs d'estimation et surpondère les titres dont le rendement est surestimé.
- Best et Grauer (1991) montrent que les poids d'un portefeuille efficient sont très sensibles à de petites variations des rendements espérés.
- Chopra et Ziemba (1993) concluent, d'après les sources secondaires consultées, que les erreurs sur les moyennes coûtent environ dix fois plus que les erreurs sur les variances, et davantage encore que celles sur les covariances. Une reprise suédoise de leur protocole juge cet effet surestimé : le chiffre ne sera cité qu'après lecture du texte.
- DeMiguel, Garlappi et Uppal (2009) comparent quatorze modèles d'allocation à la règle des parts égales (1/N) sur sept jeux de données : aucun ne la bat de façon régulière, en ratio de Sharpe, en équivalent certain ou en rotation. La fenêtre d'estimation nécessaire pour qu'une optimisation l'emporte se compte en milliers de mois.

Conséquence pour l'étude : les parts égales sont la référence à battre, pas l'indice BRVMC. L'évaluation exploratoire du tableau de bord va dans ce sens (29 % par an pour les parts égales contre 17 % pour Black-Litterman), mais elle ne compte pas comme preuve (voir `00_pertinence.md`).

## 2. Le modèle : a priori d'équilibre, vues et confiance

- **Origine.** Black et Litterman (1991, 1992) proposent de partir des rendements implicites de l'équilibre du marché (ceux qui rendent optimal le portefeuille de marché) et de les déplacer dans la direction des vues de l'investisseur, chacune avec sa confiance. Le résultat est un portefeuille proche du marché, qui ne s'en écarte que là où l'investisseur a une vue.
- **Intuition.** He et Litterman (1999) montrent que le portefeuille optimal sans contrainte est le portefeuille d'équilibre, réduit selon l'incertitude de l'a priori, auquel s'ajoute une combinaison de portefeuilles représentant les vues.
- **Lecture bayésienne.** Satchell et Scowcroft (2000) présentent le modèle comme une mise à jour bayésienne de l'a priori par les vues.
- **Paramètres.** La confiance accordée aux vues (matrice Ω) et l'échelle de l'incertitude de l'a priori (τ) n'ont pas de valeur établie. Idzorek (2007) propose d'exprimer la confiance de chaque vue en pourcentage, d'où se déduit Ω. Walters (texte de travail de SSRN, plusieurs versions) détaille les choix de τ et de Ω que retiennent les auteurs successifs.
- **Extensions.** Meucci (2010) reprend le modèle avec ses démonstrations et l'étend : vues sur les rendements et non sur leur espérance, vues par classement, marchés non normaux. Bertsimas, Gupta et Paschalidis (2012) le relisent comme un problème d'optimisation inverse, ce qui permet d'autres mesures du risque et d'autres formes de vues.

Conséquence pour l'étude : l'implémentation de Scraper-BRVM (`quant/portfolio.py`) s'écarte du modèle original sur un point central, l'**a priori neutre** au lieu de l'a priori d'équilibre. Sans équilibre, le modèle n'a plus de point d'ancrage et l'optimiseur suit les vues, ce qui rapproche le résultat d'une optimisation moyenne-variance ordinaire et de ses défauts (§ 1). La BRVM dispose des poids de capitalisation flottante quotidiens (`data/Composition_flottante.xlsx`) : l'a priori d'équilibre est donc calculable.

## 3. D'où viennent les vues : analystes ou modèles

- **Vues d'analystes.** Luna-Ramírez et Agudelo (2018) appliquent le modèle aux actions du Marché intégré latino-américain (Colombie, Chili, Mexique, Pérou) de 2008 à 2016 avec les recommandations d'analystes de Bloomberg : les portefeuilles battent l'indice de chaque pays en rendement moyen et en alpha. Mbabu (2015, mémoire) utilise les vues de deux sociétés de recherche kényanes sur huit titres de Nairobi, sur quatre mois seulement.
- **Vues tirées de modèles de séries temporelles.** Beach et Orlov (2007) tirent les vues d'un modèle EGARCH-M sur vingt marchés nationaux et trouvent une meilleure performance qu'avec les seuls poids d'équilibre. Pyo et Lee (2018), sur le KOSPI 200, prévoient la volatilité par apprentissage automatique et posent comme vue que les titres peu risqués battent les titres risqués.
- **Vues sans jugement.** Allaj (2020) déduit les vues d'une optimisation inverse, comme l'a priori, et conclut que le modèle est une stratégie d'allocation valable hors échantillon.
- **Prophet.** Taylor et Letham (2018) présentent Prophet comme un outil de prévision de séries d'activité (tendance, saisonnalités, jours particuliers), réglable par un analyste. L'article ne le propose pas pour les cours boursiers ; son emploi pour des vues sur les rendements n'est appuyé par aucune référence trouvée.

Conséquence pour l'étude : la littérature ne justifie pas de vues Prophet ; elle teste plutôt des vues d'analystes, de volatilité ou d'anomalies documentées. Sur la BRVM, faute de recommandations d'analystes en base, les vues candidates sont des anomalies mesurables sur les cours et les dividendes (momentum, rendement du dividende, faible volatilité), ou des vues nulles pour isoler l'apport de l'a priori.

## 4. La performance hors échantillon

- Bessler, Opfer et Wolff (2017) testent une version du modèle fondée sur l'échantillon sur un portefeuille multi-actifs (actions, obligations, matières premières) de 1993 à 2011 : selon le résumé, les portefeuilles Black-Litterman battent nettement les parts égales et les poids stratégiques.
- Ce résultat, sur des indices d'actifs liquides, contraste avec celui de DeMiguel, Garlappi et Uppal (2009) sur des portefeuilles d'actions ou de secteurs. Les deux ne se contredisent pas forcément : le cadre, l'univers et la manière de former les vues diffèrent.
- Allaj (2020) et Luna-Ramírez et Agudelo (2018) concluent aussi en faveur du modèle, avec des vues et des références différentes.

Ce qui reste contesté : la valeur du modèle dépend surtout de la qualité des vues et du choix des témoins ; peu d'études comparent, à vues égales, le modèle avec et sans a priori d'équilibre.

## 5. Le risque estimé et les contraintes

- Ledoit et Wolf (2004) recommandent de ne jamais utiliser la matrice de covariance empirique pour optimiser un portefeuille et de la rétrécir vers une cible structurée ; c'est l'estimateur de l'implémentation actuelle.
- Jagannathan et Ma (2003) montrent qu'interdire les ventes à découvert revient à réduire les grands éléments de la matrice de covariance, et que cette contrainte améliore le portefeuille même lorsqu'elle est « fausse ». Un erratum de 2019 corrige une démonstration sans changer les propositions.

Conséquence pour l'étude : sur la BRVM, la vente à découvert n'existe pas et les séances sans échange raccourcissent les historiques communs. L'estimation de la covariance (dates communes, fréquence, rétrécissement) fait partie de la méthode et doit être fixée d'avance.

## 6. Les frais et la rotation

- Gârleanu et Pedersen (2013) dérivent la politique optimale quand les rendements sont prévisibles et les échanges coûteux : se diriger progressivement vers une cible qui anticipe les rendements futurs, plutôt que de rééquilibrer d'un coup.
- Les références sur les frais et la liquidité de `../backtest_naif/01_revue_litterature.md` (Novy-Marx et Velikov, 2016 ; Lesmond, 2005 ; de Groot, Pang et Swinkels, 2012) s'appliquent ici sans changement.

Conséquence pour l'étude : la rotation de l'évaluation exploratoire (6,9 fois par an, frais cumulés supérieurs au capital de départ) suffit à expliquer une grande part de l'écart. Une bande de non-rééquilibrage, ou une transition partielle vers la cible, est une variante à prévoir, pas un réglage à chercher après coup.

## 7. Sur la BRVM et les marchés frontières africains

- **Black-Litterman** : aucune application à la BRVM trouvée, ni dans les revues, ni dans les mémoires en ligne. En Afrique, des mémoires sur Johannesburg (Mbofana, 2011 ; Loloee-Eshraghi, sans date relevée) et Nairobi (Mbabu, 2015) ; leurs périodes sont courtes ou leurs univers petits. Ceux de Johannesburg sont listés à part (« À confirmer ») tant que leurs notices ne sont pas complètes.
- **Prévisibilité des cours de la BRVM** : les études d'efficience sont partagées. Tan Toe (2023), sur 1998-2020, applique des tests de racine unitaire, de suites et de ratio de variance pour la forme faible, et trouve que la masse monétaire (M1, M2) aide à prévoir les cours. D'autres travaux, à retrouver, concluent à l'efficience faible sur 2002-2004 ou à l'inefficience par le ratio de variance. Cette question dit si des vues fondées sur les cours passés peuvent avoir une valeur.

## 8. Écart comblé par l'étude

- Première application documentée du modèle à la BRVM.
- Mise en œuvre réaliste (exécution en J+1, frais, limite de ±7,5 %, participation au volume, séances sans échange), rarement présente dans les études sur les marchés frontières, qui raisonnent sur des cours de clôture.
- Décomposition de l'écart de performance entre a priori, vues et rotation, à vues égales, ce que la littérature consultée ne fait pas.
- Usage d'un a priori d'équilibre sur un marché très concentré (poids de la capitalisation flottante), où l'équilibre lui-même est discutable.

## 9. Méthodes recommandées

- **Témoins** (retenus en phase 1) : parts égales (DeMiguel, Garlappi et Uppal, 2009) et pondération par la capitalisation flottante ; Markowitz sous contrainte de vente à découvert comme repère.
- **Variantes figées d'avance** : a priori neutre ou d'équilibre ; vues nulles, momentum, rendement du dividende ; avec ou sans bande de non-rééquilibrage. Paramètres τ et Ω fixés par une règle publiée (Idzorek, 2007 ; Walters), pas optimisés.
- **Validation** : réglages sur 2008-2018, confirmation sur 2019-2026 ; walk-forward (skill `walk-forward-validation`).
- **Inférence** : test de différence des ratios de Sharpe robuste à l'autocorrélation, ou bootstrap par blocs ; ratio de Sharpe dégonflé et correction de Holm pour les variantes (références de `../backtest_naif/`).
- **Coûts** : frais de 1 % testés aussi à 0,5 % et 1,5 % ; rotation et frais rapportés à côté de chaque performance.

## Références

| Référence complète | DOI ou lien | Lu | Ce qu'elle apporte à l'étude |
|---|---|---|---|
| Allaj, E. (2020). « The Black–Litterman model and views from a reverse optimization procedure: an out-of-sample performance evaluation ». *Computational Management Science*, 17(3), 465-492. | https://doi.org/10.1007/s10287-020-00373-6 | Résumé | Vues sans jugement, test hors échantillon |
| Beach, S. L. et Orlov, A. G. (2007). « An application of the Black–Litterman model with EGARCH-M-derived views for international portfolio management ». *Financial Markets and Portfolio Management*, 21(2), 147-166. | https://ideas.repec.org/a/kap/fmktpm/v21y2007i2p147-166.html | Résumé | Vues tirées d'un modèle de séries temporelles |
| Bertsimas, D., Gupta, V. et Paschalidis, I. Ch. (2012). « Inverse optimization: a new perspective on the Black-Litterman model ». *Operations Research*, 60(6), 1389-1403. | https://doi.org/10.1287/opre.1120.1115 | Résumé | Lecture du modèle par l'optimisation inverse |
| Bessler, W., Opfer, H. et Wolff, D. (2017). « Multi-asset portfolio optimization and out-of-sample performance: an evaluation of Black–Litterman, mean-variance, and naïve diversification approaches ». *European Journal of Finance*, 23(1), 1-30. | https://ideas.repec.org/a/taf/eurjfi/v23y2017i1p1-30.html | Résumé | Black-Litterman contre 1/N hors échantillon |
| Best, M. J. et Grauer, R. R. (1991). « On the sensitivity of mean-variance-efficient portfolios to changes in asset means: some analytical and computational results ». *Review of Financial Studies*, 4(2), 315-342. | https://doi.org/10.1093/rfs/4.2.315 | Notice | Sensibilité des poids aux rendements espérés |
| Black, F. et Litterman, R. (1991). « Asset allocation: combining investor views with market equilibrium ». *Journal of Fixed Income*, 1(2), 7-18. | https://doi.org/10.3905/jfi.1991.408013 | Notice | Première publication du modèle |
| Black, F. et Litterman, R. (1992). « Global portfolio optimization ». *Financial Analysts Journal*, 48(5), 28-43. | https://doi.org/10.2469/faj.v48.n5.28 | Notice | Le modèle de référence |
| Chopra, V. K. et Ziemba, W. T. (1993). « The effect of errors in means, variances, and covariances on optimal portfolio choice ». *Journal of Portfolio Management*, 19(2), 6-11. | https://scinapse.io/papers/2164883547 (notice) | Notice | Coût relatif des erreurs d'estimation |
| DeMiguel, V., Garlappi, L. et Uppal, R. (2009). « Optimal versus naive diversification: how inefficient is the 1/N portfolio strategy? ». *Review of Financial Studies*, 22(5), 1915-1953. | https://doi.org/10.1093/rfs/hhm075 | Résumé | Les parts égales comme référence |
| Gârleanu, N. et Pedersen, L. H. (2013). « Dynamic trading with predictable returns and transaction costs ». *Journal of Finance*, 68(6), 2309-2340. | https://doi.org/10.1111/jofi.12080 | Résumé | Rééquilibrage partiel en présence de frais |
| He, G. et Litterman, R. (1999). « The intuition behind Black-Litterman model portfolios ». Goldman Sachs Asset Management, document de travail ; SSRN 334304. | https://papers.ssrn.com/abstract=334304 | Notice | Décomposition du portefeuille optimal |
| Idzorek, T. M. (2007). « A step-by-step guide to the Black-Litterman model: incorporating user-specified confidence levels ». Dans Satchell, S. (dir.), *Forecasting Expected Returns in the Financial Markets*, Academic Press, 17-38. | notice citée par https://lup.lub.lu.se/student-papers/record/9061456 | Notice (source secondaire) | Confiance des vues en pourcentage |
| Jagannathan, R. et Ma, T. (2003). « Risk reduction in large portfolios: why imposing the wrong constraints helps ». *Journal of Finance*, 58(4), 1651-1683. | https://doi.org/10.1111/1540-6261.00580 | Résumé | Effet de l'interdiction des ventes à découvert |
| Ledoit, O. et Wolf, M. (2004). « Honey, I shrunk the sample covariance matrix ». *Journal of Portfolio Management*, 30(4), 110-119. | https://doi.org/10.3905/jpm.2004.110 | Résumé | Covariance rétrécie |
| Luna-Ramírez, S. et Agudelo, D. A. (2018). « ¿Agrega valor el modelo Black-Litterman en portafolios del Mercado Integrado Latinoamericano (MILA)? Evaluación empírica 2008-2016 ». *Revista de Métodos Cuantitativos para la Economía y la Empresa*. | https://www.upo.es/revistas/index.php/RevMetCuant/article/view/2809 | Résumé | Application à des marchés émergents avec vues d'analystes |
| Mbabu, W. M. (2015). « Applying the Black Litterman model to the NSE ». Mémoire, Strathmore University. | https://su-plus.strathmore.edu/handle/11071/5114 | Résumé | Application à Nairobi avec vues d'analystes, quatre mois |
| Meucci, A. (2010). « The Black-Litterman approach: original model and extensions ». *The Encyclopedia of Quantitative Finance*, Wiley ; version longue SSRN 1117574. | https://papers.ssrn.com/abstract=1117574 | Résumé | Démonstrations et extensions |
| Michaud, R. O. (1989). « The Markowitz optimization enigma: is "optimized" optimal? ». *Financial Analysts Journal*, 45(1), 31-42. | https://doi.org/10.2469/faj.v45.n1.31 | Notice | L'optimiseur maximise les erreurs |
| Pyo, S. et Lee, J. (2018). « Exploiting the low-risk anomaly using machine learning to enhance the Black–Litterman framework: evidence from South Korea ». *Pacific-Basin Finance Journal*, 51, 1-12. | https://ideas.repec.org/a/eee/pacfin/v51y2018icp1-12.html | Résumé | Vues fondées sur une anomalie documentée |
| Satchell, S. et Scowcroft, A. (2000). « A demystification of the Black–Litterman model: managing quantitative and traditional portfolio construction ». *Journal of Asset Management*, 1(2), 138-150. | https://doi.org/10.1057/palgrave.jam.2240011 | Notice | Lecture bayésienne du modèle |
| Tan Toe, D. L. (2023). « Investigating the weak and semi-strong forms of informational efficiency on the West African Economic and Monetary Union's stock exchange (BRVM) through returns predictability tests ». *SN Business & Economics*, 3(9). | https://doi.org/10.1007/s43546-023-00550-0 | Résumé | Prévisibilité des cours de la BRVM |
| Taylor, S. J. et Letham, B. (2018). « Forecasting at scale ». *The American Statistician*, 72(1), 37-45. | https://doi.org/10.1080/00031305.2017.1380080 | Résumé | Ce qu'est Prophet, et pour quoi il a été conçu |
| Walters, J. « The Black-Litterman model in detail ». Document de travail, SSRN 1314585 (plusieurs versions, 2009 à 2014). | https://doi.org/10.2139/ssrn.1314585 | Notice | Choix de τ et de Ω dans la littérature |

## À confirmer

Références signalées ailleurs mais non vérifiées ; elles ne sont pas citées tant qu'elles ne le sont pas.

- « Combining equilibrium, resampling, and analysts' views in portfolio optimization », *Journal of Banking & Finance*, 36(5), 1354-1361 (2012) : auteurs non confirmés (Fernandes, Ornelas et Cusicanqui d'après mémoire), application brésilienne à vérifier.
- Ledoit, O. et Wolf, M. (2008), test robuste de différence des ratios de Sharpe (*Journal of Empirical Finance*) : notice à retrouver.
- Mbofana (2011), mémoire de l'Université du Cap sur Black-Litterman avec distributions alpha-stables : https://open.uct.ac.za/bitstreams/340cecfb-d589-4a3d-9156-dc1ebbd270aa/download (titre et auteur complets à relever).
- Loloee-Eshraghi, application à l'indice JSE All Share de 2000 à 2010 : https://wiredspace.wits.ac.za/items/bfacf874-4876-4bcc-8461-6417c43b7551 (date et titre à relever).
- Études d'efficience de la BRVM : revue LEON (supplément 2007, efficience faible sur 2002-2004) et « The Efficiency of BRVM Tested by the Facts: Analysis of Past Share Prices » (Université d'Abomey-Calavi, https://dspace.uac.bj/handle/123456789/14539) : auteurs et références complètes à relever.
- Cheung, W. (2010). « The Black-Litterman model explained ». *Journal of Asset Management*, 11(4) : didacticiel, à vérifier.
