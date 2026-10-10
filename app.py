import time
import pandas as pd
import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

st.set_page_config(page_title="Tour Scraper", layout="centered")
st.title("Tour Data Scraper")

# 1. UI Input Fields
country_url = st.text_input("Target URL", "https://opatrip.com/search-results?q=USA")
country_file_name = st.text_input("Output File Name (without .csv)", "USA_File")

# 2. Action Button
if st.button("Start Scraping"):
    # This status box keeps your teammates updated without looking at a terminal
    with st.status("Initializing scraper...", expanded=True) as status:
        st.write("Configuring headless browser...")
        
        # Streamlit Cloud headless Chrome configuration
        chrome_options = Options()
        chrome_options.binary_location = "/usr/bin/chromium"
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        service = Service("/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=chrome_options)

        try:
            st.write(f"Loading page: {country_url}")
            driver.get(country_url)
            time.sleep(5)

            st.write("Clicking 'Show more' until all tours are loaded...")
            while True:
                try:
                    show_more_btn = driver.find_element(By.XPATH, "//span[contains(text(), 'Show more')]")
                    driver.execute_script("arguments[0].click();", show_more_btn)
                    time.sleep(3)
                except:
                    st.write("No more 'Show more' buttons found. Ready to extract!")
                    break

            st.write("Extracting tour titles and cities...")
            cards = driver.find_elements(By.XPATH, "//a[.//h3[contains(@class, 'font-bold')]]")

            data = []
            for card in cards:
                try:
                    title = card.find_element(By.CSS_SELECTOR, "h3.text-body.font-bold").text.strip()
                    city = card.find_element(By.CSS_SELECTOR, "span.text-sm.text-brand").text.strip()

                    if title:
                        data.append({
                            "Country Name": "USA", # Note: Kept hardcoded per your original script
                            "City Name": city,
                            "Tour Title": title
                        })
                except:
                    continue

            driver.quit()

            # 3. Clean and Export
            if len(data) == 0:
                status.update(label="No data found!", state="error", expanded=False)
                st.error("Could not extract any tours. Check the URL or website structure.")
            else:
                df = pd.DataFrame(data)
                df.drop_duplicates(subset=['Tour Title'], inplace=True)
                
                # Convert DataFrame to CSV string for Streamlit's download button
                csv_data = df.to_csv(index=False).encode('utf-8')
                
                status.update(label=f"Extraction complete! {len(df)} tours found.", state="complete", expanded=False)
                
                # 4. Auto-Download UI
                st.success("Scraping finished successfully!")
                st.download_button(
                    label=f"Download {country_file_name}.csv",
                    data=csv_data,
                    file_name=f"{country_file_name}.csv",
                    mime="text/csv",
                    type="primary"
                )
                
        except Exception as e:
            status.update(label="Scraping failed.", state="error", expanded=False)
            st.error(f"An error occurred: {e}")
            driver.quit()