# Boutique des livres du Docteur B. Silas Gbavou
Providence Éditions Prestige — JSE La Providence (Bénin)

## 1. Contenu du dossier

| Fichier | Rôle |
|---|---|
| `index.html` | Structure de la boutique (une seule page, plusieurs vues) |
| `style.css` | Charte Providence : orange #FD7602, bleu #1483B8, jaune #FDC60C, ivoire #F9F6EF, noir chaud #231E1A, Cormorant Garamond + Manrope |
| `app.js` | Fonctionnement : catalogue, fiches, panier, commande, confirmation |
| `data/livres.json` | **Fiches des 14 livres** (données tirées du catalogue ChatGPT) |
| `data/config.json` | **Réglages** : auteur, éditeur, WhatsApp, Mobile Money, prix de la collection, liens de paiement |
| `couvertures/` | Les 14 couvertures originales (800 px, JPEG haute qualité) |
| `couvertures/mini/` | Les mêmes en petit format, pour un chargement rapide sur téléphone |

## 2. Parcours de vente

Accueil (`#accueil`) → Catalogue (`#catalogue`) → Fiche du livre (`#livre-…`) → Commande (`#commande`) → Paiement → Confirmation (`#confirmation`) → Livraison du PDF.

Chaque livre a sa propre adresse partageable, par exemple `…#livre-vase-d-or`.

Pages complémentaires : l'auteur et la maison d'édition (`#auteur`), puis paiement et livraison (`#aide`).

## 3. Champs à compléter (laissés vides volontairement)

Aucune information absente des PDF n'a été inventée.

**Dans `data/livres.json` (pour chaque livre) :**
- `prix` : le prix en FCFA (ex. `3000`). Tant qu'il est vide, la page affiche « Prix communiqué à la commande ».
- `lienPaiement` : le lien de vente Maketou du livre. S'il est rempli, le paiement en ligne et la livraison automatique s'activent.
- `isbn` : seulement si vous en obtenez un.
- `copyright` : vide pour 3 livres (*Royaume de la Puissance*, *Sept Montagnes*, *Cinq Ministères*), car il n'a pas été relevé dans l'extraction.
- `disponible` : mettre `false` retire un livre de la vente sans le supprimer.

**Dans `data/config.json` :**
- `auteur.photo` : le chemin de votre photo (ex. `images/photo-auteur.jpg`)
- `editeur.logo` : le chemin du logo Providence
- `vente.mobileMoney` : votre numéro Mobile Money (ex. `MTN MoMo 01 XX XX XX XX — Nom`)
- `vente.prixCollection` et `vente.lienCollection` : le prix et le lien de paiement de l'offre groupée des 14 livres
- `editeur.adresse` et `editeur.slogan` : absents des PDF

## 4. Paiement et livraison : ce qui est en place, ce qu'il faut connecter

**Ce qui fonctionne dès maintenant, sans aucune inscription :**
La commande part sur WhatsApp, déjà rédigée, vers le +229 01 49 30 18 86. Vous envoyez les instructions Mobile Money, vous vérifiez le paiement, puis vous envoyez le PDF. La page ne prétend jamais qu'un paiement a réussi.

**Pour le paiement automatique et la livraison du PDF : votre compte Maketou (maketou.com)**
- Plateforme béninoise : paiement Mobile Money, retrait de l'argent sur votre téléphone
- Livraison automatique du PDF après paiement
- Codes promo, pixels Facebook, Google et TikTok, automatisations, suivi des conversions
- Pas d'abonnement : environ 5 % de commission par vente
- Plusieurs boutiques possibles sur un même compte (adresse en .mymaketou.shop)

Étapes :
1. Dans Maketou, créer un produit « Produits digitaux » par livre : titre, couverture, prix, fichier PDF.
2. Créer un produit pour la collection complète (les 14 PDF), si vous voulez la proposer.
3. Copier le lien de vente de chaque produit dans `lienPaiement` (et celui de la collection dans `lienCollection`).
4. Republier la boutique : le bouton « Paiement en ligne sécurisé » s'active tout seul.

Avant d'ouvrir la vente, faites un achat test pour vérifier : les moyens de paiement proposés (Mobile Money, carte), l'e-mail de livraison et la protection du fichier.

## 5. Administration

| Besoin | Où le faire |
|---|---|
| Modifier une fiche, un prix, un lien | `data/livres.json` et `data/config.json`, ou demander à Claude, qui republie |
| Commandes, ventes, clients | Tableau de bord Maketou (paiement en ligne) et WhatsApp (commandes manuelles) |
| Moyens de paiement | Tableau de bord Maketou |
| Téléchargements, livraison des PDF | Maketou (livraison automatique) |
| Offres groupées, codes promo | Maketou (produit « collection », codes promo) |
| Statistiques de conversion | Maketou (suivi des conversions, pixels Facebook/Google/TikTok) |

La boutique est une page sans serveur : elle ne contient ni mot de passe ni données de clients. C'est volontaire. Les données sensibles (paiements, clients) restent chez le prestataire de paiement.

## 6. Marketing intégré

- Une adresse par livre, avec des boutons de partage WhatsApp et Facebook
- Section « Vous aimerez aussi » : 3 livres recommandés sur chaque fiche
- Inscription aux nouveautés par WhatsApp, avec consentement explicite (case à cocher dans la commande et bouton sur l'accueil)
- Balises de description et d'image de partage (Open Graph) dans `index.html`

## 7. Mise en ligne sur votre propre adresse (facultatif, pour Google)

La boutique est déjà en ligne sur son lien claude.ai. Pour un nom de domaine à vous et un meilleur référencement Google, ce dossier peut être hébergé gratuitement, tel quel, sur **Netlify Drop** (app.netlify.com/drop) ou **Cloudflare Pages**. Il suffit d'y déposer le dossier complet.

Après la mise en ligne, mettez la nouvelle adresse dans `vente.urlSite` (`data/config.json`), pour que les liens de partage pointent au bon endroit.
