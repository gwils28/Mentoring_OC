// Génère presentation/segmentation_vetements_modetrends.pptx (livrable 2 du corrigé).
// Usage : uv run python presentation/export_resultats.py && cd presentation && npm ci && npm run build
// Même trame que le support fourni par OpenClassrooms (8 rubriques, la conformité est optionnelle), sans le copier.
// Les chiffres viennent de resultats.json ; ceux que les phrases citent sont vérifiés contre lui (voir VERIF).

const path = require("path");
const pptxgen = require("pptxgenjs");
const { setThemeColors } = require("./theme_colors");
const R = require("./resultats.json");

const FIG = (name) => path.join(__dirname, "figures", `${name}.png`);
const OUT = path.join(__dirname, "segmentation_vetements_modetrends.pptx");

// Nombres au format français
const fr = (v, d = 2) => v.toLocaleString("fr-FR", { minimumFractionDigits: d, maximumFractionDigits: d });

// ------------------------------------------------------------------ garde-fou : texte ↔ résultats
const VERIF = [
  [R.miou, 0.791], [R.ic[0], 0.756], [R.ic[1], 0.818], [R.verdict, "non disqualifié pour un pilote"],
  [R.iou.Jupe, 0.942], [R.iou.Pantalon, 0.899], [R.iou.Haut, 0.881], [R.iou.Robe, 0.801], [R.iou.Ceinture, 0.565],
  [R.iou.Écharpe, 0.825], [R.images_par_famille.Écharpe, 3], [R.exactitude_modele, 0.96],
  [R.exactitude_tout_fond, 0.784], [R.delta_jpeg_png, -0.0052], [R.ko_jpeg, 53], [R.ko_png, 426],
  [R.latence_mediane, 0.71], [R.latence_p95, 1.24], [R.appels_reussis, 150], [R.debit_requis_min, 11.6],
  [R.cout.serverless_max, 16.6], [R.cout.cpu_continu, 50.4], [R.cout.t4_continu, 360], [R.cout.cpu_lots, 17.5],
  [R.cout.heures_lots, 250], [R.cout.debit_cpu_min, 33],
];
VERIF.forEach(([lu, attendu], i) => {
  if (lu !== attendu) throw new Error(`Chiffre n°${i} : resultats.json donne ${lu}, le texte dit ${attendu}. Mettre à jour build_deck.js.`);
});

const THEME = {
  name: "Segmentation vêtements",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1B1B1A", lt1: "FFFFFF", dk2: "1E2A44", lt2: "F1F3F8",
    accent1: "2A78D6", accent2: "EB6834", accent3: "1BAF7A", accent4: "52514E",
    accent5: "86B6EF", accent6: "DCE6F5", hlink: "2A78D6", folHlink: "6250D6",
  },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33" × 7.5"
pres.title = "Segmenter les vêtements par API : premier test";
pres.subject = "Corrigé P01 AI Engineer OpenClassrooms — ModeTrends";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;
const W = 13.333;
const M = 0.6;

// ------------------------------------------------------------------ layouts
pres.defineSlideMaster({
  title: "TITRE_SOMBRE",
  background: { color: C.text2 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 2.0, w: 11.8, h: 1.8,
      fontSize: 40, bold: true, color: C.background1, valign: "bottom" }, text: "" } },
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
    { text: { text: "ModeTrends · Fashion Trend Intelligence · segmentation", options: {
      x: M, y: 7.0, w: 7, h: 0.3, fontSize: 10, color: C.accent4, margin: 0 } } },
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.35, w: W - 2 * M, h: 0.8,
      fontSize: 28, bold: true, color: C.text2, valign: "middle", margin: 0 }, text: "" } },
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
      fontSize: 32, bold: true, color: C.background1, valign: "middle", margin: 0 }, text: "" } },
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

const hdr = (t) => ({ text: t, options: { bold: true, color: C.background1, fill: { color: C.text2 } } });
const BORDER = { type: "solid", pt: 0.75, color: "DCE6F5" };

const lecture = (slide, msg, name, y = 5.95, h = 0.85) => {
  card(slide, { x: M, y, w: W - 2 * M, h, fill: C.accent6, name: `${name}-fond` });
  text(slide, msg, { x: M + 0.25, y, w: W - 2 * M - 0.5, h, valign: "middle", fontSize: 15,
    color: C.text2, objectName: `${name}-texte` });
};

