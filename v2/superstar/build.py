#!/usr/bin/env python3
"""Multi-page preview for Super Star Mobile Grooming (mobile grooming, Miami-Dade and Broward).

Every fact comes from superstargrooming.com (services, bundles, service areas, policies,
testimonial; read 2026-11-16) and their Google listing via Pawenn (hours, rating).
Run: python3 v2/superstar/build.py  -> writes index.html, services/, bundles/, areas/, book/.
"""
import html, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
e = html.escape

PHONE, PHONE_LABEL, PHONE_VANITY = "+13058369274", "305-836-9274", "305-836-WASH"
EMAIL = "info@superstargrooming.com"
AREAS = [("aventura", "Aventura", "Miami-Dade"), ("cooper-city", "Cooper City", "Broward"), ("coral-gables", "Coral Gables", "Miami-Dade"),
         ("cutler-bay", "Cutler Bay", "Miami-Dade"), ("dania-beach", "Dania Beach", "Broward"), ("davie", "Davie", "Broward"),
         ("doral", "Doral", "Miami-Dade"), ("fort-lauderdale", "Fort Lauderdale", "Broward"), ("hallandale", "Hallandale Beach", "Broward"),
         ("hialeah", "Hialeah", "Miami-Dade"), ("hialeah-gardens", "Hialeah Gardens", "Miami-Dade"), ("hollywood", "Hollywood", "Broward"),
         ("kendall", "Kendall", "Miami-Dade"), ("key-biscayne", "Key Biscayne", "Miami-Dade"), ("miami", "Miami", "Miami-Dade"),
         ("miami-beach", "Miami Beach", "Miami-Dade"), ("miami-gardens", "Miami Gardens", "Miami-Dade"), ("miami-lakes", "Miami Lakes", "Miami-Dade"),
         ("miami-springs", "Miami Springs", "Miami-Dade"), ("miramar", "Miramar", "Broward"), ("opa-locka", "Opa-locka", "Miami-Dade"),
         ("pembroke-pines", "Pembroke Pines", "Broward"), ("plantation", "Plantation", "Broward"), ("southwest-ranches", "Southwest Ranches", "Broward"),
         ("west-park", "West Park", "Broward"), ("weston", "Weston", "Broward")]
HOURS = {"0": "06:30-20:00", "1": "06:30-20:30", "2": "06:30-20:30", "3": "06:30-20:30", "4": "06:30-20:30", "5": "06:30-20:30", "6": "06:30-20:00"}
CONFIG = {"tz": "America/New_York", "hours": HOURS, "phone": PHONE, "phoneLabel": PHONE_LABEL, "areas": [[s, n] for s, n, _ in AREAS]}

NAV = [("", "Home"), ("services/", "Services"), ("bundles/", "Prepaid bundles"), ("areas/", "Service areas"), ("book/", "Book")]


def page(path, title, desc, body, active):
    depth = path.count("/")
    up = "../" * depth
    cur = ' aria-current="page"'
    nav = "".join(f'<a href="{up}{href}"{cur if href == active else ""}>{label}</a>' for href, label in NAV)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;700;800&family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{up}style.css">
<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", "@type": "PetGroomer", "name": "Super Star Mobile Grooming", "telephone": "+1-305-836-9274", "email": EMAIL, "areaServed": [n for _, n, _ in AREAS], "aggregateRating": {"@type": "AggregateRating", "ratingValue": "4.5", "reviewCount": "1299"}, "sameAs": ["http://www.facebook.com/SSGrooming"]})}</script>
<script id="site-config" type="application/json">{json.dumps(CONFIG)}</script>
</head>
<body>
<div class="preview-bar"><p><strong>Preview</strong> An example multi-page website made for Super Star Mobile Grooming by Pawenn. It is not live and not the official site.</p><a href="{up}#make-it-yours">See the offer</a></div>
<header class="nav">
  <a class="brand" href="{up}" aria-label="Super Star Mobile Grooming home"><span class="brand-star" aria-hidden="true">★</span><span class="brand-name">Super Star<small>Mobile Grooming</small></span></a>
  <nav class="nav-links" aria-label="Pages">{nav}</nav>
  <a class="btn btn-gold nav-call" href="tel:{PHONE}"><span class="nav-call-long">{PHONE_LABEL}</span><span class="nav-call-short">Call</span></a>
  <button class="menu-btn" type="button" aria-expanded="false" aria-controls="mobile-menu">Menu</button>
