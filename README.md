# google-map-saved-places-subscriber

Scrape google map saved places and save to csv file.

## Debug in local

To show browser window, run on local.

```powershell
# Enable python virtual environment
# like `source venv/bin/activate` or `conda activate playwright-python`
```

```powershell
.\start_dev.bat
```

## Run

Scrape google map saved places, save to csv file and send to Discord.

```bash
touch ./data/urls.csv # Add urls to scrape
docker-compose up --build
```
