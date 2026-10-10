# OpaTrip Scraper

A **Streamlit** web app that scrapes tour listings from [opatrip.com](https://opatrip.com) using headless Chrome (Selenium), and lets you download the results as a CSV file — all from a simple browser UI.

## Features

- 🔗 Enter any OpaTrip search URL (e.g., by country or region)
- 🖱️ Automatically clicks "Show more" to load all paginated results
- 📋 Extracts **tour titles** and **city names**
- 📥 One-click CSV download directly from the browser
- ☁️ Ready to deploy on **Streamlit Community Cloud**

## Screenshot

> _Launch the app and enter a URL to start scraping._

## Tech Stack

| Tool | Purpose |
|------|---------|
| [Streamlit](https://streamlit.io) | Web UI |
| [Selenium](https://selenium-python.readthedocs.io) | Headless browser automation |
| [Pandas](https://pandas.pydata.org) | Data processing & CSV export |
| Chromium | Headless browser (via `packages.txt`) |

## Getting Started

### Prerequisites

- Python 3.9+
- Google Chrome / Chromium installed locally

### Installation

```bash
git clone https://github.com/RoshaanAlee/OpatripScrapper.git
cd OpatripScrapper
pip install -r requirements.txt
```

### Run Locally

```bash
streamlit run app.py
```

### Deploy to Streamlit Community Cloud

1. Fork or push this repo to your GitHub account.
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your repo.
3. The `packages.txt` file automatically installs `chromium` and `chromium-driver` on the cloud.

## Project Structure

```
OpatripScrapper/
├── app.py            # Main Streamlit application
├── requirements.txt  # Python dependencies
├── packages.txt      # System dependencies (Chromium for headless Selenium)
└── README.md
```

## Usage

1. Open the app in your browser.
2. Paste an OpaTrip search URL (e.g., `https://opatrip.com/search-results?q=USA`).
3. Enter a name for the output CSV file.
4. Click **Start Scraping** — the app will auto-scroll and collect all tours.
5. Click **Download CSV** to save the results.

## License

MIT
