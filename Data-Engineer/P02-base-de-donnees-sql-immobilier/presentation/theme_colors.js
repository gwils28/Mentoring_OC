// pptxgenjs écrit toujours la palette Office par défaut dans ppt/theme/theme1.xml :
// on y remplace les 12 couleurs du thème pour que les couleurs « de schéma » des slides suivent notre charte.
const fs = require("fs");
const JSZip = require("jszip");

const SLOTS = ["dk1", "lt1", "dk2", "lt2", "accent1", "accent2", "accent3", "accent4", "accent5", "accent6", "hlink", "folHlink"];

async function setThemeColors(file, theme) {
  const zip = await JSZip.loadAsync(fs.readFileSync(file));
  const part = "ppt/theme/theme1.xml";
  let xml = await zip.file(part).async("string");
  for (const slot of SLOTS) {
    const hex = theme.colors[slot];
    if (!/^[0-9A-Fa-f]{6}$/.test(hex)) throw new Error(`Couleur invalide pour ${slot} : ${hex}`);
    const re = new RegExp(`<a:${slot}>[\\s\\S]*?</a:${slot}>`);
    if (!re.test(xml)) throw new Error(`Emplacement ${slot} introuvable dans ${part}`);
    xml = xml.replace(re, `<a:${slot}><a:srgbClr val="${hex.toUpperCase()}"/></a:${slot}>`);
  }
  const name = theme.name.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");
  xml = xml.replace(/<a:clrScheme name="[^"]*">/, `<a:clrScheme name="${name}">`);
  zip.file(part, xml);
  fs.writeFileSync(file, await zip.generateAsync({ type: "nodebuffer", compression: "DEFLATE" }));
}

module.exports = { setThemeColors };
