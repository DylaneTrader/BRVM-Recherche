"""Figures de l'article (PNG 300 dpi, style sobre de publication, nombres à la française)."""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

import indice as FG  # noqa: E402

SORTIE = Path(__file__).resolve().parent / "sortie"
ENCRE, BLEU, BLEU_CLAIR, GRIS = "#1F2933", "#1F4E79", "#8DB3D9", "#8A94A6"
BLEU_MOYEN, ORANGE = "#4F81BD", "#D9822B"
COULEURS_ZONES = ["#EF4444", "#F97316", "#F59E0B", "#6EE7B7", "#10B981"]   # de la peur extrême à la cupidité extrême
ZONES = [z[1] for z in FG.ECHELLE]
NOMS = {"momentum": "Momentum", "participation": "Participation", "force": "Force", "demande": "Demande",
        "vol_baissiere": "Volatilité baissière"}

plt.rcParams.update({
    "font.family": "Calibri", "font.size": 9, "axes.titlesize": 10, "axes.labelsize": 9,
    "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#9AA5B1", "axes.linewidth": 0.6,
    "xtick.color": "#52606D", "ytick.color": "#52606D", "axes.labelcolor": ENCRE, "axes.titlecolor": ENCRE,
    "axes.titleweight": "bold", "axes.titlelocation": "left", "legend.frameon": False, "legend.fontsize": 8,
    "figure.dpi": 150, "savefig.dpi": 300, "savefig.bbox": "tight", "axes.grid": True, "grid.color": "#E4E7EB",
    "grid.linewidth": 0.5, "axes.axisbelow": True, "axes.formatter.use_mathtext": False,
})


def _fr(x, _=None, dec: int = 0, suffixe: str = "") -> str:
    return f"{x:,.{dec}f}".replace(",", " ").replace(".", ",") + suffixe


def pct(dec: int = 0):
    return FuncFormatter(lambda x, _: _fr(x * 100, None, dec, " %"))


def nombre(dec: int = 0):
    return FuncFormatter(lambda x, _: _fr(x, None, dec))


def _annees(ax) -> None:
    ax.xaxis.set_major_locator(mdates.YearLocator(2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))


MOIS = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]


def _log(ax, serie: pd.Series) -> None:
    """Échelle logarithmique avec des graduations lisibles."""
    ax.set_yscale("log")
    lo, hi = float(serie.min()), float(serie.max())
    cand = [25, 50, 75, 100, 150, 200, 250, 300, 400, 500, 600, 800, 1000, 1500, 2000, 3000]
    t = [c for c in cand if lo * 0.95 <= c <= hi * 1.05]
    ax.set_yticks(t)
    ax.yaxis.set_major_formatter(nombre())
    ax.yaxis.set_minor_formatter(FuncFormatter(lambda *_: ""))


def _sauver(fig, nom: str) -> None:
    fig.savefig(SORTIE / f"{nom}.png")
    plt.close(fig)


def marche(m: pd.DataFrame, sonatel: pd.Series, illiquide: pd.Series) -> None:
    fig, axes = plt.subplots(3, 1, figsize=(6.3, 6.4), sharex=True, gridspec_kw={"height_ratios": [2.2, 1, 1]})
    ax = axes[0]
    rt = m["brvmc_rt"] * m["brvmc"].iloc[0] / m["brvmc_rt"].iloc[0]
    ax.plot(m.index, m["brvmc"], color=BLEU, lw=1, label="BRVM Composite (indice de cours)")
    ax.plot(m.index, rt, color=BLEU_CLAIR, lw=1, label="BRVM Composite, dividendes réinvestis (reconstitué)")
    _log(ax, pd.concat([m["brvmc"], rt]))
    ax.set_title("a. Niveau du marché (échelle logarithmique)")
    ax.legend(loc="upper left")
    ax = axes[1]
    s = sonatel.reindex(m.index, method="ffill")
    ax.fill_between(s.index, 0, s, color=BLEU_CLAIR, alpha=0.6, lw=0)
    ax.yaxis.set_major_formatter(pct())
    ax.set_title("b. Poids de Sonatel dans la capitalisation")
    ax = axes[2]
    il = illiquide.rolling(60, min_periods=20).mean()
    ax.plot(il.index, il, color=ENCRE, lw=1)
    ax.yaxis.set_major_formatter(pct())
    ax.set_ylim(0, None)
    ax.set_title("c. Part des séances sans échange ou à cours figé (moyenne sur 60 séances)")
    _annees(ax)
    fig.align_ylabels()
    _sauver(fig, "f1_marche")