</header>
<nav class="mobile-menu" id="mobile-menu" hidden aria-label="Pages">{nav}<a href="tel:{PHONE}">Call {PHONE_LABEL}</a></nav>
<main id="top">
{body}
</main>
<footer class="footer">
  <div class="footer-main">
    <div><p class="footer-brand"><span aria-hidden="true">★</span> Super Star Mobile Grooming</p><p class="muted">South Florida's mobile pet grooming salon, serving Miami-Dade and Broward counties.</p></div>
    <div><h2>Visit us at home</h2><p class="muted">We come to you, every day: Monday to Friday 6:30 am to 8:30 pm, weekends 6:30 am to 8 pm.</p></div>
    <div><h2>Contact</h2><p><a href="tel:{PHONE}">{PHONE_LABEL} <small class="vanity">(305-836-WASH)</small></a><br><a href="mailto:{EMAIL}">{EMAIL}</a><br><a href="http://www.facebook.com/SSGrooming" target="_blank" rel="noopener">Facebook</a></p></div>
    <nav aria-label="Footer"><h2>Pages</h2>{nav}</nav>
  </div>
  <div class="footer-bottom"><p>© 2026 Super Star Mobile Grooming</p><p>Website by <a href="https://pawenn.com/en/" rel="noopener">Pawenn</a></p></div>
</footer>
<div class="thumb-bar"><a class="btn btn-gold" href="{up}book/">Book a groom</a><a class="btn btn-ghost" href="tel:{PHONE}">Call</a></div>
<script src="{up}app.js" defer></script>
</body>
</html>
"""


def composer(area_slug=""):
    opts = "".join(f'<option value="{s}"{" selected" if s == area_slug else ""}>{e(n)}</option>' for s, n, _ in AREAS)
    return f"""<div class="composer" data-composer>
  <form class="composer-form" onsubmit="return false">
    <fieldset><legend>Who's getting the star treatment?</legend><div class="chips">
      <label class="chip"><input type="radio" name="pet" value="dog" checked><span>Dog</span></label>
      <label class="chip"><input type="radio" name="pet" value="cat"><span>Cat</span></label></div></fieldset>
    <fieldset data-dog-only><legend>How big?</legend><div class="chips">
      <label class="chip"><input type="radio" name="size" value="small" checked><span>Small</span></label>
      <label class="chip"><input type="radio" name="size" value="medium"><span>Medium</span></label>
      <label class="chip"><input type="radio" name="size" value="large"><span>Large</span></label></div></fieldset>
    <fieldset><legend>Which service?</legend><div class="chips" data-services></div></fieldset>
    <fieldset><legend>Extras</legend><div class="chips">
      <label class="chip"><input type="checkbox" name="extra" value="a flea and tick treatment"><span>Flea &amp; tick</span></label>
      <label class="chip"><input type="checkbox" name="extra" value="a de-shedding treatment"><span>De-shedding</span></label>
      <label class="chip"><input type="checkbox" name="extra" value="nail grinding"><span>Nail grinding</span></label></div></fieldset>
    <div class="row2">
      <label class="field"><span>Where are you?</span><select name="area">{opts}</select></label>
      <label class="field"><span>Which day?</span><select name="day" data-days></select></label>
    </div>
    <div class="row2">
      <label class="field"><span>Time</span><select name="time"><option value="morning">Morning</option><option value="midday">Midday</option><option value="afternoon">Afternoon</option><option value="evening">Evening</option></select></label>
      <label class="field"><span>Pet's name (optional)</span><input name="name" type="text" maxlength="30" autocomplete="off"></label>
    </div>
  </form>
  <aside class="composer-out">
    <p class="ticket-label">Your message</p>
    <p class="bubble" data-bubble></p>
    <div class="actions"><a class="btn btn-gold" data-sms href="sms:{PHONE}">Send as a text</a><a class="btn btn-ghost" data-mail href="mailto:{EMAIL}">Email it</a><button class="btn btn-ghost" type="button" data-copy>Copy</button></div>
    <p class="fine">Opens your messages or email app with everything filled in. Prefer to talk? Call {PHONE_LABEL}.</p>
  </aside>
