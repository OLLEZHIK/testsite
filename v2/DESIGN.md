# Template v2: how these sites are designed

Owner, 2026-11-15: the first template "looks AI-made". v2 follows the
`frontend-design` skill (Anthropic, `.claude/skills/frontend-design/SKILL.md`):
one design plan per business, built from its own world, checked against the
generic defaults the skill lists.

## Prototype: Yofren Master Pet Grooming (Miami, mobile van)

- **Subject:** a grooming salon in a van that parks at the client's door.
  Audience: busy Miami pet owners on phones, English and Spanish.
  Main job: get a visit booked by text or call.
- **Palette (palm green from their logo, Miami flamingo and sun):** ink #1c2a17,
  leaf #77bd00 (the exact lime of their logo), leaf-deep #3b7a0a, flamingo #ff8fa3,
  sun #ffd54a, background #f5f9ee. Owner, 2026-11-15: keep the business's own logo
  and pull the palette toward it, not the other way round.
- **Type:** Anybody (variable width) for display — the hero's second line
  "stretches" in once, like the van pulling up; Hanken Grotesk for text.
- **The one bold thing:** the visit composer on a terrazzo floor — pet, size,
  services, day, neighborhood → a ready text message to the business
  (sms: link), in English or Spanish.
- **Kept quiet on purpose:** no all-caps eyebrows, no "A · B" meta strings, no
  arrows on buttons, no identical rounded cards, no numbered steps, no
  fade-up on every section. One motion moment (hero line + video).
- **Honesty:** only facts from the business's public listing (rating, review
  themes, hours, phone). Photos and the hero video are generated illustrations
  (Higgsfield), stated on the preview; replaced by the client's own photos on
  launch. No prices unless the business publishes them.

## Reusable assets (v2/assets)

Generated 2026-11-15 with Higgsfield (≈ 50 credits): hero.mp4/webm (5 s
ping-pong loop of a poodle being blow-dried in a grooming van, Miami street
outside), hero-poster.jpg, maltese.jpg, cat.jpg, paw.jpg. No logos or text, so
they fit any grooming preview until the client sends photos.

## Next businesses

Make a new plan for each (vet clinic ≠ groomer ≠ trainer), reuse the code
patterns (composer, open-now, EN/ES, thumb bar), not the look.

## Owner feedback, 2026-11-15

- Hero video: no people or hands (AI hands shake). Start frame = end frame for a
  seamless loop. Encode near the source quality (CRF ~21), never below ~1 Mbps at 1080p.
- Credits: think before spending. Fix in post first (crop, re-encode, upscale), then ask.
  Owner prefers Seedance 2.5 for quality (720p 35 credits, 1080p 80); Kling 3.0 pro is
  cheaper (~9) but weaker. Agree the spend with the owner before any video.
- Keep the business's logo; adapt the palette to it.
- Price $200. Full footer (brand, hours, contact, links, social).
- After a palette change, grep every hard-coded colour (states such as .bubble.changed
  flashed the old teal).
