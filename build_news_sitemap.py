import time
from datetime import datetime, timedelta, timezone
import feedparser
import xml.etree.ElementTree as ET

# EDIT THESE THREE LINES
RSS_URL = "https://rss.beehiiv.com/feeds/tfZrIR9nSi.xml"   # your Beehiiv RSS URL
SITE_NAME = "The Bentonville Bulletin"
SITE_LANG = "en"

now = datetime.now(timezone.utc)
cutoff = now - timedelta(days=2)  # Google News wants last 48 hours

feed = feedparser.parse(RSS_URL)

urlset = ET.Element(
    "urlset",
    {
        "xmlns": "http://www.sitemaps.org/schemas/sitemap/0.9",
        "xmlns:news": "http://www.google.com/schemas/sitemap-news/0.9",
    },
)

def iso8601(dt):
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

count = 0
for e in feed.entries:
    # Try to get a datetime
    pub_dt = None
    if "published_parsed" in e and e.published_parsed:
        pub_dt = datetime.fromtimestamp(time.mktime(e.published_parsed), tz=timezone.utc)
    elif "updated_parsed" in e and e.updated_parsed:
        pub_dt = datetime.fromtimestamp(time.mktime(e.updated_parsed), tz=timezone.utc)
    else:
        continue  # skip if no date

    if pub_dt < cutoff:
        continue

    url = ET.SubElement(urlset, "url")
    loc = ET.SubElement(url, "loc")
    loc.text = e.link

    news = ET.SubElement(url, "{http://www.google.com/schemas/sitemap-news/0.9}news")
    pub = ET.SubElement(news, "{http://www.google.com/schemas/sitemap-news/0.9}publication")
    name = ET.SubElement(pub, "{http://www.google.com/schemas/sitemap-news/0.9}name")
    name.text = SITE_NAME
    lang = ET.SubElement(pub, "{http://www.google.com/schemas/sitemap-news/0.9}language")
    lang.text = SITE_LANG

    date_el = ET.SubElement(news, "{http://www.google.com/schemas/sitemap-news/0.9}publication_date")
    date_el.text = iso8601(pub_dt)

    title_el = ET.SubElement(news, "{http://www.google.com/schemas/sitemap-news/0.9}title")
    title_el.text = e.title

    count += 1
    if count >= 1000:
        break  # Google News limit per sitemap

tree = ET.ElementTree(urlset)
tree.write("news-sitemap.xml", encoding="utf-8", xml_declaration=True)
print(f"Wrote news-sitemap.xml with {count} items")
