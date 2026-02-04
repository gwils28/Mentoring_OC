// Génère presentation/dataimmo_laplace_immo.pptx (livrable 2 du corrigé).
// Usage : uv run python presentation/export_resultats.py && cd presentation && npm ci && npm run build
// Le SQL et les tableaux de résultats viennent de resultats.json (exporté depuis la base) ; les phrases de lecture
// reprennent le notebook corrigé. Les chiffres qu'elles citent sont vérifiés contre resultats.json (voir VERIF).

const path = require("path");
const pptxgen = require("pptxgenjs");
const { setThemeColors } = require("./theme_colors");
const R = require("./resultats.json");

const FIG = (name) => path.join(__dirname, "figures", `${name}.png`);
const OUT = path.join(__dirname, "dataimmo_laplace_immo.pptx");

// ------------------------------------------------------------------ garde-fou : texte ↔ base
const cell = (n, row = 0, col = 0) => R.besoins[n].lignes[row][col];
const VERIF = [
  [cell(1), 31378], [cell(2, 0, 1), 13995], [cell(3, 2, 2), 31.18], [cell(4, 0, 1), 12053], [cell(4, 1, 1), 7219],
  [cell(5), 3745], [cell(5, 0, 1), 1059], [cell(6), 9000000], [cell(7), 16776], [cell(7, 0, 1), 17393],
  [cell(7, 0, 2), 3.68], [cell(8, 0, 2), 8770], [cell(8, 1, 3), 2], [R.besoins[9].nb_lignes, 48],
  [cell(10), 4909], [cell(10, 0, 1), 4300], [cell(10, 0, 2), -12.4], [cell(12, 0, 4), 5.88],
  [R.controle[0][1], 34169], [R.controle[2][1], 3125], [R.controle[3][1], 19],
];
VERIF.forEach(([lu, attendu], i) => {
  if (lu !== attendu) throw new Error(`Chiffre n°${i} : la base donne ${lu}, le texte dit ${attendu}. Mettre à jour build_deck.js.`);
});

const THEME = {
  name: "DATAImmo",
  headFontFace: "Cambria",
  bodyFontFace: "Calibri",
  colors: {
    dk1: "1B1B1A", lt1: "FFFFFF", dk2: "17324D", lt2: "EEF4F5",
    accent1: "1F7A8C", accent2: "D9682B", accent3: "1BAF7A", accent4: "52514E",
    accent5: "8CC4CE", accent6: "CFE3E7", hlink: "1F7A8C", folHlink: "6250D6",
  },
};
const MONO = "Consolas";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33" × 7.5"
pres.title = "DATAImmo : une base SQL des ventes immobilières";
pres.subject = "Corrigé P02 OpenClassrooms — Laplace Immo";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;
const W = 13.333;
const M = 0.6;

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
    { text: { text: "Laplace Immo · POC DATAImmo", options: {
      x: M, y: 7.0, w: 6, h: 0.3, fontSize: 10, color: C.accent4, margin: 0 } } },
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.35, w: W - 2 * M, h: 0.8,
      fontSize: 30, bold: true, color: C.text2, valign: "middle", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "lede", type: "body", x: M, y: 1.15, w: W - 2 * M, h: 0.5,
      fontSize: 17, color: C.accent4, valign: "top", margin: 0 }, text: "" } },
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

const content = (section, title, lede) => {
  const slide = pres.addSlide({ masterName: "CONTENU", sectionTitle: section });
  slide.addText(title, { placeholder: "title" });
  slide.addText(lede, { placeholder: "lede" });
  return slide;
};

const hdr = (t) => ({ text: t, options: { bold: true, color: C.background1, fill: { color: C.text2 } } });
const BORDER = { type: "solid", pt: 0.75, color: "CFE3E7" };

// Nombres au format français : espace fine pour les milliers, virgule décimale
const fr = (v) => (typeof v === "number" ? v.toLocaleString("fr-FR", { maximumFractionDigits: 2 }) : v ?? "—");

