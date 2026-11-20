#!/usr/bin/env python3
"""Référencement de la librairie — génération automatique, sans effet visuel.

Met à jour, à partir de data/livres.json et data/config.json :
  - le bloc SEO de index.html (canonical, robots, Open Graph, X/Twitter) ;
  - les données structurées JSON-LD (Organization, Person, WebSite, ItemList de Book + Offer) ;
  - le catalogue <noscript> (lu seulement par les robots et les navigateurs sans JavaScript) ;
  - sitemap.xml (page canonique + couvertures pour Google Images).

Lancé à la main ou par l'action GitHub « Référencement » à chaque modification des données.
Rien n'est inventé : seules les informations présentes dans les fichiers de données sont publiées.
"""
import html
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
BASE_PAR_DEFAUT = "https://providenceeditions.github.io/"


def lire(nom):
    return json.loads((RACINE / nom).read_text(encoding="utf-8"))


def absolu(base, chemin):
    chemin = str(chemin or "").strip()
    if not chemin:
        return ""
    if re.match(r"^https?://", chemin):
        return chemin
    return base + chemin.lstrip("/")


def texte(t):
    return re.sub(r"\s+", " ", str(t or "")).strip()


def coupe(t, n):
    t = texte(t)
    if len(t) <= n:
        return t
    t = t[:n].rsplit(" ", 1)[0].rstrip(",;:—-")
    return t + "…"


def remplacer(source, nom, contenu):
    motif = re.compile(r"(<!-- SEO:%s:DEBUT -->)(.*?)(<!-- SEO:%s:FIN -->)" % (nom, nom), re.S)
    if not motif.search(source):
        sys.exit(f"Marqueur SEO:{nom} introuvable dans index.html")
    return motif.sub(lambda m: m.group(1) + "\n" + contenu + "\n" + m.group(3), source)


def url_livre(base, l):
    return base + "livres/" + str(l.get("slug") or "") + "/"


def date_modif(chemins):
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%cs", "--", *chemins], cwd=RACINE,
                             capture_output=True, text=True, check=True).stdout.strip()
        return out or date.today().isoformat()
    except Exception:
        return date.today().isoformat()


