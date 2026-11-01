# Revue de littérature : prévision probabiliste et stress des ratios réglementaires d'un fonds

Date : 2026-10-23. État : brouillon, en attente de validation.

Question posée : quels mouvements de marché et quels flux pourraient faire dépasser chaque ratio réglementaire, avec quelle probabilité, dans quel délai et sur quelles positions ? Deux volets :

- **empirique** : un portefeuille actions de la BRVM ;
- **théorique** : un fonds commun de placement (FCP) à quatre classes d'actifs (actions, obligations, liquidités, parts d'autres FCP).

Lecture : toutes les références ci-dessous ont été retrouvées par recherche en ligne (notice bibliographique et résumé). Aucun texte complet n'a été lu pendant cette phase. Les résultats attribués à chaque article sont ceux de son résumé ou de sa notice ; ils seront vérifiés sur le texte complet avant d'être cités dans l'article.

## 1. Le cadre réglementaire

**Dans l'UMOA.** Les OPC du marché financier régional relèvent de l'Instruction n° 66/CREPMF/2021 relative aux organismes de placement collectif et à leurs sociétés de gestion. Elle est entrée en vigueur le 1er janvier 2022, abroge sept textes antérieurs, est complétée par seize circulaires d'application du 3 janvier 2022, et figure comme non abrogée dans la liste des textes de l'AMF-UMOA. Les skills de ce dépôt en retiennent deux règles pour un FCP : un plafond par émetteur de 15 % des actifs, porté à 20 % pour un titre qui pèse plus de 10 % de l'indice, avec un maximum de 50 % pour la somme des lignes au-delà de 15 % (article 41) ; et l'interdiction de détenir des actions donnant une influence notable sur l'émetteur, appréciée pour l'ensemble des FCP d'une société de gestion, sans seuil chiffré (article 44.1). **Le texte de l'instruction n'a pas pu être lu pendant cette revue** : ces chiffres, les ratios de liquidité, d'emprunt et d'investissement dans d'autres OPC, et les délais de régularisation d'un dépassement sont à relever dans l'instruction et ses circulaires avant la phase 3.

**Ailleurs, pour comparaison.** En France, le Code monétaire et financier limite l'investissement d'un OPCVM dans un même émetteur à 5 % des actifs, porté à 10 % si les lignes au-delà de 5 % ne dépassent pas 40 % au total (règle dite « 5/10/40 », article R214-21). Aux États-Unis, la règle fiscale « 50/5/10 » des fonds (Pastor, Sikorskaya et Wang, 2026) exige qu'au moins la moitié des actifs soit en positions de moins de 5 % chacune, et interdit de détenir plus de 10 % des droits de vote d'un émetteur.

**Dépassement actif et dépassement passif.** Certaines réglementations distinguent le dépassement causé par une décision de gestion de celui causé par un mouvement de prix ou un flux, hors du contrôle du gérant, et accordent pour le second un délai de régularisation ; l'exemple indien, vu seulement dans la presse, est en « À confirmer ». C'est précisément ce second type que l'étude cherche à prévoir. Le traitement des dépassements passifs dans l'UMOA est à vérifier dans l'instruction.

## 2. Pourquoi un ratio est dépassé : prix, flux et contraintes

**Les flux suivent la performance, et pas de façon symétrique.** Sirri et Tufano (1998) montrent que les investisseurs achètent les fonds qui ont très bien fait sans quitter autant ceux qui ont mal fait. Chevalier et Ellison (1997) estiment cette relation entre flux et performance et montrent que les gérants ajustent leur risque en fonction des incitations qu'elle crée.

**Les rachats peuvent s'auto-entretenir.** Chen, Goldstein et Jiang (2010) trouvent que les rachats sont plus sensibles aux mauvaises performances dans les fonds qui détiennent des actifs peu liquides : les premiers sortants font supporter le coût de liquidation aux suivants. L'effet disparaît quand les porteurs sont surtout de gros investisseurs. Goldstein, Jiang et Ng (2017) retrouvent ce mécanisme dans les fonds obligataires, où la sensibilité des sorties aux mauvaises performances augmente avec l'illiquidité des actifs et du marché.

**Les rachats forcent des ventes qui pèsent sur les prix.** Coval et Stafford (2007) montrent que les ventes contraintes de fonds en décollecte font baisser les titres qu'ils détiennent en commun, et que ces ventes sont prévisibles.

**Les contraintes réglementaires mordent.** Almazan, Brown, Carlson et Chapman (2004) décrivent les restrictions d'investissement des fonds actions américains, leur fréquence et leurs raisons. Pastor, Sikorskaya et Wang (2026) montrent que, quand le marché se concentre, les fonds proches de la limite « 50/5/10 » réduisent leurs plus grosses lignes et font moins bien quand la contrainte s'applique.

