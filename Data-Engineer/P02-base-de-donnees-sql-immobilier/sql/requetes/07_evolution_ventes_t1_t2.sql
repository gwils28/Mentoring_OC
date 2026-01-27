-- Besoin 7 — Taux d'évolution du nombre de ventes entre le 1er et le 2nd trimestre 2020.
-- Décortiquer : compter les ventes du T1 (janv.-mars) et du T2 (avril-juin), puis (T2 - T1) / T1.
-- Une CTE (WITH) calcule les deux comptes ; la requête finale fait le calcul. Toutes les ventes sont comptées.
WITH ventes_par_trimestre AS (
    SELECT
        SUM(CASE WHEN date_vente BETWEEN '2020-01-01' AND '2020-03-31' THEN 1 ELSE 0 END) AS nb_t1,
        SUM(CASE WHEN date_vente BETWEEN '2020-04-01' AND '2020-06-30' THEN 1 ELSE 0 END) AS nb_t2
    FROM vente
)
SELECT
    nb_t1,
    nb_t2,
    ROUND((nb_t2 - nb_t1) * 100.0 / nb_t1, 2) AS evolution_pct
FROM ventes_par_trimestre;