</div>"""


AREA_CHECK = """<div class="area-check" data-areacheck>
  <label for="area-input">Do we come to you?</label>
  <div class="area-row"><input id="area-input" list="area-list" placeholder="Type your city, e.g. Doral" autocomplete="off"><button class="btn btn-gold" type="button">Check</button></div>
  <datalist id="area-list"></datalist>
  <p class="area-result" aria-live="polite"></p>
</div>"""

OFFER = """<section class="offer" id="make-it-yours" aria-labelledby="offer-title">
  <h2 id="offer-title">This is an example. Want it as your website?</h2>
  <p>Everything here comes from superstargrooming.com and your Google listing. The finished site can look different: tell us what to add, remove or change, and we'll do it before launch.</p>
  <div class="offer-grid">
    <ul>
      <li>Separate pages for services, prepaid bundles and all 26 service areas, each ready for Google</li>
      <li>No placeholder text and no broken map: every page shows real details</li>
      <li>"Do we come to you?" check and a booking message builder on every page</li>
      <li>Open-now status from your hours, works on any phone, https</li>
      <li>Your gallery, Super Star of the Month and stylists, with your real photos</li>
    </ul>
    <div><p class="offer-price">$200 <span>one-time, paid only once it's live on superstargrooming.com and you're happy</span></p>
    <a class="btn btn-gold" href="mailto:pawenn.info@gmail.com?subject=Super%20Star%20website">Reply to Pawenn</a></div>
  </div>
  <p class="fine">The video is an illustration, not your van or a client's pet. Services, bundles, areas, policies and the testimonial come from your current site (November 2026); hours and rating from your Google listing.</p>
</section>"""


def home():
    areas = "".join(f'<a href="areas/{s}/">{e(n)}</a>' for s, n, _ in AREAS)
    body = f"""
<section class="hero">
  <video class="hero-video" autoplay muted loop playsinline poster="../assets/superstar-poster.jpg" aria-hidden="true">
    <source src="../assets/superstar.webm" type="video/webm"><source src="../assets/superstar.mp4" type="video/mp4">
  </video>
  <div class="hero-shade"></div>
  <div class="hero-copy">
    <p class="kicker">Mobile pet grooming, Miami-Dade and Broward</p>
    <h1>Pampered, prepped, <em>and ready for the red carpet.</em></h1>
    <p class="lead">A full grooming salon on wheels parks at your door. Baths, haircuts, nails and teeth for dogs and cats, plus a bow or bandana to wear around town.</p>
    <div class="status" id="status"><span class="dot"></span><span class="status-text"></span></div>
    <div class="hero-actions"><a class="btn btn-gold" href="book/">Book a groom</a><a class="btn btn-ghost" href="tel:{PHONE}">Call {PHONE_LABEL}</a></div>
    <p class="rating"><span class="stars">★★★★★</span> 4.5 on Google from 1,299 reviews</p>
  </div>
</section>

<section class="band">
  <div class="wrap two">
    <div><h2>Do we come to you?</h2><p class="muted">We serve 26 cities across Miami-Dade and Broward. Type yours.</p></div>
    {AREA_CHECK}
  </div>
</section>

<section class="wrap section">
  <h2>How a Super Star groom works</h2>
  <ol class="steps">
    <li><strong>You book</strong><span>Send us your pet, service and a day. We confirm the time.</span></li>
    <li><strong>We park outside</strong><span>A clean, fully equipped mobile salon comes to your home.</span></li>
    <li><strong>Groomed at home</strong><span>No car ride and no waiting room for your pet.</span></li>
    <li><strong>Red-carpet finish</strong><span>Girls get a bow, gentlemen a bandana.</span></li>
  </ol>
</section>

<section class="wrap section">
  <div class="section-head"><h2>Four ways to shine</h2><a class="link" href="services/">See every service</a></div>
  <div class="cards">
    <article class="card"><h3>Wash</h3><p>Shampoo and conditioner, ears, nails, glands, rounded paws and a sanitary trim.</p></article>
    <article class="card"><h3>Complete Grooming</h3><p>Everything in the Wash, plus a haircut.</p></article>
    <article class="card star"><h3>Super Star Wash</h3><p>Everything in the Wash, plus teeth brushing.</p></article>
    <article class="card star"><h3>Super Star Complete</h3><p>The whole list: haircut and teeth brushing included.</p></article>
  </div>
  <p class="fine">Prices vary with size, breed and coat condition. Cats get their own Wash and Complete.</p>
