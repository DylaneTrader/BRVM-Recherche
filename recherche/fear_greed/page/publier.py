"""Page publique de l'indice Fear & Greed BRVM (version révisée, la même que BRVM app).

Calcule l'indice avec `indice.py` sur les données publiques de brvm-py (cours ajustés des divisions,
valeurs échangées en FCFA, BRVM Composite, dividendes retenus, nombre de titres), puis écrit un site
statique :

    site/index.html             page lisible, sans script ni dépendance extérieure (gabarit modele.html)
    site/etude/*.png            figures de l'article, reprises de recherche/fear_greed/sortie
    site/fear_greed.json        dernière valeur, zone, composantes et historique
    site/fear_greed.csv         historique complet, séance par séance

    python recherche/fear_greed/page/publier.py --sortie site

Le workflow `.github/workflows/fear_greed_page.yml` le lance chaque jour de séance et publie le site
sur GitHub Pages.
"""
from __future__ import annotations

import argparse
import html
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import indice as FG  # noqa: E402

# Couleurs des zones, les mêmes que les figures de l'article
COULEURS = {"Peur extrême": "#e85d5d", "Peur": "#f28c3c", "Neutre": "#f2ad3a",
            "Cupidité": "#7fdcb5", "Cupidité extrême": "#2fb886"}
SIGLES = {"Peur extrême": "PE", "Peur": "P", "Neutre": "N", "Cupidité": "C", "Cupidité extrême": "CE"}
BORNES = [(0, 25), (25, 44), (44, 55), (55, 75), (75, 100)]
ICI = Path(__file__).resolve().parent
SORTIE_ETUDE = ICI.parent / "sortie"
PDF = "https://github.com/DylaneTrader/BRVM-Recherche/blob/main/recherche/fear_greed/Fear_Greed_BRVM.pdf"


def donnees() -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, dict]:
    """(cours, valeurs, BRVM Composite, BRVM Composite dividendes réinvestis, infos de l'export)."""
    import brvm

    ix = brvm.indice("BRVMC")
    ix = ix["cloture"] if "cloture" in ix else ix.iloc[:, -1]
    ix = ix.astype(float)
    cours = brvm.panneau("cloture").reindex(ix.index)
    valeurs = brvm.panneau("volume_fcfa").reindex(index=ix.index, columns=cours.columns).fillna(0.0)
    # Poids dans la capitalisation : cours du jour x nombre de titres actuel (brvm-py ne publie pas
    # l'historique des pondérations ; écart négligeable, voir README).
    soc = brvm.societes()
    if "ticker" in soc:
        soc = soc.set_index("ticker")
    n = pd.to_numeric(soc["nombre_titres"], errors="coerce").reindex(cours.columns)
    cap = cours.ffill().mul(n, axis=1)
    poids = cap.div(cap.sum(axis=1).replace(0, np.nan), axis=0)
    d = brvm.dividendes(retenus=True)
    div = pd.DataFrame({"ticker": d["ticker"],
                        "date_detachement": pd.to_datetime(d["date_detachement"], errors="coerce"),
                        "montant": pd.to_numeric(d["montant_net_particulier_fcfa"], errors="coerce")}).dropna()
    rt = FG.indice_dividendes_reinvestis(cours, ix, poids, div)
    return cours, valeurs, ix, rt, brvm.infos()


def calculer(cours, valeurs, ix, rt) -> pd.DataFrame:
    rangs = FG.calculer(cours, valeurs, ix, FG.FENETRE_REVISEE, indice_tendance=rt)
    out = rangs.copy()
    pil = FG.piliers(rangs)
    for k in pil:
        out[k] = pil[k]
    out["score"] = FG.score_revise(rangs)
    out["brvmc"] = ix
    return out.dropna(subset=["score"])


def _fr(x, d=0, signe=False) -> str:
    if x is None or not np.isfinite(x):
        return "n.d."
    s = f"{x:+,.{d}f}" if signe else f"{x:,.{d}f}"
    return s.replace(",", " ").replace(".", ",")


def _couleur(v: float) -> str:
    return COULEURS[FG.libelle(v)]


def _x(t) -> str:
    return html.escape(str(t), quote=True)


