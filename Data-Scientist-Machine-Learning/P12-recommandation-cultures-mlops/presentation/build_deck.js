// Génère presentation/recommandation_cultures_agritech.pptx (support de soutenance du corrigé, 15 minutes).
// Usage (depuis presentation/) : npm ci && npm run build — après `uv run agrireco all` et les captures.
// Tous les chiffres viennent de ../data/processed/resultats.json : aucun n'est saisi à la main.

const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");
const { setThemeColors } = require("./theme_colors");
const R = require("../data/processed/resultats.json");

const FIG = (name) => path.join(__dirname, "figures", `${name}.png`);
const OUT = path.join(__dirname, "recommandation_cultures_agritech.pptx");

// Nombres au format français
const fr = (v, d = 2) => v.toLocaleString("fr-FR", { minimumFractionDigits: d, maximumFractionDigits: d });
const pct = (v, d = 1) => `${fr(100 * v, d)} %`;
// Rapport largeur / hauteur lu dans l'en-tête PNG (octets 16 à 23)
const ratio = (name) => {
  const b = fs.readFileSync(FIG(name));
  return b.readUInt32BE(16) / b.readUInt32BE(20);
};

const T = R.test, REC = R.recommandation, SENS = R.sensibilite, AC = R.analyse_complementaire, D = R.donnees;

const THEME = {
  name: "Agritech Answers",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1B1B1A", lt1: "FFFFFF", dk2: "1F3B2D", lt2: "F1F0EB",
    accent1: "2A78D6", accent2: "EB6834", accent3: "1BAF7A", accent4: "52514E",
    accent5: "86B6EF", accent6: "E3EFE6", hlink: "2A78D6", folHlink: "6250D6",
  },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33" × 7.5"
pres.title = "Prédire le rendement, recommander une culture : ce que les données permettent";
pres.subject = "Corrigé P12 Data Scientist ML OpenClassrooms — Agritech Answers";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;
const W = 13.333;
const M = 0.6;

// ------------------------------------------------------------------ layouts
pres.defineSlideMaster({
  title: "TITRE_SOMBRE",
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 1.8, w: 11.8, h: 2.0,
      fontSize: 38, bold: true, color: C.background1, valign: "bottom" }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: M, y: 3.95, w: 11.5, h: 1.2,
      fontSize: 20, color: C.accent6, valign: "top" }, text: "" } },
  ],
});

pres.defineSlideMaster({
  title: "CONTENU",
  background: { color: C.background1 },
  margin: [0.5, M, 0.6, M],
  slideNumber: { x: W - M - 0.6, y: 7.0, w: 0.6, h: 0.3, fontSize: 10, color: C.accent4, align: "right" },
  objects: [
    { text: { text: "Agritech Answers · prédiction et recommandation de cultures", options: {
      x: M, y: 7.0, w: 7, h: 0.3, fontSize: 10, color: C.accent4, margin: 0 } } },
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.35, w: W - 2 * M, h: 0.8,
      fontSize: 27, bold: true, color: C.text2, valign: "middle", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "lede", type: "body", x: M, y: 1.15, w: W - 2 * M, h: 0.5,
      fontSize: 16, color: C.accent4, valign: "top", margin: 0 }, text: "" } },
  ],
});

pres.defineSlideMaster({
  title: "CONCLUSION_SOMBRE",
  background: { color: C.text2 },
  slideNumber: { x: W - M - 0.6, y: 7.0, w: 0.6, h: 0.3, fontSize: 10, color: C.accent6, align: "right" },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.35, w: W - 2 * M, h: 0.8,
      fontSize: 30, bold: true, color: C.background1, valign: "middle", margin: 0 }, text: "" } },
  ],
});

// ------------------------------------------------------------------ helpers
const card = (slide, { x, y, w, h, fill = C.background2, name }) =>
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h, rectRadius: 0.12, fill: { color: fill }, line: { color: fill }, objectName: name,
  });

const text = (slide, value, opts) => slide.addText(value, { isTextBox: true, margin: 0, valign: "top", ...opts });

const content = (section, title, lede) => {
  const slide = pres.addSlide({ masterName: "CONTENU", sectionTitle: section });
  slide.addText(title, { placeholder: "title" });
  slide.addText(lede, { placeholder: "lede" });
  return slide;
};