const image = (slide, name, { x, y, w, ratio, alt }) =>
  slide.addImage({ path: FIG(name), x, y, w, h: w / ratio, objectName: `figure-${name}`, altText: alt });

const cards = (slide, items, { y, h, cols, fill = C.background2, titleSize = 17, bodySize = 13, prefix }) => {
  const gap = 0.25, cw = (W - 2 * M - gap * (cols - 1)) / cols;
  items.forEach(([k, v], i) => {
    const x = M + (i % cols) * (cw + gap), yy = y + Math.floor(i / cols) * (h + gap);
    card(slide, { x, y: yy, w: cw, h, fill, name: `${prefix}-carte-${i}` });
    text(slide, k, { x: x + 0.25, y: yy + 0.18, w: cw - 0.5, h: 0.45, fontSize: titleSize, bold: true,
      color: C.text2, objectName: `${prefix}-titre-${i}` });
    text(slide, v, { x: x + 0.25, y: yy + 0.68, w: cw - 0.5, h: h - 0.8, fontSize: bodySize, color: C.text1,
      objectName: `${prefix}-texte-${i}` });
  });
};

// ================================================================== 1. Titre
pres.addSection({ title: "Introduction" });
let s = pres.addSlide({ masterName: "TITRE_SOMBRE", sectionTitle: "Introduction" });
s.addText("Segmenter les vêtements par API : faisable, prometteur, peu coûteux", { placeholder: "title" });
s.addText("Premier test du modèle SegFormer « clothes » de Hugging Face sur 50 photos annotées, et chiffrage pour " +
  "500 000 images par mois", { placeholder: "body" });
text(s, "Corrigé de référence — projet OpenClassrooms « Requêtez des services IA » (parcours AI Engineer)", {
  x: M, y: 6.6, w: 11.5, h: 0.4, fontSize: 12, color: C.accent6, objectName: "mention-corrige" });
s.addNotes("Accroche : peut-on reconnaître automatiquement les vêtements sur des photos d'influenceurs avec un " +
  "modèle déjà entraîné, sans serveur à gérer ? Réponse en trois mots dans le titre ; la suite les justifie. " +
  "Plan : la mission, comment ça marche, les résultats, comment on valide, le coût, la conformité, la recommandation.");

// ================================================================== 2. La mission
s = content("Introduction", "Notre part du projet : la première brique, la segmentation",
  "Fashion Trend Intelligence analyse les tenues publiées sur les réseaux sociaux, en trois étapes");
[
  ["1. Segmentation", "Isoler chaque vêtement sur la photo, pixel par pixel", true],
  ["2. Analyse stylistique", "Nature, couleur, texture et style de chaque pièce", false],
  ["3. Tendances", "Agréger des milliers de publications pour repérer ce qui émerge", false],
].forEach(([k, v, nous], i) => {
  const x = M + i * 4.1;
  card(s, { x, y: 1.95, w: 3.85, h: 1.9, fill: nous ? C.accent6 : C.background2, name: `etape-carte-${i}` });
  text(s, k, { x: x + 0.3, y: 2.15, w: 3.3, h: 0.5, fontSize: 20, bold: true, color: nous ? C.accent1 : C.accent4,
    fontFace: THEME.headFontFace, objectName: `etape-titre-${i}` });
  text(s, v, { x: x + 0.3, y: 2.75, w: 3.3, h: 0.9, fontSize: 15, color: C.text1, objectName: `etape-texte-${i}` });
});
text(s, "◀ notre mission", { x: M + 0.3, y: 3.9, w: 3.3, h: 0.35, fontSize: 13, bold: true, color: C.accent1,
  objectName: "etape-nous" });
cards(s, [
  ["Question 1 : la qualité", "Le modèle sayeed99/segformer_b3_clothes, appelé par l'API serverless de Hugging Face, segmente-t-il correctement les vêtements des 50 photos annotées ?"],
  ["Question 2 : le coût", "Combien coûterait le traitement de 500 000 images en 30 jours ?"],
], { y: 4.5, h: 1.75, cols: 2, prefix: "question", bodySize: 14 });
s.addNotes("Deux questions, deux réponses à la fin. On ne développe pas de modèle : on teste un modèle existant, " +
  "affiné sur un jeu public de photos de mode annotées (18 classes : vêtements, parties du corps, fond).");

