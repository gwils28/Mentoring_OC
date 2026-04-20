"""Livrable 5 : rapport métier (PDF), généré depuis data/processed/resultats.json — aucun chiffre saisi à la main.

    uv run python scripts/rapport_metier.py

Construit `livrables/rapport_metier.html` puis l'imprime en PDF avec Chrome sans interface. Chaque nombre du texte
passe par la fonction `n()`, qui le note ; à la fin, on vérifie que le texte ne contient aucun autre nombre que ceux-là
(plus quelques constantes de contexte listées dans ALLOWED). Un chiffre tapé à la main fait échouer la génération.
"""

import base64
import html
import json
import re
import shutil
import subprocess
from pathlib import Path

import yaml

PROJECT = Path(__file__).resolve().parents[1]
RESULTS = PROJECT / "data" / "processed" / "resultats.json"
FIGURES = PROJECT / "presentation" / "figures"
OUT = PROJECT / "livrables"
# Nombres de contexte autorisés sans passer par n() : années de la période, numéros de sections et de figures,
# et l'exemple qui explique le rendement relatif (« 1,3 » = 30 % au-dessus de l'habitude)
ALLOWED = {"1990", "2013", "1", "2", "3", "4", "5", "6", "7", "8", "10", "1,3", "30"}

CROPS_FR = {
    "Cassava": "manioc",
    "Maize": "maïs",
    "Plantains and others": "banane plantain",
    "Potatoes": "pomme de terre",
    "Rice, paddy": "riz",
    "Sorghum": "sorgho",
    "Soybeans": "soja",
    "Sweet potatoes": "patate douce",
    "Wheat": "blé",
    "Yams": "igname",
}

registered: set[str] = set()


def n(x: float, decimals: int = 2, pct: bool = False, signed: bool = False) -> str:
    """Formate un nombre à la française et le note comme « issu des résultats »."""
    v = 100 * x if pct else x
    s = f"{v:+.{decimals}f}" if signed else f"{v:.{decimals}f}"
    s = s.replace(".", ",").replace("-", "−")
    if decimals == 0 and abs(v) >= 10_000:  # 15 794 : espace fine insécable entre les milliers
        s = f"{round(v):,}".replace(",", "\u202f")
    registered.add(s.lstrip("+−"))
    return s + (" %" if pct else "")


def img(name: str, width: str = "100%") -> str:
    data = base64.b64encode((FIGURES / f"{name}.png").read_bytes()).decode()
    return f'<img src="data:image/png;base64,{data}" style="width:{width}">'


