"""Données de l'étude Fear & Greed BRVM, tirées de GitHub au commit figé de ``recherche/sources.json``.

- cours bruts des actions (manquants les jours sans échange, jamais inventés), valeurs échangées en FCFA,
  BRVM Composite publié ;
- cours dividendes nets réinvestis, titre par titre (les dividendes de la base commencent en 2016) ;
- BRVM Composite dividendes réinvestis : rendement publié de l'indice plus le rendement en dividendes du
  marché le jour du détachement (poids de la veille x dividende / cours de la veille) ;
- marché reconstitué, pondéré par les capitalisations de la veille, en indice de cours et dividendes
  réinvestis, depuis 2008 ;
- dividendes retenus, séances illiquides (règles de ``commun.marche``) et leurs variantes pour le test
  de robustesse.
"""
from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

RECHERCHE = Path(__file__).resolve().parents[1]
if str(RECHERCHE) not in sys.path:
    sys.path.insert(0, str(RECHERCHE))

from commun import depot  # noqa: E402
from commun.marche import Marche, cours_fige  # noqa: E402

DATA = depot.data("brvm")
M = Marche(DATA)


@lru_cache(maxsize=1)
def base_indice() -> tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
    """(cours, valeurs FCFA, BRVM Composite) sur les séances publiées de l'indice."""
    return M.panneaux()


@lru_cache(maxsize=1)
def dividendes() -> pd.DataFrame:
    """Dividendes retenus (montants cohérents avec les cours), au nominal actuel."""
    d = M.dividendes_retenus().copy()
    d["Date_Detachement"] = pd.to_datetime(d["Date_Detachement"])
    return d


@lru_cache(maxsize=1)
def cours_dividendes_reinvestis() -> pd.DataFrame:
    """Clôtures (dernier cours connu) ajustées des dividendes : chaque dividende est réinvesti à la clôture
    de la veille du détachement. Montant net (le brut n'est connu que pour les exercices récents)."""
    cours, _, indice = base_indice()
    px = cours.ffill()
    s = px.index
    col_montant = "Montant_Net_FCFA"
    for t, g in dividendes().groupby("Ticker"):
        code = t.replace(".", "_")
        if code not in px.columns:
            continue
        x = px[code].to_numpy(dtype=float)
        facteur = np.ones(len(s))
        for jour, montant in zip(g["Date_Detachement"], g[col_montant]):
            k = int(s.searchsorted(jour))
            if k == 0 or k >= len(s) or not np.isfinite(x[k - 1]) or x[k - 1] <= 0 or not np.isfinite(montant):
                continue
            f = 1 - float(montant) / x[k - 1]
            if 0 < f < 1:
                facteur[:k] *= f
        px[code] = x * facteur
    return px


@lru_cache(maxsize=1)
def poids() -> pd.DataFrame:
    """Poids de chaque titre dans la capitalisation, par date (colonnes au format des fichiers : SNTS_sn)."""
    return M.poids()


def niveau_marche(prix: pd.DataFrame, exclus: tuple[str, ...] = ()) -> pd.Series:
    """Indice pondéré par les capitalisations de la veille, base 100 à la première séance, poids
    renormalisés chaque séance sur les titres qui ont un cours. ``exclus`` : titres retirés."""
    px = prix.ffill()
    cols = [c for c in px.columns if c not in exclus]
    px = px[cols]
    w = poids().reindex(px.index, method="ffill").reindex(columns=cols).fillna(0.0).shift(1)
    r = px.pct_change(fill_method=None)
    w = w.where(r.notna() & (w > 0), 0.0)
    den = w.sum(axis=1)
    jour = (w.div(den.where(den > 0), axis=0).fillna(0.0) * r.fillna(0.0)).sum(axis=1)
    jour.iloc[0] = 0.0
    return 100 * (1 + jour).cumprod()


