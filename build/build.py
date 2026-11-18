#!/usr/bin/env python3
"""HeartConnect.com static site builder (standard library only).

Usage:  python3 build/build.py
Reads   build/pages/*.html and build/articles/*.html (each starts with a front-matter
        comment block) and writes the finished site into the repository root.
Add a new article: drop a new file in build/articles/ and re-run (the GitHub Action
does this automatically every day).
"""
import datetime as dt
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# ----------------------------------------------------------------- settings
SITE = {
    "name": "HeartConnect.com",
    "url": "https://heartconnect.com",          # canonical domain
    "tagline": "Heart health, connected.",
    "adsense": "ca-pub-6620975821265271",
    # Optional: fill AdSense manual ad-unit slot IDs once created in AdSense.
    # Empty = rely on Auto ads (recommended for approval).
    "ad_slots": {"in_article": "", "sidebar": "", "footer": ""},
    "ga4": "",  # optional Google Analytics 4 measurement ID, e.g. G-XXXXXXX
}

ADSENSE_TAG = ('<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js'
               '?client=ca-pub-6620975821265271" crossorigin="anonymous"></script>')

NAV = [
    ("index.html", "Home", "home"),
    ("heart-health.html", "Heart Health", "library"),
    ("tools.html", "Tools", "tools"),
    ("videos.html", "Videos", "videos"),
    ("find-care.html", "Find Care", "care"),
    ("community.html", "Community", "community"),
    ("contests.html", "Contests", "contests"),
    ("news.html", "News", "news"),
    ("donate.html", "Donate", "donate"),
]

CATS = {
    "emergency": ("Emergencies", "rose"),
    "conditions": ("Conditions", "sky"),
    "prevention": ("Prevention", "teal"),
    "nutrition": ("Nutrition", "amber"),
    "living": ("Living Well", "violet"),
    "care": ("Care & Tests", "sky"),
}

LOGO = ('<svg class="logo" viewBox="0 0 48 48" aria-hidden="true"><defs><linearGradient id="lg" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#e11d48"/><stop offset="1" stop-color="#fb7185"/></linearGradient></defs>'
        '<path class="beat" fill="url(#lg)" d="M24 42s-15-9.2-15-21A8.5 8.5 0 0 1 24 15a8.5 8.5 0 0 1 15 6c0 11.8-15 21-15 21z"/>'
        '<path d="M10 25h8l3-6 4 11 3-5h10" stroke="#fff" stroke-width="2.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>')


def esc(s):
    return html.escape(str(s), quote=True)


def parse(path):
    raw = open(path, encoding="utf-8").read()
    m = re.match(r"\s*<!--(.*?)-->(.*)", raw, re.S)
    meta, body = {}, raw
    if m:
        for line in m.group(1).strip().splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        body = m.group(2)
    return meta, body


def ad_unit(kind, root):
    slot = SITE["ad_slots"].get(kind)
    if not slot:
        return ""  # Auto ads will place ads; no empty manual units (policy-safe)
    return ('<div class="ad-zone"><div class="ad-label">Advertisement</div>'
            f'<ins class="adsbygoogle" style="display:block" data-ad-client="{SITE["adsense"]}" '
            f'data-ad-slot="{slot}" data-ad-format="auto" data-full-width-responsive="true"></ins></div>')


def newsletter(root, compact=False):
    return f'''<form class="hc-form form" data-subject="Newsletter signup" data-success="You're in! Watch your inbox for weekly heart-health tips.">
  <input type="text" name="_honey" class="hp" tabindex="-1" autocomplete="off">
  <input type="hidden" name="form" value="newsletter">
  <div class="{'form' if compact else 'form-row'}">
    <div><label for="nl-name-{'c' if compact else 'f'}" class="sr">First name</label><input id="nl-name-{'c' if compact else 'f'}" name="first_name" placeholder="First name" required></div>
    <div><label for="nl-email-{'c' if compact else 'f'}" class="sr">Email</label><input id="nl-email-{'c' if compact else 'f'}" type="email" name="email" placeholder="you@example.com" required></div>
  </div>
  <label class="check"><input type="checkbox" name="consent" value="yes" required> I agree to receive emails and accept the <a href="{root}privacy.html">Privacy Policy</a>. Unsubscribe anytime.</label>
  <button class="btn btn-primary" type="submit">Get free weekly tips</button>
  <div class="form-msg" role="status"></div>
</form>'''