const LIBELLES = {
  nb_appartements_vendus: "Appartements vendus", nom_region: "Région", nb_ventes_appartements: "Ventes d'apparts",
  nb_pieces: "Pièces", nb_ventes: "Ventes", proportion_pct: "Part (%)", code_departement: "Dép.",
  prix_m2_moyen: "Prix moyen €/m²", prix_m2_moyen_maison_idf: "Prix moyen €/m²", nb_maisons: "Maisons",
  valeur_fonciere: "Valeur (€)", surface_m2: "m² Carrez", nom_commune: "Commune", nb_t1: "Ventes T1",
  nb_t2: "Ventes T2", evolution_pct: "Évolution (%)", rang: "Rang", nb_ventes_t1: "Ventes T1",
  prix_m2_2_pieces: "2 pièces €/m²", prix_m2_3_pieces: "3 pièces €/m²", ecart_pct: "Écart (%)",
  valeur_moyenne: "Valeur moyenne (€)", population: "Habitants", ventes_pour_1000_hab: "Pour 1 000 hab.",
};

// Taille de police du SQL : la plus grande qui fait tenir la requête dans le cadre, sans dépasser 12 pt
// (Consolas : un caractère ≈ 0,55 em de large ; une ligne ≈ 1,2 em de haut)
const sqlFontSize = (sql, w, h) => {
  const lignes = sql.split("\n");
  const largeur = Math.max(...lignes.map((l) => l.length));
  return Math.min(12, Math.floor((w * 72) / (0.55 * largeur) * 2) / 2, Math.floor((h * 72) / (1.2 * lignes.length) * 2) / 2);
};

const sqlBlock = (slide, sql, { x, y, w, h, name }) => {
  card(slide, { x, y, w, h, fill: "F3F5F7", name: `${name}-fond` });
  text(slide, sql, { x: x + 0.2, y: y + 0.15, w: w - 0.4, h: h - 0.3, fontFace: MONO,
    fontSize: sqlFontSize(sql, w - 0.4, h - 0.3), color: C.text1, objectName: `${name}-code` });
};

const resultTable = (slide, n, { x, y, w, colW, maxRows = 10, fontSize = 12, rowH = 0.3, name }) => {
  const b = R.besoins[n];
  const rows = b.lignes.slice(0, maxRows).map((l) => l.map((v) => ({ text: String(fr(v)) })));
  slide.addTable([b.colonnes.map((c) => hdr(LIBELLES[c] ?? c)), ...rows], {
    x, y, w, colW, fontSize, color: C.text1, border: BORDER, rowH, valign: "middle", margin: 0.05,
    objectName: name });
  if (b.nb_lignes > maxRows) {
    text(slide, `${b.nb_lignes} lignes au total : les ${maxRows} premières sont affichées`, {
      x, y: y + rowH * (rows.length + 1) + 0.08, w, h: 0.3, fontSize: 11, italic: true, color: C.accent4,
      objectName: `${name}-troncature` });
  }
};

const lecture = (slide, msg, name) => {
  card(slide, { x: M, y: 5.95, w: W - 2 * M, h: 0.85, fill: C.accent6, name: `${name}-fond` });
  text(slide, msg, { x: M + 0.25, y: 5.95, w: W - 2 * M - 0.5, h: 0.85, valign: "middle", fontSize: 15,
    color: C.text2, objectName: `${name}-texte` });
};

// ================================================================== 1. Titre
pres.addSection({ title: "Introduction" });
let s = pres.addSlide({ masterName: "TITRE_SOMBRE", sectionTitle: "Introduction" });
s.addText("DATAImmo : une base SQL des ventes immobilières", { placeholder: "title" });
s.addText("34 169 ventes du 1er semestre 2020, une base relationnelle conforme au RGPD, 12 questions métier",
  { placeholder: "body" });
text(s, "Corrigé de référence — projet OpenClassrooms « Entraînez-vous avec SQL et créez votre BDD »", {
  x: M, y: 6.6, w: 11.5, h: 0.4, fontSize: 12, color: C.accent6, objectName: "mention-corrige" });
s.addNotes("Accroche : Laplace Immo veut savoir si une base SQL sur les ventes publiques (DVF) peut répondre aux " +
  "questions de ses agences. Plan : le besoin, la préparation des données, la base, puis les 12 réponses.");

// ================================================================== 2. Contexte
s = content("Introduction", "Le POC demandé par Laplace Immo",
  "Une base relationnelle propre, conforme au RGPD, qui répond aux 12 besoins de la réunion");
