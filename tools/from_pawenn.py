#!/usr/bin/env python3
"""Draft a site from a Pawenn listing: sites/<slug>/site.json + logo.png.

    python3 tools/from_pawenn.py ../pawenn miami yofren-master-mobile-pet-grooming

Reads data/cities/<city>/businesses*.csv, review-insights/<slug>.json and the
logo from the Pawenn repository. Writes a DRAFT: every fact (hours, phone,
rating, review highlights) comes from Pawenn's data; the services list is
picked from the words in the place's own description, and the headline is
the category's default. Read it before sending - change anything in
site.json, then `node build.mjs <slug>`.

Needs Pillow for the logo (pip install pillow); without it the logo is
copied as is and the default colours of the category are used.
"""
import csv
import glob
import json
import os
import re
import sys

try:
    from PIL import Image
except ImportError:  # the draft still works, with default colours
    Image = None

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Per category: headline, steps, default colours, and the services the
# description has to mention to be listed (word -> service).
CATEGORY = {
    "GROOMING": {
        "key": "grooming",
        "label": "Pet grooming",
        "title": "Fresh, happy pets. Every visit.",
        "title_mobile": "Grooming that comes to your door.",
        "accent": "#E8577E",
        "services": [
            (r"bath|wash|shampoo", "bath", "Bath & brush", "A full bath, blow-dry and brush-out with gentle shampoo."),
            (r"haircut|\bcuts?\b|styl|\btrim|groom", "scissors", "Haircuts & styling", "Neat cuts for every breed, from a quick tidy-up to a full style."),
            (r"\bnails?\b", "paw", "Nail trims", "Quick, careful nail trims."),
            (r"\bears?\b", "ear", "Ear cleaning", "Gentle ear cleaning as part of the groom."),
            (r"teeth|tooth|dental", "tooth", "Teeth cleaning", "Brushing for fresher breath."),
            (r"de-?shed|deshed|undercoat", "sparkles", "De-shedding", "Less loose fur at home after every visit."),
            (r"\bcats?\b|feline", "heart", "Cat grooming", "Calm, careful grooming for cats."),
        ],
        "steps": [
            ("Call or text", "Tell us about your pet and pick a time that suits you."),
            ("We get to work", "A careful groom, done the way you asked."),
            ("Fresh and happy", "Your pet goes home clean, comfortable and looking great."),
        ],
        "steps_mobile": [
            ("Call or text", "Tell us about your pet and pick a time that suits you."),
            ("We come to you", "Your groomer arrives at your home, ready to work."),
            ("Fresh and happy", "Your pet stays relaxed at home and comes back looking great."),
        ],
    },
    "VET_CLINIC": {
        "key": "vet",
        "label": "Veterinary clinic",
        "title": "Caring vets for your best friend.",
        "accent": "#2F80ED",
        "services": [
            (r"wellness|exam|check", "stethoscope", "Wellness exams", "Regular check-ups to keep your pet healthy."),
            (r"vaccin", "check", "Vaccinations", "Core and lifestyle vaccines for dogs and cats."),
            (r"surg|spay|neuter", "heart", "Surgery", "Spay, neuter and other procedures."),
            (r"dental|teeth", "tooth", "Dental care", "Cleanings and dental checks."),
            (r"emergenc|urgent", "clock", "Urgent care", "Help when your pet needs it fast."),
            (r"x-?ray|radiolog|ultrasound|diagnos|lab", "sparkles", "Diagnostics", "In-house tests and imaging."),
        ],
        "steps": [
            ("Call us", "Tell us what is going on and book a visit."),
            ("Visit", "A thorough exam and a clear plan."),
            ("Follow-up", "We stay with you until your pet is well."),
        ],
    },
    "DOG_TRAINING": {
        "key": "training",
        "label": "Dog training",
        "title": "Better manners. Happier dogs.",
        "accent": "#F2994A",
        "services": [
            (r"pupp", "paw", "Puppy training", "A great start for young dogs."),
            (r"obedien|basic|manner", "check", "Obedience training", "Sit, stay, come and loose-leash walking."),
            (r"behavio|reactiv|aggress|anxi", "heart", "Behavior help", "For reactive, anxious or difficult dogs."),
            (r"private|in-?home|one-on-one", "home", "Private lessons", "Training at your pace, where you need it."),
            (r"board|stay", "calendar", "Board & train", "Your dog stays and trains with us."),
        ],
        "steps": [
            ("Call or text", "Tell us about your dog and your goals."),
            ("Train together", "Clear, kind lessons that fit your dog."),
            ("Enjoy the results", "A calmer dog and an easier everyday life."),
        ],
    },
    "PET_SITTING": {
        "key": "sitting",
        "label": "Pet sitting",
        "title": "Loving care while you're away.",
        "accent": "#9B51E0",
        "services": [
            (r"walk", "paw", "Dog walking", "Regular walks that fit your schedule."),
            (r"\bsitt|\bvisits?\b|drop-?in", "home", "Pet sitting", "Visits at your home while you are out."),
            (r"board|overnight|stay", "calendar", "Boarding & overnights", "Your pet stays in good hands."),
            (r"\bcats?\b|feline", "heart", "Cat care", "Feeding, play and litter care for cats."),
        ],
        "steps": [
            ("Call or text", "Tell us about your pet and the dates you need."),
            ("Meet & greet", "We get to know your pet and routine."),
            ("Relax", "Your pet is cared for while you are away."),
        ],
    },
    "PET_HOTEL": {
        "key": "hotel",
        "label": "Pet boarding",
        "title": "A home away from home for your pet.",
        "accent": "#27AE60",
        "services": [
            (r"board|overnight|stay|hotel", "home", "Boarding", "Comfortable overnight stays."),
            (r"day ?care|daycare", "sparkles", "Daycare", "Play and company while you work."),
            (r"groom|bath", "bath", "Grooming", "A fresh bath before going home."),
            (r"train", "check", "Training", "Good manners during the stay."),
        ],
        "steps": [
            ("Call or text", "Tell us your dates and about your pet."),
            ("Drop off", "We settle your pet in and learn their routine."),
            ("Pick up", "A happy, tired pet ready to go home."),
        ],
    },
    "PET_SHOP": {
        "key": "shop",
        "label": "Pet store",
        "title": "Everything your pet needs.",
        "accent": "#EB5757",
        "services": [
            (r"food|diet|nutrition", "heart", "Food & treats", "Quality food and treats for every pet."),
            (r"toy|accessor|supply|supplies", "sparkles", "Toys & supplies", "Everyday essentials and fun extras."),
            (r"aquar|fish", "bath", "Aquarium", "Fish and aquarium supplies."),
            (r"groom", "scissors", "Grooming", "Grooming services in store."),
        ],
        "steps": [],
    },
}
GENERIC = {"bath", "scissors"}
NEGATIVE = re.compile(r"\b(while|although|though|aside from|except|however|on the other hand|but|complain\w*|critic\w*|grievance\w*|dissatisf\w*|disput\w*|negative\w*|isolated|injur\w*|unhappy|frustrat\w*|rude\w*|a few|a small number|a couple|one (?:client|owner|reviewer))\b", re.I)
DAYS = ["mo", "tu", "we", "th", "fr", "sa", "su"]
US_TZ = {"new-york": "America/New_York", "miami": "America/New_York", "philadelphia": "America/New_York",
         "chicago": "America/Chicago", "houston": "America/Chicago", "dallas": "America/Chicago",
         "san-antonio": "America/Chicago", "phoenix": "America/Phoenix", "los-angeles": "America/Los_Angeles",
         "san-diego": "America/Los_Angeles"}


