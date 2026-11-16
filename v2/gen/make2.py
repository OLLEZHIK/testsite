#!/usr/bin/env python3
"""Multi-page preview sites in the Super Star style (owner approved 2026-11-16), from Pawenn data.

Usage: python3 v2/gen/make2.py <slug> [<slug> ...]
Writes v2/s/<slug>/: home, services/ (+ a page per service, for Google), visit/, book/.
Shared look and code: v2/multi/style.css and v2/multi/app.js. Colors follow the business's own
logo (PAL below, picked by eye from their logo), Baloo 2 + Nunito, plain backgrounds.
Only facts from Pawenn data (each backed by the business's site or Google listing): services come
from their own description, never from a generic list.
"""
import colorsys, csv, glob, html, json, os, re, shutil, sys
from urllib.parse import quote, urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make import load, hours_cfg, phone_parts, tz_for, short_name  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "v2", "s")
LOGOS = "/home/user/shop/website/public/logos"
BASE = "https://pawenn-previews.pages.dev/v2/s/"
e = html.escape

# main color, second color, dark sections: from each business's logo (None = no usable logo, calm default)
PAL = {
    "sugars-pet-sitting": ("#4f7f8a", "#e0a43a", "#1f3338", True),
    "keke-and-fetch-dog-walking-and-cat-boarding": ("#c46a1c", "#2a9d8f", "#17302e", False),
    "karas-k9-retreat": ("#e2621b", "#2aa6a0", "#241812", True),
    "diego-dogs-grooming": ("#1597c7", "#d5a032", "#0b2238", True),
    "snip-dogg-doggy-spa": ("#1f9e8f", "#f2c200", "#3a2410", True),
    "brooklyn-veterinary-group": ("#1f5a2a", "#8cc63f", "#11301a", True),
    "delta-force-k-9": ("#d61f1f", "#2a5bd7", "#0f1f45", True),
    "love-miami-dogs": ("#0f9a95", "#ff7f6e", "#173a46", False),
    "pet-lovers-animal-clinic-nw-7th-st": ("#5f9a25", "#9bd14b", "#1b2a12", True),
    "e-l-animal-clinic": ("#a0682a", "#d8a860", "#2e1a0e", True),
    "wags-animal-hospital": ("#7d9a0e", "#e6b98a", "#1f2a10", True),
    "bravo-animal-clinic": ("#2563c9", "#3fbf86", "#10233f", False),
    "maspeth-animal-hospital": ("#0f8a82", "#f3a73b", "#0f2b2c", False),
    "spawtlight-dog-salon-spa": ("#7b3fd6", "#ffc93c", "#1d1238", False),
}
HERO = {"vet": "vet-exam.jpg", "grooming": "salon-towel.jpg", "sitting": "maltese.jpg", "training": "maltese.jpg", "hotel": "cat.jpg"}
HERO_ALT = {"delta-force-k-9": "training-malinois.jpg", "love-miami-dogs": "dog-walk.jpg", "karas-k9-retreat": "daycare-play.jpg", "spawtlight-dog-salon-spa": "salon-doodle.jpg", "snip-dogg-doggy-spa": "salon-doodle.jpg", "sugars-pet-sitting": "pet-sitter-visit.jpg", "keke-and-fetch-dog-walking-and-cat-boarding": "cat-sitting.jpg"}

