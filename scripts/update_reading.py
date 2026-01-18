import json
import os
from datetime import date
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time

USERNAME = os.environ.get("STORYGRAPH_USERNAME")
COOKIE = os.environ.get("STORYGRAPH_COOKIE")

def currently_reading(uname, cookie):
    url = f"https://app.thestorygraph.com/currently-reading/{uname}"
    return fetch_url(url,cookie)

def fetch_url(url,cookie):
        options = Options()
        options.add_argument("--headless") 
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        if cookie:
            driver.add_cookie({
                'name': 'remember_user_token',
                'value': cookie,
            })
        driver.refresh()
        SCROLL_PAUSE_TIME = 2
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        html_content = driver.page_source
        driver.quit()
        return html_content

def parse_html(html):
    soup = BeautifulSoup(html, "html.parser")
    books = []

    # parse based on alt text inside cover image
    for cover_div in soup.select("div.book-cover"):
        a = cover_div.find("a", href=True)
        img = cover_div.find("img", alt=True, src=True)

        if not a or not img:
            continue

        href = a["href"]
        book_id = href.split("/")[-1]

        alt_text = img["alt"].strip()
        if not alt_text or alt_text == "":
            continue

        # split "Title by Author"
        if " by " not in alt_text:
            continue

        title, author = alt_text.rsplit(" by ", 1)
        title = title.strip()
        author = author.strip()

        if not title or not author:
            continue

        cover = img["src"]

        books.append({
            "title": title,
            "authors": [author],
            "book_id": book_id,
            "cover": cover
        })
        
    # remove duplicates by book_id
    unique_books = []
    seen = set()
    for b in books:
        if b["book_id"] in seen:
            continue
        seen.add(b["book_id"])
        unique_books.append(b)

    return unique_books

if not COOKIE:
    raise RuntimeError("STORYGRAPH_COOKIE is missing")

raw_html = currently_reading(USERNAME, cookie=COOKIE)
books = parse_html(raw_html)

# Load previous data safely
prev_data = {}
if os.path.exists("current.json"):
    try:
        with open("current.json", "r", encoding="utf-8") as f:
            prev_data = json.load(f) or {}
    except (json.JSONDecodeError, ValueError):
        prev_data = {}

prev_ids = [b["book_id"] for b in prev_data.get("books", []) if isinstance(b, dict)]
new_ids = [b.get("book_id") for b in books if isinstance(b, dict) and b.get("book_id")]

# If no change, stop
if prev_ids == new_ids:
    print("No changes detected. Skipping update.")
    exit(0)

# Save current.json
data = {
    "updated": str(date.today()),
    "books": books
}

with open("current.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Updated current.json with new books.")

