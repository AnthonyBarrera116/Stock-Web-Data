# Libraries
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

# Program to remove/click ads
import AdRemoval as a

# Tools class for interacting with charts and HTML page
class Tools:

    # Initialize with Selenium driver and ad removal handler
    def __init__(self, driver):
        self.driver = driver
        self.removal = a.Remove(self.driver)

    # Check if string matches YYYY-MM-DD date format
    def looks_like_date(self, s):
        return bool(re.match(r'^\d{4}-\d{2}-\d{2}$', s))

    # Extract visible table headers and data rows from financial chart
    def extract_grid_data(self):
        headers = [
            h.text.strip()
            for h in self.driver.find_elements(By.CSS_SELECTOR, "#jqxgrid .jqx-grid-column-header span")
        ]
        rows = [
            [cell.text.strip() for cell in row.find_elements(By.CSS_SELECTOR, "div[role='gridcell']")]
            for row in self.driver.find_elements(By.CSS_SELECTOR, "#jqxgrid .jqx-grid-content div[role='row']")
        ]
        return headers, rows

    # Get X position of the horizontal scrollbar thumb
    def get_scrollbar_thumb_x(self):
        try:
            thumb = self.driver.find_element(By.ID, "jqxScrollThumbhorizontalScrollBarjqxgrid")
            return thumb.location['x']
        except Exception:
            return None

    # Drag the horizontal scrollbar thumb by a specified pixel amount
    def drag_scrollbar(self, scroll_amount=50):
        try:
            thumb = self.driver.find_element(By.ID, "jqxScrollThumbhorizontalScrollBarjqxgrid")
            ActionChains(self.driver).click_and_hold(thumb).move_by_offset(scroll_amount, 0).release().perform()
            return True
        except Exception as e:
            print("Scroll failed:", e)
            return False

    # Scroll down the page slightly to ensure visibility
    def scroll_down(self, pixels=1000):
        self.driver.execute_script(f"window.scrollBy(0, {pixels});")
        time.sleep(1)

    # Call all ad removal methods in sequence with delay buffers
    def ensure_ads_removed(self):
        """Extra-safe ad removal wrapper with sleep buffering."""
        self.removal.close_ad_overlay()
        time.sleep(1.5)
        self.removal.remove_ad_overlay()
        time.sleep(0.5)
        self.removal.wait_for_overlay_to_disappear()
        time.sleep(1)

    # Search for a stock on the site and click first result
    def search(self, name):
        try:
            print("\nWaiting for search input...")
            try:
                # Try primary placeholder
                search_box = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH,
                        "//input[@class='js-typeahead' and @placeholder='Search over 200,000 charts...']"))
                )
                print("Found updated search box.")
            except:
                # Fallback placeholder text
                search_box = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH,
                        "//input[@class='js-typeahead' and @placeholder='Search over 200,000 interactive charts...']"))
                )
                print("Found fallback (interactive) search box.")

            self.driver.execute_script("arguments[0].scrollIntoView(true);", search_box)
            time.sleep(1)
            search_box.clear()
            print(f"Typing '{name}' into search box...")
            search_box.send_keys(name)
            time.sleep(2)

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".typeahead__result ul li a"))
            )
            first_result = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".typeahead__result ul li a"))
            )
            print("Clicking first search result...")
            first_result.click()
            time.sleep(3)

        except Exception as e:
            print(f"An error occurred while searching: {e}")

    # Click on a chart tab by visible text; handles nested sub-tabs
    def click(self, click_value, nested=False):
        try:
            self.ensure_ads_removed()  # ✅ pre-clean

            if nested:
                tabs = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul#myTabs"))
                )
                if len(tabs) < 2:
                    print("Nested tabs not found.")
                    return
                tab = tabs[1].find_element(By.XPATH, f".//a[contains(text(), '{click_value}')]")
            else:
                tab = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH,
                        f"//ul[@id='myTabs']//a[contains(text(), '{click_value}')]"))
                )

            # Scroll to avoid being blocked by overlays
            self.driver.execute_script("arguments[0].scrollIntoView(true);", tab)
            time.sleep(0.5)

            # Wait for clickability before clicking
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH,
                f"//ul[@id='myTabs']//a[contains(text(), '{click_value}')]")))

            tab.click()
            print(f"✅ Clicked on tab: {click_value}")
            time.sleep(3)

            self.ensure_ads_removed()  # ✅ post-click cleanup

        except Exception as e:
            print(f"❌ Could not click tab '{click_value}': {e}")

    # Ensure that chart data is shown in quarterly view
    def quartely(self):
        try:
            self.ensure_ads_removed()  # ✅ pre-clean

            select_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "select.frequency_select"))
            )
            selected_option = select_element.find_element(By.CSS_SELECTOR, "option[selected]")
            selected_text = selected_option.text.strip()
            selected_value = selected_option.get_attribute("value")

            print(f"Currently selected: {selected_text} (value = {selected_value})")

            # If already set to quarterly, skip
            if selected_value == "0" or "Quarterly" in selected_text:
                print("Already set to Quarterly. Skipping selection.")
                return

            print("Changing to Quarterly...")
            dropdown = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "span.select2-selection--single"))
            )
            dropdown.click()

            quarterly_option = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//li[contains(text(),'Quarterly')]"))
            )
            quarterly_option.click()

            time.sleep(5)
            self.ensure_ads_removed()  # ✅ post-switch clean
            time.sleep(5)

        except Exception as e:
            print(f"Error while checking or selecting Quarterly: {e}")