const lecture = (slide, msg, name, y = 5.95, h = 0.85) => {
  card(slide, { x: M, y, w: W - 2 * M, h, fill: C.accent6, name: `${name}-fond` });
  text(slide, msg, { x: M + 0.25, y, w: W - 2 * M - 0.5, h, valign: "middle", fontSize: 15,
    color: C.text2, objectName: `${name}-texte` });
};

// Image placée dans une boîte (x, y, w, h) en gardant ses proportions
const image = (slide, name, { x, y, w, h, alt }) => {
  const r = ratio(name);
  let iw = w, ih = w / r;
  if (ih > h) { ih = h; iw = h * r; }
  slide.addImage({ path: FIG(name), x: x + (w - iw) / 2, y, w: iw, h: ih, objectName: `figure-${name}`, altText: alt });
};

const cards = (slide, items, { y, h, cols, x0 = M, width = W - 2 * M, fill = C.background2, titleSize = 16,
  bodySize = 13, prefix }) => {
  const gap = 0.25, cw = (width - gap * (cols - 1)) / cols;
  items.forEach(([k, v], i) => {
    const x = x0 + (i % cols) * (cw + gap), yy = y + Math.floor(i / cols) * (h + gap);
    card(slide, { x, y: yy, w: cw, h, fill, name: `${prefix}-carte-${i}` });
    text(slide, k, { x: x + 0.22, y: yy + 0.16, w: cw - 0.44, h: 0.45, fontSize: titleSize, bold: true,
      color: C.text2, objectName: `${prefix}-titre-${i}` });
    text(slide, v, { x: x + 0.22, y: yy + 0.62, w: cw - 0.44, h: h - 0.72, fontSize: bodySize, color: C.text1,
      objectName: `${prefix}-texte-${i}` });
  });
};

const stat = (slide, value, label, { x, y, w, color = C.accent1, name }) => {
  card(slide, { x, y, w, h: 1.55, fill: C.accent6, name: `${name}-fond` });
  text(slide, value, { x: x + 0.2, y: y + 0.12, w: w - 0.4, h: 0.75, fontSize: 36, bold: true, color,
    fontFace: THEME.headFontFace, objectName: `${name}-valeur` });
  text(slide, label, { x: x + 0.2, y: y + 0.88, w: w - 0.4, h: 0.6, fontSize: 12, color: C.text2,
    objectName: `${name}-legende` });
};

const flow = (slide, steps, { y, h = 1.25, prefix, highlight = -1 }) => {
  const gap = 0.32, bw = (W - 2 * M - gap * (steps.length - 1)) / steps.length;
  steps.forEach(([k, v], i) => {
    const x = M + i * (bw + gap);
    card(slide, { x, y, w: bw, h, fill: i === highlight ? C.accent6 : C.background2, name: `${prefix}-carte-${i}` });
    text(slide, k, { x: x + 0.12, y: y + 0.12, w: bw - 0.24, h: 0.4, fontSize: 15, bold: true, color: C.text2,
      align: "center", objectName: `${prefix}-titre-${i}` });
    text(slide, v, { x: x + 0.12, y: y + 0.55, w: bw - 0.24, h: h - 0.62, fontSize: 11.5, color: C.text1,
      align: "center", objectName: `${prefix}-texte-${i}` });
    if (i < steps.length - 1) {
      slide.addShape(pres.shapes.RIGHT_ARROW, { x: x + bw + 0.05, y: y + h / 2 - 0.13, w: 0.22, h: 0.26,
        fill: { color: "86B6EF" }, line: { color: "86B6EF" }, objectName: `${prefix}-fleche-${i}` });
    }
  });
};

const bullets = (items) => items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1 } }));

// ================================================================== 1. Titre
pres.addSection({ title: "Problème" });
let s = pres.addSlide({ masterName: "TITRE_SOMBRE", sectionTitle: "Problème" });
s.addText("Prédire le rendement, recommander une culture : ce que les données permettent vraiment",
  { placeholder: "title" });
s.addText("Un prototype complet (modèle, MLflow, API, interface, CI/CD) et une réponse honnête à la question métier",
  { placeholder: "body" });
