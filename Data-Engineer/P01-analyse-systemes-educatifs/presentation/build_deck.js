// Génère presentation/academy_expansion_edstats.pptx (livrable 2 du corrigé).
// Usage : cd presentation && npm ci && node build_deck.js
// Les chiffres viennent du notebook corrigé (notebooks/projet_edstats_corrige.ipynb) : les mettre à jour ensemble.

const path = require("path");
const pptxgen = require("pptxgenjs");
const { setThemeColors } = require("./theme_colors");

const FIG = (name) => path.join(__dirname, "figures", `${name}.png`);
const OUT = path.join(__dirname, "academy_expansion_edstats.pptx");

const THEME = {
  name: "academy EdStats",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1B1B1A", lt1: "FFFFFF", dk2: "123049", lt2: "EEF3F8",
    accent1: "2A78D6", accent2: "EB6834", accent3: "1BAF7A", accent4: "52514E",
    accent5: "86B6EF", accent6: "C9D9EA", hlink: "2A78D6", folHlink: "6250D6",
  },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33" × 7.5"
pres.title = "Où academy doit-elle s'implanter ?";
pres.subject = "Analyse exploratoire EdStats — corrigé P01 OpenClassrooms";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;
const W = 13.333;
const M = 0.6; // marge

// ------------------------------------------------------------------ layouts
pres.defineSlideMaster({
  title: "TITRE_SOMBRE",
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 2.2, w: 11.5, h: 1.6,
      fontSize: 44, bold: true, color: C.background1, valign: "bottom" }, text: "" } },
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
    { text: { text: "academy · Analyse des données EdStats", options: {
      x: M, y: 7.0, w: 6, h: 0.3, fontSize: 10, color: C.accent4, margin: 0 } } },
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.35, w: W - 2 * M, h: 0.8,
      fontSize: 36, bold: true, color: C.text2, valign: "middle", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "lede", type: "body", x: M, y: 1.15, w: W - 2 * M, h: 0.55,
      fontSize: 18, color: C.accent4, valign: "top", margin: 0 }, text: "" } },
  ],
});

pres.defineSlideMaster({
  title: "CONCLUSION_SOMBRE",
  background: { color: C.text2 },
  slideNumber: { x: W - M - 0.6, y: 7.0, w: 0.6, h: 0.3, fontSize: 10, color: C.accent6, align: "right" },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.35, w: W - 2 * M, h: 0.8,
      fontSize: 36, bold: true, color: C.background1, valign: "middle", margin: 0 }, text: "" } },
  ],
});

// ------------------------------------------------------------------ helpers
const card = (slide, { x, y, w, h, fill = C.background2, name }) =>
  slide.addShape(pres.shapes.ROUNDED_RECTANGLE, {
    x, y, w, h, rectRadius: 0.12, fill: { color: fill }, line: { color: fill }, objectName: name,
  });

const text = (slide, value, opts) => slide.addText(value, { isTextBox: true, margin: 0, valign: "top", ...opts });

const stat = (slide, { x, y, w, value, label, color = C.accent1, name }) => {
  text(slide, value, { x, y, w, h: 0.8, fontSize: 40, bold: true, color, fontFace: THEME.headFontFace,
    objectName: `${name}-valeur` });
  text(slide, label, { x, y: y + 0.82, w, h: 0.6, fontSize: 14, color: C.accent4, objectName: `${name}-libelle` });
};

const image = (slide, name, { x, y, w, ratio }) =>
  slide.addImage({ path: FIG(name), x, y, w, h: w / ratio, objectName: `figure-${name}`,
    altText: `Graphique : ${name.replace(/_/g, " ")}` });

const content = (section, title, lede) => {
  const slide = pres.addSlide({ masterName: "CONTENU", sectionTitle: section });
  slide.addText(title, { placeholder: "title" });
  slide.addText(lede, { placeholder: "lede" });
  return slide;
};

