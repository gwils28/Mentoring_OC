"""Exporte le SQL et le résultat de chaque besoin pour la présentation : aucun chiffre saisi à la main
dans les diapositives.

Usage : uv run python presentation/export_resultats.py  (puis : cd presentation && npm run build)
"""

import json
from pathlib import Path

from dataimmo.db import DB_PATH, query
from dataimmo.dictionnaire import ENTREES
from dataimmo.io import PROJECT_DIR

REQUETES = PROJECT_DIR / "sql" / "requetes"
SORTIE = Path(__file__).with_name("resultats.json")


def sans_commentaires(sql: str) -> str:
    """Le SQL affiché sur la diapositive : sans les lignes de commentaire, pour tenir dans la place."""
    lignes = [
        ligne.split("--")[0].rstrip() for ligne in sql.splitlines() if not ligne.lstrip().startswith("--")
    ]
    return "\n".join(ligne for ligne in lignes if ligne.strip())


def main() -> None:
    besoins = {}
    for fichier in sorted(REQUETES.glob("*.sql")):
        numero = int(fichier.name[:2])
        sql = fichier.read_text(encoding="utf-8")
        resultat = query(DB_PATH, sql)
        besoins[numero] = {
            "fichier": fichier.name,
            "sql": sans_commentaires(sql),
            "colonnes": list(resultat.columns),
            "lignes": resultat.head(10).astype(object).where(resultat.head(10).notna(), None).values.tolist(),
            "nb_lignes": len(resultat),
        }
    controle = query(
        DB_PATH,
        """
        SELECT 'vente' AS table_, COUNT(*) AS lignes FROM vente UNION ALL SELECT 'bien', COUNT(*) FROM bien
        UNION ALL SELECT 'commune', COUNT(*) FROM commune UNION ALL SELECT 'region', COUNT(*) FROM region""",
    )
    par_mois = query(
        DB_PATH, "SELECT substr(date_vente, 1, 7) AS mois, COUNT(*) AS n FROM vente GROUP BY mois"
    )
    # « Capture de la base » : les premières lignes de chaque table, comme dans SQLite Studio
    apercu = {
        "region": "SELECT * FROM region ORDER BY id_region LIMIT 3",
        "commune": "SELECT * FROM commune ORDER BY id_codedep_codecommune LIMIT 3",
        "bien": "SELECT id_bien, id_codedep_codecommune, no_voie, type_voie, voie, code_postal, type_local,"
        " total_pieces, surface_carrez FROM bien ORDER BY id_bien LIMIT 3",
        "vente": "SELECT * FROM vente ORDER BY id_vente LIMIT 3",
    }
    apercu = {
        table: {
            "colonnes": list(r.columns),
            "lignes": r.astype(object).where(r.notna(), None).values.tolist(),
        }
        for table, r in ((table, query(DB_PATH, sql)) for table, sql in apercu.items())
    }
    donnees = {
        "apercu": apercu,
        "besoins": besoins,
        "controle": controle.values.tolist(),
        "ventes_par_mois": par_mois.values.tolist(),
        "dictionnaire": [
            [e.table, e.code, e.signification, e.type, e.longueur, e.nature, e.regle_gestion]
            for e in ENTREES
            if e.code
            in {
                "id_codedep_codecommune",
                "code_departement",
                "code_postal",
                "valeur_fonciere",
                "date_vente",
                "id_bien",
            }
            and not (e.table == "bien" and e.code == "id_codedep_codecommune")
        ],
    }
    SORTIE.write_text(json.dumps(donnees, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    print("écrit", SORTIE.relative_to(PROJECT_DIR))


if __name__ == "__main__":
    main()
