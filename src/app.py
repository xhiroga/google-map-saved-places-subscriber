import csv
import logging
import os
import time
from datetime import datetime

from playwright.sync_api import sync_playwright


CSS_LIST_CLASS = ".m6QErb.DxyBCb.kA9KIf.dS8AEf.ussYcc"
CSS_PLACES_CLASS = ".BsJqK.xgHk6"
CSS_PLACE_NAME_CLASS = ".fontHeadlineSmall"
CSS_RATING_CLASS = ".MW4etd"
CSS_REVIEWS_CLASS = ".UY7F9"
CSS_MEMO_CLASS = ".dWzgKe"

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s")


def _navigate_to_url_with_retry(page, url):
    max_retry_count = 5
    initial_wait_time = 60

    retry_count = 0
    wait_time = initial_wait_time

    while retry_count < max_retry_count:
        try:
            page.goto(url)
            break
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            retry_count += 1
            if retry_count < max_retry_count:
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                wait_time *= 2
            else:
                print("Max retry count reached. Exiting...")
                raise


def scrape_saved_places(url: str):
    with sync_playwright() as p:
        headless = not os.getenv("PLAYWRIGHT_SHOW_BROWSER")
        browser = p.chromium.launch(headless=headless)
        page = browser.new_page()

        _navigate_to_url_with_retry(page, url)

        places = []
        while True:
            loaded_places = page.query_selector_all(CSS_PLACES_CLASS)
            if len(places) == len(loaded_places):
                break
            places = loaded_places
            page.focus(CSS_LIST_CLASS)
            page.keyboard.press("End")
            time.sleep(3)

        extracted_data = []

        for place in places:
            logging.debug(place.inner_html())

            place_name = (
                place.query_selector(CSS_PLACE_NAME_CLASS).inner_text()
                if place.query_selector(CSS_PLACE_NAME_CLASS)
                else None
            )
            rating = (
                place.query_selector(CSS_RATING_CLASS).inner_text()
                if place.query_selector(CSS_RATING_CLASS)
                else None
            )
            reviews = (
                place.query_selector(CSS_REVIEWS_CLASS).inner_text()
                if place.query_selector(CSS_REVIEWS_CLASS)
                else None
            )
            memo = (
                place.query_selector(CSS_MEMO_CLASS).inner_text()
                if place.query_selector(CSS_MEMO_CLASS)
                else None
            )

            if place_name is None:
                continue

            extracted_data.append(
                {
                    "url": url,
                    "store_name": place_name,
                    "rating": rating,
                    "reviews": reviews,
                    "memo": memo,
                }
            )

        browser.close()
        return extracted_data


def upsert_csv(places, file_path):
    timestamp = datetime.now().isoformat()
    rows = []

    if not os.path.exists(file_path):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        open(file_path, "w", encoding="utf-8").close()

    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    for place in places:
        url = place["url"]
        store_name = place["store_name"]
        found = False

        for row in rows:
            if row["url"] == url and row["store_name"] == store_name:
                row["updated_at"] = timestamp
                row["rating"] = place["rating"]
                row["reviews"] = place["reviews"]
                row["memo"] = place["memo"]
                found = True
                break

        if not found:
            new_row = {
                "url": url,
                "store_name": store_name,
                "rating": place["rating"],
                "reviews": place["reviews"],
                "memo": place["memo"],
                "created_at": timestamp,
                "updated_at": timestamp,
            }
            rows.append(new_row)

    with open(file_path, "w", encoding="utf-8", newline="") as file:
        fieldnames = [
            "url",
            "store_name",
            "rating",
            "reviews",
            "memo",
            "created_at",
            "updated_at",
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def get_new_places_created_after(file_path, started_at: str):
    with open(file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        places = list(reader)

    return [place for place in places if place["created_at"] > started_at]


if __name__ == "__main__":
    shared_link = "https://maps.app.goo.gl/WmESh8s9xbPnkfPV7"
    file_path = "./data/saved_places_dev.csv"

    logging.getLogger().setLevel(logging.DEBUG)
    started_at = datetime.now().isoformat()
    saved_places = scrape_saved_places(shared_link)
    upsert_csv(saved_places, file_path)
    new_places = get_new_places_created_after(file_path, started_at)
    logging.info(f"New rows: {new_places}")