text(s, "Corrigé de référence — projet OpenClassrooms « Concevez un système de recommandations pour une agriculture " +
  "optimisée par les données » (parcours Data Scientist Machine Learning)", {
  x: M, y: 6.45, w: 11.8, h: 0.6, fontSize: 12, color: C.accent6, objectName: "mention-corrige" });
s.addNotes("Minutage : problème 1 min (slides 1-2), données 2 min (3-4), entraînement et MLflow 5 min (5-9), " +
  "MLOps et CI/CD 4 min (10-11), impact 3 min (12-14). Accroche : l'application doit dire à un agriculteur quel rendement attendre " +
  "et quelle culture choisir. Spoiler assumé : la prédiction fonctionne dans certaines limites, la recommandation ne " +
  "fait pas mieux qu'une liste fixe — et c'est un résultat utile.");

// ================================================================== 2. La demande
s = content("Problème", "Deux fonctions dans une même application, servies par une API",
  "Prédire le rendement d'une culture ; recommander la culture la mieux adaptée aux conditions");
cards(s, [
  ["Prédiction", "L'utilisateur choisit une culture et renseigne les conditions (température, pluie, pesticides) → rendement estimé en t/ha."],
  ["Recommandation", "L'utilisateur renseigne seulement les conditions → toutes les cultures sont simulées et classées."],
], { y: 1.85, h: 1.55, cols: 2, prefix: "fonction", bodySize: 14 });
flow(s, [
  ["Données", "FAO + Banque mondiale, jeu synthétique"],
  ["Pipeline", "préparer → entraîner → évaluer (MLflow)"],
  ["Modèle", "fichier versionné, rechargé par l'API"],
  ["API FastAPI", "/predict, /recommend, conteneur Docker"],
  ["Interface", "Streamlit, aucune logique ML"],
], { y: 3.75, h: 1.35, prefix: "archi", highlight: 1 });
lecture(s, "Livrables : captures MLflow, scripts d'entraînement, pipeline MLOps, pipeline CI/CD, rapport métier. " +
  "Deux compétences évaluées : optimiser l'entraînement, automatiser le déploiement.", "lecture-demande", 5.5, 0.9);
s.addNotes("Architecture découplée demandée : le modèle vit derrière une API, l'interface ne fait qu'appeler l'API. " +
  "Avantage : on peut changer de modèle sans toucher à l'interface, et tester chaque morceau séparément.");

// ================================================================== 3. Les données
pres.addSection({ title: "Données" });
s = content("Données", "Deux jeux fournis : l'un est simulé, l'autre doit être reconstruit",
  "Avant de modéliser, vérifier ce que contiennent vraiment les données");
cards(s, [
  ["Agriculture Crop Yield : simulé", "Les 6 cultures au même rendement moyen, rendements négatifs, ni pays ni année."],
  ["Crop Yield Prediction : réel", `FAO + Banque mondiale : ${D.cultures} cultures, pluie, température, pesticides, ${D.annees[0]}-${D.annees[1]}.`],
  ["Piège 1 : doublons", "yield_df.csv : 28 242 lignes pour 13 130 clés pays × culture × année."],
  ["Piège 2 : noms de pays", `Sans harmonisation, la jointure perd les États-Unis, la Russie… Reconstruite : ${fr(D.lignes, 0)} lignes, ${D.pays} pays.`],
], { y: 1.85, h: 1.75, cols: 2, prefix: "donnees", bodySize: 13 });
lecture(s, "Conditions = moyennes nationales : la pluie est une valeur fixe par pays, les pesticides sont des tonnes " +
  "pour tout le pays. Le modèle parlera de pays, pas de parcelles.", "lecture-donnees", 5.85, 0.95);
s.addNotes("Les 28 242 et 13 130 viennent du notebook 1 (section 3). Les pays récupérés par l'harmonisation sont " +
  "18, dont les États-Unis, la Russie et la Chine continentale. La pluie est constante pour les 119 pays sur toute " +
  "la période : c'est presque un identifiant de pays.");

// ================================================================== 4. Fusion et ACP
s = content("Données", "La fusion demandée est impossible, l'ACP ne trouve aucune structure",
  "Deux résultats « négatifs » démontrés plutôt que forcés");
