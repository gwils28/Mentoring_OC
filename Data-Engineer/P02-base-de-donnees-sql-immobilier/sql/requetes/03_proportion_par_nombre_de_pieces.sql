-- Besoin 3 — Proportion des ventes d'appartements par nombre de pièces.
-- Décortiquer : pour chaque nombre de pièces, (ventes de ce nombre de pièces) / (toutes les ventes d'appartements).
-- Le dénominateur est un total : on le calcule une fois dans une sous-requête.
-- Piège : COUNT(*) * 100 / total en entiers donne une division entière ; « 100.0 » force un résultat décimal.
SELECT
    b.total_pieces AS nb_pieces,
    COUNT(*) AS nb_ventes,
    ROUND(COUNT(*) * 100.0 / (
        SELECT COUNT(*)
        FROM vente AS v2
        INNER JOIN bien AS b2 ON b2.id_bien = v2.id_bien
        WHERE b2.type_local = 'Appartement'
    ), 2) AS proportion_pct
FROM vente AS v
INNER JOIN bien AS b ON b.id_bien = v.id_bien
WHERE b.type_local = 'Appartement'
GROUP BY b.total_pieces
ORDER BY b.total_pieces;
-- La modalité « 0 pièce » existe dans la source (30 appartements) : on la garde et on la signale.
