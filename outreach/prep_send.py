#!/usr/bin/env python3
"""Prepare one outreach email with open/click marks (outreach/TRACKING.md).

  python3 outreach/prep_send.py <emails-file.md> <section number> [shot|plain]

Prints JSON: to, subject, body (plain text), htmlBody, mail_id, variant.
Appends the email to outreach/tracking.csv. Send `body` + `htmlBody` together
with Gmail send_message (one To:), then add the message id with --sent.

  python3 outreach/prep_send.py --sent <mail_id> <gmail message id>
"""
import csv, html, json, os, re, secrets, string, sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "tracking.csv")
FIELDS = ["mail_id", "prepared_utc", "file", "section", "to", "short", "variant", "message_id"]
SITE = "https://pawenn.com"
PREVIEW = re.compile(r"https://pawenn-previews\.pages\.dev/([a-z0-9]+)/?")


def rows():
    if not os.path.exists(LOG):
        return []
    with open(LOG, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save(all_rows):
    with open(LOG, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(all_rows)


def section(path, n):
    text = open(path, encoding="utf-8").read()
    m = re.search(rf"^## {n}\. .*?(?=^---$|^## |\Z)", text, re.S | re.M)
    if not m:
        sys.exit(f"no section {n} in {path}")
    s = m.group(0)
    to = re.search(r"^\*\*To:\*\*\s*(\S+)", s, re.M).group(1)
    subject = re.search(r"^\*\*Subject:\*\*\s*(.+)$", s, re.M).group(1).strip()
    body = s.split(f"**Subject:** {subject}", 1)[1].strip()
    return to, subject, body


def main():
    if sys.argv[1] == "--sent":
        all_rows = rows()
        for r in all_rows:
            if r["mail_id"] == sys.argv[2]:
                r["message_id"] = sys.argv[3]
        save(all_rows)
        return
    path, n = sys.argv[1], sys.argv[2]
    variant = sys.argv[3] if len(sys.argv) > 3 else "plain"
    to, subject, body = section(path, n)
    m = PREVIEW.search(body)
    if not m:
        sys.exit("no preview link in the email")
    short = m.group(1)
    if variant == "shot" and not os.path.exists(os.path.join(HERE, "..", "shots", short + ".jpg")):
        sys.exit(f"no shots/{short}.jpg")
    mail_id = "".join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(10))
    link = f"{SITE}/api/r/{mail_id}?to={short}"
    plain = PREVIEW.sub(link, body, count=1)

    # HTML: the same words; the link as a button-like text link; the screenshot
    # (variant "shot") or a 1x1 image at the end. Both images mark the open.
    paras = [p for p in re.split(r"\n\s*\n", body)]
    out = []
    for p in paras:
        if PREVIEW.search(p):
            if variant == "shot":
                out.append(f'<p><a href="{html.escape(link)}"><img src="{SITE}/api/o/{mail_id}.jpg?s={short}" width="560" alt="Your example website" style="width:100%;max-width:560px;height:auto;border:1px solid #ddd;border-radius:8px;display:block"></a></p>')
            out.append(f'<p><a href="{html.escape(link)}">See your example website</a></p>')
        else:
            out.append("<p>" + "<br>".join(html.escape(l) for l in p.split("\n")) + "</p>")
    if variant != "shot":
        out.append(f'<img src="{SITE}/api/o/{mail_id}.gif" width="1" height="1" alt="" style="display:block;border:0">')
    html_body = '<div style="font-family:Arial,Helvetica,sans-serif;font-size:14px;line-height:1.5;color:#222">' + "".join(out) + "</div>"

    all_rows = rows()
    all_rows.append({"mail_id": mail_id, "prepared_utc": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
                     "file": os.path.basename(path), "section": n, "to": to, "short": short, "variant": variant, "message_id": ""})
    save(all_rows)
    print(json.dumps({"to": to, "subject": subject, "body": plain, "htmlBody": html_body, "mail_id": mail_id, "variant": variant}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
