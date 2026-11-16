#!/usr/bin/env python3
"""Generate preview sites from Pawenn data with the salon template (v2/salon).

Usage: python3 v2/gen/make.py <slug> [<slug> ...]
Reads ../shop/data/cities/*/businesses-*.csv and review-insights; writes v2/p/<slug>/index.html.
Only facts from Pawenn data (each one already backed by the business's site or Google listing).
"""
import csv, glob, hashlib, html, json, os, re, sys
from urllib.parse import quote, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.environ.get("PAWENN_DATA", "/home/user/shop/data/cities")
OUT = os.path.join(ROOT, "v2", "p")

PALETTES = [  # ink, ink-soft, accent, accent-deep, tint, surface, line, display font, text font, google fonts query, hero radius
    ("#1e2238", "#4d5270", "#3b5bdb", "#2b44ad", "#e8edff", "#f5f7ff", "#e1e6f8", "Fredoka", "Nunito Sans", "Fredoka:wght@500;600&family=Nunito+Sans:wght@400;600;700", "48% 48% 32px 32px / 34% 34% 32px 32px"),
    ("#172440", "#4b5568", "#c2382f", "#9a2a23", "#fbe9e7", "#f4f4f2", "#e3e3df", "Bricolage Grotesque", "Schibsted Grotesk", "Bricolage+Grotesque:opsz,wght@12..96,500..800&family=Schibsted+Grotesk:wght@400;500;700", "28px 28px 28px 160px"),
    ("#1d2a24", "#4f5d55", "#2f6b4f", "#1f4d3a", "#e6f1ea", "#f3f5f2", "#dfe6e0", "Gloock", "Karla", "Gloock&family=Karla:wght@400;500;700", "28px"),
    ("#24182c", "#5a4d62", "#6b3fa0", "#522c7d", "#f1eaf8", "#f7f4fa", "#e7dfee", "DM Serif Text", "Source Sans 3", "DM+Serif+Text:ital@0;1&family=Source+Sans+3:wght@400;600;700", "50% 50% 28px 28px / 40% 40% 28px 28px"),
    ("#15161a", "#4d4f57", "#c2410c", "#9a3412", "#fdeee6", "#f4f4f5", "#e4e4e7", "Archivo", "Archivo", "Archivo:wdth,wght@62..125,400..900", "8px"),
    ("#1f1b1c", "#544c4e", "#a3214a", "#7d1838", "#f9e8ee", "#f6f3f4", "#ebe0e4", "Newsreader", "Public Sans", "Newsreader:ital,opsz,wght@0,6..72,400..700;1,6..72,400..600&family=Public+Sans:wght@400;600;700", "22px 22px 22px 140px"),
    ("#13293d", "#4a5b6b", "#0f766e", "#115e59", "#e2f3f1", "#f2f6f7", "#dbe5e8", "Young Serif", "Figtree", "Young+Serif&family=Figtree:wght@400;600;700", "200px 200px 28px 28px"),
]
IMAGES = {"grooming": ["salon-doodle.jpg", "salon-towel.jpg"], "mobile": ["paw.jpg"], "vet": ["vet-exam.jpg"], "sitting": ["cat.jpg", "maltese.jpg"],
          "training": ["maltese.jpg"], "hotel": ["salon-towel.jpg", "maltese.jpg"]}
DAYS = ["mo", "tu", "we", "th", "fr", "sa", "su"]
SIZES = [{"id": "s", "label": "Small", "note": "up to 20 lb", "word": "small"}, {"id": "m", "label": "Medium", "note": "21 to 40 lb", "word": "medium"},
         {"id": "l", "label": "Large", "note": "41 to 60 lb", "word": "large"}, {"id": "xl", "label": "X-Large", "note": "61 lb and up", "word": "extra large"}]
SERVICES = {
    "grooming": [("groom", "Full groom", "a full groom"), ("bath", "Bath and brush", "a bath and brush-out"), ("cut", "Haircut", "a haircut"), ("nails", "Nails", "a nail trim")],
    "vet": [("check", "Checkup", "a checkup"), ("vacc", "Vaccines", "vaccines"), ("sick", "Sick visit", "a sick visit"), ("dental", "Dental", "a dental consult")],
    "sitting": [("visit", "Drop-in visits", "drop-in visits"), ("walk", "Dog walks", "dog walks"), ("stay", "Overnight stay", "an overnight stay")],
    "training": [("puppy", "Puppy training", "puppy training"), ("obed", "Obedience", "obedience training"), ("behav", "Behavior help", "help with behavior")],
    "hotel": [("board", "Boarding", "boarding"), ("day", "Daycare", "daycare"), ("groom", "Grooming", "grooming")],
}
NOUN = {"grooming": "groom", "vet": "visit", "sitting": "booking", "training": "session", "hotel": "stay"}
KIND = {"grooming": "Dog grooming", "vet": "Veterinary care", "sitting": "Pet sitting", "training": "Dog training", "hotel": "Boarding and daycare"}

