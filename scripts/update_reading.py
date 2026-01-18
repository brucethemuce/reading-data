from storygraph_api import User
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

books = []
for item in raw:
    # Only proceed if we have a book_id
    book_id = item.get("book_id") if isinstance(item, dict) else None

    title = item.get("title") if isinstance(item, dict) else str(item)

    author = None
    cover = None

    if book_id:
        try:
            details = user.book(book_id, cookie=COOKIE)
            # Sometimes details is string JSON
            if isinstance(details, str):
                details = json.loads(details)

            # Pick the first author name
            author_list = details.get("authors") or []
            author = author_list[0] if author_list else None

            # Cover image
            cover = details.get("cover_image_url")

        except Exception as e:
            author = None
            cover = None

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