// ================================================================== 3. Comment ça marche
pres.addSection({ title: "Solution" });
s = content("Solution", "Une photo envoyée, 18 masques reçus, une carte des vêtements",
  "SegFormer attribue une classe à chaque pixel ; l'API serverless l'exécute à notre place");
const etapes = [
  ["Photo", "réduite à 512 px, JPEG : 53 Ko"],
  ["Requête HTTPS", "POST + token secret (fichier .env)"],
  ["SegFormer", "classe chaque pixel (18 classes)"],
  ["Réponse JSON", "1 masque par classe détectée (base64)"],
  ["Carte", "1 couleur par vêtement, à la taille de la photo"],
];
etapes.forEach(([k, v], i) => {
  const x = M + i * 2.46;
  card(s, { x, y: 1.95, w: 2.2, h: 1.55, fill: i === 2 ? C.accent6 : C.background2, name: `flux-carte-${i}` });
  text(s, k, { x: x + 0.15, y: 2.08, w: 1.9, h: 0.4, fontSize: 15, bold: true, color: C.text2, align: "center",
    objectName: `flux-titre-${i}` });
  text(s, v, { x: x + 0.15, y: 2.55, w: 1.9, h: 0.85, fontSize: 12, color: C.text1, align: "center",
    objectName: `flux-texte-${i}` });
  if (i < etapes.length - 1) {
    s.addShape(pres.shapes.RIGHT_ARROW, { x: x + 2.22, y: 2.55, w: 0.22, h: 0.3, fill: { color: "86B6EF" },
      line: { color: "86B6EF" }, objectName: `flux-fleche-${i}` });
  }
});
cards(s, [
  ["Timeout", "30 s par requête : un serveur muet ne bloque jamais la boucle"],
  ["Quota", "au plus 30 requêtes par minute, sur toute fenêtre de 60 s"],
  ["Nouvelles tentatives", "429, 503, timeout : attente 2, 4, 8, 16 s ; 401 ou 402 : arrêt immédiat"],
  ["Reprise", "chaque résultat est mis en cache : relancer ne refait que les manquants"],
], { y: 3.8, h: 1.45, cols: 4, prefix: "robuste", titleSize: 15, bodySize: 12 });
lecture(s, `${R.appels_reussis} appels sur ${R.appels_reussis} réussis du premier coup ; ${fr(R.latence_mediane)} s par image en médiane ` +
  `(${fr(R.latence_p95)} s au 95ᵉ centile). Le JPEG réduit est ${Math.round(R.ko_png / R.ko_jpeg)} fois plus léger que le PNG d'origine.`,
  "lecture-solution", 5.55, 1.0);
s.addNotes("Le modèle redimensionne toute image en 512 × 512 : envoyer plus grand alourdit la requête sans rien " +
  "apporter. L'adresse de l'API a changé en 2025 (router.huggingface.co). Les protections du client n'ont pas eu " +
  "à servir sur 150 appels ; à 500 000 images, une panne passagère est certaine.");

// ================================================================== 4. Performances
pres.addSection({ title: "Résultats" });
s = content("Résultats", `mIoU vêtements = ${fr(R.miou)} : les grandes pièces sont bien segmentées`,
  "IoU = part de surface commune entre la silhouette annotée et la silhouette prédite (1 = parfait)");
image(s, "iou_par_famille", { x: M, y: 1.75, w: 6.6, ratio: 1428 / 958, alt: "IoU par famille de vêtements et de parties du corps" });
card(s, { x: 7.55, y: 1.85, w: 5.18, h: 1.9, fill: C.accent6, name: "chiffre-cle-fond" });
text(s, fr(R.miou), { x: 7.85, y: 1.95, w: 2.2, h: 1.0, fontSize: 54, bold: true, color: C.accent1,
  fontFace: THEME.headFontFace, objectName: "chiffre-cle" });
text(s, `mIoU vêtements sur 9 familles\nintervalle à 95 % : ${fr(R.ic[0])} – ${fr(R.ic[1])}`, {
  x: 10.0, y: 2.15, w: 2.6, h: 1.0, fontSize: 13, color: C.text2, objectName: "chiffre-cle-legende" });
