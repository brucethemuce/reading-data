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
    html = requests.get(url).text
    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.select_one("h1")
    title = title_tag.text.strip() if title_tag else None

    author_tag = soup.select_one("a[href*='/authors/']")
    author = author_tag.text.strip() if author_tag else None

    cover_tag = soup.select_one("img[src*='cover']")
    cover = cover_tag["src"] if cover_tag else None

    return title, author, cover

# ---- Load previous data safely ----
prev_data = {}
if os.path.exists("current.json"):
    try:
        with open("current.json", "r", encoding="utf-8") as f:
            prev_data = json.load(f) or {}
    except (json.JSONDecodeError, ValueError):
        # If file is corrupted or empty, just rebuild it
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
