"""Étude empirique de l'indice Fear & Greed BRVM : calculs, tableaux, figures et chiffres de l'article.

    python recherche/fear_greed/etude.py

Écrit dans recherche/fear_greed/sortie/ : tableaux (CSV), figures (PNG 300 dpi) et chiffres.json, d'où
viennent tous les nombres cités dans l'article. Les données sont tirées de GitHub au commit figé de
recherche/sources.json (voir commun/depot.py) ; aucun code de l'application de collecte n'est utilisé.

Échantillons chronologiques : calibration (jusqu'en 2018), validation (2019-2022), test (2023 à la fin).
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
import warnings
from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
import donnees as D  # noqa: E402
import indice as FG  # noqa: E402
from commun import depot  # noqa: E402
from commun import marche as MM  # noqa: E402

warnings.simplefilter("ignore")
SORTIE = Path(__file__).resolve().parent / "sortie"
CACHE = SORTIE / "cache"
SORTIE.mkdir(exist_ok=True)
CACHE.mkdir(exist_ok=True)

ECHANTILLONS = {"calibration": ("2010-01-01", "2018-12-31"), "validation": ("2019-01-01", "2022-12-31"),
                "test": ("2023-01-01", "2100-01-01")}
HORIZONS = (20, 60, 120)
COMPOSANTES = list(FG.NOMS)
PILIERS = {"tendance": ["momentum"], "participation": ["participation", "force"],
           "flux_stress": ["demande", "vol_baissiere"]}
ZONES = [z[1] for z in FG.ECHELLE]
CHIFFRES: dict = {}


def note(cle: str, valeur) -> None:
    """Range un chiffre cité dans l'article (arrondi raisonnable)."""
    if isinstance(valeur, (np.floating, float)):
        valeur = None if not np.isfinite(valeur) else float(valeur)
    elif isinstance(valeur, (np.integer,)):
        valeur = int(valeur)
    CHIFFRES[cle] = valeur


def tableau(nom: str, df: pd.DataFrame) -> pd.DataFrame:
    df.to_csv(SORTIE / f"{nom}.csv", sep=";", decimal=",", encoding="utf-8-sig")
    return df


def periode(s, nom: str):
    a, b = ECHANTILLONS[nom]
    return s.loc[a:b]


def zone(score: pd.Series) -> pd.Series:
    return score.map(lambda x: FG.libelle(x) if np.isfinite(x) else np.nan)


# ---------------------------------------------------------------------------
# 1. Indices : version initiale et variantes
# ---------------------------------------------------------------------------

def brutes(indice: pd.Series | None = None, indice_vol: pd.Series | None = None) -> pd.DataFrame:
    """Mesures brutes des cinq composantes ; ``indice`` remplace le BRVM Composite pour le momentum,
    ``indice_vol`` pour la volatilité baissière."""
    cours, valeurs, ix = D.base_indice()
    b = FG.valeurs_brutes(cours, valeurs, ix)
    if indice is not None:
        i = indice.reindex(ix.index)
        b["momentum"] = i / i.rolling(FG.MM_MOMENTUM).mean() - 1
    if indice_vol is not None:
        i = indice_vol.reindex(ix.index)
        neg = i.pct_change().clip(upper=0)
        b["vol_baissiere"] = -(np.sqrt((neg ** 2).rolling(FG.VOL_COURT).mean())
                               / np.sqrt((neg ** 2).rolling(FG.VOL_LONG).mean()).replace(0, np.nan))
    return b


def rangs(b: pd.DataFrame, fenetre: int | str = FG.FENETRE_DEFAUT, methode: str = "rang") -> pd.DataFrame:
    """Normalisation 0-100 de chaque mesure : rang percentile glissant (version initiale), rang
    sur tout l'historique disponible (« croissant »), ou score robuste médiane / écart absolu médian
    converti par la loi normale (``methode="robuste"``)."""
    empreinte = hashlib.md5(pd.util.hash_pandas_object(b, index=True).to_numpy().tobytes()
                            + "|".join(b.columns).encode()).hexdigest()[:16]
    cle = CACHE / f"rangs_{empreinte}_{fenetre}_{methode}.pkl"
    if cle.exists():
        return pd.read_pickle(cle)
    out = {}
    for k in b:
        s = b[k]
        if methode == "robuste":
            w = FG.FENETRE_DEFAUT if fenetre == "croissant" else int(fenetre)
            med = s.rolling(w, min_periods=FG.MIN_OBS_RANG).median()
            mad = (s - med).abs().rolling(w, min_periods=FG.MIN_OBS_RANG).median() * 1.4826
            out[k] = pd.Series(stats.norm.cdf((s - med) / mad.replace(0, np.nan)) * 100, index=s.index)
        elif fenetre == "croissant":
            out[k] = s.expanding(min_periods=FG.MIN_OBS_RANG).apply(lambda x: (x <= x[-1]).mean() * 100, raw=True)
        else:
            out[k] = FG.rang_glissant(s, int(fenetre))
    r = pd.DataFrame(out)
    r.to_pickle(cle)
    return r


def agreger(r: pd.DataFrame, schema: str = "egal", poids: dict | None = None) -> pd.Series:
    """Score composite : poids égaux sur les composantes (version initiale), poids égaux sur trois
    piliers, ou poids donnés."""
    if poids is not None:
        return FG.score(r, poids)
    if schema == "piliers":
        p = pd.DataFrame({k: r[v].mean(axis=1) for k, v in PILIERS.items()})
        return FG.score(p)
    return FG.score(r[[c for c in COMPOSANTES if c in r]])


def lisser(s: pd.Series, n: int) -> pd.Series:
    return s if n <= 1 else s.rolling(n, min_periods=1).mean().where(s.notna())


# ---------------------------------------------------------------------------
# 2. Mesures de validation
# ---------------------------------------------------------------------------

def mesures_marche() -> pd.DataFrame:
    """Mesures de l'état du marché à chaque séance (sur les 20 séances passées) et rendements à venir."""
    m = D.marches()
    cours, valeurs, ix = D.base_indice()
    rt = m["brvmc_rt"]
    lr = np.log(rt).diff()
    out = pd.DataFrame(index=ix.index)
    out["vol_20"] = lr.rolling(20).std() * np.sqrt(252)
    out["perte_depuis_haut"] = rt / rt.rolling(252, min_periods=120).max() - 1
    se = D.sans_echange()
    out["sans_echange_20"] = se.rolling(20, min_periods=10).mean().mean(axis=1)
    r = cours.ffill().pct_change(fill_method=None).abs()
    v = valeurs.reindex(columns=cours.columns)
    amihud = (r / (v / 1e6)).where((v > 0) & cours.notna())          # |r| par million de FCFA échangé
    out["amihud_20"] = np.log(amihud.rolling(20, min_periods=5).mean().median(axis=1))
    tr = D.cours_dividendes_reinvestis()
    r20 = tr / tr.shift(20) - 1
    out["mediane_titres_20"] = r20.median(axis=1)
    out["part_hausse_20"] = (r20 > 0).sum(axis=1) / r20.notna().sum(axis=1)
    out["indice_20"] = rt / rt.shift(20) - 1
    for h in HORIZONS:
        out[f"futur_{h}"] = np.log(rt.shift(-h) / rt)
        out[f"vol_futur_{h}"] = lr[::-1].rolling(h).std()[::-1].shift(-1) * np.sqrt(252)
    return out