# id, label, phrase in a message, keywords in their own description, bookable from the message builder
KEYS = {
    "vet": [("wellness-exams", "Wellness exams", "a wellness exam", ("wellness", "check-up", "checkup", "examination"), True),
            ("vaccines", "Vaccines", "vaccines", ("vaccin",), True),
            ("dental-care", "Dental care", "a dental check", ("dental", "dentist"), True),
            ("surgery", "Surgery", "a surgery consult", ("surg",), True),
            ("urgent-care", "Urgent care", "an urgent visit", ("urgent",), True),
            ("boarding", "Boarding", "boarding", ("boarding",), True),
            ("x-rays", "Digital X-rays", "x-rays", ("radiograph", "radiology", "x-ray"), False),
            ("ultrasound", "Ultrasound", "an ultrasound", ("ultrasound",), False),
            ("echocardiograms", "Echocardiograms", "an echocardiogram", ("echocardiogram",), False),
            ("lab-testing", "In-house lab", "lab tests", ("laborator", "bloodwork", "lab test"), False),
            ("pharmacy", "Pharmacy", "a prescription refill", ("pharmac",), True),
            ("intensive-care", "Intensive care", "intensive care", ("intensive",), False)],
    "grooming": [("grooming", "Full grooming", "a full groom", ("groom",), True),
                 ("baths", "Baths", "a bath", ("bath",), True),
                 ("haircuts", "Haircuts and styling", "a haircut", ("haircut", "clipping", "styling", "trim"), True),
                 ("nail-care", "Nail care", "a nail trim", ("nail",), True),
                 ("teeth-brushing", "Teeth brushing", "teeth brushing", ("teeth",), True),
                 ("coloring", "Coloring", "coloring", ("coloring",), True),
                 ("daycare", "Daycare", "daycare", ("daycare", "day care"), True),
                 ("boarding", "Boarding", "boarding", ("boarding",), True)],
    "care": [("dog-walking", "Dog walking", "dog walks", ("walk",), True),
             ("pet-visits", "In-home visits", "in-home visits", ("drop-in", "pet visits", "home visits"), True),
             ("overnight-stays", "Overnight stays", "an overnight stay", ("overnight", "home stays"), True),
             ("boarding", "Boarding", "boarding", ("boarding",), True),
             ("daycare", "Daycare", "daycare", ("daycare",), True),
             ("medication", "Medication", "help with medication", ("medication",), True),
             ("travel-help", "Travel help", "help with travel", ("travel",), True)],
    "training": [("obedience", "Basic obedience", "obedience training", ("obedience",), True),
                 ("behavior", "Behavior modification", "help with behavior", ("behavio",), True),
                 ("protection", "Personal protection", "protection training", ("protection",), True)],
}
KIND = {"grooming": "Dog grooming", "vet": "Veterinary care", "sitting": "Pet sitting", "training": "Dog training", "hotel": "Pet sitting and boarding"}
ASK = {"vet": "Is there an appointment available?", "grooming": "Do you have a spot?", "sitting": "Are you available?", "hotel": "Are you available?", "training": "Could we set up a first session?"}
CONCEPT = {"karas-k9-retreat": {"kind": "Dog daycare, boarding and grooming", "book": "Book a stay", "bubbles": False, "first": ("daycare", "boarding"),
                                 "steps": [("Send your request", "Daycare, a stay or a groom: pick it below and send it as a text."), ("We confirm", "We reply to confirm the day or the dates."),
                                           ("Drop off, pick up", "Bring your dog to 235 W Sunset Rd for the day, the stay or the groom.")]}}
LEAD = {"pharmacy": "an on-site pharmacy", "lab-testing": "in-house lab testing", "x-rays": "digital X-rays", "medication": "medication for pets in their care",
        "travel-help": "travel assistance for dogs", "intensive-care": "intensive care monitoring", "grooming": "full grooming", "pet-visits": "in-home pet visits",
        "overnight-stays": "overnight stays", "obedience": "basic obedience training", "behavior": "behavior modification", "protection": "personal protection training"}
SIZES = [("small", "Small"), ("medium", "Medium"), ("large", "Large")]


# ---------- colors ----------
def rgb(h): return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))
def hexc(t): return "#%02x%02x%02x" % tuple(max(0, min(255, round(v))) for v in t)
def mix(a, b, t): return hexc(tuple(x + (y - x) * t for x, y in zip(rgb(a), rgb(b))))


def lum(h):
    def ch(c):
        c /= 255
        return c / 12.92 if c <= .03928 else ((c + .055) / 1.055) ** 2.4
    r, g, b = rgb(h)
    return .2126 * ch(r) + .7152 * ch(g) + .0722 * ch(b)


def contrast(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + .05) / (lb + .05)


def darken_to(h, bg, target):
    while contrast(h, bg) < target:
        h = mix(h, "#000000", .06)
    return h


def palette(main, second, night):
    pink = darken_to(main, "#ffffff", 3.6)          # buttons with white text
    red = darken_to(main, "#ffffff", 4.6)           # links and small colored text
    lime_deep = darken_to(second, "#ffffff", 4.6)
    n2 = mix(night, main, .45)
    return {"--pink": pink, "--red": red, "--gold": mix(main, "#ffffff", .25), "--gold-soft": mix(main, "#ffffff", .86),
            "--lime": second, "--lime-deep": lime_deep, "--paper": mix(main, "#ffffff", .94), "--line": mix(main, "#ffffff", .82),
            "--night": night, "--night-2": n2, "--shade": ", ".join(map(str, rgb(night))), "--kicker": mix(second, "#ffffff", .55),
            "--em": mix(main, "#ffffff", .7), "--pink-rgb": ", ".join(map(str, rgb(main))), "--lime-rgb": ", ".join(map(str, rgb(second))),
            "--ink": mix(night, "#000000", .15), "--ink-soft": mix(night, "#888888", .35)}


# ---------- helpers ----------
def place(addr):
    parts = [p.strip() for p in addr.split(",")]
    st = re.match(r"([A-Z]{2})\s*\d{5}", parts[-1]) if parts else None
    return (parts[-2] if len(parts) >= 2 else "", st.group(1) if st else "")


