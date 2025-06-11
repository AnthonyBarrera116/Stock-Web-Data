from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time

# This class handles the removal of obstructive ad overlays on web pages using Selenium
class Remove:
    # Constructor to store the Selenium WebDriver instance
    def __init__(self, driver):
        self.driver = driver

    # Attempts to close visible ad overlays using common close buttons
    def close_ad_overlay(self):
        try:
            print("\n🔍 Trying to close ad overlays...")

            # Look for overlay elements commonly used for ads
            overlays = self.driver.find_elements(
                By.CSS_SELECTOR,
                "div[role='dialog'], div[class*='modal'], div[class*='popup'], div[class*='overlay']"
            )

            # Loop through each overlay found
            for overlay in overlays:
                if overlay.is_displayed():  # Check if the overlay is visible
                    try:
                        # Try to find a close button with common text patterns
                        close_btn = overlay.find_element(
                            By.XPATH,
                            ".//button[contains(text(), '×') or contains(text(), 'Close') or contains(text(), 'close') or contains(text(), 'CLOSE')]"
                        )
                        close_btn.click()  # Click the close button
                        print("✅ Ad overlay closed via button text.")
                        time.sleep(1)
                        return  # Exit after closing

                    except:
                        try:
                            # If text-based close failed, try class-based button selectors
                            close_btn = overlay.find_element(
                                By.CSS_SELECTOR,
                                "button.close, button.btn-close, button[class*='close'], button[class*='dismiss']"
                            )
                            close_btn.click()  # Click the close button
                            print("✅ Ad overlay closed via class match.")
                            time.sleep(1)
                            return

                        except:
                            print("⚠️ No clickable close button found in overlay.")

        except Exception as e:
            # Log exception if overlay closing fails
            print(f"❌ Could not close ad overlay: {e}")

    # Forcefully removes ad overlays using JavaScript execution (as a backup)
    def remove_ad_overlay(self):
        print("🧨 Removing ad overlays with aggressive JavaScript...")

        # Execute JS to remove fixed-position ad elements from DOM and restore scrolling
        self.driver.execute_script("""
            document.querySelectorAll("div[role='dialog'], div[class*='modal'], div[class*='popup'], div[class*='overlay'], div[style*='position:fixed'], div[style*='position: fixed']").forEach(function(el) {
                el.remove();
            });
            document.body.style.overflow = 'auto'; // restore scroll in case it was locked
        """)
        time.sleep(1)

    # Waits for all overlays to disappear to ensure page is clean
    def wait_for_overlay_to_disappear(self, timeout=10):
        try:
            print("⏳ Waiting for ad overlays to disappear...")

            # Wait until there are no elements matching common overlay selectors
            WebDriverWait(self.driver, timeout).until(
                lambda d: len(d.find_elements(
                    By.CSS_SELECTOR,
                    "div[id^='gray'], div[id^='overlay'], div[role='dialog'], div[class*='overlay']"
                )) == 0
            )
            print("✅ Ad overlays disappeared.")
        except:
            # Log warning if overlays remain after timeout
            print("⚠️ Ad overlays did not disappear in time.")

    # Combines all overlay removal methods to aggressively clear the page
    def force_clear_all_obstructions(self, timeout=10):
        print("🚨 Force clearing all potential obstructions...")

        # Attempt gentle close
        self.close_ad_overlay()

        # If that fails, use JavaScript brute-force
        self.remove_ad_overlay()

        # Wait to ensure the DOM is clean
        self.wait_for_overlay_to_disappear(timeout)

        try:
            # Confirm no fixed-position elements remain visible
            WebDriverWait(self.driver, timeout).until(
                lambda d: all(not el.is_displayed() for el in d.find_elements(
                    By.CSS_SELECTOR,
                    "div[style*='position:fixed'], div[style*='position: fixed']"
                ))
            )
            print("✅ All obstructive overlays removed successfully.")
        except:
            print("⚠️ Warning: Some overlays may still be present.")
