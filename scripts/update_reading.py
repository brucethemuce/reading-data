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

# If the library returns a JSON string, parse it
if isinstance(result, str):
    result = json.loads(result)

books = []
for item in result:
    if isinstance(item, dict):
        books.append({
            "title": item.get("title"),
            "book_id": item.get("book_id")
        })
    else:
        books.append({
            "title": str(item),
            "book_id": None
        })

data = {
    "updated": str(date.today()),
    "books": books
}

with open("current.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
