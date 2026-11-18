#!/usr/bin/env python3
"""Daily auto-refresh for HeartConnect.com (run by GitHub Actions).

1. Pulls heart-health headlines from public RSS feeds -> data/news.json
2. Pulls the latest videos from curated YouTube channel feeds and/or yt-dlp search
   -> data/videos.json  (keeps previous data if a source fails)
3. Rebuilds the static site (sitemap lastmod, feed, pages).
Standard library only, except optional yt-dlp for video search.
"""
import datetime as dt
import html
import json
import os
import re
import subprocess
import sys
import urllib.request
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
UA = {"User-Agent": "Mozilla/5.0 (compatible; HeartConnectBot/1.0; +https://heartconnect.com)"}

NEWS_FEEDS = [
    ("ScienceDaily", "https://www.sciencedaily.com/rss/health_medicine/heart_disease.xml"),
    ("ScienceDaily", "https://www.sciencedaily.com/rss/health_medicine/cholesterol.xml"),
    ("Medical Xpress", "https://medicalxpress.com/rss-feed/cardiology-news/"),
    ("NIH News", "https://www.nih.gov/news-releases/feed.xml"),
    ("NHLBI", "https://www.nhlbi.nih.gov/news/rss.xml"),
    ("Google News", "https://news.google.com/rss/search?q=heart+health+OR+cardiology+OR+%22heart+disease%22&hl=en-US&gl=US&ceid=US:en"),
]
KEYWORDS = re.compile(r"heart|cardi|blood pressure|hypertens|cholesterol|stroke|artery|arrhythm|atrial|statin|vascular|cpr", re.I)

# Curated YouTube channels (RSS needs channel_id). Add IDs in data/video_sources.json
VIDEO_QUERIES = {
    "cpr": "hands only CPR how to",
    "bp": "how to lower blood pressure doctor explains",
    "diet": "heart healthy diet cardiologist explains",
    "exercise": "best exercise for heart health cardiologist",
    "conditions": "heart disease explained animation",
    "stories": "heart attack survivor story",
}


def fetch(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def clean(s, n=220):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s or ""))
    s = re.sub(r"\s+", " ", s).strip()
    return (s[: n - 1] + "…") if len(s) > n else s


def parse_feed(source, raw):
    out = []
    root = ET.fromstring(raw)
    ns = {"a": "http://www.w3.org/2005/Atom"}
    items = root.findall(".//item")
    for it in items:
        title = clean(it.findtext("title"), 180)
        link = (it.findtext("link") or "").strip()
        date = it.findtext("pubDate") or it.findtext("{http://purl.org/dc/elements/1.1/}date") or ""
        desc = clean(it.findtext("description"))
        src = it.findtext("source") or source
        out.append({"title": title, "link": link, "date": to_iso(date), "summary": desc if source != "Google News" else "", "source": clean(src, 60)})
    for e in root.findall("a:entry", ns):
        link_el = e.find("a:link", ns)
        out.append({"title": clean(e.findtext("a:title", namespaces=ns), 180),
                    "link": link_el.get("href") if link_el is not None else "",
                    "date": to_iso(e.findtext("a:updated", namespaces=ns) or e.findtext("a:published", namespaces=ns)),
                    "summary": clean(e.findtext("a:summary", namespaces=ns)), "source": source})
    return out


def to_iso(s):
    if not s:
        return ""
    for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
        try:
            return dt.datetime.strptime(s.strip(), fmt).isoformat()
        except ValueError:
            continue
    return s.strip()


def update_news():
    items, seen = [], set()
    for source, url in NEWS_FEEDS:
        try:
            for it in parse_feed(source, fetch(url)):
                key = it["title"].lower()[:80]
                if not it["title"] or not it["link"] or key in seen:
                    continue
                if source in ("NIH News", "Google News") and not KEYWORDS.search(it["title"] + " " + it["summary"]):
                    continue
                seen.add(key)
                items.append(it)
            print(f"news ok: {source}")
        except Exception as e:  # keep going on any single feed failure
            print(f"news fail: {source}: {e}", file=sys.stderr)
    items.sort(key=lambda x: x.get("date", ""), reverse=True)
    path = os.path.join(DATA, "news.json")
    if not items and os.path.exists(path):
        print("no news fetched; keeping previous file")
        return
    json.dump({"updated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "items": items[:60]}, open(path, "w"), indent=1)


def channel_feed(cid, topic):
    raw = fetch(f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}")
    root = ET.fromstring(raw)
    ns = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015"}
    author = root.findtext("a:author/a:name", namespaces=ns) or ""
    vids = []
    for e in root.findall("a:entry", ns):
        title = e.findtext("a:title", namespaces=ns) or ""
        if not KEYWORDS.search(title):
            continue
        vids.append({"id": e.findtext("yt:videoId", namespaces=ns), "title": clean(title, 120), "channel": author,
                     "topic": topic, "date": e.findtext("a:published", namespaces=ns)})
    return vids


def ytdlp_search(query, topic, n=8):
    try:
        res = subprocess.run(["yt-dlp", "--flat-playlist", "-J", f"ytsearch{n}:{query}"],
                             capture_output=True, text=True, timeout=120)
        data = json.loads(res.stdout or "{}")
    except Exception as e:
        print(f"yt-dlp fail {topic}: {e}", file=sys.stderr)
        return []
    out = []
    for v in data.get("entries", []) or []:
        dur = v.get("duration") or 0
        if not v.get("id") or (dur and (dur < 45 or dur > 1800)):
            continue
        out.append({"id": v["id"], "title": clean(v.get("title"), 120), "channel": v.get("channel") or v.get("uploader") or "",
                    "topic": topic, "date": ""})
    return out


def update_videos():
    path = os.path.join(DATA, "videos.json")
    prev = []
    if os.path.exists(path):
        try:
            prev = json.load(open(path)).get("items", [])
        except Exception:
            prev = []
    vids = []
    src_path = os.path.join(DATA, "video_sources.json")
    if os.path.exists(src_path):
        for ch in json.load(open(src_path)).get("channels", []):
            try:
                vids += channel_feed(ch["id"], ch.get("topic", "conditions"))[:6]
            except Exception as e:
                print(f"channel fail {ch}: {e}", file=sys.stderr)
        for v in json.load(open(src_path)).get("pinned", []):
            vids.insert(0, v)
    for topic, q in VIDEO_QUERIES.items():
        vids += ytdlp_search(q, topic)
    seen, final = set(), []
    for v in vids:
        if v.get("id") and v["id"] not in seen:
            seen.add(v["id"])
            final.append(v)
    if not final:
        final = prev
        print("no videos fetched; keeping previous")
    json.dump({"updated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "items": final[:96]}, open(path, "w"), indent=1)
    print(f"videos: {len(final)}")


if __name__ == "__main__":
    os.makedirs(DATA, exist_ok=True)
    update_news()
    update_videos()
    subprocess.run([sys.executable, os.path.join(ROOT, "build", "build.py")], check=True)
