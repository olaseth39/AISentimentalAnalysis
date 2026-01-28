import requests
from bs4 import BeautifulSoup
from  normalize import normalize_post
import os
import dotenv
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from apify_client import ApifyClient
import json

load_dotenv()

GOOGLE_API_KEY = os.getenv("google_api")
GOOGLE_CX = os.getenv("google_cx")
APIFY_TOKEN = os.getenv("APIFY_TOKEN")

#print(GOOGLE_API_KEY)

client = ApifyClient(APIFY_TOKEN)

# let's create a function to scrape the comment and reactions from a given page url
# it will be base n the function we have for youtube, linkedin, instagram etc
def scrape_comment(site, url):
    comments = []
    
    # youtube
    # Prepare the Actor input
    if site == "youtube.com":
        run_input = {
            "startUrls": [{ "url": url}],
            "maxComments": 1,
            "commentsSortBy": "1",
        }

        # Run the Actor and wait for it to finish
        run = client.actor("p7UMdpQnjKmmpR21D").call(run_input=run_input)

        # Fetch and print Actor results from the run's dataset (if there are any)
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            comments.append(item['comment'])
            #print(item['comment'])
            
    if site == "linkedin.com":
        # linkedin
        run = client.actor("supreme_coder/linkedin-post").call(   #curious_coder/linkedin-comment-scraper if that doesn't work
            run_input={
                "urls": [
                    url
                ],
                "maxPosts": 1,
                "proxyConfiguration": {"useApifyProxy": True}
            }
        )

        # Fetch and print Actor results from the run's dataset (if there are any)
        dataset_id = run["defaultDatasetId"]
        items = client.dataset(dataset_id).list_items().items
        #print(items)
        comments = [item['comments'] for item in items]
        texts = [comment['text'] for n in range(len(comments)) for comment in comments[n]]
        comments.append(texts)
            
    if site == "instagram.com/p":
        # Instagram
        # Prepare the Actor input
        run_input = {
            "directUrls": [
                url
            ],
            "resultsLimit": 1,
            "isNewestComments": True,
            "includeNestedComments": True,
        }
        #print(url)
        # Run the Actor and wait for it to finish
        run = client.actor("SbK00X0JYCPblD2wp").call(run_input=run_input)

        # Fetch and print Actor results from the run's dataset (if there are any)
        dataset_id = run["defaultDatasetId"]
        items = client.dataset(dataset_id).list_items().items
        for item in client.dataset(run["defaultDatasetId"]).iterate_items():
            comments.append(item["text"])
        
        # for reddit
        if site == "reddit.com":
            # Prepare the Actor input
            run_input = {
                "postUrls": [
                    url
                ],
                "maxComments": 1,
                "expandThreads": True,
            }

            # Run the Actor and wait for it to finish
            run = client.actor("uRbeKXtKIZtufw8cw").call(run_input=run_input)

            # Fetch and print Actor results from the run's dataset (if there are any)
            for item in client.dataset(run["defaultDatasetId"]).iterate_items():
                comments.append(item['comment'])
                #print(item)
                
        # for facebook
        if site == "facebook.com":
            run_input = {
            "startUrls": [{ "url": url }],
            "resultsLimit": 1,
            "includeNestedComments": True,
            "viewOption": "RANKED_UNFILTERED",
        }

            # Run the Actor and wait for it to finish
            run = client.actor("us5srxAYnsrkgUv2v").call(run_input=run_input)
            
            # Fetch and print Actor results from the run's dataset (if there are any)
            for item in client.dataset(run["defaultDatasetId"]).iterate_items():
                comments.append(item['text'])
            
    return comments


def google_search(query, site=None):
    q = f"{query} site:{site}" if site else query
    url = f"https://www.googleapis.com/customsearch/v1?q={q}&key={GOOGLE_API_KEY}&cx={GOOGLE_CX}"

    response = requests.get(url)
    if response.status_code == 200:
        items = response.json().get("items", [])
        results = []
        for i in items:
            link = i.get("link")
            #print("Link:", link)
            snippet = i.get("snippet")
            # scrape comments/reactions from the link
            comments = scrape_comment(site, link)
            results.append(
                normalize_post(
                    platform=site or "google",
                    #post_id=link,
                    text=snippet,
                    #author=None,
                    url=link,
                    comments=comments,
                )
            )
            
            # save a copy of the results to a json file
            with open("all_comments.json", "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
                
        return results
    return []