Pour l'étude, la conséquence est double : un dépassement peut venir d'un mouvement de prix (une ligne grossit), d'un rachat (l'actif net baisse et le poids des lignes conservées monte) ou des deux ensemble, et les rachats sont plus probables après une mauvaise performance, c'est-à-dire précisément quand les prix ont bougé.

## 3. Liquidité des fonds et tests de résistance

- **Recommandations internationales.** L'OICV (IOSCO, 2018) formule dix-sept recommandations sur la gestion du risque de liquidité des fonds ouverts : conception du fonds, gestion quotidienne de la liquidité de l'actif et du passif, plans de contingence. Une révision est en consultation depuis novembre 2024.
- **Lignes directrices européennes.** L'ESMA (2020) impose aux OPCVM et aux FIA des tests de résistance de liquidité, appliqués depuis le 30 septembre 2020.
- **Méthode.** Bouveret (2017) propose un cadre pratique : calibrer un choc de rachats, mesurer les réserves de liquidité, et rapporter les unes aux autres (ratio de couverture des rachats).
- **Fonds de fonds.** L'autorité maltaise (MFSA, 2025), dans son test de 72 fonds de détail, traite les parts de fonds cibles étrangers comme illiquides en période de tension : c'est l'une des deux causes principales des fonds incapables d'honorer les rachats dans au moins un scénario, et deux fonds de fonds y sont signalés comme fragiles.

**Liquidation d'une position.** Almgren et Chriss (2001) arbitrent entre le coût d'impact d'une vente rapide et le risque de prix d'une vente lente, et en tirent une VaR ajustée de la liquidité. Bangia, Diebold, Schuermann et Stroughair (1999) ajoutent au risque de marché le coût de l'écart entre prix acheteur et vendeur, en distinguant illiquidité exogène et endogène.

Pour l'étude, ces travaux donnent le délai : un ratio dépassé doit être régularisé, et sur la BRVM la sortie d'une ligne peut prendre plusieurs séances, limitées à ±7,5 % de variation par séance.

## 4. Prévoir une distribution et choisir des scénarios

**Simuler les trajectoires.** Barone-Adesi, Giannopoulos et Vosper (1999) proposent la simulation historique filtrée : les rendements passés sont normalisés par une volatilité GARCH puis rééchelonnés à la volatilité du jour. Les corrélations entre actifs sont conservées sans être estimées explicitement.

**Choisir des scénarios de stress.** Breuer, Jandačka, Rheinberger et Summer (2009) définissent un scénario de stress plausible, sévère et utile : chercher, dans une région de plausibilité définie par la loi des facteurs de risque, le scénario qui cause la plus grosse perte. Glasserman, Kang et Kang (2015) traitent le stress inverse : trouver les scénarios les plus probables parmi ceux qui produisent une perte au-delà d'un seuil, par un estimateur non paramétrique de vraisemblance empirique. Remplacer « perte au-delà d'un seuil » par « ratio au-delà de sa limite » donne exactement la question de l'étude.

**Évaluer une prévision probabiliste.** Gneiting et Raftery (2007) établissent les règles de score strictement propres, qui récompensent le prévisionniste quand il annonce la vraie distribution. Christoffersen (1998) propose de tester la couverture conditionnelle d'intervalles de prévision, base des tests de VaR.

## 5. Le FCP à quatre classes d'actifs

La revue n'a pas trouvé d'étude académique qui modélise jointement les ratios réglementaires d'un fonds diversifié qui investit aussi dans d'autres fonds. Les éléments disponibles sont dispersés :

- la liquidité des parts de fonds cibles en période de tension (MFSA, 2025) ;
- la fragilité des fonds obligataires (Goldstein, Jiang et Ng, 2017) ;
- les cadres de tests de liquidité, qui traitent l'actif par classes (Bouveret, 2017 ; ESMA, 2020).

Pour un FCP de FCP, la transparence (« look-through ») sur les positions des fonds cibles conditionne le calcul de certains ratios ; sa place dans l'instruction UMOA est à vérifier.

## 6. Sur la BRVM et l'UMOA

Le secteur des OPC de l'UMOA s'est développé depuis 2022. Une étude publiée en 2024 analyse la persistance des performances de 23 FCP de la BRVM (auteurs à confirmer). Aucune étude retrouvée ne porte sur les ratios réglementaires des OPC de l'UMOA, sur leurs flux, ni sur leurs tests de liquidité.