def _svg_jauge(v: float) -> str:
    """Demi-cercle des cinq zones, aiguille sur la valeur du jour."""
    cx, cy, r, e = 200, 190, 160, 30
    p = [f'<svg viewBox="0 0 400 225" class="jauge" role="img" aria-label="Jauge : {v:.0f} sur 100">']
    for (lo, hi), c in zip(BORNES, COULEURS.values()):
        a0, a1 = np.pi * (1 - lo / 100), np.pi * (1 - hi / 100)
        x0, y0 = cx + r * np.cos(a0), cy - r * np.sin(a0)
        x1, y1 = cx + r * np.cos(a1), cy - r * np.sin(a1)
        p.append(f'<path d="M{x0:.1f},{y0:.1f} A{r},{r} 0 0 1 {x1:.1f},{y1:.1f}" stroke="{c}" '
                 f'stroke-width="{e}" fill="none"/>')
    for t in (0, 25, 44, 55, 75, 100):
        a = np.pi * (1 - t / 100)
        p.append(f'<text x="{cx + (r + 28) * np.cos(a):.1f}" y="{cy - (r + 28) * np.sin(a) + 5:.1f}" '
                 f'text-anchor="middle" class="graduation">{t}</text>')
    a = np.pi * (1 - v / 100)
    nx, ny = cx + (r - 44) * np.cos(a), cy - (r - 44) * np.sin(a)
    p.append(f'<line x1="{cx}" y1="{cy}" x2="{nx:.1f}" y2="{ny:.1f}" class="aiguille" stroke-width="6" '
             f'stroke-linecap="round"/><circle cx="{cx}" cy="{cy}" r="11" class="pivot"/></svg>')
    return "".join(p)


def _svg_historique(s: pd.Series, ix: pd.Series) -> str:
    """Toute l'histoire de l'indice, zones en bandes, BRVM Composite en fond sur sa propre échelle."""
    ix = ix.reindex(s.index)
    L, H, g, d, h, b = 1100, 380, 40, 12, 12, 30
    w, hh = L - g - d, H - h - b
    x = lambda i: g + w * i / max(len(s) - 1, 1)  # noqa: E731
    y = lambda v: h + hh * (1 - v / 100)  # noqa: E731
    p = [f'<svg viewBox="0 0 {L} {H}" class="graphe" role="img" aria-label="Historique complet de l’indice">']
    for (lo, hi), c in zip(BORNES, COULEURS.values()):
        p.append(f'<rect x="{g}" y="{y(hi):.1f}" width="{w}" height="{y(lo) - y(hi):.1f}" fill="{c}" opacity=".13"/>')
    for v in (0, 25, 44, 55, 75, 100):
        p.append(f'<text x="{g - 6}" y="{y(v) + 4:.1f}" text-anchor="end" class="ax">{v}</text>')
    lo_i, hi_i = float(np.nanmin(ix)), float(np.nanmax(ix))
    pts = [f"{x(i):.1f},{h + hh * (1 - (v - lo_i) / (hi_i - lo_i)):.1f}" for i, v in enumerate(ix) if np.isfinite(v)]
    p.append(f'<polygon points="{x(0):.1f},{h + hh} {" ".join(pts)} {x(len(s) - 1):.1f},{h + hh}" class="aire-ix"/>')
    pts = " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(s))
    p.append(f'<polyline points="{pts}" fill="none" class="trait-score" stroke-width="1.4" stroke-linejoin="round"/>')
    annees = sorted(set(s.index.year))[1:]
    pas = 1 if len(annees) <= 8 else 2
    for annee in annees:
        i = int(np.searchsorted(s.index, pd.Timestamp(f"{annee}-01-01")))
        p.append(f'<line x1="{x(i):.1f}" x2="{x(i):.1f}" y1="{h}" y2="{h + hh}" class="repere"/>')
        if annee % pas == 0:
            p.append(f'<text x="{x(i):.1f}" y="{H - 8}" text-anchor="middle" class="ax">{annee}</text>')
    p.append("</svg>")
    return "".join(p)