def dividendes(mois: pd.Series) -> None:
    fig, ax = plt.subplots(figsize=(6.3, 2.4))
    noms = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."]
    v = mois.reindex(range(1, 13)).fillna(0)
    ax.bar(noms, v, color=[BLEU if k in (5, 6, 7) else BLEU_CLAIR for k in range(1, 13)], width=0.65)
    for i, x in enumerate(v):
        if x >= 0.005:
            ax.text(i, x + 0.01, _fr(x * 100, None, 0, " %"), ha="center", va="bottom", fontsize=7.5, color=ENCRE)
    ax.yaxis.set_major_formatter(pct())
    ax.set_ylim(0, v.max() * 1.18)
    ax.grid(axis="x", visible=False)
    _sauver(fig, "f2_dividendes_par_mois")


def score_historique(s: pd.Series, brvmc: pd.Series, nom: str, titre: str, comparer: pd.Series | None = None) -> None:
    s = s.dropna()
    fig, axes = plt.subplots(2, 1, figsize=(6.3, 4.9), sharex=True, gridspec_kw={"height_ratios": [1, 1.6], "hspace": 0.32})
    ax = axes[0]
    b = brvmc.loc[s.index.min():]
    ax.plot(b.index, b, color=BLEU, lw=0.9)
    _log(ax, b)
    ax.set_title("a. BRVM Composite (échelle logarithmique)")
    ax = axes[1]
    bornes = [0, 25.5, 44.5, 55.5, 75.5, 100]
    for (a, z), c in zip(zip(bornes[:-1], bornes[1:]), COULEURS_ZONES):
        ax.axhspan(a, z, color=c, alpha=0.13, lw=0)
    if comparer is not None:
        cc = comparer.dropna().loc[s.index.min():]
        ax.plot(cc.index, cc, color=GRIS, lw=0.5, alpha=0.8, label="version initiale")
    ax.plot(s.index, s, color=ENCRE, lw=0.6, label="indice" if comparer is None else "version révisée")
    ax.plot(s.index, s.rolling(60).mean(), color=BLEU, lw=1.3, label="moyenne sur 60 séances")
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 25, 45, 55, 75, 100])
    ax.set_title(f"b. {titre}", pad=16)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=3, borderaxespad=0.1, fontsize=7.5)
    for y, z in zip([12, 35, 50, 65, 88], ZONES):
        ax.text(1.005, y, z, transform=ax.get_yaxis_transform(), fontsize=7, va="center", color="#52606D")
    _annees(ax)
    _sauver(fig, nom)


def correlations(corr: pd.DataFrame, vp: np.ndarray) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(6.3, 2.8), gridspec_kw={"width_ratios": [1.35, 1]})
    ax = axes[0]
    noms = [NOMS[c] for c in corr.columns]
    im = ax.imshow(corr.to_numpy(), cmap="RdBu", vmin=-1, vmax=1)
    ax.set_xticks(range(len(noms)), noms, rotation=35, ha="right")
    ax.set_yticks(range(len(noms)), noms)
    ax.grid(False)
    for i in range(len(noms)):
        for j in range(len(noms)):
            ax.text(j, i, _fr(corr.iat[i, j], None, 2), ha="center", va="center", fontsize=7,
                    color="white" if abs(corr.iat[i, j]) > 0.6 else ENCRE)
    ax.set_title("a. Corrélations des composantes")
    ax = axes[1]
    part = vp / vp.sum()
    ax.bar([f"CP{i + 1}" for i in range(len(vp))], part, color=BLEU_CLAIR, width=0.6)
    ax.plot(range(len(vp)), np.cumsum(part), color=BLEU, marker="o", ms=3, lw=1)
    ax.yaxis.set_major_formatter(pct())
    ax.set_ylim(0, 1.05)
    ax.grid(axis="x", visible=False)
    ax.set_title("b. Variance expliquée (ACP)")
    fig.tight_layout()
    _sauver(fig, "f5_correlations_acp")


def cas(c: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(6.3, 4.7), sharex=True, gridspec_kw={"height_ratios": [1, 1.5], "hspace": 0.32})
    ax = axes[0]
    ax.plot(c.index, c["brvmc"], color=BLEU, lw=1.1)
    ax.yaxis.set_major_formatter(nombre())
    ax.set_title("a. BRVM Composite")
    ax = axes[1]
    styles = {"momentum": (BLEU, "-"), "participation": (ORANGE, "-"), "force": (ORANGE, "--"),
              "demande": (BLEU_MOYEN, ":"), "vol_baissiere": (GRIS, "-.")}
    for k, (col, ls) in styles.items():
        ax.plot(c.index, c[k], color=col, ls=ls, lw=0.9, label=NOMS[k])
    ax.plot(c.index, c["score"], color=ENCRE, lw=2, label="Score")
    ax.set_ylim(-2, 102)
    ax.set_title("b. Rangs des composantes et score (0 = peur, 100 = cupidité)", pad=18)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=6, fontsize=7, borderaxespad=0.1,
              handlelength=1.8, columnspacing=1.0)
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: MOIS[mdates.num2date(x).month - 1]))
    _sauver(fig, "f7_cas_octobre_2026")