Données : les skills du dépôt signalent que `data/` ne contient **ni valeurs liquidatives, ni flux, ni positions de FCP** ; seuls existent les portefeuilles simulés de l'application. Le volet empirique devra donc soit porter sur des portefeuilles reconstitués ou simulés, avec des flux modélisés, soit obtenir des données de fonds réels.

## 7. Écart comblé par l'étude

1. **Aucune étude ne prévoit la probabilité de dépassement d'un ratio réglementaire** : la littérature traite les pertes (VaR, stress inverse) et la liquidité (tests de rachats), pas le franchissement d'une limite de composition.
2. **La décomposition prix, flux et interaction** d'un dépassement passif n'est pas mesurée. Les travaux sur les flux montrent pourtant que les deux sont liés.
3. **Le délai** (premier passage au-delà de la limite, puis délai de régularisation sous contrainte de liquidité et de limite de variation) n'est pas étudié.
4. **Le cas d'un marché frontière** concentré et peu liquide, où une seule capitalisation peut peser lourd dans l'indice et où la régularisation peut prendre plusieurs séances.
5. **Le FCP multi-actifs avec parts de fonds** n'a pas de cadre théorique pour ses ratios.

## 8. Méthodes recommandées

- **Simulation des prix** : simulation historique filtrée (Barone-Adesi et al., 1999), qui conserve la dépendance entre titres et l'effet des séances sans échange, avec la limite de ±7,5 % appliquée à chaque séance simulée.
- **Modèle des flux** : rachats et souscriptions fonction de la performance passée, asymétriques (Sirri et Tufano, 1998 ; Chevalier et Ellison, 1997), plus sensibles quand l'actif est peu liquide (Chen et al., 2010) ; chocs de rachat calibrés comme dans Bouveret (2017) et l'ESMA (2020).
- **Probabilité et délai de dépassement** : probabilité de premier passage de chaque ratio au-delà de sa limite, par horizon ; contribution de chaque position.
- **Scénarios** : stress inverse au sens de Glasserman, Kang et Kang (2015), appliqué au franchissement d'une limite ; scénarios plausibles et sévères au sens de Breuer et al. (2009).
- **Régularisation** : coût et durée de retour sous la limite (Almgren et Chriss, 2001 ; Bangia et al., 1999), en séances, avec la liquidité réelle des titres.
- **Validation** : score des probabilités annoncées (règles propres, Gneiting et Raftery, 2007) et couverture des intervalles (Christoffersen, 1998), hors échantillon.

## Références