def _barres(dernier: pd.Series) -> str:
    """Piliers et composantes du jour : une barre de 0 à 100 chacune, couleur de sa zone."""
    out = []
    for k, (nom, comp) in FG.PILIERS.items():
        v = dernier.get(k, np.nan)
        lignes = "".join(
            f'<div class="barre-ligne comp"><span>{_x(FG.NOMS[c])}</span>'
            f'<span class="piste"><i style="width:{dernier[c]:.1f}%;background:{_couleur(dernier[c])}"></i></span>'
            f'<b>{dernier[c]:.0f}</b></div>' for c in comp if np.isfinite(dernier[c]))
        tete = (f'<div class="barre-ligne pilier"><span>{_x(nom)}</span>'
                f'<span class="piste"><i style="width:{v:.1f}%;background:{_couleur(v)}"></i></span>'
                f'<b>{v:.0f}</b></div>') if np.isfinite(v) else ""
        out.append(f'<div class="groupe">{tete}{lignes}</div>')
    return "".join(out)


def _petits_multiples(res: pd.DataFrame) -> str:
    """Chaque composante sur un an, avec ses zones."""
    r = res.iloc[-252:]
    L, H = 300, 90
    out = []
    for k, nom in FG.NOMS.items():
        s = r[k]
        if s.dropna().empty:
            continue
        bandes = "".join(f'<rect x="0" y="{H * (1 - hi / 100):.1f}" width="{L}" height="{H * (hi - lo) / 100:.1f}" '
                         f'fill="{c}" opacity=".14"/>' for (lo, hi), c in zip(BORNES, COULEURS.values()))
        pts = " ".join(f"{L * i / (len(s) - 1):.1f},{H * (1 - v / 100):.1f}" for i, v in enumerate(s) if np.isfinite(v))
        der = float(s.dropna().iloc[-1])
        out.append(f'<figure class="multiple"><figcaption><span>{_x(nom)}</span><b style="color:{_couleur(der)}">'
                   f'{der:.0f}</b></figcaption><svg viewBox="0 0 {L} {H}" preserveAspectRatio="none" aria-hidden="true">'
                   f'{bandes}<polyline points="{pts}" fill="none" class="trait-score" stroke-width="1.6" '
                   f'vector-effect="non-scaling-stroke"/></svg></figure>')
    return "".join(out)


def _repartition(res: pd.DataFrame) -> str:
    """Part du temps passé dans chaque zone depuis le début de l'historique."""
    zones = res["score"].map(FG.libelle)
    parts = zones.value_counts(normalize=True).reindex(COULEURS.keys()).fillna(0) * 100
    barre = "".join(f'<i style="width:{v:.2f}%;background:{COULEURS[z]}" title="{_x(z)} : {_fr(v, 1)} %"></i>'
                    for z, v in parts.items())
    legende = "".join(f'<li><span class="pastille" style="background:{COULEURS[z]}"></span>{_x(z)}'
                      f'<b>{_fr(v, 1)} %</b></li>' for z, v in parts.items())
    return f'<div class="empile">{barre}</div><ul class="legende">{legende}</ul>'


def _svg_par_zone(valeurs: dict, titre: str, unite: str = "%") -> str:
    """Barres verticales par zone, valeurs positives ou négatives."""
    L, H, g, h, b = 420, 230, 44, 26, 34
    w, hh = L - g - 10, H - h - b
    vals = [v for v in valeurs.values() if np.isfinite(v)]
    lo, hi = min(0.0, min(vals)), max(0.0, max(vals))
    pad = (hi - lo) * .12 or 1
    lo, hi = lo - (pad if lo < 0 else 0), hi + pad
    y = lambda v: h + hh * (1 - (v - lo) / (hi - lo))  # noqa: E731
    p = [f'<svg viewBox="0 0 {L} {H}" class="graphe" role="img" aria-label="{_x(titre)}">',
         f'<line x1="{g}" x2="{L - 10}" y1="{y(0):.1f}" y2="{y(0):.1f}" class="zero"/>']
    n = len(valeurs)
    pas = w / n
    for i, (z, v) in enumerate(valeurs.items()):
        if not np.isfinite(v):
            continue
        x0 = g + i * pas + pas * .18
        y0, y1 = sorted((y(0), y(v)))
        p.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{pas * .64:.1f}" height="{max(y1 - y0, 1):.1f}" '
                 f'rx="3" fill="{COULEURS[z]}"/>')
        ty = y(v) - 6 if v >= 0 else y(v) + 15
        p.append(f'<text x="{x0 + pas * .32:.1f}" y="{ty:.1f}" text-anchor="middle" class="val">{_fr(v, 1, True)} {unite}</text>')
        p.append(f'<text x="{x0 + pas * .32:.1f}" y="{H - 10}" text-anchor="middle" class="ax">{SIGLES[z]}</text>')
    p.append("</svg>")
    return "".join(p)