def lead_form(root):
    return f'''<form class="hc-form steps-form form" data-subject="Heart Care Concierge lead" data-success="Thank you! A HeartConnect care coordinator will contact you within 24–48 hours with your personalised options.">
  <input type="text" name="_honey" class="hp" tabindex="-1" autocomplete="off">
  <input type="hidden" name="form" value="care-concierge">
  <div class="progress" aria-hidden="true"><span></span></div>
  <div class="step">
    <h3 style="margin:0">1. What do you need help with?</h3>
    <input type="hidden" name="need" required>
    <div class="chips" data-name="need" data-auto>
      <button type="button" class="chip">Second opinion</button><button type="button" class="chip">Find a cardiologist</button>
      <button type="button" class="chip">Heart surgery / procedure options</button><button type="button" class="chip">Cost estimate &amp; hospitals</button>
      <button type="button" class="chip">Preventive heart check-up</button><button type="button" class="chip">Cardiac rehab / recovery</button>
      <button type="button" class="chip">Medical travel for heart care</button><button type="button" class="chip">Something else</button>
    </div>
    <button type="button" class="btn btn-primary" data-next>Continue →</button>
  </div>
  <div class="step">
    <h3 style="margin:0">2. Tell us a little more</h3>
    <div class="form-row">
      <div><label for="lf-for">This is for</label><select id="lf-for" name="patient" required><option value="">Select…</option><option>Myself</option><option>Parent</option><option>Spouse / partner</option><option>Child</option><option>Other family / friend</option></select></div>
      <div><label for="lf-age">Patient age</label><select id="lf-age" name="age_range" required><option value="">Select…</option><option>Under 18</option><option>18–39</option><option>40–59</option><option>60–74</option><option>75+</option></select></div>
    </div>
    <div><label for="lf-cond">Condition or diagnosis (if known)</label><input id="lf-cond" name="condition" placeholder="e.g., blocked arteries, AFib, valve disease, high BP"></div>
    <div><label for="lf-urg">How soon do you need help?</label><select id="lf-urg" name="timeline" required><option value="">Select…</option><option>Within a week</option><option>Within a month</option><option>1–3 months</option><option>Just researching</option></select></div>
    <div style="display:flex;gap:10px"><button type="button" class="btn btn-ghost" data-prev>← Back</button><button type="button" class="btn btn-primary" data-next>Continue →</button></div>
  </div>
  <div class="step">
    <h3 style="margin:0">3. Location &amp; preferences</h3>
    <div class="form-row">
      <div><label for="lf-country">Country</label><input id="lf-country" name="country" placeholder="Country" required></div>
      <div><label for="lf-city">City</label><input id="lf-city" name="city" placeholder="City"></div>
    </div>
    <div><label for="lf-pay">How will care be paid for?</label><select id="lf-pay" name="payment"><option>Health insurance</option><option>Government scheme</option><option>Self-pay</option><option>Employer / corporate</option><option>Not sure yet</option></select></div>
    <div><label for="lf-travel">Open to travelling for treatment?</label><select id="lf-travel" name="travel"><option>Only near me</option><option>Within my country</option><option>Yes, internationally</option></select></div>
    <div style="display:flex;gap:10px"><button type="button" class="btn btn-ghost" data-prev>← Back</button><button type="button" class="btn btn-primary" data-next>Last step →</button></div>
  </div>
  <div class="step">
    <h3 style="margin:0">4. Where should we send your options?</h3>
    <div class="form-row">
      <div><label for="lf-name">Full name</label><input id="lf-name" name="name" autocomplete="name" required></div>
      <div><label for="lf-phone">Phone / WhatsApp</label><input id="lf-phone" name="phone" type="tel" autocomplete="tel" required></div>
    </div>
    <div><label for="lf-email">Email</label><input id="lf-email" type="email" name="email" autocomplete="email" required></div>
    <div><label for="lf-msg">Anything else? (optional)</label><textarea id="lf-msg" name="message" placeholder="Reports you have, hospitals you're considering, questions…"></textarea></div>
    <label class="check"><input type="checkbox" name="consent" value="yes" required> I agree to be contacted about my request and accept the <a href="{root}privacy.html">Privacy Policy</a> and <a href="{root}terms.html">Terms</a>. I understand HeartConnect is not an emergency service.</label>
    <div style="display:flex;gap:10px"><button type="button" class="btn btn-ghost" data-prev>← Back</button><button class="btn btn-primary" type="submit">Get my free options ❤</button></div>
    <p class="form-note">🔒 Your details are shared only with the coordinator handling your request. No spam, ever.</p>
  </div>
  <div class="form-msg" role="status"></div>
</form>'''