# Without brand colours from a logo: one of these, picked by the slug, so
# neighbouring previews do not all look the same.
PALETTES = [("#E8577E", "#C23B62"), ("#7C5CE0", "#5B3FC4"), ("#0F9D8A", "#0B7A6B"), ("#F2994A", "#C46F1F"), ("#2F80ED", "#1C5FBF"), ("#27AE60", "#1E8449")]


def palette(slug, cat):
    accent, deep = PALETTES[sum(map(ord, slug)) % len(PALETTES)]
    return {"accent": accent, "accentDeep": deep}


def read_place(repo, city, slug):
    for f in sorted(glob.glob(os.path.join(repo, "data", "cities", city, "businesses*.csv"))):
        with open(f, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if r["slug"] == slug:
                    return r
    sys.exit(f"{slug} not found in data/cities/{city}")


def hours(value):
    out = {}
    for part in (value or "").split(";"):
        part = part.strip()
        if not part:
            continue
        day, _, spans = part.partition(" ")
        if day in DAYS:
            out[day] = spans.strip()
    return out if len(out) == 7 else None


def clean_title(title):
    """'Welcoming staff alongside customer service disputes' -> 'Welcoming staff'."""
    return re.split(r"\s+(?:with|alongside|despite|but|amid|mixed with)\s+(?=.*(?:complain|disput|concern|issue|critic|isolated|mixed))", title, maxsplit=1, flags=re.I)[0].strip()


def clean(text):
    """Keep the praise, drop the 'while one reviewer complained' sentences."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return " ".join(s for s in sentences if not NEGATIVE.search(s)).strip()


def logo_and_colours(src, dst):
    if not src or not os.path.exists(src):
        return None
    if Image is None:
        import shutil
        shutil.copy(src, dst)
        return None
    im = Image.open(src).convert("RGBA")
    box = im.getbbox()
    if box:
        pad = 6
        im = im.crop((max(box[0] - pad, 0), max(box[1] - pad, 0), min(box[2] + pad, im.width), min(box[3] + pad, im.height)))
    im.save(dst, optimize=True)
    # brand colours: the most common saturated colour and the darkest common one
    counts = {}
    for r, g, b, a in im.convert("RGBA").get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata():
        if a < 200 or (r > 235 and g > 235 and b > 235):
            continue
        key = (r // 8 * 8, g // 8 * 8, b // 8 * 8)
        counts[key] = counts.get(key, 0) + 1
    if not counts:
        return None
    ranked = sorted(counts, key=counts.get, reverse=True)[:12]
    sat = lambda c: max(c) - min(c)
    bright = [c for c in ranked if sat(c) > 60 and sum(c) > 180]
    dark = [c for c in ranked if sum(c) < 200]
    hexc = lambda c: "#%02X%02X%02X" % c
    out = {}
    if bright:
        out["accent"] = hexc(bright[0])
        out["accentDeep"] = hexc(tuple(int(v * 0.78) for v in bright[0]))
    if dark:
        out["ink"] = hexc(dark[0])
    return out


def main():
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    repo, city, slug = sys.argv[1:]
    r = read_place(repo, city, slug)
    # who signs the offer: outreach/sender.json (name, email, postal address)
    sender_path = os.path.join(ROOT, "outreach", "sender.json")
    sender = json.load(open(sender_path, encoding="utf-8")) if os.path.exists(sender_path) else {}
    cat = CATEGORY.get(r["category"], CATEGORY["GROOMING"])
    mobile = bool(re.search(r"\bmobile\b", r["name"] + " " + r.get("description", ""), re.I))
    with open(os.path.join(repo, "data", "cities", city, "city.json"), encoding="utf-8") as fh:
        city_name = json.load(fh).get("name", city.title())

    out_dir = os.path.join(ROOT, "sites", slug)
    os.makedirs(out_dir, exist_ok=True)
    logo_src = os.path.join(repo, "website", "public", "logos", city, r.get("logo_file") or "-")
    colours = logo_and_colours(logo_src, os.path.join(out_dir, "logo.png")) or {}

    text = (r.get("description") or "") + " " + (r.get("short_description") or "")
    services = [
        {"icon": ic, "name": name, "text": desc}
        for rx, ic, name, desc in cat["services"]
        if re.search(rx, text, re.I)
    ][:6]
    if not services:  # the description names nothing: the category's first two
        services = [{"icon": ic, "name": name, "text": desc} for _, ic, name, desc in cat["services"][:2]]

    insights = None
    ins_path = os.path.join(repo, "data", "cities", city, "review-insights", slug + ".json")
    if os.path.exists(ins_path):
        with open(ins_path, encoding="utf-8") as fh:
            insights = json.load(fh)
    highlights = None
    faq = []
    if insights:
        items = [
            {"title": clean_title(c["title"]["en"]), "text": clean(c["text"]["en"])}
            for c in insights.get("cards", [])
            if c.get("sentiment") == "positive" and clean(c["text"]["en"])
        ][:3]
        if items:
            highlights = {"title": "Why pet parents choose us", "basedOn": insights.get("reviews_in_period"), "items": items}
        faq = [{"q": f["q"]["en"], "a": f["a"]["en"]} for f in insights.get("faq", [])][:4]

    phone = r.get("phone", "")
    h = hours(r.get("opening_hours"))
    steps = cat.get("steps_mobile" if mobile else "steps", cat["steps"])
    social = {k: r.get(k, "") for k in ("instagram", "facebook") if r.get(k)}
    website = r.get("website", "")
    if "instagram" in website and "instagram" not in social:
        social["instagram"] = website
    if "facebook" in website and "facebook" not in social:
        social["facebook"] = website

    site = {
        "slug": slug,
        "name": r["name"].split(" - ")[0].strip(),
        "legalName": r["name"],
        "category": cat["key"],
        "mobile": mobile,
        "domain": "",
        "preview": True,
        "theme": {**palette(slug, cat), "ink": "#1F2430", "surface": "#FBFAF7", **colours},
        "logo": "logo.png" if os.path.exists(os.path.join(out_dir, "logo.png")) else "",
        "hero": {
            "eyebrow": f"{'Mobile ' + cat['label'].lower() if mobile else cat['label']} · {city_name}",
            "title": cat.get("title_mobile") if mobile and cat.get("title_mobile") else cat["title"],
            "subtitle": r.get("short_description") or "",
        },
        "contact": {
            "phone": phone,
            "email": r.get("email", ""),
            "address": r.get("address", ""),
            "showAddress": not mobile,
            "areaServed": f"{city_name} and nearby neighborhoods",
            "geo": {"lat": float(r["lat"]), "lng": float(r["lng"])} if r.get("lat") else None,
        },
        "rating": {
            "value": float(r["google_rating"]),
            "count": int(r["google_rating_count"]),
            "source": "Google",
            "url": f"https://www.google.com/maps/place/?q=place_id:{r['google_place_id']}" if r.get("google_place_id") else r.get("google_maps_url", ""),
        }
        if r.get("google_rating") and r.get("google_rating_count")
        else None,
        "hours": h,
        "timezone": US_TZ.get(city, "America/New_York"),
        "services": services,
        "steps": [{"title": t, "text": x} for t, x in steps],
        "highlights": highlights,
        "faq": faq,
        "social": social,
        "offer": {"price": "$100", "includes": "your own domain and hosting for the first year", "contact": sender.get("email", ""), "payUrl": ""},
    }
    site = {k: v for k, v in site.items() if v not in (None, [], {})}
    with open(os.path.join(out_dir, "site.json"), "w", encoding="utf-8") as fh:
        json.dump(site, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"sites/{slug}/site.json - draft written. Read it, then: node build.mjs {slug}")


if __name__ == "__main__":
    main()