</section>

<section class="book-band" id="book">
  <div class="wrap">
    <h2>Build your booking message</h2>
    <p class="muted">Pick the details. We'll write the text for you to send.</p>
    {composer()}
  </div>
</section>

<section class="wrap section bundles-teaser">
  <div><h2>Lights, Camera, Action</h2><p class="muted">Prepaid bundles for regulars: pay once and save up to $120.</p><a class="btn btn-gold" href="bundles/">See the bundles</a></div>
  <div class="marquee"><span>Lights</span><span>Camera</span><span>Action</span></div>
</section>

<section class="wrap section quote">
  <blockquote><p>"My dog Mary HATES going to the vet or groomers. They came to us and that really helped ease my dog's anxiety. I'll definitely use them again and recommend to my friends."</p><cite>Emily R., from our testimonials</cite></blockquote>
  <p class="rating-big"><span>4.5</span> on Google from 1,299 reviews</p>
</section>

<section class="wrap section">
  <h2>Where we groom</h2>
  <div class="area-cloud">{areas}</div>
</section>

<section class="wrap section faq">
  <h2>Questions people ask</h2>
  <details><summary>Where does the grooming happen?</summary><p>In our clean, fully equipped mobile grooming salon, parked at your home.</p></details>
  <details><summary>How much does a groom cost?</summary><p>It depends on your pet's size, breed and coat condition. Send us the details and we'll tell you.</p></details>
  <details><summary>Do you groom cats?</summary><p>Yes: a Cat Wash or a Cat Complete with a haircut.</p></details>
  <details><summary>What if I need to cancel?</summary><p>Please let us know ahead of time. Cancelling within the hour of the appointment, or a no-show, adds a $10 fee to the next visit.</p></details>
  <details><summary>How can I pay?</summary><p>Cash or credit card: Visa, MasterCard and Discover.</p></details>
</section>
{OFFER}
"""
    return page("index.html", "Super Star Mobile Grooming | Mobile pet grooming in Miami-Dade and Broward",
                "Mobile dog and cat grooming at your door in 26 cities across Miami-Dade and Broward. 4.5 on Google from 1,299 reviews.", body, "")


def services():
    body = f"""