def rendement_dividendes_marche() -> pd.Series:
    """Rendement en dividendes du marché à chaque séance : somme sur les titres du poids de la veille x
    dividende net détaché / cours de la veille (0 hors détachement)."""
    cours, _, _ = base_indice()
    px = cours.ffill()
    s = px.index
    w = poids().reindex(s, method="ffill").reindex(columns=px.columns).fillna(0.0).shift(1)
    rd = pd.DataFrame(0.0, index=s, columns=px.columns)
    for t, g in dividendes().groupby("Ticker"):
        code = t.replace(".", "_")
        if code not in px.columns:
            continue
        for jour, montant in zip(g["Date_Detachement"], g["Montant_Net_FCFA"]):
            k = int(s.searchsorted(jour))
            veille = px[code].iloc[k - 1] if 0 < k < len(s) else np.nan
            if np.isfinite(veille) and veille > 0 and np.isfinite(montant):
                rd.iloc[k, rd.columns.get_loc(code)] += float(montant) / veille
    return (w.fillna(0.0) * rd).sum(axis=1)


@lru_cache(maxsize=1)
def marches() -> pd.DataFrame:
    """BRVM Composite publié, marché reconstitué en cours et dividendes réinvestis, et versions sans
    Sonatel et sans les cinq plus grandes capitalisations (au dernier jour)."""
    cours, _, indice = base_indice()
    tr = cours_dividendes_reinvestis()
    grands = list(poids().iloc[-1].sort_values(ascending=False).index[:5])
    rd = rendement_dividendes_marche()
    brvmc_rt = indice.iloc[0] * ((1 + indice.pct_change().fillna(0.0)) * (1 + rd)).cumprod()
    out = pd.DataFrame({
        "brvmc": indice,
        "brvmc_rt": brvmc_rt,
        "sikatr": M.sur_seances(M.indice("SIKATR")["Cloture"]).reindex(indice.index),
        "marche_cours": niveau_marche(cours),
        "marche_rt": niveau_marche(tr),
        "rt_sans_sonatel": niveau_marche(tr, ("SNTS_sn",)),
        "rt_sans_5_grands": niveau_marche(tr, tuple(grands)),
    })
    out.attrs["grands"] = grands
    return out


@lru_cache(maxsize=1)
def sans_echange() -> pd.DataFrame:
    """1 si la séance est illiquide pour le titre (aucun titre échangé, ou cours figé : plus de trois
    clôtures égales de suite), 0 sinon, NaN avant sa première cotation."""
    cours, _, _ = base_indice()
    m = M.illiquide()
    m.columns = [c.replace(".", "_") for c in m.columns]
    return m.reindex(index=cours.index, columns=cours.columns)


@lru_cache(maxsize=8)
def sans_echange_selon(regle: str) -> pd.DataFrame:
    """Séances illiquides selon d'autres définitions (test de robustesse), au format de ``sans_echange`` :
    ``fige:n`` : aucun titre échangé ou plus de n clôtures égales de suite (``fige:3`` : règle de l'étude) ;
    ``volume`` : aucun titre échangé ; ``lot`` : aucun titre échangé ou clôture égale à la précédente
    (rendement nul, Lesmond, Ogden et Trzcinka, 1999)."""
    s = M.seances()
    cols = {}
    for t in M.tickers():
        a = M.action(t)
        if a.empty:
            continue
        echange = a["Volume_Titres"].fillna(0) > 0
        if regle.startswith("fige:"):
            actif = echange & ~cours_fige(a["Cloture"], int(regle[5:]))
        elif regle == "lot":
            actif = echange & a["Cloture"].ne(a["Cloture"].shift())
        elif regle == "volume":
            actif = echange
        else:
            raise ValueError(f"règle inconnue : {regle}")
        actif = actif[~actif.index.duplicated()].reindex(s, fill_value=False)
        col = np.where(actif.to_numpy(dtype=bool), 0.0, 1.0)
        col[s < a.index.min()] = np.nan
        cols[t.replace(".", "_")] = col
    cours, _, _ = base_indice()
    return pd.DataFrame(cols, index=s).reindex(index=cours.index, columns=cours.columns)


__all__ = ["DATA", "M", "base_indice", "dividendes", "cours_dividendes_reinvestis", "poids",
           "niveau_marche", "marches", "sans_echange", "sans_echange_selon"]