def _apres_zone(res: pd.DataFrame, rt: pd.Series, horizon: int = 60) -> dict:
    """Rendement moyen de l'indice dividendes réinvestis sur les `horizon` séances suivantes, par zone."""
    r = rt.reindex(res.index).ffill()
    futur = (r.shift(-horizon) / r - 1) * 100
    z = res["score"].map(FG.libelle)
    return {k: float(futur[z == k].mean()) for k in COULEURS}


def _ecart_plus_haut(res: pd.DataFrame) -> dict:
    ix = res["brvmc"]
    ecart = (ix / ix.rolling(250, min_periods=60).max() - 1) * 100
    z = res["score"].map(FG.libelle)
    return {k: float(ecart[z == k].mean()) for k in COULEURS}


def _calendrier(res: pd.DataFrame, annees: int = 8) -> str:
    """Score moyen de chaque mois, sur les dernières années."""
    m = res["score"].groupby([res.index.year, res.index.month]).mean()
    ans = sorted({a for a, _ in m.index})[-annees:]
    mois = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
    tete = "<tr><th></th>" + "".join(f"<th>{x}</th>" for x in mois) + "</tr>"
    corps = ""
    for a in reversed(ans):
        corps += f"<tr><th>{a}</th>"
        for k in range(1, 13):
            v = m.get((a, k), np.nan)
            corps += (f'<td style="background:{_couleur(v)}" title="{k:02d}/{a} : {v:.0f}">{v:.0f}</td>'
                      if np.isfinite(v) else "<td></td>")
        corps += "</tr>"
    return f'<div class="defile"><table class="calendrier"><thead>{tete}</thead><tbody>{corps}</tbody></table></div>'


FIGURES = [
    ("f1_marche.png", "Le marché BRVM de 2008 à 2026",
     "Un marché concentré et longtemps peu liquide : Sonatel pesait 55 % de la capitalisation en 2008 et en pèse "
     "encore 21 % ; de 2008 à 2012, 77 % des couples titre-séance étaient sans échange ou à cours figé, contre 17 % "
     "depuis 2022."),
    ("f2_dividendes_par_mois.png", "Les dividendes détachés selon le mois, 2016-2026",
     "84 % des dividendes sont détachés de mai à juillet, dont 47 % en mai : d'où le calcul de la tendance sur un "
     "BRVM Composite dividendes réinvestis."),
    ("f8_h1_validite.png", "État du marché selon la zone de l'indice",
     "En peur extrême, l'indice est en moyenne à 13,4 % de son plus haut d'un an, contre 3,8 % en cupidité extrême. "
     "La volatilité, elle, change peu d'une zone à l'autre."),
    ("f9_h2_rendements_futurs.png", "Rendement moyen de l'indice après chaque zone, selon l'horizon",
     "Les rendements qui suivent croissent avec le score : sur 60 séances, +5,6 % après la cupidité extrême, "
     "+1,2 % en zone neutre, -0,7 % après la peur extrême."),
    ("f10_h3_divergences.png", "Momentum de l'indice et participation des titres, 2019-2026",
     "Le momentum de l'indice n'explique que 28 % du rendement du titre médian ; avec la participation et la force, "
     "47 %."),
    ("f12_score_v3.png", "La version révisée de l'indice, comparée à la version initiale",
     "Dividendes réinvestis, trois piliers, fenêtre de trois ans et lissage sur 10 séances : 2,5 fois moins de "
     "changements de zone et plus d'information sur les rendements futurs, au prix d'un léger retard."),
]


