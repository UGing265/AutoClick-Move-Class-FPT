import time
import json
import undetected_chromedriver as uc

# ========================
# CONFIGURATION
# ========================
TARGET_URL = "https://fap.fpt.edu.vn/FrontOffice/MoveSubject.aspx?id=59904"
ORIGINAL_CLASS = "ABCE"  # Auto-detected on first load
TARGET_CLASS = "SE19326"    # Set specific class to wait for (e.g., "SE1935"), or None to stop on any change
CLICK_INTERVAL = 30   # seconds between each click
COOKIES_FILE = "cookies.json"
# ========================


def load_cookies():
    """Load cookies from cookies.json"""
    with open(COOKIES_FILE, "r") as f:
        return json.load(f)


def main():
    cookies = load_cookies()
    print(f"Loaded {len(cookies)} cookies from {COOKIES_FILE}")

    # Setup Chrome options
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")

    print("Launching Chrome (stealth mode)...")

    # Launch browser - this patches Chrome to avoid detection
    driver = uc.Chrome(options=options, version_main=147)
    driver.get("https://fap.fpt.edu.vn")

    print(f"Adding cookies...")
    # Add cookies to the browser
    for cookie in cookies:
        try:
            # Handle domain differences
            cookie_dict = {
                "name": cookie["name"],
                "value": cookie["value"],
                "domain": cookie.get("domain", "fap.fpt.edu.vn"),
                "path": cookie.get("path", "/"),
            }
            driver.add_cookie(cookie_dict)
        except Exception as e:
            print(f"  Could not add {cookie['name']}: {e}")

    print(f"Navigating to {TARGET_URL}...")
    driver.get(TARGET_URL)
    time.sleep(2)

    # Get initial class to know what we're starting from
    if ORIGINAL_CLASS is None:
        try:
            initial_elem = driver.find_element("id", "ctl00_mainContent_lblOldGroup")
            original_class = initial_elem.text
            print(f"Initial class detected: {original_class}")
        except:
            print("Could not read initial class")
            original_class = "UNKNOWN"
    else:
        original_class = ORIGINAL_CLASS
        print(f"Using configured original class: {original_class}")

    attempt = 0

    while True:
        attempt += 1
        current_time = time.strftime("%H:%M:%S")
        print(f"\n[{current_time}] Attempt #{attempt}")

        # Check current class status
        try:
            old_class_elem = driver.find_element("id", "ctl00_mainContent_lblOldGroup")
            old_class = old_class_elem.text
            print(f"  Current class: {old_class}")

            # SUCCESS: Class changed from original class
            if original_class and old_class != original_class:
                # If TARGET_CLASS is set, only stop when we reach it
                if TARGET_CLASS is None or old_class == TARGET_CLASS:
                    print(f"\n>>> SUCCESS! Changed from {original_class} to {old_class}")
                    if TARGET_CLASS:
                        print(f"Reached target class: {TARGET_CLASS}")
                    print("You can close the browser now.")
                    time.sleep(5)
                    break
                else:
                    print(f"  Class changed to {old_class} but waiting for {TARGET_CLASS}...")
        except Exception as e:
            print(f"  Could not read class info: {e}")
            # Debug: print page title and snippet
            print(f"  Page title: {driver.title}")
            body = driver.find_element("tag name", "body")
            print(f"  Body text snippet: {body.text[:200]}...")

        # Check for error message
        try:
            error_elem = driver.find_element("id", "ctl00_mainContent_lblMessage")
            error_msg = error_elem.text
            if error_msg:
                if "full" in error_msg.lower() or "35" in error_msg:
                    print(f"  X Class full (35 students) - will retry")
                else:
                    print(f"  Info: {error_msg}")
        except:
            pass

        # Click Save button
        print(f"  Clicking Save button...")
        try:
            save_btn = driver.find_element("id", "ctl00_mainContent_btSave")
            save_btn.click()
            time.sleep(5)  # Wait for alert to appear

            # Handle alert dialog if present
            try:
                alert = driver.switch_to.alert
                alert_text = alert.text
                print(f"  Alert detected: {alert_text}")
                alert.accept()  # Click Ok/Yes to dismiss

                # Check if alert indicates success
                if "chấp nhận" in alert_text.lower() or "success" in alert_text.lower() or "thành công" in alert_text.lower():
                    print(f"  >>> SUCCESS! Alert confirmed: {alert_text}")
                    print("You can close the browser now.")
                    time.sleep(5)
                    break
                elif "full" in alert_text.lower() or "đầy" in alert_text.lower():
                    print(f"  X Class full - will retry")
                else:
                    print(f"  Alert dismissed (clicked Ok)")
            except:
                pass  # No alert present, continue
        except Exception as e:
            print(f"  Click failed: {e}")

        # Wait before next attempt
        print(f"  - Waiting {CLICK_INTERVAL}s before next click...")
        time.sleep(CLICK_INTERVAL)

    driver.quit()


if __name__ == "__main__":
    print("=" * 50)
    print("FPT Portal Auto-Clicker (Stealth Mode)")
    print("Will click Save every 60 seconds until success")
    print("=" * 50)
    main()
