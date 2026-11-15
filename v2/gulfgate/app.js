// Gulfgate preview: language, live status (Houston time), visit planner, hours, map.
(() => {
  const TZ = "America/Chicago";
  const PHONE = "+17136435723";
  const EMAIL = "gulfgateanimalhospital@yahoo.com";
  const LAT = 29.701259, LNG = -95.2988481;

  // Minutes from midnight. appt = last appointment start, walkin = last walk-in.
  const WEEKDAY = { open: 480, close: 1080, appt: 960, walkin: 1020 };
  const SATURDAY = { open: 480, close: 840, appt: null, walkin: 780, urgentOnly: true };
  // From the clinic's holiday schedule (gulfgateanimalhospital.com/hourslocation).
  const HOLIDAYS = {
    "2026-11-26": { en: "Thanksgiving", es: "Día de Acción de Gracias" },
    "2026-12-24": { en: "Christmas", es: "Navidad" },
    "2026-12-25": { en: "Christmas", es: "Navidad" },
    "2026-12-26": { en: "Christmas", es: "Navidad" },
    "2027-01-01": { en: "New Year's Day", es: "Año Nuevo" },
  };
  const SHORT = { "2026-12-31": { open: 480, close: 840, appt: null, walkin: 780 } };

  const DAYS = {
    en: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
    es: ["domingo", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado"],
  };
  let lang = "en";

  const fmt = (m) => {
    const h = Math.floor(m / 60), mm = m % 60, h12 = ((h + 11) % 12) + 1;
    const t = mm ? `${h12}:${String(mm).padStart(2, "0")}` : `${h12}`;
    return lang === "es" ? `${t} ${h < 12 ? "a. m." : "p. m."}` : `${t} ${h < 12 ? "am" : "pm"}`;
  };

  function houston(date = new Date()) {
    const parts = Object.fromEntries(new Intl.DateTimeFormat("en-US", {
      timeZone: TZ, year: "numeric", month: "2-digit", day: "2-digit", weekday: "short", hour: "2-digit", minute: "2-digit", hour12: false,
    }).formatToParts(date).map((p) => [p.type, p.value]));
    const dow = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].indexOf(parts.weekday);
    return { ymd: `${parts.year}-${parts.month}-${parts.day}`, dow, mins: (+parts.hour % 24) * 60 + +parts.minute };
  }
  function dayPlan(ymd, dow) {
    if (HOLIDAYS[ymd]) return null;
    if (SHORT[ymd]) return SHORT[ymd];
    if (dow >= 1 && dow <= 5) return WEEKDAY;
    if (dow === 6) return SATURDAY;
    return null;
  }
  function addDays(ymd, n) {
    const d = new Date(`${ymd}T12:00:00Z`); d.setUTCDate(d.getUTCDate() + n);
    return { ymd: d.toISOString().slice(0, 10), dow: d.getUTCDay() };
  }
  function nextOpening(now) {
    for (let i = 1; i <= 8; i++) {
      const d = addDays(now.ymd, i), p = dayPlan(d.ymd, d.dow);
      if (p) return { i, dow: d.dow, at: p.open };
    }
    return null;
  }
  const dayWord = (n) => n.i === 1 ? (lang === "es" ? "mañana" : "tomorrow") : (lang === "es" ? `el ${DAYS.es[n.dow]}` : DAYS.en[n.dow]);

  // One state object drives the hero status and the planner.
  function state() {
    const now = houston(), plan = dayPlan(now.ymd, now.dow);
    const s = { now, plan, holiday: HOLIDAYS[now.ymd] };
    s.open = !!plan && now.mins >= plan.open && now.mins < plan.close;
    s.beforeOpen = !!plan && now.mins < plan.open;
    s.walkinOpen = !!plan && now.mins < plan.walkin;
    s.apptToday = !!plan && plan.appt !== null && now.mins < plan.appt;
    s.next = nextOpening(now);
    return s;
  }

  const T = {
    en: {
      openUntil: (t) => `Open now until ${t}`,
      opensToday: (t) => `Opens today at ${t}`,
      closedHoliday: (h) => `Closed today for ${h}`,
      closed: "Closed now",
      opens: (d, t) => `Opens ${d} at ${t}`,
      walkinsUntil: (t) => `Walk-ins until ${t}`,
      apptsUntil: (t) => `appointments until ${t}`,
      walkinsDone: (t) => `Today's last walk-in was at ${t}. The pharmacy is open.`,
      saturday: (t) => `Saturday: urgent care only, walk-ins until ${t}`,
    },
    es: {
      openUntil: (t) => `Abierto ahora hasta las ${t}`,
      opensToday: (t) => `Abre hoy a las ${t}`,
      closedHoliday: (h) => `Cerrado hoy por ${h}`,
      closed: "Cerrado ahora",
      opens: (d, t) => `Abre ${d} a las ${t}`,
      walkinsUntil: (t) => `Sin cita hasta las ${t}`,
      apptsUntil: (t) => `citas hasta las ${t}`,
      walkinsDone: (t) => `El último paciente sin cita fue a las ${t}. La farmacia sigue abierta.`,
      saturday: (t) => `Sábado: solo atención urgente, sin cita hasta las ${t}`,
    },
  };

  function renderStatus(s) {
    const t = T[lang], el = document.getElementById("status");
    let main, sub = "", tone = "closed";
    if (s.open) {
      tone = s.walkinOpen ? "open" : "late";
      main = t.openUntil(fmt(s.plan.close));
      if (s.plan.urgentOnly) sub = s.walkinOpen ? t.saturday(fmt(s.plan.walkin)) : t.walkinsDone(fmt(s.plan.walkin));
      else if (!s.walkinOpen) sub = t.walkinsDone(fmt(s.plan.walkin));
      else sub = t.walkinsUntil(fmt(s.plan.walkin)) + (s.apptToday ? `, ${t.apptsUntil(fmt(s.plan.appt))}` : "");
    } else if (s.beforeOpen) {
      tone = "soon"; main = t.opensToday(fmt(s.plan.open));
      sub = s.plan.urgentOnly ? t.saturday(fmt(s.plan.walkin)) : t.walkinsUntil(fmt(s.plan.walkin)) + `, ${t.apptsUntil(fmt(s.plan.appt))}`;
    } else {
      main = s.holiday ? t.closedHoliday(s.holiday[lang]) : t.closed;
      if (s.next) sub = t.opens(dayWord(s.next), fmt(s.next.at));
    }
    el.dataset.tone = tone;
    document.getElementById("status-main").textContent = main;
    document.getElementById("status-sub").textContent = sub;
  }

  // Visit planner. Every line is from the clinic's own site; the live line depends on the clock.
  function liveLine(s, kind) {
    const es = lang === "es";
    if (kind === "walkin") {
      if (s.open && s.walkinOpen) return es ? `Hoy atendemos sin cita hasta las ${fmt(s.plan.walkin)}.` : `Walk-ins today until ${fmt(s.plan.walkin)}.`;
      if (s.beforeOpen) return es ? `Hoy abrimos a las ${fmt(s.plan.open)}; sin cita hasta las ${fmt(s.plan.walkin)}.` : `We open today at ${fmt(s.plan.open)}; walk-ins until ${fmt(s.plan.walkin)}.`;
      if (s.next) return es ? `Hoy ya no recibimos pacientes sin cita. Abrimos ${dayWord(s.next)} a las ${fmt(s.next.at)}.` : `Walk-ins are closed for today. We open ${dayWord(s.next)} at ${fmt(s.next.at)}.`;
    }
    if (kind === "appt") {
      if (s.apptToday) return es ? `Aún hay horario de citas hoy, hasta las ${fmt(s.plan.appt)}.` : `Appointment hours are still open today, until ${fmt(s.plan.appt)}.`;
      return es ? "Las citas son de lunes a viernes, de 8 a. m. a 4 p. m." : "Appointments are Monday to Friday, 8 am to 4 pm.";
    }
    if (kind === "pharmacy") {
      if (s.open) return es ? `La farmacia está abierta hasta las ${fmt(s.plan.close)}.` : `The pharmacy is open until ${fmt(s.plan.close)}.`;
      if (s.next) return es ? `La farmacia abre ${s.beforeOpen ? "hoy" : dayWord(s.next)} a las ${fmt(s.beforeOpen ? s.plan.open : s.next.at)}.` : `The pharmacy opens ${s.beforeOpen ? "today" : dayWord(s.next)} at ${fmt(s.beforeOpen ? s.plan.open : s.next.at)}.`;
    }
    return "";
  }

  const REASONS = {
    sick: (s) => lang === "es" ? {
      title: "Venga sin cita, o llame para una cita hoy",
      fee: "$51", feeNote: "examen sin cita (atención urgente)", alt: "$41 con cita",
      lines: [liveLine(s, "walkin"), liveLine(s, "appt"), "Con cita espera menos. Los sábados solo hay atención urgente, por orden de llegada."],
      sms: "Hola, mi mascota está enferma. ¿Pueden verla hoy?",
    } : {
      title: "Walk in, or call for an appointment today",
      fee: "$51", feeNote: "walk-in exam (urgent care)", alt: "$41 with an appointment",
      lines: [liveLine(s, "walkin"), liveLine(s, "appt"), "Booking ahead means a shorter wait. Saturday is urgent care only, in order of arrival."],
      sms: "Hi, my pet is sick. Can you see us today?",
    },
    checkup: (s) => lang === "es" ? {
      title: "Reserve una cita",
      fee: "$41", feeNote: "examen con cita",
      lines: [liveLine(s, "appt"), "Traiga el historial médico y de vacunas.", "Perros con correa, gatos en transportadora."],
      sms: "Hola, quisiera una cita para un chequeo y vacunas.",
    } : {
      title: "Book an appointment",
      fee: "$41", feeNote: "scheduled exam",
      lines: [liveLine(s, "appt"), "Bring your pet's medical and vaccination history.", "Dogs on a leash, cats in a carrier."],
      sms: "Hi, I'd like to book a checkup and vaccines.",
    },
    followup: (s) => lang === "es" ? {
      title: "Reserve su revisión de seguimiento",
      fee: "$35", feeNote: "revisión con cita", alt: "$51 sin cita",
      lines: [liveLine(s, "appt"), "Un seguimiento sin cita se considera atención urgente."],
      sms: "Hola, quisiera una cita de seguimiento.",
    } : {
      title: "Book your progress exam",
      fee: "$35", feeNote: "scheduled recheck", alt: "$51 without an appointment",
      lines: [liveLine(s, "appt"), "A follow-up without an appointment counts as urgent care."],
      sms: "Hi, I'd like to book a follow-up visit.",
    },
    refill: (s) => lang === "es" ? {
      title: "Llame o escriba antes, y pase a recoger",
      fee: null,
      lines: ["Tendremos su receta, preventivos o comida especial listos para recoger rápido.", liveLine(s, "pharmacy")],
      sms: "Hola, quisiera pedir una receta para recoger. Nombre de la mascota: ",
    } : {
      title: "Call or text ahead, then pick it up",
      fee: null,
      lines: ["We'll have your refill, preventatives or special food ready for a quick pickup.", liveLine(s, "pharmacy")],
      sms: "Hi, I'd like to order a refill for pickup. Pet's name: ",
    },
    emergency: () => lang === "es" ? {
      title: "Llame a una clínica de emergencias ahora",
      fee: null, urgent: true,
      lines: ["No somos un hospital de 24 horas. En una emergencia, llame a la clínica de emergencias más cercana."],
    } : {
      title: "Call an emergency hospital now",
      fee: null, urgent: true,
      lines: ["We are not a 24-hour hospital. In an emergency, call your closest animal emergency clinic."],
    },
  };

  function smsHref(body) {
    const sep = /iPhone|iPad|Macintosh/.test(navigator.userAgent) ? "&" : "?";
    return `sms:${PHONE}${sep}body=${encodeURIComponent(body)}`;
  }

  function renderTicket(s) {
    const reason = document.querySelector('input[name="reason"]:checked').value;
    const r = REASONS[reason](s), es = lang === "es";
    const el = document.getElementById("ticket");
    el.classList.toggle("ticket-urgent", !!r.urgent);
    const fee = r.fee ? `<div class="ticket-fee"><span class="fee-big">${r.fee}</span><span>${r.feeNote}${r.alt ? `<br><small>${r.alt}</small>` : ""}</span></div>` : "";
    const lines = r.lines.filter(Boolean).map((l) => `<li>${l}</li>`).join("");
    let actions;
    if (r.urgent) {
      actions = `<a class="btn btn-solid" href="#emergency">${es ? "Ver números de emergencia" : "See emergency numbers"}</a>`;
    } else {
      actions = `<a class="btn btn-solid" href="tel:${PHONE}">${es ? "Llamar" : "Call"} 713-643-5723</a>
        <a class="btn btn-line" href="${smsHref(r.sms)}">${es ? "Enviar texto" : "Send a text"}</a>`;
    }
    el.innerHTML = `<p class="ticket-label">${es ? "Su mejor opción" : "Your best option"}</p>
      <h3>${r.title}</h3>${fee}<ul class="ticket-lines">${lines}</ul><div class="ticket-actions">${actions}</div>`;
  }

  function renderHours(s) {
    const rows = [
      { days: [1, 2, 3, 4, 5], en: "Monday to Friday", es: "Lunes a viernes", h: [480, 1080] },
      { days: [6], en: "Saturday", es: "Sábado", h: [480, 840], note: { en: "urgent care only", es: "solo urgencias" } },
      { days: [0], en: "Sunday", es: "Domingo", h: null },
    ];
    const today = s.holiday ? -1 : s.now.dow;
    document.getElementById("hours").innerHTML = rows.map((r) => `<tr class="${r.days.includes(today) ? "today" : ""}">
      <th scope="row">${r[lang]}${r.days.includes(today) ? ` <span class="today-tag">${lang === "es" ? "hoy" : "today"}</span>` : ""}</th>
      <td>${r.h ? `${fmt(r.h[0])} – ${fmt(r.h[1])}${r.note ? `<small>${r.note[lang]}</small>` : ""}` : (lang === "es" ? "Cerrado" : "Closed")}</td></tr>`).join("");
  }

  function renderAll() { const s = state(); renderStatus(s); renderTicket(s); renderHours(s); }

  function setLang(l) {
    lang = l === "es" ? "es" : "en";
    document.documentElement.lang = lang;
    document.documentElement.dataset.lang = lang;
    document.querySelectorAll("[data-set-lang]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.setLang === lang)));
    try { localStorage.setItem("gulfgate-lang", lang); } catch (e) {}
    renderAll();
  }

  let saved = null;
  try { saved = localStorage.getItem("gulfgate-lang"); } catch (e) {}
  document.querySelectorAll("[data-set-lang]").forEach((b) => b.addEventListener("click", () => setLang(b.dataset.setLang)));
  document.querySelectorAll('input[name="reason"]').forEach((i) => i.addEventListener("change", () => renderTicket(state())));
  setLang(saved || ((navigator.language || "").toLowerCase().startsWith("es") ? "es" : "en"));
  setInterval(renderAll, 60000);

  // Map: Leaflet with OpenStreetMap tiles, muted with CSS. A live site would use a keyed tile provider. Falls back to the address if it can't load.
  function initMap() {
    const box = document.getElementById("map");
    if (!window.L || !box) { if (box) box.innerHTML = '<p class="map-fallback">216 Winkler Dr, Houston, TX 77087</p>'; return; }
    const map = L.map(box, { scrollWheelZoom: false, zoomControl: true, attributionControl: true }).setView([LAT, LNG], 15);
    L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    }).addTo(map);
    const icon = L.divIcon({ className: "pin", html: '<span class="pin-dot"></span><span class="pin-label">Gulfgate</span>', iconSize: [0, 0] });
    L.marker([LAT, LNG], { icon, keyboard: false }).addTo(map);
  }
  if (document.readyState === "complete") initMap(); else window.addEventListener("load", initMap);

  // Hide the thumb bar while the planner is on screen.
  const bar = document.getElementById("thumb-bar"), visit = document.getElementById("visit");
  if ("IntersectionObserver" in window && bar && visit) {
    new IntersectionObserver(([e]) => bar.classList.toggle("away", e.isIntersecting), { threshold: 0.15 }).observe(visit);
  }
})();