def _figures() -> str:
    return "".join(f'<figure class="carte figure"><img src="etude/{f}" alt="{_x(t)}">'
                   f'<figcaption><b>{_x(t)}.</b> {_x(c)}</figcaption></figure>' for f, t, c in FIGURES)


def page(res: pd.DataFrame, infos: dict, rt: pd.Series) -> str:
    dernier = res.iloc[-1]
    v = float(dernier["score"])
    zone = FG.libelle(v)
    date = res.index[-1]

    def il_y_a(n):
        return float(res["score"].iloc[-1 - n]) if len(res) > n else float("nan")

    rappels = "".join(
        f'<li><span>{lbl}</span><b style="color:{_couleur(il_y_a(n))}">{il_y_a(n):.0f}</b>'
        f'<small>{_x(FG.libelle(il_y_a(n)))}</small></li>'
        for lbl, n in (("Veille", 1), ("Il y a une semaine", 5), ("Il y a un mois", 21), ("Il y a un an", 252))
        if np.isfinite(il_y_a(n)))
    apres = _apres_zone(res, rt)
    ecart = _ecart_plus_haut(res)
    remplacements = {
        "DATE": f"{date:%d/%m/%Y}",
        "PROVISOIRE": "" if infos.get("derniere_seance_close", True) else " (séance provisoire)",
        "VALEUR": f"{v:.0f}",
        "ZONE": _x(zone),
        "COULEUR": COULEURS[zone],
        "JAUGE": _svg_jauge(v),
        "RAPPELS": rappels,
        "BARRES": _barres(dernier),
        "MULTIPLES": _petits_multiples(res),
        "HISTORIQUE": _svg_historique(res["score"], res["brvmc"]),
        "DEBUT": f"{res.index[0]:%Y}",
        "NB_SEANCES": _fr(len(res)),
        "REPARTITION": _repartition(res),
        "APRES_ZONE": _svg_par_zone(apres, "Rendement à 60 séances après chaque zone"),
        "ECART": _svg_par_zone(ecart, "Écart moyen au plus haut d'un an selon la zone"),
        "CALENDRIER": _calendrier(res),
        "FIGURES": _figures(),
        "PDF": PDF,
    }
    texte = (ICI / "modele.html").read_text(encoding="utf-8")
    for k, val in remplacements.items():
        texte = texte.replace("{{" + k + "}}", val)
    return texte

def main(argv=None) -> None:
    a = argparse.ArgumentParser()
    a.add_argument("--sortie", default="site")
    args = a.parse_args(argv)
    sortie = Path(args.sortie)
    sortie.mkdir(parents=True, exist_ok=True)
    cours, valeurs, ix, rt, infos = donnees()
    res = calculer(cours, valeurs, ix, rt)
    d = res.iloc[-1]
    (sortie / "index.html").write_text(page(res, infos, rt), encoding="utf-8")
    (sortie / "etude").mkdir(exist_ok=True)
    for f, _, _ in FIGURES:
        shutil.copy(SORTIE_ETUDE / f, sortie / "etude" / f)
    res.round(2).to_csv(sortie / "fear_greed.csv", index_label="date", date_format="%Y-%m-%d")
    (sortie / "fear_greed.json").write_text(json.dumps({
        "date": f"{res.index[-1]:%Y-%m-%d}", "seance_close": infos.get("derniere_seance_close"),
        "score": round(float(d["score"]), 2), "zone": FG.libelle(d["score"]), "version": "revisee",
        "piliers": {k: (round(float(d[k]), 2) if np.isfinite(d[k]) else None) for k in FG.PILIERS},
        "composantes": {k: (round(float(d[k]), 2) if np.isfinite(d[k]) else None) for k in FG.NOMS},
        "historique": [[f"{t:%Y-%m-%d}", round(float(v), 2)] for t, v in res["score"].items()],
    }, ensure_ascii=False), encoding="utf-8")
    print(f"{res.index[-1]:%d/%m/%Y} : {d['score']:.1f} ({FG.libelle(d['score'])}), {len(res)} séances")


if __name__ == "__main__":
    main()