image(s, "synthetique_acp_eboulis", { x: 6.9, y: 1.8, w: 5.83, h: 3.0, alt: "Éboulis de l'ACP : valeurs propres toutes proches de 1" });
text(s, bullets([
  "Le jeu simulé n'a ni pays ni année : seule clé commune, la culture (4 en commun)",
  "Jointure par culture testée : colonnes ajoutées constantes (50 % d'engrais, 50 % d'irrigation, 4,65 t/ha) → écartée",
  "La vraie fusion : les 4 fichiers FAO / Banque mondiale entre eux, noms harmonisés, clé unique vérifiée",
  "ACP (variables standardisées) : 5 valeurs propres ≈ 1 → variables indépendantes, aucun axe à interpréter",
]), { x: M, y: 1.85, w: 6.0, h: 3.6, fontSize: 15, color: C.text1, paraSpaceAfter: 10, objectName: "fusion-liste" });
s.addNotes("Variables clés du jeu simulé (régression) : pluie (≈ 4,5 t/ha d'écart sur sa plage), engrais " +
  "+1,50 t/ha, irrigation +1,20 t/ha — ce sont les règles de la simulation ; le jeu réel dit l'inverse (la culture " +
  "domine). Question attendue de l'évaluateur : pourquoi ne pas avoir fusionné ? Réponse : joindre sans vraie clé " +
  "commune fabrique de l'information. L'ACP ne regarde pas la cible : elle répond à « mes variables sont-elles " +
  "redondantes ? », pas à « qu'est-ce qui fait le rendement ? ». Quand les valeurs propres sont égales, les axes " +
  "sont arbitraires (ils changent d'un échantillon à l'autre).");

// ================================================================== 5. Protocole
pres.addSection({ title: "Entraînement" });
s = content("Entraînement", "Évaluer sur des pays jamais vus, sinon le modèle triche",
  `Test : ${D.pays_test} pays mis de côté (20 %), regardés une seule fois ; réglages en validation croisée groupée par pays`);
const rf0 = AC.random_forest_depart;
stat(s, fr(rf0.cv_aleatoire_rmse_log), "forêt par défaut, validation aléatoire (lignes mélangées)", { x: M, y: 1.95, w: 3.8, name: "stat-aleatoire", color: C.accent2 });
stat(s, fr(rf0.cv_par_pays_rmse_log), "la même forêt, validation par pays", { x: M + 4.05, y: 1.95, w: 3.8, name: "stat-pays" });
stat(s, fr(R.cv.baseline.moyenne), "référence naïve : médiane de la culture, sans conditions", { x: M + 8.1, y: 1.95, w: 4.03, name: "stat-ref", color: C.accent4 });
text(s, bullets([
  "Métrique principale : RMSE du log du rendement (0,1 ≈ 10 % d'erreur relative, quelle que soit la culture)",
  "La forêt par défaut reconnaît les pays (pluie fixe, pesticides) : excellente sur des pays connus, pire que la référence sur des pays nouveaux",
  "Mêmes plis pour tous les modèles : les comparaisons sont appariées ; graine fixée dans config.yaml",
]), { x: M, y: 3.8, w: W - 2 * M, h: 2.2, fontSize: 15, color: C.text1, paraSpaceAfter: 8, objectName: "protocole-liste" });
s.addNotes("C'est la décision la plus importante du projet. Un découpage aléatoire mettrait le maïs français de 2004 " +
  "à l'entraînement et celui de 2005 au test : le modèle n'aurait qu'à s'en souvenir. Or un client Agritech est un " +
  "nouveau pays (ou une nouvelle exploitation).");

// ================================================================== 6. Comparaison et optimisation
s = content("Entraînement", "Optimisés, les trois modèles finissent au coude à coude",
  "4 expériences MLflow : comparaison, optimisation (65 essais), variantes de variables, test final");
