"""Construit l'article Word « Fear & Greed BRVM » à partir de sortie/chiffres.json, des tableaux et des figures.

    recherche/.venv/Scripts/python.exe recherche/fear_greed/article.py

Chaque nombre du texte vient de chiffres.json ({p:cle:dec}, {n:cle:dec}…) ; un chiffre absent fait échouer
la construction, comme un renvoi inconnu ou un tiret cadratin.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI.parent))
from commun import mise_en_forme  # noqa: E402
from commun.mise_en_forme import (WD_ALIGN_PARAGRAPH, Article, BLEU, Cm, Pt, fr, lire,  # noqa: E402
                                  valeur)

mise_en_forme.configurer(ICI / "sortie")
NOM = "Fear_Greed_BRVM"
ZONES = ["Peur extrême", "Peur", "Neutre", "Cupidité", "Cupidité extrême"]
NOTE_CRITERES = ("Note : validité : moyenne des corrélations de rang du score avec la volatilité (signe inversé), "
                 "l'écart au plus haut et la part intra-annuelle des séances illiquides (signe inversé) ; information : "
                 "corrélation de rang avec le rendement des 60 séances suivantes ; écart des extrêmes : rendement moyen "
                 "sur 60 séances après la peur extrême, moins celui qui suit la cupidité extrême ; équilibre : entropie "
                 "normalisée de la répartition entre les zones.")


def pc(x, dec=1, signe=False):
    return "n.d." if pd.isna(x) else fr(x * 100, dec, signe) + " %"


def nb(x, dec=2, signe=False):
    return "" if pd.isna(x) else fr(x, dec, signe)


# ---------------------------------------------------------------------------
# Tableaux
# ---------------------------------------------------------------------------

def t_marche() -> pd.DataFrame:
    t = lire("t1_marche_par_annee")
    return pd.DataFrame({
        "Année": t.index.astype(str),
        "Indice de cours": [pc(x) for x in t["brvmc"]],
        "Dividendes réinvestis": [pc(x) for x in t["brvmc_rt"]],
        "Volatilité": [pc(x, 1) for x in t["volatilite"]],
        "Séances illiquides": [pc(x, 0) for x in t["seances_illiquides"]],
        "Poids Sonatel": [pc(x, 0) for x in t["poids_sonatel"]],
        "Titres effectifs": [nb(x, 1) for x in t["titres_effectifs"]],
        "Valeur échangée (Mds FCFA)": [nb(x, 0) for x in t["valeur_echangee_mds"]],
        "Rendement en dividendes": [pc(x, 1) for x in t["rendement_dividendes"]],
        "Sociétés": [str(int(x)) for x in t["titres_cotes"]],
    })


def t_dimensions() -> pd.DataFrame:
    return pd.DataFrame([
        ["Tendance", "Écart à la moyenne de 125 jours (CNN) ; extrapolation des rendements passés (Greenwood et "
         "Shleifer, 2014)", "Disponible", "Momentum"],
        ["Largeur", "Titres en hausse et en baisse (Brown et Cliff, 2004) ; nouveaux plus hauts et plus bas sur 52 "
         "semaines (CNN ; George et Hwang, 2004)", "Disponible", "Participation, force"],
        ["Volumes et liquidité", "Volumes des titres en hausse et en baisse (CNN) ; rotation des titres (Baker et "
         "Wurgler, 2006) ; liquidité (Baker et Stein, 2004)", "Valeurs échangées et séances",
         "Demande ; séances illiquides en validation (H1)"],
        ["Volatilité", "Volatilité implicite (CNN) ; risque de baisse (Ang, Chen et Xing, 2006 ; Estrada, 2002)",
         "Réalisée seulement", "Volatilité baissière"],
        ["Demande relative", "Valeurs refuges, écart des obligations à haut rendement (CNN)",
         "Non : pas de marché obligataire liquide", ""],
        ["Positionnement et émissions", "Options de vente et d'achat (CNN) ; introductions en bourse, émissions "
         "d'actions, décote des fonds fermés (Baker et Wurgler, 2006) ; flux des fonds (Baker et Wurgler, 2007)",
         "Non : pas de dérivés, opérations trop rares, flux non publiés chaque jour", ""],
        ["Attention et tonalité", "Recherches en ligne (Da, Engelberg et Gao, 2015) ; enquêtes ; presse",
         "Non exploitée", ""],
    ], columns=["Dimension", "Indicateurs dans la littérature", "Données BRVM", "Composante retenue"])


def t_composantes() -> pd.DataFrame:
    return pd.DataFrame([
        ["Momentum", "Écart du BRVM Composite à sa moyenne mobile de 125 séances", "Indice au-dessus de sa tendance",
         "({eq:momentum})"],
        ["Participation", "Part des titres cotés au-dessus de leur moyenne mobile de 50 séances",
         "Hausse partagée par la majorité", "({eq:participation})"],
        ["Force", "Nouveaux plus hauts moins nouveaux plus bas sur 52 semaines, rapportés au nombre de titres, "
                  "moyenne sur 10 séances", "Plus hauts nombreux", "({eq:force})"],
        ["Demande", "Part de la valeur échangée (FCFA) allant aux titres en hausse, sur 20 séances",
         "Capitaux vers les titres qui montent", "({eq:demande})"],
        ["Volatilité baissière", "Semi-volatilité de l'indice sur 20 séances rapportée à celle de 120 séances, "
                                 "signe inversé", "Calme dans les baisses", "({eq:volatilite})"],
    ], columns=["Composante", "Mesure", "Lecture « cupidité »", "Éq."])


def t_correlations() -> pd.DataFrame:
    c = lire("t3_correlations_composantes")
    noms = {"momentum": "Momentum", "participation": "Participation", "force": "Force", "demande": "Demande",
            "vol_baissiere": "Volatilité baissière"}
    d = pd.DataFrame({noms[k]: [nb(v, 2) for v in c[k]] for k in c.columns})
    d.insert(0, "", [noms[k] for k in c.index])
    return d


def t_h1_zones() -> pd.DataFrame:
    z = lire("t5b_h1_par_zone").reindex(ZONES)
    parts = [valeur(f"v2_part_zone_{i}") for i in range(5)]
    return pd.DataFrame({
        "Zone": ZONES,
        "Part du temps": [pc(x, 1) for x in parts],
        "Volatilité (20 séances)": [pc(x, 1) for x in z["vol_20"]],
        "Écart au plus haut (1 an)": [pc(x, 1) for x in z["perte_depuis_haut"]],
        "Séances illiquides (écart à l'année, points)": [nb(x * 100, 1, True) for x in z["sans_echange_20"]],
        "Illiquidité d'Amihud (écart à l'année, log)": [nb(x, 2, True) for x in z["amihud_20"]],
    })


def t_h1_reg() -> pd.DataFrame:
    t = lire("t5_h1_validite")
    noms = {"vol_20": "Volatilité (20 séances)", "perte_depuis_haut": "Écart au plus haut (1 an)",
            "sans_echange_20": "Séances illiquides (intra-annuel)", "amihud_20": "Illiquidité d'Amihud (intra-annuel)"}
    lignes = []
    for mes, nom in noms.items():
        l = [nom]
        for v in ("v2", "v2 sans volatilité baissière", "v2 sans momentum"):
            x = t[(t["version"] == v) & (t["mesure"] == mes)].iloc[0]
            l.append(f"{nb(x['spearman'], 2, True)} ({nb(x['t_hac'], 1, True)})")
        lignes.append(l)
    return pd.DataFrame(lignes, columns=["Mesure de l'état du marché", "Indice complet", "Sans volatilité baissière",
                                         "Sans momentum"])


def t_h2_zones() -> pd.DataFrame:
    t = lire("t6_h2_zones")
    lignes = []
    for z in ZONES:
        l = [z]
        for h in (20, 60, 120):
            x = t[(t["horizon"] == h) & (t["zone"] == z)].iloc[0]
            l.append(pc(x["rendement_moyen"], 1, True))
            l.append("réf." if z == "Neutre" else f"{pc(x['ecart_a_neutre'], 1, True)} ({nb(x['t_hac'], 1, True)})")
        lignes.append(l)
    return pd.DataFrame(lignes, columns=["Zone", "20 s. : moyenne", "20 s. : écart (t)", "60 s. : moyenne",
                                         "60 s. : écart (t)", "120 s. : moyenne", "120 s. : écart (t)"])


def t_h2_controle() -> pd.DataFrame:
    lignes = []
    for h in (20, 60, 120):
        lignes.append([f"{h} séances",
                       f"{nb(valeur(f'h2_pente_lin_{h}') * 100, 2, True)} ({nb(valeur(f'h2_t_lin_{h}'), 1, True)})",
                       nb(valeur(f"h2_t_quad_{h}"), 1, True),
                       nb(valeur(f"h2_ic_{h}"), 2, True),
                       f"{nb(valeur(f'h2_ic_sans_recouvrement_{h}'), 2, True)} (p = {nb(valeur(f'h2_p_sans_recouvrement_{h}'), 3)} ; n = {int(valeur(f'h2_n_sans_recouvrement_{h}'))})",
                       nb(valeur(f"h2_t_passe_h_{h}"), 1, True),
                       nb(valeur(f"h2_t_score_controle_{h}"), 1, True)])
    return pd.DataFrame(lignes, columns=["Horizon", "Pente pour 10 points, en % (t)", "t quadratique",
                                         "Corrélation de rang", "Sans recouvrement", "t du rendement passé",
                                         "t du score contrôlé"])


def t_h3() -> pd.DataFrame:
    rows = []
    for cible, nom in (("mediane_titres_20", "Rendement du titre médian (20 séances)"),
                       ("part_hausse_20", "Part des titres en hausse (20 séances)")):
        rows.append([nom, pc(valeur(f"h3_r2_momentum_{cible}"), 1), pc(valeur(f"h3_r2_momentum_participation_{cible}"), 1),
                     nb(valeur(f"h3_t_participation_{cible}"), 1, True), nb(valeur(f"h3_t_force_{cible}"), 1, True)])
    return pd.DataFrame(rows, columns=["Variable expliquée", "R² : momentum seul", "R² : momentum, participation, force",
                                       "t de la participation", "t de la force"])


def t_h4() -> pd.DataFrame:
    t = lire("t7_h4_saison")
    return pd.DataFrame({
        "Version": ["Indice de cours (version initiale)", "Dividendes réinvestis"],
        "Score : écart mai-juillet (points)": [f"{nb(x, 1, True)} ({nb(tt, 1, True)})" for x, tt in zip(t["ecart_mai_juillet"], t["t_hac"])],
        "Momentum : écart mai-juillet (points)": [f"{nb(x, 1, True)} ({nb(tt, 1, True)})" for x, tt in zip(t["ecart_momentum"], t["t_momentum"])],
    })


def _criteres(t: pd.DataFrame, avec_echantillon: bool = True) -> pd.DataFrame:
    d = pd.DataFrame({
        "Version": t["version"],
        "Validité": [nb(x, 2) for x in t["validite"]],
        "Information": [nb(x, 2, True) for x in t["ic_futur_60"]],
        "Écart des extrêmes": [pc(x, 1, True) for x in t["ecart_extremes_60"]],
        "Changements de zone par an": [nb(x, 0) for x in t["changements_par_an"]],
        "Équilibre des zones": [nb(x, 2) for x in t["equilibre_zones"]],
    })
    if avec_echantillon:
        d.insert(0, "Échantillon", ["validation" if e == "validation" else "test" for e in t["echantillon"]])
    return d


def t_h5() -> pd.DataFrame:
    return _criteres(lire("t8_h5_ponderations"))


def t_robustesse() -> pd.DataFrame:
    t = lire("t9_robustesse")
    d = _criteres(t, False)
    d["Corrélation avec l'indice"] = [nb(x, 2) for x in t["corr_avec_complet"]]
    d["Version"] = [v.replace("fenêtre 252", "fenêtre de 252 séances").replace("fenêtre 756", "fenêtre de 756 séances")
                    .replace("fenêtre croissant", "rang sur tout l'historique") for v in t["version"]]
    return d


def t_v2_v3() -> pd.DataFrame:
    return _criteres(lire("t11_v2_v3"))


def t_candidats() -> pd.DataFrame:
    t = lire("t10_candidats_validation")
    return pd.DataFrame({
        "Fenêtre": t["fenetre"].astype(int).astype(str),
        "Agrégation": ["trois piliers" if s == "piliers" else "poids égaux" for s in t["schema"]],
        "Lissage (séances)": t["lissage"].astype(int).astype(str),
        "Validité": [nb(x, 2) for x in t["validite"]],
        "Information": [nb(x, 2, True) for x in t["ic_futur_60"]],
        "Changements de zone par an": [nb(x, 0) for x in t["changements_par_an"]],
        "Équilibre des zones": [nb(x, 2) for x in t["equilibre_zones"]],
        "Note de synthèse": [nb(x, 2, True) for x in t["note"]],
    })


def t_robustesse_illiquidite() -> pd.DataFrame:
    t = lire("t12_robustesse_illiquidite")
    noms = {"fige2": "Aucun échange, ou plus de 2 clôtures égales", "etude": "Aucun échange, ou plus de 3 clôtures "
            "égales (étude)", "fige5": "Aucun échange, ou plus de 5 clôtures égales", "volume": "Aucun échange seulement",
            "lot": "Aucun échange, ou rendement nul (Lesmond et al., 1999)"}
    return pd.DataFrame({
        "Définition": [noms[k] for k in t.index],
        "Part 2008-2012": [pc(x, 0) for x in t["part_2008_2012"]],
        "Part depuis 2022": [pc(x, 0) for x in t["part_2022_fin"]],
        "Part en 2026": [pc(x, 0) for x in t["part_2026"]],
        "H1 : corrélation (t)": [f"{nb(r, 2, True)} ({nb(x, 1, True)})" for r, x in zip(t["h1_spearman"], t["h1_t_hac"])],
        "Validité : validation": [nb(x, 2) for x in t["validite_v2_validation"]],
        "Validité : test": [nb(x, 2) for x in t["validite_v2_test"]],
        "Corrélation avec l'étude": [nb(x, 2) for x in t["corr_avec_etude"]],
    })


def t_controle_dividendes() -> pd.DataFrame:
    t = lire("t13_controle_dividendes")
    t["Date_Detachement"] = pd.to_datetime(t["Date_Detachement"])
    cas = {"courant": "Au plus 15 % du cours de la veille", "baisse": "Au-delà de 15 %, baisse du cours confirmée",
           "corrige": "Au-delà de 15 %, confirmé à la source", "ecarte": "Au-delà de 15 %, non confirmé",
           "sans_cours": "Pas de cours la veille du détachement", "apres_fin": "Détachement après la dernière séance"}

    def detail(g: pd.DataFrame, st: str) -> str:
        if st == "courant":
            return f"part médiane du cours : {pc(g['part_du_cours'].median(), 1)}" if len(g) else ""
        if st == "sans_cours":
            return " ; ".join(f"{t_.split('.')[0]}, exercice{'s' if len(e) > 1 else ''} "
                              + " et ".join(str(int(v)) for v in e) for t_, e in g.groupby("Ticker")["Exercice"])
        morceaux = []
        for x in g.itertuples():
            m = f"{x.Ticker.split('.')[0]}, exercice {int(x.Exercice)}"
            if st == "apres_fin":
                m += f" (détachement le {x.Date_Detachement:%d/%m/%Y})"
            elif pd.notna(x.part_du_cours):
                m += f" : {pc(x.part_du_cours, 1)} du cours, baisse de {pc(x.baisse_du_jour, 1)}"
            morceaux.append(m)
        return " ; ".join(morceaux)

    lignes = [[nom, "Retenu" if st in ("courant", "baisse", "corrige") else "Écarté",
               str(int((t["statut"] == st).sum())), detail(t[t["statut"] == st], st)] for st, nom in cas.items()]
    lignes.append(["**Total**", "", str(len(t)), f"dont {int(t['retenu'].sum())} retenus"])
    return pd.DataFrame(lignes, columns=["Cas", "Décision", "Nombre", "Détail"])


def p_valeur(x: float) -> str:
    return "< 0,001" if x < 0.001 else nb(x, 3)


def t_descriptives() -> pd.DataFrame:
    t = lire("t15_descriptives")
    lignes = [("Séances", "n", lambda x: str(int(x))), ("Rendement moyen annualisé", "moyenne_annuelle", lambda x: pc(x, 1)),
              ("Volatilité annualisée", "volatilite_annuelle", lambda x: pc(x, 1)),
              ("Asymétrie", "asymetrie", lambda x: nb(x, 2, True)), ("Kurtosis en excès", "kurtosis", lambda x: nb(x, 1)),
              ("Rendement quotidien le plus faible", "min", lambda x: pc(x, 1, True)),
              ("Rendement quotidien le plus fort", "max", lambda x: pc(x, 1, True)),
              ("Autocorrélation des rendements (1 séance)", "autocorr_1", lambda x: nb(x, 3, True)),
              ("Autocorrélation des rendements absolus (1 séance)", "autocorr_abs_1", lambda x: nb(x, 2, True)),
              ("Ljung-Box, 10 retards, rendements : p", "ljung_box_p", p_valeur),
              ("Ljung-Box, 10 retards, rendements absolus : p", "ljung_box_abs_p", p_valeur)]
    d = pd.DataFrame([[nom, f(t.loc[k, "brvmc"]), f(t.loc[k, "brvmc_rt"])] for nom, k, f in lignes],
                     columns=["Statistique", "Indice de cours", "Dividendes réinvestis"])
    d.loc[len(d)] = ["Baisse du plus haut de 2015-2016 au plus bas de 2020", pc(valeur("cas_baisse_2016_2020"), 1), ""]
    return d


def t_concentration() -> pd.DataFrame:
    t = lire("t16_concentration")["valeur"]
    lignes = [[f"Poids de {k}", pc(t[k], 1)] for k in str(valeur("h3_grands")).split(", ")]
    lignes += [["Poids des cinq premières capitalisations", pc(t["cinq_premieres"], 1)],
               ["Indice de Herfindahl (somme des carrés des poids)", nb(t["hhi"], 3)],
               ["Titres effectifs (inverse de l'indice de Herfindahl)", nb(t["titres_effectifs"], 1)],
               ["Titres effectifs, moyenne de 2010", nb(t["titres_effectifs_2010"], 1)],
               ["Titres de poids non nul", str(int(t["titres_cotes"]))]]
    return pd.DataFrame(lignes, columns=["Mesure", "Valeur"])


def t_reconstitution() -> pd.DataFrame:
    t = lire("t17_reconstitution")
    noms = {"marche_avant_2019": "Marché reconstitué et BRVM Composite", "marche_depuis_2019": "Marché reconstitué et "
            "BRVM Composite", "rt_sikatr": "Dividendes réinvestis (reconstitué) et indice de rendement total SikaFinance"}
    return pd.DataFrame({"Comparaison des rendements quotidiens": [noms[k] for k in t.index],
                         "Période": [f"{a}-{b}" for a, b in zip(t["debut"], t["fin"])],
                         "Corrélation": [nb(x, 3) for x in t["correlation"]],
                         "Écart annualisé": [pc(x, 1) for x in t["ecart_annuel"]],
                         "Séances": [str(int(x)) for x in t["n"]]})


def t_proprietes() -> pd.DataFrame:
    t = lire("t18_proprietes_score")
    lignes = [("Autocorrélation à 1 séance", "autocorr_1", 2), ("Autocorrélation à 5 séances", "autocorr_5", 2),
              ("Autocorrélation à 20 séances", "autocorr_20", 2), ("Autocorrélation à 60 séances", "autocorr_60", 2),
              ("Durée moyenne d'un passage dans une zone (séances)", "duree_moyenne_zone", 1),
              ("Durée médiane d'un passage dans une zone (séances)", "duree_mediane_zone", 0),
              ("Changements de zone par an", "changements_par_an", 0),
              ("Corrélation de rang avec le rendement des 20 séances écoulées", "corr_passe_20", 2),
              ("Corrélation de rang avec le rendement des 20 séances à venir", "corr_futur_20", 2),
              ("Corrélation de rang avec le rendement des 60 séances à venir", "corr_futur_60", 2),
              ("Corrélation de rang avec l'autre version", "corr_autre_version", 2)]
    return pd.DataFrame([[nom, nb(t.loc[k, "v2"], d), nb(t.loc[k, "v3"], d)] for nom, k, d in lignes],
                        columns=["Propriété", "Version initiale", "Version révisée"])


def t_acp() -> pd.DataFrame:
    t = lire("t4_acp")
    return pd.DataFrame({"Composante principale": t.index, "Valeur propre": [nb(x, 2) for x in t["valeur_propre"]],
                         "Part de la variance": [pc(x, 1) for x in t["part"]],
                         "Part cumulée": [pc(x, 1) for x in t["part"].cumsum()]})


def t_acp_vecteur() -> pd.DataFrame:
    t = lire("t4b_acp_vecteur")
    noms = {"momentum": "Momentum", "participation": "Participation", "force": "Force", "demande": "Demande",
            "vol_baissiere": "Volatilité baissière"}
    return pd.DataFrame({"Composante": [noms[k] for k in t.index], "Poids dans la première composante principale":
                         [nb(x, 2) for x in t["CP1"]]})


def t_cas() -> pd.DataFrame:
    t = lire("t19_cas")
    lignes = [("Score (version initiale)", "score", None),
              ("Momentum : écart à la moyenne de 125 séances", "momentum", lambda x: pc(x, 1, True)),
              ("Participation : titres au-dessus de leur moyenne de 50 séances", "participation", lambda x: pc(x, 1)),
              ("Force : solde des plus hauts et plus bas, rapporté aux titres", "force", lambda x: pc(x, 1, True)),
              ("Demande : part de la valeur échangée sur les titres en hausse", "demande", lambda x: pc(x, 1)),
              ("Volatilité baissière : rapport 20 séances / 120 séances", "vol_baissiere", lambda x: nb(x, 2)),
              ("Participation : minimum sur deux ans", "participation_min_2ans", lambda x: pc(x, 1)),
              ("Participation : médiane sur deux ans", "participation_mediane_2ans", lambda x: pc(x, 1)),
              ("BRVM Composite : variation sur 20 séances", "indice_20", lambda x: pc(x, 1, True)),
              ("BRVM Composite : variation sur un an", "indice_1an", lambda x: pc(x, 1, True)),
              ("BRVM Composite : écart au plus haut d'un an", "indice_depuis_haut", lambda x: pc(x, 1, True)),
              ("Part des titres en hausse sur 20 séances", "part_titres_hausse_20", lambda x: pc(x, 1)),
              ("Rendement du titre médian sur 20 séances", "mediane_titres_20", lambda x: pc(x, 1, True))]
    return pd.DataFrame([[nom, f(t.loc[k, "valeur"]) if f else "", nb(t.loc[k, "rang"], 0)] for nom, k, f in lignes],
                        columns=["Mesure", "Valeur", "Rang (0-100)"])


def t_h3_complement() -> pd.DataFrame:
    lignes = [["Corrélation de rang entre les rendements de l'indice et du titre médian (20 séances)", "2009-2026",
               nb(valeur("h3_corr_indice_mediane_titres"), 2)],
              ["Séances où le momentum est au moins au rang 70 et la participation au plus au rang 30", "2009-2026",
               pc(valeur("h3_part_indice_haut_participation_basse"), 1)],
              ["Séances où les rangs du momentum et de la participation diffèrent de plus de 50 points", "2009-2026",
               pc(valeur("h3_part_divergence_50"), 1)],
              ["Version sans les cinq premières capitalisations : corrélation de rang avec la version initiale",
               "2020-2026", nb(valeur("h3_corr_v2_hors_grands"), 2)],
              ["Version sans les cinq premières capitalisations : séances dans la même zone", "2020-2026",
               pc(valeur("h3_meme_zone_hors_grands"), 0)],
              ["Corrélation de rang avec le rendement du titre médian : version initiale", "2020-2026",
               nb(valeur("h3_ic_v2_mediane_2020"), 2)],
              ["Corrélation de rang avec le rendement du titre médian : sans les cinq premières", "2020-2026",
               nb(valeur("h3_ic_hors_grands_mediane_2020"), 2)],
              ["Corrélation de rang avec le rendement du titre médian : version initiale", "2009-2026",
               nb(valeur("h3_ic_v2_mediane"), 2)],
              ["Corrélation de rang avec le rendement du titre médian : sans les cinq premières", "2009-2026",
               nb(valeur("h3_ic_hors_grands_mediane"), 2)]]
    return pd.DataFrame(lignes, columns=["Mesure", "Période", "Valeur"])


def t_collecte() -> pd.DataFrame:
    return pd.DataFrame([[nom, "Oui" if valeur(f"collecte_{k}_robots_lu") else "Non",
                          f"{fr(valeur(f'collecte_{k}_delai'), 1)} s", str(valeur(f"collecte_{k}_requetes")),
                          str(valeur(f"collecte_{k}_refusees"))]
                         for nom, k in (("www.sikafinance.com", "sika"), ("www.brvm.org", "brvm"))],
                        columns=["Domaine", "robots.txt lu", "Délai entre requêtes", "Requêtes", "Adresses refusées"])


ECHANTILLONS_ASYMETRIE = {"cours": "Indice de cours, 2008-2026", "cours_2008_2015": "Indice de cours, 2008-2015",
                          "cours_2016_2026": "Indice de cours, 2016-2026", "rt": "Dividendes réinvestis, 2008-2026"}


def t_asymetrie() -> pd.DataFrame:
    t = lire("t14_asymetrie_volatilite")

    ech = list(ECHANTILLONS_ASYMETRIE)

    def avec_t(k: str, kt: str) -> list[str]:
        return [f"{nb(t.loc[k, e], 3, True)} ({nb(t.loc[kt, e], 1, True)})" for e in ech]

    lignes = [["Séances", *[str(int(t.loc["n", e])) for e in ech]],
              ["Semi-volatilité des séances de hausse", *[pc(t.loc["semi_vol_hausse", e], 1) for e in ech]],
              ["Semi-volatilité des séances de baisse", *[pc(t.loc["semi_vol_baisse", e], 1) for e in ech]],
              ["Réaction aux hausses des 5 séances passées", *avec_t("reg_hausses", "reg_t_hausses")],
              ["Réaction aux baisses des 5 séances passées", *avec_t("reg_baisses", "reg_t_baisses")],
              ["Égalité des deux réactions : p", *[nb(t.loc["reg_p_egalite", e], 2) for e in ech]]]
    for k, nom in (("mu", "μ"), ("omega", "ω"), ("alpha", "α"), ("gamma", "γ (asymétrie)"), ("beta", "β")):
        lignes.append([f"GJR-GARCH : {nom}", *avec_t(f"gjr_{k}", f"gjr_t_{k}")])
    lignes.append(["Persistance (α + γ/2 + β)", *[nb(t.loc["gjr_persistance", e], 2) for e in ech]])
    return pd.DataFrame(lignes, columns=["Mesure", *ECHANTILLONS_ASYMETRIE.values()])


def t_donnees() -> pd.DataFrame:
    return pd.DataFrame([
        ["Cours de clôture des actions", "Quotidien, par titre", "2008-2026", "Cote de la BRVM, via SikaFinance", "Ajustés des divisions du nominal ; manquants les jours sans échange"],
        ["Volumes (titres et FCFA)", "Quotidien, par titre", "2008-2026", "Cote de la BRVM, via SikaFinance", "Valeurs en FCFA incomplètes avant 2013"],
        ["Indices publiés", "Quotidien", "2008-2026", "BRVM, via SikaFinance", "BRVM Composite, BRVM 30, Prestige, sectoriels"],
        ["Indice de rendement total SikaFinance", "Quotidien", "2019-2026", "SikaFinance", "Contrôle de l'indice dividendes réinvestis"],
        ["Dividendes", "Par détachement", "2016-2026", "Avis de la BRVM, SikaFinance", "Montants nets ; contrôle au tableau {tab:dividendes}"],
        ["Pondérations", "Quotidien, par titre", "2008-2026", "Cours et nombre de titres", "Vérifiées contre la capitalisation publiée depuis 2020"],
    ], columns=["Donnée", "Fréquence", "Période", "Source", "Traitement"])


def t_parametres() -> pd.DataFrame:
    return pd.DataFrame([
        ["Moyenne du momentum", "125 séances", "CNN (S&P 500 face à sa moyenne de 125 jours)"],
        ["Moyenne de la participation", "50 séances", "Titre coté sur au moins 60 des dernières séances"],
        ["Plus hauts et plus bas", "250 séances (52 semaines)", "Au moins 200 séances d'historique"],
        ["Lissage de la force", "10 séances", ""],
        ["Fenêtre de la demande", "20 séances", ""],
        ["Volatilité baissière", "20 contre 120 séances", "Semi-variance de l'indice"],
        ["Fenêtre du rang", "504 séances (version initiale), 756 (version révisée)", "Au moins 250 observations"],
        ["Zones", "0-25, 26-44, 45-55, 56-75, 76-100", "Échelle de CNN, score arrondi à l'entier"],
        ["Séance illiquide", "Aucun titre échangé, ou clôture identique sur plus de 3 séances consécutives",
         "Absence d'échange ou cours non actualisé ; seuil arbitraire, robustesse en annexe D"],
    ], columns=["Paramètre", "Valeur", "Commentaire"])


# ---------------------------------------------------------------------------
# Article
# ---------------------------------------------------------------------------

def construire() -> Path:
    a = Article()
    ratio_changements = valeur("v2_test_changements_par_an") / valeur("v3_test_changements_par_an")
    ecart_ae_60 = valeur("h2_60_4_ecart")
    blocs: list = []
    B = blocs.append

    # ----- Page de titre -----
    B(("titre_page",))
    # ----- Résumé -----
    B(("h1n", "Résumé"))
    B(("p", "Cet article construit et valide un indice composite de sentiment de type *Fear & Greed* (peur et cupidité) "
            "pour la Bourse Régionale des Valeurs Mobilières (BRVM), à partir des seules données publiques de marché : "
            "cours, volumes, indices et dividendes de {i:n_titres} sociétés, sur {i:n_seances} séances, du {s:date_debut} "
            "au {s:date_fin}. L'indice agrège cinq composantes (momentum de l'indice, participation des titres, nouveaux "
            "plus hauts et plus bas, demande, volatilité baissière), classées par rang percentile glissant et ramenées sur "
            "une échelle de 0 (peur extrême) à 100 (cupidité extrême). Trois résultats ressortent. D'abord, sur la BRVM, la "
            "peur se lit dans l'assèchement de la liquidité et l'éloignement du marché de son plus haut, et non dans la "
            "volatilité : une fois retirée la composante qui la contient, le lien entre le score et la volatilité disparaît. "
            "Ensuite, le sentiment annonce la poursuite de la tendance et non son retournement : les phases de cupidité "
            f"extrême sont suivies, sur 60 séances, de rendements supérieurs de {fr(ecart_ae_60 * 100, 1)} points à ceux des "
            "phases neutres ; au-delà d'un mois, cette information se confond avec l'inertie propre de l'indice, une "
            "anomalie cohérente avec l'inefficience au sens faible documentée sur ce marché. Enfin, sur un marché "
            "concentré, la participation des titres est l'information la plus précieuse : elle porte de "
            "{p:h3_r2_momentum_mediane_titres_20:0} à {p:h3_r2_momentum_participation_mediane_titres_20:0} la part "
            "expliquée du rendement du titre médian. Une version révisée (dividendes réinvestis, trois piliers, fenêtre de "
            f"trois ans, lissage) divise par {fr(ratio_changements, 1)} les changements de zone et améliore l'information "
            "sur les rendements futurs, au prix d'un léger retard. L'article en tire des recommandations pour la BRVM, "
            "le régulateur, les sociétés de gestion et d'intermédiation et les investisseurs."))
    B(("p", "**Mots-clés :** sentiment des investisseurs ; indice Fear & Greed ; BRVM ; UEMOA ; liquidité ; largeur de "
            "marché ; prévisibilité des rendements ; marchés frontières."))
    B(("p", "**Classification JEL :** G12, G14, G15, G41."))
    B(("saut",))
    B(("h1n", "Abstract"))
    B(("p", "This paper builds and validates a composite *Fear & Greed* sentiment index for the West African regional "
            "stock exchange (BRVM), using only public market data: prices, volumes, indices and dividends of "
            "{i:n_titres} listed companies over {i:n_seances} trading sessions, from January 2008 to October 2026. The "
            "index combines five components (index momentum, participation of stocks, new highs and lows, demand, "
            "downside volatility), each ranked against its own rolling history and mapped onto a 0 (extreme fear) to "
            "100 (extreme greed) scale. Three findings emerge. First, fear on the BRVM shows up as drying liquidity and "
            "distance from the market's high, not as volatility: once the volatility component is removed, the link "
            "between the score and volatility vanishes. Second, sentiment signals continuation rather than reversal: "
            f"extreme greed is followed by 60-session returns {fr(ecart_ae_60 * 100, 1).replace(',', '.')} percentage points "
            "above neutral periods; beyond one month, this information merges with the index's own momentum, an anomaly "
            "consistent with the weak-form inefficiency documented on this market. Third, in a concentrated market, "
            "participation is the most valuable piece of information: it raises the explained share of the median "
            "stock's return from {p:h3_r2_momentum_mediane_titres_20:0} to "
            "{p:h3_r2_momentum_participation_mediane_titres_20:0}. A revised index (total return, three pillars, "
            "three-year window, smoothing) cuts regime switches by a factor of "
            f"{fr(ratio_changements, 1).replace(',', '.')} and improves information on future returns, at the cost of a "
            "slight lag. Recommendations are drawn for the exchange, the regulator, brokers and asset managers, and "
            "investors."))
    B(("p", "**Keywords:** investor sentiment; Fear & Greed index; BRVM; WAEMU; liquidity; market breadth; return "
            "predictability; frontier markets."))
    B(("saut",))
    B(("h1n", "Sommaire"))
    B(("toc",))
    B(("saut",))

    # ----- 1. Introduction -----
    B(("h1", "1. Introduction"))
    B(("p", "En trente ans, la BRVM est devenue le marché d'actions commun des huit pays de l'Union Économique et "
            "Monétaire Ouest Africaine (UEMOA), première bourse régionale entièrement électronique au monde. Le marché "
            "a profondément changé sur la période étudiée : le nombre de sociétés cotées est passé de 27 en 2008 à "
            "{i:n_titres_fin} aujourd'hui, la part des séances sans échange ou à cours figé est tombée de "
            "{p:illiquide_2008_2012:0} en moyenne de 2008 à 2012 à {p:illiquide_2022_fin:0} depuis 2022, et le poids "
            "de Sonatel dans la capitalisation est revenu de {p:poids_sonatel_2008:0} à {p:poids_sonatel_fin:0}. Sur "
            "les douze derniers mois, le BRVM Composite a progressé de {p:cas_indice_1an:0}."))
    B(("p", "Ces transformations rendent plus pressant un besoin que la place n'a pas encore comblé : disposer d'un "
            "thermomètre synthétique de l'humeur du marché. Les investisseurs des marchés développés suivent des indices "
            "de sentiment, dont le plus connu est le *Fear & Greed Index* de CNN Business, qui combine sept indicateurs "
            "sur une échelle de 0 à 100. Plusieurs de ses ingrédients n'ont pas d'équivalent à la BRVM : il n'y existe "
            "ni options cotées, ni indice de volatilité implicite, ni marché liquide d'obligations à haut rendement. Une "
            "transposition directe est donc impossible, et une transposition naïve serait trompeuse : sur un marché où "
            "des titres ne s'échangent pas chaque jour et où quelques capitalisations font l'indice, un faible volume "
            "peut traduire la structure du marché plutôt que la peur, et une hausse de l'indice peut masquer la baisse "
            "de la majorité des titres."))
    B(("p", "La question de recherche est donc la suivante : comment mesurer l'alternance entre aversion et appétit "
            "pour le risque sur un marché frontière peu liquide et concentré, avec les seules données de marché "
            "disponibles, sans confondre sentiment, illiquidité structurelle et ruptures de données ? Et que vaut une "
            "telle mesure : décrit-elle fidèlement l'état du marché, et apporte-t-elle une information sur la suite ?"))
    B(("p", "L'article apporte quatre contributions. Il documente d'abord la construction, entièrement reproductible, "
            "d'un indice à cinq composantes adapté à la BRVM, dans une première version qui transpose aussi directement "
            "que possible la méthode de CNN. Il soumet ensuite cet indice à un protocole de validation sur dix-sept ans, "
            "avec des échantillons chronologiques distincts de calibration, de validation et de test, autour de cinq "
            "hypothèses propres à la BRVM. Il établit trois résultats : la peur s'y lit dans la liquidité et la largeur "
            "du marché plutôt que dans la volatilité ; le sentiment y annonce la poursuite de la tendance plutôt que son "
            "retournement ; la participation des titres y apporte l'information la plus précieuse. Il propose enfin une version révisée de l'indice et en tire des recommandations pour la "
            "place."))
    B(("p", "La littérature empirique consacrée à la BRVM s'est surtout attachée à l'efficience informationnelle au "
            "sens faible, que la plupart des travaux récents rejettent (Tan Toe, Toe et Zoungrana, 2023 ; Houndalidji, "
            "Tchindro et Hounkou, 2024), aux anomalies calendaires (Ben Mrad Douagi, Chaouachi et Mory, 2019) et au "
            "lien entre volume et volatilité (N'dri, 2007). Djahoué, Kacou Bi et Aba (2026) montrent qu'un indice de "
            "sentiment améliore la prévision de la volatilité de la BRVM. À notre connaissance, aucun travail ne propose "
            "pour la BRVM un indice composite de sentiment fondé sur la largeur et la liquidité du marché, dont la "
            "construction soit publiée et la validité éprouvée hors échantillon. C'est l'objet de cet article."))
    B(("p", "La section 2 situe le travail dans la littérature. La section 3 décrit le marché et les données. La "
            "section 4 présente la méthode. La section 5 décrit la version initiale de l'indice, la section 6 la soumet "
            "aux tests et "
            "la section 7 propose une version révisée. La section 8 formule des recommandations et la section 9 conclut."))

    # ----- 2. Littérature -----
    B(("h1", "2. Revue de la littérature"))
    B(("h2", "2.1 Le sentiment des investisseurs"))
    B(("p", "La finance comportementale admet que des investisseurs imparfaitement rationnels peuvent écarter durablement "
            "les prix de leur valeur, parce que l'arbitrage est risqué et limité (De Long, Shleifer, Summers et "
            "Waldmann, 1990 ; Shleifer et Vishny, 1997). Le sentiment, défini comme une croyance sur les flux futurs et "
            "les risques qui n'est pas justifiée par l'information disponible, n'est pas directement observable. Baker et "
            "Wurgler (2006, 2007) le mesurent par la composante commune de plusieurs indicateurs imparfaits et montrent "
            "qu'il affecte surtout les titres difficiles à évaluer et à arbitrer. Stambaugh, Yu et Yuan (2012) trouvent "
            "que les anomalies sont plus fortes après les périodes de sentiment élevé. Huang, Jiang, Tu et Zhou (2015) "
            "proposent d'aligner l'indice sur sa capacité à prévoir les rendements, et Da, Engelberg et Gao (2015) "
            "mesurent la peur des ménages par leurs recherches en ligne. Brown et Cliff (2004) observent que le "
            "sentiment est fortement corrélé aux rendements passés et contemporains, mais qu'il prévoit peu les "
            "rendements de court terme. Kumar et Lee (2006) relient les échanges des investisseurs individuels aux "
            "mouvements communs des titres qu'ils détiennent."))
    B(("h2", "2.2 Les indices de type Fear & Greed"))
    B(("p", "L'indice de CNN Business combine sept indicateurs, à poids égaux : le momentum du S&P 500 face à sa "
            "moyenne mobile de 125 jours, le solde des nouveaux plus hauts et plus bas sur 52 semaines, la largeur "
            "mesurée par les volumes des titres en hausse et en baisse, le ratio entre options de vente et d'achat, la "
            "volatilité implicite, la demande de valeurs refuges et l'écart de rendement des obligations à haut "
            "rendement. Sa méthode n'est publiée que dans ses grandes lignes. Naidoo, Moores-Pitt et Muzindutsi (2025) "
            "en construisent une version adaptée au marché sud-africain et montrent qu'elle reflète mieux les conditions "
            "locales qu'une transposition directe, ce qui justifie la démarche suivie ici. Dans les marchés frontières, "
            "l'absence de produits dérivés et de marché obligataire liquide oblige à s'en tenir aux actions."))
    B(("h2", "2.3 Tendance, largeur et volatilité asymétrique"))
    B(("p", "Les indicateurs de marché qu'utilisent CNN et Baker et Wurgler (2006, 2007) mesurent le sentiment parce "
            "que les croyances des investisseurs laissent une trace dans les prix et les échanges. La **tendance** en est "
            "la première. Les anticipations de rendement des investisseurs, mesurées par six sources d'enquêtes de 1963 à "
            "2011, suivent étroitement les rendements passés et le niveau du marché, et varient en sens inverse des "
            "rendements attendus des modèles (Greenwood et Shleifer, 2014), de même que le sentiment mesuré suit les "
            "rendements récents (Brown et Cliff, 2004 ; section 2.1). L'écart d'un "
            "indice à sa tendance capte ainsi l'extrapolation des investisseurs. Il a aussi un contenu prédictif : les "
            "règles fondées sur les moyennes mobiles ont un pouvoir explicatif sur les rendements (Brock, Lakonishok et "
            "LeBaron, 1992), et la persistance des tendances est documentée en coupe (Jegadeesh et Titman, 1993) et dans "
            "le temps (Moskowitz, Ooi et Pedersen, 2012) ; Hong et Stein (1999) l'expliquent par une diffusion "
            "progressive de l'information, qui fait réagir les prix avec retard."))
    B(("p", "La **largeur** du marché complète la tendance de l'indice. Brown et Cliff (2004) comptent le solde des "
            "titres en hausse et en baisse parmi les indicateurs indirects du sentiment, et la proximité du plus haut sur "
            "52 semaines est un repère suivi par les investisseurs (George et Hwang, 2004), ce qui donne un sens aux "
            "nouveaux plus hauts et plus bas que retient CNN. Les comportements moutonniers, mesurés par la dispersion "
            "des rendements entre titres, apparaissent en revanche aussi bien dans les paniques que dans les emballements "
            "(Christie et Huang, 1995 ; Chang, Cheng et Khorana, 2000) : la dispersion n'indique pas le sens du "
            "sentiment."))
    B(("p", "La **volatilité**, enfin, mesure la peur à deux titres. Sur les marchés développés, elle augmente davantage "
            "après les baisses qu'après les hausses (Black, 1976 ; Christie, 1982), asymétrie que mesure le modèle de "
            "Glosten, Jagannathan et Runkle (1993) ; c'est ce qui fait de la volatilité implicite un indicateur de peur. "
            "Par ailleurs, les investisseurs redoutent les pertes plus que la variabilité en général : les titres les "
            "plus exposés aux baisses du marché offrent une prime de rendement (Ang, Chen et Xing, 2006), et le risque "
            "mesuré sur les seules baisses rend mieux compte du risque des marchés émergents que le bêta classique "
            "(Estrada, 2002). La semi-variance, qui ne retient que les baisses, mesure directement ce risque."))
    B(("h2", "2.4 La liquidité dans les marchés émergents"))
    B(("p", "L'illiquidité se mesure par la réaction des prix aux volumes échangés (Amihud, 2002) ou, lorsque les "
            "données sont pauvres, par la fréquence des rendements nuls (Lesmond, Ogden et Trzcinka, 1999). Lesmond "
            "(2005) montre que ces mesures fondées sur les prix décrivent bien la liquidité des marchés émergents, et "
            "Bekaert, Harvey et Lundblad (2007) que la part des jours sans variation y prévoit les rendements futurs. "
            "Baker et Stein (2004) font de la liquidité elle-même un indicateur de sentiment : les marchés sont plus "
            "liquides quand les investisseurs optimistes y sont actifs. Lo et MacKinlay (1990) rappellent enfin que les "
            "échanges non synchrones créent mécaniquement une autocorrélation positive des rendements d'un indice, ce "
            "qui importe pour interpréter toute prévisibilité sur un marché peu liquide."))
    B(("h2", "2.5 Les travaux sur la BRVM"))
    B(("p", "Tan Toe, Toe et Zoungrana (2023), sur les données de 1998 à 2020, et Houndalidji, Tchindro et Hounkou "
            "(2024), sur le BRVM Composite de 2016 à 2022, concluent à l'inefficience de la BRVM au sens faible. Ben "
            "Mrad Douagi, Chaouachi et Mory (2019) y trouvent des effets du jour de la semaine et du mois de l'année. "
            "N'dri (2007) montre que le volume aide à prévoir la volatilité. Djahoué, Kacou Bi et Aba (2026) estiment "
            "plusieurs modèles de volatilité sur les données quotidiennes de 2010 à 2022 et montrent qu'un indice de "
            "sentiment en améliore la prévision. Le présent travail se distingue de ces études en construisant "
            "explicitement un indice de sentiment composite, en publiant sa méthode et en le validant sur des critères "
            "de description et de prévision, hors échantillon."))

    # ----- 3. Données -----
    B(("h1", "3. Le marché et les données"))
    B(("h2", "3.1 Un marché concentré, longtemps peu liquide"))
    B(("p", "Trois traits de la BRVM commandent la construction de l'indice (figure {fig:marche} et tableau {tab:marche}). "
            "Le marché est **concentré** : Sonatel représentait {p:poids_sonatel_2008:0} de la capitalisation en 2008 et "
            "en représente encore {p:poids_sonatel_fin:0} aujourd'hui ; les cinq premières capitalisations ({s:h3_grands}) en font "
            "{p:poids_5_grands_fin:0}. Mesuré par l'inverse de l'indice de Herfindahl, le marché équivalait à "
            "{n:titres_effectifs_2010:1} titres de même poids en 2010 et à {n:titres_effectifs_fin:1} aujourd'hui "
            "(tableau {tab:concentration} en annexe). Le "
            "marché a longtemps été **peu liquide** : de 2008 à 2012, {p:illiquide_2008_2012:0} des couples "
            "titre-séance étaient sans échange ou à cours figé, contre {p:illiquide_2022_fin:0} depuis 2022. Enfin, les "
            "**dividendes** sont élevés et concentrés dans le temps : le rendement en dividendes du marché a atteint en "
            "moyenne {p:rendement_dividendes_moyen:1} par an de 2019 à 2025 (tableau {tab:marche}), et "
            "{p:dividendes_mai_juillet:0} des "
            "dividendes sont détachés de mai à juillet, dont {p:dividendes_mai:0} en mai (figure {fig:dividendes}). Comme "
            "le BRVM Composite est un indice de cours, chaque détachement le fait baisser mécaniquement."))
    B(("fig", "marche", "f1_marche.png", "Le marché BRVM de 2008 à 2026.",
       "Note : la série dividendes réinvestis ajoute chaque jour au rendement du BRVM Composite le rendement en "
       "dividendes du marché (équation {eq:rt}) ; elle se confond avec l'indice de cours avant 2016, faute de dividendes "
       "dans la base. Séance illiquide : aucun titre échangé, ou clôture identique sur plus de trois séances "
       "consécutives (seuil arbitraire, d'après l'idée des rendements nuls de Lesmond, 2005 ; robustesse en annexe D)."))
    B(("p", "Les rendements quotidiens du BRVM Composite présentent les traits habituels des séries financières "
            "(tableau {tab:descriptives} et figure {fig:autocorr} en annexe) : une "
            "distribution à queues épaisses (kurtosis en excès de {n:brvmc_kurtosis:1}) et une volatilité qui se "
            "regroupe dans le temps (autocorrélation des rendements absolus de {n:brvmc_autocorr_abs_1:2} d'une séance à "
            "l'autre), alors que l'autocorrélation des rendements eux-mêmes est quasi nulle à un jour "
            "({n:brvmc_autocorr_1:3})."))
    B(("tab", "marche", "Le marché BRVM année par année.", t_marche(),
       "Note : rendements annuels du BRVM Composite publié et de sa version dividendes réinvestis ; volatilité "
       "annualisée des rendements quotidiens ; séances illiquides : moyenne sur les titres cotés ; titres effectifs : "
       "inverse de la somme des carrés des poids ; rendement en dividendes : somme sur l'année du rendement en "
       "dividendes du marché (équation {eq:rt}), disponible depuis {s:debut_dividendes} ; 2026 : jusqu'au "
       "{s:date_fin}. Les valeurs échangées avant 2013 paraissent incomplètes dans les sources.",
       [1.35, 1.6, 1.9, 1.6, 1.7, 1.3, 1.6, 1.7, 1.9, 1.4], 7.5))
    B(("h2", "3.2 Sources et collecte"))
    B(("p", "Les données proviennent de deux sites publics (tableau {tab:donnees} en annexe). Les cours de clôture, "
            "les volumes et les indices sont ceux de la cote de la BRVM, dont SikaFinance diffuse l'historique "
            "quotidien depuis 2008 : {i:n_titres} sociétés sur {i:n_seances} séances, du {s:date_debut} au "
            "{s:date_fin}. Les dividendes viennent des avis de paiement publiés par la BRVM, complétés par SikaFinance. "
            "Des programmes de collecte automatiques, exécutés chaque jour ouvré après la clôture, enregistrent ces "
            "données dans un dépôt GitHub. L'étude lit les fichiers de ce dépôt tels qu'ils sont à un commit figé "
            "({s:commit_brvm}) : chaque résultat peut ainsi être recalculé à l'identique, et le code de l'étude est "
            "indépendant de celui de la collecte (annexe G)."))
    B(("p", "La collecte respecte les règles d'accès publiées par chaque site. Avant la première requête vers un "
            "domaine, son fichier robots.txt est lu et interprété selon le protocole d'exclusion des robots (Koster, "
            "Illyes, Zeller et Sassman, 2022) : une adresse interdite n'est pas demandée, et deux requêtes vers un même "
            "domaine sont espacées au moins du délai demandé par le site, et jamais de moins de "
            "{n:collecte_sika_delai:1} seconde. Le robots.txt de la BRVM impose un délai de {i:collecte_brvm_delai} "
            "secondes, que la collecte applique ; celui de SikaFinance n'interdit aucune des pages consultées. Chaque "
            "exécution tient un journal des requêtes : lors de la collecte du {s:collecte_controle}, la dernière prise "
            "en compte, {i:collecte_sika_requetes} requêtes ont été adressées à SikaFinance et "
            "{i:collecte_brvm_requetes} à la BRVM, et aucune adresse n'a dû être écartée (tableau {tab:collecte} en "
            "annexe). Le plan de site (sitemap) de "
            "SikaFinance, déclaré dans son robots.txt, recense la page de cotation de chaque titre ; la BRVM n'en publie "
            "pas. Le robots.txt est une convention d'accès, non une licence : les données sont utilisées ici à des fins "
            "de recherche, avec mention de leurs sources."))
    B(("h2", "3.3 Traitements"))
    B(("p", "Quatre traitements comptent pour la suite. "
            "Les cours sont ajustés des divisions du nominal, pour que les rendements restent comparables. Un titre non "
            "échangé à une séance n'a pas de cours ce jour-là : aucun prix n'est inventé, et les moyennes s'appuient sur "
            "le dernier cours connu. Une séance est dite **illiquide** pour un titre lorsqu'aucun titre n'a été échangé, "
            "ou que sa clôture est restée identique sur plus de trois séances consécutives. Cette mesure s'inspire de la "
            "part des rendements nuls (Lesmond, Ogden et Trzcinka, 1999 ; Lesmond, 2005), mais ne retient que les cours "
            "durablement figés : une clôture inchangée un jour ou deux peut refléter un équilibre réel entre acheteurs "
            "et vendeurs, alors qu'une suite plus longue signale plutôt un cours non actualisé. Le seuil de trois "
            "séances est un choix arbitraire ; l'annexe D montre que les résultats n'en dépendent pas."))
    B(("p", "Les dividendes, que la base recense depuis {s:debut_dividendes}, sont contrôlés pour écarter les erreurs "
            "de saisie, qui créeraient de faux bonds dans l'indice dividendes réinvestis. Un dividende est retenu "
            "lorsque son montant ne dépasse pas {p:div_seuil:0} du cours de la veille du détachement, ordre de grandeur "
            "habituel sur la BRVM ; au-delà, il doit être confirmé par une baisse du cours d'au moins "
            "{p:div_confirmation:0} de son montant à la première clôture des {i:div_delai_jours} jours qui suivent, ou "
            "par l'avis publié par la BRVM. Ces seuils sont arbitraires. Sur {i:div_candidats} dividendes, "
            "{i:div_retenus} sont retenus (tableau {tab:dividendes} en annexe) ; "
            + ("les {i:div_ecartes} autres ne sont pas vérifiables, faute de cours avant le détachement ou parce que "
               "celui-ci intervient après la dernière séance de l'étude. Aucun n'est donc écarté pour un montant "
               "incohérent avec le cours." if valeur("div_n_ecarte") == 0 else
               "{i:div_n_ecarte} sont écartés pour un montant que le cours ne confirme pas.")))
    B(("h2", "3.4 Un BRVM Composite dividendes réinvestis"))
    B(("p", "La BRVM ne publie pas de version dividendes réinvestis de son indice composite. Elle est reconstituée en "
            "ajoutant chaque jour au rendement de l'indice publié le rendement en dividendes du marché :"))
    B(("eq", "rt", r"I^{RT}_t = I^{RT}_{t-1}\,\left(1 + r^{C}_t\right)\left(1 + d_t\right), \qquad d_t = \sum_i w_{i,t-1}\,\frac{D_{i,t}}{P_{i,t-1}}"))
    B(("leg", [(r"I^{RT}_t", "niveau de l'indice dividendes réinvestis à la séance t"),
               (r"r^{C}_t", "rendement du BRVM Composite publié"),
               (r"d_t", "rendement en dividendes du marché, nul hors détachement"),
               (r"w_{i,t-1}", "poids du titre i dans la capitalisation à la veille"),
               (r"D_{i,t}", "dividende net détaché par le titre i à la séance t"),
               (r"P_{i,t-1}", "cours de clôture du titre i la veille")]))
    B(("p", "Les poids sont les capitalisations de chaque titre (cours multiplié par le nombre de titres), "
            "recalculées à chaque collecte et vérifiées contre la capitalisation publiée par la BRVM. Seul le terme de "
            "dividende en "
            "dépend, si bien qu'une erreur de poids n'affecte que l'ordre de grandeur, faible, du rendement en "
            "dividendes. Depuis 2019, les rendements quotidiens de cette série et ceux de l'indice de rendement total "
            "publié par SikaFinance sont corrélés à {n:correlation_rt_sikatr:2}. Le marché pondéré reconstitué titre par "
            "titre reproduit le BRVM Composite avec une corrélation quotidienne de {n:fidelite_reconstitution_depuis_2019:3} "
            "depuis 2019, mais seulement de {n:fidelite_reconstitution_avant_2019:2} avant (tableau {tab:reconstitution} "
            "et figure {fig:reconstitution} en annexe) : il n'est donc utilisé, pour les tests de concentration, qu'à "
            "partir de 2020."))
    B(("fig", "dividendes", "f2_dividendes_par_mois.png",
       "Répartition des dividendes détachés selon le mois (rendement en dividendes du marché, 2016-2026).", None, 14))

    # ----- 4. Méthodologie -----
    B(("h1", "4. Méthodologie"))
    B(("h2", "4.1 Des indicateurs de la littérature aux données de la BRVM"))
    B(("p", "Le sentiment n'est pas observable directement. La littérature le mesure par plusieurs indicateurs de "
            "marché, dont chacun reflète en partie le sentiment et en partie des facteurs qui lui sont propres ; leur "
            "combinaison atténue ce bruit (Baker et Wurgler, 2006, 2007). L'indice de CNN applique le même principe "
            "avec sept indicateurs (section 2.2). La démarche suivie ici part de ces deux listes et retient, pour chaque "
            "dimension, l'indicateur que l'on peut mesurer chaque jour sur la BRVM avec des données publiques (tableau "
            "{tab:dimensions})."))
    B(("tab", "dimensions", "Dimensions du sentiment, indicateurs de la littérature et données disponibles pour la BRVM.",
       t_dimensions(), None, [2.9, 6.3, 3.2, 3.6], 8.5))
    B(("p", "Quatre dimensions sont mesurables. La **tendance** est mesurée par le momentum, écart de l'indice à sa "
            "moyenne de 125 séances repris de CNN : les anticipations des investisseurs extrapolent les rendements "
            "passés (Greenwood et Shleifer, 2014), si bien que cet écart mesure leur optimisme. La **largeur** est "
            "mesurée par la participation, part des titres au-dessus de leur moyenne, et par la force, solde des "
            "nouveaux plus hauts et plus bas : ce sont des mesures de largeur, dont Brown et Cliff (2004) comptent le "
            "solde des titres en hausse et en baisse parmi les indicateurs indirects du sentiment, et qui distinguent, "
            "sur un marché concentré (section 3.1), une hausse partagée d'une hausse portée par quelques "
            "capitalisations. Les **volumes** sont mesurés par la demande, part de la valeur échangée qui va aux titres "
            "en hausse, transposition de l'indicateur de volumes de CNN : la rotation des titres figure parmi les "
            "indicateurs de Baker et Wurgler (2006), et la liquidité augmente lorsque les investisseurs optimistes sont "
            "actifs (Baker et Stein, 2004). La part des séances illiquides, autre mesure de liquidité, est gardée hors "
            "de l'indice pour servir à le valider (H1) sans circularité. La **volatilité** est mesurée par la volatilité "
            "baissière : faute d'options, la volatilité implicite est remplacée par la volatilité réalisée, restreinte "
            "aux séances de baisse pour cibler le risque que redoutent les investisseurs (Ang, Chen et Xing, 2006 ; "
            "Estrada, 2002)."))
    B(("p", "Les autres indicateurs ne sont pas mesurables sur la BRVM. La place ne cote pas de produits dérivés, ce qui "
            "exclut le ratio des options de vente et d'achat et la volatilité implicite. Aucun marché obligataire n'y "
            "est assez liquide pour mesurer chaque jour la demande de valeurs refuges ou l'écart des obligations à haut "
            "rendement. Les introductions en bourse et les émissions d'actions sont trop rares pour une mesure "
            "quotidienne, aucun fonds fermé n'est coté, et les flux des fonds communs de placement ne sont pas publiés "
            "chaque jour. Il n'existe enfin ni enquête régulière auprès des investisseurs, ni série de recherches en "
            "ligne propre à la BRVM, et la tonalité de la presse n'est pas exploitée ici. Ces dimensions constituent une "
            "limite de l'étude et une piste d'amélioration."))
    B(("p", "Une composante n'est retenue que si elle remplit cinq conditions : être disponible chaque séance, avoir "
            "un historique suffisant, ne pas être révisée après publication, avoir une interprétation économique "
            "claire et apporter une information distincte des autres. La troisième condition tient à l'usage d'un indice "
            "publié chaque jour : un indice estimé sur tout l'échantillon, comme celui de Baker et Wurgler (2006), n'est "
            "connu qu'après coup, ce qui conduit Huang, Jiang, Tu et Zhou (2015) à évaluer le leur hors échantillon, "
            "avec la seule information disponible à chaque date. La dernière fonde la combinaison à poids égaux de CNN, "
            "reprise ici et mise à l'épreuve par H5."))
    B(("h2", "4.2 Les cinq composantes"))
    B(("p", "Chaque composante est une mesure brute, orientée de sorte qu'une valeur élevée corresponde à davantage de "
            "cupidité (tableau {tab:composantes}). Le **momentum** compare l'indice à sa tendance de moyen terme :"))
    B(("tab", "composantes", "Les cinq composantes de l'indice.", t_composantes(), None, [2.6, 7.4, 4.8, 1.2], 8.5))
    B(("eq", "momentum", r"M_t = \frac{I_t}{\frac{1}{125}\sum_{j=0}^{124} I_{t-j}} - 1"))
    B(("leg", [(r"I_t", "clôture du BRVM Composite à la séance t"),
               (r"M_t", "écart relatif de l'indice à sa moyenne mobile de 125 séances")]))
    B(("p", "La **participation** mesure la part des titres qui partagent la hausse :"))
    B(("eq", "participation", r"P_t = \frac{1}{N_t}\sum_{i=1}^{N_t} \mathbb{1}\left\{C_{i,t} > \bar{C}^{(50)}_{i,t}\right\}"))
    B(("leg", [(r"N_t", "nombre de titres suivis, c'est-à-dire cotés sur au moins 60 des dernières séances"),
               (r"C_{i,t}", "dernier cours connu du titre i"),
               (r"\bar{C}^{(50)}_{i,t}", "moyenne mobile de ses 50 dernières clôtures"),
               (r"\mathbb{1}\{\cdot\}", "indicatrice, égale à 1 si la condition est vraie")]))
    B(("p", "La **force** compte les titres à leur plus haut ou à leur plus bas de 52 semaines :"))
    B(("eq", "force", r"F_t = \frac{1}{10}\sum_{j=0}^{9} \frac{H_{t-j} - B_{t-j}}{N_{t-j}}"))
    B(("leg", [(r"H_t", "nombre de titres à leur plus haut des 250 dernières séances"),
               (r"B_t", "nombre de titres à leur plus bas des 250 dernières séances")]))
    B(("p", "La **demande** rapporte la valeur échangée sur les titres en hausse à la valeur échangée sur les titres qui "
            "varient :"))
    B(("eq", "demande", r"D_t = \frac{\sum_{j=0}^{19} V^{+}_{t-j}}{\sum_{j=0}^{19} \left(V^{+}_{t-j} + V^{-}_{t-j}\right)}"))
    B(("leg", [(r"V^{+}_t", "valeur échangée, en FCFA, sur les titres en hausse à la séance t"),
               (r"V^{-}_t", "valeur échangée sur les titres en baisse")]))
    B(("p", "La **volatilité baissière** compare l'ampleur récente des baisses de l'indice à leur ampleur habituelle, "
            "avec un signe inversé pour que le calme corresponde à la cupidité :"))
    B(("eq", "volatilite", r"S_t = -\frac{\sigma^{-}_{20,t}}{\sigma^{-}_{120,t}}, \qquad \sigma^{-}_{n,t} = \sqrt{\frac{1}{n}\sum_{j=0}^{n-1} \left[\mathrm{min}\left(r_{t-j},\,0\right)\right]^2}"))
    B(("leg", [(r"r_t", "rendement quotidien du BRVM Composite"),
               (r"\sigma^{-}_{n,t}", "semi-volatilité de l'indice sur les n dernières séances")]))
    B(("p", "La volatilité totale et la dispersion des rendements entre titres, présentes dans d'autres indices, ne "
            "sont pas retenues. Sur la BRVM, la volatilité ne réagit pas davantage aux baisses qu'aux hausses, à "
            "l'inverse de l'effet de levier observé sur les marchés développés. Du {s:date_debut} au {s:date_fin}, la "
            "semi-volatilité annualisée du BRVM Composite atteint {p:brvmc_semi_vol_baisse:1} dans les séances de "
            "baisse et {p:brvmc_semi_vol_hausse:1} dans les séances de hausse ; le rendement absolu réagit autant aux "
            "hausses qu'aux baisses des cinq séances précédentes (l'égalité des deux coefficients n'est pas rejetée, "
            "p = {n:brvmc_reg_p_egalite:2}) ; et dans un modèle GJR-GARCH (Glosten, Jagannathan et Runkle, 1993), le "
            "coefficient d'asymétrie vaut {ns:brvmc_gjr_gamma:2} (t de {ns:brvmc_gjr_t_gamma:1}), non significatif et "
            "de signe opposé à l'effet de levier ; ces résultats tiennent sur deux sous-périodes et sur l'indice "
            "dividendes réinvestis (annexe E). La volatilité totale ne dit donc pas, à elle seule, si le marché a "
            "peur, et la dispersion traduit un comportement moutonnier qui survient dans les paniques comme dans les "
            "emballements (section 2.3). Seule la volatilité des séances de baisse, au sens de la semi-variance, garde "
            "un sens de peur : elle mesure l'ampleur des pertes, que redoutent les investisseurs, indépendamment de "
            "celle des gains."))
    B(("h2", "4.3 Normalisation"))
    B(("p", "Les mesures brutes n'ont ni la même échelle ni la même distribution. Chacune est remplacée par son rang "
            "percentile parmi ses propres valeurs des N dernières séances, ce qui la situe par rapport à l'histoire "
            "récente du marché sans importer de seuil étranger :"))
    B(("eq", "rang", r"R_{k,t} = \frac{100}{N}\sum_{j=0}^{N-1} \mathbb{1}\left\{x_{k,t-j} \le x_{k,t}\right\}"))
    B(("leg", [(r"x_{k,t}", "mesure brute de la composante k à la séance t"),
               (r"N", "fenêtre du rang : 504 séances, soit environ deux ans, avec au moins 250 observations"),
               (r"R_{k,t}", "rang de 0 (la valeur la plus « peureuse » de la fenêtre) à 100 (la plus « cupide »)")]))
    B(("p", "Deux variantes servent aux tests de robustesse : le rang sur tout l'historique disponible, et un score "
            "robuste qui centre la mesure sur sa médiane glissante, la réduit par l'écart absolu médian et la convertit "
            "en probabilité par la loi normale :"))
    B(("eq", "robuste", r"R^{rob}_{k,t} = 100\,\Phi\!\left(\frac{x_{k,t} - \mathrm{m}_{k,t}}{1{,}4826\,\mathrm{MAD}_{k,t}}\right)"))
    B(("leg", [(r"\mathrm{m}_{k,t}", "médiane glissante de la mesure"),
               (r"\mathrm{MAD}_{k,t}", "médiane glissante des écarts absolus à cette médiane"),
               (r"\Phi", "fonction de répartition de la loi normale centrée réduite")]))
    B(("h2", "4.4 Agrégation et lecture"))
    B(("p", "Le score est la moyenne pondérée des rangs disponibles ; les poids sont renormalisés lorsqu'une composante "
            "manque, ce qui n'arrive qu'en début d'historique :"))
    B(("eq", "score", r"G_t = \frac{\sum_k w_k\,R_{k,t}}{\sum_k w_k\,\mathbb{1}\left\{R_{k,t}\ \text{disponible}\right\}}"))
    B(("leg", [(r"w_k", "poids de la composante k, égaux dans la version initiale"),
               (r"G_t", "score Fear & Greed, de 0 (peur extrême) à 100 (cupidité extrême)")]))
    B(("p", "Le score est lu sur l'échelle de CNN, après arrondi à l'entier : peur extrême de 0 à 25, peur de 26 à 44, "
            "neutre de 45 à 55, cupidité de 56 à 75, cupidité extrême de 76 à 100. Une échelle en quintiles (20, 40, 60, "
            "80) serait plus symétrique ; l'échelle de CNN est conservée pour que la lecture reste comparable à celle "
            "d'un indice familier des investisseurs."))
    B(("h2", "4.5 Protocole de validation"))
    B(("p", "L'historique est découpé en trois échantillons chronologiques : **calibration** de 2010 à 2018, "
            "**validation** de 2019 à 2022 et **test** de 2023 à octobre 2026. Les choix de méthode sont faits sur la "
            "calibration ou la validation, et jugés une seule fois sur le test. L'état du marché à chaque séance est "
            "décrit par quatre mesures calculées sur les 20 séances passées : la volatilité annualisée de l'indice "
            "dividendes réinvestis, son écart à son plus haut d'un an, la part des séances illiquides et la mesure "
            "d'illiquidité d'Amihud (2002), agrégée par la médiane des titres :"))
    B(("eq", "amihud", r"A_t = \mathrm{ln}\left[\,\mathrm{med}_i\left(\frac{1}{T_i}\sum_{j=0}^{19}\frac{\left|r_{i,t-j}\right|}{V_{i,t-j}}\right)\right]"))
    B(("leg", [(r"r_{i,t}", "rendement du titre i, les seuls jours où il est échangé"),
               (r"V_{i,t}", "valeur échangée sur le titre i, en millions de FCFA"),
               (r"T_i", "nombre de séances d'échange du titre i dans la fenêtre")]))
    B(("p", "La part des séances illiquides et la mesure d'Amihud ont fortement baissé d'année en année avec le "
            "développement du marché. Pour ne pas confondre cette tendance lente avec le sentiment, elles sont comparées "
            "au score en écart à leur moyenne de l'année. La prévisibilité est mesurée par les rendements logarithmiques "
            "de l'indice dividendes réinvestis sur les 20, 60 et 120 séances suivantes, dans la régression :"))
    B(("eq", "prevision", r"r_{t \to t+h} = \alpha + \beta\,G_t + \gamma\,r_{t-h \to t} + \delta\,r_{t-20 \to t} + \varepsilon_{t+h}"))
    B(("leg", [(r"r_{t \to t+h}", "rendement de l'indice sur les h séances qui suivent"),
               (r"r_{t-h \to t}", "rendement de l'indice sur les h séances passées, de même pour 20 séances"),
               (r"\varepsilon_{t+h}", "erreur, dont la variance est estimée selon Newey et West (1987) avec h retards")]))
    B(("p", "Les fenêtres qui se recouvrent gonflent artificiellement la significativité. Les écarts-types de Newey et "
            "West (1987) corrigent l'autocorrélation qui en résulte, et chaque résultat est vérifié sur des observations "
            "sans recouvrement, une toutes les h séances. Pour comparer des versions de l'indice, quatre critères sont "
            "calculés sur chaque échantillon : la **validité**, moyenne des corrélations de rang du score avec la "
            "volatilité (signe inversé), l'écart au plus haut et la part intra-annuelle des séances illiquides (signe "
            "inversé) ; l'**information**, corrélation de rang du score avec le rendement des 60 séances suivantes ; la "
            "**stabilité**, nombre de changements de zone par an ; l'**équilibre**, entropie normalisée de la répartition "
            "entre les cinq zones, égale à 1 lorsque toutes les zones sont aussi fréquentes."))
    B(("p", "Cinq hypothèses, propres à la BRVM, sont testées. **H1** (validité) : un score bas coïncide avec une "
            "volatilité plus forte, une illiquidité plus forte et un marché plus éloigné de son plus haut. **H2** "
            "(information des extrêmes) : les rendements qui suivent diffèrent selon la zone, et les zones extrêmes "
            "portent plus d'information que les zones centrales. **H3** (concentration) : sur un marché dominé par "
            "quelques capitalisations, la participation des titres apporte une information distincte du momentum de "
            "l'indice. **H4** (saison des dividendes) : calculé sur un indice de cours, le score confond les "
            "détachements de dividendes avec la peur. **H5** (simplicité) : hors échantillon, une pondération simple fait "
            "au moins aussi bien qu'une pondération statistique."))

    # ----- 5. Version initiale -----
    B(("h1", "5. La version initiale de l'indice"))
    B(("h2", "5.1 Dix-sept ans de sentiment"))
    B(("p", "L'indice est disponible à partir du {s:v2_debut}, une fois accumulées les 250 observations requises "
            "(figure {fig:v2}). Cette version initiale suit la méthode de CNN au plus près : cinq composantes à poids "
            "égaux, classées sur deux ans. Elle retrace les grandes phases du marché : la peur qui suit la crise financière de 2008, la "
            "cupidité de la hausse de 2012 à 2014, la peur persistante du long repli de 2016 à 2020, au cours duquel le "
            "BRVM Composite perd {p:cas_baisse_2016_2020:0} de sa valeur (tableau {tab:descriptives}), la cupidité extrême de la reprise de 2021, la "
            "peur extrême de la fin de 2022 et la cupidité de la hausse engagée en 2024."))
    B(("fig", "v2", "f4_score_v2.png", "Le BRVM Composite et l'indice Fear & Greed BRVM (version initiale), 2009-2026.",
       "Note : score quotidien et sa moyenne sur 60 séances ; bandes de couleur : zones de lecture."))
    B(("p", "Sur l'ensemble de la période, le marché a passé {p:v2_part_zone_0:0} du temps en peur extrême, "
            "{p:v2_part_zone_1:0} en peur, {p:v2_part_zone_2:0} en zone neutre, {p:v2_part_zone_3:0} en cupidité et "
            "{p:v2_part_zone_4:0} en cupidité extrême. Le score est persistant d'une séance à l'autre (autocorrélation "
            "de {n:v2_autocorr_1:2}), mais nettement moins à un mois ({n:v2_autocorr_20:2} à 20 séances), et il change de "
            "zone en moyenne toutes les {n:v2_duree_moyenne_zone:1} séances : sa lecture quotidienne est nerveuse "
            "(tableau {tab:proprietes} et figure {fig:autocorrscore} en annexe). Comme "
            "le notent Brown et Cliff (2004) pour d'autres marchés, il reflète d'abord le passé récent : sa corrélation "
            "de rang avec le rendement des 20 séances écoulées atteint {n:corr_v2_indice_passe_20:2}, contre "
            "{n:corr_v2_futur_20:2} avec celui des 20 séances à venir."))
    B(("h2", "5.2 Une structure dominée par la tendance"))
    B(("p", "Les composantes de tendance et de largeur sont nettement corrélées entre elles (tableau "
            "{tab:correlations} et figure {fig:acp}) : {n:corr_momentum_participation:2} entre le momentum et la "
            "participation, {n:corr_participation_force:2} entre la participation et la force, "
            "{n:corr_momentum_force:2} entre le momentum et la force. La demande et la volatilité baissière apportent en "
            "revanche une information largement distincte (corrélations de {n:corr_demande_vol_baissiere:2} entre elles "
            "et de {n:corr_momentum_vol_baissiere:2} entre le momentum et la volatilité baissière). La première "
            "composante principale explique {p:acp_part_1:0} de la variance des cinq rangs, la deuxième "
            "{p:acp_part_2:0} (tableaux {tab:acp} et {tab:acpvecteur} en annexe). Avec des poids égaux sur les cinq composantes, la dimension « tendance » compte donc de "
            "fait trois fois, ce qui motive l'agrégation par piliers testée à la section 7."))
    B(("tab", "correlations", "Corrélations entre les rangs des composantes (2009-2026).", t_correlations(), None,
       [3.2, 2.5, 2.5, 2.5, 2.5, 2.8], 9))
    B(("fig", "acp", "f5_correlations_acp.png", "Corrélations des composantes et analyse en composantes principales.", None))
    B(("h2", "5.3 Étude de cas : octobre 2026"))
    B(("p", "Le {s:date_fin}, la version initiale affiche {n:v2_dernier:0}, soit une « {s:v2_dernier_zone} », alors "
            "que le BRVM Composite se trouve à {p:cas_indice_depuis_haut:1} de son plus haut d'un an et a gagné "
            "{p:cas_indice_1an:0} en un an (figure {fig:cas} et tableau {tab:cas} en annexe). Le momentum de l'indice est à son rang {n:v2_dernier_momentum:0} "
            "sur 100 : l'indice reste {p:cas_brvmc_vs_mm125:0} au-dessus de sa moyenne de 125 séances. Mais la "
            "participation est tombée à {p:cas_participation_brute:0} des titres au-dessus de leur moyenne de 50 "
            "séances, près de son plus bas de deux ans ({p:cas_participation_min_2ans:0} le "
            "{s:cas_participation_min_2ans_date}, pour une médiane de {p:cas_participation_mediane_2ans:0}), la "
            "force est au rang {n:v2_dernier_force:0}, et la volatilité des baisses récentes de l'indice atteint "
            "{n:cas_vol_baissiere_ratio:1} fois son niveau habituel."))
    B(("p", "Le signal n'est pas une anomalie de calcul : il décrit un marché étroit. Sur les 20 dernières séances, "
            "l'indice est quasi stable ({ps:cas_indice_20:1}), mais seuls {p:cas_part_titres_hausse_20:0} des titres ont "
            "monté et le titre médian a perdu {p:cas_mediane_titres_20:1}. Quelques grandes capitalisations soutiennent "
            "l'indice pendant que la majorité des titres recule. C'est précisément l'information qu'un indice de cours "
            "ne montre pas, et que l'hypothèse H3 met à l'épreuve."))
    B(("fig", "cas", "f7_cas_octobre_2026.png", "Composantes et score de janvier à octobre 2026.", None))

    # ----- 6. Validation -----
    B(("h1", "6. Validation"))
    B(("h2", "6.1 H1 : la peur se lit dans la liquidité, pas dans la volatilité"))
    B(("p", "Le score varie dans le sens attendu avec l'état du marché (tableaux {tab:h1zones} et {tab:h1reg}, figure "
            "{fig:h1}). En peur extrême, l'indice se trouve en moyenne à {p:h1_perte_peur_extreme:1} de son plus haut "
            "d'un an, contre {p:h1_perte_avidite_extreme:1} en cupidité extrême ; la corrélation de rang entre le score "
            "et cet écart atteint {n:h1_v2_perte_depuis_haut_rho:2} (t de Newey-West de {n:h1_v2_perte_depuis_haut_t:1}). "
            "Le score est aussi plus bas lorsque les séances illiquides sont plus fréquentes que d'habitude dans l'année "
            "(corrélation de {n:h1_v2_sans_echange_20_rho:2}, t de {n:h1_v2_sans_echange_20_t:1}) et lorsque l'illiquidité "
            "d'Amihud est plus forte ({n:h1_v2_amihud_20_rho:2}, t de {n:h1_v2_amihud_20_t:1}). Ces liens subsistent "
            "lorsque l'on retire la composante de volatilité baissière ou celle de momentum : ils ne sont pas "
            "mécaniques."))
    B(("p", "Le lien avec la volatilité est plus faible ({n:h1_v2_vol_20_rho:2}) et, surtout, il disparaît lorsque la "
            "composante de volatilité baissière est retirée (tableau {tab:h1reg}). Autrement dit, sur la BRVM, la peur "
            "mesurée par le comportement des titres ne s'accompagne pas d'une volatilité plus forte : elle se manifeste "
            "par un marché qui s'éloigne de son plus haut et par des échanges qui se raréfient. Ce résultat rejoint "
            "l'observation, faite à la section 4.2, d'une volatilité symétrique sur ce marché, et l'idée de Baker et "
            "Stein (2004) selon laquelle la liquidité est elle-même un indicateur de sentiment. **H1 est validée pour la "
            "liquidité et l'écart au plus haut, rejetée pour la volatilité.**"))
    B(("tab", "h1zones", "État du marché selon la zone de l'indice (moyennes, 2009-2026).", t_h1_zones(),
       "Note : séances illiquides et illiquidité d'Amihud en écart à leur moyenne de l'année.",
       [2.6, 2.0, 2.5, 2.6, 3.3, 3.2], 8.5))
    B(("tab", "h1reg", "Corrélations de rang entre le score et l'état du marché (t de Newey-West entre parenthèses).",
       t_h1_reg(), "Note : 20 retards ; t de la pente d'une régression de la mesure sur le score.",
       [5.2, 3.6, 3.6, 3.6], 9))
    B(("fig", "h1", "f8_h1_validite.png", "État du marché selon la zone de l'indice.",
       "Note : PE peur extrême, P peur, N neutre, A cupidité, AE cupidité extrême ; boîtes : premier et troisième "
       "quartiles ; moustaches : 1,5 fois l'écart interquartile."))
    B(("h2", "6.2 H2 : le sentiment annonce la poursuite, pas le retournement"))
    B(("p", "La lecture usuelle d'un indice Fear & Greed est « à contre-courant » : la peur extrême signalerait un point "
            "bas, la cupidité extrême un excès. Les données de la BRVM ne la confirment pas (tableau {tab:h2zones} et "
            "figure {fig:h2}). Les rendements qui suivent croissent avec le score : sur 60 séances, l'indice progresse "
            "en moyenne de {ps:h2_60_4_moy:1} après une séance de cupidité extrême et de {ps:h2_60_3_moy:1} après une "
            "séance de cupidité, contre {ps:h2_60_2_moy:1} en zone neutre et {ps:h2_60_0_moy:1} après une séance de peur "
            "extrême. À 120 séances, la peur extrême est suivie d'un rendement inférieur de "
            f"{fr(abs(valeur('h2_120_0_ecart')) * 100, 1)} points à celui des périodes neutres "
            "(t de {n:h2_120_0_t:1})."))
    B(("tab", "h2zones", "Rendement de l'indice dividendes réinvestis après chaque zone.", t_h2_zones(),
       "Note : rendements logarithmiques moyens ; écart à la zone neutre et t de Newey-West (h retards) d'une régression "
       "sur les indicatrices de zone. 20 s. : 20 séances.", [2.6, 1.9, 2.4, 1.9, 2.4, 1.9, 2.4], 8))
    B(("fig", "h2", "f9_h2_rendements_futurs.png", "Rendement moyen de l'indice après chaque zone, selon l'horizon.",
       "Note : PE peur extrême, P peur, N neutre, A cupidité, AE cupidité extrême."))
    B(("p", "La relation est linéaire : le terme quadratique n'est significatif à aucun horizon (tableau "
            "{tab:h2controle}), et les zones extrêmes n'apportent pas d'information au-delà de leur position sur "
            "l'échelle. **H2 est rejetée** dans sa forme « à contre-courant » comme dans l'idée d'un contenu propre aux "
            "extrêmes. Deux précautions s'imposent toutefois. Sur des observations sans recouvrement, la corrélation reste "
            "nette à 20 séances ({n:h2_ic_sans_recouvrement_20:2}, p = {n:h2_p_sans_recouvrement_20:3}) mais n'est plus "
            "significative à 60 et 120 séances, faute d'un nombre suffisant d'observations indépendantes. Surtout, une "
            "fois contrôlés les rendements passés de l'indice, le score ne conserve un pouvoir de prévision significatif "
            "qu'à 20 séances (t de {n:h2_t_score_controle_20:1}) ; à 60 et 120 séances, c'est le rendement passé de "
            "l'indice lui-même qui prévoit le rendement futur (t de {n:h2_t_passe_h_60:1} et {n:h2_t_passe_h_120:1})."))
    B(("tab", "h2controle", "Prévisibilité des rendements : linéarité, recouvrement et rendements passés.",
       t_h2_controle(), "Note : régressions du rendement futur (équation {eq:prevision}) avec t de Newey-West à h retards ; "
       "corrélation de rang de Spearman ; sans recouvrement : une observation toutes les h séances.",
       [1.6, 2.5, 1.6, 1.8, 3.6, 2.0, 2.0], 8))
    B(("p", "Ce résultat a deux lectures, qui ne s'excluent pas. La première est comportementale : si l'information "
            "se diffuse lentement entre des investisseurs peu nombreux, les prix s'ajustent avec retard et les tendances "
            "persistent (Hong et Stein, 1999 ; Moskowitz, Ooi et Pedersen, 2012). La seconde est microstructurelle : sur "
            "un marché où des titres ne s'échangent pas chaque jour, les cours anciens qui se mettent à jour avec retard "
            "créent une autocorrélation positive des rendements de l'indice (Lo et MacKinlay, 1990), dont la baisse de "
            "l'illiquidité depuis 2014 devrait réduire l'ampleur. Dans les deux cas, la persistance des tendances "
            "constitue une anomalie au regard de l'efficience au sens faible, en accord avec les travaux qui la rejettent "
            "sur la BRVM (Tan Toe, Toe et Zoungrana, 2023 ; Houndalidji, Tchindro et Hounkou, 2024). Pour l'utilisateur "
            "de l'indice, la conséquence est claire : sur la BRVM, la peur n'annonce pas un rebond."))
    B(("h2", "6.3 H3 : sur un marché concentré, la participation compte"))
    B(("p", "Le rendement de l'indice et celui du titre médian sont liés (corrélation de rang de "
            "{n:h3_corr_indice_mediane_titres:2} sur 20 séances, tableau {tab:h3complement} en annexe), mais loin "
            "d'être confondus. Le momentum de l'indice "
            "n'explique que {p:h3_r2_momentum_mediane_titres_20:0} des variations du rendement du titre médian sur 20 "
            "séances ; l'ajout de la participation et de la force porte cette part à "
            "{p:h3_r2_momentum_participation_mediane_titres_20:0}, avec un t de {n:h3_t_participation_mediane_titres_20:1} "
            "pour la participation (tableau {tab:h3}). Le constat est le même pour la part des titres en hausse "
            "({p:h3_r2_momentum_part_hausse_20:0} contre {p:h3_r2_momentum_participation_part_hausse_20:0}). Les "
            "épisodes où l'indice est haut et la participation basse, comme en octobre 2026, sont rares "
            "({p:h3_part_indice_haut_participation_basse:1} des séances) mais riches d'information (figure "
            "{fig:h3}). **H3 est validée.**"))
    B(("tab", "h3", "Ce que la participation ajoute au momentum de l'indice.", t_h3(),
       "Note : régressions sur les rangs des composantes, 2009-2026 ; t de Newey-West à 20 retards.",
       [5.0, 2.7, 3.3, 2.5, 2.5], 8.5))
    B(("fig", "h3", "f10_h3_divergences.png", "Momentum de l'indice et participation des titres, 2019-2026.",
       "Note : rangs lissés sur 10 séances ; zones colorées : écart de plus de 40 points entre les deux rangs."))
    B(("p", "Calculé à partir d'un marché qui exclut les cinq premières capitalisations, l'indice reste proche de la "
            "version initiale (corrélation de {n:h3_corr_v2_hors_grands:2} depuis 2020) mais ne se trouve dans la même "
            "zone que {p:h3_meme_zone_hors_grands:0} du temps, et il suit de plus près le rendement du titre médian "
            "(corrélation de rang de {n:h3_ic_hors_grands_mediane_2020:2} depuis 2020, contre "
            "{n:h3_ic_v2_mediane_2020:2} pour la version initiale ; tableau {tab:h3complement} et figure "
            "{fig:horsgrands} en annexe). Une version « hors grandes capitalisations » apporte donc un "
            "éclairage complémentaire, utile lorsque quelques titres font l'indice."))
    B(("h2", "6.4 H4 : la saison des dividendes ne biaise pas le score"))
    B(("p", "Les détachements de mai à juillet font baisser l'indice de cours, mais l'effet sur le score est faible et "
            "non significatif : sur 2017-2026, le score est en moyenne supérieur de {n:h4_ecart_v2:1} points de mai à "
            "juillet (t de {n:h4_t_v2:1}), et le rang du momentum n'y est pas différent ({n:h4_ecart_momentum_v2:1} point, "
            "t de {n:h4_t_momentum_v2:1}) (tableau {tab:h4} et figure {fig:h4}). La baisse due aux dividendes, de l'ordre "
            "de quelques pour cent répartis sur trois mois, reste petite devant les écarts habituels de l'indice à sa "
            "moyenne de 125 séances. **H4 est rejetée.** Le calcul sur l'indice dividendes réinvestis reste néanmoins "
            "préférable par principe, puisqu'il mesure ce que perçoit l'investisseur."))
    B(("tab", "h4", "Effet de la saison des dividendes (mai à juillet), 2017-2026.", t_h4(),
       "Note : coefficient d'une indicatrice de mai à juillet, en points de score ; t de Newey-West à 60 retards.",
       [5.0, 5.0, 5.0], 9))
    B(("fig", "h4", "f11_h4_saison.png", "Momentum et score moyens selon le mois, 2017-2026.",
       "Note : zone colorée : mai à juillet, période des détachements."))
    B(("h2", "6.5 H5 : la simplicité suffit"))
    B(("p", "Quatre pondérations sont comparées : poids égaux sur les cinq composantes, poids égaux sur trois piliers, "
            "poids de la première composante principale estimés sur la calibration, et poids optimisés sur la "
            "calibration pour maximiser la validité (grille de pas 0,1). Hors échantillon, les quatre schémas obtiennent "
            "des résultats très proches (tableau {tab:h5}). Les poids optimisés, qui concentrent "
            "l'essentiel sur la volatilité baissière et le momentum, gagnent un peu de validité sur le test mais perdent "
            "de l'information sur les rendements futurs et rendent le score nettement plus nerveux. **H5 est validée** : "
            "rien ne justifie une pondération statistique, plus difficile à expliquer et à auditer."))
    B(("tab", "h5", "Comparaison des pondérations (indice dividendes réinvestis).", t_h5(), NOTE_CRITERES,
       [2.0, 3.3, 1.5, 2.1, 1.8, 2.3, 2.0], 8))
    B(("h2", "6.6 Robustesse"))
    B(("p", "Les conclusions résistent aux variations de méthode (tableau {tab:robustesse}). Retirer une composante "
            "laisse l'indice corrélé à plus de 0,96 avec la version complète. Le score robuste fondé sur la médiane et "
            "l'écart absolu médian donne un indice presque identique. La fenêtre du rang est le choix le plus sensible : "
            "une fenêtre d'un an rend l'indice nerveux et lui fait perdre presque toute information sur les rendements "
            "futurs, alors qu'une fenêtre de trois ans l'améliore ; le rang sur tout l'historique déséquilibre les zones "
            "(aucune séance de peur extrême sur le test), parce que la liquidité et la largeur du marché ont "
            "durablement changé. Enfin, la définition de la séance illiquide ne change ni la conclusion de H1 ni le "
            "choix de la version révisée (annexe D)."))
    B(("tab", "robustesse", "Variantes de l'indice sur l'échantillon de test (2023-2026).", t_robustesse(),
       NOTE_CRITERES + " Corrélation avec l'indice : corrélation de rang avec l'indice dividendes réinvestis complet.",
       [3.9, 1.5, 2.1, 1.8, 2.3, 2.0, 2.0], 8))

    # ----- 7. Version révisée -----
    B(("h1", "7. Une version révisée de l'indice"))
    B(("p", "Les résultats précédents suggèrent trois changements : calculer le momentum et la volatilité baissière sur "
            "l'indice dividendes réinvestis, regrouper les composantes en trois piliers pour que la tendance ne compte "
            "plus trois fois, et allonger la fenêtre du rang. Douze combinaisons (fenêtre de 504 ou 756 séances, poids "
            "égaux ou piliers, lissage sur 1, 5 ou 10 séances) ont été classées sur l'échantillon de validation par une "
            "note qui additionne les écarts réduits de la validité, de l'information, de l'équilibre et de la stabilité "
            "(tableau {tab:candidats} en annexe). La combinaison retenue associe une fenêtre de {i:v3_fenetre} séances, "
            "les trois piliers et un lissage sur {i:v3_lissage} séances :"))
    B(("eq", "v3", r"G^{v3}_t = \frac{1}{10}\sum_{j=0}^{9} \frac{1}{3}\left[R^{M}_{t-j} + \frac{R^{P}_{t-j} + R^{F}_{t-j}}{2} + \frac{R^{D}_{t-j} + R^{S}_{t-j}}{2}\right]"))
    B(("leg", [(r"R^{M}", "rang du momentum, calculé sur l'indice dividendes réinvestis (pilier « tendance »)"),
               (r"R^{P},\,R^{F}", "rangs de la participation et de la force (pilier « participation »)"),
               (r"R^{D},\,R^{S}", "rangs de la demande et de la volatilité baissière (pilier « flux et stress »)")]))
    B(("p", "Sur l'échantillon de test, jamais utilisé jusque-là, la version révisée change de zone "
            f"{fr(ratio_changements, 1)} fois moins souvent ({{n:v3_test_changements_par_an:0}} fois par an contre "
            "{n:v2_test_changements_par_an:0}) et elle est plus informative sur les rendements des 60 séances suivantes "
            "(corrélation de {n:v3_test_ic_futur_60:2} contre {n:v2_test_ic_futur_60:2}), avec un équilibre des zones "
            "comparable (tableau {tab:v2v3} et figure {fig:v3}). Elle cède en revanche un peu de validité "
            "contemporaine ({n:v3_test_validite:2} contre {n:v2_test_validite:2}) : c'est le coût attendu du lissage, qui "
            "retarde la réaction de quelques séances. La version révisée ne domine donc pas sur tous les critères ; elle "
            "constitue un meilleur compromis pour une publication quotidienne, à condition de montrer aussi les "
            "composantes non lissées. Le {s:date_fin}, elle se situe à {n:v3_dernier:0} (« {s:v3_dernier_zone} »), contre "
            "{n:v2_dernier:0} pour la version initiale ; leur corrélation de rang sur toute la période est de "
            "{n:corr_v2_v3:2} (tableau {tab:proprietes} en annexe)."))
    B(("tab", "v2v3", "Version initiale et version révisée.", t_v2_v3(), NOTE_CRITERES,
       [2.0, 3.3, 1.5, 2.1, 1.8, 2.3, 2.0], 8))
    B(("fig", "v3", "f12_score_v3.png", "La version révisée de l'indice, comparée à la version initiale.", None))

    # ----- 8. Recommandations -----
    B(("h1", "8. Recommandations"))
    B(("p", "La BRVM a fait de nouveaux indices et de la liquidité du marché secondaire deux axes de sa stratégie. Les "
            "résultats de cette étude suggèrent plusieurs actions concrètes, qui ne demandent que des données dont la "
            "place dispose déjà."))
    B(("h2", "8.1 Pour la BRVM"))
    B(("puces", [
        "**Publier un indicateur quotidien de sentiment**, accompagné de sa méthode, de ses composantes et de son "
        "historique, sur le modèle de la version révisée. Il donnerait aux investisseurs locaux et internationaux une "
        "lecture commune de l'humeur du marché, fondée sur les données de la place plutôt que sur des indicateurs "
        "importés.",
        "**Publier des statistiques de largeur et de liquidité** avec le bulletin de la cote : part des titres en "
        "hausse, part des titres au-dessus de leur moyenne de 50 séances, nouveaux plus hauts et plus bas, part des "
        "séances sans échange. La participation est l'information la plus précieuse sur un marché concentré, et elle "
        "est aujourd'hui invisible dans les indices publiés.",
        "**Publier un BRVM Composite dividendes réinvestis.** Avec un rendement en dividendes de l'ordre de "
        "{p:rendement_dividendes_moyen:0} par an (tableau {tab:marche}), l'indice de cours sous-estime fortement la performance réelle du "
        "marché ; une version de rendement total serait aussi la référence naturelle des fonds communs de placement.",
        "**Rendre accessibles des historiques complets et vérifiés** de cours, de volumes en valeur et de dividendes, "
        "pour que les travaux de recherche sur la place reposent sur une base commune.",
    ]))
    B(("h2", "8.2 Pour le régulateur et les sociétés de gestion et d'intermédiation"))
    B(("puces", [
        "**Suivre les phases de peur comme des phases de liquidité dégradée** : un score bas accompagné d'une hausse des "
        "séances sans échange signale un marché où les ordres de vente trouvent difficilement preneur. C'est le moment "
        "où les contrats d'animation de marché, obligatoires pour les titres des compartiments Prestige et Principal "
        "(BRVM, 2022, articles 35 et 65 ; CREPMF, s.d., articles 138 et 139), sont les plus sollicités. Leurs moyens en titres et en espèces, publiés "
        "chaque semestre, sont limités : l'indice peut aider le régulateur et les SGI animatrices à vérifier qu'ils "
        "restent suffisants dans les périodes de peur.",
        "**Surveiller les divergences entre l'indice et la participation** : un indice porté par quelques capitalisations "
        "pendant que la majorité des titres recule appelle une communication prudente auprès des épargnants.",
    ]))
    B(("h2", "8.3 Pour les investisseurs"))
    B(("puces", [
        "**Lire l'indice comme une description, pas comme un signal.** Sur la BRVM, la peur extrême n'annonce pas de "
        "rebond : elle accompagne des marchés qui continuent souvent de baisser.",
        "**Regarder les composantes**, et en particulier la participation : un score bas avec un momentum élevé décrit "
        "un marché étroit, pas une panique générale.",
    ]))

    # ----- 9. Conclusion -----
    B(("h1", "9. Limites et conclusion"))
    B(("p", "Plusieurs limites tiennent aux données. Les valeurs échangées avant 2013 paraissent incomplètes, ce qui "
            "fragilise la composante de demande en début de période. Les dividendes de la base ne commencent qu'en 2016. "
            "Les pondérations du marché ne sont vérifiées contre la capitalisation publiée que depuis 2020. La part des "
            "séances illiquides tombe à {p:illiq_etude_part_2026:0} en 2026 selon la définition retenue, contre "
            "{p:illiq_lot_part_2026:0} si l'on compte toute séance à cours inchangé (annexe D) : cette baisse reflète "
            "l'essor des échanges, mais son ampleur dépend de la définition et demanderait à être confirmée à la "
            "source. D'autres limites tiennent au marché : un historique de dix-sept ans ne contient "
            "qu'un petit nombre de cycles complets, et les tests à long horizon reposent sur peu d'observations "
            "indépendantes. Enfin, trois dimensions du sentiment restent hors de portée faute de données publiques : la "
            "demande relative face aux obligations, les flux des fonds et des investisseurs non résidents, et la tonalité "
            "de la presse financière, dont la collecte quotidienne rassemble déjà les articles et qu'une étude "
            "ultérieure pourrait exploiter."))
    B(("p", "Sous ces réserves, l'étude établit qu'un indice de sentiment construit avec les seules données de marché "
            "décrit fidèlement l'état de la BRVM. Sur ce marché, la peur prend la forme d'un assèchement des échanges et "
            "d'un rétrécissement de la hausse plutôt que d'une flambée de la volatilité ; le sentiment accompagne la "
            "poursuite des tendances plutôt que leur retournement ; et la participation des titres est l'information la "
            "plus précieuse lorsqu'un petit nombre de capitalisations fait l'indice. Ces résultats plaident pour que la "
            "place publie elle-même un tel indicateur, avec les statistiques de largeur et de liquidité qui le "
            "fondent : à l'heure où la BRVM entre dans sa quatrième décennie, mesurer l'humeur de son marché avec ses "
            "propres données contribuerait à la transparence et à la confiance dont dépend sa liquidité."))

    # ----- Références -----
    B(("h1", "Références"))
    for r in REFERENCES:
        B(("ref", r))

    # ----- Annexes -----
    B(("saut",))
    B(("h1", "Annexes"))
    B(("h2", "Annexe A. Données"))
    B(("tab", "donnees", "Données utilisées.", t_donnees(), None, [3.4, 2.4, 1.6, 2.8, 5.8], 8.5))
    B(("tab", "dividendes", "Contrôle des dividendes.", t_controle_dividendes(),
       "Note : part du cours : dividende net rapporté à la clôture de la veille du détachement ; baisse : écart entre "
       "cette clôture et la première clôture des {i:div_delai_jours} jours suivants. Confirmé à la source : date ou "
       "montant vérifiés dans l'avis publié par la BRVM. Les seuils de {p:div_seuil:0} et de {p:div_confirmation:0} "
       "du montant sont arbitraires.",
       [5.0, 1.6, 1.7, 7.7], 8.5))
    B(("tab", "collecte", "Journal de la dernière collecte prise en compte ({s:collecte_controle}).", t_collecte(),
       "Note : délai : intervalle minimal entre deux requêtes vers le même domaine, celui du robots.txt s'il est plus "
       "long ; adresses refusées : adresses interdites par le robots.txt, donc non demandées.",
       [4.0, 2.4, 3.4, 2.4, 3.4], 8.5))
    B(("h2", "Annexe B. Paramètres"))
    B(("tab", "parametres", "Paramètres de l'indice.", t_parametres(), None, [4.0, 5.4, 6.6], 8.5))
    B(("h2", "Annexe C. Choix de la version révisée"))
    B(("tab", "candidats", "Combinaisons évaluées sur l'échantillon de validation (2019-2022).", t_candidats(),
       "Note : note de synthèse : somme des écarts réduits de la validité, de la valeur absolue de la corrélation avec le "
       "rendement futur, de l'équilibre des zones et de la stabilité (nombre de changements, signe inversé).",
       [1.6, 2.2, 1.7, 1.6, 2.1, 2.4, 2.0, 2.0], 8))
    B(("h2", "Annexe D. Robustesse à la définition de la séance illiquide"))
    B(("p", "La séance illiquide sert à valider l'indice (H1) et entre dans le critère de validité qui classe les "
            "versions révisées ; elle n'intervient pas dans le calcul du score. Le seuil de trois clôtures égales étant "
            "arbitraire, tous les résultats qui en dépendent ont été recalculés avec quatre autres définitions : un seuil "
            "plus strict et un seuil plus large, l'absence d'échange seule, et la part des rendements nuls de Lesmond, "
            "Ogden et Trzcinka (1999), qui compte toute séance où le cours n'a pas varié (tableau {tab:illiquidite}). Le "
            "lien entre le score et l'illiquidité subsiste avec chacune : la corrélation de rang intra-annuelle est "
            "comprise entre −{n:illiq_rho_max:2} et −{n:illiq_rho_min:2}, et le t de Newey-West entre "
            "−{n:illiq_t_max:1} et −{n:illiq_t_min:1}. La mesure des rendements nuls donne le lien le plus net "
            "et l'absence d'échange seule le plus faible : la règle du cours figé apporte donc une information propre. "
            + ("La version révisée retenue est la même avec les cinq définitions. " if valeur("illiq_v3_identique")
               else "La version révisée retenue change selon la définition. ") +
            "Seul le niveau de la part des séances illiquides dépend fortement de la définition : depuis 2022, il va de "
            "{p:illiq_volume_part_2022_fin:0} (absence d'échange seule) à {p:illiq_lot_part_2022_fin:0} (rendements "
            "nuls)."))
    B(("tab", "illiquidite", "Résultats selon la définition de la séance illiquide.", t_robustesse_illiquidite(),
       "Note : parts : moyenne sur les titres cotés des séances illiquides ; H1 : corrélation de rang entre le score "
       "de la version initiale et la part des séances illiquides sur 20 séances, toutes deux en écart à leur moyenne "
       "de l'année, avec le t de Newey-West (20 retards) entre parenthèses ; validité : critère du tableau {tab:h5} ; "
       "corrélation avec l'étude : corrélation de rang de la mesure intra-annuelle avec celle de la définition retenue.",
       [4.0, 1.4, 1.4, 1.4, 2.1, 1.7, 1.6, 1.8], 8))
    B(("h2", "Annexe E. Asymétrie de la volatilité"))
    t_gamma = [valeur(f"asym_{e}_gjr_t_gamma") for e in ECHANTILLONS_ASYMETRIE]
    gamma_negatif = all(valeur(f"asym_{e}_gjr_gamma") < 0 for e in ECHANTILLONS_ASYMETRIE)
    B(("p", "La section 4.2 conclut que la volatilité de la BRVM ne réagit pas davantage aux baisses qu'aux hausses. "
            "Trois mesures l'établissent (tableau {tab:asymetrie}) : les semi-volatilités des séances de hausse et de "
            "baisse ; une régression du rendement absolu sur les hausses et sur les baisses des cinq séances "
            "précédentes, dont les deux coefficients seraient différents en présence d'un effet de levier ; et un "
            "modèle GJR-GARCH(1,1) à moyenne constante (Glosten, Jagannathan et Runkle, 1993) :"))
    B(("eq", "gjr", r"r_t = \mu + \varepsilon_t, \qquad \sigma^2_t = \omega + \left(\alpha + \gamma\,\mathbb{1}\left\{\varepsilon_{t-1} < 0\right\}\right)\varepsilon^2_{t-1} + \beta\,\sigma^2_{t-1}"))
    B(("leg", [(r"r_t", "rendement logarithmique quotidien de l'indice, en %"),
               (r"\sigma^2_t", "variance conditionnelle de la séance t"),
               (r"\gamma", "supplément de réaction de la variance après une baisse : un effet de levier le rend "
                           "positif et significatif")]))
    B(("p", "Le modèle est estimé par quasi-maximum de vraisemblance gaussienne, avec les écarts-types robustes de "
            "Bollerslev et Wooldridge (1992), valides si les rendements ne suivent pas une loi normale. Les résultats "
            "sont reproduits sur deux sous-périodes et sur l'indice dividendes réinvestis. Le coefficient "
            + ("d'asymétrie γ est négatif dans les quatre échantillons" if gamma_negatif else
               "d'asymétrie γ change de signe selon l'échantillon")
            + f" et n'y est jamais significatif (t compris entre {fr(min(t_gamma), 1)} et {fr(max(t_gamma), 1)}) ; "
            + "les deux coefficients de la régression ne diffèrent dans aucun échantillon. La persistance de la "
            "volatilité (α + γ/2 + β) est modérée, de {n:asym_cours_2008_2015_gjr_persistance:2} avant 2016 à "
            "{n:asym_cours_2016_2026_gjr_persistance:2} depuis."))
    B(("tab", "asymetrie", "Asymétrie de la volatilité du BRVM Composite.", t_asymetrie(),
       "Note : semi-volatilités annualisées des rendements quotidiens ; réaction : coefficient du rendement absolu "
       "(en %) sur la somme des hausses ou des baisses (en valeur absolue) des cinq séances précédentes, t de "
       "Newey-West (10 retards) entre parenthèses ; égalité : p du test d'égalité des deux coefficients ; GJR-GARCH : "
       "équation {eq:gjr}, t robustes de Bollerslev et Wooldridge entre parenthèses.",
       [5.2, 2.7, 2.7, 2.7, 2.7], 8.5))
    B(("h2", "Annexe F. Statistiques complémentaires"))
    B(("p", "Cette annexe documente les calculs cités dans le texte qui ne figurent dans aucun autre tableau, dans "
            "l'ordre des sections qui les utilisent. Les rendements du BRVM Composite (section 3.1) ont des queues "
            "épaisses et une volatilité qui se regroupe dans le temps (tableau {tab:descriptives} et figure "
            "{fig:autocorr}). Leur autocorrélation est quasi nulle d'une séance à l'autre, mais positive et "
            "significative à quelques retards ({ns:desc_acf_3:2} à trois séances et {ns:desc_acf_5:2} à cinq, pour un "
            "seuil de {n:desc_acf_borne:3}), ce que confirme le test de Ljung-Box : c'est l'inertie qu'étudie la "
            "section 6.2, et que les échanges non synchrones d'un marché peu liquide suffisent en partie à créer (Lo et "
            "MacKinlay, 1990). Le tableau {tab:concentration} détaille la concentration du marché à la dernière "
            "séance."))
    B(("tab", "descriptives", "Rendements quotidiens du BRVM Composite, 2008-2026.", t_descriptives(),
       "Note : rendements logarithmiques quotidiens ; moyenne et volatilité annualisées sur 252 séances ; kurtosis en "
       "excès de celui de la loi normale ; Ljung-Box : p du test de nullité des 10 premières autocorrélations. La "
       "baisse de 2016 à 2020 va du plus haut du {s:desc_haut_2015_2016_date} au plus bas du {s:desc_bas_2020_date}.",
       [7.6, 3.8, 3.8], 8.5))
    B(("fig", "autocorr", "f14_autocorrelations.png", "Autocorrélations des rendements quotidiens du BRVM Composite.",
       "Note : bande bleue : intervalle à 95 % sous l'hypothèse d'absence d'autocorrélation."))
    B(("tab", "concentration", "Concentration de la capitalisation le {s:conc_date}.", t_concentration(), None,
       [10.0, 3.0], 8.5))
    B(("p", "Le tableau {tab:reconstitution} et la figure {fig:reconstitution} justifient l'usage restreint du "
            "marché reconstitué (section 3.4) : avant 2019, les pondérations disponibles ne reproduisent pas le BRVM "
            "Composite, alors que depuis 2019 l'écart de rendement entre les deux séries est minime."))
    B(("tab", "reconstitution", "Fidélité des séries reconstituées.", t_reconstitution(),
       "Note : écart annualisé : écart-type de la différence des rendements quotidiens, multiplié par la racine de 252.",
       [6.4, 1.9, 2.1, 2.3, 1.8], 8.5))
    B(("fig", "reconstitution", "f15_reconstitution.png",
       "Corrélation des rendements quotidiens sur 250 séances glissantes.", None))
    B(("p", "Le tableau {tab:proprietes} et la figure {fig:autocorrscore} décrivent la persistance du score "
            "(sections 5.1 et 7), les tableaux {tab:acp} et {tab:acpvecteur} l'analyse en composantes principales "
            "(section 5.2), le tableau {tab:cas} la dernière séance de l'étude de cas (section 5.3), et le tableau "
            "{tab:h3complement} avec la figure {fig:horsgrands} les mesures complémentaires de H3 (section 6.3)."))
    B(("tab", "proprietes", "Propriétés du score, versions initiale et révisée.", t_proprietes(),
       "Note : séances depuis le début de chaque version ; corrélations de rang de Spearman.", [9.0, 3.0, 3.0], 8.5))
    B(("fig", "autocorrscore", "f16_autocorrelations_score.png", "Autocorrélation du score selon le retard.", None))
    B(("tab", "acp", "Analyse en composantes principales des rangs des cinq composantes (2009-2026).", t_acp(), None,
       [4.0, 3.0, 3.5, 3.0], 8.5))
    B(("tab", "acpvecteur", "Poids des composantes dans la première composante principale.", t_acp_vecteur(),
       "Note : vecteur propre normé, signe choisi pour que la somme des poids soit positive.", [5.0, 6.0], 8.5))
    B(("tab", "cas", "Étude de cas : la dernière séance de l'étude ({s:date_fin}).", t_cas(),
       "Note : rang : position de la mesure parmi ses valeurs des 504 dernières séances, de 0 (la plus « peureuse ») "
       "à 100 ; deux ans : 504 dernières séances ; titres : rendements dividendes réinvestis.",
       [9.6, 2.6, 2.6], 8.5))
    B(("tab", "h3complement", "Concentration et score : mesures complémentaires de H3.", t_h3_complement(),
       "Note : sans les cinq premières capitalisations : score calculé sur un marché pondéré qui exclut "
       "{s:h3_grands} ; depuis 2020 seulement pour les comparaisons de zones, faute de pondérations fiables avant "
       "2019 et d'une année de rangs.",
       [10.6, 2.2, 2.0], 8.5))
    B(("fig", "horsgrands", "f17_hors_grands.png",
       "Version initiale et version sans les cinq premières capitalisations, 2020-2026.",
       "Note : moyennes sur 20 séances ; bandes de couleur : zones de lecture."))
    B(("h2", "Annexe G. Reproduire l'étude"))
    B(("p", "L'étude est entièrement reproductible. Les données sont lues dans le dépôt GitHub *{s:depot_brvm}*, "
            "au commit {s:commit_brvm} : cours, volumes, indices, dividendes, pondérations et journal de conformité de "
            "la collecte. Le fichier *recherche/sources.json* désigne ce commit et les seuls fichiers utiles, que le module *recherche/commun/depot.py* extrait "
            "avant tout calcul ; un dépôt privé demande un jeton d'accès en lecture."))
    B(("p", "Le code de l'étude est indépendant de celui de la collecte : les règles de traitement (divisions du "
            "nominal, contrôle des dividendes, séances illiquides) et le calcul de l'indice sont réécrits dans "
            "*recherche/commun/marche.py* et *recherche/fear_greed/indice.py*. Le script *recherche/fear_greed/etude.py* "
            "produit tous les tableaux, les figures et le fichier *chiffres.json* d'où proviennent tous les nombres "
            "cités dans le texte ; le script *article.py* construit ce document à partir de ces résultats. Les calculs "
            "reposent sur Python, pandas, NumPy, SciPy et statsmodels."))

    # ----- Rendu -----
    a.numeroter([(b[0], b[1]) if b[0] in ("fig", "tab", "eq") else (b[0], None) for b in blocs])
    import os
    sauter = set(filter(None, os.environ.get("ARTICLE_SANS", "").split(",")))
    for b in blocs:
        genre = b[0]
        if genre in sauter:
            continue
        if genre == "titre_page":
            page_titre(a)
        elif genre == "h1":
            a.titre(b[1], 1)
        elif genre == "h1n":
            p = a.para(f"**{b[1]}**", align=WD_ALIGN_PARAGRAPH.LEFT, taille=13, avant=6, apres=6, couleur=BLEU)
        elif genre == "h2":
            a.titre(b[1], 2)
        elif genre == "p":
            a.para(b[1])
        elif genre == "puces":
            a.puces(b[1])
        elif genre == "eq":
            a.equation(b[1], b[2])
        elif genre == "leg":
            a.legende_symboles(b[1])
        elif genre == "fig":
            a.figure(b[1], b[2], b[3], b[4] if len(b) > 4 else None, b[5] if len(b) > 5 else 15.5)
        elif genre == "tab":
            a.tableau(b[1], b[2], b[3], b[4] if len(b) > 4 else None, b[5] if len(b) > 5 else None,
                      b[6] if len(b) > 6 else 9)
        elif genre == "ref":
            p = a.para(b[1], align=WD_ALIGN_PARAGRAPH.LEFT, apres=4, taille=10)
            p.paragraph_format.left_indent = Cm(0.8)
            p.paragraph_format.first_line_indent = Cm(-0.8)
        elif genre == "saut":
            a.saut()
        elif genre == "toc":
            a.table_des_matieres()
    chemin = Path(os.environ["ARTICLE_SORTIE"]) if os.environ.get("ARTICLE_SORTIE") else ICI / f"{NOM}.docx"
    a.sauver(chemin)
    return chemin


def page_titre(a: Article) -> None:
    for _ in range(4):
        a.doc.add_paragraph()
    a.para("Prix de la Recherche du 30^e^ anniversaire de la BRVM", align=WD_ALIGN_PARAGRAPH.CENTER, taille=11,
           couleur=BLEU)
    a.para("Rapport de recherche", align=WD_ALIGN_PARAGRAPH.CENTER, taille=11, apres=30)
    a.para("**Peur et cupidité sur un marché frontière peu liquide**", align=WD_ALIGN_PARAGRAPH.CENTER, taille=20,
           apres=8)
    a.para("Construction et validation d'un indice de sentiment pour la Bourse Régionale des Valeurs Mobilières",
           align=WD_ALIGN_PARAGRAPH.CENTER, taille=14, apres=40)
    a.para("[Prénom NOM]", align=WD_ALIGN_PARAGRAPH.CENTER, taille=12, apres=2)
    a.para("[Fonction, institution, ville, pays]", align=WD_ALIGN_PARAGRAPH.CENTER, taille=11, apres=2)
    a.para("[adresse électronique]", align=WD_ALIGN_PARAGRAPH.CENTER, taille=11, apres=60)
    a.para("Octobre 2026", align=WD_ALIGN_PARAGRAPH.CENTER, taille=11)
    a.para("Données arrêtées au {s:date_fin}", align=WD_ALIGN_PARAGRAPH.CENTER, taille=10)
    a.saut()


REFERENCES = [
    "Amihud, Y. (2002). Illiquidity and stock returns: cross-section and time-series effects. *Journal of Financial "
    "Markets*, 5(1), 31-56.",
    "Ang, A., Chen, J. et Xing, Y. (2006). Downside risk. *Review of Financial Studies*, 19(4), 1191-1239.",
    "Baker, M. et Stein, J. C. (2004). Market liquidity as a sentiment indicator. *Journal of Financial Markets*, "
    "7(3), 271-299.",
    "Baker, M. et Wurgler, J. (2006). Investor sentiment and the cross-section of stock returns. *Journal of "
    "Finance*, 61(4), 1645-1680.",
    "Baker, M. et Wurgler, J. (2007). Investor sentiment in the stock market. *Journal of Economic Perspectives*, "
    "21(2), 129-151.",
    "Bekaert, G., Harvey, C. R. et Lundblad, C. (2007). Liquidity and expected returns: lessons from emerging "
    "markets. *Review of Financial Studies*, 20(6), 1783-1831.",
    "Ben Mrad Douagi, F. W., Chaouachi, O. et Mory, S. (2019). Seasonal anomalies: empirical evidence from Regional "
    "Stock Exchange Ivory Coast Securities. *Asian Journal of Empirical Research*, 9(2), 38-45.",
    "Black, F. (1976). Studies of stock price volatility changes. *Proceedings of the 1976 Meetings of the American "
    "Statistical Association, Business and Economic Statistics Section*, 177-181.",
    "Bollerslev, T. et Wooldridge, J. M. (1992). Quasi-maximum likelihood estimation and inference in dynamic models "
    "with time-varying covariances. *Econometric Reviews*, 11(2), 143-172.",
    "Brock, W., Lakonishok, J. et LeBaron, B. (1992). Simple technical trading rules and the stochastic properties of "
    "stock returns. *Journal of Finance*, 47(5), 1731-1764.",
    "Brown, G. W. et Cliff, M. T. (2004). Investor sentiment and the near-term stock market. *Journal of Empirical "
    "Finance*, 11(1), 1-27.",
    "BRVM, Bourse Régionale des Valeurs Mobilières (2022). *Règlement général*, publié le 1er juillet 2022 après "
    "approbation du CREPMF, articles 35 et 65. https://www.brvm.org/sites/default/files/rg_brvm_-_apres_approbation_"
    "crepmf_sept_2021_01_07_2022_bis.pdf (consulté en octobre 2026).",
    "Chang, E. C., Cheng, J. W. et Khorana, A. (2000). An examination of herd behavior in equity markets: an "
    "international perspective. *Journal of Banking & Finance*, 24(10), 1651-1679.",
    "Christie, A. A. (1982). The stochastic behavior of common stock variances: value, leverage and interest rate "
    "effects. *Journal of Financial Economics*, 10(4), 407-432.",
    "Christie, W. G. et Huang, R. D. (1995). Following the pied piper: do individual returns herd around the market? "
    "*Financial Analysts Journal*, 51(4), 31-37.",
    "CNN Business (s.d.). Fear & Greed Index. https://www.cnn.com/markets/fear-and-greed (consulté en octobre 2026).",
    "CREPMF, Conseil Régional de l'Épargne Publique et des Marchés Financiers, aujourd'hui AMF-UMOA (s.d.). "
    "*Règlement général relatif à "
    "l'organisation, au fonctionnement et au contrôle du marché financier régional de l'UMOA*, articles 138 et 139. "
    "https://www.amf-umoa.org/assets/docs/general/Reglement_General.pdf (consulté en octobre 2026).",
    "Da, Z., Engelberg, J. et Gao, P. (2015). The sum of all FEARS: investor sentiment and asset prices. *Review of "
    "Financial Studies*, 28(1), 1-32.",
    "De Long, J. B., Shleifer, A., Summers, L. H. et Waldmann, R. J. (1990). Noise trader risk in financial markets. "
    "*Journal of Political Economy*, 98(4), 703-738.",
    "Djahoué, M. G., Kacou Bi, K. A. et Aba, N. E. A. (2026). Investor sentiment and stock market volatility: evidence "
    "from the West African Regional Stock Exchange. *Applied Economics and Finance*, 13(1). "
    "https://doi.org/10.11114/aef.v13i1.8816",
    "Estrada, J. (2002). Systematic risk in emerging markets: the D-CAPM. *Emerging Markets Review*, 3(4), 365-379.",
    "George, T. J. et Hwang, C.-Y. (2004). The 52-week high and momentum investing. *Journal of Finance*, 59(5), "
    "2145-2176.",
    "Glosten, L. R., Jagannathan, R. et Runkle, D. E. (1993). On the relation between the expected value and the "
    "volatility of the nominal excess return on stocks. *Journal of Finance*, 48(5), 1779-1801.",
    "Greenwood, R. et Shleifer, A. (2014). Expectations of returns and expected returns. *Review of Financial "
    "Studies*, 27(3), 714-746.",
    "Hong, H. et Stein, J. C. (1999). A unified theory of underreaction, momentum trading, and overreaction in asset "
    "markets. *Journal of Finance*, 54(6), 2143-2184.",
    "Houndalidji, Y. H. E., Tchindro, G. R. et Hounkou, C. E. (2024). The efficiency of BRVM tested by the facts: "
    "analysis of past share prices. *Journal of Financial Risk Management*, 13(4), 769-797.",
    "Huang, D., Jiang, F., Tu, J. et Zhou, G. (2015). Investor sentiment aligned: a powerful predictor of stock "
    "returns. *Review of Financial Studies*, 28(3), 791-837.",
    "Jegadeesh, N. et Titman, S. (1993). Returns to buying winners and selling losers: implications for stock market "
    "efficiency. *Journal of Finance*, 48(1), 65-91.",
    "Koster, M., Illyes, G., Zeller, H. et Sassman, L. (2022). *Robots Exclusion Protocol*. RFC 9309, Internet "
    "Engineering Task Force.",
    "Kumar, A. et Lee, C. M. C. (2006). Retail investor sentiment and return comovements. *Journal of Finance*, "
    "61(5), 2451-2486.",
    "Lesmond, D. A. (2005). Liquidity of emerging markets. *Journal of Financial Economics*, 77(2), 411-452.",
    "Lesmond, D. A., Ogden, J. P. et Trzcinka, C. A. (1999). A new estimate of transaction costs. *Review of "
    "Financial Studies*, 12(5), 1113-1141.",
    "Lo, A. W. et MacKinlay, A. C. (1990). An econometric analysis of nonsynchronous trading. *Journal of "
    "Econometrics*, 45(1-2), 181-211.",
    "Moskowitz, T. J., Ooi, Y. H. et Pedersen, L. H. (2012). Time series momentum. *Journal of Financial Economics*, "
    "104(2), 228-250.",
    "Naidoo, D., Moores-Pitt, P. et Muzindutsi, P.-F. (2025). The South African Fear and Greed Index and its "
    "connectedness to the U.S. index. *Journal of Risk and Financial Management*, 18(7), 349.",
    "N'dri, K. L. (2007). An empirical study of the relation between stock return volatility and trading volume in "
    "the BRVM. *African Journal of Business Management*, 1(5), 107-112.",
    "Newey, W. K. et West, K. D. (1987). A simple, positive semi-definite, heteroskedasticity and autocorrelation "
    "consistent covariance matrix. *Econometrica*, 55(3), 703-708.",
    "Shleifer, A. et Vishny, R. W. (1997). The limits of arbitrage. *Journal of Finance*, 52(1), 35-55.",
    "Stambaugh, R. F., Yu, J. et Yuan, Y. (2012). The short of it: investor sentiment and anomalies. *Journal of "
    "Financial Economics*, 104(2), 288-302.",
    "Tan Toe, D. L., Toe, M. et Zoungrana, T. D. (2023). Investigating the weak and semi-strong forms of "
    "informational efficiency on the West African Economic and Monetary Union's stock exchange (BRVM) through returns "
    "predictability tests. *SN Business & Economics*, 3(9). https://doi.org/10.1007/s43546-023-00550-0",
]


if __name__ == "__main__":
    print(construire())
