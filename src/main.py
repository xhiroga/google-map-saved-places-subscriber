import csv
import logging
import os
import requests
import time

from datetime import datetime
from app import get_new_rows_created_after, scrape_saved_places, upsert_csv

GOOGLE_BLUE = 4359668


def main():
    started_at = datetime.now().isoformat()
    logging.info(f"Started at {started_at}")

    # Read the URLs from the csv file
    with open("./data/urls.csv", "r") as file:
        reader = csv.reader(file)
        urls = [row[0] for row in reader]

    # Loop through the URLs
    for url in urls:
        saved_places = scrape_saved_places(url)
        upsert_csv(saved_places, "./data/saved_places.csv")
        new_rows = get_new_rows_created_after("./data/saved_places.csv", started_at)

        webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
        if not webhook_url:
            logging.error("DISCORD_WEBHOOK_URL is not set")
            exit(1)

        for row in new_rows:
            fields = []
            if row["rating"]:
                fields.append({"name": ":star:評価", "value": row["rating"], "inline": True})
            if row["reviews"]:
                fields.append({"name": ":speech_balloon:クチコミ", "value": row["reviews"], "inline": True})

            payload = {
                "content": "新しい場所が追加されました！",
                "username": "Google Map",
                "avatar_url": "https://blog.gisplanning.com/hs-fs/hubfs/GoogleMaps-Icon-alone-1.png",
                "embeds": [
                    {
                        "title": row["store_name"],
                        "description": row["memo"],
                        "url": row["url"],
                        "color": GOOGLE_BLUE,
                        "fields": fields,
                    }
                ],
            }
            response = requests.post(webhook_url, json=payload)
            if response.status_code >= 400:
                logging.error(
                    f"Failed to post to Discord. Status code: {response.status_code}, message: {response.text}"
                )
            time.sleep(1)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    while True:
        main()
        time.sleep(300)