e = html.escape


def load(slug):
    for f in glob.glob(f"{DATA}/*/businesses-*.csv"):
        for r in csv.DictReader(open(f, encoding="utf-8")):
            if r["slug"] == slug:
                city = f.split("/")[-2]
                cat = f.split("-")[-1][:-4]
                ins_p = f"{DATA}/{city}/review-insights/{slug}.json"
                ins = json.load(open(ins_p)) if os.path.exists(ins_p) else None
                cj = json.load(open(f"{DATA}/{city}/city.json")) if os.path.exists(f"{DATA}/{city}/city.json") else {}
                return r, city, cat, ins, cj
    extra = os.path.join(os.path.dirname(os.path.abspath(__file__)), "extra", slug + ".json")
    if os.path.exists(extra):  # places that are not on Pawenn yet (Maps candidates + their own site)
        r = json.load(open(extra))
        city = r["city"]
        cj = json.load(open(f"{DATA}/{city}/city.json")) if os.path.exists(f"{DATA}/{city}/city.json") else {}
        return r, city, r["cat"], None, cj
    raise SystemExit(f"not found: {slug}")


def hours_cfg(s):
    if not s or "appointment" in s:
        return None
    out = {}
    for part in s.split(";"):
        part = part.strip()
        if not part:
            continue
        d, _, v = part.partition(" ")
        if d in DAYS:
            out[str((DAYS.index(d) + 1) % 7)] = v.strip() if v.strip() != "closed" else "closed"
    return out or None


def phone_parts(p):
    digits = re.sub(r"\D", "", p or "")
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) != 10:
        return None, p
    return "+1" + digits, f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"


def tz_for(city, cj):
    return cj.get("timezone") or {"miami": "America/New_York", "new-york": "America/New_York", "philadelphia": "America/New_York",
                                  "chicago": "America/Chicago", "houston": "America/Chicago", "dallas": "America/Chicago", "san-antonio": "America/Chicago",
                                  "phoenix": "America/Phoenix", "los-angeles": "America/Los_Angeles", "san-diego": "America/Los_Angeles"}.get(city, "America/New_York")


SHORT = {"Kara’s K9 Retreat Daycare Boarding and Grooming": "Kara’s K9 Retreat", "Keke and Fetch Dog Walking and Cat Boarding": "Keke and Fetch"}


def short_name(name):
    if name in SHORT:
        return SHORT[name]
    n = re.split(r"\s[-|–]\s|\s\|\s|,|\s@", name)[0].strip()
    return n[:-1] if n.endswith(".") else n