// ================================================================== 1. Titre
pres.addSection({ title: "Introduction" });
let s = pres.addSlide({ masterName: "TITRE_SOMBRE", sectionTitle: "Introduction" });
s.addText("Où academy doit-elle s'implanter ?", { placeholder: "title" });
s.addText("Ce que les données éducatives de la Banque mondiale disent du potentiel de 216 pays",
  { placeholder: "body" });
text(s, "Corrigé de référence — projet OpenClassrooms « Analysez les données de systèmes éducatifs »", {
  x: M, y: 6.6, w: 11.5, h: 0.4, fontSize: 12, color: C.accent6, objectName: "mention-corrige" });
s.addNotes(
  "Accroche : academy veut s'étendre à l'international. Avant de dépenser en études de marché, on regarde ce que des " +
  "données publiques et gratuites peuvent déjà dire. Annoncer le plan : le besoin, les données, la démarche, " +
  "la réponse et ses limites. Durée visée : 10 minutes.");

// ================================================================== 2. Contexte
s = content("Introduction", "La demande de Mark", "Deux questions avant de choisir où lancer academy à l'international");
const besoin = [
  ["Qui ?", "Lycéens et étudiants : la cible d'academy, qui forme du lycée à l'université"],
  ["Comment ?", "100 % en ligne : sans accès à internet, pas de client possible"],
  ["Question 1", "Les données EdStats de la Banque mondiale peuvent-elles éclairer la décision ?"],
  ["Question 2", "Quels pays ont le plus fort potentiel, et comment évoluera-t-il d'ici 2030 ?"],
];
besoin.forEach(([k, v], i) => {
  const x = M + (i % 2) * 6.15, y = 2.1 + Math.floor(i / 2) * 2.25;
  card(s, { x, y, w: 5.9, h: 2.0, fill: i < 2 ? C.background2 : C.accent6, name: `carte-besoin-${i}` });
  text(s, k, { x: x + 0.35, y: y + 0.3, w: 5.2, h: 0.5, fontSize: 22, bold: true, color: C.text2,
    fontFace: THEME.headFontFace, objectName: `besoin-titre-${i}` });
  text(s, v, { x: x + 0.35, y: y + 0.9, w: 5.2, h: 0.9, fontSize: 16, color: C.text1, objectName: `besoin-texte-${i}` });
});
s.addNotes("Rappeler le contexte en une phrase, puis les deux questions. Tout ce qui suit sert à y répondre : " +
  "c'est le fil rouge de la présentation.");

// ================================================================== 3. Données
pres.addSection({ title: "Données et démarche" });
s = content("Données et démarche", "Cinq fichiers, une seule table de valeurs",
  "EdStats : 3 665 indicateurs sur l'éducation, la démographie et l'économie, de 1970 à 2100");
const hdr = (t) => ({ text: t, options: { bold: true, color: C.background1, fill: { color: C.text2 } } });
s.addTable([
  [hdr("Fichier"), hdr("Une ligne ="), hdr("Lignes"), hdr("Colonnes clés")],
  ["Data", "un indicateur pour un pays, une colonne par année", "886 930", "Country Code, Indicator Code, 1970 … 2100"],
  ["Country", "un pays (ou un agrégat de pays)", "241", "Region, Income Group, 2-alpha code"],
  ["Series", "un indicateur et sa définition", "3 665", "Series Code, Topic, Indicator Name"],
  ["FootNote", "une note sur un (pays, indicateur, année)", "643 638", "CountryCode, SeriesCode, Year"],
  ["Country-Series", "une note méthodologique (pays, indicateur)", "613", "CountryCode, SeriesCode, DESCRIPTION"],
], { x: M, y: 2.0, w: W - 2 * M, colW: [1.9, 4.4, 1.4, 4.43], fontSize: 14, color: C.text1,
  border: { type: "solid", pt: 0.75, color: "C9D9EA" }, rowH: 0.62, valign: "middle", objectName: "table-fichiers" });
