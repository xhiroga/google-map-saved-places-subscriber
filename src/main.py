import csv
import logging
import os
import requests
import time

from datetime import datetime
from app import get_new_places_created_after, scrape_saved_places, upsert_csv

GOOGLE_BLUE = 4359668


def main():
    # Read the URLs from the csv file
    with open("./data/urls.csv", "r") as file:
        reader = csv.reader(file)
        urls = [row[0] for row in reader]

    # Loop through the URLs
    for url in urls:
        started_at = datetime.now().isoformat()
        logging.info(f"Started at {started_at}")

        saved_places = scrape_saved_places(url)
        upsert_csv(saved_places, "./data/saved_places.csv")
        new_places = get_new_places_created_after("./data/saved_places.csv", started_at)
        logging.info(f"New places: {new_places}")

        webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
        if not webhook_url:
            logging.error("DISCORD_WEBHOOK_URL is not set")
            exit(1)

        for place in new_places:
            fields = []
            if place["rating"]:
                fields.append(
                    {"name": ":star:評価", "value": place["rating"], "inline": True}
                )
            if place["reviews"]:
                fields.append(
                    {
                        "name": ":speech_balloon:クチコミ",
                        "value": place["reviews"],
                        "inline": True,
                    }
                )

            payload = {
                "content": f"{place['store_name']}が追加されました！",
                "username": "Google Map",
                "avatar_url": "https://blog.gisplanning.com/hs-fs/hubfs/GoogleMaps-Icon-alone-1.png",
                "embeds": [
                    {
                        "title": place["store_name"],
                        "description": place["memo"],
                        "url": place["url"],
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