def sentence_with(desc, words):
    for s in re.split(r"(?<=\.)\s+", desc):
        if any(w in s.lower() for w in words):
            return s.strip()
    return ""


def page(slug, path, title, desc, body, active, ctx):
    depth = path.count("/")
    up = "../" * depth
    cur = ' aria-current="page"'
    nav = "".join(f'<a href="{up}{href}"{cur if href == active else ""}>{label}</a>' for href, label in ctx["nav"])
    c = ctx
    brand = (f'<img class="brand-logo{" named" if c["logo_named"] else ""}" src="{up}logo.{c["logo_ext"]}" alt="">' if c["logo_ext"] else f'<span class="brand-mono" aria-hidden="true">{e(c["sname"][0])}</span>')
    leaflet_css = '<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css">' if c["map"] and "visit/" in path else ""
    leaflet_js = '<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>' if c["map"] and "visit/" in path else ""
    call = f'<a class="btn btn-gold nav-call" href="tel:{c["tel"]}"><span class="nav-call-long">{e(c["tel_label"])}</span><span class="nav-call-short">Call</span></a>' if c["tel"] else ""
    contact = (f'<a href="tel:{c["tel"]}">{e(c["tel_label"])}</a><br>' if c["tel"] else "") + (f'<a href="mailto:{e(c["email"])}">{e(c["email"])}</a><br>' if c["email"] else "")
    social = " · ".join(f'<a href="{e(u)}" target="_blank" rel="noopener">{n}</a>' for n, u in (("Instagram", c["ig"]), ("Facebook", c["fb"])) if u)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{e(title)}</title>
<meta name="description" content="{e(desc[:158])}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;700;800&family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
{leaflet_css}
<link rel="stylesheet" href="{up}../../multi/style.css">
<style>:root {{ {c["css"]} }}</style>
<script type="application/ld+json">{json.dumps(c["schema"])}</script>
<script id="site-config" type="application/json">{json.dumps(c["cfg"])}</script>
</head>
<body>
<div class="preview-bar"><p><strong>Preview</strong> An example website made for {e(c["name"])} by Pawenn. It is not live and not the official site.</p><a href="{up}#make-it-yours">See the offer</a></div>
<header class="nav">
  <a class="brand" href="{up}" aria-label="{e(c["sname"])} home">{brand}<span class="brand-name">{e(c["sname"])}<small>{e(c["tagline_small"])}</small></span></a>
  <nav class="nav-links" aria-label="Pages">{nav}</nav>
  {call}
  <button class="menu-btn" type="button" aria-expanded="false" aria-controls="mobile-menu">Menu</button>
</header>
<nav class="mobile-menu" id="mobile-menu" hidden aria-label="Pages">{nav}{f'<a href="tel:{c["tel"]}">Call {e(c["tel_label"])}</a>' if c["tel"] else ''}</nav>
<main id="top">
{body}
</main>
<footer class="footer">
  <div class="footer-main">
    <div><p class="footer-brand">{e(c["sname"])}</p><p class="muted">{e(c["kind"])} in {e(c["loc"])}.</p></div>
    <div><h2>{'Visit us' if c["show_addr"] else 'Where we work'}</h2><p class="muted">{e(c["addr"]) if c["show_addr"] else e(c["loc"]) + ' and nearby'}</p><p class="muted">{e(c["hours_line"])}</p></div>
    <div><h2>Contact</h2><p>{contact}{social}</p></div>
    <nav aria-label="Footer"><h2>Pages</h2>{nav}</nav>
  </div>
  <div class="footer-bottom"><p>© 2026 {e(c["name"])}</p><p>Website by <a href="https://pawenn.com/en/" rel="noopener">Pawenn</a></p></div>
