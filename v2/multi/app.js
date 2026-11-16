// Multi-page preview template: menu, open-now status, hours table, booking message, map.
// Everything is driven by <script id="site-config" type="application/json"> on each page.
(() => {
  const C = JSON.parse(document.getElementById("site-config").textContent);
  const DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  const SHORT = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const H = C.hours || {};
  const hasHours = Object.keys(H).length > 0;
  const fmt = (m) => { const h = Math.floor(m / 60) % 24, mm = m % 60; return `${((h + 11) % 12) + 1}${mm ? ":" + String(mm).padStart(2, "0") : ""} ${h < 12 ? "am" : "pm"}`; };
  const span = (d) => { const s = H[d]; if (!s || s === "closed") return null; return s.split("-").map((t) => { const [h, m] = t.split(":").map(Number); return h * 60 + m; }); };
  function now() {
    const p = Object.fromEntries(new Intl.DateTimeFormat("en-US", { timeZone: C.tz, weekday: "short", hour: "2-digit", minute: "2-digit", hour12: false }).formatToParts(new Date()).map((x) => [x.type, x.value]));
    return { dow: SHORT.indexOf(p.weekday), mins: (+p.hour % 24) * 60 + +p.minute };
  }
  const nextOpen = (from) => { for (let i = 1; i <= 7; i++) { const d = (from + i) % 7, s = span(d); if (s) return { i, d, s }; } return null; };

  // Mobile menu
  const mb = document.querySelector(".menu-btn"), mm = document.getElementById("mobile-menu");
  if (mb && mm) mb.addEventListener("click", () => { const o = mm.hidden; mm.hidden = !o; mb.setAttribute("aria-expanded", String(o)); });

  // Open now
  if (hasHours) document.querySelectorAll("[data-status]").forEach((el) => {
    const n = now(), h = span(n.dow); let text, tone = "closed";
    if (h && n.mins >= h[0] && n.mins < h[1]) { text = h[1] - n.mins <= 45 ? `Open now, closing soon at ${fmt(h[1])}` : `Open now, until ${fmt(h[1])}`; tone = h[1] - n.mins <= 45 ? "soon" : "open"; }
    else if (h && n.mins < h[0]) { text = `Closed now. Opens today at ${fmt(h[0])}`; tone = "soon"; }
    else { const x = nextOpen(n.dow); text = x ? `Closed now. Opens ${x.i === 1 ? "tomorrow" : DAYS[x.d]} at ${fmt(x.s[0])}` : "Closed now"; }
    el.dataset.tone = tone; el.querySelector(".status-text").textContent = text;
  });

  // Hours table
  document.querySelectorAll("[data-hours]").forEach((ht) => {
    const t = now().dow;
    ht.innerHTML = [1, 2, 3, 4, 5, 6, 0].map((d) => { const h = span(d); return `<tr class="${d === t ? "today" : ""}"><th scope="row">${DAYS[d]}</th><td>${h ? `${fmt(h[0])} – ${fmt(h[1])}` : "Closed"}</td></tr>`; }).join("");
  });

  // Booking message
  const P = C.composer;
  document.querySelectorAll("[data-composer]").forEach((box) => {
    const f = box.querySelector("form"), bubble = box.querySelector("[data-bubble]");
    const pre = box.dataset.preselect || "";
    const n = now(), opts = [];
    for (let i = 0; i < 8 && opts.length < 6; i++) {
      const dow = (n.dow + i) % 7, s = span(dow);
      if (hasHours && !s) continue;
      if (hasHours && i === 0 && n.mins > s[1] - 60) continue;
      const label = i === 0 ? "Today" : i === 1 ? "Tomorrow" : DAYS[dow], word = i === 0 ? "today" : i === 1 ? "tomorrow" : `on ${DAYS[dow]}`;
      opts.push(`<option value="${word}">${label}</option>`);
    }
    f.elements.day.innerHTML = opts.join("");
    if (f.elements.day.options.length > 1 && f.elements.day.options[0].text === "Today") f.elements.day.selectedIndex = 1;
    const val = (name) => (f.querySelector(`[name="${name}"]:checked`) || {}).value;
    function drawPet() {
      const pet = val("pet") || Object.keys(P.pets)[0], cfg = P.pets[pet], wrap = box.querySelector("[data-services]");
      const keep = [...f.querySelectorAll('[name="svc"]:checked')].map((x) => x.value);
      wrap.innerHTML = cfg.services.map(([id, l, p], i) => `<label class="chip"><input type="checkbox" name="svc" value="${id}" data-phrase="${p}" ${(keep.length ? keep.includes(id) : (pre ? pre === id : i === 0)) ? "checked" : ""}><span>${l}</span></label>`).join("");
      if (!wrap.querySelector(":checked")) wrap.querySelector("input").checked = true;
      const sz = box.querySelector("[data-sizes]"); if (sz) sz.hidden = !cfg.sizes;
    }
    function draw() {
      const pet = val("pet") || Object.keys(P.pets)[0], cfg = P.pets[pet];
      const svcs = [...f.querySelectorAll('[name="svc"]:checked')].map((x) => x.dataset.phrase);
      const list = svcs.length > 1 ? svcs.slice(0, -1).join(", ") + " and " + svcs[svcs.length - 1] : svcs[0] || "an appointment";
      const name = f.elements.petname.value.trim(), size = cfg.sizes ? val("size") : "";
      const time = f.elements.time.value, day = f.elements.day.value || "soon";
      const area = f.elements.area ? f.elements.area.value.trim() : "";
      const shy = f.elements.shy && f.elements.shy.checked;
      let t = `${P.greeting} I'd like ${list} for my ${size ? size + " " : ""}${cfg.noun}${name ? `, ${name},` : ""} ${day}${time ? ` in the ${time}` : ""}.`;
      if (area) t += ` We're in ${area}.`;
      if (shy) t += ` ${name || (pet === "cat" ? "She" : "He")} can get nervous, so a calm, patient visit would be great.`;
      t += ` ${P.ask}`;
      bubble.textContent = t.replace(/\s+/g, " ").replace(" ,", ",");
      const sep = /iPhone|iPad|Macintosh/.test(navigator.userAgent) ? "&" : "?";
      const sms = box.querySelector("[data-sms]"); if (sms) sms.href = `sms:${C.phone}${sep}body=${encodeURIComponent(bubble.textContent)}`;
      const mail = box.querySelector("[data-mail]"); if (mail) mail.href = `mailto:${C.email}?subject=${encodeURIComponent(P.subject)}&body=${encodeURIComponent(bubble.textContent)}`;
    }
    if (pre) { const own = Object.keys(P.pets).find((k) => P.pets[k].services.some((s) => s[0] === pre)); const r = own && f.querySelector(`[name="pet"][value="${own}"]`); if (r) r.checked = true; }
    f.addEventListener("change", (e) => { if (e.target.name === "pet") drawPet(); draw(); });
    f.addEventListener("input", draw);
    box.querySelector("[data-copy]").addEventListener("click", async (e) => { try { await navigator.clipboard.writeText(bubble.textContent); e.target.textContent = "Copied"; setTimeout(() => (e.target.textContent = "Copy"), 1500); } catch (err) {} });
    drawPet(); draw();
  });

  // Map
  const mapEl = document.getElementById("map");
  if (mapEl && window.L && C.lat != null) {
    const map = L.map(mapEl, { scrollWheelZoom: false }).setView([C.lat, C.lng], 15);
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", { maxZoom: 19, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>' }).addTo(map);
    L.marker([C.lat, C.lng], { icon: L.divIcon({ className: "", html: `<span class="pin-dot"></span><span class="pin-label">${C.pin}</span>`, iconSize: [0, 0] }), keyboard: false }).addTo(map);
  }

  // Thumb bar hides while a booking form is on screen
  const bar = document.querySelector(".thumb-bar"), comp = document.querySelector("[data-composer]");
  if (bar && comp && "IntersectionObserver" in window) new IntersectionObserver(([en]) => bar.classList.toggle("away", en.isIntersecting)).observe(comp);
})();
