// The page: one function from site.json to a finished HTML file. Every text
// and colour comes from site.json; the template only decides the layout.
// Sections without data are left out (no hours -> no hours table).
import { icon } from "./icons.mjs";

const DAYS = [
  ["mo", "Monday"],
  ["tu", "Tuesday"],
  ["we", "Wednesday"],
  ["th", "Thursday"],
  ["fr", "Friday"],
  ["sa", "Saturday"],
  ["su", "Sunday"],
];
const SCHEMA_DAY = { mo: "Monday", tu: "Tuesday", we: "Wednesday", th: "Thursday", fr: "Friday", sa: "Saturday", su: "Sunday" };

const esc = (s) =>
  String(s ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");

const telHref = (phone) => `tel:${phone.replace(/[^\d+]/g, "")}`;
const smsHref = (phone) => `sms:${phone.replace(/[^\d+]/g, "")}`;

/** "+1 786-320-0218" -> "(786) 320-0218" */
function prettyPhone(phone) {
  const d = phone.replace(/\D/g, "");
  if (d.length === 11 && d.startsWith("1")) return `(${d.slice(1, 4)}) ${d.slice(4, 7)}-${d.slice(7)}`;
  return phone;
}

/** "08:00-19:00" -> "8:00 AM – 7:00 PM"; "closed" -> "Closed" */
function prettyHours(value) {
  if (!value || value === "closed") return "Closed";
  if (value === "24h") return "Open 24 hours";
  return value
    .split(",")
    .map((span) =>
      span
        .split("-")
        .map((t) => {
          const [h, m] = t.split(":").map(Number);
          const ampm = h >= 12 && h < 24 ? "PM" : "AM";
          const h12 = h % 12 === 0 ? 12 : h % 12;
          return `${h12}:${String(m).padStart(2, "0")} ${ampm}`;
        })
        .join(" – "),
    )
    .join(", ");
}

const fmtRating = (v) => Number(v).toFixed(1);

function stars(value) {
  const full = Math.round(value);
  return Array.from({ length: 5 }, (_, i) => icon("star", i < full ? "star on" : "star")).join("");
}

function jsonLd(site, url) {
  const c = site.contact ?? {};
  const data = {
    "@context": "https://schema.org",
    "@type": site.category === "vet" ? "VeterinaryCare" : "LocalBusiness",
    name: site.legalName ?? site.name,
    url: url || undefined,
    telephone: c.phone,
    email: c.email,
    image: site.logo ? `${url}${site.logo}` : undefined,
    // A mobile business often works from home: its street address only when shown on the page.
    address: c.address && c.showAddress !== false ? { "@type": "PostalAddress", streetAddress: c.address } : undefined,
    geo: c.geo ? { "@type": "GeoCoordinates", latitude: c.geo.lat, longitude: c.geo.lng } : undefined,
    areaServed: c.areaServed,
    sameAs: Object.values(site.social ?? {}).filter(Boolean),
    openingHoursSpecification: site.hours
      ? Object.entries(site.hours)
          .filter(([, v]) => v && v !== "closed")
          .flatMap(([d, v]) =>
            v.split(",").map((span) => {
              const [opens, closes] = span.split("-");
              return { "@type": "OpeningHoursSpecification", dayOfWeek: SCHEMA_DAY[d], opens, closes };
            }),
          )
      : undefined,
  };
  return JSON.stringify(data).replace(/</g, "\\u003c");
}

export function render(site, { css, js, canonical = "" }) {
  const c = site.contact ?? {};
  const phone = c.phone ? prettyPhone(c.phone) : "";
  const r = site.rating;
  const open7 = site.hours && DAYS.every(([d]) => site.hours[d] && site.hours[d] !== "closed");
  const title = `${site.name} | ${site.hero?.eyebrow ?? ""}`.replace(/ \| $/, "");
  const description = site.hero?.subtitle ?? "";
  const t = site.theme ?? {};

  const nav = `
  <header class="nav" id="top">
    <div class="wrap nav-in">
      <a class="brand" href="#top" aria-label="${esc(site.name)}">
        ${site.logo ? `<img src="${esc(site.logo)}" alt="${esc(site.name)}" height="40">` : `<span>${esc(site.name)}</span>`}
      </a>
      <nav class="links" aria-label="Sections">
        ${site.services?.length ? `<a href="#services">Services</a>` : ""}
        ${site.highlights ? `<a href="#reviews">Reviews</a>` : ""}
        ${site.hours ? `<a href="#hours">Hours</a>` : ""}
        <a href="#contact">Contact</a>
      </nav>
      ${phone ? `<a class="btn btn-dark btn-sm" href="${telHref(c.phone)}">${icon("phone")}<span>${esc(phone)}</span></a>` : ""}
    </div>
  </header>`;

  const chips = [
    site.mobile ? ["van", "We come to you"] : null,
    open7 ? ["calendar", "Open 7 days"] : null,
    r ? ["star", `${fmtRating(r.value)} on ${r.source}`] : null,
  ].filter(Boolean);

  const hero = `
  <section class="hero">
    <div class="glow g1"></div><div class="glow g2"></div>
    <div class="wrap hero-in">
      <div class="hero-copy">
        ${site.hero?.eyebrow ? `<p class="eyebrow"><span class="dot"></span>${esc(site.hero.eyebrow)}</p>` : ""}
        <h1>${esc(site.hero?.title ?? site.name)}</h1>
        ${site.hero?.subtitle ? `<p class="lead">${esc(site.hero.subtitle)}</p>` : ""}
        <div class="cta">
          ${phone ? `<a class="btn btn-dark" href="${telHref(c.phone)}">${icon("phone")}Call ${esc(phone)}</a>` : ""}
          ${phone ? `<a class="btn btn-ghost" href="${smsHref(c.phone)}">${icon("message")}Text us</a>` : ""}
        </div>
        <div class="proof">
          ${r ? `<a class="rating" href="${esc(r.url)}" target="_blank" rel="noopener"><span class="stars">${stars(r.value)}</span><strong>${fmtRating(r.value)}</strong><span>${r.count} ${esc(r.source)} reviews</span></a>` : ""}
          ${site.hours ? `<span class="status" data-status>${icon("clock")}<span>Hours below</span></span>` : ""}
        </div>
      </div>
      <div class="hero-art" aria-hidden="true">
        <div class="logo-card">
          ${site.logo ? `<img src="${esc(site.logo)}" alt="">` : `<span class="logo-text">${esc(site.name)}</span>`}
          <div class="paws">${icon("paw")}${icon("heart")}${icon("sparkles")}</div>
        </div>
        ${chips.map(([ic, text], i) => `<div class="chip chip-${i + 1}">${icon(ic)}<span>${esc(text)}</span></div>`).join("")}
      </div>
    </div>
  </section>`;

  const facts = [
    r ? [`${fmtRating(r.value)}★`, `rating on ${r.source}`] : null,
    r ? [String(r.count), "reviews from pet parents"] : null,
    open7 ? ["7 days", "a week"] : null,
    c.areaServed ? [site.mobile ? "At home" : "Local", c.areaServed] : null,
  ].filter(Boolean);
  const factsBar = facts.length
    ? `<section class="wrap facts" style="grid-template-columns:repeat(${facts.length},1fr)">${facts.map(([big, small]) => `<div><strong>${esc(big)}</strong><span>${esc(small)}</span></div>`).join("")}</section>`
    : "";

  const services = site.services?.length
    ? `
  <section class="wrap section" id="services">
    <p class="kicker">Services</p>
    <h2>Everything your pet needs${site.mobile ? ", at home" : ""}.</h2>
    <div class="grid services">
      ${site.services
        .map(
          (s) => `<article class="card service">
        <div class="ic">${icon(s.icon)}</div>
        <h3>${esc(s.name)}</h3>
        <p>${esc(s.text)}</p>
        ${s.price ? `<p class="price">${esc(s.price)}</p>` : ""}
      </article>`,
        )
        .join("")}
    </div>
  </section>`
    : "";

  const steps = site.steps?.length
    ? `
  <section class="wrap section">
    <p class="kicker">How it works</p>
    <h2>Three easy steps.</h2>
    <ol class="steps">
      ${site.steps.map((s, i) => `<li><span class="num">${i + 1}</span><h3>${esc(s.title)}</h3><p>${esc(s.text)}</p></li>`).join("")}
    </ol>
  </section>`
    : "";

  const h = site.highlights;
  const highlights = h?.items?.length
    ? `
  <section class="dark" id="reviews">
    <div class="wrap section">
      <p class="kicker">Reviews</p>
      <h2>${esc(h.title)}</h2>
      <div class="grid quotes">
        ${h.items
          .map(
            (q) => `<figure class="quote">
          <span class="stars">${stars(5)}</span>
          <figcaption>${esc(q.title)}</figcaption>
          <blockquote>${esc(q.text)}</blockquote>
        </figure>`,
          )
          .join("")}
      </div>
      ${r ? `<p class="source">${h.basedOn ? `Summarised from ${h.basedOn} recent reviews. ` : ""}<a href="${esc(r.url)}" target="_blank" rel="noopener">Read all ${r.count} reviews on ${esc(r.source)} ${icon("arrow")}</a></p>` : ""}
    </div>
  </section>`
    : "";

  const hours = site.hours
    ? `
    <div class="card hours" id="hours">
      <div class="card-head">${icon("clock")}<h3>Opening hours</h3><span class="status" data-status></span></div>
      <table>
        ${DAYS.map(([d, label]) => `<tr data-day="${d}"><th>${label}</th><td>${esc(prettyHours(site.hours[d]))}</td></tr>`).join("")}
      </table>
    </div>`
    : "";

  // Without the address on the page the map shows the area, not the house.
  const mapSrc = c.geo ? `https://www.google.com/maps?q=${c.geo.lat},${c.geo.lng}&z=${c.showAddress === false ? 11 : 15}&output=embed` : "";
  const contact = `
  <section class="wrap section" id="contact">
    <p class="kicker">Contact</p>
    <h2>Book your pet's next visit.</h2>
    <div class="grid contact">
      <div class="card contact-card">
        ${phone ? `<a class="line" href="${telHref(c.phone)}">${icon("phone")}<span><small>Call or text</small>${esc(phone)}</span></a>` : ""}
        ${c.email ? `<a class="line" href="mailto:${esc(c.email)}">${icon("mail")}<span><small>Email</small>${esc(c.email)}</span></a>` : ""}
        ${c.address && c.showAddress !== false ? `<div class="line">${icon("pin")}<span><small>Address</small>${esc(c.address)}</span></div>` : ""}
        ${c.areaServed ? `<div class="line">${icon(site.mobile ? "van" : "home")}<span><small>${site.mobile ? "We visit" : "Serving"}</small>${esc(c.areaServed)}</span></div>` : ""}
        <div class="social">
          ${site.social?.instagram ? `<a href="${esc(site.social.instagram)}" target="_blank" rel="noopener" aria-label="Instagram">${icon("instagram")}</a>` : ""}
          ${site.social?.facebook ? `<a href="${esc(site.social.facebook)}" target="_blank" rel="noopener" aria-label="Facebook">${icon("facebook")}</a>` : ""}
        </div>
      </div>
      ${hours}
    </div>
    ${mapSrc ? `<div class="map"><iframe title="Map" src="${mapSrc}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></div>` : ""}
  </section>`;

  const faq = site.faq?.length
    ? `
  <section class="wrap section narrow">
    <p class="kicker">FAQ</p>
    <h2>Good to know.</h2>
    <div class="faq">
      ${site.faq.map((f, i) => `<details${i === 0 ? " open" : ""}><summary>${esc(f.q)}<span class="plus"></span></summary><p>${esc(f.a)}</p></details>`).join("")}
    </div>
  </section>`
    : "";

  const finalCta = phone
    ? `
  <section class="wrap">
    <div class="band">
      <div>
        <h2>Ready for a fresh, happy pet?</h2>
        <p>${open7 ? "We are available every day of the week." : "Call us to book a time that suits you."}</p>
      </div>
      <a class="btn btn-dark" href="${telHref(c.phone)}">${icon("phone")}Call ${esc(phone)}</a>
    </div>
  </section>`
    : "";

  const o = site.offer ?? {};
  const banner = site.preview
    ? `<div class="preview-bar"><div class="wrap preview-in">
      <p><strong>Preview built for ${esc(site.legalName ?? site.name)}.</strong> This site is not live yet. Make it yours for ${esc(o.price ?? "")}${o.includes ? `, ${esc(o.includes)} included` : ""}.</p>
      ${o.payUrl ? `<a class="btn btn-light btn-sm" href="${esc(o.payUrl)}">Claim this site ${icon("arrow")}</a>` : o.contact ? `<a class="btn btn-light btn-sm" href="mailto:${esc(o.contact)}?subject=${encodeURIComponent(`Website for ${site.name}`)}">Claim this site ${icon("arrow")}</a>` : ""}
    </div></div>`
    : "";

  const mobileBar = phone
    ? `<div class="mobile-bar"><a class="btn btn-dark" href="${telHref(c.phone)}">${icon("phone")}Call</a><a class="btn btn-ghost" href="${smsHref(c.phone)}">${icon("message")}Text</a></div>`
    : "";

  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(title)}</title>
<meta name="description" content="${esc(description)}">
${site.preview ? '<meta name="robots" content="noindex, nofollow">' : canonical ? `<link rel="canonical" href="${esc(canonical)}">` : ""}
<meta property="og:title" content="${esc(site.name)}">
<meta property="og:description" content="${esc(description)}">
<meta property="og:type" content="website">
${site.logo ? `${canonical ? `<meta property="og:image" content="${esc(canonical + site.logo)}">` : ""}<link rel="icon" href="${esc(site.logo)}">` : ""}
<meta name="theme-color" content="${esc(t.surface ?? "#ffffff")}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>:root{--accent:${t.accent ?? "#2f80ed"};--accent-deep:${t.accentDeep ?? t.accent ?? "#1c5fbf"};--ink:${t.ink ?? "#15171c"};--surface:${t.surface ?? "#fafaf7"}}
${css}</style>
<script type="application/ld+json">${jsonLd(site, canonical)}</script>
</head>
<body>
${banner}
${nav}
<main>
${hero}
${factsBar}
${services}
${steps}
${highlights}
${contact}
${faq}
${finalCta}
</main>
<footer class="footer">
  <div class="wrap foot-in">
    <p>© <span data-year>${new Date().getFullYear()}</span> ${esc(site.legalName ?? site.name)}</p>
    <p class="made">Website by <a href="https://pawenn.com" target="_blank" rel="noopener">Pawenn</a></p>
  </div>
</footer>
${mobileBar}
<script>window.SITE_HOURS=${JSON.stringify(site.hours ?? null)};window.SITE_TZ=${JSON.stringify(site.timezone ?? "America/New_York")};
${js}</script>
</body>
</html>
`;
}
