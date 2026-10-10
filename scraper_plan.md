# Goal
Convert a working Python Colab scraper into a Streamlit Community Cloud web app.

# UI Requirements
- Single-page web interface.
- Two input fields: Target URL and Output File Name.
- One action button to start scraping.
- One download button to serve the resulting CSV.

# Files to Generate
1. `app.py`: The main Streamlit app.
2. `requirements.txt`: Python dependencies (e.g., streamlit, selenium, pandas).
3. `packages.txt`: System dependencies (`chromium` and `chromium-driver` for headless Selenium).