[
  ["Qui ?", "Laplace Immo, réseau national d'agences immobilières, qui veut suivre le marché"],
  ["Quoi ?", "Les ventes de logements du 1er semestre 2020 (DVF), enrichies des communes et des régions"],
  ["Comment ?", "Une base SQLite en 3ᵉ forme normale, chargée depuis des CSV, sans donnée personnelle inutile"],
  ["Pour quoi ?", "12 besoins : volumes de ventes, prix au m², classements de départements, régions et communes"],
].forEach(([k, v], i) => {
  const x = M + (i % 2) * 6.15, y = 2.0 + Math.floor(i / 2) * 2.0;
  card(s, { x, y, w: 5.9, h: 1.8, fill: i < 2 ? C.background2 : C.accent6, name: `carte-besoin-${i}` });
  text(s, k, { x: x + 0.35, y: y + 0.25, w: 5.2, h: 0.5, fontSize: 22, bold: true, color: C.text2,
    fontFace: THEME.headFontFace, objectName: `besoin-titre-${i}` });
  text(s, v, { x: x + 0.35, y: y + 0.8, w: 5.2, h: 0.9, fontSize: 16, color: C.text1, objectName: `besoin-texte-${i}` });
});
s.addNotes("Le POC est une preuve de faisabilité : un semestre de données, mais un schéma pensé pour en accueillir " +
  "d'autres. Tout ce qui suit sert à répondre aux 12 besoins, présentés un par un à la fin.");

// ================================================================== 3. Transformation
pres.addSection({ title: "Données et base" });
s = content("Données et base", "Trois fichiers, quatre pièges, quatre tables",
  "La préparation corrige ce qu'un import naïf aurait cassé");
s.addTable([
  [hdr("Fichier source"), hdr("Lignes"), hdr("Ce qu'on en garde")],
  ["Valeurs foncières (DVF)", "34 169", "la vente et le bien (17 colonnes vides et le nom de l'acquéreur écartés)"],
  ["Données communes (INSEE)", "34 991", "la population municipale de chaque commune"],
  ["Référentiel géographique", "38 916", "le lien commune → département → région (19 régions)"],
], { x: M, y: 1.9, w: 6.3, colW: [2.0, 0.9, 3.4], fontSize: 13, color: C.text1, border: BORDER, rowH: 0.6,
  valign: "middle", objectName: "table-sources" });
[
  ["Les codes sont du texte", "« 2A », « 2B », « 01 » : en nombre, la Corse et les zéros disparaissent"],
  ["Le code postal décrit l'adresse", "Nice en a 4, 05100 couvre 3 communes : il va dans bien"],
  ["Des noms abîmés", "« SchÅ“lcher » réparé en « Schœlcher » (24 communes)"],
  ["Des vides qui comptent", "18 ventes sans valeur gardées en NULL : un '' serait lu comme 0 par AVG"],
].forEach(([k, v], i) => {
  const y = 1.9 + i * 1.0;
  card(s, { x: 7.2, y, w: 5.53, h: 0.88, name: `carte-piege-${i}` });
  text(s, k, { x: 7.45, y: y + 0.1, w: 5.1, h: 0.35, fontSize: 15, bold: true, color: C.text2, objectName: `piege-titre-${i}` });
  text(s, v, { x: 7.45, y: y + 0.45, w: 5.1, h: 0.4, fontSize: 13, color: C.text1, objectName: `piege-texte-${i}` });
});
text(s, "Clé d'une commune : code département + code commune (ex. 34172 = Montpellier), présente dans les 3 fichiers.",
  { x: M, y: 5.95, w: W - 2 * M, h: 0.5, fontSize: 14, italic: true, color: C.accent4, objectName: "note-cle" });
s.addNotes("Chaque piège se démontre : convertir les codes en nombres fait disparaître les 251 ventes de Corse des " +
  "jointures. La préparation est faite en Python dans le corrigé ; elle se fait aussi au tableur, avec les mêmes " +
  "pièges.");

// ================================================================== 4. Dictionnaire
s = content("Données et base", "Un dictionnaire pour chaque colonne de la base",
  "Extrait : 7 lignes, choisies pour leurs pièges (dictionnaire complet : dictionnaire_donnees.xlsx)");
s.addTable([
  [hdr("Table"), hdr("Code"), hdr("Signification"), hdr("Type"), hdr("Long."), hdr("Nature"), hdr("Règle de gestion")],
  ...R.dictionnaire.map((l) => l.map((v, j) => ({ text: v, options: j === 1 ? { fontFace: MONO } : {} }))),
], { x: M, y: 1.85, w: W - 2 * M, colW: [0.85, 2.35, 2.2, 0.85, 0.65, 1.15, 4.08], fontSize: 11, color: C.text1,
  border: BORDER, rowH: 0.5, valign: "middle", objectName: "table-dictionnaire" });
s.addNotes("Le dictionnaire est la colonne vertébrale du projet : il fixe le type et la règle de chaque champ avant " +
  "d'écrire une ligne de SQL. Montrer code_departement en texte et code_postal rangé dans bien.");