def hac(y: pd.Series, X: pd.DataFrame, lags: int):
    d = pd.concat([y, X], axis=1).dropna()
    return sm.OLS(d.iloc[:, 0], sm.add_constant(d.iloc[:, 1:])).fit(cov_type="HAC", cov_kwds={"maxlags": lags})


def _gjr_vraisemblances(p: np.ndarray, r: np.ndarray) -> np.ndarray:
    """Log-vraisemblance gaussienne de chaque séance, GJR-GARCH(1,1) à moyenne constante :
    s2_t = omega + (alpha + gamma 1{e_{t-1} < 0}) e_{t-1}^2 + beta s2_{t-1}."""
    mu, omega, alpha, gamma, beta = p
    e = r - mu
    s2 = np.empty_like(r)
    s2[0] = r.var()
    for t in range(1, len(r)):
        s2[t] = omega + (alpha + gamma * (e[t - 1] < 0)) * e[t - 1] ** 2 + beta * s2[t - 1]
    s2 = np.maximum(s2, 1e-12)
    return -0.5 * (np.log(2 * np.pi) + np.log(s2) + e ** 2 / s2)


def gjr_garch(r: pd.Series) -> tuple[dict, dict]:
    """Estimation par quasi-maximum de vraisemblance (Glosten, Jagannathan et Runkle, 1993), écarts-types
    robustes de Bollerslev-Wooldridge. Rendements en %. Renvoie (paramètres, t)."""
    from scipy.optimize import minimize
    from statsmodels.tools.numdiff import approx_fprime, approx_hess
    x = np.asarray(r, float)
    res = minimize(lambda p: -_gjr_vraisemblances(p, x).sum(), [x.mean(), x.var() * 0.05, 0.08, 0.02, 0.88],
                   bounds=[(None, None), (1e-8, None), (0, 1), (-0.5, 1), (0, 0.9999)], method="L-BFGS-B")
    g = approx_fprime(res.x, lambda p: _gjr_vraisemblances(p, x))
    h_inv = np.linalg.inv(approx_hess(res.x, lambda p: _gjr_vraisemblances(p, x).sum()))
    se = np.sqrt(np.diag(h_inv @ (g.T @ g) @ h_inv))
    noms = ["mu", "omega", "alpha", "gamma", "beta"]
    return dict(zip(noms, res.x)), dict(zip(noms, res.x / se))


def asymetrie_volatilite(rq: pd.Series) -> dict:
    """La volatilité est-elle plus forte dans les baisses (effet de levier) ? Semi-volatilités des séances
    de hausse et de baisse, régression du rendement absolu sur les hausses et les baisses des 5 séances
    passées, et coefficient d'asymétrie d'un GJR-GARCH. ``rq`` : rendements logarithmiques quotidiens."""
    r = rq.dropna() * 100
    hausse, baisse = r.clip(lower=0), -r.clip(upper=0)
    X = pd.DataFrame({"hausses": hausse.shift(1).rolling(5).sum(), "baisses": baisse.shift(1).rolling(5).sum()})
    reg = hac(r.abs().rename("y"), X, 10)
    ecart = reg.t_test("baisses - hausses = 0")
    p, t = gjr_garch(r)
    out = {"n": len(r), "semi_vol_hausse": np.sqrt((hausse ** 2).mean() * 252) / 100,
           "semi_vol_baisse": np.sqrt((baisse ** 2).mean() * 252) / 100,
           "reg_hausses": reg.params["hausses"], "reg_t_hausses": reg.tvalues["hausses"],
           "reg_baisses": reg.params["baisses"], "reg_t_baisses": reg.tvalues["baisses"],
           "reg_p_egalite": float(np.asarray(ecart.pvalue)),
           "gjr_persistance": p["alpha"] + p["gamma"] / 2 + p["beta"]}
    for k in p:
        out[f"gjr_{k}"], out[f"gjr_t_{k}"] = p[k], t[k]
    return out


# Échantillons du test d'asymétrie : (série de marches(), début, fin)
ECHANTILLONS_ASYMETRIE = {"cours": ("brvmc", "2008", "2026"), "cours_2008_2015": ("brvmc", "2008", "2015"),
                          "cours_2016_2026": ("brvmc", "2016", "2026"), "rt": ("brvmc_rt", "2008", "2026")}


def spearman(a: pd.Series, b: pd.Series) -> float:
    d = pd.concat([a, b], axis=1).dropna()
    return float(stats.spearmanr(d.iloc[:, 0], d.iloc[:, 1])[0]) if len(d) > 30 else np.nan


def intra_annuel(s: pd.Series) -> pd.Series:
    """Écart à la moyenne de l'année : retire les tendances lentes (la liquidité progresse d'année en année)."""
    return s - s.groupby(s.index.year).transform("mean")


def criteres(score: pd.Series, mm: pd.DataFrame, nom: str = "") -> dict:
    """Critères de comparaison des versions de l'indice, sur la période de ``score`` :
    validité (H1), information (H2), stabilité, équilibre des zones."""
    s = score.dropna()
    x = mm.reindex(s.index)
    valid = np.nanmean([-spearman(s, x["vol_20"]), spearman(s, x["perte_depuis_haut"]),
                        -spearman(intra_annuel(s), intra_annuel(x["sans_echange_20"]))])
    z = zone(s)
    ext_peur, ext_avid = s[s <= 25].index, s[s > 75].index
    f = x["futur_60"]
    ecart = f.reindex(ext_peur).mean() - f.reindex(ext_avid).mean()
    rep = z.value_counts(normalize=True).reindex(ZONES).fillna(0)
    entropie = float(-(rep[rep > 0] * np.log(rep[rep > 0])).sum() / np.log(len(ZONES)))
    changements = float((z != z.shift()).iloc[1:].sum() / (len(s) / 252))
    return {"version": nom, "validite": valid, "ic_futur_60": spearman(s, f), "ecart_extremes_60": ecart,
            "changements_par_an": changements, "ecart_type_variation": float(s.diff().std()),
            "equilibre_zones": entropie, "part_peur_extreme": float(rep.iloc[0]),
            "part_avidite_extreme": float(rep.iloc[-1]), "n": len(s)}


