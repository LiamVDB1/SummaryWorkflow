#https://x.com/i/broadcasts/1mrGmMNdNWBGy

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import json

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (optional)
chrome_options.add_argument("--enable-logging")
chrome_options.add_argument("--v=1")
chrome_options.add_argument("--log-level=0")

# Enable performance logging
chrome_options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

# Initialize the Chrome driver with WebDriver Manager
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

# Visit the target webpage
driver.get("https://x.com/i/broadcasts/1mrGmMNdNWBGy")

# Retrieve the performance logs (includes network requests)
logs = driver.get_log("performance")

# Parse the logs to extract .m3u8 file requests
m3u8_urls = []
for log in logs:
    log_json = json.loads(log["message"])["message"]
    if log_json["method"] == "Network.responseReceived":
        url = log_json["params"]["response"]["url"]
        if ".m3u8" in url:
            m3u8_urls.append(url)

# Print the extracted .m3u8 URLs
for url in m3u8_urls:
    print("Found .m3u8 URL:", url)

# Quit the driver when done
driver.quit()