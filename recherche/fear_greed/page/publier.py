"""Page publique de l'indice Fear & Greed BRVM (version révisée, la même que BRVM app).

Calcule l'indice avec `indice.py` sur les données publiques de brvm-py (cours ajustés des divisions,
valeurs échangées en FCFA, BRVM Composite, dividendes retenus, nombre de titres), puis écrit un site
statique :

    site/index.html             page lisible, sans script ni dépendance extérieure
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
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import indice as FG  # noqa: E402

COULEURS = {"Peur extrême": "#8b1e1e", "Peur": "#d9822b", "Neutre": "#8a8f98",
            "Cupidité": "#4f8a3a", "Cupidité extrême": "#1f5f2a"}
BORNES = [(0, 25), (25, 44), (44, 55), (55, 75), (75, 100)]


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


def _svg_historique(s: pd.Series, ix: pd.Series) -> str:
    """Score sur deux ans, zones en bandes, BRVM Composite en fond (échelle propre)."""
    s = s.iloc[-504:]
    ix = ix.reindex(s.index)
    L, H, g, d, h, b = 760, 300, 44, 14, 14, 30
    w, hh = L - g - d, H - h - b
    x = lambda i: g + w * i / max(len(s) - 1, 1)  # noqa: E731
    y = lambda v: h + hh * (1 - v / 100)  # noqa: E731
    parts = [f'<svg viewBox="0 0 {L} {H}" role="img" aria-label="Historique de l\'indice sur deux ans">']
    for (lo, hi), (zone, c) in zip(BORNES, COULEURS.items()):
        parts.append(f'<rect x="{g}" y="{y(hi):.1f}" width="{w}" height="{y(lo) - y(hi):.1f}" fill="{c}" opacity="0.09"/>')
    for v in (0, 25, 44, 55, 75, 100):
        parts.append(f'<text x="{g - 6}" y="{y(v) + 4:.1f}" text-anchor="end" class="ax">{v}</text>')
    lo_i, hi_i = ix.min(), ix.max()
    if np.isfinite(lo_i) and hi_i > lo_i:
        pts = " ".join(f"{x(i):.1f},{h + hh * (1 - (v - lo_i) / (hi_i - lo_i)):.1f}" for i, v in enumerate(ix) if np.isfinite(v))
        parts.append(f'<polyline points="{pts}" fill="none" stroke="#8a8f98" stroke-width="1" opacity="0.6"/>')
    pts = " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(s))
    parts.append(f'<polyline points="{pts}" fill="none" stroke="#1f4e79" stroke-width="1.8"/>')
    for annee in sorted(set(s.index.year))[1:]:
        i = int(np.searchsorted(s.index, pd.Timestamp(f"{annee}-01-01")))
        parts.append(f'<line x1="{x(i):.1f}" x2="{x(i):.1f}" y1="{h}" y2="{h + hh}" stroke="#ccc" stroke-dasharray="3,3"/>')
        parts.append(f'<text x="{x(i):.1f}" y="{H - 10}" text-anchor="middle" class="ax">{annee}</text>')
    parts.append("</svg>")
    return "".join(parts)


def _svg_jauge(v: float) -> str:
    cx, cy, r = 160, 150, 120
    arc = []
    for (lo, hi), c in zip(BORNES, COULEURS.values()):
        a0, a1 = np.pi * (1 - lo / 100), np.pi * (1 - hi / 100)
        x0, y0 = cx + r * np.cos(a0), cy - r * np.sin(a0)
        x1, y1 = cx + r * np.cos(a1), cy - r * np.sin(a1)
        arc.append(f'<path d="M{x0:.1f},{y0:.1f} A{r},{r} 0 0 1 {x1:.1f},{y1:.1f}" stroke="{c}" stroke-width="22" fill="none"/>')
    a = np.pi * (1 - v / 100)
    nx, ny = cx + (r - 30) * np.cos(a), cy - (r - 30) * np.sin(a)
    return (f'<svg viewBox="0 0 320 175" role="img" aria-label="Jauge : {v:.0f} sur 100">{"".join(arc)}'
            f'<line x1="{cx}" y1="{cy}" x2="{nx:.1f}" y2="{ny:.1f}" stroke="#222" stroke-width="4" stroke-linecap="round"/>'
            f'<circle cx="{cx}" cy="{cy}" r="7" fill="#222"/></svg>')


def page(res: pd.DataFrame, infos: dict) -> str:
    dernier = res.iloc[-1]
    v = float(dernier["score"])
    zone = FG.libelle(v)
    date = res.index[-1]

    def il_y_a(n):
        return float(res["score"].iloc[-1 - n]) if len(res) > n else float("nan")

    lignes = ""
    for p, (nom, comp) in FG.PILIERS.items():
        if np.isfinite(dernier[p]):
            lignes += (f'<tr class="pilier"><td>{html.escape(nom)}</td><td>{dernier[p]:.0f}</td>'
                       f'<td>{html.escape(FG.libelle(dernier[p]))}</td></tr>')
        lignes += "".join(
            f'<tr><td class="comp">{html.escape(FG.NOMS[k])}</td><td>{dernier[k]:.0f}</td>'
            f'<td>{html.escape(FG.libelle(dernier[k]))}</td></tr>'
            for k in comp if np.isfinite(dernier[k]))
    rappels = "".join(f"<li>{lbl} : <b>{il_y_a(n):.0f}</b> ({FG.libelle(il_y_a(n))})</li>"
                      for lbl, n in (("Séance précédente", 1), ("Il y a une semaine", 5), ("Il y a un mois", 21), ("Il y a un an", 252))
                      if np.isfinite(il_y_a(n)))
    provisoire = "" if infos.get("derniere_seance_close", True) else " (séance provisoire)"
    return f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Fear &amp; Greed BRVM</title>
<meta name="description" content="Indice de sentiment du marché de la BRVM, de 0 (peur extrême) à 100 (cupidité extrême), mis à jour chaque séance.">
<style>
:root{{--fond:#fff;--texte:#1d1d1f;--doux:#5f6368;--trait:#e3e3e3}}
@media (prefers-color-scheme:dark){{:root{{--fond:#121417;--texte:#e8e8e8;--doux:#a0a4aa;--trait:#2c3036}}}}
body{{margin:0;background:var(--fond);color:var(--texte);font-family:"Times New Roman",Times,serif;line-height:1.5}}
main{{max-width:820px;margin:0 auto;padding:24px 16px 48px}}
h1{{font-size:1.9rem;margin:0 0 4px}} .sous{{color:var(--doux);margin:0 0 24px}}
.haut{{display:flex;flex-wrap:wrap;gap:24px;align-items:center}} .haut svg{{width:300px;max-width:100%}}
.valeur{{font-size:3.4rem;font-weight:bold;line-height:1}} .zone{{font-size:1.4rem;color:{COULEURS[zone]}}}
ul{{padding-left:18px}} tr.pilier td{{font-weight:bold}} td.comp{{padding-left:24px}} table{{border-collapse:collapse;width:100%;margin:8px 0 24px}}
td,th{{border-bottom:1px solid var(--trait);padding:6px 8px;text-align:left}} td:nth-child(2){{text-align:right}}
svg .ax{{font-size:11px;fill:var(--doux)}} .hist svg{{width:100%;height:auto}}
footer,.note{{color:var(--doux);font-size:.92rem}} a{{color:#3d7cc9}}
</style></head><body><main>
<h1>Fear &amp; Greed BRVM</h1>
<p class="sous">Sentiment du marché d'actions de la BRVM au {date:%d/%m/%Y}{provisoire}, de 0 (peur extrême) à 100 (cupidité extrême).</p>
<section class="haut">{_svg_jauge(v)}<div><div class="valeur">{v:.0f}</div><div class="zone">{zone}</div><ul>{rappels}</ul></div></section>
<h2>Trois piliers, cinq composantes</h2>
<p class="note">Chaque composante est le rang de sa mesure du jour parmi les 756 dernières séances (environ trois ans), de 0 à 100, non lissé. Chaque pilier est la moyenne de ses composantes. L'indice est la moyenne des trois piliers à poids égaux, lissée sur les 10 dernières séances.</p>
<table><thead><tr><th>Composante</th><th>Rang</th><th>Lecture</th></tr></thead><tbody>{lignes}</tbody></table>
<h2>Deux ans d'historique</h2>
<div class="hist">{_svg_historique(res["score"], res["brvmc"])}</div>
<p class="note">Trait bleu : l'indice. Trait gris : le BRVM Composite, sur sa propre échelle. Bandes : les cinq zones.</p>
<h2>Méthode</h2>
<ul>
<li><b>Momentum</b> (pilier Tendance) : BRVM Composite dividendes réinvestis face à sa moyenne de 125 séances.</li>
<li><b>Participation</b> (pilier Participation) : part des titres cotés au-dessus de leur moyenne de 50 séances.</li>
<li><b>Force</b> (pilier Participation) : nouveaux plus hauts moins nouveaux plus bas sur 52 semaines, en part des titres, lissé sur 10 séances.</li>
<li><b>Demande</b> (pilier Flux et stress) : part des valeurs échangées sur 20 séances qui l'ont été en hausse.</li>
<li><b>Volatilité baissière</b> (pilier Flux et stress) : volatilité des baisses du BRVM Composite dividendes réinvestis sur 20 séances face à 120 séances, inversée.</li>
</ul>
<p class="note">Transposition à la BRVM de la méthode de CNN, sans ses composantes sur les options, les obligations à haut rendement et les valeurs refuges. Construction et validation détaillées dans l'article « Peur et cupidité sur un marché frontière peu liquide », préparé pour le Prix de la Recherche des 30 ans de la BRVM. Version affichée : version révisée de l'article (section 7), la même que la page Overview de BRVM app.</p>
<p>Données : <a href="fear_greed.json">JSON</a> · <a href="fear_greed.csv">CSV</a> · <a href="https://github.com/DylaneTrader/BRVM-Recherche">code</a></p>
<footer>Données de marché : <a href="https://github.com/DylaneTrader/brvm-py">brvm-py</a> (Sikafinance, brvm.org). Indicateur de recherche, sans garantie ; ce n'est pas un conseil en investissement. Dylane NDOUDY-BAMOUENIZO.</footer>
</main></body></html>
"""


def main(argv=None) -> None:
    a = argparse.ArgumentParser()
    a.add_argument("--sortie", default="site")
    args = a.parse_args(argv)
    sortie = Path(args.sortie)
    sortie.mkdir(parents=True, exist_ok=True)
    cours, valeurs, ix, rt, infos = donnees()
    res = calculer(cours, valeurs, ix, rt)
    d = res.iloc[-1]
    (sortie / "index.html").write_text(page(res, infos), encoding="utf-8")
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
