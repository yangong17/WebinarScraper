# Webinar Aggregation Agent

An automated agent that collects webinar information from multiple providers, normalizes the data, and stores it in a local SQLite database.

## Providers

- **Syndio** - Resources/webinars from synd.io
- **WorldatWork** - Public on-demand webinars (excludes member-exclusive)
- **Pave** - Events and webinars from pave.com

## Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Unix/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Run Manually

```bash
python src/main.py
```

### Output

- **Database**: `data/webinars.db` (SQLite)
- **Logs**: `logs/scraper_YYYYMMDD.log`

## Database Schema

| Column | Type | Description |
|--------|------|-------------|
| provider | TEXT | Source provider name |
| title | TEXT | Webinar title |
| webinar_type | TEXT | "Upcoming" or "On Demand" |
| date_str | TEXT | Original date string |
| date_iso | TEXT | ISO formatted date |
| available_until | TEXT | Expiration date (on-demand) |
| detail_link | TEXT | URL to webinar page |
| registration_info | TEXT | Registration URL |
| status | TEXT | "Active" or "Removed" |
| last_updated | TEXT | Last seen timestamp |

## Adding New Providers

1. Create a new collector in `src/collectors/`
2. Extend `BaseCollector`
3. Implement the `collect()` method
4. Register in `src/collectors/__init__.py`
5. Add to the collectors list in `src/main.py`

## GitHub Actions

The workflow runs daily at 6:00 AM UTC. See `.github/workflows/daily_scrape.yml`.

## Project Structure

```
WebinarScraper/
├── .github/workflows/
│   └── daily_scrape.yml
├── data/
│   └── webinars.db
├── logs/
├── src/
│   ├── collectors/
│   │   ├── base.py
│   │   ├── syndio.py
│   │   ├── worldatwork.py
│   │   └── pave.py
│   ├── database/
│   │   ├── db_manager.py
│   │   └── models.py
│   ├── utils/
│   │   └── logger.py
│   └── main.py
├── requirements.txt
└── README.md
```
