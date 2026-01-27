-- Besoin 8 — Classement des régions selon le prix au m² des appartements de plus de 4 pièces.
-- Décortiquer : appartements, « plus de 4 pièces » lu strictement (5 pièces et plus), moyenne des prix au m²
-- par région, classement décroissant. n est affiché : une moyenne sur 2 ventes ne permet pas de classer une région.
SELECT
    RANK() OVER (ORDER BY AVG(v.valeur_fonciere / b.surface_carrez) DESC) AS rang,
    r.nom_region,
    ROUND(AVG(v.valeur_fonciere / b.surface_carrez), 0) AS prix_m2_moyen,
    COUNT(*) AS nb_ventes
FROM vente AS v
INNER JOIN bien    AS b ON b.id_bien = v.id_bien
INNER JOIN commune AS c ON c.id_codedep_codecommune = b.id_codedep_codecommune
INNER JOIN region  AS r ON r.id_region = c.id_region
WHERE b.type_local = 'Appartement'
  AND b.total_pieces > 4
  AND v.valeur_fonciere IS NOT NULL
GROUP BY r.id_region, r.nom_region
ORDER BY rang;
