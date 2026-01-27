def normalize_post(platform, text, url, comments=None, reactions=None):
    return {
        "platform": platform,
        #"id": post_id,
        "text": text,
        #"author": author,
        "url": url,
        "comments": comments or [],
        #"reactions": reactions or {}
    }
