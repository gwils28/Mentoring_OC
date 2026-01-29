-- Besoin 11 — Moyenne des valeurs foncières pour le top 3 des communes des départements 6, 13, 33, 59 et 69.
-- Décortiquer : moyenne des valeurs foncières par commune ; rang de chaque commune DANS son département ;
-- garder les rangs 1 à 3. Piège : le département « 6 » s'écrit « 06 » en base (texte sur 2 caractères).
WITH moyenne_par_commune AS (
    SELECT
        c.code_departement,
        c.nom_commune,
        AVG(v.valeur_fonciere) AS valeur_moyenne,     -- arrondie seulement à l'affichage
        COUNT(*) AS nb_ventes
    FROM vente AS v
    INNER JOIN bien    AS b ON b.id_bien = v.id_bien
    INNER JOIN commune AS c ON c.id_codedep_codecommune = b.id_codedep_codecommune
    WHERE c.code_departement IN ('06', '13', '33', '59', '69')
      AND v.valeur_fonciere IS NOT NULL
    GROUP BY c.id_codedep_codecommune, c.code_departement, c.nom_commune
),
classement AS (
    SELECT
        *,
        RANK() OVER (PARTITION BY code_departement ORDER BY valeur_moyenne DESC) AS rang
    FROM moyenne_par_commune
)
SELECT code_departement, rang, nom_commune, ROUND(valeur_moyenne, 0) AS valeur_moyenne, nb_ventes
FROM classement
WHERE rang <= 3
ORDER BY code_departement, rang;
