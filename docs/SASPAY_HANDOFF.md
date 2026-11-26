# SasPay — état de l'intégration (passation Claude ↔ ChatGPT)

Dernière mise à jour : 26 novembre 2026 — Claude Opus 5.5. Aucun secret dans ce fichier.

## Situation
- Compte marchand SasPay validé (KYC confirmé le 24/11/2026 selon le propriétaire).
- Maketou reste **le seul paiement actif** sur la boutique. Rien n'a été basculé.
- Aucune clé API créée, aucun webhook créé, aucun backend déployé, aucun PDF copié, aucun paiement lancé.

## Audit du kit préparatoire V3 (backend/worker.mjs, catalogue.mjs, schema.sql)
Base saine et réutilisable :
- clé lue côté serveur uniquement ; prix et contenu des lots fixés côté serveur ;
- montant en chaîne décimale (`"8000.00"`) ; nom + e-mail collectés avant paiement ;
- webhook : contrôle de l'horodatage (300 s) puis HMAC-SHA256 hexadécimal sur `timestamp + "." + corps brut`, comparaison en temps constant ;
- livraison conditionnée à une vérification serveur, passage `pending → paid` atomique (une seule fois), liens de téléchargement liés à la commande payée ;
- reprise programmée des commandes en attente si le navigateur se ferme.

Points à confirmer ou corriger avant tout déploiement :
1. **Réponse de `GET /checkout-sessions/{id}/status/`** : le kit suppose `status=PAID` et `transaction_status=SUCCESS`. Champs non confirmés par l'OpenAPI officiel → à vérifier sur `https://api.saspay.me/api-reference/openapi.json` et sur une réponse réelle.
2. **Environnement de test** : le kit n'envoie une clé `sk_test_` qu'à `sandbox-api.saspay.me`, hôte **non confirmé**. À vérifier auprès de SasPay avant tout test ; aucun test débiteur sans accord écrit du propriétaire.
3. **Données du webhook `transaction.success`** : le kit lit `data.metadata.order_id` ; forme exacte à confirmer avec un `webhook.test` du tableau de bord.
4. **Renvoi d'e-mail** : `requestEmail` ne renvoie rien si un premier envoi a réussi (`email_sent_at` déjà rempli). Prévoir un vrai renvoi limité en fréquence.
5. **Expéditeur e-mail** : Brevo n'autorise pas d'office une adresse Gmail comme expéditeur ; à valider (quota gratuit, SPF/DKIM).
6. **Hébergement** : Cloudflare Workers + D1 + KV (offre gratuite) proposé ; compte Cloudflare à ouvrir par le propriétaire (création de compte = son accord).

## Prochaines étapes (ordre)
1. Lire l'OpenAPI officiel et la documentation `llms.txt` (accès web à autoriser).
2. Propriétaire : ouvrir Chrome sur l'ordinateur, se connecter à SasPay, GitHub et (nouveau) Cloudflare.
3. Claude : backend sur cette branche, coffre de secrets Cloudflare, clé « Encaissement uniquement » transférée directement dans le coffre, webhook créé dans le tableau de bord SasPay.
4. Copie privée des 14 PDF (Drive → KV) avec manifeste SHA-256.
5. Tests simulés, puis `webhook.test`, puis un paiement réel de faible montant **après accord**.
6. Bascule derrière un interrupteur (`SASPAY_ENABLED=false` par défaut) ; Maketou retiré seulement après validation complète.
