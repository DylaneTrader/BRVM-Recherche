# Revue de littérature : score de risque des titres de la BRVM

Date : 2026-10-22. État : brouillon, en attente de validation.

Objet de l'étude : le score de risque de l'application classe les titres comparés, sur une même fenêtre de 1, 3 ou 5 ans, de 0 (le moins risqué) à 100 (le plus risqué). Il fait la moyenne des rangs de cinq mesures : volatilité et volatilité baissière (rendements hebdomadaires), perte maximale, indice d'ulcère (cours de chaque séance) et CVaR à 95 % (rendements hebdomadaires). Les titres peu liquides sont écartés par défaut. Le dossier prévoit aussi des régimes de volatilité. La revue rassemble ce que la littérature dit des choix de ce score : quelles mesures retenir, comment les agréger, ce que le risque mesuré annonce, et comment l'illiquidité fausse la mesure.

Lecture : toutes les références ci-dessous ont été retrouvées par recherche en ligne (notice bibliographique et résumé). Aucun texte complet n'a été lu pendant cette phase. Les résultats attribués à chaque article sont ceux de son résumé ou de sa notice ; ils seront vérifiés sur le texte complet avant d'être cités dans l'article.

## 1. Quelles mesures du risque d'un titre ?

**La volatilité et le risque de baisse.** La volatilité traite de la même façon les hausses et les baisses. Sortino et Price (1994) proposent de ne mesurer que l'écart sous un rendement minimal acceptable (semi-variance), d'où le ratio de Sortino. Estrada (2002) défend ce choix pour les marchés émergents : sur 28 marchés, un bêta calculé sur les seules baisses (D-CAPM) y expliquerait mieux les rendements que le bêta usuel. Les réplications sur des marchés nationaux sont partagées.

**Les mesures de pertes extrêmes.** Artzner, Delbaen, Eber et Heath (1999) définissent les propriétés qu'une mesure de risque devrait respecter (mesure « cohérente ») ; la VaR, un quantile, n'est pas sous-additive. Rockafellar et Uryasev (2000) proposent une méthode d'optimisation d'un portefeuille sous la CVaR, perte moyenne au-delà de la VaR. Acerbi et Tasche (2002) établissent qu'une définition de l'expected shortfall est cohérente quelle que soit la loi des rendements, et qu'elle s'estime même là où les estimateurs usuels de la VaR échouent.

**Les mesures fondées sur les pertes depuis un plus haut.** Chekhlov, Uryasev et Zabarankin (2005) définissent une famille de mesures de la courbe des pertes depuis le plus haut (Conditional Drawdown), dont la perte maximale et la perte moyenne sont des cas limites. Magdon-Ismail et Atiya (2004) relient la perte maximale attendue au rendement moyen et au ratio de Sharpe, et proposent de quoi comparer des historiques de longueurs différentes. L'indice d'ulcère, qui mesure la profondeur et la durée des baisses, vient d'un ouvrage de praticiens (Martin et McCann) ; sa référence d'origine reste à confirmer.

Ce qui est établi : aucune mesure ne résume seule le risque, et les mesures de baisse et de queue ont des fondements théoriques solides. Ce qui est contesté : l'apport du risque de baisse par rapport à la volatilité selon les marchés (Estrada et ses réplications). Ce qui manque : un choix argumenté des mesures pour un marché où beaucoup de titres ne s'échangent pas chaque jour.

## 2. Les mesures se recoupent-elles, et comment les agréger ?

**Des classements souvent très proches.** Eling et Schuhmacher (2007) comparent le ratio de Sharpe à douze autres mesures de performance sur 2 763 fonds alternatifs. Malgré des rendements non normaux, les classements sont presque identiques. Si les mesures de risque du score se recoupent autant sur la BRVM, la moyenne de cinq rangs n'apporte guère plus qu'une seule mesure. C'est à tester.

**Construire un indicateur composite.** Le manuel de l'OCDE et du Centre commun de recherche de la Commission européenne (Nardo et al., 2008) porte sur la méthode de construction et de validation des indicateurs composites ; son contenu détaillé reste à lire. Le score de l'application, moyenne de rangs à poids égaux, est un indicateur composite de ce type, dont les choix (mesures, normalisation, poids) n'ont pas été validés.