| Référence complète | DOI ou lien | Lu | Ce qu'elle apporte à l'étude |
|---|---|---|---|
| Almazan, A., Brown, K. C., Carlson, M. et Chapman, D. A. (2004). « Why constrain your mutual fund manager? ». *Journal of Financial Economics*, 73(2), 289-321. | https://doi.org/10.1016/j.jfineco.2003.05.007 | Résumé | Restrictions d'investissement des fonds |
| Almgren, R. et Chriss, N. (2001). « Optimal execution of portfolio transactions ». *Journal of Risk*, 3(2). | https://doi.org/10.21314/JOR.2001.041 | Résumé | Coût et délai de liquidation ; VaR ajustée de la liquidité |
| AMF-UMOA, ex-CREPMF (2021). *Instruction n° 66/CREPMF/2021 relative aux organismes de placement collectif et à leurs sociétés de gestion sur le marché financier régional de l'UMOA*. | https://www.amf-umoa.org/reglementation/instruction | Liste des textes (texte non lu) | Ratios réglementaires des OPC de l'UMOA |
| Bangia, A., Diebold, F. X., Schuermann, T. et Stroughair, J. D. (1999). « Modeling liquidity risk, with implications for traditional market risk measurement and management ». Document de travail, Wharton Financial Institutions Center, 99-06. | https://ideas.repec.org/p/wop/pennin/99-06.html | Résumé | Risque de liquidité exogène et endogène |
| Barone-Adesi, G., Giannopoulos, K. et Vosper, L. (1999). « VaR without correlations for portfolios of derivative securities ». *Journal of Futures Markets*, 19(5), 583-602. | https://ideas.repec.org/a/wly/jfutmk/v19y1999i5p583-602.html | Résumé | Simulation historique filtrée |
| Bouveret, A. (2017). « Liquidity stress tests for investment funds: a practical guide ». Document de travail du FMI, WP/17/226. | https://doi.org/10.5089/9781484324783.001 | Résumé | Cadre des tests de liquidité des fonds |
| Breuer, T., Jandačka, M., Rheinberger, K. et Summer, M. (2009). « How to find plausible, severe, and useful stress scenarios ». *International Journal of Central Banking*, 5(3), 205-224. | https://www.ijcb.org/journal/v5n3/how-find-plausible-severe-and-useful-stress-scenarios | Résumé | Scénarios plausibles et sévères |
| Chen, Q., Goldstein, I. et Jiang, W. (2010). « Payoff complementarities and financial fragility: evidence from mutual fund outflows ». *Journal of Financial Economics*, 97(2), 239-262. | https://doi.org/10.1016/j.jfineco.2010.03.016 | Résumé | Rachats et illiquidité des actifs |
| Chevalier, J. et Ellison, G. (1997). « Risk taking by mutual funds as a response to incentives ». *Journal of Political Economy*, 105(6), 1167-1200. | https://doi.org/10.1086/516389 | Résumé | Relation entre flux et performance |
| Christoffersen, P. F. (1998). « Evaluating interval forecasts ». *International Economic Review*, 39(4), 841-862. | https://doi.org/10.2307/2527341 | Résumé | Test de couverture des prévisions |
| Coval, J. et Stafford, E. (2007). « Asset fire sales (and purchases) in equity markets ». *Journal of Financial Economics*, 86(2), 479-512. | https://doi.org/10.1016/j.jfineco.2006.09.007 | Résumé | Ventes forcées après rachats |
| ESMA (2020). *Guidelines on liquidity stress testing in UCITS and AIFs*. ESMA34-39-897. | https://www.esma.europa.eu/node/91900 | Présentation | Tests de liquidité réglementaires |
| Glasserman, P., Kang, C. et Kang, W. (2015). « Stress scenario selection by empirical likelihood ». *Quantitative Finance*, 15(1), 25-41. | https://doi.org/10.1080/14697688.2014.926019 | Résumé | Stress inverse : scénarios les plus probables au-delà d'un seuil |
| Gneiting, T. et Raftery, A. E. (2007). « Strictly proper scoring rules, prediction, and estimation ». *Journal of the American Statistical Association*, 102(477), 359-378. | https://doi.org/10.1198/016214506000001437 | Résumé | Évaluation des prévisions probabilistes |
| Goldstein, I., Jiang, H. et Ng, D. T. (2017). « Investor flows and fragility in corporate bond funds ». *Journal of Financial Economics*, 126, 592-613. | https://doi.org/10.1016/j.jfineco.2016.11.007 | Résumé | Fragilité des fonds obligataires |
| IOSCO (2018). *Recommendations for Liquidity Risk Management for Collective Investment Schemes*. Rapport final FR01/2018. | https://api.iosco.org/library/pubdocs/pdf/IOSCOPD590.pdf | Présentation | Gestion du risque de liquidité des fonds ouverts |
| MFSA, Malta Financial Services Authority (2025). *Liquidity stress testing of Maltese retail investment funds: 2025 update*. | https://www.mfsa.mt/publication/liquidity-stress-testing-for-maltese-retail-investment-funds-2025-update/ | Présentation | Fonds de fonds : parts de fonds cibles illiquides sous tension |
| Pastor, L., Sikorskaya, T. et Wang, J. (2026). « The hidden cost of stock market concentration: when funds hit regulatory limits ». Document de travail NBER 35007. | https://ideas.repec.org/p/bfi/wpaper/2026-51.html | Résumé | Limites de concentration qui mordent |
| République française. *Code monétaire et financier*, partie réglementaire, articles R214-21 à R214-29 (ratios d'investissement des OPCVM). | https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006072026/LEGISCTA000024429045/2020-10-01 | Extraits | Règle 5/10/40, point de comparaison |
| Sirri, E. R. et Tufano, P. (1998). « Costly search and mutual fund flows ». *Journal of Finance*, 53(5), 1589-1622. | https://doi.org/10.1111/0022-1082.00066 | Résumé | Asymétrie des flux selon la performance |

Détails à vérifier : année et numéro d'Almgren et Chriss (2000 ou 2001 selon les sources) ; DOI de Barone-Adesi et al. (1999) ; auteurs du document NBER de Pastor et al. (une page en liste d'autres).

## À confirmer

Références repérées mais pas encore vérifiées ou pas encore lues ; elles ne sont pas citées.

- Les seize circulaires d'application de l'Instruction n° 66/CREPMF/2021 (3 janvier 2022) : ratios chiffrés, traitement des dépassements, investissement dans d'autres OPC.
- Une étude publiée sur Zenodo le 2 juillet 2024, « Analyse de la persistance des performances des fonds communs de placement au niveau de la BRVM » (23 FCP) : auteurs et revue non retrouvés. https://zenodo.org/records/12628485
- La pratique indienne des « dépassements passifs » (circulaire SEBI de 2025, délai de régularisation de 30 jours ouvrés) : vue dans la presse seulement.
- Les ouvrages et rapports sur le développement des OPCVM dans l'UMOA (CODESRIA) : non consultés.