<section class="page-head"><div class="wrap"><p class="kicker">Services</p><h1>Every service, done at your door</h1><p class="lead">All of our services are performed at your location in a clean, fully equipped mobile grooming salon.</p></div></section>
<section class="wrap section two">
  <div><h2>For dogs</h2>
    <div class="table-wrap"><table class="compare"><thead><tr><th></th><th scope="col">Wash</th><th scope="col">Complete Grooming</th><th scope="col">Super Star Wash</th><th scope="col">Super Star Complete</th></tr></thead><tbody><tr><th scope="row">Shampoo and conditioner</th><td><span class="yes" aria-label="included">★</span></td><td><span class="yes" aria-label="included">★</span></td><td><span class="yes" aria-label="included">★</span></td><td><span class="yes" aria-label="included">★</span></td></tr><tr><th scope="row">Haircut</th><td><span class="no" aria-label="not included">–</span></td><td><span class="yes" aria-label="included">★</span></td><td><span class="no" aria-label="not included">–</span></td><td><span class="yes" aria-label="included">★</span></td></tr><tr><th scope="row">Ear cleaning</th><td><span class="yes" aria-label="included">★</span></td><td><span class="yes" aria-label="included">★</span></td><td><span class="yes" aria-label="included">★</span></td><td><span class="yes" aria-label="included">★</span></td></tr><tr><th scope="row">Nail trimming</th><td><span class="yes" aria-label="included">★</span></td><td><span class="yes" aria-label="included">★</span></td><td><span class="yes" aria-label="included">★</span></td><td><span class="yes" aria-label="included">★</span></td></tr><tr><th scope="row">Teeth brushing</th><td><span class="no" aria-label="not included">–</span></td><td><span class="no" aria-label="not included">–</span></td><td><span class="yes" aria-label="included">★</span></td><td><span class="yes" aria-label="included">★</span></td></tr><tr><th scope="row">Gland expression</th><td><span class="yes" aria-label="included">★</span></td><td><span class="yes" aria-label="included">★</span></td><td><span class="yes" aria-label="included">★</span></td><td><span class="yes" aria-label="included">★</span></td></tr><tr><th scope="row">Rounding the paws</th><td><span class="yes" aria-label="included">★</span></td><td><span class="yes" aria-label="included">★</span></td><td><span class="yes" aria-label="included">★</span></td><td><span class="yes" aria-label="included">★</span></td></tr><tr><th scope="row">Sanitary and nose area clean-up</th><td><span class="yes" aria-label="included">★</span></td><td><span class="yes" aria-label="included">★</span></td><td><span class="yes" aria-label="included">★</span></td><td><span class="yes" aria-label="included">★</span></td></tr></tbody></table></div>
  </div>
  <div><h2>For cats</h2>
    <div class="table-wrap"><table class="compare"><thead><tr><th></th><th scope="col">Cat Wash</th><th scope="col">Cat Complete</th></tr></thead><tbody><tr><th scope="row">Shampoo and conditioner</th><td><span class="yes" aria-label="included">★</span></td><td><span class="yes" aria-label="included">★</span></td></tr><tr><th scope="row">Haircut</th><td><span class="no" aria-label="not included">–</span></td><td><span class="yes" aria-label="included">★</span></td></tr><tr><th scope="row">Ear cleaning</th><td><span class="yes" aria-label="included">★</span></td><td><span class="yes" aria-label="included">★</span></td></tr><tr><th scope="row">Nail trimming</th><td><span class="yes" aria-label="included">★</span></td><td><span class="yes" aria-label="included">★</span></td></tr></tbody></table></div>
    <h2 class="mt">Extras</h2>
    <ul class="ticks"><li>Spot-on treatment</li><li>Flea and tick treatment</li><li>De-shedding treatment</li><li>Nail grinding</li></ul>
  </div>
</section>
<section class="band"><div class="wrap two">
  <div><h2>The red-carpet finish</h2><p class="muted">All pets are super stars, so every makeover ends with an accessory: hair bows for the ladies, a bandana for the gentlemen.</p></div>
  <div><h2>Prices</h2><p class="muted">Prices vary with size, breed and the condition of your pet's coat. Send us the details for a quote, or save with a <a href="../bundles/">prepaid bundle</a>.</p></div>
</div></section>
<section class="wrap section two">
  <div><h2>Cancellation policy</h2><p class="muted">Please tell us about any changes to your appointment. Cancelling within the hour of the appointment, or a no-show, adds a $10 fee to the next visit. After two missed appointments without notice, the next one is paid in advance by phone.</p></div>
  <div><h2>Payment</h2><p class="muted">Cash and credit cards: Visa, MasterCard and Discover.</p></div>
</section>
<section class="book-band"><div class="wrap"><h2>Ready to book?</h2>{composer()}</div></section>
{OFFER}"""
    return page("services/index.html", "Services | Super Star Mobile Grooming", "Dog and cat grooming packages, extras, policies and payment for Super Star Mobile Grooming.", body, "services/")


def bundles():
    body = f"""
<section class="page-head"><div class="wrap"><p class="kicker">Prepaid bundles</p><h1>Lights, Camera, Action</h1><p class="lead">To reward loyal clients: buy grooming in advance and save instantly. The more you bundle, the more you save.</p></div></section>
<section class="wrap section">
  <div class="bundles" data-bundles>
    <button class="bundle" type="button" data-pay="149.99" data-get="170"><span class="b-name">Lights</span><span class="b-pay">$149.99</span><span class="b-get">for $170 of grooming</span><span class="b-save">You save $20</span></button>
    <button class="bundle on" type="button" data-pay="249.99" data-get="300"><span class="b-name">Camera</span><span class="b-pay">$249.99</span><span class="b-get">for $300 of grooming</span><span class="b-save">You save $50</span></button>
    <button class="bundle" type="button" data-pay="479.99" data-get="600"><span class="b-name">Action</span><span class="b-pay">$479.99</span><span class="b-get">for $600 of grooming</span><span class="b-save">You save $120</span></button>
  </div>
  <div class="bundle-out" aria-live="polite" data-bundle-out></div>
  <p class="fine">Discount does not apply to products. One pet per bundle.</p>
