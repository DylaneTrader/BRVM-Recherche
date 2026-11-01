"""Mise en forme Word des articles de recherche : styles, paragraphes avec renvois et chiffres, équations
Word natives, figures, tableaux, table des matières (environnement recherche/.venv).

Chaque article appelle d'abord ``configurer(dossier)`` : dossier ``sortie/`` de son étude, qui contient
chiffres.json, les tableaux (CSV) et les figures (PNG)."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from latex2mathml.converter import convert
from lxml import etree

SORTIE = Path("sortie")
XSL = Path(r"C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL")
POLICE = "Cambria"
ENCRE = RGBColor(0x1F, 0x29, 0x33)
BLEU = RGBColor(0x1F, 0x4E, 0x79)
FOND_EN_TETE, BORDURE = "DCE6F2", "9FB3C8"     # en-tête et filets des tableaux
NBSP, FINE = "\u00a0", "\u202f"

CHIFFRES: dict = {}
_XSLT = etree.XSLT(etree.parse(str(XSL)))


def configurer(sortie: Path) -> None:
    """Dossier des résultats de l'étude : chiffres.json, tableaux et figures."""
    global SORTIE
    SORTIE = Path(sortie)
    CHIFFRES.clear()
    CHIFFRES.update(json.loads((SORTIE / "chiffres.json").read_text(encoding="utf-8")))


# ---------------------------------------------------------------------------
# Nombres à la française
# ---------------------------------------------------------------------------

def fr(x: float, dec: int = 1, signe: bool = False) -> str:
    s = f"{x:+,.{dec}f}" if signe else f"{x:,.{dec}f}"
    return s.replace(",", FINE).replace(".", ",").replace("-", "\u2212")


def valeur(cle: str):
    if cle not in CHIFFRES:
        raise KeyError(f"chiffre absent de chiffres.json : {cle}")
    return CHIFFRES[cle]


def chiffre(spec: str) -> str:
    """{n:cle:dec} nombre, {p:cle:dec} pourcentage, {ps:cle:dec} pourcentage signé, {ns:cle:dec} nombre
    signé, {pt:cle:dec} points de pourcentage, {s:cle} texte, {i:cle} entier."""
    parts = spec.split(":")
    genre, cle = parts[0], parts[1]
    dec = int(parts[2]) if len(parts) > 2 else 1
    v = valeur(cle)
    if genre == "s":
        return str(v)
    if genre == "i":
        return fr(float(v), 0)
    v = float(v)
    if genre == "n":
        return fr(v, dec)
    if genre == "ns":
        return fr(v, dec, True)
    if genre == "p":
        return fr(v * 100, dec) + NBSP + "%"
    if genre == "ps":
        return fr(v * 100, dec, True) + NBSP + "%"
    if genre == "pt":
        return fr(v * 100, dec)
    raise ValueError(spec)


# ---------------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------------

