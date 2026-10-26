# Sites for local pet businesses

One template, many sites. Each business is a folder `sites/<slug>/` with a
`site.json` (all texts, colours, hours, contacts) and its images. The build
turns it into a static site with no dependencies — Node 18+ is all it needs.

```
template/       the design: page.mjs (layout), styles.css, script.js, icons.mjs
sites/<slug>/   one business: site.json + logo.png
tools/          from_pawenn.py - draft a site from a Pawenn listing
outreach/       PLAYBOOK.md (sales system, in Russian), templates.md, leads.csv
build.mjs       sites -> dist/
```

## Build and look

```bash
node build.mjs                 # every site -> dist/<slug>/ (previews) + dist/index.html
node build.mjs <slug>          # one site -> dist/<slug>/
SITE=<slug> node build.mjs     # one site at the root of dist/ (a client's live site)
cd dist && python3 -m http.server 4000   # open http://localhost:4000/<slug>/
```

## A new site

From a Pawenn listing (`../pawenn` is the Pawenn repository):

```bash
python3 tools/from_pawenn.py ../pawenn miami yofren-master-mobile-pet-grooming
node build.mjs yofren-master-mobile-pet-grooming
```

The tool writes a **draft**. Facts (hours, phone, rating, review highlights)
come from Pawenn; the headline is the category's default and the services
are picked from the words in the place's own description. Read `site.json`
and fix anything before sending. Colours come from the logo (Pillow
installed) or the category's default.

By hand: copy `sites/yofren-master-mobile-pet-grooming/` and edit
`site.json`. Every section is optional — leave out `hours`, `faq`,
`highlights`… and the section disappears.

### site.json

| Key | What |
|---|---|
| `name`, `legalName` | short name (headings) and full name (footer, preview bar) |
| `category` | `grooming`, `vet`, `training`, `sitting`, `hotel`, `shop` |
| `mobile` | `true` for businesses that come to the client (copy, map, address) |
| `domain` | the live domain, e.g. `yofrengrooming.com` (canonical, Open Graph) |
| `preview` | `true`: preview bar + `noindex`. Always `false` on a live site (`SITE=` build sets it) |
| `theme` | `accent`, `accentDeep`, `ink`, `surface` colours |
| `hero` | `eyebrow`, `title`, `subtitle` |
| `contact` | `phone`, `email`, `address`, `showAddress` (false for home-based), `areaServed`, `geo` |
| `rating` | `value`, `count`, `source`, `url` |
| `hours` | `mo`…`su`: `"08:00-19:00"`, `"09:00-12:00,13:00-17:00"`, `"closed"`, `"24h"` |
| `timezone` | IANA zone for "Open now" |
| `services` | `[{icon, name, text, price?}]` — icons in `template/icons.mjs` |
| `steps`, `highlights`, `faq`, `social` | the sections of the same name |
| `offer` | preview bar: `price`, `includes`, `contact` (email) or `payUrl` |

## Deploy

**Previews** (one project, all sites under `/<slug>/`): import the repository
in Vercel, default settings from `vercel.json`. Send clients
`https://<project>.vercel.app/<slug>/`.

**A client's live site**: a separate project from the same repository with
the environment variable `SITE=<slug>`; add the client's domain to that
project. In `site.json` set `domain` and `preview: false` first.

Hosting note: Vercel's free Hobby plan is for non-commercial use only. Sites
we sell need Vercel Pro (20 $ a month per member, any number of projects) or
Cloudflare Pages (free for commercial use, custom domains included; build
command `node build.mjs`, output `dist`, variable `SITE=<slug>`).
