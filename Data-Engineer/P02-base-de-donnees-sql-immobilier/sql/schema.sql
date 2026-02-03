-- Schéma de la base DATAImmo (SQLite) : region <- commune <- bien <- vente
-- Une flèche = une clé étrangère : chaque vente porte sur un bien, situé dans une commune, rattachée à une région.
-- Le DDL est écrit pour SQLite. Pour PostgreSQL, il faut l'adapter (NUMERIC au lieu de REAL pour les montants,
-- type DATE, CHECK sans typeof()) : voir ALLER_PLUS_LOIN.md, section 1.

-- SQLite ignore les clés étrangères tant qu'on ne les active pas (réglage valable pour la connexion en cours).
PRAGMA foreign_keys = ON;

CREATE TABLE region (
    id_region        TEXT PRIMARY KEY,           -- code INSEE en texte : « 02 » (Martinique) garde son zéro
    nom_region       TEXT NOT NULL,
    nom_regroupement TEXT NOT NULL               -- « Province », « Ile-de-France », « DROM-COM »
);

CREATE TABLE commune (
    id_codedep_codecommune TEXT PRIMARY KEY,     -- département + commune sur 3 chiffres : « 01103 », « 972229 », « 2A004 »
    id_region              TEXT NOT NULL REFERENCES region (id_region),
    code_departement       TEXT NOT NULL,        -- texte : « 2A », « 2B », « 972 »
    code_commune           TEXT NOT NULL CHECK (length(code_commune) = 3),
    nom_commune            TEXT NOT NULL,
    population             INTEGER NOT NULL CHECK (population >= 0)  -- population municipale (PMUN)
);

CREATE TABLE bien (
    id_bien                INTEGER PRIMARY KEY,
    id_codedep_codecommune TEXT NOT NULL REFERENCES commune (id_codedep_codecommune),
    -- Adresse découpée en champs atomiques (1re forme normale)
    no_voie                INTEGER,
    btq                    TEXT,                 -- indice de répétition : B (bis), T (ter), Q (quater)...
    type_voie              TEXT,                 -- RUE, AV, BD...
    voie                   TEXT NOT NULL,
    -- Le code postal décrit l'adresse, pas la commune : Nice a 4 codes postaux, 05100 couvre 3 communes.
    code_postal            TEXT CHECK (length(code_postal) = 5),
    type_local             TEXT NOT NULL CHECK (type_local IN ('Appartement', 'Maison')),
    total_pieces           INTEGER CHECK (total_pieces >= 0),
    surface_carrez         REAL CHECK (surface_carrez > 0),     -- surface Carrez du 1er lot seulement
    surface_reelle_bati    INTEGER CHECK (surface_reelle_bati >= 0)
);

CREATE TABLE vente (
    id_vente        INTEGER PRIMARY KEY,
    id_bien         INTEGER NOT NULL UNIQUE REFERENCES bien (id_bien),  -- UNIQUE : 1 vente par bien sur la période
    date_vente      TEXT NOT NULL CHECK (date(date_vente) IS date_vente),  -- une vraie date AAAA-MM-JJ (refuse 2020-13-45)
    valeur_fonciere REAL CHECK (valeur_fonciere IS NULL
                                OR (typeof(valeur_fonciere) = 'real' AND valeur_fonciere > 0)),  -- NULL si absente (18) ; refuse ''
    nombre_lots     INTEGER NOT NULL CHECK (nombre_lots >= 1)
);
