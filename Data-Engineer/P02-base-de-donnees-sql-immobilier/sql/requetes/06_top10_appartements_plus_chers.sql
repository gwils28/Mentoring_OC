-- Besoin 6 — Les 10 appartements les plus chers, avec la région et le nombre de mètres carrés.
-- Décortiquer : appartements, tri décroissant sur la valeur foncière, 10 premiers ; afficher région et surface.
SELECT
    v.valeur_fonciere,
    b.surface_carrez AS surface_m2,
    b.total_pieces   AS nb_pieces,
    c.nom_commune,
    r.nom_region
FROM vente AS v
INNER JOIN bien    AS b ON b.id_bien = v.id_bien
INNER JOIN commune AS c ON c.id_codedep_codecommune = b.id_codedep_codecommune
INNER JOIN region  AS r ON r.id_region = c.id_region
WHERE b.type_local = 'Appartement'
  AND v.valeur_fonciere IS NOT NULL
ORDER BY v.valeur_fonciere DESC
LIMIT 10;