def h1(par_zone: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(6.3, 2.5))
    for ax, (col, titre, fmt) in zip(axes, [("vol_20", "Volatilité sur 20 séances", pct()),
                                            ("perte_depuis_haut", "Écart au plus haut sur un an", pct()),
                                            ("sans_echange_20", "Séances illiquides (écart à la\nmoyenne de l'année, en points)",
                                             FuncFormatter(lambda x, _: _fr(x * 100, None, 0)))]):
        donnees = [par_zone.loc[par_zone["zone"] == z, col].dropna() for z in ZONES]
        bp = ax.boxplot(donnees, widths=0.55, showfliers=False, patch_artist=True, medianprops={"color": ENCRE})
        for p_, c in zip(bp["boxes"], COULEURS_ZONES):
            p_.set_facecolor(c)
            p_.set_alpha(0.55)
            p_.set_linewidth(0.5)
        ax.set_xticks(range(1, 6), ["PE", "P", "N", "A", "AE"])
        ax.yaxis.set_major_formatter(fmt)
        ax.set_title(titre, fontsize=8.5)
        ax.grid(axis="x", visible=False)
    fig.tight_layout()
    _sauver(fig, "f8_h1_validite")


def h2(t: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(6.3, 2.4), sharey=False)
    for ax, h in zip(axes, sorted(t["horizon"].unique())):
        d = t[t["horizon"] == h].set_index("zone").reindex(ZONES)
        ax.bar(["PE", "P", "N", "A", "AE"], d["rendement_moyen"], color=COULEURS_ZONES, alpha=0.8, width=0.6)
        ax.axhline(0, color="#9AA5B1", lw=0.6)
        ax.yaxis.set_major_formatter(pct(1))
        ax.set_title(f"{h} séances", fontsize=8.5)
        ax.grid(axis="x", visible=False)
    fig.tight_layout()
    _sauver(fig, "f9_h2_rendements_futurs")


def h3(r: pd.DataFrame, mm: pd.DataFrame) -> None:
    d = pd.concat([r[["momentum", "participation"]], mm["part_hausse_20"]], axis=1).dropna().loc["2019":]
    fig, ax = plt.subplots(figsize=(6.3, 2.6))
    ax.plot(d.index, d["momentum"].rolling(10).mean(), color=BLEU, lw=0.9, label="Momentum de l'indice (rang)")
    ax.plot(d.index, d["participation"].rolling(10).mean(), color=ORANGE, lw=0.9, label="Participation des titres (rang)")
    ax.fill_between(d.index, d["momentum"].rolling(10).mean(), d["participation"].rolling(10).mean(),
                    where=(d["momentum"] - d["participation"]).rolling(10).mean() > 40, color=COULEURS_ZONES[0],
                    alpha=0.18, lw=0, label="indice haut, participation basse")
    ax.set_ylim(0, 100)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=3, fontsize=7, borderaxespad=0.1)
    _annees(ax)
    ax.xaxis.set_major_locator(mdates.YearLocator(1))
    _sauver(fig, "f10_h3_divergences")


def h4(mois: pd.DataFrame) -> None:
    noms = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
    fig, axes = plt.subplots(1, 2, figsize=(6.3, 2.4), sharey=True)
    for ax, (a, b, titre) in zip(axes, [("momentum_v2", "momentum_rt", "a. Momentum (rang moyen)"),
                                        ("v2", "rt", "b. Score (moyenne)")]):
        x = np.arange(12)
        ax.bar(x - 0.2, mois[a], width=0.38, color=GRIS, label="indice de cours")
        ax.bar(x + 0.2, mois[b], width=0.38, color=BLEU, label="dividendes réinvestis")
        ax.axvspan(3.5, 6.5, color=BLEU_CLAIR, alpha=0.18, lw=0)
        ax.set_xticks(x, noms)
        ax.set_ylim(0, 75)
        ax.axhline(50, color="#9AA5B1", lw=0.6, ls="--")
        ax.set_title(titre, fontsize=8.5)
        ax.grid(axis="x", visible=False)
    axes[0].legend(loc="lower left", fontsize=7)
    fig.tight_layout()
    _sauver(fig, "f11_h4_saison")