def main():
    livres_tous = lire("data/livres.json")
    cfg = lire("data/config.json")
    vente = cfg.get("vente", {})
    base = (vente.get("urlCanonique") or vente.get("urlSite") or BASE_PAR_DEFAUT).strip()
    if "claude.ai" in base or not base.startswith("http"):
        base = BASE_PAR_DEFAUT
    if not base.endswith("/"):
        base += "/"
    auteur = cfg.get("auteur", {})
    edit = cfg.get("editeur", {})
    livres = [l for l in livres_tous if l and l.get("titre") and l.get("disponible") is not False]
    devise = vente.get("devise") or "XOF"

    titre_site = "Les livres du Docteur B. Silas Gbavou — Providence Éditions Prestige"
    desc_site = ("Librairie numérique du Docteur B. Silas Gbavou : ouvrages PDF d'enseignement biblique, "
                 "doctrinal et prophétique sur la prière, le Royaume, l'Église et le ministère. "
                 "Providence Éditions Prestige, Bénin.")
    image_site = absolu(base, (livres[0].get("couverture") if livres else "") or "images/logo-providence.png")

    # ---- 1. Balises d'en-tête ----
    tete = "\n".join([
        f'<link rel="canonical" href="{html.escape(base)}">',
        '<meta name="robots" content="index, follow, max-image-preview:large">',
        '<meta property="og:locale" content="fr_FR">',
        f'<meta property="og:url" id="og-url" content="{html.escape(base)}">',
        f'<meta property="og:image:alt" content="{html.escape("Couverture d’un ouvrage du Docteur B. Silas Gbavou")}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" id="tw-titre" content="{html.escape(titre_site)}">',
        f'<meta name="twitter:description" id="tw-desc" content="{html.escape(desc_site)}">',
        f'<meta name="twitter:image" id="tw-image" content="{html.escape(image_site)}">',
        '<meta name="author" content="Docteur B. Silas Gbavou">',
        f'<link rel="alternate" hreflang="fr" href="{html.escape(base)}">',
        '<link rel="sitemap" type="application/xml" href="sitemap.xml">',
    ])

    # ---- 2. Données structurées ----
    org_id, pers_id, site_id = base + "#editeur", base + "#auteur", base + "#site"
    contacts = []
    if edit.get("email"):
        contacts.append({"@type": "ContactPoint", "contactType": "customer service", "email": edit["email"],
                         **({"telephone": edit["whatsapp"]} if edit.get("whatsapp") else {}),
                         "availableLanguage": "fr"})
    organisation = {"@type": "Organization", "@id": org_id, "name": "Providence Éditions Prestige",
                    "alternateName": cfg.get("structure") or "JSE La Providence", "url": base}
    if edit.get("logo"):
        organisation["logo"] = absolu(base, edit["logo"])
    if edit.get("email"):
        organisation["email"] = edit["email"]
    if edit.get("adresse"):
        organisation["address"] = {"@type": "PostalAddress", "streetAddress": edit["adresse"], "addressCountry": "BJ"}
    if contacts:
        organisation["contactPoint"] = contacts
    personne = {"@type": "Person", "@id": pers_id, "name": auteur.get("nom") or "Docteur B. Silas Gbavou"}
    if auteur.get("bioCourte"):
        personne["description"] = texte(auteur["bioCourte"])
    if auteur.get("photo"):
        personne["image"] = absolu(base, auteur["photo"])
    if auteur.get("nationalite") == "Béninoise":
        personne["nationality"] = {"@type": "Country", "name": "Bénin"}
    if auteur.get("facebook", "").startswith("http"):
        personne["sameAs"] = [auteur["facebook"]]
    site = {"@type": "WebSite", "@id": site_id, "url": base, "name": "Librairie du Docteur B. Silas Gbavou",
            "description": desc_site, "inLanguage": "fr", "publisher": {"@id": org_id}}

    elements = []
    for i, l in enumerate(livres, 1):
        auteurs = [a for a in (l.get("auteurs") or []) if a] or [personne["name"]]
        desc = l.get("description") or []
        desc = desc[0] if isinstance(desc, list) and desc else desc
        livre = {"@type": "Book", "name": texte(l["titre"]),
                 "author": [{"@id": pers_id} if a == personne["name"] else {"@type": "Person", "name": a} for a in auteurs],
                 "publisher": {"@id": org_id}, "bookFormat": "https://schema.org/EBook", "inLanguage": "fr",
                 "url": url_livre(base, l)}
        if l.get("sous"):
            livre["alternativeHeadline"] = texte(l["sous"])
        if desc:
            livre["description"] = coupe(desc, 500)
        if l.get("couverture"):
            livre["image"] = absolu(base, l["couverture"])
        if l.get("pages"):
            livre["numberOfPages"] = int(l["pages"])
        if l.get("isbn"):
            livre["isbn"] = str(l["isbn"])
        if l.get("theme"):
            livre["genre"] = texte(l["theme"])
        mots = [texte(m) for m in (l.get("motsCles") or []) if texte(m)]
        if mots:
            livre["keywords"] = ", ".join(mots)
        if l.get("prix") and str(l.get("lienPaiement", "")).startswith("https://"):
            livre["offers"] = {"@type": "Offer", "price": int(l["prix"]), "priceCurrency": devise,
                               "url": livre["url"], "availability": "https://schema.org/InStock",
                               "seller": {"@id": org_id}}
        elements.append({"@type": "ListItem", "position": i, "item": livre})
    catalogue = {"@type": "ItemList", "@id": base + "#catalogue", "name": "Ouvrages du Docteur B. Silas Gbavou",
                 "numberOfItems": len(elements), "itemListElement": elements}
    graphe = {"@context": "https://schema.org", "@graph": [organisation, personne, site, catalogue]}
    ld = '<script type="application/ld+json" id="ld-site">' + json.dumps(graphe, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + "</script>"

    # ---- 3. Catalogue lisible sans JavaScript ----
    lignes = ['<noscript>', '<section class="catalogue-statique">',
              '<h1>Les livres du Docteur B. Silas Gbavou — Providence Éditions Prestige</h1>',
              f'<p>{html.escape(desc_site)}</p>', '<ul>']
    for l in livres:
        desc = l.get("description") or []
        desc = desc[0] if isinstance(desc, list) and desc else desc
        prix = f'{int(l["prix"]):,}'.replace(",", " ") + " FCFA" if l.get("prix") else ""
        lien = l.get("lienPaiement", "")
        lignes.append("<li><article>")
        lignes.append(f'<h2>{html.escape(texte(l["titre"]))}</h2>')
        if l.get("sous"):
            lignes.append(f'<p>{html.escape(texte(l["sous"]))}</p>')
        lignes.append(f'<p>{html.escape(", ".join(a for a in (l.get("auteurs") or []) if a) or "Docteur B. Silas Gbavou")} · Livre numérique PDF{(" · " + str(l["pages"]) + " pages") if l.get("pages") else ""}{(" · " + prix) if prix else ""}</p>')
        if desc:
            lignes.append(f'<p>{html.escape(coupe(desc, 400))}</p>')
        chap = [texte(c) for c in (l.get("chapitres") or []) if texte(c)]
        if chap:
            lignes.append("<p>Au fil des pages : " + html.escape(" ; ".join(chap)) + ".</p>")
        if str(lien).startswith("https://"):
            # Le lien de paiement reste masqué : on renvoie vers la fiche du livre sur la librairie.
            lignes.append(f'<p><a href="{html.escape(url_livre(base, l))}">Découvrir et se procurer « {html.escape(texte(l["titre"]))} »</a></p>')
        lignes.append("</article></li>")
    lignes += ["</ul>", "</section>", "</noscript>"]
    noscript = "\n".join(lignes)

    # ---- Écriture de index.html ----
    p = RACINE / "index.html"
    src = p.read_text(encoding="utf-8")
    nouv = remplacer(src, "TETE", tete)
    nouv = remplacer(nouv, "JSONLD", ld)
    nouv = remplacer(nouv, "NOSCRIPT", noscript)
    if nouv != src:
        p.write_text(nouv, encoding="utf-8")

    # ---- 4. Plan du site ----
    lastmod = date_modif(["data", "index.html"])
    images = "".join(
        f"\n    <image:image><image:loc>{html.escape(absolu(base, l['couverture']))}</image:loc></image:image>"
        for l in livres if l.get("couverture"))
    urls = "".join(
        f"  <url>\n    <loc>{html.escape(url_livre(base, l))}</loc>\n    <lastmod>{lastmod}</lastmod>"
        + (f"\n    <image:image><image:loc>{html.escape(absolu(base, l['couverture']))}</image:loc></image:image>" if l.get("couverture") else "")
        + "\n  </url>\n" for l in livres if l.get("slug"))
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
               '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
               f'  <url>\n    <loc>{html.escape(base)}</loc>\n    <lastmod>{lastmod}</lastmod>{images}\n  </url>\n'
               + urls + '</urlset>\n')
    (RACINE / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    pages_livres(nouv, base, livres, organisation, personne, desc_site)
    print(f"SEO à jour : {len(livres)} livres, base {base}")



def attr(source, motif, valeur):
    """Remplace la valeur content/href d'une balise repérée par motif (regex sur la balise)."""
    m = re.search(motif, source)
    if not m:
        return source
    balise = m.group(0)
    nouvelle = re.sub(r'(content|href)="[^"]*"', lambda x: f'{x.group(1)}="{html.escape(valeur)}"', balise, count=1)
    return source.replace(balise, nouvelle, 1)


def pages_livres(gabarit, base, livres, organisation, personne, desc_site):
    """Une page publique par livre : même interface, même design, adresse propre et indexable.
    La page charge exactement la même application, puis affiche la fiche du livre."""
    dossier = RACINE / "livres"
    dossier.mkdir(exist_ok=True)
    gardes = set()
    for l in livres:
        slug = str(l.get("slug") or "")
        if not slug or not re.match(r"^[a-z0-9-]+$", slug):
            continue
        gardes.add(slug)
        url = url_livre(base, l)
        titre = texte(l["titre"])
        auteurs = [a for a in (l.get("auteurs") or []) if a] or [personne["name"]]
        desc = l.get("description") or []
        d0 = desc[0] if isinstance(desc, list) and desc else (desc or "")
        meta_desc = coupe(f"{titre} — livre PDF de {', '.join(auteurs)}. {texte(d0)}", 158)
        titre_page = f"{titre} — {auteurs[0]} | Livre PDF, Providence Éditions Prestige"
        image = absolu(base, l.get("couverture") or "")
        page = gabarit
        page = page.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<base href="../../">', 1)
        page = re.sub(r"<title>.*?</title>", f"<title>{html.escape(titre_page)}</title>", page, count=1, flags=re.S)
        page = attr(page, r'<meta name="description"[^>]*>', meta_desc)
        page = attr(page, r'<meta property="og:title"[^>]*>', f"{titre} — {auteurs[0]}")
        page = attr(page, r'<meta property="og:description"[^>]*>', meta_desc)
        page = attr(page, r'<meta property="og:image" [^>]*>', image)
        page = attr(page, r'<meta property="og:url"[^>]*>', url)
        page = attr(page, r'<meta property="og:type"[^>]*>', "book")
        page = attr(page, r'<meta name="twitter:title"[^>]*>', f"{titre} — {auteurs[0]}")
        page = attr(page, r'<meta name="twitter:description"[^>]*>', meta_desc)
        page = attr(page, r'<meta name="twitter:image"[^>]*>', image)
        page = attr(page, r'<link rel="alternate" hreflang="fr"[^>]*>', url)
        page = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{html.escape(url)}" data-fixe="1">', page, count=1)
        # Données structurées du livre
        livre = {"@type": "Book", "@id": url + "#livre", "name": titre, "url": url, "mainEntityOfPage": url,
                 "author": [{"@id": personne["@id"]} if a == personne["name"] else {"@type": "Person", "name": a} for a in auteurs],
                 "publisher": {"@id": organisation["@id"]}, "bookFormat": "https://schema.org/EBook", "inLanguage": "fr"}
        if l.get("sous"):
            livre["alternativeHeadline"] = texte(l["sous"])
        if d0:
            livre["description"] = coupe(" ".join(texte(x) for x in (desc if isinstance(desc, list) else [desc])), 900)
        if image:
            livre["image"] = image
        if l.get("pages"):
            livre["numberOfPages"] = int(l["pages"])
        if l.get("isbn"):
            livre["isbn"] = str(l["isbn"])
        if l.get("theme"):
            livre["genre"] = texte(l["theme"])
        mots = [texte(m) for m in (l.get("motsCles") or []) if texte(m)]
        if mots:
            livre["keywords"] = ", ".join(mots)
        if l.get("prix") and str(l.get("lienPaiement", "")).startswith("https://"):
            livre["offers"] = {"@type": "Offer", "price": int(l["prix"]), "priceCurrency": "XOF", "url": url,
                               "availability": "https://schema.org/InStock", "seller": {"@id": organisation["@id"]}}
        fil = {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Librairie", "item": base},
            {"@type": "ListItem", "position": 2, "name": "Les livres", "item": base + "#catalogue"},
            {"@type": "ListItem", "position": 3, "name": titre, "item": url}]}
        graphe = {"@context": "https://schema.org", "@graph": [livre, fil, organisation, personne]}
        ld = '<script type="application/ld+json" id="ld-site">' + json.dumps(graphe, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + "</script>"
        page = remplacer(page, "JSONLD", ld)
        # Contenu lisible sans JavaScript : la fiche du livre
        bloc = ["<noscript>", '<article class="livre-statique">', f"<h1>{html.escape(titre)}</h1>"]
        if l.get("sous"):
            bloc.append(f"<p>{html.escape(texte(l['sous']))}</p>")
        prix = f'{int(l["prix"]):,}'.replace(",", " ") + " FCFA" if l.get("prix") else ""
        bloc.append(f"<p>{html.escape(', '.join(auteurs))} · Livre numérique PDF{(' · ' + str(l['pages']) + ' pages') if l.get('pages') else ''}{(' · ' + prix) if prix else ''} · Providence Éditions Prestige</p>")
        for para in (desc if isinstance(desc, list) else [desc]):
            if texte(para):
                bloc.append(f"<p>{html.escape(texte(para))}</p>")
        cles = [texte(c) for c in (l.get("cles") or []) if texte(c)]
        if cles:
            bloc.append("<h2>Ce que vous allez découvrir</h2><ul>" + "".join(f"<li>{html.escape(c)}</li>" for c in cles) + "</ul>")
        chap = [texte(c) for c in (l.get("chapitres") or []) if texte(c)]
        if chap:
            bloc.append("<h2>Au fil des chapitres</h2><ul>" + "".join(f"<li>{html.escape(c)}</li>" for c in chap) + "</ul>")
        if l.get("pour"):
            bloc.append(f"<p>Pour qui ? {html.escape(texte(l['pour']))}</p>")
        bloc.append(f'<p><a href="{html.escape(base)}">Voir tous les livres de la librairie</a></p>')
        bloc += ["</article>", "</noscript>"]
        page = remplacer(page, "NOSCRIPT", "\n".join(bloc))
        # Ouvre directement la fiche du livre dans l'application (même design que la librairie)
        page = page.replace('<script src="app.js', f'<script>if(!location.hash)history.replaceState(null,"",location.pathname+location.search+"#livre-{slug}")</script>\n<script src="app.js', 1)
        cible = dossier / slug
        cible.mkdir(exist_ok=True)
        (cible / "index.html").write_text(page, encoding="utf-8")
    # Pages de livres retirés : supprimées pour ne pas laisser d'adresses mortes
    for d in dossier.iterdir():
        if d.is_dir() and d.name not in gardes:
            for f in d.iterdir():
                f.unlink()
            d.rmdir()


if __name__ == "__main__":
    main()
