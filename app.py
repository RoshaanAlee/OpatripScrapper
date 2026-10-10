import sys
import subprocess
import pandas as pd
import streamlit as st
from playwright.sync_api import sync_playwright

st.set_page_config(page_title="Tour Scraper", layout="centered")
st.title("Tour Data Scraper")

@st.cache_resource
def install_playwright_browser():
    """Install Playwright's bundled Chromium (runs once, cached for the session)."""
    subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        check=True,
        capture_output=True
    )

install_playwright_browser()

# 1. UI Input Fields
country_url = st.text_input("Target URL", "https://opatrip.com/search-results?q=USA")
country_file_name = st.text_input("Output File Name (without .csv)", "USA_File")

# 2. Action Button
if st.button("Start Scraping"):
    # Clear any previous result when a new scrape starts
    st.session_state.pop("csv_data", None)
    st.session_state.pop("tour_count", None)

    with st.status("Initializing scraper...", expanded=True) as status:
        st.write("Configuring headless browser...")

        try:
            st.write(f"Loading page: {country_url}")
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(country_url, timeout=60000)
                page.wait_for_timeout(5000)

                st.write("Clicking 'Show more' until all tours are loaded...")
                while True:
                    try:
                        show_more = page.locator("span:text('Show more')")
                        if show_more.count() > 0:
                            show_more.first.click()
                            page.wait_for_timeout(3000)
                        else:
                            st.write("No more 'Show more' buttons found. Ready to extract!")
                            break
                    except Exception:
                        st.write("No more 'Show more' buttons found. Ready to extract!")
                        break

                st.write("Extracting tour titles and cities...")
                cards = page.locator("a:has(h3.font-bold)")
                count = cards.count()

                data = []
                for i in range(count):
                    try:
                        card = cards.nth(i)
                        title = card.locator("h3.text-body.font-bold").text_content()
                        city  = card.locator("span.text-sm.text-brand").text_content()
                        if title and title.strip():
                            data.append({
                                "Country Name": "USA",  # Note: kept per original script
                                "City Name": city.strip() if city else "",
                                "Tour Title": title.strip()
                            })
                    except Exception:
                        continue

                browser.close()

            # 3. Clean and store result in session state
            if len(data) == 0:
                status.update(label="No data found!", state="error", expanded=False)
                st.error("Could not extract any tours. Check the URL or website structure.")
            else:
                df = pd.DataFrame(data)
                df.drop_duplicates(subset=['Tour Title'], inplace=True)

                # Store in session state so the button renders outside this block
                st.session_state["csv_data"]   = df.to_csv(index=False).encode('utf-8')
                st.session_state["tour_count"] = len(df)
                st.session_state["file_name"]  = country_file_name

                status.update(
                    label=f"Extraction complete! {len(df)} tours found.",
                    state="complete",
                    expanded=False
                )

        except Exception as e:
            status.update(label="Scraping failed.", state="error", expanded=False)
            st.error(f"An error occurred: {e}")

# 4. Download button — rendered outside st.status so it's always visible after scraping
if "csv_data" in st.session_state:
    st.success(f"✅ {st.session_state['tour_count']} tours extracted successfully!")
    st.download_button(
        label=f"⬇️ Download {st.session_state['file_name']}.csv",
        data=st.session_state["csv_data"],
        file_name=f"{st.session_state['file_name']}.csv",
        mime="text/csv",
        type="primary"
    )