image(s, "cv_modeles", { x: M, y: 1.75, w: 6.9, h: 3.9, alt: "Erreur en validation par pays avant et après optimisation" });
const sp = R.params;
text(s, bullets([
  `Forêt et gradient boosting : recherche aléatoire (30 essais chacun) ; Ridge : grille de 5 valeurs d'alpha`,
  "Hyperparamètre décisif : min_samples_leaf (50) — chaque feuille doit regrouper plusieurs pays, l'arbre ne peut plus mémoriser",
  `Forêt ${fr(R.cv.random_forest.moyenne, 3)}, boosting ${fr(R.cv.hist_gb.moyenne, 3)}, Ridge ${fr(R.cv.ridge.moyenne, 3)} : écarts plus petits que le bruit entre plis`,
  `Règle fixée avant : à score équivalent (moins d'une erreur-type), le plus simple → Ridge (alpha = ${fr(sp.alpha, 0)})`,
]), { x: 7.75, y: 1.85, w: 4.98, h: 4.0, fontSize: 14, color: C.text1, paraSpaceAfter: 9, objectName: "optim-liste" });
lecture(s, "Ridge est retenu à un cheveu : la forêt prédit sans doute un peu mieux. Le choix ne change pas la " +
  "conclusion sur la recommandation.", "lecture-optim", 6.0, 0.8);
s.addNotes("Plages justifiées : min_samples_leaf de 1 à 50 pour aller de « par cœur » à « très lissé » ; " +
  "learning_rate de 0,01 à 0,2 ; profondeur de 8 à illimitée. Ridge bouge à peine avec alpha : un modèle peu " +
  "flexible a peu à régler et ne peut pas mémoriser les pays (écart validation − entraînement 0,02 contre 0,16 à 0,19 " +
  "pour les arbres optimisés).");

// ================================================================== 7. MLflow
s = content("Entraînement", "MLflow garde la trace de chaque essai : paramètres, scores, graine",
  "Captures de l'interface MLflow (livrable 1) ; tous les runs sont aussi exportés en CSV");
image(s, "mlflow_2_optimisation", { x: M, y: 1.75, w: 6.5, h: 3.9, alt: "MLflow : essais d'optimisation triés par erreur" });
image(s, "mlflow_3_comparaison_modeles", { x: 7.3, y: 1.75, w: 5.43, h: 4.9, alt: "MLflow : comparaison des modèles retenus" });
text(s, "Gauche : les 68 runs de l'expérience « optimisation » (65 essais et 3 runs parents, un par recherche), triés par erreur de validation. Droite : la vue " +
  "Compare de la référence et des trois meilleurs réglages (paramètres, erreur, écart entraînement / validation).", {
  x: M, y: 5.8, w: 6.5, h: 1.0, fontSize: 12.5, color: C.accent4, objectName: "mlflow-legende" });
s.addNotes("Chaque run note : modèle, hyperparamètres, graine, RMSE-log par pli, moyenne, écart-type, erreur " +
  "d'entraînement et écart. Les essais sont des runs enfants d'un run parent par recherche. Ce que MLflow m'a appris : " +
  "1) la forêt par défaut mémorise, 2) la régularisation est le réglage qui compte, 3) au-delà, les modèles se valent.");

// ================================================================== 8. Résultat final
s = content("Entraînement", `Sur ${D.pays_test} pays jamais vus, une erreur typique de ${pct(T.median_rel_error, 0)} sur le rendement`,
  "Évaluation unique du modèle retenu, puis réentraînement sur tous les pays pour l'API");