def make(slug, angle="nosite"):
    r, city, cat, ins, cj = load(slug)
    name = r["name"].strip().rstrip(".")
    sname = short_name(name)
    mobile = r.get("home_visits") in ("yes", "true", "1") or "mobile" in name.lower()
    h = int(hashlib.md5(slug.encode()).hexdigest(), 16)
    P = PALETTES[h % len(PALETTES)]
    imgs = IMAGES["mobile" if (mobile and cat == "grooming") else cat] if cat in IMAGES else IMAGES["grooming"]
    img = imgs[h % len(imgs)]
    tel, tel_label = phone_parts(r["phone"])
    hours = hours_cfg(r["opening_hours"])
    tz = tz_for(city, cj)
    city_name = cj.get("name_en") or cj.get("name") or city.replace("-", " ").title()
    if isinstance(city_name, dict):
        city_name = city_name.get("en") or city.replace("-", " ").title()
    rating, count = r["google_rating"], r["google_rating_count"]
    cards = [c for c in (ins or {}).get("cards", []) if c.get("sentiment") == "positive"][:3]
    faq = [q for q in (ins or {}).get("faq", []) if q.get("basis") in ("site", "both")][:3] or (ins or {}).get("faq", [])[:2]
    email = r["email"]
    site = r["website"]
    domain = urlparse(site if "//" in site else "http://" + site).netloc.replace("www.", "") if site else ""
    d_low = (r["description"] or "").lower()
    KEYS = [("walk", "Dog walks", "dog walks", ("walk",)), ("visit", "Drop-in visits", "drop-in visits", ("drop-in", "visit", "sitting")),
            ("stay", "Overnight stay", "an overnight stay", ("overnight", "house sitting", "in-home")), ("board", "Boarding", "boarding", ("boarding", "board")),
            ("day", "Daycare", "daycare", ("daycare", "day care")), ("groom", "Grooming", "grooming", ("groom",)), ("bath", "Bath", "a bath", ("bath",)),
            ("puppy", "Puppy training", "puppy training", ("puppy",)), ("obed", "Obedience", "obedience training", ("obedience",)),
            ("behav", "Behavior help", "help with behavior", ("behavio",)), ("protect", "Protection training", "protection training", ("protection",))]
    if cat in ("hotel", "sitting", "training"):
        svc = [{"id": a, "label": b, "phrase": c} for a, b, c, ks in KEYS if any(k in d_low for k in ks)]
        svc = svc or [{"id": a, "label": b, "phrase": c} for a, b, c in SERVICES[cat][:1]]
    else:
        svc = [{"id": a, "label": b, "phrase": c} for a, b, c in SERVICES.get(cat, SERVICES["grooming"])]
    pets = {"dog": {"label": "Dog", "noun": "dog", "sizes": SIZES if cat in ("grooming", "hotel") and any(x["id"] in ("groom", "bath", "board", "day") for x in svc) else None,
                    "services": svc}}
    if cat in ("vet", "sitting") or re.search(r"\bcats?\b", d_low):
        pets["cat"] = {"label": "Cat", "noun": "cat", "sizes": None, "services": [s for s in pets["dog"]["services"] if s["id"] not in ("walk", "cut")]}
    cfg = {"tz": tz, "hours": hours or {}, "phone": tel or "", "phoneLabel": tel_label, "address": r["address"],
           "lat": None if (mobile or not r["lat"]) else float(r["lat"]), "lng": None if (mobile or not r["lng"]) else float(r["lng"]),
           "pin": sname, "thumbHideOn": "book",
           "composer": {"greeting": f"Hi {sname}!", "pets": pets}}
    kind = KIND.get(cat, "Pet care")
    where = f"{kind}{', mobile' if mobile else ''} in {city_name}"
    desc = (r["description"] or "").strip()
    first_card = cards[0]["text"]["en"].split(". ")[0] + "." if cards else desc
    rating_line = f'<p class="hero-rating"><span class="stars" aria-hidden="true">★★★★★</span> {e(rating)} on Google from {int(count):,} reviews</p>' if rating else ""
    voices = "".join(f'<blockquote><strong>{e(c["title"]["en"])}</strong><p>{e(c["text"]["en"])}</p></blockquote>' for c in cards)
    faq_html = "".join(f'<details><summary>{e(q["q"]["en"])}</summary><p>{e(q["a"]["en"])}</p></details>' for q in faq)
    hours_block = '<table class="hours" id="hours"></table>' if hours else '<p class="find-note"><strong>By appointment.</strong> Send a text or call to book a time.</p>'
    status_block = '<div class="status" id="status" aria-live="polite"><span class="status-dot" aria-hidden="true"></span><div><p class="status-main"></p><p class="status-sub"></p></div></div>' if hours else ""
    find_right = (f'<div class="map-wrap"><div class="map" id="map" role="region" aria-label="Map: {e(r["address"])}"></div></div>' if cfg["lat"] is not None
                  else f'<div class="find-info" style="justify-self:start;background:var(--ink);color:#fff;max-width:none"><h2 style="color:#fff">{"We come to you" if mobile else e(city_name)}</h2><p class="find-note" style="color:rgba(255,255,255,.82)">{e(desc)}</p></div>')
    directions = f'https://www.google.com/maps/dir/?api=1&destination={quote(name + ", " + r["address"])}' + (f'&destination_place_id={r["google_place_id"]}' if r.get("google_place_id") else "")
    if angle == "outdated" and domain:
        offer_left = f"""<h3>What it adds to {e(domain)}</h3><ul><li>A layout built for phones first</li><li>Open or closed right now, from your own hours</li><li>New clients send you a ready request in a few taps</li><li>What your reviews say, on the first page</li><li>Details marked up for Google search</li></ul>"""
        live = f"Live on your current domain, {e(domain)}, within a week"
    else:
        offer_left = """<h3>What a website adds</h3><ul><li>A home people find on Google, with your hours and address marked up for search</li><li>New clients send you a ready request in a few taps</li><li>Open or closed right now, a map and one-tap directions</li><li>What your reviews say, on the first page</li></ul>"""
        live = "Live on your own domain within a week"
    title = f"{name} | {where}"
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{e(title)}</title>
<meta name="description" content="{e(desc[:155])}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family={P[9]}&display=swap" rel="stylesheet">
{'<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css">' if cfg["lat"] is not None else ""}
<link rel="stylesheet" href="../../salon/salon.css">
<style>
  :root {{ --ink: {P[0]}; --ink-soft: {P[1]}; --accent: {P[2]}; --accent-deep: {P[3]}; --tint: {P[4]}; --bg: #ffffff; --surface: {P[5]}; --line: {P[6]};
    --display: "{P[7]}", Georgia, serif; --text: "{P[8]}", system-ui, sans-serif; --hero-radius: {P[10]}; }}
  h1, h2, h3 {{ font-weight: {700 if P[7] in ("Bricolage Grotesque", "Archivo", "Fredoka") else 400}; }}
