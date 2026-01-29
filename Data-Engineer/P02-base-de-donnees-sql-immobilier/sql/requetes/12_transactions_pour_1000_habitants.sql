-- Besoin 12 — Les 20 communes avec le plus de transactions pour 1 000 habitants (communes de plus de 10 000 habitants).
-- Décortiquer : nombre de ventes par commune, divisé par la population, multiplié par 1 000 ;
-- garder les communes de plus de 10 000 habitants (population municipale) ; 20 premières.
SELECT
    c.nom_commune,
    c.code_departement,
    c.population,
    COUNT(*) AS nb_ventes,
    ROUND(COUNT(*) * 1000.0 / c.population, 2) AS ventes_pour_1000_hab
FROM vente AS v
INNER JOIN bien    AS b ON b.id_bien = v.id_bien
INNER JOIN commune AS c ON c.id_codedep_codecommune = b.id_codedep_codecommune
WHERE c.population > 10000
GROUP BY c.id_codedep_codecommune, c.nom_commune, c.code_departement, c.population
ORDER BY COUNT(*) * 1.0 / c.population DESC   -- trier sur la valeur exacte, pas sur l'arrondi
LIMIT 20;
