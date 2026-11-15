// Fixed-location salon template: live status, hours, price finder, map, thumb bar.
// Each site puts its data in <script id="site-config" type="application/json">.
(() => {
  const C = JSON.parse(document.getElementById("site-config").textContent);
  const DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  const SHORT = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  const fmt = (m) => {
    const h = Math.floor(m / 60), mm = m % 60, h12 = ((h + 11) % 12) + 1;
    return `${h12}${mm ? ":" + String(mm).padStart(2, "0") : ""} ${h < 12 ? "am" : "pm"}`;
  };
  // Minutes from "HH:MM-HH:MM", or null when closed.
  const span = (s) => {
    if (!s || s === "closed") return null;
    const [a, b] = s.split("-").map((t) => { const [h, m] = t.split(":").map(Number); return h * 60 + m; });
    return [a, b];
  };
  const hours = (dow) => span(C.hours[dow]);

  function local() {
    const p = Object.fromEntries(new Intl.DateTimeFormat("en-US", {
      timeZone: C.tz, year: "numeric", month: "2-digit", day: "2-digit", weekday: "short", hour: "2-digit", minute: "2-digit", hour12: false,
    }).formatToParts(new Date()).map((x) => [x.type, x.value]));
    return { ymd: `${p.year}-${p.month}-${p.day}`, dow: SHORT.indexOf(p.weekday), mins: (+p.hour % 24) * 60 + +p.minute };
  }
  const closedOn = (ymd) => (C.closedDates || {})[ymd];
  function nextOpen(now) {
    for (let i = 1; i <= 8; i++) {
      const d = new Date(`${now.ymd}T12:00:00Z`); d.setUTCDate(d.getUTCDate() + i);
      const ymd = d.toISOString().slice(0, 10), dow = d.getUTCDay(), h = hours(dow);
      if (h && !closedOn(ymd)) return { word: i === 1 ? "tomorrow" : DAYS[dow], at: h[0] };
    }
    return null;
  }

  function renderStatus() {
    const el = document.getElementById("status");
    if (!el) return;
    const now = local(), h = closedOn(now.ymd) ? null : hours(now.dow);
    let main, sub = "", tone = "closed";
    if (h && now.mins >= h[0] && now.mins < h[1]) {
      tone = h[1] - now.mins <= 60 ? "late" : "open";
      main = `Open now until ${fmt(h[1])}`;
      sub = C.openNote || "";
    } else if (h && now.mins < h[0]) {
      tone = "soon"; main = `Opens today at ${fmt(h[0])}`;
    } else {
      main = closedOn(now.ymd) ? `Closed today for ${closedOn(now.ymd)}` : "Closed now";
      const n = nextOpen(now); if (n) sub = `Opens ${n.word} at ${fmt(n.at)}`;
    }
    el.dataset.tone = tone;
    el.querySelector(".status-main").textContent = main;
    el.querySelector(".status-sub").textContent = sub;
  }

  function renderHours() {
    const t = document.getElementById("hours");
    if (!t) return;
    const today = local().dow;
    // Group consecutive days with the same hours, Monday first.
    const order = [1, 2, 3, 4, 5, 6, 0], rows = [];
    order.forEach((d) => {
      const v = C.hours[d] || "closed", last = rows[rows.length - 1];
      if (last && last.v === v) last.days.push(d); else rows.push({ v, days: [d] });
    });
    t.innerHTML = rows.map((r) => {
      const label = r.days.length > 2 ? `${DAYS[r.days[0]]} to ${DAYS[r.days[r.days.length - 1]]}` : r.days.map((d) => DAYS[d]).join(" and ");
      const h = span(r.v), isToday = r.days.includes(today);
      return `<tr class="${isToday ? "today" : ""}"><th scope="row">${label}${isToday ? ' <span class="today-tag">today</span>' : ""}</th><td>${h ? `${fmt(h[0])} – ${fmt(h[1])}` : "Closed"}</td></tr>`;
    }).join("");
  }

  // Price finder: prices exactly as the business publishes them.
  function finder() {
    const box = document.getElementById("finder");
    if (!box || !C.finder) return;
    const F = C.finder, petSel = box.querySelector("[data-pets]"), sizeSel = box.querySelector("[data-sizes]"), svcSel = box.querySelector("[data-services]"), out = document.getElementById("quote");
    const pets = Object.keys(F);
    petSel.innerHTML = pets.map((p, i) => `<label class="chip"><input type="radio" name="pet" value="${p}" ${i ? "" : "checked"}><span>${F[p].label}</span></label>`).join("");
    const state = () => ({ pet: box.querySelector('input[name="pet"]:checked').value, size: (box.querySelector('input[name="size"]:checked') || {}).value, svc: (box.querySelector('input[name="svc"]:checked') || {}).value });
    function drawOptions() {
      const s = state(), P = F[s.pet];
      sizeSel.closest(".step").hidden = !P.sizes;
      if (P.sizes) {
        const keep = P.sizes.some((z) => z.id === s.size) ? s.size : P.sizes[0].id;
        sizeSel.innerHTML = P.sizes.map((z) => `<label class="size-opt"><input type="radio" name="size" value="${z.id}" ${z.id === keep ? "checked" : ""}><span><strong>${z.label}</strong><small>${z.note}</small></span></label>`).join("");
      }
      const keepSvc = P.services.some((v) => v.id === s.svc) ? s.svc : P.services[0].id;
      svcSel.innerHTML = P.services.map((v) => `<label class="chip"><input type="radio" name="svc" value="${v.id}" ${v.id === keepSvc ? "checked" : ""}><span>${v.label}</span></label>`).join("");
      drawQuote();
    }
    function drawQuote() {
      const s = state(), P = F[s.pet], v = P.services.find((x) => x.id === s.svc);
      const price = P.sizes ? v.prices[s.size] : v.price;
      const size = P.sizes ? P.sizes.find((z) => z.id === s.size) : null;
      const priceHtml = price ? `<span class="quote-price">${price}</span>` : `<span class="quote-price quote-call">Call us</span>`;
      const what = `${v.label}${size ? `, ${size.label.toLowerCase()} ${P.noun || ""} (${size.note})` : ""}`;
      out.innerHTML = `<p class="quote-label">Your price</p>${priceHtml}
        <p class="quote-what">${what}</p>
        ${price ? "" : `<p class="quote-note">${C.noPriceNote || "This one isn't on the price list. Call us and we'll quote it."}</p>`}
        ${v.includes ? `<p class="quote-inc"><strong>Includes:</strong> ${v.includes}</p>` : ""}
        ${v.note ? `<p class="quote-note">${v.note}</p>` : ""}
        <div class="quote-actions">${C.booking ? `<a class="btn btn-solid" href="${C.booking}" target="_blank" rel="noopener">Book online</a>` : ""}<a class="btn ${C.booking ? "btn-line" : "btn-solid"}" href="tel:${C.phone}">Call ${C.phoneLabel}</a></div>
        <p class="quote-src">${C.priceSource}</p>`;
    }
    box.addEventListener("change", (e) => { if (e.target.name === "pet") drawOptions(); else drawQuote(); });
    drawOptions();
  }

  // Request composer (for salons without a public price list): writes a text message.
  function composer() {
    const box = document.getElementById("composer");
    if (!box || !C.composer) return;
    const K = C.composer, out = document.getElementById("message");
    const pets = Object.keys(K.pets);
    box.querySelector("[data-pets]").innerHTML = pets.map((p, i) => `<label class="chip"><input type="radio" name="pet" value="${p}" ${i ? "" : "checked"}><span>${K.pets[p].label}</span></label>`).join("");
    // The next seven open days, from the business hours.
    const now = local(), days = [];
    for (let i = 0; days.length < 6 && i < 14; i++) {
      const d = new Date(`${now.ymd}T12:00:00Z`); d.setUTCDate(d.getUTCDate() + i);
      const dow = d.getUTCDay(), h = hours(dow);
      if (!h || closedOn(d.toISOString().slice(0, 10))) continue;
      if (i === 0 && now.mins > h[1] - 90) continue;
      days.push({ i, dow, label: i === 0 ? "Today" : i === 1 ? "Tomorrow" : `${SHORT[dow]} ${d.getUTCDate()}`, word: i === 0 ? "today" : i === 1 ? "tomorrow" : `on ${DAYS[dow]}` });
    }
    box.querySelector("[data-days]").innerHTML = days.map((d, n) => `<label class="chip"><input type="radio" name="day" value="${n}" ${n === (days.length > 1 ? 1 : 0) ? "checked" : ""}><span>${d.label}</span></label>`).join("");
    const val = (n) => (box.querySelector(`input[name="${n}"]:checked`) || {}).value;
    function drawOptions() {
      const P = K.pets[val("pet")], keepSize = val("size"), keepSvc = [...box.querySelectorAll('input[name="svc"]:checked')].map((i) => i.value);
      const sizeStep = box.querySelector("[data-sizes]");
      sizeStep.closest(".step").hidden = !P.sizes;
      if (P.sizes) sizeStep.innerHTML = P.sizes.map((z, i) => `<label class="size-opt"><input type="radio" name="size" value="${z.id}" ${(keepSize ? z.id === keepSize : i === 0) ? "checked" : ""}><span><strong>${z.label}</strong><small>${z.note}</small></span></label>`).join("");
      box.querySelector("[data-services]").innerHTML = P.services.map((v, i) => `<label class="chip"><input type="checkbox" name="svc" value="${v.id}" ${(keepSvc.length ? keepSvc.includes(v.id) : i === 0) ? "checked" : ""}><span>${v.label}</span></label>`).join("");
      draw();
    }
    const list = (a) => a.length < 2 ? a.join("") : `${a.slice(0, -1).join(", ")} and ${a[a.length - 1]}`;
    function draw() {
      const P = K.pets[val("pet")], size = P.sizes ? P.sizes.find((z) => z.id === val("size")) : null;
      const svcs = [...box.querySelectorAll('input[name="svc"]:checked')].map((i) => P.services.find((v) => v.id === i.value).phrase);
      const day = days[+val("day")] || null, time = val("time") || "morning";
      const name = box.querySelector("#pet-name").value.trim(), shy = box.querySelector("#shy") && box.querySelector("#shy").checked;
      const who = `my ${size ? size.word + " " : ""}${P.noun}${name ? `, ${name},` : ""}`;
      let text = `${K.greeting} I'd like ${svcs.length ? list(svcs) : "a groom"} for ${who} ${day ? day.word + " " : ""}${(K.times || { morning: "in the morning", afternoon: "in the afternoon" })[time]}.`;
      if (shy) text += ` ${name || "My " + P.noun} can be nervous.`;
      text += " Do you have a spot?";
      out.querySelector(".bubble").textContent = text;
      const sep = /iPhone|iPad|Macintosh/.test(navigator.userAgent) ? "&" : "?";
      out.querySelector("[data-sms]").href = `sms:${C.phone}${sep}body=${encodeURIComponent(text)}`;
    }
    box.addEventListener("change", (e) => { if (e.target.name === "pet") drawOptions(); else draw(); });
    box.addEventListener("input", draw);
    out.querySelector("[data-copy]").addEventListener("click", async (e) => {
      try { await navigator.clipboard.writeText(out.querySelector(".bubble").textContent); e.target.textContent = "Copied"; setTimeout(() => (e.target.textContent = "Copy message"), 1800); } catch (err) {}
    });
    drawOptions();
  }

  function initMap() {
    const box = document.getElementById("map");
    if (!box || C.lat == null) return;
    if (!window.L) { box.innerHTML = `<p class="map-fallback">${C.address}</p>`; return; }
    const map = L.map(box, { scrollWheelZoom: false }).setView([C.lat, C.lng], 15);
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map);
    L.marker([C.lat, C.lng], { keyboard: false, icon: L.divIcon({ className: "pin", html: `<span class="pin-dot"></span><span class="pin-label">${C.pin}</span>`, iconSize: [0, 0] }) }).addTo(map);
  }

  renderStatus(); renderHours(); finder(); composer();
  setInterval(() => { renderStatus(); renderHours(); }, 60000);
  if (document.readyState === "complete") initMap(); else window.addEventListener("load", initMap);

  const bar = document.getElementById("thumb-bar"), hide = document.getElementById(C.thumbHideOn || "prices");
  if ("IntersectionObserver" in window && bar && hide) new IntersectionObserver(([e]) => bar.classList.toggle("away", e.isIntersecting), { threshold: 0.15 }).observe(hide);
})();
