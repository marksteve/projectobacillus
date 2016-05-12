#!./venv/bin/python
import json
import os
import sys

import pytumblr
import requests
from tqdm import tqdm


def get_creds():
    for key in [
        "CONSUMER_KEY",
        "CONSUMER_SECRET",
        "TOKEN",
        "TOKEN_SECRET",
    ]:
        yield os.environ["TUMBLR_" + key]


def download_gif(gif):
    url = gif["original_size"]["url"]
    output = os.path.join("gifs", os.path.basename(url))
    resp = requests.get(url, stream=True)
    if resp.status_code == 200:
        with open(output, 'wb') as f:
            for chunk in resp.iter_content(1024):
                f.write(chunk)


def get_gifs(client):
    offset = 0
    total = 0
    while True:
        resp = client.posts("protobacillus", type="photo", tag="gif",
                            offset=offset)
        posts = resp["posts"]
        if not total:
            total = resp["total_posts"]
            pbar = tqdm(total=total, unit="gif")
        if not posts:
            return
        for post in posts:
            for gif in post["photos"]:
                pbar.update(1)
                download_gif(gif)
                yield gif
        offset += len(posts)
    pbar.close()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        command = "serve"
    if len(sys.argv) == 2:
        command = sys.argv[1]
    if command == "fetch":
        client = pytumblr.TumblrRestClient(*get_creds())
        metadata = os.path.join("gifs", "metadata.json")
        with open(metadata, "wb") as f:
            f.write(json.dumps([
                gif for gif in get_gifs(client)
            ]))
    elif command == "serve":
        print "serve"
    else:
        raise RuntimeError("Invalid command")

