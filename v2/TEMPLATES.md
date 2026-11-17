# Website templates (v2)

Owner, 2026-11-15: the mobile grooming site is approved ("груминг мне нравится, как
выглядит") and is fixed as a template. Add a second template for businesses with a fixed
address and a map, starting with a vet clinic.

Two templates, each with a reference site. A new site starts from a copy of its reference,
then gets its own palette, type and character (never the same look twice).

| Template | For | Reference | Live |
|---|---|---|---|
| Mobile service | Mobile groomers, mobile vets, pet sitters who come to you | `v2/yofren/` | https://pawenn-previews.pages.dev/v2/yofren/ |
| Fixed location: vet | Vet clinics | `v2/gulfgate/` | https://pawenn-previews.pages.dev/v2/gulfgate/ |
| Fixed location: salon | Grooming salons and home groomers (shared code in `v2/salon/`) | `v2/kays/` (price finder), `v2/legacy/` and `v2/jackelyn/` (text composer) | https://pawenn-previews.pages.dev/v2/kays/ |

## What both templates share

- Yellow preview bar on top: "example website made for X by Pawenn, not live, not the
  official site". `noindex`. Never removed until the business pays and the site moves to
  their domain.
- Sticky nav, EN/ES switch (default from the browser language, remembered), call button.
- A live status from the business's own hours in their time zone: open now, closing,
  opens tomorrow, holiday closures.
- One bold interactive element that saves the customer a phone call (see below).
- Real review themes from the Pawenn review insights, attributed ("Themes from Google
  reviews, <period>"), positive themes only, never invented quotes; the real rating.
- FAQ answered only from the business's site or reviews.
- Offer block (dashed border): "This is an example. The finished site can look different:
  tell us what to add, remove or change", what is new compared with the current site,
  price ($200 one-time, paid once live), reply to pawenn.info@gmail.com, and the fine
  print about where every fact comes from.
- Full footer: brand, hours, contact, page links, social, "Website by Pawenn", back to top.
- Phone: thumb bar with the two main actions, hidden while the bold element is on screen.
- Schema.org markup (LocalBusiness or VeterinaryCare) with the real hours and rating.

## Mobile service template (`yofren`)

- Hero: looping video of the service (no people or hands in generated video), headline
  about coming to the customer's door.
- Bold element: the visit composer. Pet, size, services, day, time, name, neighborhood;
  it writes the text message and opens the phone's messages app.
- Palette and type follow the business's own logo (the logo stays as it is).
- Sections: composer, reviews, services with photos, hours and contact, FAQ, offer.

## Fixed location template (`gulfgate`)

- Hero: headline about the place and how to come in, live status card, one still photo
  (illustration, labeled, no faces so it is never taken for real staff).
- Bold element: the visit planner. "What brings you in?" (sick today, checkup, follow-up,
  refill, emergency) gives the best way to come today, the fee, what to bring, and call or
  text buttons; the emergency choice points to emergency hospitals, never to the clinic.
- Fees as a clear list, exactly as the business publishes them, with the date they took
  effect. No fees invented or estimated; "call us" where the site says so.
- Services and what an exam covers; team as names and bios from their site, monogram
  instead of photos until they send their own.
- Hours table with today highlighted, appointment and walk-in cutoffs, pharmacy hours,
  holiday schedule; Leaflet map (OpenStreetMap tiles, muted) with a pin and a "Get
  directions" link to Google Maps with their place ID.
- Emergencies (vets): "We are not a 24-hour hospital" and the emergency hospitals the
  clinic itself lists, with tap-to-call.
- For grooming salons and other non-vet places: drop fees-per-exam, team bios become
  groomer bios, the planner becomes "book a groom" (service, size, day) as in Yofren, the
  emergency block goes away. Map, hours and parking stay.

## Salon template (`v2/salon/` + one page per salon)

- Shared `salon.css` and `salon.js`; each page sets its palette and fonts on `:root` and
  its data in `<script id="site-config" type="application/json">` (time zone, hours,
  phone, booking link, map position, and either `finder` or `composer`).
- `finder`: when the salon publishes prices (Kay's MoeGo page). Pet, size, service gives
  the price exactly as published, what's included, and Book online / Call.
- `composer`: when there are no public prices (Legacy, Jackelyn). Pet, size, services, one
  of the next open days, time, name, "nervous" tick; writes the text message.
- Home groomers: no map and no street address (only the ZIP), "ask for the address when
  you book".
- Before any email: re-check the business still has no website (2026-11-15: Yofren put a
  site live at yofrenpetgrooming.com since October, so it was taken off the list).

## Multi-page template (`v2/superstar/`, owner approved 2026-11-16)

- Built by `v2/superstar/build.py`: home, services (package comparison table), prepaid
  bundles, a page per service area (SEO: "Mobile pet grooming in <city>, FL"), booking.
- Every page: "Do we come to you?" check, booking message (text or email), open-now status.
- Look: the business's own brand colors (for Super Star, the pink and lime of their vans),
  a round friendly display face (Baloo 2 + Nunito) and soap-bubble rings in the hero.
  Owner: glam serif and black/red/gold "don't fit grooming"; terrazzo dots on the whole
  page "look bad" (tried and removed 2026-11-16), keep backgrounds plain.

## Multi-page generator (`v2/gen/make2.py`, 2026-11-16)

- Same look as Super Star, for any business in the Pawenn data: `python3 v2/gen/make2.py <slug>` writes
  `v2/s/<slug>/` with home, services, a page per service ("Vaccines in Hialeah"), hours and location
  (Leaflet map), and booking. Shared `v2/multi/style.css` and `v2/multi/app.js`, config in each page.
- Colors from the business's own logo (`PAL` in the script, picked by eye; their logo in the nav).
  Soap bubbles only for groomers (they mean grooming); everyone else gets a plain hero. Sitters and home businesses: no street address and no map.
- The hero picture shows the actual service (owner, 2026-11-16: a poodle in a pink bandana
  is not dog training). Training: a working dog with a trainer (no face); walking: a walk; daycare:
  dogs playing; vets: an exam. Reusable: `training-malinois.jpg`, `dog-walk.jpg`, `daycare-play.jpg`,
  `pet-sitter-visit.jpg`, `cat-sitting.jpg`. `cat.jpg` is a cat being groomed: grooming only, never sitting.
- Pictures: Seedream 5.0 Flash at 2K (0.5 credit; owner, 2026-11-16: GPT Image at 2.75 is too
  expensive). Landscape 4:3, one hero and three photos per site (`v2/assets/s/`), shown in frames,
  never stretched. Check every picture with people at full size before use: hands with wrong
  fingers or three hands get through at thumbnail size (owner caught one, 2026-11-16). Prefer
  scenes with no hands at all.
- Services only from their own description (keywords), never a generic list. Old single-page
  previews in `v2/p/` stay online for links already sent.

## Rules that keep the sites safe (vets especially)

1. Every fact comes from the business's own site or Google listing, with the month it was
   read; nothing invented (no founding year, no awards, no "best", no staff counts).
2. No medical advice and no claims about outcomes. Use the clinic's own words for
   services. "Specialist" only if the clinic says board-certified.
3. No generated faces or staff photos; no photos copied from their site. Illustrations
   are labeled.
4. Emergencies always go to emergency hospitals the clinic lists; the planner never tells
   a pet owner to wait.
5. No forms that collect pet or owner data on the preview: call, text and email only.
   (A live site can add the clinic's own booking system.)
6. Accessible: zoom allowed, contrast AA, keyboard focus visible, 44 px tap targets,
   reduced motion respected.
7. The preview is plainly a preview and never pretends to be the official site.

## Assets and credits

Higgsfield budget for the whole sales project: 200 credits (owner). Spent so far:
about 123. Think before spending: fix in post first (crop, re-encode, upscale), images
cost 2.75 at high quality, video only after agreeing with the owner (Seedance 2.5:
35 credits at 720p, 80 at 1080p). Reuse: `v2/assets/hero.*` (grooming van video),
`maltese.jpg`, `cat.jpg`, `paw.jpg`, `vet-exam.jpg`, `salon-doodle.jpg`, `salon-towel.jpg`.

## Short links in emails (owner, 2026-11-17)

Emails never carry the long `/v2/s/<slug>/` address. Every preview gets a short
name in `short-links.txt` (`<name> <path>`, lowercase letters and digits, 6–12
characters, recognisable: `bowwow`, `goldenpaws`), and the email links
`https://pawenn-previews.pages.dev/<name>`. The build turns the file into
`dist/_redirects`; it fails on a repeated name or a missing preview. After the
push, check the short link opens the preview before the email goes out.