</footer>
<div class="thumb-bar"><a class="btn btn-gold" href="{up}book/">{e(c["book_label"])}</a>{f'<a class="btn btn-ghost" href="tel:{c["tel"]}">Call</a>' if c["tel"] else f'<a class="btn btn-ghost" href="{up}visit/">Contact</a>'}</div>
{leaflet_js}
<script src="{up}../../multi/app.js" defer></script>
</body>
</html>
"""


def composer(c, pre=""):
    pets = c["cfg"]["composer"]["pets"]
    pet_chips = "".join(f'<label class="chip"><input type="radio" name="pet" value="{k}"{" checked" if i == 0 else ""}><span>{v["label"]}</span></label>' for i, (k, v) in enumerate(pets.items()))
    sizes = "".join(f'<label class="chip"><input type="radio" name="size" value="{v}"{" checked" if i == 0 else ""}><span>{l}</span></label>' for i, (v, l) in enumerate(SIZES))
    any_sizes = any(v["sizes"] for v in pets.values())
    times = "".join(f'<option value="{t}">{t.capitalize()}</option>' for t in c["times"])
    area = '<label class="field"><span>Your neighborhood (optional)</span><input name="area" type="text" maxlength="40" autocomplete="off"></label>' if not c["show_addr"] else ""
    mail = f'<a class="btn btn-ghost" data-mail href="mailto:{e(c["email"])}">Email it</a>' if c["email"] else ""
    sms = f'<a class="btn btn-gold" data-sms href="sms:{c["tel"]}">Send as a text</a>' if c["tel"] else ""
    return f"""<div class="composer" data-composer data-preselect="{pre}">
  <form class="composer-form" onsubmit="return false">
    <fieldset{' hidden' if len(pets) == 1 else ''}><legend>Who's it for?</legend><div class="chips">{pet_chips}</div></fieldset>
    {f'<fieldset data-sizes><legend>How big?</legend><div class="chips">{sizes}</div></fieldset>' if any_sizes else ''}
    <fieldset><legend>What do you need?</legend><div class="chips" data-services></div></fieldset>
    <div class="row2">
      <label class="field"><span>Which day?</span><select name="day"></select></label>
      <label class="field"><span>Time</span><select name="time">{times}</select></label>
    </div>
    <div class="row2">
      <label class="field"><span>Pet's name (optional)</span><input name="petname" type="text" maxlength="30" autocomplete="off"></label>
      {area or '<label class="chip" style="align-self:end"><input type="checkbox" name="shy"><span>My pet gets nervous</span></label>'}
    </div>
    {'<label class="chip"><input type="checkbox" name="shy"><span>My pet gets nervous</span></label>' if area else ''}
  </form>
  <aside class="composer-out">
    <p class="ticket-label">Your message</p>
    <p class="bubble" data-bubble></p>
    <div class="actions">{sms}{mail}<button class="btn btn-ghost" type="button" data-copy>Copy</button></div>
    <p class="fine">Opens your messages or email app with everything filled in.{f' If this number does not take texts, call {e(c["tel_label"])}.' if c["tel"] else ''}</p>
  </aside>
</div>"""


def offer(c):
    items = [f"A page for each service, ready for Google searches like “{e(c['svcs'][0]['label'].lower())} in {e(c['loc'])}”" if c["svcs"] else "Pages ready for Google search",
             "Built for phones first, with https",
             "Open-now status from your own hours" + (", a map and one-tap directions" if c["map"] else ""),
             "A booking message builder on every page, by text or email"]
    if c["cards"]:
        items.append("What your Google reviews say, on the home page")
    lis = "".join(f"<li>{x}</li>" for x in items)
    return f"""<section class="offer" id="make-it-yours" aria-labelledby="offer-title">
  <h2 id="offer-title">This is an example. Want it as your website?</h2>
  <p>We made it from {e(c["domain"]) if c["domain"] else 'your public details'} and your Google listing. The finished site can look different: tell us what to add, remove or change (photos, prices, your team, Spanish, online booking), and we'll do it before launch.</p>
  <div class="offer-grid">
    <ul>{lis}</ul>
    <div><p class="offer-price">$200 <span>one-time, first year of hosting included, paid only once it's live{(' on ' + e(c["domain"])) if c["domain"] else ''} and you're happy</span></p>
    <a class="btn btn-gold" href="mailto:pawenn.info@gmail.com?subject={quote(c['sname'] + ' website')}">Reply to Pawenn</a></div>
  </div>
  <p class="fine">Photos are illustrations, not your business or your clients' pets{'; the logo is from your current site' if c["logo_ext"] else ''}. Services and details come from your website and Google listing (November 2026); the rating{' and review themes come' if c["cards"] else ' comes'} from Google reviews.</p>