text(s, "Tout le reste du travail porte sur Data, filtré à l'aide de Country (quels pays ?) et de Series (quels indicateurs ?).",
  { x: M, y: 6.1, w: W - 2 * M, h: 0.5, fontSize: 14, italic: true, color: C.accent4, objectName: "note-fichiers" });
s.addNotes("Une phrase par fichier, sans entrer dans le code. Insister sur la maille de Data : un pays × un " +
  "indicateur, avec les années en colonnes. C'est elle qu'on va transformer.");

// ================================================================== 4. Entonnoir
s = content("Données et démarche", "De 3 665 indicateurs à 5",
  "Chaque filtre est chiffré : la démarche est reproductible et défendable");
const etapes = [
  ["3 665", "indicateurs bruts"],
  ["751", "familles utiles au métier (démographie, scolarisation, internet, économie)"],
  ["314", "renseignés pour ≥ 60 % des couples (pays, année) sur 2010-2014"],
  ["15", "retenus pour leur sens métier"],
  ["5", "non redondants (|ρ| < 0,7)"],
];
etapes.forEach(([v, l], i) => {
  const w = 11.9 - i * 1.55, x = (W - w) / 2, y = 1.95 + i * 0.92;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h: 0.78, rectRadius: 0.1,
    fill: { color: i === 4 ? C.accent2 : C.accent1, transparency: i === 4 ? 0 : 55 - i * 12 },
    line: { color: C.background1, width: 0 }, objectName: `entonnoir-${i}` });
  text(s, [
    { text: v + "  ", options: { bold: true, fontSize: 22, fontFace: THEME.headFontFace } },
    { text: l, options: { fontSize: 14 } },
  ], { x: x + 0.3, y, w: w - 0.6, h: 0.78, valign: "middle", align: "center",
    color: i >= 3 ? C.background1 : C.text2, objectName: `entonnoir-texte-${i}` });
});
text(s, "En parallèle : 241 lignes « pays » → 216 vrais pays (25 agrégats retirés : Monde, zones, groupes de revenu) · 65 années → 5",
  { x: M, y: 6.6, w: W - 2 * M, h: 0.35, fontSize: 13, color: C.accent4, align: "center", objectName: "note-entonnoir" });
s.addNotes("C'est la slide méthodologie : chaque marche est un filtre, et on donne son impact. Préciser que Gibraltar " +
  "et Nauru n'ont pas de région mais ont été gardés : la règle a été vérifiée sur ses exceptions.");

// ================================================================== 5. Hypothèses
s = content("Données et démarche", "Trois hypothèses, toutes paramétrables",
  "Les années récentes et bien remplies, une valeur robuste par pays");
image(s, "remplissage_par_annee", { x: M, y: 1.95, w: 7.6, ratio: 2.473 });
const hyp = [
  ["Années 2010-2014", "Après 2014, le remplissage s'effondre ; après 2017, ce sont des projections"],
  ["Seuil de 60 %", "En dessous, un indicateur manque pour plus de 4 pays sur 10"],
  ["Médiane, ≥ 3 années", "Robuste à une année aberrante ; jamais une valeur isolée"],
];
hyp.forEach(([k, v], i) => {
  const y = 1.95 + i * 1.5;
  card(s, { x: 8.6, y, w: 4.13, h: 1.32, name: `carte-hypothese-${i}` });
  text(s, k, { x: 8.85, y: y + 0.18, w: 3.7, h: 0.4, fontSize: 17, bold: true, color: C.text2, objectName: `hyp-titre-${i}` });
  text(s, v, { x: 8.85, y: y + 0.58, w: 3.7, h: 0.7, fontSize: 14, color: C.text1, objectName: `hyp-texte-${i}` });
});
text(s, "Projections 2020-2100 (Wittgenstein) : mises de côté, puis utilisées seules pour estimer l'évolution de la cible",
  { x: M, y: 5.25, w: 7.6, h: 0.6, fontSize: 13, italic: true, color: C.accent4, objectName: "note-projections" });
