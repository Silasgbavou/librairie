# Résultats des tests (Playwright, Chromium)

| Test | Résultat | Détail |
|---|---|---|
| Un livre : arrive sur la commande | OK |  |
| Un livre : compteur du dock = 1 | OK |  |
| Prix absent : libellé honnête | OK |  |
| Formulaire vide : erreurs par champ | OK |  |
| Formulaire vide : focus sur le 1er champ en erreur | OK |  |
| Téléphone invalide refusé | OK |  |
| E-mail invalide refusé | OK |  |
| Plusieurs livres : 2 dans la commande | OK |  |
| Coordonnées conservées après changement | OK |  |
| Sans lien de paiement vérifié : seule l'option WhatsApp | OK |  |
| Envoi : page de confirmation | OK |  |
| Lien WhatsApp contient les 2 titres | OK |  |
| Aucune coche ni « payé » présenté comme preuve | OK |  |
| Rechargement de la dernière étape : lien conservé | OK |  |
| Collection : compteur = 14 | OK |  |
| Collection : bascule expliquée | OK |  |
| Collection : annulation rend la sélection | OK |  |
| #confirmation sans commande : message adapté | OK |  |
| Livre retiré nettoyé du panier | OK |  |
| Clavier : 1er Tab = lien d'évitement | OK |  |
| Changement de page : focus sur le titre | OK |  |
| Recherche filtre la grille | OK |  |
| Pas de défilement horizontal à 360px (11 pages) | OK |  |
| Dock 360px : zones ≥ 44 px | OK | 0 |
| Dock 360px : 5 entrées inchangées | OK | ['Accueil', 'Livres', 'Commande', 'Auteur', 'Aide'] |
| Pas de défilement horizontal à 390px (11 pages) | OK |  |
| Dock 390px : zones ≥ 44 px | OK | 0 |
| Dock 390px : 5 entrées inchangées | OK | ['Accueil', 'Livres', 'Commande', 'Auteur', 'Aide'] |
| Pas de défilement horizontal à 430px (11 pages) | OK |  |
| Dock 430px : zones ≥ 44 px | OK | 0 |
| Dock 430px : 5 entrées inchangées | OK | ['Accueil', 'Livres', 'Commande', 'Auteur', 'Aide'] |
| Pas de défilement horizontal à 768px (11 pages) | OK |  |
| Dock 768px : zones ≥ 44 px | OK | 0 |
| Dock 768px : 5 entrées inchangées | OK | ['Accueil', 'Livres', 'Commande', 'Auteur', 'Aide'] |
| Pas de défilement horizontal à 1024px (11 pages) | OK |  |
| Pas de défilement horizontal à 1440px (11 pages) | OK |  |
| Aucun lien href="#" | OK | 0 |
| Mouvement réduit : pas de classe d'animation | OK |  |
| Bouton retour : revient au catalogue | OK |  |
| Erreurs JavaScript | OK |  |

Note : la police Plus Jakarta Sans vient de Google Fonts ; sur le serveur de test, une police système de remplacement a pu être utilisée.