</style>
<script id="site-config" type="application/json">{json.dumps(cfg)}</script>
</head>
<body>
<div class="preview-bar"><p><strong>Preview</strong> An example website made for {e(name)} by Pawenn. It is not live and not the business's official site.</p><a href="#make-it-yours">See the offer</a></div>
<header class="nav">
  <a class="brand" href="#top"><span class="brand-name">{e(sname)}</span></a>
  <nav class="nav-links" aria-label="Sections"><a href="#book">Book</a>{'<a href="#reviews">Reviews</a>' if cards else ''}<a href="#visit">{'Hours' if hours else 'Contact'}</a>{'<a href="#faq">Questions</a>' if faq else ''}</nav>
  <div class="nav-actions">{f'<a class="btn btn-solid" href="tel:{tel}"><span>{e(tel_label)}</span></a>' if tel else ''}</div>
</header>
<main id="top">
<section class="hero" aria-labelledby="hero-title">
  <div class="hero-copy">
    <p class="hero-kicker">{e(where)}</p>
    <h1 id="hero-title">{e(sname)}</h1>
    <p class="hero-sub">{e(desc)}</p>
    {status_block}
    <div class="hero-actions"><a class="btn btn-solid" href="#book">Book a {NOUN.get(cat, 'visit')}</a>{f'<a class="btn btn-line" href="tel:{tel}">Call {e(tel_label)}</a>' if tel else ''}</div>
    {rating_line}
  </div>
  <figure class="hero-photo"><img src="../../assets/{img}" alt="" width="1000" height="1250"><figcaption>Illustration</figcaption></figure>
</section>
<section class="prices" id="book" aria-labelledby="book-title">
  <div class="prices-inner">
    <div class="prices-head"><h2 id="book-title">Tell us what you need. We'll write the text.</h2><p>Pick the details and send them as a text message, then ask for a time and a price.</p></div>
    <div class="finder-grid">
      <form id="composer" onsubmit="return false">
        <fieldset class="step"{' hidden' if len(pets) == 1 else ''}><legend>Who's coming?</legend><div class="chips" data-pets></div></fieldset>
        <fieldset class="step"><legend>How big?</legend><div class="sizes" data-sizes></div></fieldset>
        <fieldset class="step"><legend>What do you need?</legend><div class="chips" data-services></div></fieldset>
        <fieldset class="step"><legend>Which day?</legend><div class="chips" data-days></div></fieldset>
        <fieldset class="step"><legend>What time?</legend><div class="chips"><label class="chip"><input type="radio" name="time" value="morning" checked><span>Morning</span></label><label class="chip"><input type="radio" name="time" value="afternoon"><span>Afternoon</span></label></div></fieldset>
        <div class="field"><label for="pet-name">Your pet's name (optional)</label><input id="pet-name" type="text" autocomplete="off" maxlength="30"></div>
        <label class="check"><input type="checkbox" id="shy"> My pet gets nervous</label>
      </form>
      <aside id="message" aria-live="polite">
        <div class="thread"><p class="thread-to">To {e(sname)}{', ' + e(tel_label) if tel else ''}</p><p class="bubble"></p></div>
        <div class="composer-actions"><a class="btn btn-solid" data-sms href="sms:{tel}">Send as a text</a><button class="btn btn-line" type="button" data-copy>Copy message</button></div>
        <p class="composer-note">Opens your messages app with the text ready. If this number doesn't take texts, call it instead.</p>
      </aside>
    </div>
  </div>