def classer_candidats(b_rt: pd.DataFrame, mm: pd.DataFrame) -> pd.DataFrame:
    """Douze combinaisons de la version révisée, classées sur l'échantillon de validation par une note de
    synthèse : validité, information (|IC|), stabilité (moins de changements), équilibre."""
    candidats = []
    for fen, schema, lis in product((504, 756), ("egal", "piliers"), (1, 5, 10)):
        s = lisser(agreger(rangs(b_rt, fen), schema), lis)
        c = criteres(periode(s, "validation"), periode(mm, "validation"), f"{fen}/{schema}/{lis}")
        c.update({"fenetre": fen, "schema": schema, "lissage": lis})
        candidats.append(c)
    cand = pd.DataFrame(candidats)
    z = lambda col, sens=1: sens * (cand[col] - cand[col].mean()) / cand[col].std(ddof=0)  # noqa: E731
    cand["note"] = z("validite") + z("equilibre_zones") + z("changements_par_an", -1) + cand["ic_futur_60"].abs().pipe(
        lambda s_: (s_ - s_.mean()) / s_.std(ddof=0))
    return cand.sort_values("note", ascending=False)


# Définitions de la séance illiquide comparées (règle de D.sans_echange_selon, clé des chiffres)
DEFINITIONS_ILLIQUIDE = {"fige:2": "fige2", "fige:3": "etude", "fige:5": "fige5", "volume": "volume", "lot": "lot"}


def robustesse_illiquidite(s2: pd.Series, b_rt: pd.DataFrame, mm: pd.DataFrame) -> pd.DataFrame:
    """Tout ce qui dépend de la définition de la séance illiquide, recalculé pour chaque définition :
    parts des séances illiquides, H1 (corrélation intra-annuelle et t de Newey-West), écart par zone,
    validité de la version initiale et version révisée retenue."""
    z2 = zone(s2.dropna())
    a = intra_annuel(s2)
    series, lignes = {}, []
    for regle, cle in DEFINITIONS_ILLIQUIDE.items():
        se = D.sans_echange_selon(regle)
        part = se.mean(axis=1)
        m_ = mm.copy()
        m_["sans_echange_20"] = se.rolling(20, min_periods=10).mean().mean(axis=1)
        x = series[cle] = intra_annuel(m_["sans_echange_20"])
        res = hac(x.rename("y"), a.rename("score").to_frame(), 20)
        par_zone = x.reindex(z2.index).groupby(z2).mean()
        v3 = classer_candidats(b_rt, m_).iloc[0]
        lignes.append({"definition": cle, "part_2008_2012": part.loc["2008":"2012"].mean(),
                       "part_2022_fin": part.loc["2022":].mean(), "part_2026": part.loc["2026":].mean(),
                       "h1_spearman": spearman(a, x), "h1_t_hac": res.tvalues["score"],
                       "ecart_peur_extreme": par_zone.get(ZONES[0], np.nan),
                       "ecart_avidite_extreme": par_zone.get(ZONES[-1], np.nan),
                       "validite_v2_validation": criteres(periode(s2, "validation"), periode(m_, "validation"))["validite"],
                       "validite_v2_test": criteres(periode(s2, "test"), periode(m_, "test"))["validite"],
                       "v3_retenue": f"{int(v3['fenetre'])}/{v3['schema']}/{int(v3['lissage'])}"})
    t = pd.DataFrame(lignes).set_index("definition")
    t["corr_avec_etude"] = [spearman(series[k], series["etude"]) for k in t.index]
    return t


def descriptives(rq: pd.Series) -> dict:
    """Statistiques des rendements logarithmiques quotidiens ``rq`` (annexe : statistiques complémentaires)."""
    from statsmodels.stats.diagnostic import acorr_ljungbox
    r = rq.dropna()
    lb = acorr_ljungbox(r, lags=[10])
    lb_abs = acorr_ljungbox(r.abs(), lags=[10])
    return {"n": len(r), "moyenne_annuelle": r.mean() * 252, "volatilite_annuelle": r.std() * np.sqrt(252),
            "asymetrie": stats.skew(r), "kurtosis": stats.kurtosis(r), "min": r.min(), "max": r.max(),
            "autocorr_1": r.autocorr(1), "autocorr_abs_1": r.abs().autocorr(1),
            "ljung_box_p": float(lb["lb_pvalue"].iloc[0]), "ljung_box_abs_p": float(lb_abs["lb_pvalue"].iloc[0])}


def proprietes_score(s: pd.Series, mm: pd.DataFrame) -> dict:
    """Persistance du score, stabilité de sa lecture et lien avec les rendements passés et futurs."""
    s = s.dropna()
    z = zone(s)
    duree = z.groupby((z != z.shift()).cumsum()).size()
    out = {f"autocorr_{l}": s.autocorr(l) for l in (1, 5, 20, 60)}
    out.update({"duree_moyenne_zone": duree.mean(), "duree_mediane_zone": duree.median(),
                "changements_par_an": float((z != z.shift()).iloc[1:].sum() / (len(s) / 252)),
                "corr_passe_20": spearman(s, mm["indice_20"]), "corr_futur_20": spearman(s, mm["futur_20"]),
                "corr_futur_60": spearman(s, mm["futur_60"])})
    return out