text(s, `Règle fixée avant les résultats : « ${R.verdict} »`, { x: 7.85, y: 3.1, w: 4.7, h: 0.5,
  fontSize: 13, bold: true, color: C.text2, objectName: "chiffre-cle-verdict" });
text(s, [
  { text: `Jupe ${fr(R.iou.Jupe)}, pantalon ${fr(R.iou.Pantalon)}, haut ${fr(R.iou.Haut)}, robe ${fr(R.iou.Robe)}`, options: { bullet: true, breakLine: true } },
  { text: `Objets fins plus difficiles : ceinture ${fr(R.iou.Ceinture)}`, options: { bullet: true, breakLine: true } },
  { text: `Écharpe (${R.images_par_famille.Écharpe} images) : trop rare pour conclure`, options: { bullet: true, breakLine: true } },
  { text: `Pourquoi pas « ${Math.round(R.exactitude_modele * 100)} % de pixels bien classés » ? Un modèle qui ne voit que du fond atteint déjà ${Math.round(R.exactitude_tout_fond * 100)} %`, options: { bullet: true } },
], { x: 7.55, y: 4.0, w: 5.18, h: 2.7, fontSize: 14, color: C.text1, paraSpaceAfter: 8, objectName: "resultats-liste" });
s.addNotes("Métrique principale fixée avant les résultats : moyenne des IoU des 9 familles de vêtements présentes " +
  "dans au moins 5 images, gauche et droite fusionnées. L'intervalle vient d'un bootstrap sur les images. Le mIoU " +
  "18 classes est plus bas (0,65) car le modèle distingue mal la gauche de la droite, sans importance pour une marque.");

// ================================================================== 5. Exemples
s = content("Résultats", "Les erreurs viennent surtout de vêtements ambigus",
  "Meilleur et pire cas des 50 images : photo (visage flouté), annotation, prédiction du modèle");
image(s, "triptyque_meilleur_image_42", { x: M, y: 1.75, w: 6.0, ratio: 1709 / 720, alt: "Meilleur cas : robe, presque parfaite" });
image(s, "triptyque_pire_image_29", { x: 6.73, y: 1.75, w: 6.0, ratio: 1749 / 720, alt: "Pire cas : short annoté robe, prédit pantalon" });
cards(s, [
  ["Robe simple, fond dégagé", "Presque parfait : contours, cheveux et peau sont justes."],
  ["Short annoté « robe », prédit « pantalon »", "La silhouette est juste, le nom du vêtement est discutable : où s'arrête une robe, où commence un short ?"],
], { y: 4.45, h: 1.3, cols: 2, prefix: "exemple", titleSize: 15, bodySize: 13 });
lecture(s, "Les deux plus mauvaises images (mIoU 0,40) sont des cas ambigus : short et tunique-robe. Pour ModeTrends, " +
  "c'est autant une question de définition des classes que de modèle.", "lecture-exemples");
s.addNotes("Deuxième cas ambigu (image 31) : une tunique sur un collant, annotée robe, prédite haut. Toutes les " +
  "figures publiées floutent les visages, à partir de l'annotation : ce sont des photos de vraies personnes.");

// ================================================================== 6. Méthode de validation
s = content("Résultats", "Ces 50 images, le modèle les a déjà vues : le score est optimiste",
  "Une méthode de validation pour la suite : des photos nouvelles, découpées par influenceur");
card(s, { x: M, y: 1.85, w: 5.6, h: 4.85, fill: "FCE9E1", name: "fuite-fond" });
text(s, "⚠ Fuite de données", { x: M + 0.3, y: 2.0, w: 5.0, h: 0.5, fontSize: 20, bold: true, color: C.accent2,
  fontFace: THEME.headFontFace, objectName: "fuite-titre" });
