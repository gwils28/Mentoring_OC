-- Besoin 4 — Les 10 départements où le prix du mètre carré est le plus élevé.
-- Décortiquer : prix au m² d'une vente = valeur foncière / surface Carrez ; moyenne par département ; 10 premiers.
-- Les ventes sans valeur foncière (NULL) sont ignorées par AVG ; on affiche n pour juger la solidité de chaque moyenne.
SELECT
    c.code_departement,
    ROUND(AVG(v.valeur_fonciere / b.surface_carrez), 0) AS prix_m2_moyen,
    COUNT(*) AS nb_ventes
FROM vente AS v
INNER JOIN bien    AS b ON b.id_bien = v.id_bien
INNER JOIN commune AS c ON c.id_codedep_codecommune = b.id_codedep_codecommune
WHERE v.valeur_fonciere IS NOT NULL
GROUP BY c.code_departement
ORDER BY AVG(v.valeur_fonciere / b.surface_carrez) DESC   -- trier sur la valeur exacte, pas sur l'arrondi
LIMIT 10;