def build(r: dict) -> str:
    t, rec, sens, ac = r["test"], r["recommandation"], r["sensibilite"], r["analyse_complementaire"]
    d = r["donnees"]
    lo, hi = t["rmse_log_ic95"]
    dlo, dhi = rec["diff_modele_moins_constant_ic95"]
    cv = r["cv"]
    ref = {CROPS_FR[k]: v for k, v in r["reference_t_ha"].items()}
    rf0 = ac["random_forest_depart"]
    search = yaml.safe_load((PROJECT / "config.yaml").read_text(encoding="utf-8"))["search"]
    n_trials = len(search["ridge"]["alpha"]) + 2 * search["n_iter"]

    return f"""
<h1>Choisir une culture avec les données : ce que l'on peut promettre</h1>
<p class="sub">Rapport métier — Agritech Answers · prototype « prédiction et recommandation de cultures »</p>

<div class="box">
<h2 class="nobreak">En bref</h2>
<ul>
<li><b>L'outil estime le rendement moyen national</b> d'une culture dans un pays aux conditions données (température,
pluie, pesticides), avec une erreur typique (médiane) de <b>{n(t["median_rel_error"], 0, pct=True)}</b> sur des pays
qu'il n'a jamais vus. Il ne prédit pas le rendement d'une parcelle.</li>
<li><b>La culture compte plus que tout le reste</b> : une pomme de terre rapporte toujours plus de tonnes qu'un soja.
Les conditions du pays améliorent la prédiction, mais modestement.</li>
<li><b>Le classement des cultures ne fait pas mieux qu'une liste fixe</b>, la même pour tous : il trouve la meilleure
culture dans {n(rec["taux_top1_modele"], 1, pct=True)} des cas, contre {n(rec["taux_top1_constant"], 1, pct=True)}
pour la liste fixe (et {n(rec["taux_top1_hasard"], 1, pct=True)} au hasard). La différence n'est pas significative.</li>
<li><b>Aucune rentabilité n'est calculée</b> : les données ne contiennent ni prix ni coûts.</li>
<li><b>Pour une vraie recommandation</b>, il faut des données à la parcelle (sol, irrigation, intrants par hectare,
météo de l'année) et des prix. Le prototype technique (modèle, API, interface, déploiement automatisé) est prêt à
les accueillir.</li>
</ul>
</div>

<h2>1. Les données disponibles, et leurs pièges</h2>
<p>Deux jeux de données ont été fournis.</p>
<p><b>Le jeu « Agriculture Crop Yield »</b> (un million de lignes) est <b>simulé</b> : toutes les cultures y ont le
même rendement moyen, il contient des rendements négatifs, et une simple formule reproduit l'essentiel des valeurs.
Il n'a ni pays ni année : impossible de le relier à des données réelles. L'analyse en composantes principales (ACP)
demandée le confirme : aucune variable ne résume les autres, elles sont indépendantes. Il dit que la pluie, l'engrais et
l'irrigation augmentent le rendement, mais ce sont les règles de la simulation, pas une observation de terrain.</p>
<p><b>Le jeu « Crop Yield Prediction »</b> rassemble des statistiques officielles (FAO, Banque mondiale) :
rendements de {n(d["cultures"], 0)} cultures dans {n(d["pays"], 0)} pays de 1990 à 2013, avec la température moyenne,
la pluie annuelle et les pesticides utilisés par pays. La table fournie toute prête contenait des lignes en double ;
nous l'avons reconstruite à partir des fichiers d'origine et harmonisé les noms de pays, ce qui a permis de
récupérer de gros producteurs (États-Unis, Russie, Chine) : {n(d["lignes"], 0)} observations au total.</p>
<p class="warn"><b>Point clé :</b> ces conditions sont des <b>moyennes nationales</b>. La pluie est une valeur fixe par
pays, les pesticides sont des tonnes pour tout le pays (un grand pays en utilise beaucoup sans que chaque champ en
reçoive plus). Le modèle ne peut donc parler que de pays, pas de parcelles.</p>

<h2>2. Les variables qui comptent</h2>
{img("fao_rendement_par_culture", "88%")}
<p class="cap">Figure 1 — Le rendement dépend d'abord de la culture (échelle logarithmique).</p>
<ul>
<li><b>La culture</b> fixe l'ordre de grandeur : de {n(ref["sorgho"], 1)} t/ha pour le sorgho à
{n(ref["pomme de terre"], 1)} t/ha pour la pomme de terre (rendements habituels). Ces tonnes ne se comparent pas entre
cultures (une pomme de terre est gorgée d'eau, un grain de sorgho est sec) : pour classer les cultures, l'outil
compare chaque culture à son rendement habituel (« 1,3 » = 30 % au-dessus de l'habitude).</li>
<li><b>Les pesticides du pays</b> sont la condition la plus utile au modèle. Ils reflètent surtout la taille et
l'intensité de l'agriculture du pays (mécanisation, intrants, encadrement). <b>Ce n'est pas un effet des
pesticides</b> : on ne peut pas en conclure qu'en utiliser plus augmenterait le rendement.</li>
<li><b>La température</b> aide aussi ; <b>la pluie</b>, une valeur fixe par pays qui ne dit rien de l'année,
n'apporte presque rien au modèle (ce qui ne veut pas dire qu'elle ne compte pas pour une plante).</li>
</ul>
<p>Sur des pays jamais vus, ajouter les conditions réduit l'erreur d'environ un dixième (de
{n(t["rmse_log_culture_seule"], 2)} à {n(t["rmse_log"], 2)} sur notre échelle d'erreur) : un gain réel mais limité.</p>

<h2>3. Le moteur de prédiction</h2>
<p>Quatre approches ont été comparées, chaque essai étant enregistré dans MLflow, le journal des expériences
(paramètres, scores, versions) : une référence naïve qui donne simplement le rendement habituel de la culture, une
formule linéaire (dite Ridge) et deux familles plus souples, faites de combinaisons d'arbres de décision (forêt
aléatoire, gradient boosting). Les réglages des deux derniers ont été
optimisés automatiquement ({n(n_trials, 0)} essais au total). Toutes les comparaisons se font sur des pays mis de côté :
c'est la situation d'un nouveau client.</p>
{img("cv_modeles", "80%")}
<p class="cap">Figure 2 — Une fois réglés, les trois modèles se valent (erreur sur des pays mis de côté, plus bas = mieux).</p>
<p><b>Ce que les expériences ont appris.</b> Sans réglage, la forêt aléatoire apprend les pays « par cœur » : elle
semble excellente si l'on mélange les années d'un même pays (erreur {n(rf0["cv_aleatoire_rmse_log"], 2)}) mais fait
pire que la référence sur de nouveaux pays ({n(rf0["cv_par_pays_rmse_log"], 2)} contre
{n(cv["baseline"]["moyenne"], 2)}). Le réglage décisif est le nombre minimal d'exemples qu'un arbre doit regrouper avant de
trancher : il l'oblige à généraliser au lieu de retenir chaque pays. Une fois optimisés, les trois modèles sont au coude à coude ({n(cv["random_forest"]["moyenne"], 3)} à
{n(cv["ridge"]["moyenne"], 3)}) : selon la règle fixée à l'avance, nous gardons le plus simple, la régression
linéaire.</p>
<p><b>Résultat final</b>, mesuré une seule fois sur {n(d["pays_test"], 0)} pays jamais vus : la prédiction s'écarte en
général d'environ un tiers du rendement réel (erreur médiane de {n(t["median_rel_error"], 0, pct=True)}), dans un sens
ou dans l'autre. Ce chiffre varie sensiblement selon les pays testés.</p>
<p class="cap" style="text-align:left">Pour les spécialistes : erreur logarithmique (RMSE du log)
{n(t["rmse_log"], 2)}, intervalle de confiance {n(lo, 2)} à {n(hi, 2)}, contre {n(t["reference_mediane"]["rmse_log"], 2)}
pour la référence naïve ; de {n(sens["rmse_log"]["min"], 2)} à {n(sens["rmse_log"]["max"], 2)} sur d'autres tirages de
pays ; facteur typique entre prédiction et réalité {n(t["facteur_typique"], 2)}, inférieur à
{n(t["facteur_exp_rmse"], 1)} dans {n(t["part_dans_facteur_exp_rmse"], 0, pct=True)} des cas.</p>
{img("mlflow_3_comparaison_modeles", "100%")}
<p class="cap">Figure 3 — MLflow : comparaison de la référence et des trois modèles optimisés (paramètres retenus et
scores).</p>
{img("mlflow_2_optimisation", "100%")}
<p class="cap">Figure 4 — MLflow : les essais d'optimisation, triés par erreur.</p>

<h2>4. La recommandation de culture</h2>
<p>Pour savoir si le classement est utile, nous avons regardé, dans chaque pays de test et chaque année, les cultures
réellement pratiquées : la culture classée première par l'outil est-elle celle qui a le mieux réussi ? Nous avons
comparé l'outil au hasard et, surtout, à une <b>liste fixe</b> (toujours le même ordre des cultures).</p>
{img("recommandation_top1", "85%")}
<p class="cap">Figure 5 — Le modèle ne trouve pas la meilleure culture plus souvent qu'une liste fixe.</p>
<ul>
<li>L'outil fait beaucoup mieux que le hasard, mais <b>pas mieux qu'une liste fixe</b> : l'écart
est de {n(100 * rec["diff_modele_moins_constant"], 1)} points, mais vu le petit nombre de pays, l'écart réel pourrait
aller de {n(100 * dlo, 0)} à {n(100 * dhi, 0)} points : on ne peut pas dire qu'il existe. Évalués après coup, les modèles plus flexibles (forêt, gradient boosting) ne font pas mieux de
façon discernable.</li>
<li>Le modèle retenu classe <b>toujours les cultures dans le même ordre</b> : changer les conditions monte ou
descend toutes les cultures ensemble. Seule change la liste des cultures « appuyées par des données » : l'application
relègue en fin de liste une culture qu'aucun pays aux conditions proches ne pratique (l'igname en climat tempéré, par
exemple). Cette règle a été ajoutée après l'évaluation ; testée à titre exploratoire, elle donne
{n(rec["filtre_taux_top1"], 1, pct=True)} de bonne première place, sans différence discernable avec la liste fixe.</li>
<li>Le potentiel existe : choisir à coup sûr la meilleure culture pratiquée rapporterait en moyenne
{n(rec["gain_oracle"], 2)} fois le rendement habituel de plus qu'une culture prise au hasard parmi celles du pays.
L'outil obtient {n(rec["gain_modele"], 2)}, la liste fixe {n(rec["gain_constant"], 2)}. Ce n'est pas un gain
économique.</li>
</ul>
<p class="warn">Ces chiffres ne valent que pour les cultures déjà pratiquées dans chaque pays. Recommander une culture
jamais cultivée dans des conditions semblables n'a pas pu être évalué.</p>

<h2>5. Recommandations</h2>
<p><b>Pour les agriculteurs (ce que l'outil permet de dire aujourd'hui)</b></p>
<ul>
<li>Utiliser la prédiction comme un <b>ordre de grandeur national</b> : « dans un pays comme le vôtre, le blé donne
en moyenne environ X t/ha », avec une erreur typique d'environ {n(t["median_rel_error"], 0, pct=True)} (dans la
moitié des cas, l'écart est plus grand).</li>
<li>Se méfier d'une culture signalée « non appuyée par des données » : personne ne la pratique dans des conditions
proches, la prédiction est une extrapolation.</li>
<li>Ne pas interpréter les pesticides comme un levier : le lien observé reflète le niveau d'équipement des pays.</li>
</ul>
<p><b>Pour Agritech Answers (pour que la recommandation devienne utile)</b></p>
<ul>
<li><b>Collecter des données à la parcelle</b> : sol, irrigation, intrants par hectare, météo de la saison, rendement
obtenu. C'est la condition pour que le classement s'adapte à chaque exploitation.</li>
<li><b>Ajouter les prix</b> (prix producteurs FAO, coûts de production) pour passer du rendement à la rentabilité.</li>
<li><b>Mesurer avant de promettre</b> : garder la règle « l'outil doit battre une liste fixe » comme critère de mise
en service d'un nouveau modèle.</li>
</ul>

<h2>6. Le prototype technique</h2>
<p>Le travail est automatisé de bout en bout : une commande prépare les données, entraîne et compare les modèles
(journal MLflow), puis évalue et sauvegarde le modèle retenu, avec une configuration centralisée. Une API (FastAPI)
(le service qui répond aux demandes de l'application) sert deux fonctions, prédiction et recommandation ; une
interface web (Streamlit) permet de l'interroger sans écrire de code. À chaque modification du code, un automate
(GitHub Actions) lance les tests, construit le paquet logiciel prêt à installer de l'API (une image Docker),
vérifie qu'il répond, puis le publie ; en cas d'échec, rien n'est publié et l'équipe est prévenue.</p>

<h2>7. Limites</h2>
<ul>
<li>Données nationales et annuelles de 1990 à 2013 : niveau technique de cette période, pas de météo de l'année.</li>
<li>Rendement et non profit ; aucune donnée de sol, d'irrigation ni d'engrais réels.</li>
<li>{n(d["pays_test"], 0)} pays de test seulement : les chiffres varient d'un tirage de pays à l'autre (section 3).</li>
<li>Le jeu « Agriculture Crop Yield » est simulé et n'a pas servi au modèle.</li>
</ul>
"""