// ================================================================== 5. Schéma
s = content("Données et base", "Un schéma en troisième forme normale",
  "region ← commune ← bien ← vente : chaque information est stockée une seule fois");
s.addImage({ path: FIG("schema_relationnel"), x: M, y: 1.85, w: W - 2 * M, h: (W - 2 * M) / 3.763,
  objectName: "figure-schema", altText: "Schéma relationnel : tables region, commune, bien et vente reliées par clés étrangères" });
[
  ["1NF", "Valeurs atomiques : l'adresse est découpée en n°, indice, type de voie, voie, code postal"],
  ["2NF", "Clés à une seule colonne : la 2NF est respectée d'office"],
  ["3NF", "Le nom de région dépend du code région : stocké 19 fois, pas 3 125"],
].forEach(([k, v], i) => {
  const x = M + i * 4.1;
  card(s, { x, y: 5.4, w: 3.85, h: 1.3, name: `carte-nf-${i}` });
  text(s, k, { x: x + 0.25, y: 5.5, w: 3.4, h: 0.4, fontSize: 18, bold: true, color: C.accent1, objectName: `nf-titre-${i}` });
  text(s, v, { x: x + 0.25, y: 5.9, w: 3.4, h: 0.75, fontSize: 13, color: C.text1, objectName: `nf-texte-${i}` });
});
s.addNotes("La figure est générée depuis sql/schema.sql : elle ne peut pas diverger de la base. Écart assumé avec " +
  "l'ébauche fournie : le code postal est dans bien, pas dans commune (57 communes en ont plusieurs).");

// ================================================================== 6. Capture de la base
s = content("Données et base", "Dans la base : codes avec leurs zéros, dates au format ISO",
  "Les 3 premières lignes de chaque table, colonnes principales (export de la base, comme dans SQLite Studio)");
const apercu = (table, { x, y, w, colW }) => {
  const a = R.apercu[table];
  text(s, table, { x, y, w, h: 0.3, fontSize: 14, bold: true, fontFace: MONO, color: C.accent1, objectName: `apercu-titre-${table}` });
  s.addTable([a.colonnes.map(hdr), ...a.lignes.map((l) => l.map((v) => String(v ?? "NULL")))], {
    x, y: y + 0.32, w, colW, fontSize: 9, color: C.text1, border: BORDER, rowH: 0.26, valign: "middle", margin: 0.03,
    objectName: `apercu-${table}` });
};
apercu("region", { x: M, y: 1.8, w: 4.6, colW: [0.9, 2.3, 1.4] });
apercu("commune", { x: 5.5, y: 1.8, w: 7.23, colW: [1.75, 0.8, 1.3, 1.1, 1.48, 0.8] });
apercu("bien", { x: M, y: 3.35, w: W - 2 * M, colW: [0.65, 1.75, 0.65, 0.9, 1.95, 1.05, 1.15, 1.0, 1.08].map((c) => c * 1.1918) });
apercu("vente", { x: M, y: 4.9, w: 6.5, colW: [1.0, 0.9, 1.6, 1.7, 1.3] });
text(s, "« 01 », « 01170 », « 2020-01-02 » : des textes, pas des nombres. Une valeur absente s'affiche NULL.",
  { x: 7.4, y: 5.3, w: 5.33, h: 0.9, fontSize: 14, italic: true, color: C.accent4, objectName: "note-apercu" });
s.addNotes("Cette slide remplace la capture d'écran demandée : mêmes informations, exportées de la base elle-même.");

// ================================================================== 7. Preuve du chargement
s = content("Données et base", "Aucune ligne perdue au chargement",
  "Les mêmes comptages côté CSV et côté base");
sqlBlock(s, "SELECT 'vente' AS table_, COUNT(*) AS lignes FROM vente\nUNION ALL SELECT 'bien',    COUNT(*) FROM bien\n" +
  "UNION ALL SELECT 'commune', COUNT(*) FROM commune\nUNION ALL SELECT 'region',  COUNT(*) FROM region;",
  { x: M, y: 1.85, w: 6.4, h: 1.7, name: "sql-controle" });
