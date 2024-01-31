# google-map-saved-places-subscriber

Scrape google map saved places and save to csv file.

## Debug on local

To show browser window, run on local.

```powershell
# Enable python virtual environment
# like `source venv/bin/activate` or `conda activate playwright-python`
```

```powershell
.\start_dev.bat
```

## Debug on Dev Container

To use breakpoint, run on Dev Container.

- `Dev Containers: Reopen in Container`
- Open python file
- Hit `Run and Debug`

## Run

Scrape google map saved places, save to csv file and send to Discord.

```bash
touch ./data/urls.csv # Add urls to scrape
touch .env # Add DISCORD_WEBHOOK_URL
docker compose up --build
```
