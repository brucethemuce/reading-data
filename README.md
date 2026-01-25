# Story Graph HTML Reader
This scrapes the html of a users storygraph `currently reading' page, grabs the book titles, authors, and link to the cover image and dumps it in a json file. 
It updates once a day via github actions and a cron job.
You can then reference that json file from your own website for displaying.

I found a (mostly broken) unofficial storygraph "api", but digging through the source its really an overly complicated html scraper that hasn't been updated to work with the sites current format, and so it returns a bunch of nulls. So I redid it and made my own.

## How To
To use this you'll have to do a few things.
1. ~~Clone~~ Fork the repo and make it public. (Dont just clone it, I dont want your book info)
2. On github actions, ensure that the main branch is selected. Also change the action settings to allow the bot to read/write. This is under Action settings -> general.
3. Set two new secrets (under settings -> security -> secrets and variables -> actions). The first is STORYGRAPH_COOKIE, the second is STORYGRAPH_USERNAME. The cookie you get from logging in to your storygraph profile, hit F12, then go to storage. There will be a cookie called "remember_user_token", copy that bad boy over as the cookie secret. Do NOT hardcode it into the python file, someone *could* use it to login as you and takeover your account.
4. Force a run of the action to verify its all good and current.json gets updated to your stuff.
5. Setup a github "pages", the .io domain thing. Settings -> pages and select the branch you want.
6. Reference the .json file on the .io page to display it on your personal website

To put it on your site you can do something like the below (what I did). This will display the books as covers with the title and author(s) below it. 

Enjoy!  

Source for displaying:
```
## Currently Reading

<ul id="reading-list">
  <li>Loading…</li>
</ul>

<script>
fetch("https://yourgithubusername.github.io/reading-data/current.json")
  .then(r => r.json())
  .then(data => {
    document.getElementById("reading-list").innerHTML =
      data.books
        .map(b => `
          <li class="book-item">
            <img src="${b.cover}" alt="${b.title} by ${b.authors}" />
            <div class="book-info">
              <strong>${b.title}</strong>
              <div class="author">${b.authors}</div>
            </div>
          </li>
        `)
        .join("");
  })
  .catch(() => {
    document.getElementById("reading-list").innerHTML =
      "<li>Unable to load reading list.</li>";
  });
</script>

<style>
  #reading-list {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    list-style: none;
    padding: 0;
    margin: 0;
    justify-content: center;
  }

  .book-item {
    width: 140px;
    text-align: center;
  }

  .book-item img {
    width: 100%;
    height: auto;
    border-radius: 0; /* removed rounded corners */
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
  }

  .book-info {
    margin-top: 8px;
    font-size: 14px;
  }

  .author {
    margin-top: 4px;
    font-size: 13px;
  }
</style>
```

## How it works
The book info inside the currently reading page's html is kind of sporadic. And not consistent between books in a series and standalones. But what is consistent is the alt-text of the book covers. The script parses that into useful text, and also grabs the image's url.

A webcrawler will go to the user's profile (accessible only with the cookie, profiles arent public without a signin), grab the html, parse it, dump it in the json, add a commit and push it to main.

The crawler will run once a day at 0600 UTC, check for differences in the json, write if there was any changes, then exit. 

## Disclaimer
I am not responsible if your account gets comprised or for any other possible damage caused by the use of this code. Use at your own risk.
