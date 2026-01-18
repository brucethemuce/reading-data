from storygraph_api import User, Book
import json
import os
from datetime import date

USERNAME = "brucethemuce"
COOKIE = os.environ.get("STORYGRAPH_COOKIE")

if not COOKIE:
    raise RuntimeError("STORYGRAPH_COOKIE is missing")

user = User()
raw = user.currently_reading(USERNAME, cookie=COOKIE)

# If the library returns a JSON string, parse it
if isinstance(raw, str):
    raw = json.loads(raw)

# Load previous data safely
prev_data = {}
if os.path.exists("current.json"):
    try:
        with open("current.json", "r", encoding="utf-8") as f:
            prev_data = json.load(f) or {}
    except (json.JSONDecodeError, ValueError):
        prev_data = {}

prev_ids = [b["book_id"] for b in prev_data.get("books", []) if isinstance(b, dict)]
new_ids = [b.get("book_id") for b in raw if isinstance(b, dict) and b.get("book_id")]

# If no change, stop
if prev_ids == new_ids:
    print("No changes detected. Skipping update.")
    exit(0)

# Fetch metadata using Book().book_info()
book_api = Book()
books = []

for item in raw:
    if not isinstance(item, dict):
        continue

    book_id = item.get("book_id")
    title = item.get("title")

    if not book_id or not title:
        continue

    authors = None
    try:
        details = book_api.book_info(book_id)
        if isinstance(details, str):
            details = json.loads(details)

        authors = details.get("authors")

    except Exception as e:
        authors = None

    books.append({
        "title": title,
        "book_id": book_id,
        "authors": authors
    })

# Save current.json
data = {
    "updated": str(date.today()),
    "books": books
}

with open("current.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Updated current.json with new books.")