def autocorrelations(acf: pd.DataFrame, n: int) -> None:
    """Autocorrélations des rendements quotidiens du BRVM Composite et de leurs valeurs absolues."""
    fig, axes = plt.subplots(1, 2, figsize=(6.3, 2.3), sharey=True)
    borne = 1.96 / np.sqrt(n)
    for ax, (col, titre) in zip(axes, [("rendement", "a. Rendements"), ("rendement_absolu", "b. Rendements absolus")]):
        ax.bar(acf.index, acf[col], color=BLEU, width=0.7)
        ax.axhspan(-borne, borne, color=BLEU_CLAIR, alpha=0.35, lw=0)
        ax.axhline(0, color="#9AA5B1", lw=0.6)
        ax.set_title(titre, fontsize=8.5)
        ax.set_xlabel("retard (séances)")
        ax.yaxis.set_major_formatter(nombre(2))
        ax.grid(axis="x", visible=False)
    fig.tight_layout()
    _sauver(fig, "f14_autocorrelations")


def reconstitution(glissant: pd.DataFrame) -> None:
    """Corrélation glissante sur 250 séances des rendements quotidiens : marché reconstitué contre BRVM Composite,
    BRVM Composite dividendes réinvestis contre l'indice de rendement total SikaFinance."""
    fig, ax = plt.subplots(figsize=(6.3, 2.4))
    ax.plot(glissant.index, glissant["marche"], color=BLEU, lw=1, label="Marché reconstitué et BRVM Composite")
    ax.plot(glissant.index, glissant["rt_sikatr"], color=ORANGE, lw=1,
            label="Dividendes réinvestis (reconstitué) et indice SikaFinance")
    ax.set_ylim(0, 1.05)
    ax.yaxis.set_major_formatter(nombre(1))
    ax.legend(loc="lower right", fontsize=7)
    _annees(ax)
    _sauver(fig, "f15_reconstitution")


def autocorrelations_score(acf: pd.DataFrame) -> None:
    """Autocorrélation du score selon le retard, versions initiale et révisée."""
    fig, ax = plt.subplots(figsize=(6.3, 2.3))
    ax.plot(acf.index, acf["v2"], color=GRIS, lw=1.2, label="version initiale")
    ax.plot(acf.index, acf["v3"], color=BLEU, lw=1.2, label="version révisée")
    ax.axhline(0, color="#9AA5B1", lw=0.6)
    ax.set_xlabel("retard (séances)")
    ax.yaxis.set_major_formatter(nombre(1))
    ax.legend(loc="upper right", fontsize=7)
    _sauver(fig, "f16_autocorrelations_score")


def hors_grands(v2: pd.Series, hors: pd.Series) -> None:
    """Version initiale et version calculée sans les cinq premières capitalisations, depuis 2020."""
    fig, ax = plt.subplots(figsize=(6.3, 2.5))
    bornes = [0, 25.5, 44.5, 55.5, 75.5, 100]
    for (a, z), c in zip(zip(bornes[:-1], bornes[1:]), COULEURS_ZONES):
        ax.axhspan(a, z, color=c, alpha=0.10, lw=0)
    ax.plot(v2.index, v2.rolling(20).mean(), color=GRIS, lw=1, label="version initiale")
    ax.plot(hors.index, hors.rolling(20).mean(), color=BLEU, lw=1, label="sans les cinq premières capitalisations")
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 25, 45, 55, 75, 100])
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, fontsize=7, borderaxespad=0.1)
    _annees(ax)
    ax.xaxis.set_major_locator(mdates.YearLocator(1))
    _sauver(fig, "f17_hors_grands")


def h5(t: pd.DataFrame) -> None:
    d = t[t["echantillon"] == "test"].set_index("version")
    fig, axes = plt.subplots(1, 3, figsize=(6.3, 2.3))
    for ax, (col, titre, fmt) in zip(axes, [("validite", "Validité (ρ moyen)", nombre(2)),
                                            ("changements_par_an", "Changements de zone par an", nombre(0)),
                                            ("equilibre_zones", "Équilibre des zones", nombre(2))]):
        ax.barh(range(len(d)), d[col], color=BLEU_CLAIR, height=0.55)
        ax.set_yticks(range(len(d)), d.index if ax is axes[0] else [""] * len(d), fontsize=7.5)
        ax.invert_yaxis()
        ax.xaxis.set_major_formatter(fmt)
        ax.set_title(titre, fontsize=8.5)
        ax.grid(axis="y", visible=False)
    fig.tight_layout()
    _sauver(fig, "f13_h5_ponderations")

