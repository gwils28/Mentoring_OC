-- Besoin 5 — Prix moyen du mètre carré d'une maison en Île-de-France.
-- Décortiquer : maisons seulement, région Île-de-France, moyenne des prix au m².
-- Piège : le référentiel écrit « Ile-de-France » sans accent ; on filtre sur le code région ('11'), plus sûr qu'un nom.
SELECT
    ROUND(AVG(v.valeur_fonciere / b.surface_carrez), 0) AS prix_m2_moyen_maison_idf,
    COUNT(*) AS nb_maisons
FROM vente AS v
INNER JOIN bien    AS b ON b.id_bien = v.id_bien
INNER JOIN commune AS c ON c.id_codedep_codecommune = b.id_codedep_codecommune
WHERE b.type_local = 'Maison'
  AND c.id_region = '11'
  AND v.valeur_fonciere IS NOT NULL;