VIDEO_TOPICS = [
    ("cpr", "Hands-Only CPR", "🫀", "hands only CPR how to"),
    ("bp", "Blood Pressure", "🩺", "how to lower blood pressure naturally doctor explains"),
    ("diet", "Heart-Healthy Eating", "🥗", "heart healthy diet cardiologist"),
    ("exercise", "Exercise & Fitness", "🏃", "exercise for heart health cardiologist"),
    ("conditions", "Heart Conditions", "📚", "heart disease explained animation"),
    ("stories", "Survivor Stories", "💬", "heart attack survivor story"),
]


def video_fallback(limit=6):
    cards = []
    for key, title, ico, q in VIDEO_TOPICS[:limit]:
        url = "https://www.youtube.com/results?search_query=" + q.replace(" ", "+")
        cards.append(f'<div class="card reveal"><div class="ico">{ico}</div><h3>{title}</h3>'
                     f'<p class="muted">Hand-picked explainer videos from hospitals, cardiologists and heart charities.</p>'
                     f'<a class="btn btn-ghost btn-sm" href="{url}" target="_blank" rel="noopener">Watch on YouTube ↗</a></div>')
    return "".join(cards)


def head(meta, root, path):
    title = meta.get("title", SITE["name"])
    full_title = title if "HeartConnect" in title else f"{title} | HeartConnect.com"
    desc = meta.get("description", "")
    canonical = SITE["url"] + "/" + ("" if path == "index.html" else path)
    schema = meta.get("_schema", "")
    ga = ""
    if SITE["ga4"]:
        ga = (f'<script async src="https://www.googletagmanager.com/gtag/js?id={SITE["ga4"]}"></script>'
              f'<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}gtag("js",new Date());gtag("config","{SITE["ga4"]}");</script>')
    return f'''<!DOCTYPE html>
<html lang="en" data-root="{root}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="google-adsense-account" content="{SITE['adsense']}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="{meta.get('robots', 'index,follow,max-image-preview:large')}">
<meta name="theme-color" content="#e11d48">
<meta property="og:type" content="{'article' if meta.get('_article') else 'website'}">
<meta property="og:site_name" content="HeartConnect.com">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE['url']}/assets/img/og-image.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{root}assets/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{root}assets/img/icon-192.png">
<link rel="manifest" href="{root}manifest.json">
<link rel="alternate" type="application/rss+xml" title="HeartConnect.com" href="{root}feed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}assets/css/style.css">
{ADSENSE_TAG}
{ga}
<script>try{{var t=localStorage.getItem('hc-theme');if(t)document.documentElement.setAttribute('data-theme',t)}}catch(e){{}}</script>
{schema}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
'''


