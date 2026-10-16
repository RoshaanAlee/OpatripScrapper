import sys
import subprocess
import pandas as pd
import streamlit as st
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

st.set_page_config(page_title="Tour Scraper", layout="centered")
st.title("Tour Data Scraper")

# ---------------------------------------------------------------------------
# Browser setup — runs once per session, cached so it never re-installs
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner="Setting up browser (first run only)...")
def install_playwright_browser():
    """Install Playwright's bundled Chromium with all required system deps."""
    result = subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Playwright browser install failed:\n{result.stderr}"
        )

try:
    install_playwright_browser()
except RuntimeError as e:
    st.error(f"⚠️ Browser setup failed. Please reload the app.\n\n{e}")
    st.stop()

# ---------------------------------------------------------------------------
# UI — inputs
# ---------------------------------------------------------------------------
country_url      = st.text_input("Target URL", "https://opatrip.com/search-results?q=USA")
country_file_name = st.text_input("Output File Name (without .csv)", "USA_File")

# ---------------------------------------------------------------------------
# Scraping logic
# ---------------------------------------------------------------------------
def run_scraper(url: str) -> list[dict]:
    """Open the page, paginate through 'Show more', and return extracted rows."""
    data = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()

        try:
            page.goto(url, timeout=60_000, wait_until="domcontentloaded")
        except PlaywrightTimeoutError:
            raise RuntimeError(
                "The page took too long to load. "
                "Check the URL or try again in a moment."
            )

        # Wait for at least one tour card to appear before proceeding
        try:
            page.wait_for_selector("h3.font-bold", timeout=20_000)
        except PlaywrightTimeoutError:
            raise RuntimeError(
                "No tour cards found on the page. "
                "The URL may be incorrect or the site layout may have changed."
            )

        # Click "Show more" until all tours are loaded
        clicks = 0
        while True:
            try:
                show_more = page.locator("span:text('Show more')")
                if show_more.count() > 0:
                    show_more.first.scroll_into_view_if_needed()
                    show_more.first.click()
                    page.wait_for_timeout(3_000)
                    clicks += 1
                else:
                    break
            except Exception:
                break

        # Extract tour data
        cards = page.locator("a:has(h3.font-bold)")
        count = cards.count()

        for i in range(count):
            try:
                card  = cards.nth(i)
                title = card.locator("h3.text-body.font-bold").text_content(timeout=3_000)
                city  = card.locator("span.text-sm.text-brand").text_content(timeout=3_000)
                if title and title.strip():
                    data.append({
                        "Country Name": "USA",
                        "City Name":    city.strip() if city else "",
                        "Tour Title":   title.strip()
                    })
            except Exception:
                continue

        browser.close()
    return data


# ---------------------------------------------------------------------------
# Action button
# ---------------------------------------------------------------------------
if st.button("Start Scraping"):
    # Clear any previous result
    st.session_state.pop("csv_data",   None)
    st.session_state.pop("tour_count", None)
    st.session_state.pop("file_name",  None)

    if not country_url.strip():
        st.warning("Please enter a Target URL before scraping.")
        st.stop()

    with st.status("Scraping in progress...", expanded=True) as status:
        st.write(f"🌐 Loading: {country_url}")
        st.write("⏳ Clicking 'Show more' to load all tours...")

        try:
            data = run_scraper(country_url)

            if not data:
                status.update(label="No tours found.", state="error", expanded=False)
                st.error(
                    "No tour listings were extracted. "
                    "The URL may not return results, or the page structure may have changed."
                )
            else:
                df = pd.DataFrame(data)
                df.drop_duplicates(subset=["Tour Title"], inplace=True)

                st.session_state["csv_data"]   = df.to_csv(index=False).encode("utf-8")
                st.session_state["tour_count"] = len(df)
                st.session_state["file_name"]  = country_file_name

                status.update(
                    label=f"✅ Done — {len(df)} tours extracted.",
                    state="complete",
                    expanded=False
                )

        except RuntimeError as e:
            # Known, user-friendly errors raised by run_scraper()
            status.update(label="Scraping failed.", state="error", expanded=False)
            st.error(f"❌ {e}")

        except Exception as e:
            # Catch-all for any unexpected error
            status.update(label="Unexpected error.", state="error", expanded=False)
            st.error(
                f"❌ Something unexpected went wrong. "
                f"Please try again or report this:\n\n`{e}`"
            )

# ---------------------------------------------------------------------------
# Download button — always visible after a successful scrape
# ---------------------------------------------------------------------------
if "csv_data" in st.session_state:
    st.success(f"✅ {st.session_state['tour_count']} tours ready for download.")
    st.download_button(
        label=f"⬇️ Download {st.session_state['file_name']}.csv",
        data=st.session_state["csv_data"],
        file_name=f"{st.session_state['file_name']}.csv",
        mime="text/csv",
        type="primary"
    )