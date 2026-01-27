-- Besoin 9 — Communes ayant eu au moins 50 ventes au 1er trimestre.
-- Décortiquer : ventes du T1 (WHERE, avant le regroupement), comptées par commune (GROUP BY),
-- puis condition sur ce compte (HAVING, après le regroupement). On regroupe par clé : des communes homonymes existent.
SELECT
    c.nom_commune,
    c.code_departement,
    COUNT(*) AS nb_ventes_t1
FROM vente AS v
INNER JOIN bien    AS b ON b.id_bien = v.id_bien
INNER JOIN commune AS c ON c.id_codedep_codecommune = b.id_codedep_codecommune
WHERE v.date_vente BETWEEN '2020-01-01' AND '2020-03-31'
GROUP BY c.id_codedep_codecommune, c.nom_commune, c.code_departement
HAVING COUNT(*) >= 50
ORDER BY nb_ventes_t1 DESC;