s.addNotes("Lire le graphique : barres bleues = années gardées. Les pics tous les 5 ans viennent de sources " +
  "quinquennales. Le message : nos choix sont justifiés par la donnée, et modifiables en un seul endroit du code.");

// ================================================================== 6. Redondance
pres.addSection({ title: "Analyse" });
s = content("Analyse", "Beaucoup d'indicateurs disent la même chose",
  "Deux blocs très corrélés : la taille du pays et son niveau de développement");
image(s, "correlations_pearson_spearman", { x: M, y: 1.85, w: 8.4, ratio: 2.401 });
card(s, { x: 9.3, y: 1.85, w: 3.43, h: 4.75, name: "carte-indicateurs-gardes" });
text(s, "On garde 5 indicateurs", { x: 9.55, y: 2.05, w: 3.0, h: 0.4, fontSize: 17, bold: true, color: C.text2, objectName: "gardes-titre" });
text(s, [
  { text: "Internet (% population)", options: { bullet: true, breakLine: true } },
  { text: "Population 15-24 ans", options: { bullet: true, breakLine: true } },
  { text: "Croissance démographique", options: { bullet: true, breakLine: true } },
  { text: "PIB total", options: { bullet: true, breakLine: true } },
  { text: "Chômage", options: { bullet: true } },
], { x: 9.55, y: 2.55, w: 3.0, h: 2.1, fontSize: 14, color: C.text1, paraSpaceAfter: 6, objectName: "gardes-liste" });
text(s, "Internet résume le bloc développement : ρ ≈ 0,9 avec le PIB/hab, ≈ 0,8 avec la scolarisation supérieure.",
  { x: 9.55, y: 4.8, w: 3.0, h: 1.6, fontSize: 13, italic: true, color: C.accent4, objectName: "gardes-note" });
text(s, "Spearman (à droite) est la référence : il travaille sur les rangs et n'est pas dominé par la Chine ou l'Inde.",
  { x: M, y: 5.5, w: 8.4, h: 0.6, fontSize: 13, color: C.accent4, objectName: "note-spearman" });
s.addNotes("Pourquoi supprimer des indicateurs corrélés ? Parce qu'ils compteraient plusieurs fois la même " +
  "information dans le score. Dans chaque paire, on garde le plus utile pour academy : internet passe en premier, " +
  "car c'est le prérequis d'un service en ligne. Attention : corrélation ne veut pas dire causalité.");

// ================================================================== 7. Distributions
s = content("Analyse", "Des pays très inégaux… et une cible qui grandit",
  "Internet va de 0 à 96 % selon les pays ; la cible progresse d'ici 2030 dans la plupart d'entre eux");
image(s, "distribution_internet", { x: M, y: 1.95, w: 5.95, ratio: 1.842 });
image(s, "croissance_cible_2030", { x: 6.78, y: 1.95, w: 5.95, ratio: 1.813 });
stat(s, { x: M, y: 5.35, w: 5.9, value: "37,5 %", label: "d'internautes dans le pays médian (moyenne 39,9 % : distribution presque symétrique)", name: "stat-internet" });
stat(s, { x: 6.78, y: 5.35, w: 5.9, value: "+24 %", label: "croissance médiane 2015-2030 des 15-24 ans ayant au moins le niveau lycée", color: C.accent2, name: "stat-croissance" });
s.addNotes("Lire les deux distributions en une phrase chacune. À gauche : pas de pays type, d'où un critère très " +
  "discriminant. À droite : la cible grandit presque partout, mais beaucoup plus vite dans les pays aujourd'hui " +
  "peu connectés. C'est la tension qu'on retrouve sur la carte.");

// ================================================================== 8. Méthode
s = content("Analyse", "Un score sur trois critères",
  "Chaque critère est converti en rang (0 = dernier pays, 1 = premier), puis pondéré");
