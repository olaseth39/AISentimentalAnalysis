from fastapi import FastAPI
from google_search import google_search

app = FastAPI()

@app.get("/search")
def search(query: str):
    results = []

    # LinkedIn via Google
    results.extend(google_search(query, site="linkedin.com"))

    # Twitter via Google
    results.extend(google_search(query, site="twitter.com"))

    # Reddit via Google
    results.extend(google_search(query, site="reddit.com"))

    # YouTube via Google
    results.extend(google_search(query, site="youtube.com"))

    # Facebook via Google
    results.extend(google_search(query, site="facebook.com"))

    # Instagram via Google
    results.extend(google_search(query, site="instagram.com/p"))
    
    # Instagram via Google
    #results.extend(google_search(query, site="medium.com"))

    return {"query": query, "results": results}
