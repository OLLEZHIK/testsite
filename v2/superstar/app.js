// Super Star preview: menu, open-now, area check, booking message, bundles, hours.
(() => {
  const C = JSON.parse(document.getElementById("site-config").textContent);
  const DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  const SHORT = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const fmt = (m) => { const h = Math.floor(m / 60), mm = m % 60; return `${((h + 11) % 12) + 1}${mm ? ":" + String(mm).padStart(2, "0") : ""} ${h < 12 ? "am" : "pm"}`; };
  const span = (s) => s ? s.split("-").map((t) => { const [h, m] = t.split(":").map(Number); return h * 60 + m; }) : null;
  function now() {
    const p = Object.fromEntries(new Intl.DateTimeFormat("en-US", { timeZone: C.tz, weekday: "short", hour: "2-digit", minute: "2-digit", hour12: false, year: "numeric", month: "2-digit", day: "2-digit" }).formatToParts(new Date()).map((x) => [x.type, x.value]));
    return { dow: SHORT.indexOf(p.weekday), mins: (+p.hour % 24) * 60 + +p.minute, d: +p.day };
  }

  // Mobile menu
  const mb = document.querySelector(".menu-btn"), mm = document.getElementById("mobile-menu");
  if (mb && mm) mb.addEventListener("click", () => { const o = mm.hidden; mm.hidden = !o; mb.setAttribute("aria-expanded", String(o)); });

  // Open now
  document.querySelectorAll("#status").forEach((el) => {
    const n = now(), h = span(C.hours[n.dow]); let text, tone = "closed";
    if (h && n.mins >= h[0] && n.mins < h[1]) { text = `Booking today until ${fmt(h[1])}`; tone = "open"; }
    else if (h && n.mins < h[0]) { text = `Out on the road from ${fmt(h[0])} today`; tone = "soon"; }
    else { const t = (n.dow + 1) % 7, th = span(C.hours[t]); text = `Closed for today. Back tomorrow at ${fmt(th[0])}`; }
    el.dataset.tone = tone; el.querySelector(".status-text").textContent = text;
  });

  // Hours table
  const ht = document.getElementById("hours");
  if (ht) { const t = now().dow; ht.innerHTML = [1, 2, 3, 4, 5, 6, 0].map((d) => { const h = span(C.hours[d]); return `<tr class="${d === t ? "today" : ""}"><th scope="row">${DAYS[d]}</th><td>${fmt(h[0])} – ${fmt(h[1])}</td></tr>`; }).join(""); }

  // Area check
  const norm = (s) => s.toLowerCase().replace(/[^a-z]/g, "");
  const root = location.pathname.replace(/(areas\/[^/]+\/|areas\/|services\/|bundles\/|book\/)$/, "");
  document.querySelectorAll("[data-areacheck]").forEach((box) => {
    const input = box.querySelector("input"), out = box.querySelector(".area-result"), dl = box.querySelector("datalist");
    if (dl && !dl.children.length) dl.innerHTML = C.areas.map(([, n]) => `<option value="${n}">`).join("");
    const check = () => {
      const q = norm(input.value); if (!q) { out.textContent = ""; out.className = "area-result"; return; }
      const hit = C.areas.find(([s, n]) => norm(n) === q || norm(n).startsWith(q) || q.startsWith(norm(n)));
      if (hit) { out.className = "area-result yes"; out.innerHTML = `Yes, we groom in ${hit[1]}. <a href="${root}areas/${hit[0]}/#book">Book in ${hit[1]}</a>`; }
      else { out.className = "area-result"; out.innerHTML = `${input.value} isn't on our list yet. <a href="tel:${C.phone}">Call us</a> and ask: we may still come.`; }
    };
    box.querySelector("button").addEventListener("click", check);
    input.addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); check(); } });
    input.addEventListener("change", check);
  });

  // Booking message
  const SVC = { dog: [["Complete Grooming", "a Complete Grooming"], ["Wash", "a Wash"], ["Super Star Complete", "a Super Star Complete"], ["Super Star Wash", "a Super Star Wash"]],
    cat: [["Cat Complete", "a Cat Complete"], ["Cat Wash", "a Cat Wash"]] };
  document.querySelectorAll("[data-composer]").forEach((box) => {
    const f = box.querySelector("form"), bubble = box.querySelector("[data-bubble]");
    const days = box.querySelector("[data-days]"), n = now();
    const opts = [];
    for (let i = 0; i < 7; i++) { const dow = (n.dow + i) % 7; const label = i === 0 ? "Today" : i === 1 ? "Tomorrow" : DAYS[dow]; const word = i === 0 ? "today" : i === 1 ? "tomorrow" : `on ${DAYS[dow]}`; opts.push(`<option value="${word}"${i === 1 ? " selected" : ""}>${label}</option>`); }
    days.innerHTML = opts.join("");
    const val = (name) => (f.querySelector(`[name="${name}"]:checked`) || f.querySelector(`[name="${name}"]`) || {}).value;
    function drawServices() {
      const pet = val("pet"), wrap = box.querySelector("[data-services]"), keep = val("svc");
      wrap.innerHTML = SVC[pet].map(([l, p], i) => `<label class="chip"><input type="radio" name="svc" value="${p}" ${(keep ? keep === p : i === 0) ? "checked" : ""}><span>${l}</span></label>`).join("");
      if (!wrap.querySelector(":checked")) wrap.querySelector("input").checked = true;
      box.querySelector("[data-dog-only]").hidden = pet !== "dog";
    }
    function draw() {
      const pet = val("pet"), size = val("size"), svc = val("svc"), name = f.elements.name.value.trim();
      const area = f.elements.area.selectedOptions[0].text, day = f.elements.day.value, time = f.elements.time.value;
      const extras = [...f.querySelectorAll('[name="extra"]:checked')].map((x) => x.value);
      const who = pet === "dog" ? `my ${size} dog` : "my cat";
      let t = `Hi Super Star! I'd like ${svc} for ${who}${name ? `, ${name},` : ""}${extras.length ? ` with ${extras.join(" and ")}` : ""}, ${day} in the ${time === "midday" ? "middle of the day" : time}. We're in ${area}. Do you have a spot?`;
      bubble.textContent = t;
      const sep = /iPhone|iPad|Macintosh/.test(navigator.userAgent) ? "&" : "?";
      box.querySelector("[data-sms]").href = `sms:${C.phone}${sep}body=${encodeURIComponent(t)}`;
      box.querySelector("[data-mail]").href = `mailto:info@superstargrooming.com?subject=${encodeURIComponent("Grooming appointment")}&body=${encodeURIComponent(t)}`;
    }
    f.addEventListener("change", (e) => { if (e.target.name === "pet") drawServices(); draw(); });
    f.addEventListener("input", draw);
    box.querySelector("[data-copy]").addEventListener("click", async (e) => { try { await navigator.clipboard.writeText(bubble.textContent); e.target.textContent = "Copied"; setTimeout(() => (e.target.textContent = "Copy"), 1500); } catch (err) {} });
    drawServices(); draw();
  });

  // Bundles
  const bw = document.querySelector("[data-bundles]"), bo = document.querySelector("[data-bundle-out]");
  if (bw && bo) {
    const show = (b) => {
      bw.querySelectorAll(".bundle").forEach((x) => x.classList.toggle("on", x === b));
      const pay = +b.dataset.pay, get = +b.dataset.get, pct = Math.round((1 - pay / get) * 100), name = b.querySelector(".b-name").textContent;
      bo.innerHTML = `<strong>${name}:</strong> pay $${pay.toFixed(2)} now and get $${get} of grooming for one pet. That's ${pct}% off every groom until it's used up. <a href="tel:${C.phone}">Call to buy a bundle</a>.`;
    };
    bw.addEventListener("click", (e) => { const b = e.target.closest(".bundle"); if (b) show(b); });
    show(bw.querySelector(".bundle.on"));
  }

  // Pause the video for people who prefer less motion
  const v = document.querySelector(".hero-video");
  if (v && window.matchMedia("(prefers-reduced-motion: reduce)").matches) v.pause();
})();
