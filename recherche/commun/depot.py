"""Données des travaux de recherche : tirées de GitHub, à un commit figé.

Chaque source de ``recherche/sources.json`` désigne un dépôt GitHub, le commit dont les données sont
lues et les fichiers utiles. ``obtenir(nom)`` extrait ces seuls fichiers, tels qu'ils sont à ce
commit, dans ``recherche/.donnees/<nom>/<commit>/`` (ignoré par git), puis les réutilise. Les
résultats ne dépendent donc ni d'un dossier local ni du jour d'exécution.

Accès : un dépôt privé demande un jeton en lecture dans ``GITHUB_TOKEN`` (ou ``GH_TOKEN``). Pour
travailler hors ligne, ``RECHERCHE_SOURCE_<NOM>`` peut désigner une copie locale du dépôt (chemin
d'un clone git) : le même commit y est extrait, pas l'état de son dossier de travail. Sans cette
variable, un clone de la source placé à côté de BRVM-Recherche (``../Scraper-BRVM``) est lu quand il
contient le commit : ni réseau ni jeton.
"""
from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
from datetime import datetime, timezone
from pathlib import Path

RECHERCHE = Path(__file__).resolve().parents[1]
SOURCES = RECHERCHE / "sources.json"
DONNEES = RECHERCHE / ".donnees"
MANIFESTE = "manifeste.json"


def sources() -> dict:
    return json.loads(SOURCES.read_text(encoding="utf-8"))


def _supprimer(chemin: Path) -> None:
    """Supprime un dossier, y compris les fichiers en lecture seule de git (Windows)."""
    def forcer(fonction, cible, _exc):
        os.chmod(cible, stat.S_IWRITE)
        fonction(cible)
    if chemin.exists():
        shutil.rmtree(chemin, onexc=forcer)


def _git(args: list[str], cwd: Path | None = None, jeton: str | None = None) -> str:
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")
    entete = ["-c", f"http.extraHeader=Authorization: Bearer {jeton}"] if jeton else []
    r = subprocess.run(["git", *entete, *args], cwd=cwd, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"git {' '.join(args[:2])} : {r.stderr.strip()}")
    return r.stdout.strip()


def _clone_courant(cfg: dict) -> str | None:
    """Clone local de la source (dépôt de recherche/ ou dossier voisin), s'il a son commit."""
    nom = cfg["depot"].lower()
    for depot in (RECHERCHE.parent, RECHERCHE.parent.parent / cfg["depot"].split("/")[-1]):
        if not (depot / ".git").exists():
            continue
        try:
            origine = _git(["remote", "get-url", "origin"], depot)
            _git(["cat-file", "-e", f"{cfg['commit']}^{{commit}}"], depot)
        except (RuntimeError, OSError):
            continue
        if origine.lower().rstrip("/").removesuffix(".git").endswith(nom):
            return str(depot)
    return None


def obtenir(nom: str) -> Path:
    """Dossier contenant les fichiers de la source ``nom`` au commit figé (téléchargés au premier appel)."""
    cfg = sources()[nom]
    commit = cfg["commit"]
    dest = DONNEES / nom / commit[:12]
    if (dest / MANIFESTE).exists():
        return dest
    local = os.environ.get(f"RECHERCHE_SOURCE_{nom.upper()}") or _clone_courant(cfg)
    url = str(Path(local).resolve()) if local else f"https://github.com/{cfg['depot']}.git"
    jeton = None if local else (os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"))
    _supprimer(dest)                            # extraction interrompue : reprise complète
    dest.mkdir(parents=True)
    _git(["init", "-q"], dest)
    _git(["remote", "add", "origin", url], dest)
    _git(["sparse-checkout", "set", "--no-cone", *cfg["chemins"]], dest)
    try:                                        # le seul commit voulu, sans l'historique
        _git(["fetch", "-q", "--depth", "1", "--filter=blob:none", "origin", commit], dest, jeton)
    except RuntimeError:                        # serveur qui refuse un commit non annoncé
        _git(["fetch", "-q", "--filter=blob:none", "origin"], dest, jeton)
    _git(["checkout", "-q", commit], dest)
    if _git(["rev-parse", "HEAD"], dest) != commit:
        raise RuntimeError(f"{nom} : le commit extrait n'est pas {commit}")
    _supprimer(dest / ".git")
    # écrit en dernier : sa présence signale une extraction complète
    (dest / MANIFESTE).write_text(json.dumps({
        "source": nom, "depot": cfg["depot"], "commit": commit, "chemins": cfg["chemins"],
        "origine": "copie locale" if local else "GitHub",
        "extrait_le": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return dest


def data(nom: str) -> Path:
    """Dossier ``data/`` de la source ``nom``."""
    return obtenir(nom) / "data"