def header(root, nav_key):
    cur = ' aria-current="page"'
    items = "".join(
        f'<li><a href="{root}{href}"{cur if key == nav_key else ""}>{label}</a></li>'
        for href, label, key in NAV)
    return f'''<div class="topbar"><span class="pulse"></span>Contact, if you are interested in this website / domain name / Sponsorship / Advertisement / Partnership — <a href="#" data-wc>Get in touch →</a></div>
<div class="emergency">⚠️ Medical emergency? Call your local emergency number now (e.g., 911 US · 112 EU/India · 999 UK). HeartConnect does not provide emergency care.</div>
<header class="header"><div class="container nav">
  <a class="brand" href="{root}index.html" aria-label="HeartConnect.com home">{LOGO}<span>HeartConnect<small>.com</small></span></a>
  <ul class="menu" id="menu">{items}</ul>
  <div class="nav-actions">
    <button class="icon-btn" id="themeToggle" aria-label="Toggle dark mode">🌙</button>
    <a class="btn btn-primary btn-sm" href="{root}find-care.html">Free Care Match</a>
    <button class="icon-btn burger" id="burger" aria-label="Open menu" aria-expanded="false" aria-controls="menu">☰</button>
  </div>
</div></header>
<main id="main">
'''


def footer(root):
    return f'''</main>
<footer class="footer"><div class="container">
  <div class="footer-grid">
    <div>
      <a class="brand" href="{root}index.html" style="color:#fff">{LOGO}<span>HeartConnect<small>.com</small></span></a>
      <p style="margin-top:12px">Independent heart-health education, tools and care connections — helping people understand their hearts and reach the right care faster.</p>
      <div class="share" style="margin-top:12px"><a class="btn btn-sm btn-outline-white" href="#" data-share="x">Share on X</a><a class="btn btn-sm btn-outline-white" href="#" data-share="whatsapp">WhatsApp</a></div>
    </div>
    <div><h4>Learn</h4><ul>
      <li><a href="{root}heart-health.html">Heart Health Library</a></li><li><a href="{root}tools.html">Heart Tools &amp; Calculators</a></li>
      <li><a href="{root}videos.html">Video Hub</a></li><li><a href="{root}news.html">Heart News</a></li><li><a href="{root}heart-reset-plan.html">Free 30-Day Plan</a></li></ul></div>
    <div><h4>Connect</h4><ul>
      <li><a href="{root}find-care.html">Heart Care Concierge</a></li><li><a href="{root}community.html">Community &amp; Stories</a></li>
      <li><a href="{root}contests.html">Contests &amp; Prizes</a></li><li><a href="{root}careers.html">Careers &amp; Volunteers</a></li><li><a href="{root}faq.html">FAQ</a></li></ul></div>
    <div><h4>Support</h4><ul>
      <li><a href="{root}donate.html">Donate</a></li><li><a href="{root}advertise.html">Advertise &amp; Sponsor</a></li>
      <li><a href="{root}about.html">About Us</a></li><li><a href="{root}contact.html">Contact</a></li><li><a href="#" data-wc>Buy / Partner on this domain</a></li></ul></div>
    <div><h4>Policies</h4><ul>
      <li><a href="{root}privacy.html">Privacy Policy</a></li><li><a href="{root}terms.html">Terms of Use</a></li>
      <li><a href="{root}disclaimer.html">Medical Disclaimer</a></li><li><a href="{root}cookie-policy.html">Cookie Policy</a></li>
      <li><a href="{root}editorial-policy.html">Editorial Policy</a></li><li><a href="{root}trademark.html">Trademark &amp; Copyright</a></li></ul></div>
  </div>
  <p class="disclaim">HeartConnect.com provides general health information for educational purposes only. It is not medical advice and does not replace a qualified healthcare professional. Always seek the advice of your doctor with questions about a medical condition. HeartConnect.com is an independent website and is not affiliated with, endorsed by, or sponsored by any hospital, charity, government body or company named on this site, or by any other business using a similar name.</p>
  <div class="legal"><span>© <span data-year></span> HeartConnect.com · All original content and design rights reserved.</span><span><a href="{root}sitemap.xml">Sitemap</a> · <a href="{root}feed.xml">RSS</a> · <a href="{root}trademark.html">Trademark disclosure</a></span></div>
</div></footer>
<div class="cookie" id="cookie" role="dialog" aria-label="Cookie consent">
  <strong>We value your privacy 🍪</strong>
  <p>We use cookies to run this site, measure traffic and show ads (including personalised ads from Google). See our <a href="{root}cookie-policy.html">Cookie Policy</a>.</p>
  <div style="display:flex;gap:8px;flex-wrap:wrap"><button class="btn btn-primary btn-sm" data-consent="all">Accept all</button><button class="btn btn-ghost btn-sm" data-consent="essential">Essential only</button></div>
</div>
<div class="modal" id="leadModal" aria-modal="true" role="dialog" aria-labelledby="mTitle"><div class="modal-box">
  <button class="modal-close" aria-label="Close">×</button>
  <div class="ico" style="font-size:2.2rem">🎁</div>
  <h3 id="mTitle">Free: 30-Day Heart Reset Plan</h3>
  <p class="muted">A printable day-by-day plan with simple food, movement, sleep and stress habits. Join 1 email a week — unsubscribe anytime.</p>
  <form class="hc-form form" data-subject="Lead magnet: 30-Day Heart Reset" data-success="Done! Open your plan now: it's also on its way to your inbox.">
    <input type="text" name="_honey" class="hp" tabindex="-1" autocomplete="off"><input type="hidden" name="form" value="lead-magnet">
    <input name="first_name" placeholder="First name" required aria-label="First name"><input type="email" name="email" placeholder="Email address" required aria-label="Email">
    <label class="check"><input type="checkbox" name="consent" value="yes" required> I agree to the <a href="{root}privacy.html">Privacy Policy</a>.</label>
    <button class="btn btn-primary btn-block" type="submit">Send me the plan</button>
    <div class="form-msg" role="status"></div>
  </form>
  <p class="form-note" style="margin-top:10px">Prefer to just read it? <a href="{root}heart-reset-plan.html">Open the plan</a>.</p>
</div></div>
<div class="sticky-cta"><a class="btn btn-primary" href="{root}find-care.html">❤ Free Care Match</a><a class="btn btn-dark" href="{root}donate.html">Donate</a></div>
<button class="icon-btn to-top" id="toTop" aria-label="Back to top">↑</button>
<script src="{root}assets/js/main.js" defer></script>
'''