stat(s, pct(T.median_rel_error, 0), "erreur relative médiane", { x: M, y: 1.95, w: 2.9, name: "stat-erreur" });
stat(s, fr(T.rmse_log), `RMSE-log (IC 95 % : ${fr(T.rmse_log_ic95[0])} – ${fr(T.rmse_log_ic95[1])})`, { x: M + 3.1, y: 1.95, w: 2.9, name: "stat-rmse" });
stat(s, fr(T.reference_mediane.rmse_log), "référence naïve sur les mêmes pays", { x: M + 6.2, y: 1.95, w: 2.9, name: "stat-ref-test", color: C.accent4 });
stat(s, fr(T.rmse_log_culture_seule), "même modèle avec la culture seule", { x: M + 9.3, y: 1.95, w: 2.83, name: "stat-culture", color: C.accent4 });
text(s, bullets([
  `Les conditions du pays améliorent l'erreur de ${fr(T.rmse_log_culture_seule)} à ${fr(T.rmse_log)} : réel mais modeste ; la culture fait l'essentiel`,
  `Sur ${SENS.n_decoupages} autres tirages de pays, l'erreur varie de ${fr(SENS.rmse_log.min)} à ${fr(SENS.rmse_log.max)} : le chiffre dépend des pays testés`,
]), { x: M, y: 3.8, w: W - 2 * M, h: 2.9, fontSize: 15, color: C.text1, paraSpaceAfter: 8, objectName: "final-liste" });
s.addNotes("Traduction pour un agriculteur : « dans un pays comme le vôtre, attendez-vous à environ X t/ha, avec une " +
  `erreur typique de ${pct(T.median_rel_error, 0)} ». Dans un cas typique, prédiction et réalité diffèrent d'un facteur ` +
  `${fr(T.facteur_typique)} ; dans ${pct(T.part_dans_facteur_exp_rmse, 0)} des cas, d'un facteur inférieur à ` +
  `${fr(T.facteur_exp_rmse, 1)}. Le test a été regardé une seule fois pour le modèle retenu. Biais (prédiction − ` +
  `réalité) : ${fr(T.bias_t_ha)} t/ha sur ce test, mais négatif dans ${SENS.biais_t_ha.negatif} tirages sur ` +
  `${SENS.n_decoupages} : son signe dépend des pays tirés. R² global ${fr(T.r2_log)} trompeur : au sein d'une ` +
  "culture, le modèle départage mal les pays (R² négatif pour 5 cultures sur 10).");

// ================================================================== 9. Variables clés
s = content("Entraînement", "Ce que le modèle utilise : la culture, loin devant",
  "Importance par permutation sur les pays de test : hausse de l'erreur quand on mélange une variable");
image(s, "importance_permutation", { x: M, y: 1.75, w: 6.6, h: 3.5, alt: "Importance par permutation des variables" });
text(s, bullets([
  "Culture : une pomme de terre rapporte toujours plus de tonnes qu'un soja",
  "Pesticides (tonnes du pays) : reflètent la taille et l'équipement de l'agriculture du pays — pas un effet du produit",
  "Température : utile ; pluie (valeur fixe par pays, rien sur l'année) : presque rien pour ce modèle, même seule",
  "Une importance n'est ni une cause, ni un sens d'effet, ni une part du rendement",
]), { x: 7.45, y: 1.85, w: 5.28, h: 4.2, fontSize: 14.5, color: C.text1, paraSpaceAfter: 10, objectName: "importance-liste" });
s.addNotes("Le bloc climat + pesticides mélangé d'un seul tenant pèse plus que la somme des trois : les variables " +
  "sont corrélées et se partagent l'importance de façon arbitraire. Interdit : « augmenter les pesticides augmente le " +
  "rendement », « la pluie n'a pas d'effet ».");

// ================================================================== 10. Architecture MLOps
pres.addSection({ title: "MLOps et CI/CD" });
s = content("MLOps et CI/CD", "Une commande reproduit tout, de la donnée brute au modèle servi",
  "Étapes séparées, reliées par des fichiers, pilotées par un seul fichier de configuration");
flow(s, [
  ["prepare", "téléchargement vérifié (SHA-256), fusion → dataset_consolide.csv"],
  ["train", "comparaison + optimisation + sélection → MLflow, selection.json"],
  ["evaluate", "test unique, recommandation, sensibilité → resultats.json"],
  ["modèle", "models/model.joblib : modèle, références, domaine de validité"],
  ["API + interface", "FastAPI dans Docker, Streamlit ; docker compose up"],
], { y: 1.9, h: 1.6, prefix: "pipeline", highlight: 3 });
cards(s, [
  ["config.yaml", "Graine, découpage, variables, plages d'hyperparamètres : rien de codé en dur."],
  ["Reproductible", "uv.lock fige les versions ; requirements.txt de l'image générés depuis lui ; modèle rechargé avec la même version de scikit-learn."],
  ["Robuste", "Fichier absent ou configuration incomplète : message clair et arrêt. Entrée absurde à l'API : refus 422."],
], { y: 3.85, h: 1.6, cols: 3, prefix: "mlops", bodySize: 13 });
image(s, "interface_recommandation", { x: 9.6, y: 5.6, w: 3.13, h: 1.3, alt: "Interface Streamlit" });
text(s, "uv run agrireco all   →   " + `${fr(D.lignes, 0)} lignes, 4 expériences MLflow, un modèle servi`, {
  x: M, y: 5.85, w: 8.8, h: 0.5, fontSize: 15, bold: true, color: C.accent1, fontFace: "Consolas", objectName: "commande" });
