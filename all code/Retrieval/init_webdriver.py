import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options 
import RetriveData as data

class Intialize:
    def __init__(self, driver_path=None):
        # Use default path relative to this file
        # Use absolute path directly to Chrome Web Driver
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        driver_path = driver_path or os.path.join(project_root, "Chrome Web Driver", "chromedriver.exe")

        # Debug log to confirm
        print(f"Using ChromeDriver at: {driver_path}")

        # Chrome options for better automation and fewer interruptions
        options = Options()
        options.add_argument("user-agent=Mozilla/5.0")
        options.add_argument("--log-level=3")  # Only log fatal errors
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-extensions")
        options.add_argument("--start-minimized")
        options.add_argument("--window-position=4000,0")  # Move off screen if needed

        # Start ChromeDriver with these options
        service = Service(driver_path)
        self.driver = webdriver.Chrome(service=service, options=options)

        # Load website and prepare scraping tool
        self.driver.get("https://www.macrotrends.net")
        self.scrape = data.Collect(self.driver)

    def collect(self, stock):
        """Collect data for a single stock name."""
        self.scrape.collect_stock_info(stock)

    def quit(self):
        """Quit the browser session."""
        self.driver.quit()
