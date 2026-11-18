# HeartConnect.com — Phase-wise Build Prompt

## Chosen idea (and why)
**HeartConnect.com = an independent heart-health hub: education + free tools + video hub + community + a "Heart Care Concierge" lead-generation engine.**

Why this beats the alternatives (dating site, charity-only, generic wellness blog):
- **Highest CPC niche.** Cardiology, heart surgery, health insurance and medical-travel keywords are among the most expensive health ad categories, so AdSense RPM is far above lifestyle niches.
- **Lead value.** A qualified heart-procedure / second-opinion lead is worth far more to hospitals, medical-travel facilitators, diagnostics and insurers than an ad click. The concierge turns traffic into sellable leads.
- **Brand fit.** "Heart" + "Connect" literally describes connecting people to heart care and to each other.
- **AdSense-safe.** Unlike dating, a health-education site with original content, policies and an editorial standard is approvable.
- **Five revenue streams:** AdSense · care leads/partner referrals · sponsorships & contest sponsors · donations/memberships · affiliate (BP monitors, trackers) later.

---

## Phase 1 — Foundation & brand
Build a static, GitHub Pages-compatible site (HTML/CSS/vanilla JS, no server). Brand: rose/crimson + deep navy, heart-with-ECG logo (original SVG), Inter + Plus Jakarta Sans, light/dark mode. Every page must include:
- A top bar: "Contact, if you are interested in this website / domain name / Sponsorship / Advertisement / Partnership" linking to the owner's external business contact page. The URL must be set by JavaScript from an encoded value, never shown as text.
- An emergency strip ("call your local emergency number"), sticky glass header, mobile menu, footer with legal links, a cookie banner, a mobile sticky CTA and a back-to-top button.
- The AdSense script in `<head>` plus `meta google-adsense-account`; `ads.txt` at root.

## Phase 2 — Build system (expandable)
`build/build.py` (Python standard library only) generates every page from `build/pages/*.html` and `build/articles/*.html` fragments with front-matter. It must produce canonical URLs, Open Graph, JSON-LD (WebSite, MedicalWebPage, FAQPage), `sitemap.xml`, `feed.xml` and `robots.txt`. To add a new article, drop a file in `build/articles/` and rebuild.

## Phase 3 — Content for AdSense approval (E-E-A-T)
Write 12+ original long-form guides (600–900 words each) with trusted-source lists: heart attack signs, BP numbers, cholesterol, heart-healthy diet, exercise, AFib, heart failure, women's heart health, South-Asian heart risk, stress & sleep, Hands-Only CPR, heart tests, planning a heart procedure. Add About, Contact, Privacy (with Google ad-cookie disclosures), Terms, Medical Disclaimer, Cookie Policy, Editorial Policy, Trademark & Copyright disclosure, FAQ and a 404 page. No fake reviews, no fabricated statistics, no copied text, no third-party logos.

## Phase 4 — Interactive tools
In-browser, private: BP category checker, Heart Habits Score (8 factors), BP tracker with canvas chart, average and CSV export (localStorage), BMI with Asian cut-offs, target heart-rate zones (Tanaka/Karvonen), cholesterol ratio, waist-to-height ratio. Every result ends with a call to action for the concierge.

## Phase 5 — Lead generation (core revenue)
- **Heart Care Concierge**: 4-step form with progress bar and chip answers (need → patient details → location/payment/travel → contact + consent), shown on the home page and on `find-care.html`.
- Exit-intent and 45-second modal offering the **free 30-Day Heart Reset Plan** (printable page).
- Newsletter forms in sidebars, CTA bands on every page and a sticky mobile CTA.
- All forms POST by AJAX to FormSubmit. The destination address is stored XOR-encoded in JS (never in HTML), with a honeypot, consent checkbox and success/error states.

## Phase 6 — Donations, contests, hiring, partnerships
- `donate.html`: one-time/monthly toggle, preset amounts and custom amount, currency, fund selector (operations, promotion, hiring, prizes, CPR drives), a PayPal checkout link built at runtime, and a pledge form for UPI, bank transfer, CSR or crypto.
- `contests.html`: a live monthly contest with an auto-rolling countdown, prizes, 8 rotating contest themes, official rules and an entry form.
- `careers.html`: roles plus an application/volunteer form. `advertise.html`: sponsorship tiers plus an enquiry form (including domain acquisition).
- `community.html`: support circles, a join form and a story-submission form.

## Phase 7 — Self-updating automation
- `scripts/update_content.py` pulls heart-health RSS feeds into `data/news.json` and YouTube videos (yt-dlp search plus optional channel RSS in `data/video_sources.json`) into `data/videos.json`, then rebuilds the site.
- `.github/workflows/auto-refresh.yml` runs daily, on manual dispatch and on pushes to `build/` or `scripts/`. It commits changes and requests a Pages rebuild.
- The front-end lazily renders news and lite-YouTube embeds (youtube-nocookie, click to play). A daily rotating tip and a countdown keep pages fresh.

## Phase 8 — Deploy & approval checklist
1. Push to `main` and set Pages to deploy from `main` / root, with `.nojekyll` present.
2. Point the custom domain: add a `CNAME` file containing `heartconnect.com`, then at the DNS host create A records to 185.199.108.153, .109, .110 and .111 plus `www` CNAME → `webworksa1.github.io`. Enable "Enforce HTTPS".
3. Submit the sitemap in Google Search Console.
4. In AdSense, add the site, verify `ads.txt`, and enable Auto ads plus Google's certified **Privacy & messaging** CMP for EEA/UK.
5. Confirm FormSubmit activation (the first submission sends an activation email to the owner's inbox; click it once).
6. Publish 2–4 new articles a month, then add manual ad-unit slot IDs in `SITE["ad_slots"]` once approved.

## Phase 9 — Scale (after approval)
Hospital and medical-travel partner program (pay per qualified lead), affiliate gear reviews (BP monitors, ECG watches), regional languages (Hindi, Spanish), a quiz engine, a webinar series and a paid premium "Heart Coach" membership.