**Un précédent réglementaire.** L'indicateur synthétique de risque et de rendement (SRRI) des OPCVM européens (CESR, 2010) classe chaque fonds dans l'une de sept catégories selon sa volatilité, calculée sur des rendements hebdomadaires ou mensuels des cinq dernières années. Un changement de catégorie n'est retenu qu'après quatre mois hors de la catégorie d'origine. C'est une échelle absolue fondée sur une seule mesure, là où le score de l'application est relatif et combine cinq mesures. Les bornes des classes n'ont été lues que dans des sources secondaires et restent à vérifier dans le texte de la CESR.

## 3. Ce que le risque mesuré annonce

La finance classique attend un rendement plus élevé pour un risque plus élevé. Les données disent souvent l'inverse.

- Ang, Hodrick, Xing et Zhang (2006) : les titres à forte volatilité idiosyncratique ont des rendements moyens très faibles, ce que ni la taille, ni la valeur, ni le momentum, ni la liquidité n'expliquent.
- Baker, Bradley et Wurgler (2011) : la sous-performance des titres à fort bêta et à forte volatilité, de 1968 à 2008, persiste en partie parce que les gérants jugés contre un indice n'ont pas intérêt à l'exploiter.
- Frazzini et Pedersen (2014) documentent l'anomalie des titres à faible bêta (« betting against beta »). Novy-Marx et Velikov (2022) attribuent une partie de leurs résultats à leur méthode d'estimation du bêta.
- Sur les marchés émergents, Blitz, Pang et van Vliet (2013) trient les titres sur la volatilité et le bêta passés, dans des portefeuilles neutres par pays.
- Sur les marchés frontières africains, Steyn, Gilbert et Viviers (2024) étudient neuf marchés de 2004 à 2023. Une prime des titres peu volatils y apparaît, sauf pendant les marchés haussiers, et résiste à l'illiquidité et à des frais élevés.

Pour l'étude, la question n'est pas de bâtir une stratégie, mais de savoir si le score classe des titres dont les pertes futures diffèrent : un titre classé risqué subit-il ensuite des baisses plus fortes ? C'est la validation prédictive que la littérature ne fournit pas pour un score composite.

## 4. L'illiquidité fausse la mesure du risque

Sur la BRVM, beaucoup de titres ne s'échangent pas chaque jour. Leur cours reste inchangé et leur rendement du jour vaut zéro.

- Scholes et Williams (1977) montrent que le bêta estimé sur des données non synchrones est biaisé et non convergent. Dimson (1979) traite de la mesure du risque des titres peu échangés ; sa méthode reste à lire sur le texte complet.
- Lo et MacKinlay (1990) montrent que les échanges non synchrones créent une autocorrélation des rendements et faussent leur variance.
- Getmansky, Lo et Makarov (2004) proposent, sur les fonds alternatifs, un modèle économétrique de l'autocorrélation des rendements due à l'illiquidité. Ses conséquences sur la volatilité mesurée restent à lire sur le texte complet.

C'est la raison donnée par l'application pour calculer volatilité et CVaR sur des rendements hebdomadaires. Mais la perte maximale et l'indice d'ulcère sont calculés sur les cours de chaque séance, et l'effet de ce mélange de fréquences n'est pas mesuré.

## 5. Régimes de volatilité

- Schwert (1989), sur des données mensuelles de 1857 à 1986, relie la volatilité boursière à la volatilité macroéconomique, au levier, à l'activité des échanges. Une grande part de ses variations reste difficile à expliquer.
- Hamilton et Susmel (1994) introduisent un modèle ARCH à changement de régime (SWARCH), où le niveau de la volatilité change d'état selon une chaîne de Markov.
- Rydén, Teräsvirta et Åsbrink (1998) reproduisent les faits stylisés des rendements quotidiens par un modèle de Markov caché.
- Bekaert et Harvey (1997) étudient la volatilité des marchés émergents, dans le temps et entre pays ; la libéralisation des marchés y augmente la corrélation avec le marché mondial sans augmenter la volatilité locale.

Sur la BRVM :

- Djahoué, Kacou Bi et Aba (2026), sur des données quotidiennes de 2010 à 2022, comparent cinq modèles de volatilité ; un EGARCH à loi de Student asymétrique est le meilleur, et un indice de sentiment améliore la prévision.
- N'dri (2007) montre que le volume aide à prévoir la volatilité.
- Poussi compare des modèles GARCH(1,1) et APARCH(1,1) sur les indices Composite, BRVM 30 et Prestige ; la volatilité y est persistante, et l'indice Composite réagit davantage aux baisses. L'année et le volume de cet article restent à confirmer.

