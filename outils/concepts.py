#!/usr/bin/env python3
"""Lexique doctrinal de l'assistant bibliothécaire.

Lit le texte intégral des livres (NN.txt, hors du dépôt) et retient pour chaque livre
ses grands termes distinctifs (mots et expressions de 2 à 3 mots qui reviennent souvent
dans ce livre et peu ailleurs). Produit data/concepts.json : {"terme": {"NN": poids}}.
Les textes eux-mêmes ne sont jamais publiés.
Usage : python3 outils/concepts.py /chemin/vers/textes
"""
import json, math, re, sys, unicodedata
from collections import Counter, defaultdict
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
LIAISON = set("de du des la le les l d a au aux et en sur dans par pour".split())
VIDES = set("""alors aucun aussi autre autres avant avec avoir bien cela celle celles celui cette ceux chaque chez comme comment dans depuis donc dont elle elles encore entre etre fait faire leur leurs lors mais meme moins nous notre plus pourquoi quand quel quelle quelles quels sans selon sera ses sont sous tous tout toute toutes tres une vers vous votre vos etait etaient avait avaient peut peuvent ainsi apres cest quil quils dune aux des les est par pas que qui sur son ces mes tes nos lui eux ont ete cet ceci cela ici deja car dire dit fois chose choses cas part celui faut doit doivent avons avez sommes etes serait seront sera ceux tant tel telle tels telles sans donc puis enfin ensuite non oui point voici voila egalement toujours jamais souvent ainsi alors leur lorsque lorsqu jusqu quoi aussi bien tres plus moins peu beaucoup autre autres meme memes chapitre page partie introduction conclusion figure tableau verset versets lire voir""".split())

def normal(s):
    s = unicodedata.normalize("NFD", s.replace("\u00ad", "").lower().replace("œ", "oe").replace("æ", "ae"))
    return "".join(c for c in s if unicodedata.category(c) != "Mn")

def mots(t):
    t = normal(t.replace("’", " ").replace("'", " "))
    t = re.sub(r"\bdedieu\b", "de dieu", t)
    return re.findall(r"[a-z]+(?:-[a-z]+)*", t)

PARASITES = ("parole declare", "parce qu", "resume dans", "developpement ci", "j entends", "temps soit", "invisible c", "fondement enseigne", "esprit sort", "sort de dieu", "lieu final", "experience personnelle", "differentes dimensions")

ENTETES = set("docteur silas gbavou appolos sommaire section encadre visuel dr chapitre bavo b m g u".split())

def recoller(tokens, vocab):
    """Recolle les syllabes séparées par certaines extractions PDF (« sacri fica teur »)."""
    out, i = [], 0
    while i < len(tokens):
        for n in (5, 4, 3, 2):
            part = tokens[i:i + n]
            if len(part) == n:
                mot = "".join(part)
                if len(mot) >= 6 and mot in vocab and any(p not in vocab for p in part):
                    out.append(mot); i += n; break
        else:
            out.append(tokens[i]); i += 1
    return out

def grammes(tokens):
    out = Counter()
    for i, w in enumerate(tokens):
        if len(w) >= 5 and w not in VIDES and w not in ENTETES:
            out[w] += 1
        for n in (2, 3, 4):
            g = tokens[i:i + n]
            if len(g) < n or g[0] in LIAISON or g[-1] in LIAISON or g[0] in VIDES or g[-1] in VIDES:
                continue
            if any(x in VIDES and x not in LIAISON for x in g) or any(x in ENTETES for x in g) or sum(len(x) >= 4 for x in g) < 2:
                continue
            out[" ".join(g)] += 1
    return out

def main(dossier):
    livres = json.loads((RACINE / "data/livres.json").read_text(encoding="utf-8"))
    ids = [l["id"] for l in livres]
    textes = {i: mots((Path(dossier) / f"{i}.txt").read_text(encoding="utf-8")) for i in ids if (Path(dossier) / f"{i}.txt").exists()}
    # Vocabulaire de référence : livres dont l'extraction est propre (sans syllabes séparées)
    propres = [t for t in textes.values() if Counter(t)["sance"] < 20]
    tous = Counter(w for t in propres for w in t)
    vocab = {w for w, n in tous.items() if n >= 3 and len(w) >= 4}
    comptes = {i: grammes(recoller(t, vocab)) for i, t in textes.items()}
    tailles = {i: sum(c.values()) for i, c in comptes.items()}
    df = Counter()
    for c in comptes.values():
        df.update(k for k, n in c.items() if n >= 2)
    N = len(comptes)
    lex = defaultdict(dict)
    for i, c in comptes.items():
        cands = []
        for k, n in c.items():
            mini = 3 if " " in k else 6
            if n < mini or df[k] > 4 or any(p in k for p in PARASITES):
                continue
            tf = n / tailles[i] * 1e5
            s = tf * math.log(1 + N / df[k]) * (1.6 if " " in k else 1)
            cands.append((s, k))
        cands.sort(reverse=True)
        for s, k in cands[:260]:
            lex[k][i] = round(s, 2)
    # Normalisation : poids 1 à 10 par terme
    m = max(v for d in lex.values() for v in d.values())
    out = {k: {i: max(1, round(10 * math.sqrt(v / m), 1)) for i, v in d.items()} for k, d in sorted(lex.items())}
    (RACINE / "data/concepts.json").write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(len(out), "termes")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "../textes")

def doctrines(dossier):
    """Pour chaque grand terme de outils/doctrines.txt : livres où il est réellement développé (fréquence relative)."""
    livres = json.loads((RACINE / "data/livres.json").read_text(encoding="utf-8"))
    ids = [l["id"] for l in livres]
    textes = {i: " " + " ".join(mots((Path(dossier) / f"{i}.txt").read_text(encoding="utf-8"))) + " " for i in ids if (Path(dossier) / f"{i}.txt").exists()}
    taille = {i: len(t) / 1e5 for i, t in textes.items()}
    termes = [normal(x).strip() for x in (RACINE / "outils/doctrines.txt").read_text(encoding="utf-8").splitlines() if x.strip() and not x.startswith("#")]
    out = {}
    for terme in termes:
        cle = " " + " ".join(mots(terme)) + " "
        dens = {i: t.count(cle) / taille[i] for i, t in textes.items() if t.count(cle) >= 3}
        if not dens:
            continue
        haut = max(dens.values())
        garde = {i: round(10 * d / haut, 1) for i, d in dens.items() if d >= haut * 0.25}
        out[cle.strip()] = dict(sorted(garde.items(), key=lambda x: -x[1])[:5])
    return out

if __name__ == "__main__" and len(sys.argv) > 1:
    d = json.loads((RACINE / "data/concepts.json").read_text(encoding="utf-8"))
    doc = doctrines(sys.argv[1])
    (RACINE / "data/concepts.json").write_text(json.dumps({"termes": d, "doctrines": doc}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(len(doc), "grands termes doctrinaux")
