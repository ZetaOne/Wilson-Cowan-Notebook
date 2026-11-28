// Build the Wilson–Cowan book: Markdown chapters (+ KaTeX maths, boxes, figures)
// -> one HTML file (rendered-anims/wilson-cowan/book/wc-book.html) and,
// with --pdf, a PDF printed by headless Chrome.
//
//   node scripts/wilson-cowan/book/build.mjs [--pdf]
//
// Markdown extensions
//   $...$, $$...$$                       maths (KaTeX, rendered here: no JS in the page)
//   :::kind Title  ...  :::              boxes: def thm idea ex warn paper key try
//   ::fig name | caption                  figure from figs/manifest.json (png/svg/gif + code link)
//   ::deck                                link to this chapter's slide deck
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "../../..");
const NODE = path.join(ROOT, "sci-anim-tools/node/node_modules");
const require = createRequire(path.join(NODE, "x.js"));
const katex = require("katex");
const { marked } = await import(path.join(NODE, "marked/lib/marked.esm.js"));

const OUT = path.join(ROOT, "rendered-anims/wilson-cowan/book");
const book = JSON.parse(fs.readFileSync(path.join(HERE, "book.json"), "utf8"));
const manifestPath = path.join(OUT, "figs/manifest.json");
const manifest = fs.existsSync(manifestPath) ? JSON.parse(fs.readFileSync(manifestPath, "utf8")) : {};

const MACROS = {
  "\\R": "\\mathbb{R}", "\\dd": "\\mathrm{d}", "\\e": "\\mathrm{e}",
  "\\Gam": "\\Gamma", "\\ph": "\\vartheta", "\\Wss": "W^{ss}", "\\Ws": "W^{s}", "\\Wu": "W^{u}",
};

const missingFigs = new Set();
let figCount = 0;