s.addTable([[hdr("Table"), hdr("Lignes en base"), hdr("Côté CSV")],
  ...R.controle.map(([t, n]) => [{ text: t, options: { fontFace: MONO } }, fr(n),
    { vente: "34 169 lignes DVF", bien: "34 169 (1 bien par vente)", commune: "3 125 communes distinctes dans DVF",
      region: "19 régions du référentiel" }[t]]),
], { x: 7.3, y: 1.85, w: 5.43, colW: [1.3, 1.5, 2.63], fontSize: 13, color: C.text1, border: BORDER, rowH: 0.42,
  valign: "middle", objectName: "table-controle" });
text(s, "Seules les communes ayant au moins une vente sont chargées : 3 125 sur les 34 991 du fichier INSEE.",
  { x: 7.3, y: 3.6, w: 5.43, h: 0.45, fontSize: 12, italic: true, color: C.accent4, objectName: "note-controle" });
[
  ["Corse comprise", "les codes 2A / 2B sont en texte : aucune vente corse ne disparaît"],
  ["Contraintes actives", "une vente rattachée à un bien inexistant, une date 2020-13-45 ou une valeur vide ('') sont refusées"],
].forEach(([k, v], i) => {
  const x = M + i * 6.15;
  card(s, { x, y: 4.1, w: 5.9, h: 1.5, name: `carte-preuve-${i}` });
  text(s, k, { x: x + 0.3, y: 4.25, w: 5.3, h: 0.4, fontSize: 17, bold: true, color: C.text2, objectName: `preuve-titre-${i}` });
  text(s, v, { x: x + 0.3, y: 4.7, w: 5.3, h: 0.8, fontSize: 14, color: C.text1, objectName: `preuve-texte-${i}` });
});
s.addNotes("C'est la preuve que la base est complète avant d'interroger quoi que ce soit. Au bilan, lancer cette " +
  "requête en direct dans SQLite Studio.");

// ================================================================== 8. Sauvegarde et RGPD
s = content("Données et base", "Moins de données personnelles, une base restaurable",
  "RGPD et sauvegarde : deux obligations qui se prévoient dès la conception");
[
  ["RGPD : minimisation", [
    "Le nom de l'acquéreur identifie une personne et ne sert à aucun besoin : il est supprimé",
    "Ce n'est pas une anonymisation : adresse, date et prix rattachent encore une vente à un bien",
    "Accès à la base limité aux personnes qui en ont besoin",
  ]],
  ["Sauvegarde", [
    "La base se reconstruit à l'identique depuis les sources, dont l'empreinte SHA-256 est vérifiée",
    "Sauvegarde cohérente avec .backup (SQLite) ou pg_dump (PostgreSQL), pas une copie pendant l'écriture",
    "Une sauvegarde se teste en la restaurant ; elle contient les mêmes données, donc les mêmes protections",
  ]],
].forEach(([k, items], i) => {
  const x = M + i * 6.15;
  card(s, { x, y: 1.9, w: 5.9, h: 4.6, fill: i ? C.accent6 : C.background2, name: `carte-rgpd-${i}` });
  text(s, k, { x: x + 0.35, y: 2.1, w: 5.2, h: 0.5, fontSize: 21, bold: true, color: C.text2,
    fontFace: THEME.headFontFace, objectName: `rgpd-titre-${i}` });
  text(s, items.map((t, j) => ({ text: t, options: { bullet: true, breakLine: j < items.length - 1 } })),
    { x: x + 0.35, y: 2.75, w: 5.2, h: 3.6, fontSize: 15, color: C.text1, paraSpaceAfter: 10, objectName: `rgpd-liste-${i}` });
});
s.addNotes("Minimisation : on ne garde que ce qui sert. Pseudonymiser le nom n'aurait d'intérêt que pour suivre un " +
  "acheteur dans le temps, ce que personne ne demande. Côté sauvegarde, insister sur le test de restauration.");