## 6. Sur la BRVM et les marchés frontières africains

Les travaux retrouvés sur la BRVM modélisent la volatilité des indices (Djahoué et al., 2026 ; Poussi) ou sa relation au volume (N'dri, 2007). Aucun ne mesure le risque titre par titre, ni ne compare des mesures de risque, ni ne construit un classement des titres. Sur les marchés frontières africains, la seule étude retrouvée sur le risque des titres (Steyn et al., 2024) porte sur la prime des titres peu volatils, pas sur la mesure du risque.

## 7. Écart comblé par l'étude

1. **Aucune mesure du risque titre par titre n'a été publiée pour la BRVM.** L'étude décrirait la volatilité, les pertes extrêmes et les pertes depuis un plus haut de chaque titre, sur un marché frontière peu liquide.
2. **La redondance des mesures n'est pas connue sur ce marché.** Le résultat d'Eling et Schuhmacher (2007) peut ne pas tenir quand les rendements sont souvent nuls : c'est à tester avant de justifier cinq mesures plutôt qu'une.
3. **Un score composite de risque n'a jamais été validé.** Ni sa stabilité dans le temps, ni sa sensibilité aux choix (mesures, poids, fenêtre, fréquence), ni son pouvoir d'annoncer les pertes futures.
4. **L'effet de l'illiquidité sur chaque mesure n'est pas quantifié** : rendements quotidiens contre hebdomadaires, titres liquides contre tous les titres.
5. **Les régimes de volatilité de la BRVM** n'ont été étudiés que sur les indices, par des modèles GARCH ; ni par des modèles à changement de régime, ni titre par titre.

## 8. Méthodes recommandées

- **Construction et validation du composite** : s'appuyer sur le manuel OCDE-CCR (Nardo et al., 2008) et analyser la sensibilité du classement aux choix de mesures, de poids et de fenêtres.
- **Redondance des mesures** : corrélations de rang entre mesures et entre classements, comme Eling et Schuhmacher (2007) ; analyse en composantes principales des rangs.
- **Validation prédictive** : relier le score à une date aux pertes réalisées ensuite (volatilité, perte maximale, CVaR sur la fenêtre suivante), hors échantillon, avec des erreurs types robustes au recouvrement des fenêtres.
- **Stabilité** : persistance des classements d'une fenêtre à la suivante ; migration entre classes, avec une règle de lissage comme celle du SRRI (CESR, 2010).
- **Illiquidité** : comparer les mesures sur rendements quotidiens et hebdomadaires ; corrections du bêta de Scholes et Williams (1977) et de Dimson (1979) ; modèle de Getmansky, Lo et Makarov (2004) pour l'autocorrélation due à l'illiquidité.
- **Mesures de queue** : la CVaR plutôt que la VaR, pour sa cohérence (Artzner et al., 1999 ; Acerbi et Tasche, 2002). Sur cinq ans de rendements hebdomadaires, la CVaR à 95 % repose sur une douzaine de semaines : à dire, et à tester par bootstrap.
- **Régimes de volatilité** : modèle SWARCH (Hamilton et Susmel, 1994) ou de Markov caché (Rydén et al., 1998), comparé à un GARCH asymétrique, dont l'EGARCH retenu par Djahoué et al. (2026) sur la BRVM.

## Références

| Référence complète | DOI ou lien | Lu | Ce qu'elle apporte à l'étude |
|---|---|---|---|
| Acerbi, C. et Tasche, D. (2002). « On the coherence of expected shortfall ». *Journal of Banking & Finance*, 26(7), 1487-1503. | https://arxiv.org/abs/cond-mat/0104295 (version de travail) | Résumé | Cohérence de l'expected shortfall (CVaR) |
| Ang, A., Hodrick, R. J., Xing, Y. et Zhang, X. (2006). « The cross-section of volatility and expected returns ». *Journal of Finance*, 61(1), 259-299. | https://doi.org/10.1111/j.1540-6261.2006.00836.x | Résumé | Titres volatils, rendements faibles |
| Artzner, P., Delbaen, F., Eber, J.-M. et Heath, D. (1999). « Coherent measures of risk ». *Mathematical Finance*, 9(3), 203-228. | https://doi.org/10.1111/1467-9965.00068 | Résumé | Propriétés d'une mesure de risque |
| Baker, M., Bradley, B. et Wurgler, J. (2011). « Benchmarks as limits to arbitrage: understanding the low-volatility anomaly ». *Financial Analysts Journal*, 67(1). | https://rpc.cfainstitute.org/research/financial-analysts-journal/2011/benchmarks-as-limits-to-arbitrage-understanding-the-low-volatility-anomaly | Résumé | Persistance de l'anomalie des titres peu volatils |
| Bekaert, G. et Harvey, C. R. (1997). « Emerging equity market volatility ». *Journal of Financial Economics*, 43(1), 29-77. | https://doi.org/10.1016/S0304-405X(96)00889-6 | Résumé | Volatilité des marchés émergents |
| Blitz, D., Pang, J. et van Vliet, P. (2013). « The volatility effect in emerging markets ». *Emerging Markets Review*, 16, 31-45. | https://doi.org/10.1016/j.ememar.2013.02.004 | Résumé | Effet de la volatilité sur les marchés émergents |
| CESR, Committee of European Securities Regulators (2010). *CESR's guidelines on the methodology for the calculation of the synthetic risk and reward indicator in the Key Investor Information Document*. CESR/10-673. | https://www.esma.europa.eu/sites/default/files/library/2015/11/10_673.pdf | Résumé (sources secondaires) | Échelle de risque réglementaire, règle de migration |
| Chekhlov, A., Uryasev, S. et Zabarankin, M. (2005). « Drawdown measure in portfolio optimization ». *International Journal of Theoretical and Applied Finance*, 8(1), 13-58. | https://doi.org/10.1142/S0219024905002767 | Résumé | Famille des mesures de perte depuis un plus haut |
| Dimson, E. (1979). « Risk measurement when shares are subject to infrequent trading ». *Journal of Financial Economics*, 7(2), 197-226. | https://econpapers.repec.org/RAS/pdi298.htm (notice) | Notice | Bêta des titres peu échangés |
| Djahoué, M. G., Kacou Bi, K. A. et Aba, N. E. A. (2026). « Investor sentiment and stock market volatility: evidence from the West African Regional Stock Exchange ». *Applied Economics and Finance*, 13(1). | https://doi.org/10.11114/aef.v13i1.8816 | Résumé | Modèles de volatilité sur la BRVM |
| Eling, M. et Schuhmacher, F. (2007). « Does the choice of performance measure influence the evaluation of hedge funds? ». *Journal of Banking & Finance*, 31(9), 2632-2647. | https://doi.org/10.1016/j.jbankfin.2006.09.015 | Résumé | Classements presque identiques selon la mesure |
| Estrada, J. (2002). « Systematic risk in emerging markets: the D-CAPM ». *Emerging Markets Review*, 365-379. | https://doi.org/10.1016/S1566-0141(02)00042-0 | Résumé (sources secondaires) | Risque de baisse sur les marchés émergents |
| Frazzini, A. et Pedersen, L. H. (2014). « Betting against beta ». *Journal of Financial Economics*, 111(1), 1-25. | https://doi.org/10.1016/j.jfineco.2013.10.005 | Résumé | Rendement ajusté positif des titres à faible bêta |
| Getmansky, M., Lo, A. W. et Makarov, I. (2004). « An econometric model of serial correlation and illiquidity in hedge fund returns ». *Journal of Financial Economics*, 74(3), 529-609. | https://doi.org/10.1016/j.jfineco.2004.04.001 | Résumé | Autocorrélation des rendements due à l'illiquidité |
| Hamilton, J. D. et Susmel, R. (1994). « Autoregressive conditional heteroskedasticity and changes in regime ». *Journal of Econometrics*, 64, 307-333. | https://www.estima.com/webhelp/topics/hamiltonsusmeljoe1994.html (réplication) | Résumé | Régimes de volatilité (SWARCH) |
| Lo, A. W. et MacKinlay, A. C. (1990). « An econometric analysis of nonsynchronous trading ». *Journal of Econometrics*, 45(1-2), 181-211. | https://ideas.repec.org/a/eee/econom/v45y1990i1-2p181-211.html | Résumé | Effet des échanges non synchrones sur la variance |
| Magdon-Ismail, M. et Atiya, A. F. (2004). « Maximum drawdown ». *Risk*, 17(10), 99-102. | https://papers.ssrn.com/abstract=874069 | Résumé | Perte maximale attendue, comparaison d'historiques |
| N'dri, K. L. (2007). « An empirical study of the relation between stock return volatility and trading volume in the BRVM ». *African Journal of Business Management*, 1(5), 107-112. | https://academicjournals.org/journal/AJBM/article-abstract/7B75A0417552 | Résumé | Volume et volatilité sur la BRVM |
| Nardo, M., Saisana, M., Saltelli, A., Tarantola, S., Hoffmann, A. et Giovannini, E. (2008). *Handbook on Constructing Composite Indicators: Methodology and User Guide*. OCDE et Centre commun de recherche de la Commission européenne. | https://publications.jrc.ec.europa.eu/repository/handle/JRC47008 | Table des matières et présentation | Méthode de construction et de validation d'un composite |
| Novy-Marx, R. et Velikov, M. (2022). « Betting against betting against beta ». *Journal of Financial Economics*, 143(1). | https://doi.org/10.1016/j.jfineco.2021.05.023 | Résumé | Critique de l'estimation du bêta de Frazzini et Pedersen |
| Rockafellar, R. T. et Uryasev, S. (2000). « Optimization of conditional value-at-risk ». *Journal of Risk*, 2, 21-41. | https://sites.math.washington.edu/~rtr/papers/rtr179-CVaR1.pdf | Résumé | Définition et optimisation de la CVaR |
| Rydén, T., Teräsvirta, T. et Åsbrink, S. (1998). « Stylized facts of daily return series and the hidden Markov model ». *Journal of Applied Econometrics*, 13(3), 217-244. | https://ideas.repec.org/a/jae/japmet/v13y1998i3p217-244.html | Résumé | Modèle de Markov caché des rendements quotidiens |
| Scholes, M. et Williams, J. (1977). « Estimating betas from nonsynchronous data ». *Journal of Financial Economics*, 5(3), 309-327. | https://se.vlex.com/vid/bibliography-of-myron-s-856414489 (bibliographie de l'auteur) | Notice | Bêta et données non synchrones |
| Schwert, G. W. (1989). « Why does stock market volatility change over time? ». *Journal of Finance*, 44(5), 1115-1153. | https://doi.org/10.3386/w2798 (version de travail NBER) | Résumé | Variations de la volatilité dans le temps |
| Sortino, F. A. et Price, L. N. (1994). « Performance measurement in a downside risk framework ». *Journal of Investing*, 3. | https://search.r-project.org/CRAN/refmans/JFE/html/SortinoRatio.html (notice secondaire) | Notice secondaire | Volatilité baissière, rendement minimal acceptable |
| Steyn, Gilbert et Viviers (2024). « The low-volatility effect in African frontier equity markets ». *Investment Analysts Journal*. | https://doi.org/10.1080/10293523.2024.2361986 | Résumé | Prime des titres peu volatils sur neuf marchés frontières africains |

Détails à vérifier sur le texte complet ou la page de l'éditeur : pages de Sortino et Price (50-58 ou 59-65 selon les sources) ; volume d'Estrada (3 ou 4 selon les sources) ; numéro d'Acerbi et Tasche et de Rockafellar et Uryasev ; prénoms et pages de Steyn, Gilbert et Viviers ; pages de Baker et al. (2011) et de Novy-Marx et Velikov (2022).

## À confirmer

Références repérées mais pas encore vérifiées ou pas encore lues ; elles ne sont pas citées.

- Martin, P. G. et McCann, B. B. *The Investor's Guide to Fidelity Funds* : origine de l'indice d'ulcère, 1987 ou 1989 selon les sources.
- Markowitz, H. (1959). *Portfolio Selection: Efficient Diversification of Investments* : semi-variance ; édition à vérifier.
- Poussi, S. A. « Modélisation et prévision des indices de la BRVM : une analyse comparative des indices Composite, 30 et Prestige ». *European Journal of Economic and Financial Research* (OAPub), https://www.oapub.org/soc/index.php/EJEFR/article/view/1903 : année, volume et DOI non trouvés.
- Une étude sur la volatilité excessive des actions de la BRVM (2000-2018) par la finance comportementale, vue sur ResearchGate : auteur, revue et année non retrouvés.
- Eling, M. (2008), *Financial Analysts Journal* : extension de Eling et Schuhmacher à 38 954 fonds ; DOI non retrouvé.
