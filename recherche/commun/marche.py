"""Marché actions de la BRVM : lecture des fichiers de données et règles de traitement.

Autonome : ne dépend que de pandas et numpy, et lit les fichiers extraits de GitHub par ``depot``
(``data/`` du dépôt de collecte, au commit figé de ``recherche/sources.json``).

Fichiers lus (CSV ``;``, décimale ``,``, UTF-8) :
- ``actions/<TICKER>_historique.csv`` : une ligne par séance où le titre a coté (ouverture, plus haut,
  plus bas, clôture, volume en titres, valeur échangée en FCFA) ;
- ``indices/<CODE>_historique.csv`` : clôtures des indices publiés (BRVM Composite, SIKATR…) ;
- ``dividendes/dividendes.csv`` : dividendes par action, montants au nominal des cours ;
- ``Composition_flottante.xlsx`` : poids de chaque titre dans la capitalisation, par séance.

Règles :
- divisions du nominal : les cours antérieurs sont divisés par le rapport à partir de la première
  séance où la clôture l'est (``OPERATIONS``) ; les opérations passées sont déjà intégrées aux cours
  publiés ;
- dividendes : nets d'IRVM au taux du particulier (12 %) quand le montant publié est brut ; retenus
  s'ils sont cohérents avec les cours (``dividendes_retenus``) ;
- séance illiquide : aucun titre échangé, ou cours figé (plus de trois clôtures égales de suite).
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

TAUX_IRVM = 12.0                       # IRVM du particulier, en %
DIVIDENDE_MAX = 0.15                   # au-delà (part du cours de la veille), le dividende doit se voir...
CONFIRMATION = 0.60                    # ... dans une baisse du cours d'au moins 60 % de son montant
DELAI_BAISSE = pd.Timedelta(days=10)   # première clôture cherchée au plus 10 jours après le détachement
CONTROLES = {"courant": "retenu : au plus 15 % du cours", "baisse": "retenu : baisse du cours confirmée",
             "corrige": "retenu : confirmé à la source", "ecarte": "écarté : au-delà de 15 %, non confirmé",
             "sans_cours": "écarté : pas de cours la veille", "apres_fin": "écarté : après la dernière séance"}
COURS_FIGE = 3                         # plus de 3 clôtures égales de suite : cours figé
COLONNES_COURS = ("Ouverture", "Plus_Haut", "Plus_Bas", "Cloture")


# ---------------------------------------------------------------------------
# Divisions du nominal
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Operation:
    ticker: str
    date: pd.Timestamp            # première séance annoncée au nouveau nominal
    rapport: float                # 10 : une action devient dix
    source: str


# Opérations pas encore intégrées aux cours publiés : les cours antérieurs sont ajustés au chargement.
OPERATIONS: tuple[Operation, ...] = (
    Operation("SNTS.sn", pd.Timestamp("2026-10-26"), 10,
              "Fractionnement de l'action Sonatel par dix : bulletin officiel de la cote du 17/09/2026, "
              "effet le 26/10/2026."),
)
FENETRE_AVANT = pd.Timedelta(days=7)
FENETRE_APRES = pd.Timedelta(days=60)
TOLERANCE = 0.25


def premiere_seance(op: Operation, cloture: pd.Series) -> pd.Timestamp | None:
    """Première séance, entre 7 jours avant et 60 jours après la date annoncée, où la clôture est divisée
    par le rapport (à 25 % près) ; None si elle n'est pas dans les données."""
    s = pd.to_numeric(cloture, errors="coerce").dropna()
    s = s[s > 0].sort_index()
    s = s[~s.index.duplicated(keep="last")]
    r = (s / s.shift(1)).dropna()
    fen = r[(r.index >= op.date - FENETRE_AVANT) & (r.index <= op.date + FENETRE_APRES)]
    ok = fen[(fen * op.rapport - 1).abs() <= TOLERANCE]
    return pd.Timestamp(ok.index[0]) if len(ok) else None


