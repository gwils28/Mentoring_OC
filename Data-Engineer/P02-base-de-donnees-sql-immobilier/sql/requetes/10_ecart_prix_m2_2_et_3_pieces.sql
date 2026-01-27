-- Besoin 10 — Différence en % du prix au m² entre un appartement de 2 pièces et un de 3 pièces.
-- Décortiquer : prix au m² moyen des 2 pièces, puis des 3 pièces, puis (P3 - P2) / P2 : l'écart vu depuis le 2 pièces.
WITH prix_par_taille AS (
    SELECT
        AVG(CASE WHEN b.total_pieces = 2 THEN v.valeur_fonciere / b.surface_carrez END) AS prix_m2_2p,
        AVG(CASE WHEN b.total_pieces = 3 THEN v.valeur_fonciere / b.surface_carrez END) AS prix_m2_3p
    FROM vente AS v
    INNER JOIN bien AS b ON b.id_bien = v.id_bien
    WHERE b.type_local = 'Appartement'
      AND v.valeur_fonciere IS NOT NULL
)
SELECT
    ROUND(prix_m2_2p, 0) AS prix_m2_2_pieces,
    ROUND(prix_m2_3p, 0) AS prix_m2_3_pieces,
    ROUND((prix_m2_3p - prix_m2_2p) * 100.0 / prix_m2_2p, 2) AS ecart_pct
FROM prix_par_taille;