// ================================================================== 9-21. Les 12 besoins (le besoin 11 sur deux slides)
pres.addSection({ title: "Les 12 besoins" });
const BESOINS = [
  { titre: "31 378 appartements vendus au 1er semestre", question: "Nombre total d'appartements vendus au 1er semestre 2020",
    lecture: "92 % des 34 169 ventes de l'extrait, les 2 791 autres sont des maisons : c'est une caractéristique de l'extrait, pas du marché français.",
    notes: "COUNT(*) sur les appartements, ventes sans valeur foncière comprises : une vente reste une vente." },
  { titre: "L'Île-de-France concentre 45 % des appartements vendus", question: "Nombre de ventes d'appartements par région",
    lecture: "13 995 ventes, loin devant Provence-Alpes-Côte d'Azur (3 649) et Auvergne-Rhône-Alpes (3 253). Mayotte et les collectivités d'outre-mer n'ont aucune vente.",
    notes: "17 régions sur 19 apparaissent : les deux autres sont dans la table region mais sans vente dans l'extrait." },
  { titre: "8 ventes sur 10 portent sur un 1 à 3 pièces", question: "Proportion des ventes d'appartements par nombre de pièces",
    lecture: "2 pièces 31,2 %, 3 pièces 28,6 %, studios 21,5 % ; 5 pièces et plus : 4,5 %. Les 30 ventes « 0 pièce » viennent de la source : signalées, pas corrigées.",
    notes: "Le dénominateur est le nombre de ventes d'appartements, calculé dans une sous-requête." },
  { titre: "Le m² parisien vaut 1,7 fois celui des Hauts-de-Seine", question: "Les 10 départements où le prix du m² est le plus élevé",
    lecture: "12 053 €/m² à Paris contre 7 219 dans le 92. En médiane, 9 départements sur 10 restent : le haut du classement est solide, la 10ᵉ place ne l'est pas.",
    notes: "Avec la médiane, la Gironde sort et la Charente-Maritime entre. Prix au m² = valeur foncière / surface Carrez." },
  { titre: "Une maison francilienne : 3 745 €/m² en moyenne", question: "Prix moyen du m² d'une maison en Île-de-France",
    lecture: "Sur 1 059 maisons, médiane 3 244 €/m² : trois fois moins que le m² parisien, car les maisons vendues sont presque toutes hors de Paris.",
    notes: "Filtre sur id_region = '11' : le référentiel écrit « Ile-de-France » sans accent, un filtre sur le nom serait fragile." },
  { titre: "Les 10 appartements les plus chers… dont un suspect", question: "Les 10 appartements les plus chers, avec leur région et leur surface",
    lecture: "Tous en Île-de-France. Le 1er coûte 9 M€ pour 9,10 m² Carrez avec un seul lot : erreur de saisie ou vente incomplète. On signale ces lignes.",
    notes: "Même doute pour Corbeil-Essonnes (8,6 M€ pour 64 m²). Impossible de trancher avec ces données : un analyste le dit." },
  { titre: "Le +3,68 % du T1 au T2 masque le creux d'avril", question: "Évolution du nombre de ventes entre le 1er et le 2ᵉ trimestre 2020",
    lecture: "16 776 puis 17 393 ventes, mais chute dès la mi-mars, creux en avril, rebond en mai-juin. La chute coïncide avec le premier confinement (17 mars - 11 mai) : à confirmer en comparant avec 2019.",
    notes: "La chute coïncide avec le premier confinement (17 mars - 11 mai). La date DVF est celle de l'acte notarié : le rebond peut refléter des signatures reportées. +3,87 % pour les seuls appartements.",
    chart: true, large: true },
  { titre: "Île-de-France en tête, des rangs suivants fragiles", question: "Régions classées par prix au m² des appartements de plus de 4 pièces",
    lecture: "8 770 €/m² sur 684 ventes en Île-de-France. Mais La Réunion est 2ᵉ sur 2 ventes : sous 30 ventes, un rang ne veut pas dire grand-chose.",
    notes: "Parmi les régions avec au moins 30 ventes : Île-de-France, PACA, Auvergne-Rhône-Alpes, Nouvelle-Aquitaine. Avec « 4 pièces et plus », une seule vente aberrante (1,31 m² Carrez à Orléans) fait passer le Centre-Val de Loire de 1 453 à plus de 3 300 €/m²." },
  { titre: "48 communes dépassent 50 ventes au 1er trimestre", question: "Communes ayant au moins 50 ventes au 1er trimestre",
    lecture: "Dont 19 arrondissements de Paris et 4 de Marseille, que DVF traite comme des communes. Hors Paris : Nice (173), Bordeaux (157), Nantes (119).",
    notes: "Groupement par clé commune et non par nom : 15 noms de communes sont des homonymes dans DVF." },
  { titre: "3 pièces : −12,4 % au m², surtout par la géographie", question: "Écart de prix au m² entre les appartements de 2 et de 3 pièces",
    lecture: "Le m² d'un 3 pièces coûte 4 300 €, contre 4 909 € pour un 2 pièces. Les 2 pièces sont plus souvent à Paris : à répartition géographique égale, l'écart tombe à environ 5 %.",
    notes: "À Paris seul, l'écart disparaît presque. Le sens du calcul compte : vu depuis le 3 pièces, le 2 pièces est 14,2 % plus cher. Médiane : −13,9 %.", large: true },
  { titre: "Top 3 par département : 5 communes sur une seule vente", question: "Les 3 communes à la valeur foncière moyenne la plus haute dans 5 départements",
    lecture: "5 des 15 communes n'ont qu'une seule vente : leur moyenne n'est pas « la » valeur de la commune. En gardant les communes d'au moins 5 ventes, le top 3 change : par exemple Cassis, Arcachon, Lyon 2ᵉ et 6ᵉ.",
    notes: "Départements 06, 13, 33, 59, 69. RANK() dans une fonction de fenêtre, partitionnée par département.", deuxSlides: true },
  { titre: "Paris 2ᵉ : 5,88 ventes de l'extrait pour 1 000 hab.", question: "Les 20 communes de plus de 10 000 habitants avec le plus de ventes pour 1 000 habitants",
    lecture: "Ratio interne à l'extrait, pas un taux réel. En tête : arrondissements centraux et communes littorales (La Baule, Arcachon). Pistes à vérifier : beaucoup de logements par habitant, des résidences secondaires.",
    notes: "Le ratio ne compare les communes qu'à l'intérieur de l'extrait : ce n'est pas un taux de transactions réel. Avec la population totale (PTOT), ce sont les mêmes 20 communes." },
];
// Largeurs de colonnes des résultats (somme = largeur du panneau : 5,23" à côté d'un SQL large, 5,83" sinon)
const COLW = {
  2: [3.4, 1.83], 3: [1.3, 1.6, 2.33], 4: [1.1, 2.3, 1.83], 5: [3.1, 2.13], 8: [0.6, 2.7, 1.13, 0.8], 9: [2.6, 0.9, 1.73],
  6: [1.25, 0.85, 0.7, 1.58, 1.45], 11: [0.6, 0.6, 2.2, 1.6, 0.83], 12: [1.8, 0.6, 1.1, 0.8, 1.53],
};