const crit = [
  ["50 %", "Marché connecté", "jeunes de 15-24 ans × % d'internautes", "Combien de clients peuvent suivre un cours en ligne ?", C.accent1],
  ["30 %", "Maturité numérique", "% d'internautes", "Le numérique est-il entré dans les usages (et le pouvoir d'achat suit-il) ?", C.accent1],
  ["20 %", "Dynamique", "croissance 2015-2030 de la cible", "Le marché de demain sera-t-il plus grand ?", C.accent2],
];
crit.forEach(([p, k, f, q, col], i) => {
  const x = M + i * 4.1;
  card(s, { x, y: 2.0, w: 3.85, h: 3.6, name: `carte-critere-${i}` });
  text(s, p, { x: x + 0.3, y: 2.2, w: 3.3, h: 0.9, fontSize: 44, bold: true, color: col, fontFace: THEME.headFontFace, objectName: `critere-poids-${i}` });
  text(s, k, { x: x + 0.3, y: 3.15, w: 3.3, h: 0.45, fontSize: 19, bold: true, color: C.text2, objectName: `critere-nom-${i}` });
  text(s, f, { x: x + 0.3, y: 3.65, w: 3.3, h: 0.6, fontSize: 14, italic: true, color: C.accent4, objectName: `critere-formule-${i}` });
  text(s, q, { x: x + 0.3, y: 4.35, w: 3.3, h: 1.1, fontSize: 14, color: C.text1, objectName: `critere-question-${i}` });
});
text(s, "Contrôle de robustesse : 1 000 jeux de poids tirés au hasard. Un pays recommandé doit rester dans le top 10 quels que soient nos choix.",
  { x: M, y: 5.9, w: W - 2 * M, h: 0.6, fontSize: 14, color: C.text2, bold: true, objectName: "note-robustesse" });
s.addNotes("Pourquoi des rangs ? Sinon le critère en millions de personnes écraserait le critère en pourcentage. " +
  "Les poids sont un choix métier, assumé et affiché. Le test des 1 000 tirages vérifie que la recommandation " +
  "ne dépend pas de ce choix.");

// ================================================================== 9. Carte
pres.addSection({ title: "Recommandation" });
s = content("Recommandation", "Deux familles de marchés",
  "Les pays les plus connectés sont ceux où la cible grandit le moins : il faut choisir une stratégie");
image(s, "carte_marches", { x: 2.6, y: 1.8, w: 7.6, ratio: 1.499 });
text(s, "Taille de bulle = marché connecté. Bleu = top 12 du score.", { x: 10.4, y: 2.0, w: 2.33, h: 1.2, fontSize: 13, color: C.accent4, objectName: "legende-carte" });
text(s, "ρ = -0,66 entre maturité et dynamique", { x: 10.4, y: 3.4, w: 2.33, h: 1.0, fontSize: 16, bold: true, color: C.accent2, objectName: "stat-anticorrelation" });
s.addNotes("La slide clé. En bas à droite : les marchés matures (Royaume-Uni, France, États-Unis, Allemagne, " +
  "Japon), gros et solvables mais stables. En haut au centre : des marchés déjà connectés dont la cible grandit " +
  "vite (Maroc, Arabie saoudite, Mexique). En haut à gauche : le potentiel futur (Nigeria, Inde), avec un accès " +
  "encore limité. La Chine, énorme bulle grise, a une cible quasi stable d'ici 2030.");

// ================================================================== 10. Recommandation
s = content("Recommandation", "Notre recommandation à Mark",
  "Commencer par deux marchés robustes, préparer la vague émergente, surveiller le potentiel futur");
