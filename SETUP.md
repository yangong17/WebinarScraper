# Webinar Scraper - Setup Guide

## Quick Start (Local)

```bash
# Activate virtual environment
.\venv\Scripts\activate

# Run the scraper
python src/main.py
```

---

## GitHub Actions + Coda Integration

### Step 1: Create Your Coda Table

1. Go to [coda.io](https://coda.io) and create a new document (or use existing)
2. Create a table with these **exact column names**:
   - `Source` (Text)
   - `Title` (Text)
   - `Air Date` (Text)
   - `Link` (URL)

### Step 2: Get Your Coda API Token

1. Go to [Coda Account Settings](https://coda.io/account)
2. Scroll to **API Settings**
3. Click **Generate API Token**
4. Copy and save the token securely

### Step 3: Get Your Document and Table IDs

**Document ID:**
- Look at your Coda doc URL: `https://coda.io/d/Your-Doc-Name_dXXXXXXXXXX`
- The Document ID is the part after `_d` → `XXXXXXXXXXX`

**Table ID:**
- Click on your table, look at the URL: `...#_tXXXXXX`
- The Table ID is `XXXXXX` (can also use the table name like `grid-1`)
- Or right-click table → Copy table ID

### Step 4: Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/WebinarScraper.git
git push -u origin main
```

### Step 5: Add GitHub Secrets

1. Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** and add:

| Secret Name | Value |
|-------------|-------|
| `CODA_API_TOKEN` | Your Coda API token |
| `CODA_DOC_ID` | Your Document ID (e.g., `abc123XYZ`) |
| `CODA_TABLE_ID` | Your Table ID or name (e.g., `grid-1` or `tbl123`) |

### Step 6: Test the Workflow

1. Go to **Actions** tab in your GitHub repo
2. Click **Daily Webinar Scrape** workflow
3. Click **Run workflow** → **Run workflow**
4. Watch the logs to verify it works

---

## Schedule

The workflow runs automatically at **6 AM UTC daily** (10 PM PST / 2 AM EST).

To change the schedule, edit `.github/workflows/daily_scrape.yml`:
```yaml
schedule:
  - cron: '0 6 * * *'  # Change this cron expression
```

Common schedules:
- `0 6 * * *` = 6 AM UTC daily
- `0 14 * * *` = 6 AM PST daily (2 PM UTC)
- `0 6 * * 1` = 6 AM UTC every Monday

---

## Local Testing with Coda

To test Coda export locally:

```powershell
$env:CODA_API_TOKEN = "your-token-here"
$env:CODA_DOC_ID = "your-doc-id"
$env:CODA_TABLE_ID = "your-table-id"
python src/main.py
```

---

## Troubleshooting

**"Missing required environment variables"**
- Ensure all three secrets are set in GitHub

**"401 Unauthorized"**
- Your Coda API token may be invalid or expired
- Generate a new token at [coda.io/account](https://coda.io/account)

**"404 Not Found"**
- Check your Document ID and Table ID are correct
- Ensure the table exists in the document

**"Column not found"**
- Ensure your Coda table has columns named exactly: `Source`, `Title`, `Air Date`, `Link`