</section>"""


def status_html():
    return '<div class="status" data-status><span class="dot"></span><span class="status-text"></span></div>'


def make(slug):
    r, city, cat, ins, cj = load(slug)
    name = r["name"].strip().rstrip(".")
    sname = short_name(name)
    main, second, night, use_logo = PAL[slug]
    tel, tel_label = phone_parts(r["phone"])
    hours = hours_cfg(r["opening_hours"])
    raw_hours = (r["opening_hours"] or "").strip()
    tz = tz_for(city, cj)
    locality, state = place(r["address"])
    loc = f"{locality}, {state}" if state else locality
    desc = (r["description"] or "").strip()
    d_low = (desc + " " + (r["short_description"] or "")).lower()
    group = "care" if cat in ("sitting", "hotel") else cat if cat in KEYS else "grooming"
    svcs = [{"id": a, "label": b, "phrase": p, "keys": ks, "book": bk} for a, b, p, ks, bk in KEYS[group] if any(k in d_low for k in ks)]
    if not svcs:
        a, b, p, ks, bk = KEYS[group][0]
        svcs = [{"id": a, "label": b, "phrase": p, "keys": ks, "book": bk}]
    first = CONCEPT.get(slug, {}).get("first", ())
    svcs.sort(key=lambda x: (x["id"] not in first, first.index(x["id"]) if x["id"] in first else 0))
    book_svcs = [s for s in svcs if s["book"]][:6]
    if cat == "vet":
        book_svcs = book_svcs + [{"id": "sick-visit", "label": "Sick pet", "phrase": "a visit for my sick pet", "keys": (), "book": True}]
    cats = bool(re.search(r"\bcats?\b", d_low)) or cat == "vet"
    show_addr = cat not in ("sitting", "hotel")
    lat = float(r["lat"]) if (show_addr and r["lat"]) else None
    lng = float(r["lng"]) if (show_addr and r["lng"]) else None
    sizes = cat in ("grooming",) or any(s["id"] in ("boarding", "daycare") for s in book_svcs) and cat != "vet"
    pets = {"dog": {"label": "Dog", "noun": "dog", "sizes": sizes, "services": [[s["id"], s["label"], s["phrase"]] for s in book_svcs]}}
    if cats:
        pets["cat"] = {"label": "Cat", "noun": "cat", "sizes": False,
                       "services": [[s["id"], s["label"], s["phrase"]] for s in book_svcs if s["id"] not in ("dog-walking", "obedience", "protection", "haircuts")]}
    late = hours and any(v != "closed" and int(v.split("-")[1][:2]) >= 19 for v in hours.values())
    times = ["morning", "afternoon"] + (["evening"] if late else [])
    email = r["email"]
    site = r["website"]
    domain = urlparse(site if "//" in site else "http://" + site).netloc.replace("www.", "") if site else ""
    cards = [x for x in (ins or {}).get("cards", []) if x.get("sentiment") == "positive"][:3]
    faq = [q for q in (ins or {}).get("faq", []) if q.get("basis") in ("site", "both")][:4]
    rating, count = r["google_rating"], r["google_rating_count"]
    kind = CONCEPT.get(slug, {}).get("kind") or KIND.get(cat, "Pet care")
    if raw_hours == "24h":
        hours_line = "Open 24 hours."
    elif not hours:
        hours_line = "By appointment."
    else:
        closed = [n for d, n in (("1", "Mondays"), ("2", "Tuesdays"), ("3", "Wednesdays"), ("4", "Thursdays"), ("5", "Fridays"), ("6", "Saturdays"), ("0", "Sundays")) if hours.get(d, "closed") == "closed"]
        hours_line = "Open every day." if not closed else "Closed " + " and ".join(closed) + "."
    # logo
    logo_ext = ""
    if use_logo and r["logo_file"]:
        src = glob.glob(f"{LOGOS}/{city}/{r['logo_file']}")
        if src:
            logo_ext = src[0].rsplit(".", 1)[1]
            os.makedirs(os.path.join(OUT, slug), exist_ok=True)
            shutil.copy(src[0], os.path.join(OUT, slug, f"logo.{logo_ext}"))
    pal = palette(main, second, night)
    css = " ".join(f"{k}: {v};" for k, v in pal.items())
    cfg = {"tz": tz, "hours": hours or {}, "phone": tel or "", "phoneLabel": tel_label, "email": email, "lat": lat, "lng": lng, "pin": sname,
           "composer": {"greeting": f"Hi {sname}!", "ask": ASK.get(cat, "Are you available?"), "subject": f"Request for {sname}", "pets": pets}}
    stype = "VeterinaryCare" if cat == "vet" else "LocalBusiness"
    schema = {"@context": "https://schema.org", "@type": stype, "name": name, "telephone": tel or None, "email": email or None,
              "address": {"@type": "PostalAddress", "streetAddress": r["address"].split(",")[0], "addressLocality": locality, "addressRegion": state} if show_addr else None,
              "areaServed": None if show_addr else loc,
              "aggregateRating": {"@type": "AggregateRating", "ratingValue": rating, "reviewCount": count} if rating else None,
              "sameAs": [u for u in (r["instagram"], r["facebook"]) if u] or None}
    schema = {k: v for k, v in schema.items() if v}
    nav = [("", "Home"), ("services/", "Services"), ("visit/", "Hours & location" if show_addr else "Hours & contact"), ("book/", "Book")]
    book_label = {"vet": "Book a visit", "grooming": "Book a groom", "training": "Book a session"}.get(cat, "Book care")
    book_label = CONCEPT.get(slug, {}).get("book", book_label)
    tagline = {"vet": f"Vet care for dogs and cats in {locality}", "grooming": f"Dog grooming in {locality}", "training": f"Dog training in {locality}",
               "sitting": f"Pet sitting in {locality}", "hotel": f"Pet sitting and boarding in {locality}"}.get(cat, f"Pet care in {locality}")
    if slug == "karas-k9-retreat":
        tagline = f"Daycare, boarding and grooming in {locality}"
    if slug == "snip-dogg-doggy-spa":
        tagline = f"Dog grooming and daycare in {locality}"
    tagline_small = {"vet": "Animal clinic", "grooming": "Grooming", "training": "Dog training", "sitting": "Pet sitting", "hotel": "Pet care"}.get(cat, "")
    if sname.lower().endswith(("clinic", "hospital", "group", "spa", "retreat", "grooming", "sitting")):
        tagline_small = locality
    c = dict(name=name, sname=sname, tel=tel, tel_label=tel_label, email=email, ig=r["instagram"], fb=r["facebook"], kind=kind, loc=loc,
             addr=r["address"], show_addr=show_addr, map=lat is not None, hours_line=hours_line, nav=nav, logo_ext=logo_ext, css=css, schema=schema,
             cfg=cfg, times=times, logo_named=bool(logo_ext) and slug != "karas-k9-retreat", svcs=svcs, cards=cards, domain=domain, book_label=book_label, tagline_small=tagline_small)
    directions = f'https://www.google.com/maps/dir/?api=1&destination={quote(name + ", " + r["address"])}' + (f'&destination_place_id={r["google_place_id"]}' if r.get("google_place_id") else "")
    rating_line = f'<p class="rating"><span class="stars" aria-hidden="true">★★★★★</span> {e(rating)} on Google from {int(count):,} reviews</p>' if rating else ""
    lead = (r["short_description"] or desc).strip()
    img = HERO_ALT.get(slug) or HERO.get(cat, "paw.jpg")
    from PIL import Image
    iw, ih = Image.open(os.path.join(ROOT, "v2", "assets", img)).size
    hours_block = '<table class="hours" data-hours></table>' if hours else f'<p class="big-status">{e(hours_line)}</p><p class="muted">Send a text or call to book a time.</p>'
    status = status_html() if hours else ""
    street = r["address"].split(",")[0]

    # steps by category (process only, no claims)
    if cat == "vet":
        steps = [("Tell us why you're coming", "A checkup, vaccines or a sick pet: pick it below and send it as a text."), ("We confirm a time", "We reply with an appointment that works for you."),
                 ("Come in", f"We're at {street}, {locality}. Bring your pet's past records if you have them.")]
    elif cat == "grooming":
        steps = [("Send your request", "Pick the service and a day below. It goes to us as a text."), ("We confirm a time", "We reply with a time and a price for your dog."),
                 ("Drop off, pick up", f"Bring your dog to {street}, then pick them up clean and fresh.")]
    elif cat == "training":
        steps = [("Tell us about your dog", "What you'd like to work on, sent as a text."), ("We set up a first session", "We reply with a time."),
                 ("A program for your dog", "Training built around your dog's individual needs.")]
    else:
        joined = ", ".join(s["label"].lower() for s in svcs[:3])
        steps = [("Tell us about your pets", "Who they are and the dates you need, sent as a text."), ("We confirm", "We reply to set up the care you need."),
                 ("Your pets are looked after", f"{joined[0].upper() + joined[1:]}, as you booked." if joined else "As you booked.")]
    steps = CONCEPT.get(slug, {}).get("steps", steps)
    steps_html = "".join(f"<li><strong>{e(a)}</strong><span>{e(b)}</span></li>" for a, b in steps)
    def card_text(sv):
        said = sentence_with(desc, sv["keys"])
        if said and sum(1 for o in svcs if any(k in said.lower() for k in o["keys"])) == 1:
            return said
        pets_txt = " for dogs and cats" if cats and sv["id"] not in ("dog-walking", "obedience", "protection", "behavior") else (" for dogs" if cat != "vet" else "")
        return f"{sv['label']}{pets_txt}{' at ' + street if show_addr else ' in ' + locality}."
    svc_cards = "".join(f'<article class="card{" star" if i == 0 else ""}"><h3>{e(s["label"])}</h3><p>{e(card_text(s))}</p><a class="more" href="services/{s["id"]}/">More about {e(s["label"].lower())}</a></article>' for i, s in enumerate(svcs[:6]))
    voices = "".join(f'<blockquote><strong>{e(x["title"]["en"])}</strong><p>{e(x["text"]["en"])}</p></blockquote>' for x in cards)
    reviews_html = (f'<section class="wrap section"><div class="section-head"><h2>What clients say</h2><p class="rating-big"><span>{e(rating)}</span> on Google from {int(count):,} reviews</p></div><div class="voices-grid">{voices}</div><p class="fine">Themes from Google reviews, {e(ins.get("period_from", "")[:7])} to {e(ins.get("period_to", "")[:7])}. Not quotes.</p></section>'
                    if cards else (f'<section class="wrap section quote"><p class="rating-big"><span>{e(rating)}</span> on Google from {int(count):,} reviews</p></section>' if rating else ""))
    gen_faq = []
    if hours:
        gen_faq.append(("When are you open?", "Today's hours are at the top of the page; the full week is on the Hours page."))
    if show_addr:
        gen_faq.append(("Where are you?", f"{r['address']}. Directions are on the Hours & location page."))
    if cats and cat != "vet":
        gen_faq.append(("Do you take cats?", "Yes, cats too."))
    faq_items = [(q["q"]["en"], q["a"]["en"]) for q in faq] + gen_faq
    faq_html = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in faq_items[:6])
    emerg = ""
    if cat == "vet":
        note = (r.get("emergency_note") or "").strip()
        emerg = f'<div class="note-box"><strong>Emergency?</strong> {e(note) if note else "Call us right away during opening hours. When we are closed, go to the nearest 24-hour animal emergency hospital."}</div>'

    home = f"""