def complements(m: pd.DataFrame, w: pd.DataFrame, hhi: pd.Series, b2: pd.DataFrame, r2: pd.DataFrame,
                s2: pd.Series, s3: pd.Series, s_ex: pd.Series, mm: pd.DataFrame, fig) -> None:
    """Annexe « statistiques complémentaires » : tableaux et figures de chaque calcul cité dans le texte sans
    autre tableau (rendements de l'indice, concentration, reconstitution, propriétés du score, étude de cas,
    concentration et score)."""
    # rendements du BRVM Composite (section 3.1)
    rq = {k: np.log(m[k]).diff().dropna() for k in ("brvmc", "brvmc_rt")}
    d = pd.DataFrame({k: descriptives(v) for k, v in rq.items()})
    haut = m["brvmc"].loc["2015":"2016"]
    bas = m["brvmc"].loc["2020"]
    note("desc_haut_2015_2016_date", f"{haut.idxmax():%d/%m/%Y}")
    note("desc_bas_2020_date", f"{bas.idxmin():%d/%m/%Y}")
    tableau("t15_descriptives", d)
    for k, col in d.items():
        for j, v in col.items():
            note(f"desc_{k}_{j}", v)
    acf = pd.DataFrame({"rendement": [rq["brvmc"].autocorr(l) for l in range(1, 61)],
                        "rendement_absolu": [rq["brvmc"].abs().autocorr(l) for l in range(1, 61)]}, index=range(1, 61))
    tableau("t15b_autocorrelations", acf)
    for l in (3, 5):
        note(f"desc_acf_{l}", acf.loc[l, "rendement"])
    note("desc_acf_borne", 1.96 / np.sqrt(len(rq["brvmc"])))
    fig.autocorrelations(acf, len(rq["brvmc"]))

    # concentration à la dernière séance (section 3.1)
    der = w.iloc[-1].sort_values(ascending=False)
    conc = pd.Series({**{c.split("_")[0]: der[c] for c in der.index[:5]}, "cinq_premieres": der.iloc[:5].sum(),
                      "hhi": hhi.iloc[-1], "titres_effectifs": 1 / hhi.iloc[-1],
                      "titres_effectifs_2010": 1 / hhi.loc["2010"].mean(), "titres_cotes": int((der > 0).sum())},
                     name="valeur")
    tableau("t16_concentration", conc.to_frame())
    note("conc_date", f"{w.index[-1]:%d/%m/%Y}")
    note("conc_titres_cotes", int((der > 0).sum()))

    # reconstitution du marché et indice dividendes réinvestis (section 3.4)
    rq_ = m[["brvmc", "marche_cours", "brvmc_rt", "sikatr"]].pct_change(fill_method=None)
    lignes = []
    for nom, a, b, debut, fin_ in (("marche_avant_2019", "marche_cours", "brvmc", None, "2018"),
                                   ("marche_depuis_2019", "marche_cours", "brvmc", "2019", None),
                                   ("rt_sikatr", "brvmc_rt", "sikatr", None, None)):
        x = rq_[[a, b]].loc[debut:fin_].dropna()
        lignes.append({"comparaison": nom, "debut": f"{x.index.min():%Y}", "fin": f"{x.index.max():%Y}",
                       "correlation": x.corr().iloc[0, 1], "ecart_annuel": (x[a] - x[b]).std() * np.sqrt(252),
                       "n": len(x)})
    rec = tableau("t17_reconstitution", pd.DataFrame(lignes).set_index("comparaison"))
    for k, l in rec.iterrows():
        note(f"rec_{k}_ecart_annuel", l["ecart_annuel"])
    glissant = pd.DataFrame({"marche": rq_["marche_cours"].rolling(250, min_periods=200).corr(rq_["brvmc"]),
                             "rt_sikatr": rq_["brvmc_rt"].rolling(250, min_periods=200).corr(rq_["sikatr"])})
    fig.reconstitution(glissant)

    # propriétés du score, versions initiale et révisée (sections 5.1 et 7)
    p = pd.DataFrame({"v2": proprietes_score(s2, mm), "v3": proprietes_score(s3, mm)})
    p.loc["corr_autre_version"] = spearman(s2, s3)
    tableau("t18_proprietes_score", p)
    for v, col in p.items():
        for j, x in col.items():
            note(f"prop_{v}_{j}", x)
    acf_s = pd.DataFrame({v: [s.dropna().autocorr(l) for l in range(1, 121)] for v, s in (("v2", s2), ("v3", s3))},
                         index=range(1, 121))
    fig.autocorrelations_score(acf_s)

    # étude de cas : dernière séance (section 5.3)
    fin = s2.dropna().index[-1]
    tr = D.cours_dividendes_reinvestis()
    r20 = (tr.iloc[-1] / tr.iloc[-21] - 1).dropna()
    part2 = b2["participation"].iloc[-504:]
    note("cas_participation_min_2ans_date", f"{part2.idxmin():%d/%m/%Y}")
    cas = pd.DataFrame([
        ("score", np.nan, s2.loc[fin]), ("momentum", b2["momentum"].loc[fin], r2.loc[fin, "momentum"]),
        ("participation", b2["participation"].loc[fin], r2.loc[fin, "participation"]),
        ("force", b2["force"].loc[fin], r2.loc[fin, "force"]), ("demande", b2["demande"].loc[fin], r2.loc[fin, "demande"]),
        ("vol_baissiere", -b2["vol_baissiere"].loc[fin], r2.loc[fin, "vol_baissiere"]),
        ("participation_min_2ans", part2.min(), np.nan), ("participation_mediane_2ans", part2.median(), np.nan),
        ("indice_20", m["brvmc"].iloc[-1] / m["brvmc"].iloc[-21] - 1, np.nan),
        ("indice_1an", m["brvmc"].iloc[-1] / m["brvmc"].iloc[-253] - 1, np.nan),
        ("indice_depuis_haut", m["brvmc"].iloc[-1] / m["brvmc"].iloc[-252:].max() - 1, np.nan),
        ("part_titres_hausse_20", (r20 > 0).mean(), np.nan), ("mediane_titres_20", r20.median(), np.nan),
    ], columns=["mesure", "valeur", "rang"]).set_index("mesure")
    tableau("t19_cas", cas)

    # concentration et score : version hors grandes capitalisations (section 6.3)
    fig.hors_grands(s2.loc["2020":].dropna(), s_ex.loc["2020":])

    # les tableaux de l'annexe reprennent exactement les chiffres cités dans le texte
    controles = [(d.loc["kurtosis", "brvmc"], "brvmc_kurtosis"), (d.loc["autocorr_1", "brvmc"], "brvmc_autocorr_1"),
                 (d.loc["autocorr_abs_1", "brvmc"], "brvmc_autocorr_abs_1"), (conc["cinq_premieres"], "poids_5_grands_fin"),
                 (conc["titres_effectifs"], "titres_effectifs_fin"), (conc["titres_effectifs_2010"], "titres_effectifs_2010"),
                 (rec.loc["marche_avant_2019", "correlation"], "fidelite_reconstitution_avant_2019"),
                 (rec.loc["marche_depuis_2019", "correlation"], "fidelite_reconstitution_depuis_2019"),
                 (rec.loc["rt_sikatr", "correlation"], "correlation_rt_sikatr"),
                 (p.loc["autocorr_1", "v2"], "v2_autocorr_1"), (p.loc["autocorr_20", "v2"], "v2_autocorr_20"),
                 (p.loc["duree_moyenne_zone", "v2"], "v2_duree_moyenne_zone"),
                 (p.loc["corr_passe_20", "v2"], "corr_v2_indice_passe_20"),
                 (p.loc["corr_futur_20", "v2"], "corr_v2_futur_20"), (p.loc["corr_autre_version", "v2"], "corr_v2_v3"),
                 (cas.loc["momentum", "valeur"], "cas_brvmc_vs_mm125"),
                 (cas.loc["participation", "valeur"], "cas_participation_brute"),
                 (cas.loc["participation_mediane_2ans", "valeur"], "cas_participation_mediane_2ans"),
                 (cas.loc["vol_baissiere", "valeur"], "cas_vol_baissiere_ratio"),
                 (cas.loc["indice_20", "valeur"], "cas_indice_20"), (cas.loc["indice_1an", "valeur"], "cas_indice_1an"),
                 (cas.loc["indice_depuis_haut", "valeur"], "cas_indice_depuis_haut"),
                 (cas.loc["part_titres_hausse_20", "valeur"], "cas_part_titres_hausse_20"),
                 (cas.loc["mediane_titres_20", "valeur"], "cas_mediane_titres_20"),
                 (cas.loc["score", "rang"], "v2_dernier"), (cas.loc["momentum", "rang"], "v2_dernier_momentum")]
    ecarts = [cle for x, cle in controles if not np.isclose(x, CHIFFRES[cle])]
    assert not ecarts, f"annexe : chiffres différents du texte : {ecarts}"


