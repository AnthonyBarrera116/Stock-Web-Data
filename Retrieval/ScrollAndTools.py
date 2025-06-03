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

    # intilzie class
    def __init__(self, driver):
        self.driver = driver  # web driver from Retrieve Data from Intilaze web 
        self.removal = a.Remove(self.driver)  # Adremoval.py to clean overlays

    # pattern check to see if string is a date format like 2020-12-31
    def looks_like_date(self, s):
        return bool(re.match(r'^\d{4}-\d{2}-\d{2}$', s))

    # gets data from chart headers and rows
    def extract_grid_data(self):
        # headers of chart
        headers = [
            h.text.strip()
            for h in self.driver.find_elements(By.CSS_SELECTOR, "#jqxgrid .jqx-grid-column-header span")
        ]

        # rows of data from grid
        rows = [
            [cell.text.strip() for cell in row.find_elements(By.CSS_SELECTOR, "div[role='gridcell']")]
            for row in self.driver.find_elements(By.CSS_SELECTOR, "#jqxgrid .jqx-grid-content div[role='row']")
        ]

        # returns headers and rows
        return headers, rows

    # get position of scrollbar to see if it moved
    def get_scrollbar_thumb_x(self):
        try:
            thumb = self.driver.find_element(By.ID, "jqxScrollThumbhorizontalScrollBarjqxgrid")
            return thumb.location['x']
        except Exception:
            return None

    # moves the scroll bar to right to load more chart data
    def drag_scrollbar(self, scroll_amount=50):
        try:
            thumb = self.driver.find_element(By.ID, "jqxScrollThumbhorizontalScrollBarjqxgrid")
            ActionChains(self.driver).click_and_hold(thumb).move_by_offset(scroll_amount, 0).release().perform()
            return True
        except Exception as e:
            print("Scroll failed:", e)
            return False

    # scroll down the page
    def scroll_down(self, pixels=1000):
        self.driver.execute_script(f"window.scrollBy(0, {pixels});")
        time.sleep(1)

    # search function to find stock on macrotrends
    def search(self, name):
        try:
            print("\nWaiting for search input...")

            # try main input
            try:
                search_box = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH,
                        "//input[@class='js-typeahead' and @placeholder='Search over 200,000 charts...']"))
                )
                print("Found updated search box.")
            # fallback if page isn't homepage
            except:
                search_box = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH,
                        "//input[@class='js-typeahead' and @placeholder='Search over 200,000 interactive charts...']"))
                )
                print("Found fallback (interactive) search box.")

            # scroll to input
            self.driver.execute_script("arguments[0].scrollIntoView(true);", search_box)
            time.sleep(1)

            # type stock
            search_box.clear()
            print(f"Typing '{name}' into search box...")
            search_box.send_keys(name)

            # wait for dropdown
            time.sleep(2)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".typeahead__result ul li a"))
            )

            # click first result
            first_result = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".typeahead__result ul li a"))
            )
            print("Clicking first search result...")
            first_result.click()
            time.sleep(3)

        except Exception as e:
            print(f"An error occurred while searching: {e}")

    # clicks chart tabs on page, optionally within a nested tab like "Employee Count"
    def click(self, click_value, nested=False):
        try:
            # close and remove any ad overlays before interacting with the page
            self.removal.close_ad_overlay()
            self.removal.remove_ad_overlay()
            self.removal.wait_for_overlay_to_disappear()

            # if the tab is inside a nested section (e.g., "Employee Count" under "Other Metrics")
            if nested:
                # wait for nested tab section to appear (ul#myTabs)
                tabs = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul#myTabs"))
                )

                # if the structure doesn't have enough nested sections, print warning and return
                if len(tabs) < 2:
                    print("Nested tabs not found.")
                    return

                # find the nested tab using the text value
                tab = tabs[1].find_element(By.XPATH, f".//a[contains(text(), '{click_value}')]")
            else:
                # find the main tab using text value (non-nested)
                tab = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH,
                        f"//ul[@id='myTabs']//a[contains(text(), '{click_value}')]"))
                )

            # click on the tab to load its content
            tab.click()
            print(f"Clicked on tab: {click_value}")
            time.sleep(3)  # allow time for content to load

        # catch and print any errors during the click
        except Exception as e:
            print(f"Could not click tab '{click_value}': {e}")

    # switches the chart view from annual to quarterly if it's not already set
    def quartely(self):
        try:
            # remove any overlays that might block interaction
            self.removal.close_ad_overlay()
            self.removal.remove_ad_overlay()
            self.removal.wait_for_overlay_to_disappear()

            # locate the dropdown that selects frequency
            select_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "select.frequency_select"))
            )

            # get the currently selected option
            selected_option = select_element.find_element(By.CSS_SELECTOR, "option[selected]")
            selected_text = selected_option.text.strip()
            selected_value = selected_option.get_attribute("value")

            print(f"Currently selected: {selected_text} (value = {selected_value})")

            # if already set to quarterly, skip
            if selected_value == "0" or "Quarterly" in selected_text:
                print("Already set to Quarterly. Skipping selection.")
                return

            # otherwise, change to Quarterly view using the custom dropdown (select2)
            print("Changing to Quarterly...")

            # click the dropdown to open it
            dropdown = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "span.select2-selection--single"))
            )
            dropdown.click()

            # find and click the "Quarterly" option
            quarterly_option = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//li[contains(text(),'Quarterly')]"))
            )
            quarterly_option.click()
            time.sleep(5)  # wait for table to reload

        # handle any issue with dropdown selection or visibility
        except Exception as e:
            print(f"Error while checking or selecting Quarterly: {e}")