class Article:
    def __init__(self) -> None:
        self.doc = Document()
        self.renvois: dict[str, str] = {}
        self.compteurs = {"fig": 0, "tab": 0, "eq": 0}
        self._styles()

    # -- styles --
    def _styles(self) -> None:
        d = self.doc
        sec = d.sections[0]
        sec.page_height, sec.page_width = Cm(29.7), Cm(21.0)
        sec.left_margin = sec.right_margin = Cm(2.5)
        sec.top_margin, sec.bottom_margin = Cm(2.5), Cm(2.3)
        st = d.styles["Normal"]
        st.font.name = POLICE
        st.font.size = Pt(11)
        st.element.rPr.rFonts.set(qn("w:eastAsia"), POLICE)
        pf = st.paragraph_format
        pf.space_after = Pt(6)
        pf.line_spacing = 1.25
        for nom, taille, avant, apres in (("Heading 1", 14, 18, 8), ("Heading 2", 12, 12, 6), ("Heading 3", 11, 10, 4)):
            h = d.styles[nom]
            h.font.name = POLICE
            h.font.size = Pt(taille)
            h.font.bold = True
            h.font.italic = False
            h.font.color.rgb = BLEU if nom == "Heading 1" else ENCRE
            rpr = h.element.get_or_add_rPr()
            rf = rpr.find(qn("w:rFonts"))
            if rf is None:
                rf = OxmlElement("w:rFonts")
                rpr.append(rf)
            for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
                rf.set(qn(a), POLICE)
            for a in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
                if rf.get(qn(a)) is not None:
                    del rf.attrib[qn(a)]
            h.paragraph_format.space_before = Pt(avant)
            h.paragraph_format.space_after = Pt(apres)
            h.paragraph_format.keep_with_next = True
        cap = d.styles["Caption"]
        cap.font.name = POLICE
        cap.font.size = Pt(9.5)
        cap.font.bold = False
        cap.font.italic = False
        cap.font.color.rgb = ENCRE
        cap.paragraph_format.space_after = Pt(4)
        self._pied()

    def _pied(self) -> None:
        sec = self.doc.sections[0]
        p = sec.footer.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        self._champ(p, "PAGE", taille=9)

    def _champ(self, p, code: str, taille: float = 11) -> None:
        r = p.add_run()
        r.font.size = Pt(taille)
        for t, txt in (("begin", None), (None, code), ("separate", None), (None, "1"), ("end", None)):
            if t:
                e = OxmlElement("w:fldChar")
                e.set(qn("w:fldCharType"), t)
                r._r.append(e)
            elif txt == code:
                e = OxmlElement("w:instrText")
                e.set(qn("xml:space"), "preserve")
                e.text = f" {code} "
                r._r.append(e)
            else:
                e = OxmlElement("w:t")
                e.text = txt
                r._r.append(e)

    # -- renvois --
    def numeroter(self, blocs: list) -> None:
        """Premier passage : numéros des figures, tableaux et équations dans l'ordre d'apparition."""
        for b in blocs:
            if b[0] in ("fig", "tab", "eq") and b[1]:
                self.compteurs[b[0]] += 1
                self.renvois[f"{b[0]}:{b[1]}"] = str(self.compteurs[b[0]])
        self.compteurs = {"fig": 0, "tab": 0, "eq": 0}

    def resoudre(self, texte: str) -> str:
        def rep(m):
            spec = m.group(1)
            if spec.split(":")[0] in ("fig", "tab", "eq"):
                if spec not in self.renvois:
                    raise KeyError(f"renvoi inconnu : {spec}")
                return self.renvois[spec]
            return chiffre(spec)
        texte = re.sub(r"\{([a-z]+:[^{}]+)\}", rep, texte).replace("'", "\u2019")
        if "\u2014" in texte:
            raise ValueError(f"tiret cadratin interdit : {texte[:80]}")
        return texte

    # -- texte enrichi : **gras**, *italique*, ^exposant^ --
    def _runs(self, p, texte: str, taille: float | None = None, couleur=None) -> None:
        for morceau in re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*|\^[^^]+\^)", texte):
            if not morceau:
                continue
            if morceau.startswith("**"):
                r = p.add_run(morceau[2:-2])
                r.bold = True
            elif morceau.startswith("*"):
                r = p.add_run(morceau[1:-1])
                r.italic = True
            elif morceau.startswith("^"):
                r = p.add_run(morceau[1:-1])
                r.font.superscript = True
            else:
                r = p.add_run(morceau)
            if taille:
                r.font.size = Pt(taille)
            if couleur is not None:
                r.font.color.rgb = couleur

    def para(self, texte: str, style: str | None = None, align=WD_ALIGN_PARAGRAPH.JUSTIFY, taille=None,
             retrait: float | None = None, avant: float | None = None, apres: float | None = None, couleur=None):
        p = self.doc.add_paragraph(style=style)
        p.alignment = align
        self._runs(p, self.resoudre(texte), taille, couleur)
        if retrait is not None:
            p.paragraph_format.left_indent = Cm(retrait)
        if avant is not None:
            p.paragraph_format.space_before = Pt(avant)
        if apres is not None:
            p.paragraph_format.space_after = Pt(apres)
        return p

    def puces(self, items: list[str], numerotees: bool = False) -> None:
        for i, t in enumerate(items, 1):
            p = self.doc.add_paragraph(style="List Number" if numerotees else "List Bullet")
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_after = Pt(3)
            self._runs(p, self.resoudre(t))

    def titre(self, texte: str, niveau: int = 1) -> None:
        self.doc.add_heading(self.resoudre(texte), level=niveau)

    def saut(self) -> None:
        self.doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    # -- équations --
    def _omml(self, latex: str):
        return etree.fromstring(etree.tostring(_XSLT(etree.fromstring(convert(latex).encode())).getroot()))

    def equation(self, label: str | None, latex: str) -> None:
        """Équation centrée, numérotée à droite (tableau sans bordure à deux colonnes)."""
        t = self.doc.add_table(rows=1, cols=2)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        largeurs = (Cm(14.5), Cm(1.5))
        for c, w in zip(t.rows[0].cells, largeurs):
            c.width = w
        p = t.rows[0].cells[0].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(4)
        p._p.append(self._omml(latex))
        if label:
            self.compteurs["eq"] += 1
            q = t.rows[0].cells[1].paragraphs[0]
            q.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            q.add_run(f"({self.compteurs['eq']})")

    def legende_symboles(self, items: list[tuple[str, str]]) -> None:
        """Légende d'une formule : symbole (LaTeX) et sens."""
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.left_indent = Cm(1.0)
        p.paragraph_format.space_after = Pt(8)
        r = p.add_run("où ")
        r.font.size = Pt(10)
        for i, (sym, sens) in enumerate(items):
            p._p.append(self._omml(sym))
            r = p.add_run(" : " + self.resoudre(sens) + (" ;" if i < len(items) - 1 else "."))
            r.font.size = Pt(10)
            if i < len(items) - 1:
                r.add_break()

    def math_en_ligne(self, p, latex: str) -> None:
        p._p.append(self._omml(latex))

    # -- figures et tableaux --
    def figure(self, label: str, fichier: str, legende: str, note: str | None = None, largeur: float = 15.5) -> None:
        self.compteurs["fig"] += 1
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.keep_with_next = True
        p.add_run().add_picture(str(SORTIE / fichier), width=Cm(largeur))
        c = self.doc.add_paragraph(style="Caption")
        c.alignment = WD_ALIGN_PARAGRAPH.LEFT
        r = c.add_run(f"Figure {self.compteurs['fig']}. ")
        r.bold = True
        self._runs(c, self.resoudre(legende))
        if note:
            c.paragraph_format.keep_with_next = True       # la note reste sous la légende, sur la même page
            n = self.para(note, taille=9, align=WD_ALIGN_PARAGRAPH.LEFT, apres=10)
            n.paragraph_format.space_before = Pt(0)

    def tableau(self, label: str, legende: str, df: pd.DataFrame, note: str | None = None,
                largeurs: list[float] | None = None, taille: float = 9, gras_premiere: bool = True) -> None:
        self.compteurs["tab"] += 1
        c = self.doc.add_paragraph(style="Caption")
        c.paragraph_format.keep_with_next = True
        r = c.add_run(f"Tableau {self.compteurs['tab']}. ")
        r.bold = True
        self._runs(c, self.resoudre(legende))
        n_l, n_c = df.shape[0] + 1, df.shape[1]
        t = self.doc.add_table(rows=n_l, cols=n_c)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        t.autofit = False
        largeurs = largeurs or [16.0 / n_c] * n_c
        for j, col in enumerate(df.columns):
            self._cellule(t.cell(0, j), str(col), taille, gras=True, centre=j > 0, fond=FOND_EN_TETE)
        for i, (_, ligne) in enumerate(df.iterrows(), 1):
            for j, v in enumerate(ligne):
                txt = "" if v is None else str(v)
                self._cellule(t.cell(i, j), txt, taille, centre=j > 0 and (txt == "n.d." or txt[:1] in
                              "+-\u22120123456789(r" and not txt.startswith("rang")))
        for i, row in enumerate(t.rows):
            row.cells[0]._tc.get_or_add_tcPr()
            # tableau d'un seul tenant, et sa note avec lui : chaque ligne reste avec la suivante (la
            # dernière avec la note, s'il y en a une)
            garder = bool(note) or i < n_l - 1
            for j, cell in enumerate(row.cells):
                cell.width = Cm(largeurs[j])
                for p in cell.paragraphs:
                    p.paragraph_format.keep_with_next = garder
            trpr = row._tr.get_or_add_trPr()
            cant = OxmlElement("w:cantSplit")
            trpr.append(cant)
        self._bordures(t)
        lay = OxmlElement("w:tblLayout")
        lay.set(qn("w:type"), "fixed")
        t._tbl.tblPr.append(lay)
        if note:
            self.para(note, taille=8.5, align=WD_ALIGN_PARAGRAPH.LEFT, avant=3, apres=10)
        else:
            self.doc.add_paragraph().paragraph_format.space_after = Pt(4)

    def _cellule(self, cell, texte: str, taille: float, gras: bool = False, centre: bool = False, fond: str | None = None):
        cell.text = ""
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER if centre else WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.line_spacing = 1.0
        self._runs(p, self.resoudre(texte) or NBSP, taille)      # une cellule vide garde la taille du tableau
        if gras:
            for r in p.runs:
                r.bold = True
        if fond:
            tcpr = cell._tc.get_or_add_tcPr()
            shd = OxmlElement("w:shd")
            shd.set(qn("w:val"), "clear")
            shd.set(qn("w:color"), "auto")
            shd.set(qn("w:fill"), fond)
            tcpr.append(shd)

    def _bordures(self, t) -> None:
        tblpr = t._tbl.tblPr
        b = OxmlElement("w:tblBorders")
        for cote, val in (("top", "single"), ("bottom", "single"), ("insideH", "single"), ("left", "nil"),
                          ("right", "nil"), ("insideV", "nil")):
            e = OxmlElement(f"w:{cote}")
            e.set(qn("w:val"), val)
            if val == "single":
                e.set(qn("w:sz"), "4")
                e.set(qn("w:color"), BORDURE)
            b.append(e)
        tblpr.append(b)

    def table_des_matieres(self) -> None:
        p = self.doc.add_paragraph()
        r = p.add_run()
        for t, txt in (("begin", None), (None, 'TOC \\o "1-2" \\h \\z \\u'), ("separate", None),
                       (None, "Table des matières : à mettre à jour (clic droit, Mettre à jour les champs)."),
                       ("end", None)):
            if t:
                e = OxmlElement("w:fldChar")
                e.set(qn("w:fldCharType"), t)
                r._r.append(e)
            elif txt.startswith("TOC"):
                e = OxmlElement("w:instrText")
                e.set(qn("xml:space"), "preserve")
                e.text = txt
                r._r.append(e)
            else:
                e = OxmlElement("w:t")
                e.text = txt
                r._r.append(e)

    def sauver(self, chemin: Path) -> None:
        self.doc.core_properties.title = "Indice Fear & Greed BRVM"
        self.doc.core_properties.language = "fr-FR"
        self.doc.save(str(chemin))


def lire(nom: str) -> pd.DataFrame:
    return pd.read_csv(SORTIE / f"{nom}.csv", sep=";", decimal=",", encoding="utf-8-sig", index_col=0)


__all__ = ["Article", "configurer", "fr", "chiffre", "valeur", "lire", "CHIFFRES", "SORTIE", "WD_ALIGN_PARAGRAPH", "Cm", "Pt",
           "RGBColor", "BLEU", "ENCRE", "WD_SECTION"]
