from storygraph_api import User
import json
import os
from datetime import date

USERNAME = "brucethemuce"
COOKIE = os.environ["STORYGRAPH_COOKIE"]

user = User()
books = user.currently_reading(USERNAME, cookie=COOKIE)

data = {
    "updated": str(date.today()),
    "books": [
        {
            "title": b.get("title"),
            "author": b.get("author")
        }
        for b in books
    ]
}

with open("current.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
