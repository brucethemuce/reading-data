from storygraph_api import User
import json
import os
from datetime import date

USERNAME = "brucethemuce"
COOKIE = os.environ.get("STORYGRAPH_COOKIE")

if not COOKIE:
    raise RuntimeError("STORYGRAPH_COOKIE is missing")

user = User()
result = user.currently_reading(USERNAME, cookie=COOKIE)

books = []

for item in result:
    # Expected case: dict with title + book_id
    if isinstance(item, dict):
        books.append({
            "title": item.get("title"),
            "book_id": item.get("book_id")
        })

    # Fallback case: plain string
    elif isinstance(item, str):
        books.append({
            "title": item,
            "book_id": None
        })

data = {
    "updated": str(date.today()),
    "books": books
}

with open("current.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
