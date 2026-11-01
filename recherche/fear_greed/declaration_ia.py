"""Modèle de déclaration sur l'honneur relative à l'usage de l'intelligence artificielle (Prix de la Recherche
du 30e anniversaire de la BRVM). À compléter, relire et signer par l'auteur : le texte décrit l'usage réel qui a
été fait d'un assistant d'IA pour ce rapport ; l'auteur l'ajuste s'il a lui-même réécrit des parties."""
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

ICI = Path(__file__).resolve().parent

doc = Document()
s = doc.sections[0]
s.page_height, s.page_width = Cm(29.7), Cm(21.0)
s.left_margin = s.right_margin = Cm(2.5)
st = doc.styles["Normal"]
st.font.name = "Cambria"
st.font.size = Pt(11)
st.paragraph_format.space_after = Pt(6)
st.paragraph_format.line_spacing = 1.2


def p(texte="", gras=False, centre=False, taille=None):
    q = doc.add_paragraph()
    q.alignment = WD_ALIGN_PARAGRAPH.CENTER if centre else WD_ALIGN_PARAGRAPH.JUSTIFY
    r = q.add_run(texte)
    r.bold = gras
    if taille:
        r.font.size = Pt(taille)
    return q


def puce(texte):
    q = doc.add_paragraph(style="List Bullet")
    q.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    q.add_run(texte)


p("DÉCLARATION SUR L'HONNEUR", gras=True, centre=True, taille=14)
p("relative au degré d'utilisation de l'intelligence artificielle", centre=True)
p("Prix de la Recherche du 30e anniversaire de la BRVM", centre=True)
p()
p("Je soussigné(e) [Prénom NOM], [fonction, institution], auteur du rapport de recherche intitulé « Peur et "
  "cupidité sur un marché frontière peu liquide : construction et validation d'un indice de sentiment pour la "
  "Bourse Régionale des Valeurs Mobilières », déclare sur l'honneur que l'intelligence artificielle a été utilisée "
  "pour la production de ce rapport dans les conditions suivantes.")
p("1. Outil utilisé", gras=True)
p("Claude (Anthropic), assistant d'intelligence artificielle, utilisé dans un environnement de développement "
  "(Claude Code) ayant accès au code de l'étude et aux données de marché collectées par l'auteur.")
p("2. Travail réalisé par l'auteur", gras=True)
puce("Conception de la collecte des données de marché, de leur base historique et de l'indice Fear & Greed BRVM "
     "dans sa version initiale.")
puce("Rédaction du cadre méthodologique initial (problématique, architecture de l'indice, protocole empirique, "
     "hypothèses de départ).")
puce("Choix du sujet, validation de la thèse de l'article et des orientations de la recherche, relecture et "
     "validation de l'ensemble du rapport. [À compléter : parties réécrites ou corrigées par l'auteur.]")
p("3. Travail réalisé avec l'assistance de l'intelligence artificielle", gras=True)
puce("Écriture du code de l'étude empirique (calculs, tests statistiques, figures et tableaux), sous la direction "
     "de l'auteur ; tous les résultats sont reproductibles à partir de ce code et des données publiées sur GitHub.")
puce("Recherche et vérification des références bibliographiques.")
puce("Rédaction du texte du rapport à partir des résultats obtenus et du cadre méthodologique de l'auteur, puis "
     "mise en forme du document.")
p("4. Degré d'utilisation", gras=True)
p("L'intelligence artificielle a été utilisée de manière substantielle pour la programmation de l'étude, la "
  "recherche bibliographique et la rédaction. Les données, l'indice étudié, le cadre méthodologique et les choix de "
  "recherche relèvent de l'auteur, qui assume l'entière responsabilité du contenu du rapport. Aucune donnée n'a été "
  "générée par l'intelligence artificielle : tous les chiffres proviennent des données de marché et sont "
  "reproductibles.")
p()
p("Fait à [ville], le [date].")
p()
p("[Signature]")
doc.save(str(ICI / "Declaration_IA.docx"))
print(ICI / "Declaration_IA.docx")