def ajuster_cours(df: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """Cours au nominal le plus récent (dates en index)."""
    ops = [op for op in OPERATIONS if op.ticker == ticker]
    if not ops or df.empty or "Cloture" not in df.columns:
        return df
    dates = pd.DatetimeIndex(df.index)
    facteur = np.ones(len(df))
    cloture = pd.Series(pd.to_numeric(df["Cloture"], errors="coerce").to_numpy(), index=dates)
    for op in ops:
        debut = premiere_seance(op, cloture)
        if debut is not None:
            facteur[dates < debut] /= op.rapport
    if (facteur == 1.0).all():
        return df
    out = df.copy()
    for col in COLONNES_COURS:
        if col in out.columns:
            out[col] = pd.to_numeric(out[col], errors="coerce") * facteur
    if "Volume_Titres" in out.columns:
        out["Volume_Titres"] = (pd.to_numeric(out["Volume_Titres"], errors="coerce") / facteur).round()
    return out


def ticker(fichier: Path) -> str:
    """``SNTS_sn_historique.csv`` -> ``SNTS.sn``."""
    return Path(fichier).name.replace("_historique.csv", "").replace("_", ".", 1)


# ---------------------------------------------------------------------------
# Lecture
# ---------------------------------------------------------------------------

def lire_brut(fichier: Path) -> pd.DataFrame:
    """Historique tel que publié : dates valides, dernière ligne gardée pour une date en double."""
    d = pd.read_csv(fichier, sep=";", decimal=",", encoding="utf-8-sig", parse_dates=["Date"])
    d = d.dropna(subset=["Date"]).set_index("Date").sort_index()
    return d[~d.index.duplicated(keep="last")]


def lire_seances(fichier: Path) -> pd.DataFrame:
    """Historique limité aux séances cotées : clôture connue, première ligne gardée pour une date en double."""
    df = pd.read_csv(fichier, sep=";", decimal=",", encoding="utf-8-sig")
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    for col in ("Ouverture", "Plus_Haut", "Plus_Bas", "Cloture", "Volume_Titres", "Volume_FCFA", "Variation_Pct"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df.dropna(subset=["Date", "Cloture"]).drop_duplicates("Date").sort_values("Date").set_index("Date")


class Marche:
    """Données actions lues dans un dossier ``data/``."""

    def __init__(self, data: Path):
        self.data = Path(data)
        self.actions = self.data / "actions"
        self.dossier_indices = self.data / "indices"

    def fichiers(self) -> list[Path]:
        return sorted(self.actions.glob("*_historique.csv"))

    @lru_cache(maxsize=1)
    def panneaux(self, indice: str = "BRVMC") -> tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
        """(cours, valeurs échangées en FCFA, indice) sur les séances publiées de l'indice. Un titre non
        échangé n'a pas de ligne : son cours reste manquant (jamais inventé), sa valeur échangée vaut 0.
        Colonnes au format des fichiers (``SNTS_sn``)."""
        ind = lire_brut(self.dossier_indices / f"{indice}_historique.csv")["Cloture"].astype(float)
        cours, valeurs = {}, {}
        for f in self.fichiers():
            d = ajuster_cours(lire_brut(f), ticker(f))
            if d.empty or "Cloture" not in d:
                continue
            t = f.name.replace("_historique.csv", "")
            cours[t] = d["Cloture"].astype(float)
            if "Volume_FCFA" in d:
                valeurs[t] = pd.to_numeric(d["Volume_FCFA"], errors="coerce")
        s = ind.index
        return pd.DataFrame(cours).reindex(s), pd.DataFrame(valeurs).reindex(s).fillna(0.0), ind

    @lru_cache(maxsize=64)
    def action(self, t: str) -> pd.DataFrame:
        """Séances cotées d'un titre (code ``SNTS.sn``), au nominal le plus récent."""
        return ajuster_cours(lire_seances(self.actions / f"{t.replace('.', '_', 1)}_historique.csv"), t)

    def tickers(self) -> list[str]:
        return [ticker(f) for f in self.fichiers()]

    @lru_cache(maxsize=16)
    def indice(self, code: str) -> pd.DataFrame:
        return lire_seances(self.dossier_indices / f"{code}_historique.csv")

    def seances(self) -> pd.DatetimeIndex:
        """Calendrier de la bourse : les séances du BRVM Composite."""
        return self.indice("BRVMC").index

    def sur_seances(self, df: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
        """Dernière valeur connue à chaque séance, rien avant la première."""
        s = self.seances()
        return df.reindex(df.index.union(s)).ffill().reindex(s)

    @lru_cache(maxsize=1)
    def clotures(self) -> pd.DataFrame:
        """Clôtures par titre (codes ``SNTS.sn``) aux dates où au moins un titre a coté."""
        return pd.DataFrame({t: self.action(t)["Cloture"] for t in self.tickers()})

    # -- dividendes ---------------------------------------------------------

    def dividendes(self) -> pd.DataFrame:
        """Dividendes publiés, montant net d'IRVM au taux du particulier là où le brut est connu."""
        df = pd.read_csv(self.data / "dividendes" / "dividendes.csv", sep=";", decimal=",", encoding="utf-8-sig")
        for col in ("Date_Detachement", "Date_Paiement"):
            df[col] = pd.to_datetime(df[col], errors="coerce")
        for col in ("Montant_Net_FCFA", "Montant_Brut_FCFA"):
            df[col] = pd.to_numeric(df[col], errors="coerce")
        brut = df["Montant_Brut_FCFA"]
        df["Montant_Net_FCFA"] = df["Montant_Net_FCFA"].where(brut.isna(), (brut * (1 - TAUX_IRVM / 100)).round(4))
        return self._dividendes_au_nominal(df.sort_values("Date_Detachement"))

    def _dividendes_au_nominal(self, df: pd.DataFrame) -> pd.DataFrame:
        """Montants détachés avant une division du nominal visible dans les cours : divisés par le rapport."""
        out = df.copy()
        for op in OPERATIONS:
            try:
                cl = lire_brut(self.actions / f"{op.ticker.replace('.', '_', 1)}_historique.csv")["Cloture"]
            except (OSError, KeyError):
                continue
            debut = premiere_seance(op, cl)
            if debut is None:
                continue
            m = (out["Ticker"] == op.ticker) & (out["Date_Detachement"] < debut)
            for col in ("Montant_Net_FCFA", "Montant_Brut_FCFA"):
                out.loc[m, col] = out.loc[m, col] / op.rapport
        return out

    @lru_cache(maxsize=1)
    def controle_dividendes(self) -> pd.DataFrame:
        """Chaque dividende daté, avec sa part du cours de la veille, la baisse du cours au détachement et son
        statut (``CONTROLES``) : au plus 15 % de la clôture de la veille, retenu ; au-delà, retenu seulement
        si le cours a baissé d'au moins 60 % du montant à la première clôture dans les 10 jours, ou si le
        dividende a été corrigé et confirmé à la source (colonne ``Correction``). Sans cours la veille, ou
        après la dernière séance, rien n'est vérifiable : non retenu."""
        d = self.dividendes().dropna(subset=["Date_Detachement", "Montant_Net_FCFA"])
        d = d[d["Montant_Net_FCFA"] > 0]
        d = d.drop_duplicates(["Ticker", "Exercice", "Date_Detachement"]).sort_values("Date_Detachement")
        s = self.seances()
        brut = self.clotures()
        veilles = brut.reindex(brut.index.union(s)).ffill().reindex(s)
        cl = {t: brut[t].dropna() for t in d["Ticker"].unique() if t in brut.columns}
        part, baisse = [], []
        for x in d.itertuples():
            k = int(s.searchsorted(x.Date_Detachement))
            p, b = np.nan, np.nan
            if 0 < k < len(s) and x.Ticker in cl:
                veille = veilles[x.Ticker].iloc[k - 1]
                if np.isfinite(veille) and veille > 0:
                    p = float(x.Montant_Net_FCFA) / veille
                    c = cl[x.Ticker]
                    jour = c[(c.index >= s[k]) & (c.index <= s[k] + DELAI_BAISSE)]
                    if len(jour):
                        b = float(1 - jour.iloc[0] / veille)
            part.append(p)
            baisse.append(b)
        d["part_du_cours"], d["baisse_du_jour"] = part, baisse
        corrige = d["Correction"].fillna("").astype(str).str.len().gt(0) if "Correction" in d.columns else False
        statut = np.select(
            [d["Date_Detachement"] > s[-1], d["part_du_cours"].isna(), d["part_du_cours"] <= DIVIDENDE_MAX,
             d["baisse_du_jour"] >= CONFIRMATION * d["part_du_cours"], corrige],
            ["apres_fin", "sans_cours", "courant", "baisse", "corrige"], "ecarte")
        d["statut"] = statut
        d["retenu"] = d["statut"].isin(["courant", "baisse", "corrige"])
        return d

    def dividendes_retenus(self) -> pd.DataFrame:
        """Dividendes dont le montant est cohérent avec les cours (``controle_dividendes``)."""
        d = self.controle_dividendes()
        return d[d["retenu"]]

    # -- capitalisations et liquidité ---------------------------------------

    @lru_cache(maxsize=1)
    def poids(self) -> pd.DataFrame:
        """Poids de chaque titre dans la capitalisation, par séance (colonnes ``SNTS_sn``)."""
        w = pd.read_excel(self.data / "Composition_flottante.xlsx", sheet_name="Ponderations_totales")
        w["Date"] = pd.to_datetime(w["Date"], errors="coerce")
        w = w.dropna(subset=["Date"]).set_index("Date").sort_index()
        cours, _, _ = self.panneaux()
        codes = {c.split("_")[0]: c for c in cours.columns}
        w = w.rename(columns=codes)
        return w[[c for c in w.columns if c in codes.values()]].fillna(0.0)

    @lru_cache(maxsize=2)
    def illiquide(self, fige: int = COURS_FIGE) -> pd.DataFrame:
        """1 les séances sans échange (volume nul) ou dans un cours figé (plus de ``fige`` clôtures égales
        de suite), 0 sinon, NaN avant la première cotation. Colonnes ``SNTS.sn``."""
        s = self.seances()
        cols = {}
        for t in self.tickers():
            a = self.action(t)
            if a.empty:
                continue
            actif = (a["Volume_Titres"].fillna(0) > 0) & ~cours_fige(a["Cloture"], fige)
            actif = actif[~actif.index.duplicated()].reindex(s, fill_value=False)
            col = np.where(actif.to_numpy(dtype=bool), 0.0, 1.0)
            col[s < a.index.min()] = np.nan
            cols[t] = col
        return pd.DataFrame(cols, index=s)


def cours_fige(cloture: pd.Series, seuil: int) -> pd.Series:
    """Vrai pour les séances d'une suite de clôtures égales plus longue que ``seuil``."""
    meme = cloture.eq(cloture.shift())
    groupe = (~meme).cumsum()
    longueur = meme.groupby(groupe).transform("sum") + 1
    return longueur > seuil