</section>
<section class="book-band"><div class="wrap"><h2>Ask about a bundle</h2>{composer()}</div></section>
{OFFER}"""
    return page("bundles/index.html", "Prepaid grooming bundles | Super Star Mobile Grooming", "Lights, Camera and Action prepaid grooming bundles: save $20, $50 or $120.", body, "bundles/")


def areas_index():
    groups = ""
    for county in ("Miami-Dade", "Broward"):
        links = "".join(f'<a href="{s}/">{e(n)}</a>' for s, n, c in AREAS if c == county)
        groups += f'<div><h2>{county}</h2><div class="area-cloud">{links}</div></div>'
    body = f"""
<section class="page-head"><div class="wrap"><p class="kicker">Service areas</p><h1>We come to 26 cities</h1><p class="lead">From Key Biscayne to Weston, our mobile salon comes to your door.</p>{AREA_CHECK}</div></section>
<section class="wrap section two">{groups}</section>
{OFFER}"""
    return page("areas/index.html", "Service areas | Super Star Mobile Grooming", "Mobile pet grooming in 26 cities across Miami-Dade and Broward counties.", body, "areas/")


def area_page(slug, name, county):
    others = [a for a in AREAS if a[2] == county and a[0] != slug][:6]
    near = ", ".join(n for _, n, _ in others)
    body = f"""
<section class="page-head"><div class="wrap"><p class="kicker">Mobile grooming in {county} County</p><h1>Mobile pet grooming in {e(name)}</h1><p class="lead">Super Star brings a full grooming salon to homes in {e(name)}: baths, haircuts, nails, ears and teeth for dogs and cats, without the car ride.</p>
<div class="hero-actions"><a class="btn btn-gold" href="#book">Book in {e(name)}</a><a class="btn btn-ghost-dark" href="tel:{PHONE}">Call {PHONE_LABEL}</a></div></div></section>
<section class="wrap section two">
  <div><h2>What we do in {e(name)}</h2><ul class="ticks"><li>Wash and Complete Grooming for dogs</li><li>Super Star Wash and Super Star Complete</li><li>Cat Wash and Cat Complete</li><li>Flea and tick, de-shedding and nail grinding extras</li></ul></div>
  <div><h2>When</h2><p class="muted">Every day: Monday to Friday 6:30 am to 8:30 pm, weekends 6:30 am to 8 pm.</p><h2 class="mt">Also nearby</h2><p class="muted">{e(near)}.</p></div>
</section>
<section class="book-band" id="book"><div class="wrap"><h2>Book in {e(name)}</h2>{composer(slug)}</div></section>
{OFFER}"""
    return page(f"areas/{slug}/index.html", f"Mobile pet grooming in {name}, FL | Super Star Mobile Grooming",
                f"Mobile dog and cat grooming at your home in {name}, {county} County. Book Super Star Mobile Grooming.", body, "areas/")


def book():
    body = f"""
<section class="page-head"><div class="wrap"><p class="kicker">Book</p><h1>Book your pet's makeover</h1><p class="lead">Build your message below, or call {PHONE_LABEL}. We'll confirm a time.</p><div class="status" id="status"><span class="dot"></span><span class="status-text"></span></div></div></section>
<section class="book-band"><div class="wrap">{composer()}</div></section>
<section class="wrap section two">
  <div><h2>Hours</h2><table class="hours" id="hours"></table></div>
  <div><h2>Contact</h2><p><a href="tel:{PHONE}">{PHONE_LABEL} <small class="vanity">(305-836-WASH)</small></a><br><a href="mailto:{EMAIL}">{EMAIL}</a></p>{AREA_CHECK}</div>
</section>
{OFFER}"""
    return page("book/index.html", "Book a groom | Super Star Mobile Grooming", "Book mobile dog or cat grooming at your door in Miami-Dade and Broward.", body, "book/")


def write(path, content):
    full = os.path.join(HERE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w").write(content)


if __name__ == "__main__":
    write("index.html", home())
    write("services/index.html", services())
    write("bundles/index.html", bundles())
    write("areas/index.html", areas_index())
    write("book/index.html", book())
    for s, n, c in AREAS:
        write(f"areas/{s}/index.html", area_page(s, n, c))
    print("pages:", 5 + len(AREAS))