CSS = """
@page { size: A4; margin: 18mm 16mm; }
body { font-family: "DejaVu Sans", Arial, sans-serif; font-size: 10.5pt; line-height: 1.45; color: #1d1d1b; }
h1 { font-size: 20pt; margin: 0 0 4px; color: #0b0b0b; }
.sub { color: #52514e; margin: 0 0 14px; }
h2 { font-size: 13.5pt; margin: 18px 0 6px; color: #2a78d6; page-break-after: avoid; }
h2.nobreak { margin-top: 0; color: #0b0b0b; }
.box { background: #f1f0eb; border-left: 4px solid #2a78d6; padding: 10px 14px; margin: 8px 0 12px; }
.warn { background: #fdf3e7; border-left: 4px solid #eb6834; padding: 8px 12px; }
img { display: block; margin: 8px auto 2px; page-break-inside: avoid; }
.cap { font-size: 9pt; color: #52514e; text-align: center; margin: 0 0 10px; }
ul { margin: 4px 0 8px 18px; padding: 0; } li { margin: 3px 0; }
"""


def check_numbers(body: str) -> None:
    text = html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r'src="data:[^"]+"', "", body)))
    found = set(re.findall(r"\d{1,3}(?:\u202f\d{3})+|\d+(?:,\d+)?", text))
    unknown = sorted(found - registered - ALLOWED)
    if unknown:
        raise ValueError(f"Nombres du rapport qui ne viennent pas de resultats.json : {unknown}")


def main() -> None:
    r = json.loads(RESULTS.read_text(encoding="utf-8"))
    body = build(r)
    check_numbers(body)
    OUT.mkdir(exist_ok=True)
    page = OUT / "rapport_metier.html"
    page.write_text(f"<!doctype html><html lang='fr'><meta charset='utf-8'><style>{CSS}</style><body>{body}</body></html>",
                    encoding="utf-8")  # fmt: skip
    chrome = shutil.which("google-chrome") or shutil.which("chromium")
    if chrome is None:
        raise SystemExit("Google Chrome ou Chromium introuvable : nécessaire pour imprimer le PDF.")
    pdf = OUT / "rapport_metier.pdf"
    subprocess.run(
        [chrome, "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
         f"--print-to-pdf={pdf}", page.as_uri()],
        check=True, capture_output=True,
    )  # fmt: skip
    print("écrit :", pdf.relative_to(PROJECT), f"({pdf.stat().st_size // 1024} Ko)")


if __name__ == "__main__":
    main()