s.addTable([
  [hdr("Priorité"), hdr("Pays"), hdr("Pourquoi"), hdr("Point d'attention")],
  [{ text: "1 · Matures", options: { bold: true, color: C.accent1 } }, "Royaume-Uni, France, puis États-Unis, Allemagne, Japon",
    "Gros marché connecté et solvable", "Cible stable d'ici 2030 ; forte concurrence"],
  [{ text: "2 · Émergents connectés", options: { bold: true, color: C.accent2 } }, "Maroc, Arabie saoudite, Espagne, Mexique, Émirats",
    "Déjà connectés, cible en forte croissance", "Pouvoir d'achat plus hétérogène"],
  [{ text: "3 · Potentiel futur", options: { bold: true, color: C.accent4 } }, "Nigeria, Inde, Égypte",
    "Cible en très forte croissance", "Accès à internet limité (données 2014)"],
], { x: M, y: 1.95, w: 8.3, colW: [1.9, 2.5, 2.0, 1.9], fontSize: 13, color: C.text1,
  border: { type: "solid", pt: 0.75, color: "C9D9EA" }, valign: "middle", rowH: 0.95, objectName: "table-recommandation" });
image(s, "robustesse_poids", { x: 9.15, y: 1.95, w: 3.58, ratio: 1.992 });
stat(s, { x: 9.15, y: 4.0, w: 3.58, value: "74 % · 59 %", label: "des jeux de poids placent le Royaume-Uni et la France dans le top 10", name: "stat-robustesse" });
s.addNotes("Seuls le Royaume-Uni et la France résistent à plus de la moitié des jeux de poids : c'est la " +
  "recommandation ferme. Le reste dépend de la stratégie : solvabilité immédiate ou croissance. Cette décision " +
  "appartient à Mark, pas aux données. Les deux pays robustes sont francophone et anglophone : vérifier la langue " +
  "des contenus d'academy.");

// ================================================================== 11. Limites
s = pres.addSlide({ masterName: "CONCLUSION_SOMBRE", sectionTitle: "Recommandation" });
s.addText("Ce que les données ne disent pas", { placeholder: "title" });
const limites = [
  ["Données datées", "Dernières valeurs exploitables en 2014 ; l'usage d'internet a fortement progressé depuis"],
  ["Angles morts", "Ni langue, ni concurrence, ni prix, ni réglementation : des critères pourtant décisifs"],
  ["Associations, pas causes", "Le score trie des pays ; il ne prédit pas un chiffre d'affaires"],
];
limites.forEach(([k, v], i) => {
  const x = M + i * 4.1;
  card(s, { x, y: 1.6, w: 3.85, h: 2.4, fill: "1D4466", name: `carte-limite-${i}` });
  text(s, k, { x: x + 0.3, y: 1.85, w: 3.3, h: 0.5, fontSize: 19, bold: true, color: C.background1, objectName: `limite-titre-${i}` });
  text(s, v, { x: x + 0.3, y: 2.45, w: 3.3, h: 1.4, fontSize: 15, color: C.accent6, objectName: `limite-texte-${i}` });
});
text(s, "Prochaines étapes", { x: M, y: 4.4, w: 6, h: 0.5, fontSize: 22, bold: true, color: C.background1,
  fontFace: THEME.headFontFace, objectName: "etapes-titre" });
text(s, [
  { text: "Actualiser les données (API Banque mondiale, UIT pour internet, UNESCO pour la scolarisation)", options: { bullet: { type: "number" }, breakLine: true } },
  { text: "Ajouter la langue d'enseignement et le prix moyen de l'EdTech locale", options: { bullet: { type: "number" }, breakLine: true } },
  { text: "Valider par une étude de marché sur 2 ou 3 pays pilotes (Royaume-Uni, France, Maroc)", options: { bullet: { type: "number" } } },
], { x: M, y: 5.0, w: W - 2 * M, h: 1.6, fontSize: 16, color: C.background1, paraSpaceAfter: 8, objectName: "etapes-liste" });
s.addNotes("Réponse à la question 1 : oui, EdStats permet un premier tri crédible, mais pas une décision. " +
  "Terminer sur les prochaines étapes concrètes, puis ouvrir les questions.");

(async () => {
  await pres.writeFile({ fileName: OUT });
  await setThemeColors(OUT, THEME);
  console.log("écrit", OUT);
})();
