from storygraph_api import User
import json
import os
from datetime import date
import requests
from bs4 import BeautifulSoup

USERNAME = "brucethemuce"
COOKIE = os.environ.get("STORYGRAPH_COOKIE")

if not COOKIE:
    raise RuntimeError("STORYGRAPH_COOKIE is missing")

user = User()
raw = user.currently_reading(USERNAME, cookie=COOKIE)

if isinstance(raw, str):
    raw = json.loads(raw)

def scrape_book(book_id):
    url = f"https://app.thestorygraph.com/books/{book_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; reading-bot/1.0)"
    }
    html = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html, "html.parser")

    # Title from Open Graph
    og_title = soup.select_one('meta[property="og:title"]')
    title = og_title["content"].strip() if og_title else None

    # Cover from Open Graph
    og_image = soup.select_one('meta[property="og:image"]')
    cover = og_image["content"].strip() if og_image else None

    # Author from description if present
    og_desc = soup.select_one('meta[property="og:description"]')
    author = None
    if og_desc:
        desc = og_desc["content"]
        if "by" in desc:
            author = desc.split("by")[-1].strip()

    return title, author, cover

# ---- Load previous data safely ----
prev_data = {}
if os.path.exists("current.json"):
    try:
        with open("current.json", "r", encoding="utf-8") as f:
            prev_data = json.load(f) or {}
    except (json.JSONDecodeError, ValueError):
        prev_data = {}

prev_ids = [b["book_id"] for b in prev_data.get("books", []) if isinstance(b, dict)]
new_ids  = [b.get("book_id") for b in raw if isinstance(b, dict) and b.get("book_id")]

# ---- If no change, stop ----
if prev_ids == new_ids:
    print("No changes detected. Skipping scraping.")
    exit(0)

# ---- Scrape if changed ----
books = []
for book_id in new_ids:
    title, author, cover = scrape_book(book_id)
    books.append({
        "title": title,
        "author": author,
        "book_id": book_id,
        "cover": cover
    })

data = {
    "updated": str(date.today()),
    "books": books
}

with open("current.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Updated current.json with new books.")
