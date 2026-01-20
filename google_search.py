import requests
from bs4 import BeautifulSoup
from  normalize import normalize_post
import os
import dotenv
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("google_api")
GOOGLE_CX = os.getenv("google_cx")

#print(GOOGLE_API_KEY)

def google_search(query, site=None):
    q = f"{query} site:{site}" if site else query
    url = f"https://www.googleapis.com/customsearch/v1?q={q}&key={GOOGLE_API_KEY}&cx={GOOGLE_CX}"

    response = requests.get(url)
    if response.status_code == 200:
        items = response.json().get("items", [])
        results = []
        for i in items:
            link = i.get("link")
            snippet = i.get("snippet")
            # scrape comments/reactions from the link
            comments, reactions = scrape_page(link)
            results.append(
                normalize_post(
                    platform=site or "google",
                    post_id=link,
                    text=snippet,
                    author=None,
                    url=link,
                    comments=comments,
                    reactions=reactions
                )
            )
        return results
    return []

def scrape_page(url):
    """
    Basic scraper to extract comments/reactions.
    This is site-specific and may need adjustments.
    """
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")

        # Example: find comments
        comments = [c.get_text(strip=True) for c in soup.find_all("div", class_="comment")]

        # Example: find reactions (likes/shares)
        reactions = {}
        likes = soup.find("span", class_="like-count")
        shares = soup.find("span", class_="share-count")
        if likes: reactions["likes"] = likes.get_text(strip=True)
        if shares: reactions["shares"] = shares.get_text(strip=True)

        return comments, reactions
    except Exception as e:
        return [], {}
