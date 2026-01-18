from storygraph_api import User
import json
import os
from datetime import date
import requests

USERNAME = "brucethemuce"
COOKIE = os.environ.get("STORYGRAPH_COOKIE")

if not COOKIE:
    raise RuntimeError("STORYGRAPH_COOKIE is missing")

user = User()
raw = user.currently_reading(USERNAME, cookie=COOKIE)

if isinstance(raw, str):
    raw = json.loads(raw)

def get_book_metadata(book_id):
    url = f"https://app.thestorygraph.com/api/books/{book_id}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "cookie": COOKIE
    }
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.json()

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

# ---- Fetch metadata if changed ----
books = []
for book_id in new_ids:
    meta = get_book_metadata(book_id)

    books.append({
        "title": meta.get("title"),
        "author": meta.get("author"),
        "book_id": book_id,
        "cover": meta.get("cover_image_url")
    })

data = {
    "updated": str(date.today()),
    "books": books
}

with open("current.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Updated current.json with new books.")
