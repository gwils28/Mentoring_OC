-- Besoin 2 — Nombre de ventes d'appartements par région, 1er semestre 2020.
-- Décortiquer : compter des ventes (COUNT), par région (GROUP BY), appartements seulement (WHERE).
-- Chemin des jointures : vente -> bien -> commune -> region.
SELECT
    r.nom_region,
    COUNT(*) AS nb_ventes_appartements
FROM vente AS v
INNER JOIN bien    AS b ON b.id_bien = v.id_bien
INNER JOIN commune AS c ON c.id_codedep_codecommune = b.id_codedep_codecommune
INNER JOIN region  AS r ON r.id_region = c.id_region
WHERE b.type_local = 'Appartement'
  AND v.date_vente BETWEEN '2020-01-01' AND '2020-06-30'
GROUP BY r.id_region, r.nom_region
ORDER BY nb_ventes_appartements DESC;
-- 17 régions apparaissent : Mayotte et les collectivités d'outre-mer n'ont aucune vente dans le fichier.