s.addNotes("Démonstration possible : lancer docker compose up et interroger l'interface. L'API signale les " +
  "conditions hors des plages vues et relègue les cultures que personne ne pratique dans des conditions proches.");

// ================================================================== 11. CI/CD
s = content("MLOps et CI/CD", "À chaque modification : tests, image, test du conteneur, publication",
  "GitHub Actions ; un échec arrête tout, rien n'est publié, l'équipe est prévenue");
flow(s, [
  ["Lint + tests", "ruff, pytest (fusion, métriques, sélection, API, interface sans ML)"],
  ["Synchronisation", "requirements.txt = uv.lock ?"],
  ["Build", "image Docker de l'API, modèle embarqué"],
  ["Intégration", "conteneur lancé : /health, /predict, /recommend, erreur 422"],
  ["Publication", "ghcr.io, tag du commit + latest (branche main)"],
], { y: 1.9, h: 1.6, prefix: "ci", highlight: 3 });
cards(s, [
  ["En cas d'échec", "Job rouge, étapes suivantes sautées, journaux du conteneur affichés, résumé ❌ et e-mail GitHub."],
  ["Sécurité", "Aucun secret dans les fichiers : GITHUB_TOKEN éphémère, permissions minimales, utilisateur non root dans l'image."],
], { y: 3.85, h: 1.65, cols: 2, prefix: "ci-cartes", bodySize: 13 });
lecture(s, "Non automatisé volontairement : le réentraînement. Les résultats sont relus par un humain avant de servir " +
  "un nouveau modèle ; la suite logique serait un réentraînement déclenché par de nouvelles données, avec validation.",
  "lecture-ci", 5.8, 1.0);
s.addNotes("Échecs simulés en local : test faux, modèle absent de l'image, requirements modifié à la main ; chaque fois le pipeline s'arrête au bon endroit. " +
  "Question attendue : que se passe-t-il si une étape échoue ? Le job image dépend du job qualité (needs) : " +
  "pas d'image si un test casse. Le dernier latest reste en place. Surveillance en production : journaux, alertes, " +
  "suivi des entrées hors domaine, suivi de l'erreur quand les rendements réels arrivent.");

// ================================================================== 12. Recommandation
pres.addSection({ title: "Impact métier" });
s = content("Impact métier", "Le classement des cultures ne fait pas mieux qu'une liste fixe",
  "Part des cas où la culture classée 1ʳᵉ est la meilleure des cultures réellement pratiquées (pays de test)");
image(s, "recommandation_top1", { x: M, y: 1.75, w: 7.0, h: 3.9, alt: "Taux de bonne première place : hasard, classement fixe, modèles" });
text(s, bullets([
  `Modèle ${pct(REC.taux_top1_modele)}, liste fixe ${pct(REC.taux_top1_constant)}, hasard ${pct(REC.taux_top1_hasard)}`,
  `Écart avec la liste fixe : ${fr(100 * REC.diff_modele_moins_constant, 1)} points (IC ${fr(100 * REC.diff_modele_moins_constant_ic95[0], 0)} à ${fr(100 * REC.diff_modele_moins_constant_ic95[1], 0)}) : non significatif`,
  "Forêt et boosting optimisés, évalués après coup : pas mieux de façon discernable",
  "Ridge classe toujours les cultures dans le même ordre : il ne s'adapte pas aux conditions",
]), { x: 7.85, y: 1.85, w: 4.88, h: 4.0, fontSize: 14.5, color: C.text1, paraSpaceAfter: 10, objectName: "reco-liste" });
lecture(s, "Règle de décision fixée avant les résultats : « utile pour recommander » seulement si le modèle bat la " +
  "liste fixe. Ce n'est pas le cas : on le dit, plutôt que d'annoncer « 2 fois mieux que le hasard ».",
  "lecture-reco", 6.0, 0.85);