function renderMath(src) {
  // protect code spans/blocks, then render $$..$$ and $..$
  const store = [];
  const keep = (s) => { store.push(s); return `\u0000${store.length - 1}\u0000`; };
  const code = [];
  const keepCode = (s) => { code.push(s); return `\u0001${code.length - 1}\u0001`; };
  src = src.replace(/```[\s\S]*?```/g, keepCode).replace(/`[^`\n]+`/g, keepCode);
  src = src.replace(/\$\$([\s\S]+?)\$\$/g, (_, tex) =>
    keep(`<div class="math-display">${katex.renderToString(tex.trim(), { displayMode: true, throwOnError: false, macros: { ...MACROS }, strict: "ignore", trust: true })}</div>`));
  src = src.replace(/(^|[^\\$])\$([^\s$](?:[^$\n]*?[^\s\\$])?)\$/g, (_, pre, tex) =>
    pre + keep(katex.renderToString(tex, { throwOnError: false, macros: { ...MACROS }, strict: "ignore" })));
  src = src.replace(/\u0001(\d+)\u0001/g, (_, i) => code[+i]);   // code goes back to Markdown, maths stays protected
  return { src, restore: (html) => html.replace(/\u0000(\d+)\u0000/g, (_, i) => store[+i]) };
}

const BOX = {
  def: "Definition", thm: "Theorem", idea: "The idea", ex: "Example", warn: "Careful",
  paper: "In the paper", key: "Key point", try: "Try it", recap: "Recap", note: "Note",
};

function figureHTML(name, caption, chap) {
  const f = manifest[name];
  figCount += 1;
  const num = `${chap.num}.${chap.fig = (chap.fig || 0) + 1}`;
  if (!f) {
    missingFigs.add(name);
    return `<figure class="missing"><div class="ph">figure “${name}” not built yet</div><figcaption><b>Figure ${num}.</b> ${caption}</figcaption></figure>`;
  }
  const code = f.script ? ` <a class="code" href="code/${f.script.replace(/\.py$/, ".html")}" target="_blank">code ↗</a>` : "";
  const cls = f.wide ? "wide" : "";
  let img;
  if (f.gif) {
    img = `<img class="screen" src="figs/${f.gif}" alt="${name}" loading="lazy"><img class="print" src="figs/${f.still || f.file}" alt="${name}">`;
  } else {
    img = `<img src="figs/${f.file}" alt="${name}" loading="lazy">`;
  }
  const anim = f.gif ? ` <span class="animtag">animated</span>` : "";
  return `<figure id="fig-${name}" class="${cls}">${img}<figcaption><b>Figure ${num}.</b> ${caption}${anim}${code}</figcaption></figure>`;
}

function preprocess(md, chap) {
  // ::fig name | caption
  md = md.replace(/^::fig\s+([\w.-]+)\s*\|\s*(.+)$/gm, (_, n, c) => `\n\n<!--FIG:${n}|${c}-->\n\n`);
  md = md.replace(/^::deck\s*$/gm, () => `\n\n<!--DECK-->\n\n`);
  // :::kind Title ... :::  (not nested)
  md = md.replace(/^:::(\w+)[ \t]*(.*)\n([\s\S]*?)^:::[ \t]*$/gm, (_, kind, title, body) =>
    `\n\n<!--BOX:${kind}|${title.trim()}-->\n\n${body}\n\n<!--/BOX-->\n\n`);
  return md;
}

function postprocess(html, chap) {
  html = html.replace(/<!--FIG:([\w.-]+)\|([\s\S]*?)-->/g, (_, n, c) => figureHTML(n, marked.parseInline(c), chap));
  html = html.replace(/<!--DECK-->/g, () =>
    `<p class="decklink"><a href="decks/${chap.id}/wc-${chap.id}_deck.html" target="_blank">▶ Open the slide deck for this chapter</a></p>`);
  html = html.replace(/<!--BOX:(\w+)\|(.*?)-->/g, (_, kind, title) => {
    const label = BOX[kind] || kind;
    const t = title ? `<span class="box-label">${label}</span> ${marked.parseInline(title)}` : `<span class="box-label">${label}</span>`;
    return `<div class="box ${kind}"><div class="box-title">${t}</div>`;
  });
  // close boxes: details for try, div otherwise (track a stack)
  const stack = [];
  html = html.replace(/<!--\/BOX-->/g, () => "</div>");
  // number h2/h3 inside the chapter
  let s2 = 0, s3 = 0;
  html = html.replace(/<h2>(.*?)<\/h2>/g, (_, t) => { s2++; s3 = 0; const id = `${chap.id}-s${s2}`; chap.secs.push({ id, t: `${chap.num}.${s2} ${t}` }); return `<h2 id="${id}"><span class="secnum">${chap.num}.${s2}</span> ${t}</h2>`; });
  html = html.replace(/<h3>(.*?)<\/h3>/g, (_, t) => { s3++; return `<h3><span class="secnum">${chap.num}.${s2}.${s3}</span> ${t}</h3>`; });
  return html;
}

marked.setOptions({ gfm: true, breaks: false });

let body = "";
let toc = "";
let chapNum = 0;
for (const part of book.parts) {
  toc += `<li class="toc-part"><a href="#${part.id}">${part.title}</a><ol>`;
  body += `<section class="part" id="${part.id}"><div class="part-kicker">${part.kicker}</div><h1 class="part-title">${part.title}</h1><p class="part-blurb">${part.blurb}</p></section>`;
  for (const ch of part.chapters) {
    const isApp = ch.appendix;
    const num = isApp ? ch.letter : String(++chapNum);
    const chap = { id: ch.id, num, secs: [], fig: 0 };
    const file = path.join(HERE, "chapters", `${ch.id}.md`);
    let md = fs.existsSync(file) ? fs.readFileSync(file, "utf8") : `*This chapter is being written.*`;
    md = preprocess(md, chap);
    const { src, restore } = renderMath(md);
    let html = restore(marked.parse(src));
    html = postprocess(html, chap);
    const kicker = isApp ? `Appendix ${num}` : `Chapter ${num}`;
    body += `<section class="chapter" id="${ch.id}"><header class="chap-head"><div class="chap-kicker">${kicker}</div>${isApp ? `<h1>${ch.title}</h1>` : `<h1><a class="decklink-h" href="decks/${ch.id}/wc-${ch.id}_deck.html" target="_blank" title="Open the slide deck for this chapter">${ch.title}<span class="deckicon"> ▶ slides</span></a></h1>`}${ch.subtitle ? `<p class="chap-sub">${ch.subtitle}</p>` : ""}</header>${html}</section>`;
    toc += `<li><a href="#${ch.id}"><span class="tocnum">${num}</span> ${ch.title}</a></li>`;
  }
  toc += `</ol></li>`;
}

const css = fs.readFileSync(path.join(HERE, "style.css"), "utf8");
const page = `<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${book.title}</title>
<link rel="stylesheet" href="assets/katex/katex.min.css">
<style>${css}</style>
</head><body>
<nav id="side"><div class="side-title">${book.short}</div><ol class="toc">${toc}</ol></nav>
<main>
<section class="cover">
  <div class="cover-kicker">${book.kicker}</div>
  <h1 class="cover-title">${book.title}</h1>
  <p class="cover-sub">${book.subtitle}</p>
  <div class="cover-art"><img src="figs/${(manifest["cover"] || {}).file || "ch06_fig11.png"}" alt=""></div>
  <p class="cover-meta">${book.meta}</p>
</section>
<section class="toc-page"><h1>Contents</h1><ol class="toc big">${toc}</ol></section>
${body}
</main>
</body></html>`;

fs.mkdirSync(OUT, { recursive: true });
// KaTeX css + fonts next to the book (works offline)
const kdst = path.join(OUT, "assets/katex");
fs.mkdirSync(path.join(kdst, "fonts"), { recursive: true });
fs.copyFileSync(path.join(NODE, "katex/dist/katex.min.css"), path.join(kdst, "katex.min.css"));
for (const f of fs.readdirSync(path.join(NODE, "katex/dist/fonts")))
  fs.copyFileSync(path.join(NODE, "katex/dist/fonts", f), path.join(kdst, "fonts", f));
const htmlPath = path.join(OUT, "wc-book.html");
fs.writeFileSync(htmlPath, page);
console.log(`wrote ${htmlPath} (${chapNum} chapters, ${figCount} figures)`);
if (missingFigs.size) console.log("missing figures:", [...missingFigs].join(", "));

if (process.argv.includes("--pdf")) {
  const pdf = path.join(OUT, "wc-book.pdf");
  const chrome = process.env.SCIVIZ_CHROME || "/usr/bin/google-chrome";
  execFileSync(chrome, ["--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=20000",
    `--print-to-pdf=${pdf}`, "file://" + htmlPath], { stdio: "inherit" });
  console.log("wrote", pdf);
  execFileSync(path.join(ROOT, ".venv/bin/python"), [path.join(HERE, "relink_pdf.py"), pdf], { stdio: "inherit" });
}