BESOINS.forEach((b, i) => {
  const n = i + 1, besoin = R.besoins[n];
  const lede = `Besoin ${n} · ${b.question}`;
  if (b.deuxSlides) {
    // Requête trop longue pour partager la slide : la requête seule, puis le résultat complet
    s = content("Les 12 besoins", `Besoin ${n} : un classement par département avec RANK()`, lede);
    sqlBlock(s, besoin.sql, { x: M, y: 1.8, w: W - 2 * M, h: 4.95, name: `sql-besoin-${n}` });
    s.addNotes(`Fichier sql/requetes/${besoin.fichier}. Deux CTE : la moyenne par commune, puis le rang dans le département.`);
    s = content("Les 12 besoins", b.titre, lede);
    resultTable(s, n, { x: M, y: 1.8, w: W - 2 * M, colW: [1.4, 0.9, 4.8, 2.83, 2.2], maxRows: besoin.nb_lignes,
      fontSize: 11, rowH: 0.24, name: `resultat-besoin-${n}` });
  } else if (b.large) {
    // Lignes de SQL longues : la requête sur toute la largeur, le résultat dessous
    const sqlH = b.chart ? 2.2 : 3.0;
    sqlBlock(s = content("Les 12 besoins", b.titre, lede), besoin.sql, { x: M, y: 1.8, w: W - 2 * M, h: sqlH, name: `sql-besoin-${n}` });
    resultTable(s, n, { x: M, y: 1.8 + sqlH + 0.15, w: 5.6, fontSize: 13, name: `resultat-besoin-${n}` });
  } else {
    s = content("Les 12 besoins", b.titre, lede);
    const sqlW = besoin.colonnes.length >= 5 ? 6.0 : 6.6;
    sqlBlock(s, besoin.sql, { x: M, y: 1.8, w: sqlW, h: 3.95, name: `sql-besoin-${n}` });
    const x = M + sqlW + 0.3, w = W - M - x;
    resultTable(s, n, { x, y: 1.8, w, colW: COLW[n], fontSize: besoin.colonnes.length >= 5 ? 10 : 12,
      name: `resultat-besoin-${n}` });
  }
  if (b.chart) {
    s.addChart(pres.charts.BAR, [{ name: "Ventes", labels: R.ventes_par_mois.map(([m]) => m),
      values: R.ventes_par_mois.map(([, v]) => v) }], {
      x: 6.5, y: 4.05, w: W - M - 6.5, h: 1.8, barDir: "col", chartColors: [THEME.colors.accent1], showValue: true, dataLabelFontSize: 10,
      dataLabelFormatCode: "# ##0", catAxisLabelFontSize: 11, valAxisHidden: true, valGridLine: { style: "none" },
      showTitle: true, title: "Ventes par mois (toutes ventes)", titleFontSize: 12, objectName: "graphique-ventes-mois" });
  }
  lecture(s, b.lecture, `lecture-besoin-${n}`);
  s.addNotes(`Fichier sql/requetes/${besoin.fichier}. ${b.notes}`);
});

