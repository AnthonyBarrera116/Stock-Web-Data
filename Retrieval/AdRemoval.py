# Libraries
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time

# Removal class for ads
class Remove:

    # Intializes class
    def __init__(self, driver):
        # Driver from ScrollAndTools which is from RetrieveData from Intialize Web
        self.driver = driver

    # Close ad overlay function removes gray background or popups
    def close_ad_overlay(self):
        try:
            print("\nTrying to close ad overlays...")

            # find all possible overlay containers
            overlays = self.driver.find_elements(
                By.CSS_SELECTOR,
                "div[role='dialog'], div[class*='modal'], div[class*='popup'], div[class*='overlay']"
            )

            # loop through overlays found
            for overlay in overlays:
                if overlay.is_displayed():
                    try:
                        # Try common text-based close buttons (×, Close, etc.)
                        close_btn = overlay.find_element(
                            By.XPATH,
                            ".//button[contains(text(), '×') or contains(text(), 'Close') or contains(text(), 'close') or contains(text(), 'CLOSE')]"
                        )
                        close_btn.click()
                        print("Ad overlay closed via button text.")
                        time.sleep(1)
                        return

                    except:
                        try:
                            # Try known close class names
                            close_btn = overlay.find_element(
                                By.CSS_SELECTOR,
                                "button.close, button.btn-close, button[class*='close'], button[class*='dismiss']"
                            )
                            close_btn.click()
                            print("Ad overlay closed via class match.")
                            time.sleep(1)
                            return

                        except:
                            print("No clickable close button found in overlay.")

        except Exception as e:
            print(f"Could not close ad overlay: {e}")

    # Remove all overlays directly using JavaScript
    def remove_ad_overlay(self):
        print("Removing ad overlays with JavaScript...")

        self.driver.execute_script("""
            document.querySelectorAll("div[role='dialog'], div[class*='modal'], div[class*='popup'], div[class*='overlay']").forEach(function(el) {
                el.remove();
            });
        """)
        time.sleep(1)

    # Wait for overlays to disappear completely
    def wait_for_overlay_to_disappear(self, timeout=10):
        try:
            print("Waiting for ad overlays to disappear...")

            WebDriverWait(self.driver, timeout).until(
                lambda d: len(d.find_elements(
                    By.CSS_SELECTOR,
                    "div[id^='gray'], div[id^='overlay'], div[role='dialog']"
                )) == 0
            )

            print("Ad overlays disappeared.")
        except:
            print("Ad overlays did not disappear in time.")