text(s, [
  { text: "Les 50 masques de test se retrouvent à l'identique dans le jeu public sur lequel le modèle a été affiné (17 706 photos)", options: { bullet: true, breakLine: true } },
  { text: "L'auteur n'a gardé que 0,6 % des images pour son propre test : nos images ont presque toutes servi à l'entraînement", options: { bullet: true, breakLine: true } },
  { text: `Donc ${fr(R.miou)} est une estimation optimiste : elle écarte un échec grossier, elle ne prouve pas que le modèle marchera sur les photos de ModeTrends`, options: { bullet: true } },
], { x: M + 0.3, y: 2.6, w: 5.0, h: 4.0, fontSize: 15, color: C.text1, paraSpaceAfter: 10, objectName: "fuite-liste" });
s.addTable([
  [hdr("Jeu"), hdr("Rôle"), hdr("Proposition")],
  ["Entraînement ≈ 70 %", "le modèle apprend", "photos ModeTrends annotées"],
  ["Validation ≈ 15 %", "régler, arrêter l'apprentissage", "jamais utilisé pour apprendre"],
  ["Test ≈ 15 %", "mesurer une fois, à la fin", "mis sous clé dès le début"],
], { x: 6.55, y: 1.85, w: 6.18, colW: [1.9, 2.1, 2.18], fontSize: 13, color: C.text1, border: BORDER, rowH: 0.55,
  valign: "middle", objectName: "table-jeux" });
[
  ["Découper par influenceur", "Deux photos d'une même personne ne doivent jamais se retrouver de part et d'autre."],
  ["Mesurer", "IoU par vêtement (et Dice), cumulé sur les images, avec un intervalle de confiance."],
].forEach(([k, v], i) => {
  const y = 4.2 + i * 1.3;
  card(s, { x: 6.55, y, w: 6.18, h: 1.15, name: `methode-carte-${i}` });
  text(s, k, { x: 6.8, y: y + 0.12, w: 5.7, h: 0.4, fontSize: 15, bold: true, color: C.text2, objectName: `methode-titre-${i}` });
  text(s, v, { x: 6.8, y: y + 0.55, w: 5.7, h: 0.5, fontSize: 13, color: C.text1, objectName: `methode-texte-${i}` });
});
s.addNotes("Ici rien n'est entraîné : les 50 images ne servent que de test. Le découpage train/val/test devient " +
  "nécessaire si ModeTrends affine le modèle sur ses propres photos. La vérification de la fuite compare des " +
  "empreintes de masques (script dans la fiche pédagogique 7).");

// ================================================================== 7. Passage à l'échelle et coût
pres.addSection({ title: "Passage à l'échelle" });
s = content("Passage à l'échelle", `500 000 images par mois : moins de ${Math.ceil(R.cout.serverless_max)} $ en serverless`,
  `Besoin moyen : ${fr(R.debit_requis_min, 1)} images par minute. Trois façons de payer (prix Hugging Face d'octobre 2026)`);
s.addTable([
  [hdr("Scénario"), hdr("Base du calcul"), hdr("Coût sur 30 jours"), hdr("À gérer")],
  ["A. Serverless (à l'usage)", "facture réelle : < 0,01 $ pour 301 requêtes", `< ${fr(R.cout.serverless_max, 1)} $`, "rien"],
  ["B. Machine CPU allumée 24 h/24", `2 vCPU à 0,07 $/h ; ≈ ${R.cout.debit_cpu_min} images/min (hypothèse)`, `${fr(R.cout.cpu_continu, 1)} $`, "créer, surveiller"],
  ["B. Machine GPU T4 24 h/24", "0,50 $/h ; large surcapacité", `${fr(R.cout.t4_continu, 0)} $`, "créer, surveiller"],
  ["B'. Machine CPU par lots", `≈ ${R.cout.heures_lots} h de machine, puis arrêt`, `${fr(R.cout.cpu_lots, 1)} $`, "planifier les lots"],
], { x: M, y: 1.85, w: W - 2 * M, colW: [3.2, 4.73, 2.2, 2.0], fontSize: 14, color: C.text1, border: BORDER, rowH: 0.55,
  valign: "middle", objectName: "table-couts" });
cards(s, [
  ["Recommandation", "Serverless pour le pilote : aucun serveur, coût faible. Mesurer la facture réelle sur quelques milliers d'images."],
  ["Si le volume se confirme", "Machine dédiée par lots : coût prévisible, débit garanti, pas de quota partagé."],
  ["Le vrai coût", "L'annotation de photos ModeTrends pour valider le modèle, pas le calcul."],
], { y: 4.95, h: 1.75, cols: 3, prefix: "cout", titleSize: 15, bodySize: 13 });
s.addNotes("Hugging Face ne publie pas de prix par seconde pour hf-inference : on a extrapolé la facture réelle " +
  "(301 requêtes, affichage < 0,01 $), d'où un majorant. Débit de la machine CPU : mesure locale (0,9 s par image " +
  "sur 2 cœurs) doublée par prudence. Au-delà d'environ 1,4 million d'images par mois, une machine CPU ne suffit plus.");

