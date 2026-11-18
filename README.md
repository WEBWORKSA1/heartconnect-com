# HeartConnect.com

Independent heart-health education, free tools, a self-updating video and news hub, a community, and a **Heart Care Concierge** lead-generation engine. The site is static and hosted free on GitHub Pages (`main` branch, root).

- **Live (GitHub Pages):** https://webworksa1.github.io/heartconnect-com/
- **Custom domain:** heartconnect.com (see DNS steps in `docs/PROMPT.md`, Phase 8)

## Structure
| Path | Purpose |
|---|---|
| `build/build.py` | Static site generator (Python standard library only) |
| `build/pages/` | Page fragments (home, tools, find-care, donate, contests…) |
| `build/articles/` | Article fragments; add a file and rebuild to publish a new guide |
| `assets/` | CSS, JS (`main.js` core, `tools.js` calculators), images |
| `data/` | `news.json` and `videos.json` are auto-updated daily; `video_sources.json` is optional curation |
| `scripts/update_content.py` | Fetches news and videos, then rebuilds the site |
| `.github/workflows/auto-refresh.yml` | Daily automation |
| `docs/PROMPT.md` | Phase-wise build prompt and launch checklist |
| `docs/RESEARCH.md` | Findings from 39 heart-health sites |

## Edit and rebuild
```bash
python3 build/build.py
```
Monetization settings (AdSense manual slot IDs, GA4) live in `SITE` at the top of `build/build.py`.

## Forms
All forms submit through FormSubmit to the owner's private inbox. The address is stored only in encoded form in `assets/js/main.js` and is never rendered on the site. **The first submission triggers a one-time activation email, which the owner must confirm.**

## Trademark & copyright disclosure
"HeartConnect.com" is used as a domain name and descriptive site identifier. No exclusive trademark rights are claimed in "heart connect", and no ®/™ symbols are used. This project is **independent and not affiliated with any organisation, program, product or service using a similar name**, nor with any hospital, charity, society, agency or publisher referenced on the site. Third-party names are used nominatively to cite sources. No third-party logos are used. Embedded videos and news headlines remain the property of their owners. Original content, design and code are © HeartConnect.com. For takedown requests, use the site's contact page.

Content is for general education only and is not medical advice.
