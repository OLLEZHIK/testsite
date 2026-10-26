// Builds the sites in sites/<slug>/ (site.json + images) into dist/.
//
//   node build.mjs                    every site: dist/<slug>/ (previews) + dist/index.html
//   node build.mjs <slug> [<slug>..]  only these, into dist/<slug>/
//   SITE=<slug> node build.mjs        one site at the root of dist/ - the build
//                                     of a client's own deployment (vercel.json)
//
// No dependencies: Node 18+ only.
import fs from "node:fs";
import path from "node:path";
import { render } from "./template/page.mjs";

const root = path.dirname(new URL(import.meta.url).pathname);
const sitesDir = path.join(root, "sites");
const dist = path.join(root, "dist");
const css = fs.readFileSync(path.join(root, "template", "styles.css"), "utf8").replace(/\/\*[\s\S]*?\*\//g, "").replace(/\s*\n\s*/g, "\n");
const js = fs.readFileSync(path.join(root, "template", "script.js"), "utf8");

const single = process.env.SITE;
const all = fs.readdirSync(sitesDir).filter((d) => fs.existsSync(path.join(sitesDir, d, "site.json")));
const wanted = single ? [single] : process.argv.slice(2).length ? process.argv.slice(2) : all;

fs.rmSync(dist, { recursive: true, force: true });
fs.mkdirSync(dist, { recursive: true });

for (const slug of wanted) {
  const dir = path.join(sitesDir, slug);
  if (!fs.existsSync(path.join(dir, "site.json"))) {
    console.error(`No sites/${slug}/site.json`);
    process.exit(1);
  }
  const site = JSON.parse(fs.readFileSync(path.join(dir, "site.json"), "utf8"));
  // A client's own build (SITE=) is the live site: no preview banner.
  if (single && process.env.PREVIEW !== "1") site.preview = false;
  const out = single ? dist : path.join(dist, slug);
  fs.mkdirSync(out, { recursive: true });
  const canonical = site.domain ? `https://${site.domain.replace(/^https?:\/\//, "").replace(/\/$/, "")}/` : "";
  fs.writeFileSync(path.join(out, "index.html"), render(site, { css, js, canonical }));
  for (const f of fs.readdirSync(dir)) if (f !== "site.json") fs.copyFileSync(path.join(dir, f), path.join(out, f));
  console.log(`built ${slug} -> ${path.relative(root, out) || "dist"}/`);
}

// The root of the previews deployment lists nothing: every prospect gets
// only their own link and must not see who else got one.
if (!single) {
  fs.writeFileSync(
    path.join(dist, "index.html"),
    `<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex"><title>Website previews</title><body style="font-family:system-ui;padding:40px;color:#333">Website previews for local pet businesses.</body>`,
  );
}
