#!/usr/bin/env python3
"""Index de recherche plein texte de la librairie.

Lit le texte intégral des livres (fichiers NN.txt dans un dossier hors du dépôt,
NN = numéro du livre) et produit data/recherche.json : la liste des mots présents
dans chaque livre (sans les textes eux-mêmes), pour que la recherche du site trouve
un livre dès qu'un terme y apparaît réellement.

Format : {"livres": ["01", ...], "mots": {"synthetique": 4097, ...}}
Chaque valeur est un masque binaire : bit i = le mot figure dans livres[i].
Usage : python3 outils/index_recherche.py /chemin/vers/textes
"""
import json, re, sys, unicodedata
from collections import Counter
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
VIDES = set("""alors aucun aussi autre autres avant avec avoir bien cela celle celles celui cette ceux chaque chez comme comment dans depuis donc dont elle elles encore entre etre fait faire leur leurs lors mais meme moins nous notre nous plus pour pourquoi quand quel quelle quelles quels sans selon sera sera ses sont sous tous tout toute toutes tres une vers vous votre vos etait etaient avait avaient peut peuvent ainsi apres cest quil quils quelle dune dans aux des les une est par pas que qui sur son ses ces mes tes nos lui eux ont sont ete""".split())

def normal(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")

def mots(texte):
    return re.findall(r"[a-z0-9]+", normal(texte.replace("\u00ad", "").replace("’", " ").replace("'", " ").replace("ʼ", " ")))

def recoller(tokens, vocab):
    """Recolle les syllabes séparées par certaines extractions PDF (« con nais sance »)."""
    out, i = [], 0
    while i < len(tokens):
        fait = False
        for n in (5, 4, 3, 2):
            if i + n <= len(tokens):
                part = tokens[i:i + n]
                mot = "".join(part)
                if len(mot) >= 6 and mot in vocab and any(p not in vocab or len(p) <= 3 for p in part):
                    out.append(mot); i += n; fait = True; break
        if not fait:
            out.append(tokens[i]); i += 1
    return out

def main(dossier):
    dossier = Path(dossier)
    livres = json.loads((RACINE / "data/livres.json").read_text(encoding="utf-8"))
    ids = [str(l["id"]) for l in livres]
    textes = {i: (dossier / f"{i}.txt").read_text(encoding="utf-8") for i in ids if (dossier / f"{i}.txt").exists()}
    # Vocabulaire de référence à partir des textes propres (sans syllabes séparées)
    compte = Counter()
    for t in textes.values():
        compte.update(mots(t))
    vocab = {m for m, n in compte.items() if n >= 3 and len(m) >= 4}
    index, paires = {}, {}
    for k, i in enumerate(ids):
        if i not in textes:
            continue
        utiles = [m for m in recoller(mots(textes[i]), vocab) if len(m) >= 3 and not m.isdigit() and m not in VIDES and len(m) <= 30]
        for m in set(utiles):
            index[m] = index.get(m, 0) | (1 << k)
        # Expressions de deux mots (« sein Abraham », « nuée témoins ») présentes au moins deux fois dans le livre
        for (a, b), n in Counter(zip(utiles, utiles[1:])).items():
            if n >= 3 and len(a) >= 4 and len(b) >= 4:
                cle = a + " " + b
                paires[cle] = paires.get(cle, 0) | (1 << k)
    paires = {c: v for c, v in paires.items() if bin(v).count("1") <= 4}
    sortie = {"livres": ids, "mots": dict(sorted(index.items())), "paires": dict(sorted(paires.items()))}
    (RACINE / "data/recherche.json").write_text(json.dumps(sortie, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{len(index)} mots indexés pour {len(textes)} livres sur {len(ids)}")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "../textes")
