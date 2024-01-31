import csv

from src.app import scrape_saved_places, upsert_csv

# Read the URLs from the csv file
with open('./data/urls.csv', 'r') as file:
    reader = csv.reader(file)
    urls = [row[0] for row in reader]

# Loop through the URLs
for url in urls:
    saved_places = scrape_saved_places(url)
    upsert_csv(saved_places, './data/saved_places.csv')
