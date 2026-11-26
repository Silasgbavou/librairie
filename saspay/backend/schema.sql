CREATE TABLE IF NOT EXISTS commandes (
  id TEXT PRIMARY KEY,
  offre TEXT NOT NULL,
  titre TEXT NOT NULL,
  livres TEXT NOT NULL,
  montant INTEGER NOT NULL CHECK (montant > 0),
  devise TEXT NOT NULL DEFAULT 'XOF',
  etat TEXT NOT NULL DEFAULT 'en_attente' CHECK (etat IN ('en_attente','payee','abandonnee')),
  email TEXT NOT NULL,
  nom TEXT NOT NULL,
  ip TEXT,
  session_id TEXT UNIQUE,
  url_paiement TEXT,
  transaction_id TEXT,
  montant_debite TEXT,
  montant_net TEXT,
  cree_le INTEGER NOT NULL,
  verifie_le INTEGER,
  payee_le INTEGER,
  email_envoye_le INTEGER,
  telechargements INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS i_commandes_etat ON commandes(etat, cree_le);
CREATE INDEX IF NOT EXISTS i_commandes_ip ON commandes(ip, cree_le);
CREATE TABLE IF NOT EXISTS evenements (n INTEGER PRIMARY KEY AUTOINCREMENT, recu_le INTEGER, evenement TEXT, ref TEXT);