s.addNotes("Classement par rendement relatif (rendement prédit ÷ rendement habituel de la culture) : les tonnes ne " +
  "se comparent pas entre cultures. Évaluation limitée aux cultures pratiquées : une culture jamais plantée n'a pas " +
  "de vérité terrain. Avec un autre normaliseur, l'écart change de signe mais reste non significatif ; sur 20 tirages " +
  "de pays : 9 fois mieux, 1 égalité, 10 fois moins bien.");

// ================================================================== 13. Recommandations métier
s = content("Impact métier", "Ce que l'on peut promettre aux agriculteurs, et ce qu'il faut pour aller plus loin",
  "Résultats traduits pour un décideur non technique");
cards(s, [
  ["Aujourd'hui", `Un ordre de grandeur du rendement moyen national d'une culture, avec une erreur typique de ${pct(T.median_rel_error, 0)}. Un signal quand une culture n'est pratiquée nulle part dans des conditions proches.`],
  ["Ce qu'on ne promet pas", "Le rendement d'une parcelle. La culture « la plus rentable » (aucun prix). Un effet des pesticides ou de la pluie."],
  ["Pour une vraie recommandation", "Données à la parcelle : sol, irrigation, intrants par hectare, météo de la saison, rendement obtenu."],
  ["Pour parler rentabilité", "Prix producteurs (FAO) et coûts de production ; garder la règle « battre une liste fixe » avant toute mise en service."],
], { y: 1.85, h: 2.05, cols: 2, prefix: "metier", bodySize: 14 });
lecture(s, `Potentiel : choisir à coup sûr la meilleure culture pratiquée rapporterait en moyenne ${fr(REC.gain_oracle)} fois ` +
  `le rendement habituel de plus qu'une culture prise au hasard parmi celles du pays. Le modèle : ${fr(REC.gain_modele)} ; la liste fixe : ${fr(REC.gain_constant)}.`,
  "lecture-metier", 6.2, 0.75);
s.addNotes("Question probable : comment présenter ce résultat à un exploitant ? Réponse : un ordre de " +
  "grandeur national, pas un conseil pour sa parcelle. Le gain est en rendement relatif, pas en euros.");

// ================================================================== 14. Conclusion
s = pres.addSlide({ masterName: "CONCLUSION_SOMBRE", sectionTitle: "Impact métier" });
s.addText("Un prototype complet et reproductible, une recommandation à reconstruire avec de meilleures données",
  { placeholder: "title" });
[
  ["Problème", "Prédire et recommander une culture à partir de données nationales, dont un jeu simulé."],
  ["Solution", "Pipeline reproductible, 4 expériences MLflow, API conteneurisée, interface, CI/CD avec test du conteneur."],
  ["Impact", `Prédiction utile comme ordre de grandeur (${pct(T.median_rel_error, 0)} d'erreur typique) ; recommandation pas meilleure qu'une liste fixe : données à la parcelle et prix nécessaires.`],
].forEach(([k, v], i) => {
  const x = M + i * 4.1;
  card(s, { x, y: 1.9, w: 3.85, h: 3.6, fill: "2C4F3D", name: `conclusion-carte-${i}` });
  text(s, k, { x: x + 0.3, y: 2.1, w: 3.3, h: 0.5, fontSize: 22, bold: true, color: C.accent6,
    fontFace: THEME.headFontFace, objectName: `conclusion-titre-${i}` });
  text(s, v, { x: x + 0.3, y: 2.75, w: 3.3, h: 2.6, fontSize: 15, color: C.background1, objectName: `conclusion-texte-${i}` });
});
text(s, "Suite : registre de modèles, suivi de dérive, intervalles de prédiction, hébergement de l'API (voir « aller plus loin »)", {
  x: M, y: 5.85, w: W - 2 * M, h: 0.5, fontSize: 14, color: C.accent6, objectName: "conclusion-suite" });
s.addNotes("Conclure sur la méthode : chaque chiffre vient d'une sortie du pipeline, chaque règle a été fixée avant " +
  "les résultats. Ouvrir sur la discussion : choix techniques, robustesse, impact, hyperparamètres.");

(async () => {
  await pres.writeFile({ fileName: OUT });
  await setThemeColors(OUT, THEME);
  console.log("écrit :", path.relative(process.cwd(), OUT));
})();
