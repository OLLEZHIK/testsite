// Phone menu: the burger opens the section list; a tap on a section closes it.
(function () {
  var top = document.querySelector(".top"), burger = document.querySelector(".burger");
  if (!top || !burger) return;
  var set = function (open) { top.classList.toggle("open", open); burger.setAttribute("aria-expanded", open ? "true" : "false"); };
  burger.addEventListener("click", function () { set(!top.classList.contains("open")); });
  document.querySelectorAll(".menu a").forEach(function (a) { a.addEventListener("click", function () { set(false); }); });
})();

// Phone: the Call/Text bar appears once the hero's own buttons scroll away.
(function () {
  var bar = document.querySelector(".mobile-bar");
  if (!bar) return;
  var onScroll = function () { bar.classList.toggle("show", window.scrollY > 560); };
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();
})();

// "Open now" from site.json hours, in the business's own time zone, and
// today's row in the hours table. Without JavaScript the table still shows
// every day.
(function () {
  var hours = window.SITE_HOURS;
  if (!hours) return;
  var keys = ["su", "mo", "tu", "we", "th", "fr", "sa"];
  var parts = new Intl.DateTimeFormat("en-US", {
    timeZone: window.SITE_TZ,
    weekday: "short",
    hour: "2-digit",
    minute: "2-digit",
    hourCycle: "h23",
  }).formatToParts(new Date());
  var get = function (t) {
    var p = parts.find(function (x) { return x.type === t; });
    return p ? p.value : "";
  };
  var dayIdx = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].indexOf(get("weekday"));
  var now = Number(get("hour")) * 60 + Number(get("minute"));
  var mins = function (t) { var a = t.split(":"); return Number(a[0]) * 60 + Number(a[1]); };
  var fmt = function (m) {
    var h = Math.floor(m / 60) % 24, mm = m % 60, ap = h >= 12 ? "PM" : "AM", h12 = h % 12 === 0 ? 12 : h % 12;
    return h12 + (mm ? ":" + String(mm).padStart(2, "0") : "") + " " + ap;
  };
  var spans = function (k) {
    var v = hours[k];
    if (!v || v === "closed") return [];
    if (v === "24h") return [[0, 1440]];
    return v.split(",").map(function (s) { var x = s.split("-"); return [mins(x[0]), mins(x[1])]; });
  };

  var today = keys[dayIdx];
  var row = document.querySelector('tr[data-day="' + today + '"]');
  if (row) row.classList.add("today");

  var text, cls;
  var open = spans(today).find(function (s) { return now >= s[0] && now < s[1]; });
  if (open) {
    text = "Open now · until " + fmt(open[1]);
    cls = "open";
  } else {
    var later = spans(today).find(function (s) { return now < s[0]; });
    if (later) {
      text = "Closed · opens " + fmt(later[0]);
    } else {
      for (var i = 1; i <= 7; i++) {
        var k = keys[(dayIdx + i) % 7], s = spans(k)[0];
        if (s) {
          var name = i === 1 ? "tomorrow" : ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][(dayIdx + i) % 7];
          text = "Closed · opens " + name + " " + fmt(s[0]);
          break;
        }
      }
    }
    cls = "closed";
  }
  document.querySelectorAll("[data-status]").forEach(function (el) {
    var label = el.querySelector("span");
    if (label) label.textContent = text; else el.textContent = text;
    el.classList.add(cls);
  });
})();
