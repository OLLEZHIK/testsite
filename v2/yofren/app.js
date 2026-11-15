// Yofren preview: language switch, visit composer, hours and "open now".
(() => {
  const PHONE = "+17863200218";
  const TZ = "America/New_York";
  // 0 = Sunday. Minutes from midnight.
  const HOURS = { 0: [540, 1020], 1: [480, 1140], 2: [480, 1140], 3: [480, 1140], 4: [480, 1140], 5: [480, 1140], 6: [480, 1140] };

  const T = {
    en: {
      previewText: "built for Yofren Master Pet Grooming by Pawenn. This site is not live yet.",
      previewLink: "See the offer",
      navPlan: "Book a visit", navReviews: "Reviews", navServices: "Services", navHours: "Hours",
      heroLine1: "The grooming salon", heroLine2: "that parks at your door.",
      heroSub: "Baths, haircuts, ears and teeth for dogs and cats, done in our van right outside your home. No car ride, no crate, no waiting room.",
      heroCta: "Plan a visit", heroCall: "Call us", heroRating: "4.8 on Google from 230 reviews",
      openNow: (t) => `Open now, until ${t}`, closedNow: (d, t) => `Closed now. Opens ${d} at ${t}`,
      today: "today", tomorrow: "tomorrow",
      planTitle: "Tell us about your pet. We'll write the text for you.",
      planLead: "Pick what you need and send it to us as a text. We reply with a time and a price for your pet.",
      qPet: "Who's getting groomed?", petDog: "Dog", petCat: "Cat",
      qSize: "How big?", sizeS: "Small", sizeSNote: "under 20 lb", sizeM: "Medium", sizeMNote: "20 to 50 lb", sizeL: "Large", sizeLNote: "over 50 lb",
      qServices: "What does your pet need?", svcBath: "Bath and blow-dry", svcCut: "Haircut", svcNails: "Nails", svcEars: "Ear cleaning", svcTeeth: "Teeth brushing",
      qDay: "When works for you?", timeAm: "Morning", timePm: "Afternoon",
      qName: "Pet's name", phName: "Luna", qArea: "Your neighborhood", phArea: "Kendall, Doral, Brickell…",
      previewTitle: "Your message", toLabel: "To",
      sendSms: "Send as a text", copyMsg: "Copy message", copied: "Copied. Paste it into a text to (786) 320-0218.",
      planNote: "Opens your messages app with the text ready to send to (786) 320-0218.",
      reviewsTitle: "What 106 Google reviews from the past year keep saying",
      t1Title: "Miguel, Carlos, Victor and Pablo show up on time",
      t1Text: "Clients name the groomers again and again, for being punctual, friendly and careful with their pets.",
      t2Title: "Nervous pets stay calm",
      t2Text: "Owners of puppies, anxious dogs and cats say their pets stay relaxed, because the groom happens at home, with no trip and no crate.",
      t3Title: "Clean coats that smell great",
      t3Text: "Reviews mention spotless coats, neat breed haircuts, a shampoo scent that lasts and thorough teeth cleaning.",
      allReviews: "Read all reviews on Google",
      servicesTitle: "A full salon, inside the van",
      servicesLead: "Our grooming vans are self-contained, so the whole groom happens right outside your home.",
      s1: "Bath and blow-dry", s1t: "Warm bath, gentle shampoo, a full dry and brush-out.",
      s2: "Haircuts and breed styling", s2t: "From a tidy trim to a full breed cut, done the way you ask.",
      s3: "Nails, ears and teeth", s3t: "Nail trims, ear cleaning and teeth brushing, on their own or with any groom.",
      s4: "Cats too", s4t: "Quiet, patient brushing and bathing for cats, without a trip to a salon.",
      priceNote: "Prices depend on your pet's size and coat. Send us a text and we'll quote your exact price.",
      hoursTitle: "When we're on the road", contactTitle: "Get in touch",
      cPhone: "Call or text", cEmail: "Email", cArea: "Where", cAreaText: "We come to homes across Miami", cSocial: "Follow",
      faqTitle: "Questions people ask",
      f1q: "Do you really groom at my home?", f1a: "Yes. Our self-contained van parks outside your home and the whole groom happens inside it.",
      f2q: "Do you groom cats?", f2a: "Yes, we groom dogs and cats. Tell us about your cat when you text, so we can plan enough time.",
      f3q: "How much does a groom cost?", f3a: "It depends on size, coat and services. Text us your pet's breed and what you need, and we'll send your price before the visit.",
      f4q: "Which days do you work?", f4a: "Monday to Saturday from 8 am to 7 pm, and Sunday from 9 am to 5 pm.",
      madeBy: "Website by",
      days: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
      daysShort: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
      closed: "Closed",
      msg: (m) => {
        const who = m.pet === "cat" ? "my cat" : `my ${m.size} dog`;
        const name = m.name ? `, ${m.name},` : "";
        const svc = m.services.length ? listEn(m.services.map((s) => SVC.en[s])) : "a groom";
        const where = m.area ? ` We're in ${m.area}.` : "";
        const part = m.time === "morning" ? "morning" : "afternoon";
        const when = m.dayIndex === 0 ? `this ${part}` : m.dayIndex === 1 ? `tomorrow ${part}` : `on ${m.day} ${part}`;
        return `Hi Yofren! I'd like ${svc} for ${who}${name} ${when}.${where} Do you have a spot?`;
      },
    },
    es: {
      previewText: "hecha para Yofren Master Pet Grooming por Pawenn. Este sitio aún no está publicado.",
      previewLink: "Ver la oferta",
      navPlan: "Reservar", navReviews: "Reseñas", navServices: "Servicios", navHours: "Horario",
      heroLine1: "El salón de grooming", heroLine2: "que llega a tu puerta.",
      heroSub: "Baño, corte, oídos y dientes para perros y gatos, en nuestra camioneta frente a tu casa. Sin viajes en carro, sin jaulas, sin sala de espera.",
      heroCta: "Planea una visita", heroCall: "Llámanos", heroRating: "4.8 en Google con 230 reseñas",
      openNow: (t) => `Abierto ahora, hasta las ${t}`, closedNow: (d, t) => `Cerrado ahora. Abre ${d} a las ${t}`,
      today: "hoy", tomorrow: "mañana",
      planTitle: "Cuéntanos de tu mascota. Nosotros escribimos el mensaje.",
      planLead: "Elige lo que necesitas y envíanoslo por mensaje de texto. Te respondemos con un horario y el precio para tu mascota.",
      qPet: "¿A quién vamos a arreglar?", petDog: "Perro", petCat: "Gato",
      qSize: "¿De qué tamaño?", sizeS: "Pequeño", sizeSNote: "menos de 20 lb", sizeM: "Mediano", sizeMNote: "de 20 a 50 lb", sizeL: "Grande", sizeLNote: "más de 50 lb",
      qServices: "¿Qué necesita tu mascota?", svcBath: "Baño y secado", svcCut: "Corte", svcNails: "Uñas", svcEars: "Limpieza de oídos", svcTeeth: "Cepillado de dientes",
      qDay: "¿Qué día te conviene?", timeAm: "Mañana", timePm: "Tarde",
      qName: "Nombre de tu mascota", phName: "Luna", qArea: "Tu barrio", phArea: "Kendall, Doral, Brickell…",
      previewTitle: "Tu mensaje", toLabel: "Para",
      sendSms: "Enviar por mensaje", copyMsg: "Copiar mensaje", copied: "Copiado. Pégalo en un mensaje al (786) 320-0218.",
      planNote: "Abre tu app de mensajes con el texto listo para enviar al (786) 320-0218.",
      reviewsTitle: "Lo que repiten 106 reseñas de Google del último año",
      t1Title: "Miguel, Carlos, Victor y Pablo llegan a tiempo",
      t1Text: "Los clientes nombran a los groomers una y otra vez: puntuales, amables y cuidadosos con sus mascotas.",
      t2Title: "Las mascotas nerviosas se quedan tranquilas",
      t2Text: "Dueños de cachorros, perros ansiosos y gatos cuentan que sus mascotas están relajadas, porque el grooming es en casa, sin viajes ni jaulas.",
      t3Title: "Pelaje limpio y con buen olor",
      t3Text: "Las reseñas hablan de pelaje impecable, cortes de raza prolijos, un olor a champú que dura y una buena limpieza de dientes.",
      allReviews: "Leer todas las reseñas en Google",
      servicesTitle: "Un salón completo dentro de la camioneta",
      servicesLead: "Nuestras camionetas de grooming son autónomas: todo el servicio se hace frente a tu casa.",
      s1: "Baño y secado", s1t: "Baño tibio, champú suave, secado completo y cepillado.",
      s2: "Cortes y estilo de raza", s2t: "Desde un retoque hasta un corte de raza completo, como tú lo pidas.",
      s3: "Uñas, oídos y dientes", s3t: "Corte de uñas, limpieza de oídos y cepillado de dientes, solos o con cualquier servicio.",
      s4: "También gatos", s4t: "Cepillado y baño con calma y paciencia, sin llevar a tu gato a un salón.",
      priceNote: "El precio depende del tamaño y el pelaje. Escríbenos y te decimos el precio exacto.",
      hoursTitle: "Cuándo estamos en camino", contactTitle: "Contacto",
      cPhone: "Llamada o mensaje", cEmail: "Correo", cArea: "Dónde", cAreaText: "Vamos a casas en todo Miami", cSocial: "Síguenos",
      faqTitle: "Preguntas frecuentes",
      f1q: "¿De verdad hacen el grooming en mi casa?", f1a: "Sí. Nuestra camioneta autónoma se estaciona frente a tu casa y todo el servicio se hace adentro.",
      f2q: "¿Arreglan gatos?", f2a: "Sí, atendemos perros y gatos. Cuéntanos de tu gato en el mensaje para reservar el tiempo necesario.",
      f3q: "¿Cuánto cuesta?", f3a: "Depende del tamaño, el pelaje y los servicios. Escríbenos la raza y lo que necesitas, y te enviamos el precio antes de la visita.",
      f4q: "¿Qué días trabajan?", f4a: "De lunes a sábado de 8 am a 7 pm, y domingos de 9 am a 5 pm.",
      madeBy: "Sitio web por",
      days: ["domingo", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado"],
      daysShort: ["dom", "lun", "mar", "mié", "jue", "vie", "sáb"],
      closed: "Cerrado",
      msg: (m) => {
        const who = m.pet === "cat" ? "mi gato" : `mi perro ${({ small: "pequeño", medium: "mediano", large: "grande" })[m.size]}`;
        const name = m.name ? `, ${m.name},` : "";
        const svc = m.services.length ? listEs(m.services.map((s) => SVC.es[s])) : "un grooming";
        const where = m.area ? ` Estamos en ${m.area}.` : "";
        const part = m.time === "morning" ? "por la mañana" : "por la tarde";
        const when = m.dayIndex === 0 ? `hoy ${part}` : m.dayIndex === 1 ? `mañana ${part}` : `el ${m.day} ${part}`;
        return `¡Hola Yofren! Quisiera ${svc} para ${who}${name} ${when}.${where} ¿Tienen espacio?`;
      },
    },
  };
  const SVC = {
    en: { bath: "a bath with blow-dry", haircut: "a haircut", nails: "a nail trim", ears: "ear cleaning", teeth: "teeth brushing" },
    es: { bath: "baño con secado", haircut: "corte", nails: "corte de uñas", ears: "limpieza de oídos", teeth: "cepillado de dientes" },
  };
  const listEn = (a) => (a.length < 2 ? a[0] : `${a.slice(0, -1).join(", ")} and ${a[a.length - 1]}`);
  const listEs = (a) => (a.length < 2 ? a[0] : `${a.slice(0, -1).join(", ")} y ${a[a.length - 1]}`);

  let lang = "en";
  try { const saved = localStorage.getItem("yofren-lang"); if (saved === "es" || saved === "en") lang = saved; } catch {}
  if (lang === "en" && /^es\b/i.test(navigator.language || "")) lang = "es";

  // Time in Miami, not the visitor's zone.
  function miamiNow() {
    const p = Object.fromEntries(new Intl.DateTimeFormat("en-US", { timeZone: TZ, weekday: "short", hour: "numeric", minute: "numeric", hourCycle: "h23", year: "numeric", month: "numeric", day: "numeric" }).formatToParts(new Date()).map((x) => [x.type, x.value]));
    const dow = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].indexOf(p.weekday);
    return { dow, min: Number(p.hour) * 60 + Number(p.minute), date: new Date(Number(p.year), Number(p.month) - 1, Number(p.day)) };
  }
  const fmt = (min) => {
    const h = Math.floor(min / 60), m = min % 60;
    const ampm = h >= 12 ? "pm" : "am";
    const h12 = ((h + 11) % 12) + 1;
    return m ? `${h12}:${String(m).padStart(2, "0")} ${ampm}` : `${h12} ${ampm}`;
  };

  function renderOpen() {
    const t = T[lang], now = miamiNow(), el = document.getElementById("open-status");
    const [o, c] = HOURS[now.dow];
    if (now.min >= o && now.min < c) { el.textContent = t.openNow(fmt(c)); el.classList.remove("closed"); return; }
    let d = now.min < o ? 0 : 1;
    const day = (now.dow + d) % 7;
    el.textContent = t.closedNow(d === 0 ? t.today : t.tomorrow, fmt(HOURS[day][0]));
    el.classList.add("closed");
  }

  function renderHours() {
    const t = T[lang], now = miamiNow(), table = document.getElementById("hours-table");
    const order = [1, 2, 3, 4, 5, 6, 0];
    table.innerHTML = order.map((d) => `<tr class="${d === now.dow ? "today" : ""}"><th scope="row">${cap(t.days[d])}</th><td>${fmt(HOURS[d][0])} – ${fmt(HOURS[d][1])}</td></tr>`).join("");
  }
  const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);

  function renderDays() {
    const t = T[lang], now = miamiNow(), row = document.getElementById("day-row");
    const prev = row.querySelector("input:checked")?.value;
    row.innerHTML = Array.from({ length: 7 }, (_, i) => {
      const d = new Date(now.date); d.setDate(d.getDate() + i);
      const dow = d.getDay();
      const label = i === 0 ? cap(t.today) : t.daysShort[dow];
      return `<label class="day"><input type="radio" name="day" value="${i}" ${String(i) === (prev ?? "1") ? "checked" : ""}><span>${label}<b>${d.getDate()}</b></span></label>`;
    }).join("");
  }

  const form = document.getElementById("plan-form");
  const bubble = document.getElementById("bubble");
  const sizeSet = document.getElementById("size-set");
  function state() {
    const f = new FormData(form);
    const t = T[lang], now = miamiNow();
    const i = Number(f.get("day") ?? 1);
    const d = new Date(now.date); d.setDate(d.getDate() + i);
    const day = i === 0 ? t.today : i === 1 ? t.tomorrow : t.days[d.getDay()];
    return {
      pet: f.get("pet"), size: f.get("size"), services: f.getAll("svc"), time: f.get("time"),
      day, dayIndex: i, name: String(f.get("petName") || "").trim(), area: String(f.get("area") || "").trim(),
    };
  }
  function renderMessage() {
    const m = state();
    sizeSet.hidden = m.pet === "cat";
    const text = T[lang].msg(m);
    bubble.textContent = text;
    bubble.classList.add("changed");
    clearTimeout(renderMessage.t);
    renderMessage.t = setTimeout(() => bubble.classList.remove("changed"), 220);
    const sep = /iPhone|iPad|iPod|Mac/.test(navigator.userAgent) ? "&" : "?";
    document.getElementById("send-sms").href = `sms:${PHONE}${sep}body=${encodeURIComponent(text)}`;
  }
  form.addEventListener("input", renderMessage);
  form.addEventListener("change", renderMessage);

  document.getElementById("copy-msg").addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(bubble.textContent);
      document.getElementById("copy-note").textContent = T[lang].copied;
    } catch {
      const r = document.createRange(); r.selectNodeContents(bubble);
      const s = getSelection(); s.removeAllRanges(); s.addRange(r);
    }
  });

  function applyLang() {
    const t = T[lang];
    document.documentElement.lang = lang;
    document.querySelectorAll("[data-i18n]").forEach((el) => { const v = t[el.dataset.i18n]; if (typeof v === "string") el.textContent = v; });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => { el.placeholder = t[el.dataset.i18nPlaceholder]; });
    document.querySelectorAll(".lang button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.lang === lang)));
    renderOpen(); renderHours(); renderDays(); renderMessage();
  }
  document.querySelectorAll(".lang button").forEach((b) => b.addEventListener("click", () => {
    lang = b.dataset.lang;
    try { localStorage.setItem("yofren-lang", lang); } catch {}
    applyLang();
  }));

  // The hero video stays still for people who asked for less motion.
  const video = document.querySelector(".hero-media");
  if (matchMedia("(prefers-reduced-motion: reduce)").matches && video) { video.removeAttribute("autoplay"); video.pause(); }

  // Hide the phone bar while the composer (which has its own send button) is in view.
  const bar = document.getElementById("thumb-bar");
  if (bar && "IntersectionObserver" in window) {
    new IntersectionObserver(([e]) => bar.classList.toggle("away", e.isIntersecting), { threshold: 0.15 }).observe(document.getElementById("plan"));
  }

  applyLang();
  setInterval(renderOpen, 60000);
})();