// ================================================================== 8. Conformité (optionnelle)
s = content("Passage à l'échelle", "Des photos de personnes : minimiser, flouter, ne jamais identifier",
  "Conformité (rubrique optionnelle) : RGPD et AI Act");
cards(s, [
  ["RGPD", "Une photo d'influenceur est une donnée personnelle : base légale, durée de conservation, information des personnes. Minimisation : ne garder que les masques de vêtements."],
  ["Dans ce test", "Visages floutés dans toutes les figures publiées ; images envoyées à un service hébergé : vérifier où il traite les données."],
  ["AI Act", "Reconnaître des vêtements n'est pas, en soi, un usage à haut risque. Il ne doit jamais servir à identifier les personnes (biométrie)."],
], { y: 1.95, h: 3.4, cols: 3, prefix: "conformite", bodySize: 15, titleSize: 19 });
lecture(s, "Avant la production : une analyse d'impact (AIPD) avec le DPO, et des conditions d'utilisation des réseaux sociaux vérifiées.",
  "lecture-conformite", 5.65, 0.9);
s.addNotes("Rubrique optionnelle du support. Points à retenir : données personnelles, minimisation, pas " +
  "d'identification. À valider avec un juriste ; ce n'est pas un avis juridique.");

// ================================================================== 9. Bilan
pres.addSection({ title: "Conclusion" });
s = pres.addSlide({ masterName: "CONCLUSION_SOMBRE", sectionTitle: "Conclusion" });
s.addText("Recommandation : lancer un pilote, mais tester d'abord sur nos propres photos", { placeholder: "title" });
[
  ["Faisable", `L'API répond, le client résiste aux erreurs : ${fr(R.latence_mediane)} s et ${R.ko_jpeg} Ko par image`],
  ["Prometteur", `mIoU vêtements ${fr(R.miou)}, à confirmer : ces images sont déjà connues du modèle`],
  ["Peu coûteux", `Moins de ${Math.ceil(R.cout.serverless_max)} $ par mois en serverless pour 500 000 images`],
].forEach(([k, v], i) => {
  const x = M + i * 4.1;
  card(s, { x, y: 1.6, w: 3.85, h: 2.4, fill: "2C3D5E", name: `bilan-carte-${i}` });
  text(s, k, { x: x + 0.3, y: 1.85, w: 3.3, h: 0.5, fontSize: 22, bold: true, color: C.background1, objectName: `bilan-titre-${i}` });
  text(s, v, { x: x + 0.3, y: 2.45, w: 3.3, h: 1.4, fontSize: 15, color: C.accent6, objectName: `bilan-texte-${i}` });
});
text(s, "Prochaines étapes", { x: M, y: 4.4, w: 6, h: 0.5, fontSize: 22, bold: true, color: C.background1,
  fontFace: THEME.headFontFace, objectName: "etapes-titre" });
text(s, [
  { text: "Annoter 200 à 300 photos ModeTrends jamais vues, découpées par influenceur, et mesurer le vrai score", options: { bullet: { type: "number" }, breakLine: true } },
  { text: "Préciser les classes ambiguës avec les équipes mode (robe, tunique, short)", options: { bullet: { type: "number" }, breakLine: true } },
  { text: "Pilote serverless sur quelques milliers d'images pour mesurer la facture réelle", options: { bullet: { type: "number" } } },
], { x: M, y: 5.0, w: W - 2 * M, h: 1.6, fontSize: 16, color: C.background1, paraSpaceAfter: 8, objectName: "etapes-liste" });
s.addNotes("Trois mots à retenir : faisable, prometteur, peu coûteux. Le seul vrai risque est la qualité sur des " +
  "photos réelles, et il se lève avec un petit jeu de test annoté.");

(async () => {
  await pres.writeFile({ fileName: OUT });
  await setThemeColors(OUT, THEME);
  console.log("écrit", OUT);
})();