<section class="hero{" plain" if cat != "grooming" or not CONCEPT.get(slug, {}).get("bubbles", True) else ""}">
  <img class="hero-img" src="../../assets/{img}" alt="" width="{iw}" height="{ih}"><span class="illus">Illustration</span>
  <div class="hero-shade"></div>
  <div class="hero-copy">
    <p class="kicker">{e(kind)} · {e(loc)}</p>
    <h1>{e(sname)} <em>{e(tagline)}</em></h1>
    <p class="lead">{e(lead)}</p>
    {status}
    <div class="hero-actions"><a class="btn btn-gold" href="book/">{e(book_label)}</a>{f'<a class="btn btn-ghost" href="tel:{tel}">Call {e(tel_label)}</a>' if tel else ''}</div>
    {rating_line}
  </div>
</section>

<section class="band">
  <div class="wrap two">
    <div><h2>{'Find us' if show_addr else 'Where we work'}</h2><p class="muted">{e(r["address"]) if show_addr else e(loc) + ' and nearby. Tell us your neighborhood when you book.'}</p>
      <div class="hero-actions">{f'<a class="btn btn-gold" href="{e(directions)}" target="_blank" rel="noopener">Get directions</a>' if show_addr else ''}<a class="btn btn-ghost-dark" href="visit/">{'Hours & map' if show_addr else 'Hours & contact'}</a></div></div>
    <div><h2>What we do</h2><div class="svc-chips">{''.join(f'<span>{e(s["label"])}</span>' for s in svcs)}</div></div>
  </div>
