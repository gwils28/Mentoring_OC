-- Besoin 1 — Nombre total d'appartements vendus au 1er semestre 2020.
-- Décortiquer : compter (COUNT) des ventes, filtrer le type de bien (Appartement) et la période (janv.-juin 2020).
-- Le type de bien est dans « bien », la date dans « vente » : une jointure est nécessaire.
SELECT
    COUNT(*) AS nb_appartements_vendus
FROM vente AS v
INNER JOIN bien AS b ON b.id_bien = v.id_bien
WHERE b.type_local = 'Appartement'
  AND v.date_vente BETWEEN '2020-01-01' AND '2020-06-30';