def render(meta, body, root, path, nav_key, extra_js=""):
    return head(meta, root, path) + header(root, nav_key) + body + footer(root) + extra_js + "</body>\n</html>\n"


def fill(body, root, ctx):
    rep = {
        "{{ROOT}}": root,
        "{{NEWSLETTER}}": newsletter(root),
        "{{NEWSLETTER_COMPACT}}": newsletter(root, compact=True),
        "{{LEAD_FORM}}": lead_form(root),
        "{{VIDEO_FALLBACK}}": video_fallback(6),
        "{{AD_IN_ARTICLE}}": ad_unit("in_article", root),
        "{{AD_FOOTER}}": ad_unit("footer", root),
    }
    rep.update(ctx)
    for k, v in rep.items():
        body = body.replace(k, v)
    return body


def article_card(a, root, lib=False):
    label, color = CATS.get(a["category"], ("Health", "rose"))
    attrs = f' data-lib data-cat="{a["category"]}"' if lib else ""
    return (f'<article class="card article-card reveal"{attrs}>'
            f'<div class="thumb" style="background:{a.get("bg", "var(--rose-50)")}">{a.get("emoji", "❤️")}</div>'
            f'<div class="meta"><span class="tag {color}">{label}</span><span>{a.get("read", "6")} min read</span></div>'
            f'<h3><a href="{root}articles/{a["slug"]}.html">{esc(a["title"])}</a></h3>'
            f'<p class="muted">{esc(a["description"])}</p>'
            f'<a class="card-link" href="{root}articles/{a["slug"]}.html" aria-label="{esc(a["title"])}"></a></article>')