</section>

<section class="wrap section">
  <h2>How it works</h2>
  <ol class="steps three">{steps_html}</ol>
</section>

<section class="wrap section">
  <div class="section-head"><h2>Services</h2><a class="link" href="services/">See every service</a></div>
  <div class="cards auto">{svc_cards}</div>
</section>

<section class="book-band" id="book">
  <div class="wrap">
    <h2>Build your message</h2>
    <p class="muted">Pick the details. We'll write the text for you to send.</p>
    {composer(c)}
  </div>
</section>
{reviews_html}
{f'<section class="wrap section faq"><h2>Questions people ask</h2>{faq_html}</section>' if faq_html else ''}
{offer(c)}
"""
    pages = {"index.html": page(slug, "index.html", f"{name} | {tagline}", desc, home, "", c)}

    # services index
    rows = "".join(f'<article class="card"><h3>{e(s["label"])}</h3><p>{e(card_text(s))}</p><a class="more" href="{s["id"]}/">More about {e(s["label"].lower())}</a></article>' for s in svcs)
    sv = f"""
<section class="page-head"><div class="wrap"><p class="kicker">Services</p><h1>{e(kind)} in {e(locality)}</h1><p class="lead">{e(desc)}</p></div></section>
<section class="wrap section"><div class="cards auto">{rows}</div>{emerg}</section>
<section class="book-band"><div class="wrap"><h2>Ready to book?</h2>{composer(c)}</div></section>
{offer(c)}"""
    pages["services/index.html"] = page(slug, "services/index.html", f"Services | {sname}, {loc}", desc, sv, "services/", c)

    # a page per service
    for s in svcs:
        others = "".join(f'<a href="../{o["id"]}/">{e(o["label"])}</a>' for o in svcs if o["id"] != s["id"])
        said = sentence_with(desc, s["keys"])
        where = f"at {street}, {locality}" if show_addr else f"in {loc}"
        sp = f"""
