# Fear & Greed BRVM : étude et article

Article « Peur et cupidité sur un marché frontière peu liquide : construction et validation d'un indice de sentiment pour la Bourse Régionale des Valeurs Mobilières », destiné au Prix de la Recherche du 30e anniversaire de la BRVM.

## Reproduire

Toutes les commandes se lancent à la racine du dépôt, avec l'environnement `recherche/.venv` (voir [`../README.md`](../README.md)).

> **Changement de source (01/11/2026).** `recherche/sources.json` désigne désormais Scraper-BRVM (données au 29/10/2026) au lieu de brvm-app (données au 07/10/2026). `sortie/`, `Fear_Greed_BRVM.docx` et `Fear_Greed_BRVM.pdf` datent encore de l'ancienne source. Un recalcul d'essai déplace 56 des 471 chiffres de plus de 5 %, dont l'étude de cas d'octobre 2026 (score v2 : 24,8 puis 19,6 ; v3 : 40,6 puis 27,6), les tests H2 à 120 séances et l'écart saisonnier H4.

1. **Calculs, tableaux et figures.** Les données sont lues au commit figé de `recherche/sources.json`, sans aucun code de l'application.

   ```bash
   recherche/.venv/Scripts/python.exe recherche/fear_greed/etude.py
   ```

   Le script écrit dans `sortie/` :
   - les tableaux (CSV) ;
   - les figures (PNG) ;
   - `chiffres.json`, d'où viennent tous les nombres du texte.

Le texte de l'article n'est pas dans ce dépôt : seuls les calculs, tableaux et figures sont reproductibles. L'article final est fourni tel quel en Word et en PDF (`Fear_Greed_BRVM.docx`, `Fear_Greed_BRVM.pdf`), avec la déclaration sur l'usage de l'IA (`Declaration_IA.docx`).

## Fichiers

| Fichier | Rôle |
|---|---|
| `indice.py` | Indice Fear & Greed, version initiale et version révisée (piliers, lissage, dividendes réinvestis) |
| `donnees.py` | Cours, valeurs échangées, BRVM Composite dividendes réinvestis, marché reconstitué, séances illiquides |
| `etude.py` | Diagnostics, hypothèses H1 à H5, robustesse, version révisée |
| `figures.py` | Figures de l'article |
| `Fear_Greed_BRVM.docx`, `Fear_Greed_BRVM.pdf` | Article final |
| `Declaration_IA.docx` | Déclaration sur l'usage de l'IA |