def build():
    today = dt.date.today().isoformat()
    # ---------- articles
    arts = []
    adir = os.path.join(HERE, "articles")
    for fn in sorted(os.listdir(adir)):
        if not fn.endswith(".html"):
            continue
        meta, body = parse(os.path.join(adir, fn))
        meta["slug"] = fn[:-5]
        meta["body"] = body
        arts.append(meta)
    arts.sort(key=lambda a: (int(a.get("order", 99)), a["slug"]))

    os.makedirs(os.path.join(ROOT, "articles"), exist_ok=True)
    for a in arts:
        root = "../"
        path = f"articles/{a['slug']}.html"
        label, color = CATS.get(a["category"], ("Health", "rose"))
        related = [x for x in arts if x["category"] == a["category"] and x["slug"] != a["slug"]][:2]
        related += [x for x in arts if x not in related and x["slug"] != a["slug"]][: 3 - len(related)]
        sources = ""
        if a.get("sources"):
            items = []
            for s in a["sources"].split(";;"):
                if "|" in s:
                    t, u = s.split("|", 1)
                    items.append(f'<li><a href="{esc(u.strip())}" target="_blank" rel="noopener nofollow">{esc(t.strip())}</a></li>')
            sources = '<h2>Trusted sources &amp; further reading</h2><ul>' + "".join(items) + "</ul>"
        schema = {
            "@context": "https://schema.org", "@type": "MedicalWebPage",
            "headline": a["title"], "description": a["description"],
            "datePublished": a.get("date", today), "dateModified": a.get("updated", a.get("date", today)),
            "author": {"@type": "Organization", "name": "HeartConnect Editorial Team"},
            "publisher": {"@type": "Organization", "name": "HeartConnect.com", "logo": {"@type": "ImageObject", "url": SITE["url"] + "/assets/img/icon-512.png"}},
            "mainEntityOfPage": SITE["url"] + "/" + path, "about": {"@type": "MedicalCondition", "name": a.get("about", a["title"])},
        }
        a["_schema"] = f'<script type="application/ld+json">{json.dumps(schema)}</script>'
        a["_article"] = "1"
        body = fill(a["body"], root, {})
        # insert in-article ad after the 3rd paragraph block if a slot exists
        page = f'''<section class="article-hero"><div class="container">
  <div class="breadcrumb"><a href="{root}index.html">Home</a> › <a href="{root}heart-health.html">Heart Health</a> › {label}</div>
  <span class="tag {color}">{label}</span>
  <h1 style="margin-top:12px;max-width:900px">{esc(a["title"])}</h1>
  <p class="muted" style="font-size:1.15rem;max-width:820px">{esc(a["description"])}</p>
  <div class="byline"><span>✍️ HeartConnect Editorial Team</span><span>📅 Updated {a.get("updated", a.get("date", today))}</span><span>⏱ {a.get("read", "6")} min read</span><span>📚 Based on guidance from leading heart organisations</span></div>
</div></section>
<section style="padding-top:20px"><div class="container article-layout">
  <article class="prose">
    {body}
    <div class="callout teal"><strong>Medical note:</strong> This article is general education, not a diagnosis. Talk with a qualified clinician about your own situation. If you think someone is having a heart attack or stroke, call emergency services immediately.</div>
    {sources}
    <div class="share no-print" style="margin-top:24px"><strong>Share:</strong> <a class="btn btn-ghost btn-sm" href="#" data-share="whatsapp">WhatsApp</a><a class="btn btn-ghost btn-sm" href="#" data-share="facebook">Facebook</a><a class="btn btn-ghost btn-sm" href="#" data-share="x">X</a><a class="btn btn-ghost btn-sm" href="#" data-share="linkedin">LinkedIn</a><a class="btn btn-ghost btn-sm" href="#" data-share="copy">Copy link</a></div>
  </article>
  <aside class="sidebar no-print"><div class="toc">
    <div class="card" style="background:var(--grad);color:#fff;border:0"><h3 style="color:#fff">Need a cardiologist or second opinion?</h3><p style="color:#ffe4e6">Get matched with trusted heart-care options — free, fast and no obligation.</p><a class="btn btn-white btn-block" href="{root}find-care.html">Get free care match</a></div>
    {ad_unit("sidebar", root)}
    <div class="card"><h3>Try our free tools</h3><ul style="padding-left:1.1em;margin:0"><li><a href="{root}tools.html#bp">Blood pressure checker</a></li><li><a href="{root}tools.html#score">Heart Habits Score</a></li><li><a href="{root}tools.html#log">BP tracker &amp; chart</a></li><li><a href="{root}tools.html#hr">Target heart rate</a></li></ul></div>
    <div class="card"><h3>Weekly heart tips</h3>{newsletter(root, compact=True)}</div>
  </div></aside>
</div></section>
<section class="section-alt no-print"><div class="container"><h2>Keep reading</h2><div class="grid g3">{"".join(article_card(r, root) for r in related)}</div></div></section>
'''
        out = render(a, page, root, path, "library")
        open(os.path.join(ROOT, path), "w", encoding="utf-8").write(out)

    # ---------- pages
    pdir = os.path.join(HERE, "pages")
    pages = []
    for fn in sorted(os.listdir(pdir)):
        if not fn.endswith(".html"):
            continue
        meta, body = parse(os.path.join(pdir, fn))
        path = meta.get("path", fn)
        ctx = {
            "{{FEATURED_ARTICLES}}": "".join(article_card(a, "") for a in arts[:6]),
            "{{LIBRARY}}": "".join(article_card(a, "", lib=True) for a in arts),
            "{{ARTICLE_COUNT}}": str(len(arts)),
        }
        body = fill(body, "", ctx)
        extra = '<script src="assets/js/tools.js" defer></script>\n' if meta.get("tools") else ""
        if meta.get("schema") == "faq":
            qa = re.findall(r"<summary>(.*?)</summary>\s*<p>(.*?)</p>", body, re.S)
            meta["_schema"] = '<script type="application/ld+json">' + json.dumps({
                "@context": "https://schema.org", "@type": "FAQPage",
                "mainEntity": [{"@type": "Question", "name": re.sub("<.*?>", "", q),
                                "acceptedAnswer": {"@type": "Answer", "text": re.sub("<.*?>", "", ans)}} for q, ans in qa]}) + "</script>"
        if path == "index.html":
            meta["_schema"] = '<script type="application/ld+json">' + json.dumps({
                "@context": "https://schema.org", "@type": "WebSite", "name": "HeartConnect.com", "url": SITE["url"],
                "potentialAction": {"@type": "SearchAction", "target": SITE["url"] + "/heart-health.html?q={search_term_string}",
                                    "query-input": "required name=search_term_string"}}) + "</script>"
        open(os.path.join(ROOT, path), "w", encoding="utf-8").write(render(meta, body, "", path, meta.get("nav", ""), extra))
        if meta.get("robots", "").startswith("noindex"):
            continue
        pages.append((path, meta.get("priority", "0.7")))

    # ---------- sitemap, feed, robots
    urls = [(p, pr) for p, pr in pages] + [(f"articles/{a['slug']}.html", "0.8") for a in arts]
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p, pr in urls:
        loc = SITE["url"] + "/" + ("" if p == "index.html" else p)
        sm.append(f"  <url><loc>{loc}</loc><lastmod>{today}</lastmod><priority>{pr}</priority></url>")
    sm.append("</urlset>")
    open(os.path.join(ROOT, "sitemap.xml"), "w").write("\n".join(sm) + "\n")

    items = "".join(
        f"<item><title>{esc(a['title'])}</title><link>{SITE['url']}/articles/{a['slug']}.html</link>"
        f"<guid>{SITE['url']}/articles/{a['slug']}.html</guid><description>{esc(a['description'])}</description></item>"
        for a in arts)
    open(os.path.join(ROOT, "feed.xml"), "w").write(
        f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>HeartConnect.com</title>'
        f'<link>{SITE["url"]}</link><description>Heart health, connected.</description>'
        f'<lastBuildDate>{dt.datetime.now(dt.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")}</lastBuildDate>{items}</channel></rss>\n')
    open(os.path.join(ROOT, "robots.txt"), "w").write(
        f"User-agent: *\nAllow: /\nDisallow: /build/\nDisallow: /scripts/\n\nUser-agent: Mediapartners-Google\nAllow: /\n\nSitemap: {SITE['url']}/sitemap.xml\n")
    print(f"Built {len(pages)} pages + {len(arts)} articles")


if __name__ == "__main__":
    build()