<section class="page-head"><div class="wrap"><p class="kicker">{e(sname)} · {e(loc)}</p><h1>{e(s["label"])} in {e(locality)}</h1><p class="lead">{e(sname)} offers {e(LEAD.get(s["id"], s["label"].lower()))}{' for dogs and cats' if cats and s["id"] not in ('dog-walking', 'obedience', 'protection', 'behavior', 'medication', 'travel-help') else ''} {e(where)}.</p>
<div class="hero-actions"><a class="btn btn-gold" href="#book">Ask about {e(s["label"].lower())}</a>{f'<a class="btn btn-ghost-dark" href="tel:{tel}">Call {e(tel_label)}</a>' if tel else ''}</div></div></section>
<section class="wrap section two">
  <div><h2>About this service</h2>{f'<p class="muted">{e(said)}</p>' if said else ''}<p class="muted" style="margin-top:.8rem">Ask us for the price and the next free time: send the message below or call.</p>{emerg if s["id"] in ("urgent-care",) else ''}</div>
  <div><h2>{'Hours' if hours else 'When'}</h2>{status}{hours_block}{f'<h2 class="mt">Other services</h2><div class="area-cloud">{others}</div>' if others else ''}</div>
</section>
<section class="book-band" id="book"><div class="wrap"><h2>Ask about {e(s["label"].lower())}</h2>{composer(c, s["id"] if s["book"] else "")}</div></section>
{offer(c)}"""
        pages[f"services/{s['id']}/index.html"] = page(slug, f"services/{s['id']}/index.html", f"{s['label']} in {loc} | {sname}",
                                                         f"{s['label']} at {sname}, {loc}. {said}", sp, "services/", c)

    # visit
    map_html = (f'<div class="map-box"><div class="map" id="map" role="region" aria-label="Map: {e(r["address"])}"></div></div><div class="hero-actions"><a class="btn btn-gold" href="{e(directions)}" target="_blank" rel="noopener">Get directions</a></div>'
                if lat is not None else f'<div class="note-box"><strong>We come from {e(locality)}.</strong> Tell us your neighborhood in your message and we\'ll let you know if we cover it.</div>')
    vi = f"""
<section class="page-head"><div class="wrap"><p class="kicker">{'Hours & location' if show_addr else 'Hours & contact'}</p><h1>{'Visit ' + e(sname) if show_addr else 'Get in touch'}</h1><p class="lead">{e(r["address"]) if show_addr else e(loc)}</p>{status}</div></section>
<section class="wrap section two">
  <div><h2>Hours</h2>{hours_block}{emerg}</div>
  <div><h2>Contact</h2><p>{f'<a href="tel:{tel}">{e(tel_label)}</a><br>' if tel else ''}{f'<a href="mailto:{e(email)}">{e(email)}</a>' if email else ''}</p>{map_html}</div>
</section>
{offer(c)}"""
    pages["visit/index.html"] = page(slug, "visit/index.html", f"Hours and {'location' if show_addr else 'contact'} | {sname}, {loc}",
                                     f"Hours, {'address, map and directions' if show_addr else 'phone and email'} for {name} in {loc}.", vi, "visit/", c)

    # book
    bk = f"""
<section class="page-head"><div class="wrap"><p class="kicker">Book</p><h1>{e(book_label)}</h1><p class="lead">Build your message below{f', or call {e(tel_label)}' if tel else ''}. We'll confirm a time.</p>{status}</div></section>
<section class="book-band"><div class="wrap">{composer(c)}</div></section>
<section class="wrap section two">
  <div><h2>Hours</h2>{hours_block}</div>
  <div><h2>Contact</h2><p>{f'<a href="tel:{tel}">{e(tel_label)}</a><br>' if tel else ''}{f'<a href="mailto:{e(email)}">{e(email)}</a>' if email else ''}</p>{f'<p class="muted" style="margin-top:.8rem">{e(r["address"])}</p>' if show_addr else ''}</div>
</section>
{offer(c)}"""
    pages["book/index.html"] = page(slug, "book/index.html", f"{book_label} | {sname}, {loc}", f"Book with {name} in {loc}.", bk, "book/", c)

    for p, content in pages.items():
        full = os.path.join(OUT, slug, p)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        open(full, "w").write(content)
    return {"slug": slug, "pages": len(pages), "url": BASE + slug + "/", "services": [s["id"] for s in svcs], "logo": bool(logo_ext)}


if __name__ == "__main__":
    for s in sys.argv[1:]:
        print(json.dumps(make(s)))