# ---------------------------------------------------------------------------
# 3. Étude
# ---------------------------------------------------------------------------

def main() -> None:
    t0 = time.time()
    import figures as FIG

    cours, valeurs, ix = D.base_indice()
    m = D.marches()
    fin = ix.index.max()
    note("date_fin", f"{fin:%d/%m/%Y}")
    note("date_debut", f"{ix.index.min():%d/%m/%Y}")
    note("n_seances", len(ix))
    note("n_titres", int(cours.notna().any().sum()))
    note("n_titres_fin", int(cours.loc[fin].notna().sum()))

    # --- Données : commits lus et journal de conformité de la collecte ---
    src = depot.sources()
    note("commit_brvm", src["brvm"]["commit"][:7])
    note("depot_brvm", src["brvm"]["depot"])
    conf = json.loads((D.DATA / "sources_conformite.json").read_text(encoding="utf-8"))
    for cle, domaine in (("sika", "www.sikafinance.com"), ("brvm", "www.brvm.org")):
        c = conf[domaine]
        note(f"collecte_{cle}_requetes", c["requetes_derniere_execution"])
        note(f"collecte_{cle}_delai", c["delai_applique"])
        note(f"collecte_{cle}_refusees", len(c["urls_refusees"]))
        note(f"collecte_{cle}_robots_lu", bool(c["robots_lu"]))
    note("collecte_controle", f"{pd.Timestamp(conf['www.sikafinance.com']['controle_le']):%d/%m/%Y}")

    # --- Données ---
    w = D.poids()
    note("poids_sonatel_2008", w["SNTS_sn"].loc["2008"].mean())
    note("poids_sonatel_fin", w["SNTS_sn"].iloc[-1])
    top5 = w.apply(lambda r: r.sort_values(ascending=False).iloc[:5].sum(), axis=1)
    note("poids_5_grands_fin", top5.iloc[-1])
    hhi = (w ** 2).sum(axis=1)
    note("titres_effectifs_fin", 1 / hhi.iloc[-1])
    note("titres_effectifs_2010", 1 / hhi.loc["2010"].mean())
    se = D.sans_echange()
    part_se = se.mean(axis=1)
    rd = D.rendement_dividendes_marche()
    debut_div = D.dividendes()["Date_Detachement"].min().year
    rd_annuel = rd.groupby(rd.index.year).sum()
    annuel = pd.DataFrame({
        "brvmc": m["brvmc"].resample("YE").last().pct_change(),
        "brvmc_rt": m["brvmc_rt"].resample("YE").last().pct_change(),
        "volatilite": np.log(m["brvmc_rt"]).diff().groupby(m.index.year).std().set_axis(
            m["brvmc"].resample("YE").last().index) * np.sqrt(252),
        "seances_illiquides": part_se.resample("YE").mean(),
        "poids_sonatel": w["SNTS_sn"].resample("YE").mean().reindex(m["brvmc"].resample("YE").last().index),
        "titres_effectifs": (1 / hhi).resample("YE").mean().reindex(m["brvmc"].resample("YE").last().index),
        "valeur_echangee_mds": valeurs.sum(axis=1).resample("YE").sum() / 1e9,
        "titres_cotes": cours.notna().resample("YE").max().sum(axis=1),
    })
    annuel.index = annuel.index.year
    annuel["rendement_dividendes"] = rd_annuel.reindex(annuel.index).where(annuel.index >= debut_div)
    tableau("t1_marche_par_annee", annuel)
    note("illiquide_2008_2012", part_se.loc["2008":"2012"].mean())
    note("illiquide_2022_fin", part_se.loc["2022":].mean())
    mois = rd.groupby(rd.index.month).sum() / rd.sum()
    note("dividendes_mai", mois.get(5, 0.0))
    note("dividendes_mai_juillet", mois.reindex([5, 6, 7]).sum())
    note("rendement_dividendes_moyen", rd.loc["2019":"2025"].groupby(rd.loc["2019":"2025"].index.year).sum().mean())
    x = m[["brvmc_rt", "sikatr"]].pct_change().dropna()
    note("correlation_rt_sikatr", x.corr().iloc[0, 1])
    note("debut_dividendes", f"{D.dividendes()['Date_Detachement'].min():%Y}")
    # contrôle des dividendes : part du cours de la veille, baisse au détachement, statut
    ctrl = D.M.controle_dividendes()
    tableau("t13_controle_dividendes", ctrl[["Ticker", "Exercice", "Date_Detachement", "Montant_Net_FCFA",
                                             "part_du_cours", "baisse_du_jour", "statut", "retenu"]].reset_index(drop=True))
    for st in MM.CONTROLES:
        note(f"div_n_{st}", int((ctrl["statut"] == st).sum()))
    note("div_candidats", len(ctrl))
    note("div_retenus", int(ctrl["retenu"].sum()))
    note("div_ecartes", int((~ctrl["retenu"]).sum()))
    note("div_seuil", MM.DIVIDENDE_MAX)
    note("div_confirmation", MM.CONFIRMATION)
    note("div_delai_jours", MM.DELAI_BAISSE.days)
    note("div_part_mediane", ctrl.loc[ctrl["statut"] == "courant", "part_du_cours"].median())
    rq = np.log(m["brvmc"]).diff().dropna()
    note("brvmc_asymetrie", stats.skew(rq))
    note("brvmc_kurtosis", stats.kurtosis(rq))
    note("brvmc_autocorr_1", rq.autocorr(1))
    note("brvmc_autocorr_abs_1", rq.abs().autocorr(1))
    asym = {}
    for ech, (serie, debut, fin_) in ECHANTILLONS_ASYMETRIE.items():
        asym[ech] = asymetrie_volatilite(np.log(m[serie]).diff().loc[debut:fin_])
        for k, v in asym[ech].items():
            note(f"asym_{ech}_{k}", v)
    tableau("t14_asymetrie_volatilite", pd.DataFrame(asym))
    for k, v in asym["cours"].items():
        note(f"brvmc_{k}", v)
    FIG.marche(m, w["SNTS_sn"], part_se)
    FIG.dividendes(mois)

    # --- Version initiale (v2) ---
    b2 = brutes()
    r2 = rangs(b2)
    direct = FG.score(FG.calculer(cours, valeurs, ix))
    s2 = agreger(r2)
    assert np.allclose(s2.dropna(), direct.dropna()) and s2.dropna().index.equals(direct.dropna().index), \
        "le score de l'étude diffère du calcul direct de l'indice"
    note("v2_debut", f"{s2.first_valid_index():%d/%m/%Y}")
    note("v2_dernier", s2.dropna().iloc[-1])
    note("v2_dernier_zone", FG.libelle(s2.dropna().iloc[-1]))
    for k in COMPOSANTES:
        note(f"v2_dernier_{k}", r2[k].dropna().iloc[-1])
    z2 = zone(s2.dropna())
    rep = z2.value_counts(normalize=True).reindex(ZONES)
    for i, zz in enumerate(ZONES):
        note(f"v2_part_zone_{i}", rep[zz])
    corr = r2.dropna().corr()
    tableau("t3_correlations_composantes", corr)
    for a_, b_ in [("momentum", "participation"), ("momentum", "force"), ("participation", "force"),
                   ("demande", "vol_baissiere"), ("momentum", "vol_baissiere")]:
        note(f"corr_{a_}_{b_}", corr.loc[a_, b_])
    vp = np.linalg.eigvalsh(corr.to_numpy())[::-1]
    note("acp_part_1", vp[0] / vp.sum())
    note("acp_part_2", vp[1] / vp.sum())
    vec = np.linalg.eigh(corr.to_numpy())[1][:, ::-1][:, 0]
    vec = vec * np.sign(vec.sum())
    tableau("t4_acp", pd.DataFrame({"valeur_propre": vp, "part": vp / vp.sum()}, index=[f"CP{i+1}" for i in range(5)]))
    tableau("t4b_acp_vecteur", pd.Series(vec, index=corr.index, name="CP1").to_frame())
    # persistance
    duree = z2.groupby((z2 != z2.shift()).cumsum()).size()
    note("v2_duree_moyenne_zone", duree.mean())
    note("v2_autocorr_1", s2.dropna().autocorr(1))
    note("v2_autocorr_20", s2.dropna().autocorr(20))
    FIG.score_historique(s2, m["brvmc"], "f4_score_v2", "Indice Fear & Greed BRVM (version initiale)")
    FIG.correlations(corr, vp)

    mm = mesures_marche()
    note("corr_v2_indice_passe_20", spearman(s2, mm["indice_20"]))
    note("corr_v2_futur_20", spearman(s2, mm["futur_20"]))

    # Étude de cas : octobre 2026
    cas = pd.concat([r2, s2.rename("score"), m["brvmc"]], axis=1).loc[fin - pd.DateOffset(months=9):]
    tableau("t_cas_octobre", cas.tail(30).round(1))
    FIG.cas(cas)
    note("cas_brvmc_vs_mm125", b2["momentum"].iloc[-1])
    note("cas_participation_brute", b2["participation"].iloc[-1])
    note("cas_participation_min_2ans", b2["participation"].iloc[-504:].min())
    note("cas_participation_mediane_2ans", b2["participation"].iloc[-504:].median())
    note("cas_force_brute", b2["force"].iloc[-1])
    note("cas_vol_baissiere_ratio", -b2["vol_baissiere"].iloc[-1])
    note("cas_indice_depuis_haut", (m["brvmc"].iloc[-1] / m["brvmc"].iloc[-252:].max()) - 1)
    note("cas_indice_1an", m["brvmc"].iloc[-1] / m["brvmc"].iloc[-253] - 1)
    note("cas_baisse_2016_2020", 1 - m["brvmc"].loc["2020"].min() / m["brvmc"].loc["2015":"2016"].max())
    tr = D.cours_dividendes_reinvestis()
    r20 = (tr.iloc[-1] / tr.iloc[-21] - 1).dropna()
    note("cas_part_titres_hausse_20", (r20 > 0).mean())
    note("cas_mediane_titres_20", r20.median())
    note("cas_indice_20", m["brvmc"].iloc[-1] / m["brvmc"].iloc[-21] - 1)

    # --- H1 : validité ---
    lignes = []
    variantes_h1 = {"v2": s2, "v2 sans volatilité baissière": agreger(r2.drop(columns="vol_baissiere")),
                    "v2 sans momentum": agreger(r2.drop(columns="momentum"))}
    for nom, s in variantes_h1.items():
        for mes, signe in [("vol_20", -1), ("perte_depuis_haut", 1), ("sans_echange_20", -1), ("amihud_20", -1)]:
            a = s if mes not in ("sans_echange_20", "amihud_20") else intra_annuel(s)
            bb = mm[mes] if mes not in ("sans_echange_20", "amihud_20") else intra_annuel(mm[mes])
            rho = spearman(a, bb)
            res = hac(bb.rename("y"), a.rename("score").to_frame(), 20)
            lignes.append({"version": nom, "mesure": mes, "spearman": rho, "pente_pour_10_points": res.params["score"] * 10,
                           "t_hac": res.tvalues["score"], "n": int(res.nobs)})
    h1 = tableau("t5_h1_validite", pd.DataFrame(lignes))
    for _, l in h1.iterrows():
        note(f"h1_{l['version'].replace(' ', '_')}_{l['mesure']}_rho", l["spearman"])
        note(f"h1_{l['version'].replace(' ', '_')}_{l['mesure']}_t", l["t_hac"])
    par_zone = pd.concat([z2.rename("zone"), mm[["vol_20", "perte_depuis_haut", "sans_echange_20", "amihud_20"]]],
                         axis=1).dropna(subset=["zone"])
    par_zone["sans_echange_20"] = intra_annuel(mm["sans_echange_20"]).reindex(par_zone.index)
    par_zone["amihud_20"] = intra_annuel(mm["amihud_20"]).reindex(par_zone.index)
    t_h1z = tableau("t5b_h1_par_zone", par_zone.groupby("zone").mean().reindex(ZONES))
    note("h1_vol_peur_extreme", t_h1z.loc[ZONES[0], "vol_20"])
    note("h1_vol_avidite_extreme", t_h1z.loc[ZONES[-1], "vol_20"])
    note("h1_perte_peur_extreme", t_h1z.loc[ZONES[0], "perte_depuis_haut"])
    note("h1_perte_avidite_extreme", t_h1z.loc[ZONES[-1], "perte_depuis_haut"])
    FIG.h1(par_zone)

    # --- H2 : information des extrêmes ---
    lignes = []
    for h in HORIZONS:
        f = mm[f"futur_{h}"]
        dz = pd.get_dummies(z2, dtype=float).reindex(columns=ZONES)
        res = hac(f.rename("y"), dz.drop(columns="Neutre"), h)
        for zz in ZONES:
            idx = z2.index[z2 == zz]
            moy = f.reindex(idx).mean()
            ecart = res.params.get(zz, 0.0)
            t = res.tvalues.get(zz, np.nan)
            lignes.append({"horizon": h, "zone": zz, "rendement_moyen": moy, "ecart_a_neutre": ecart if zz != "Neutre" else 0.0,
                           "t_hac": t, "vol_future": mm[f"vol_futur_{h}"].reindex(idx).mean(), "n": len(idx)})
        lin = hac(f.rename("y"), s2.rename("score").to_frame(), h)
        quad = hac(f.rename("y"), pd.DataFrame({"score": s2, "score2": (s2 - 50) ** 2}), h)
        note(f"h2_pente_lin_{h}", lin.params["score"] * 10)
        note(f"h2_t_lin_{h}", lin.tvalues["score"])
        note(f"h2_t_quad_{h}", quad.tvalues["score2"])
        note(f"h2_r2_lin_{h}", lin.rsquared)
        note(f"h2_r2_zones_{h}", res.rsquared)
        note(f"h2_ic_{h}", spearman(s2, f))
        # observations sans recouvrement
        nr = pd.concat([s2, f], axis=1).dropna().iloc[::h]
        rho_nr, p_nr = stats.spearmanr(nr.iloc[:, 0], nr.iloc[:, 1])
        note(f"h2_ic_sans_recouvrement_{h}", rho_nr)
        note(f"h2_p_sans_recouvrement_{h}", p_nr)
        note(f"h2_n_sans_recouvrement_{h}", len(nr))
        # le score apporte-t-il plus que les rendements passés de l'indice ?
        passe = pd.DataFrame({"score": s2, "passe_20": np.log(m["brvmc_rt"] / m["brvmc_rt"].shift(20)),
                              "passe_h": np.log(m["brvmc_rt"] / m["brvmc_rt"].shift(h))})
        ctrl = hac(f.rename("y"), passe, h)
        seul = hac(f.rename("y"), passe[["passe_20", "passe_h"]], h)
        note(f"h2_t_score_controle_{h}", ctrl.tvalues["score"])
        note(f"h2_pente_score_controle_{h}", ctrl.params["score"] * 10)
        note(f"h2_r2_passe_{h}", seul.rsquared)
        note(f"h2_r2_passe_score_{h}", ctrl.rsquared)
        note(f"h2_t_passe_h_{h}", seul.tvalues["passe_h"])
    h2 = tableau("t6_h2_zones", pd.DataFrame(lignes))
    for _, l in h2.iterrows():
        k = f"h2_{int(l['horizon'])}_{ZONES.index(l['zone'])}"
        note(k + "_moy", l["rendement_moyen"])
        note(k + "_ecart", l["ecart_a_neutre"])
        note(k + "_t", l["t_hac"])
        note(k + "_vol", l["vol_future"])
    # par sous-échantillon
    lignes = []
    for nom in ECHANTILLONS:
        for h in HORIZONS:
            lignes.append({"echantillon": nom, "horizon": h, "ic": spearman(periode(s2, nom), mm[f"futur_{h}"]),
                           "ic_vol": spearman(periode(s2, nom), mm[f"vol_futur_{h}"])})
    tableau("t6b_h2_sous_echantillons", pd.DataFrame(lignes))
    FIG.h2(h2)

    # --- H3 : concentration ---
    x = pd.concat([r2, mm[["mediane_titres_20", "part_hausse_20", "indice_20"]]], axis=1).dropna()
    for cible in ("mediane_titres_20", "part_hausse_20"):
        r_m = sm.OLS(x[cible], sm.add_constant(x[["momentum"]])).fit()
        r_mp = sm.OLS(x[cible], sm.add_constant(x[["momentum", "participation", "force"]])).fit()
        note(f"h3_r2_momentum_{cible}", r_m.rsquared)
        note(f"h3_r2_momentum_participation_{cible}", r_mp.rsquared)
        res = hac(x[cible].rename("y"), x[["momentum", "participation", "force"]], 20)
        note(f"h3_t_participation_{cible}", res.tvalues["participation"])
        note(f"h3_t_force_{cible}", res.tvalues["force"])
    note("h3_corr_indice_mediane_titres", spearman(mm["indice_20"], mm["mediane_titres_20"]))
    div = (r2["momentum"] - r2["participation"]).abs()
    note("h3_part_divergence_50", (div > 50).mean())
    divergents = (r2["momentum"] >= 70) & (r2["participation"] <= 30)
    note("h3_part_indice_haut_participation_basse", divergents.mean())
    # fidélité du marché reconstitué : rendements quotidiens comparés à ceux du BRVM Composite publié
    rq_ = m[["brvmc", "marche_cours"]].pct_change()
    note("fidelite_reconstitution_avant_2019", rq_.loc[:"2018"].corr().iloc[0, 1])
    note("fidelite_reconstitution_depuis_2019", rq_.loc["2019":].corr().iloc[0, 1])
    b_ex = brutes(m["rt_sans_5_grands"], m["rt_sans_5_grands"])
    s_ex = agreger(rangs(b_ex))
    s2r, s_exr = s2.loc["2020":].dropna(), s_ex.loc["2020":]          # pondérations fiables depuis 2019, rangs sur un an
    note("h3_corr_v2_hors_grands", spearman(s2r, s_exr))
    note("h3_meme_zone_hors_grands", (zone(s2r) == zone(s_exr.reindex(s2r.index))).mean())
    note("h3_ic_v2_mediane_2020", spearman(s2r, mm["mediane_titres_20"]))
    note("h3_ic_hors_grands_mediane_2020", spearman(s_exr, mm["mediane_titres_20"]))
    note("h3_grands", ", ".join(c.split("_")[0] for c in m.attrs["grands"]))
    note("h3_ic_v2_mediane", spearman(s2, mm["mediane_titres_20"]))
    note("h3_ic_hors_grands_mediane", spearman(s_ex, mm["mediane_titres_20"]))
    FIG.h3(r2, mm)

    # --- H4 : saison des dividendes ---
    b_rt = brutes(m["brvmc_rt"], m["brvmc_rt"])
    r_rt = rangs(b_rt)
    s_rt = agreger(r_rt)
    lignes = []
    for nom, s, mo in [("v2 (indice de cours)", s2, r2["momentum"]), ("dividendes réinvestis", s_rt, r_rt["momentum"])]:
        sd = s.loc["2017":]
        saison = pd.Series(sd.index.month.isin([5, 6, 7]).astype(float), index=sd.index)
        res = hac(sd.rename("y"), saison.rename("mai_juillet").to_frame(), 60)
        res_m = hac(mo.loc["2017":].rename("y"), saison.rename("mai_juillet").to_frame(), 60)
        lignes.append({"version": nom, "ecart_mai_juillet": res.params["mai_juillet"], "t_hac": res.tvalues["mai_juillet"],
                       "ecart_momentum": res_m.params["mai_juillet"], "t_momentum": res_m.tvalues["mai_juillet"]})
    h4 = tableau("t7_h4_saison", pd.DataFrame(lignes))
    note("h4_ecart_v2", h4.iloc[0]["ecart_mai_juillet"])
    note("h4_t_v2", h4.iloc[0]["t_hac"])
    note("h4_ecart_rt", h4.iloc[1]["ecart_mai_juillet"])
    note("h4_t_rt", h4.iloc[1]["t_hac"])
    note("h4_ecart_momentum_v2", h4.iloc[0]["ecart_momentum"])
    note("h4_t_momentum_v2", h4.iloc[0]["t_momentum"])
    note("h4_ecart_momentum_rt", h4.iloc[1]["ecart_momentum"])
    note("h4_t_momentum_rt", h4.iloc[1]["t_momentum"])
    mois_scores = pd.DataFrame({"v2": s2.loc["2017":].groupby(s2.loc["2017":].index.month).mean(),
                                "rt": s_rt.loc["2017":].groupby(s_rt.loc["2017":].index.month).mean(),
                                "momentum_v2": r2["momentum"].loc["2017":].groupby(r2.loc["2017":].index.month).mean(),
                                "momentum_rt": r_rt["momentum"].loc["2017":].groupby(r_rt.loc["2017":].index.month).mean()})
    tableau("t7b_h4_par_mois", mois_scores)
    FIG.h4(mois_scores)

    # --- H5 et version révisée : pondérations et paramètres ---
    calib = periode(r_rt, "calibration").dropna()
    c_cal = calib.corr()
    vp_c, vec_c = np.linalg.eigh(c_cal.to_numpy())
    v1 = np.abs(vec_c[:, -1])
    poids_acp = dict(zip(c_cal.columns, v1 / v1.sum()))
    # poids optimisés sur la calibration : validité maximale (grille de pas 0,1)
    meilleurs, best = None, -np.inf
    mm_cal = periode(mm, "calibration")
    grille = [p for p in product(np.arange(0, 1.01, 0.1), repeat=5) if abs(sum(p) - 1) < 1e-9]
    for p in grille:
        s = FG.score(calib, dict(zip(COMPOSANTES, p)))
        v = criteres(s, mm_cal)["validite"]
        if v > best:
            best, meilleurs = v, dict(zip(COMPOSANTES, p))
    note("h5_poids_optimises", {k: round(v, 1) for k, v in meilleurs.items()})
    note("h5_poids_acp", {k: round(v, 3) for k, v in poids_acp.items()})
    schemas = {"poids égaux (5)": agreger(r_rt), "trois piliers": agreger(r_rt, "piliers"),
               "ACP (calibration)": agreger(r_rt, poids=poids_acp), "optimisés (calibration)": agreger(r_rt, poids=meilleurs)}
    lignes = []
    for nom_e in ("validation", "test"):
        for nom, s in schemas.items():
            c = criteres(periode(s, nom_e), periode(mm, nom_e), nom)
            c["echantillon"] = nom_e
            lignes.append(c)
    h5 = tableau("t8_h5_ponderations", pd.DataFrame(lignes))
    FIG.h5(h5)

    # Robustesse : retrait d'une composante, normalisation, fenêtre
    lignes = []
    for k in COMPOSANTES:
        s = agreger(r_rt.drop(columns=k))
        c = criteres(periode(s, "test"), periode(mm, "test"), f"sans {FG.NOMS[k].lower()}")
        c["corr_avec_complet"] = spearman(s, s_rt)
        lignes.append(c)
    for fen in (252, 756, "croissant"):
        s = agreger(rangs(b_rt, fen))
        c = criteres(periode(s, "test"), periode(mm, "test"), f"fenêtre {fen}")
        c["corr_avec_complet"] = spearman(s, s_rt)
        lignes.append(c)
    s = agreger(rangs(b_rt, FG.FENETRE_DEFAUT, "robuste"))
    c = criteres(periode(s, "test"), periode(mm, "test"), "score robuste (médiane, MAD)")
    c["corr_avec_complet"] = spearman(s, s_rt)
    lignes.append(c)
    tableau("t9_robustesse", pd.DataFrame(lignes))

    # Version révisée : choix sur l'échantillon de validation
    cand = tableau("t10_candidats_validation", classer_candidats(b_rt, mm))
    choix = cand.iloc[0]
    note("v3_fenetre", int(choix["fenetre"]))
    note("v3_schema", choix["schema"])
    note("v3_lissage", int(choix["lissage"]))
    s3 = lisser(agreger(rangs(b_rt, int(choix["fenetre"])), choix["schema"]), int(choix["lissage"]))
    s3.to_frame("v3").join(s2.rename("v2")).to_csv(SORTIE / "series_v2_v3.csv", sep=";", decimal=",")
    lignes = []
    for nom_e in ("validation", "test"):
        for nom, s in (("v2 (initiale)", s2), ("v3 (révisée)", s3)):
            c = criteres(periode(s, nom_e), periode(mm, nom_e), nom)
            c["echantillon"] = nom_e
            lignes.append(c)
    comp = tableau("t11_v2_v3", pd.DataFrame(lignes))
    for _, l in comp.iterrows():
        k = f"{'v2' if l['version'].startswith('v2') else 'v3'}_{l['echantillon']}"
        for col in ("validite", "ic_futur_60", "ecart_extremes_60", "changements_par_an", "equilibre_zones",
                    "part_peur_extreme", "part_avidite_extreme"):
            note(f"{k}_{col}", l[col])
    note("v3_dernier", s3.dropna().iloc[-1])
    note("v3_dernier_zone", FG.libelle(s3.dropna().iloc[-1]))
    note("corr_v2_v3", spearman(s2, s3))
    FIG.score_historique(s3, m["brvmc"], "f12_score_v3", "Indice révisé (version 3)", comparer=s2)

    # Robustesse : définition de la séance illiquide
    ri = tableau("t12_robustesse_illiquidite", robustesse_illiquidite(s2, b_rt, mm))
    assert np.isclose(ri.loc["etude", "h1_spearman"], CHIFFRES["h1_v2_sans_echange_20_rho"]) and \
        ri.loc["etude", "v3_retenue"] == f"{CHIFFRES['v3_fenetre']}/{CHIFFRES['v3_schema']}/{CHIFFRES['v3_lissage']}", \
        "la définition de l'étude ne retrouve pas H1 ou la version révisée"
    for cle, l in ri.iterrows():
        for col in ("part_2008_2012", "part_2022_fin", "part_2026", "h1_spearman", "h1_t_hac",
                    "validite_v2_validation", "validite_v2_test", "corr_avec_etude"):
            note(f"illiq_{cle}_{col}", l[col])
    note("illiq_rho_min", ri["h1_spearman"].abs().min())
    note("illiq_rho_max", ri["h1_spearman"].abs().max())
    note("illiq_t_min", ri["h1_t_hac"].abs().min())
    note("illiq_t_max", ri["h1_t_hac"].abs().max())
    note("illiq_v3_identique", bool((ri["v3_retenue"] == ri.loc["etude", "v3_retenue"]).all()))

    complements(m, w, hhi, b2, r2, s2, s3, s_ex, mm, FIG)

    with open(SORTIE / "chiffres.json", "w", encoding="utf-8") as fichier:
        json.dump(CHIFFRES, fichier, ensure_ascii=False, indent=1, default=str)
    print(f"{len(CHIFFRES)} chiffres, {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