// ================================================================== 22. Synthèse
pres.addSection({ title: "Conclusion" });
s = content("Conclusion", "Trois messages pour la direction",
  "La base répond aux 12 besoins, avec des volumes vérifiés et sans donnée personnelle superflue");
[
  ["L'extrait est dominé par l'Île-de-France", "45 % des appartements vendus ; en médiane, le m² parisien coûte 3,3 fois celui de l'extrait (11 094 contre 3 377 €)"],
  ["Comparer à géographie égale", "L'écart 2 / 3 pièces passe de −12 % à environ −5 % quand on neutralise la localisation"],
  ["Un semestre pas comme les autres", "Chute des ventes à la mi-mars, rebond en mai-juin : comparer avec 2019 avant de parler de tendance"],
].forEach(([k, v], i) => {
  const x = M + i * 4.1;
  card(s, { x, y: 2.0, w: 3.85, h: 3.6, name: `carte-message-${i}` });
  text(s, String(i + 1), { x: x + 0.3, y: 2.2, w: 1, h: 0.9, fontSize: 44, bold: true, color: i === 2 ? C.accent2 : C.accent1,
    fontFace: THEME.headFontFace, objectName: `message-numero-${i}` });
  text(s, k, { x: x + 0.3, y: 3.15, w: 3.3, h: 0.8, fontSize: 18, bold: true, color: C.text2, objectName: `message-titre-${i}` });
  text(s, v, { x: x + 0.3, y: 4.0, w: 3.3, h: 1.5, fontSize: 14, color: C.text1, objectName: `message-texte-${i}` });
});
s.addNotes("Les médianes viennent du notebook corrigé (SQLite n'a pas de fonction médiane). Trois messages, pas douze : " +
  "c'est ce que la direction retiendra.");

// ================================================================== 23. Limites
s = pres.addSlide({ masterName: "CONCLUSION_SOMBRE", sectionTitle: "Conclusion" });
s.addText("Limites et prochaines étapes", { placeholder: "title" });
[
  ["Erreurs de saisie", "Quelques prix au m² aberrants tirent les moyennes ; la médiane les neutralise"],
  ["Surface du 1er lot", "La surface ne compte que le 1er lot, le prix toute la vente : le m² est surestimé pour les ventes à plusieurs lots"],
  ["Petits effectifs", "Sous 30 ventes, un classement régional ou communal est peu fiable"],
].forEach(([k, v], i) => {
  const x = M + i * 4.1;
  card(s, { x, y: 1.6, w: 3.85, h: 2.4, fill: "1F4462", name: `carte-limite-${i}` });
  text(s, k, { x: x + 0.3, y: 1.85, w: 3.3, h: 0.5, fontSize: 19, bold: true, color: C.background1, objectName: `limite-titre-${i}` });
  text(s, v, { x: x + 0.3, y: 2.45, w: 3.3, h: 1.4, fontSize: 15, color: C.accent6, objectName: `limite-texte-${i}` });
});
text(s, "Prochaines étapes", { x: M, y: 4.4, w: 6, h: 0.5, fontSize: 22, bold: true, color: C.background1,
  fontFace: THEME.headFontFace, objectName: "etapes-titre" });
text(s, [
  { text: "Charger les années précédentes : le schéma est prêt, la comparaison avec 2019 devient possible", options: { bullet: { type: "number" }, breakLine: true } },
  { text: "Passer à un serveur (PostgreSQL) pour les accès simultanés et les droits par utilisateur", options: { bullet: { type: "number" }, breakLine: true } },
  { text: "Planifier la sauvegarde et tester sa restauration", options: { bullet: { type: "number" } } },
], { x: M, y: 5.0, w: W - 2 * M, h: 1.6, fontSize: 16, color: C.background1, paraSpaceAfter: 8, objectName: "etapes-liste" });
s.addNotes("Terminer sur les prochaines étapes, puis passer à la démonstration en direct des requêtes.");

(async () => {
  await pres.writeFile({ fileName: OUT });
  await setThemeColors(OUT, THEME);
  console.log("écrit", OUT);
})();