</section>
{f'<section class="voices" id="reviews" aria-labelledby="voices-title"><h2 id="voices-title">What clients say</h2><div class="voices-grid">{voices}</div><p class="voices-src">Themes from Google reviews. {e(rating)} from {int(count):,} reviews.</p></section>' if cards else ''}
<section class="find" id="visit" aria-labelledby="visit-title">
  <div class="find-info">
    <h2 id="visit-title">{'Hours' if hours else 'Get in touch'}</h2>
    {'' if mobile else f'<address>{e(r["address"])}</address>'}
    {hours_block}
    <div class="find-actions">{'' if mobile or cfg["lat"] is None else f'<a class="btn btn-solid" href="{e(directions)}" target="_blank" rel="noopener">Get directions</a>'}{f'<a class="btn btn-line" href="tel:{tel}">{e(tel_label)}</a>' if tel else ''}</div>
  </div>
  {find_right}
</section>
{f'<section class="faq" id="faq" aria-labelledby="faq-title"><h2 id="faq-title">Questions people ask</h2>{faq_html}</section>' if faq else ''}
<section class="offer" id="make-it-yours" aria-labelledby="offer-title">
  <div class="offer-head"><h2 id="offer-title">This is an example. Want a site like this?</h2><p>We made it from your Google listing, your website and your reviews. The finished site can look different: tell us what to add, remove or change (prices, photos, your logo, Spanish, online booking), and we'll do it before launch.</p></div>
  <div class="offer-grid">
    <div>{offer_left}</div>
    <div><h3>What you get</h3><ul><li>{live}</li><li>First year of hosting included</li><li>Your logo, photos, colors and wording, changed as you like</li></ul>
      <p class="offer-price">$200 <span>one-time, paid only once it's live and you're happy</span></p>
      <a class="btn btn-solid" href="mailto:pawenn.info@gmail.com?subject={quote(sname + ' website')}">Reply to Pawenn</a></div>
  </div>
  <p class="offer-fine">The photo is an illustration, not your business or a client's pet. Details come from your Google listing and website (November 2026); the rating and review themes come from Google reviews.</p>
</section>
</main>
<footer class="footer">
  <div class="footer-main">
    <div class="footer-brand"><a class="brand" href="#top"><span class="brand-name" style="font-size:1.7rem">{e(sname)}</span></a><p>{e(where)}.</p></div>
    <div class="footer-col"><h2>{'Area' if mobile else 'Visit'}</h2><p>{e(city_name) if mobile else e(r["address"])}</p></div>
    <div class="footer-col"><h2>Contact</h2><p>{f'<a href="tel:{tel}">{e(tel_label)}</a><br>' if tel else ''}{f'<a href="mailto:{e(email)}">{e(email)}</a>' if email else ''}</p></div>
    <nav class="footer-col" aria-label="Footer"><h2>On this page</h2><ul><li><a href="#book">Book</a></li>{'<li><a href="#reviews">Reviews</a></li>' if cards else ''}<li><a href="#visit">Hours</a></li></ul></nav>
  </div>
  <div class="footer-bottom"><p>© 2026 {e(name)}</p><p>Website by <a href="https://pawenn.com/en/" rel="noopener">Pawenn</a></p><a class="footer-top" href="#top">Back to top</a></div>
</footer>
<div class="thumb-bar" id="thumb-bar"><a class="btn btn-solid" href="#book">Book</a>{f'<a class="btn btn-line" href="tel:{tel}">Call</a>' if tel else ''}</div>
{'<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js" defer></script>' if cfg["lat"] is not None else ''}
<script src="../../salon/salon.js" defer></script>
</body>
</html>
"""
    os.makedirs(os.path.join(OUT, slug), exist_ok=True)
    open(os.path.join(OUT, slug, "index.html"), "w").write(page)
    return {"slug": slug, "name": name, "city": city, "cat": cat, "url": f"https://pawenn-previews.pages.dev/v2/p/{slug}/", "email": email, "domain": domain}


if __name__ == "__main__":
    args = sys.argv[1:]
    angle = "nosite"
    if args and args[0].startswith("--angle="):
        angle = args.pop(0).split("=", 1)[1]
    for s in args:
        print(json.dumps(make(s, angle)))
