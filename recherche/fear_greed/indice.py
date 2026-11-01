"""Indice Fear & Greed BRVM, version initiale : score de sentiment de 0 (peur extrême) à 100 (cupidité extrême).

Cinq composantes orientées dans le même sens (hausse du marché = cupidité), chacune ramenée à son rang
percentile sur une fenêtre glissante de 504 séances (environ deux ans) ; le score est la moyenne des
rangs disponibles. Transposition à la BRVM de la méthode de CNN, sans ses composantes sur les options,
les obligations à haut rendement et les valeurs refuges.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

FENETRE_DEFAUT = 504          # séances de la fenêtre du rang (environ 2 ans)
MIN_OBS_RANG = 250            # séances minimales avant de publier un rang
MM_MOMENTUM = 125             # CNN : S&P 500 face à sa moyenne de 125 jours
MM_PARTICIPATION = 50
JOURS_52_SEMAINES = 250
LISSAGE_FORCE = 10
FENETRE_DEMANDE = 20
VOL_COURT, VOL_LONG = 20, 120

NOMS = {
    "momentum": "Momentum",
    "participation": "Participation",
    "force": "Force",
    "demande": "Demande",
    "vol_baissiere": "Volatilité baissière",
}

# Échelle de CNN : (borne haute incluse, libellé)
ECHELLE = [
    (25, "Peur extrême"),
    (44, "Peur"),
    (55, "Neutre"),
    (75, "Cupidité"),
    (100, "Cupidité extrême"),
]


def libelle(score: float) -> str:
    """Zone du score, classé une fois arrondi à l'entier."""
    s = int(round(score))
    for haut, lbl in ECHELLE:
        if s <= haut:
            return lbl
    return ECHELLE[-1][1]


def rang_glissant(s: pd.Series, fenetre: int = FENETRE_DEFAUT, min_obs: int = MIN_OBS_RANG) -> pd.Series:
    """Rang percentile (0-100) de chaque valeur parmi les ``fenetre`` dernières (elle comprise)."""
    return s.rolling(fenetre, min_periods=min_obs).apply(lambda x: (x <= x[-1]).mean() * 100, raw=True)


def valeurs_brutes(cours: pd.DataFrame, valeurs: pd.DataFrame, indice: pd.Series) -> pd.DataFrame:
    """Les cinq mesures avant classement, orientées (plus haut = plus de cupidité)."""
    cf = cours.ffill()                        # dernier cours connu pour les moyennes et plus hauts ou bas
    echange = cours.notna()
    rend = cf.pct_change(fill_method=None)
    # titre suivi : coté (cours connu) sur les 60 dernières séances au moins
    actifs = cf.notna() & (cf.notna().rolling(60).sum() >= 60)
    n_actifs = actifs.sum(axis=1).replace(0, np.nan)

    out = pd.DataFrame(index=indice.index)
    out["momentum"] = indice / indice.rolling(MM_MOMENTUM).mean() - 1

    mm = cf.rolling(MM_PARTICIPATION, min_periods=int(MM_PARTICIPATION * 0.8)).mean()
    out["participation"] = ((cf > mm) & actifs).sum(axis=1) / n_actifs

    hauts = cf >= cf.rolling(JOURS_52_SEMAINES, min_periods=200).max()
    bas = cf <= cf.rolling(JOURS_52_SEMAINES, min_periods=200).min()
    net = ((hauts.astype(int) - bas.astype(int)) * actifs).sum(axis=1) / n_actifs
    out["force"] = net.rolling(LISSAGE_FORCE).mean()

    v = valeurs.reindex(columns=cours.columns).fillna(0.0)
    hausse = (v * ((rend > 0) & echange)).sum(axis=1).rolling(FENETRE_DEMANDE).sum()
    baisse = (v * ((rend < 0) & echange)).sum(axis=1).rolling(FENETRE_DEMANDE).sum()
    out["demande"] = hausse / (hausse + baisse).replace(0, np.nan)

    neg = indice.pct_change().clip(upper=0)
    semi_court = np.sqrt((neg ** 2).rolling(VOL_COURT).mean())
    semi_long = np.sqrt((neg ** 2).rolling(VOL_LONG).mean())
    out["vol_baissiere"] = -(semi_court / semi_long.replace(0, np.nan))   # inversée : calme = cupidité
    return out


def calculer(cours: pd.DataFrame, valeurs: pd.DataFrame, indice: pd.Series,
             fenetre: int = FENETRE_DEFAUT) -> pd.DataFrame:
    """Rangs 0-100 des cinq composantes, séance par séance."""
    brut = valeurs_brutes(cours, valeurs, indice)
    return pd.DataFrame({k: rang_glissant(brut[k], fenetre) for k in brut})


def score(rangs: pd.DataFrame, poids: dict[str, float] | None = None) -> pd.Series:
    """Moyenne pondérée des rangs disponibles (poids renormalisés si une composante manque)."""
    poids = {k: float(w) for k, w in (poids or {k: 1.0 for k in rangs}).items() if k in rangs and w > 0}
    if not poids:
        return pd.Series(np.nan, index=rangs.index)
    r = rangs[list(poids)]
    w = pd.Series(poids)
    masque = r.notna()
    return (r.fillna(0) * w).sum(axis=1) / (masque * w).sum(axis=1).replace(0, np.nan)
