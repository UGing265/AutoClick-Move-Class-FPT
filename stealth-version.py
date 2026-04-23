import time
import json
import undetected_chromedriver as uc

# ========================
# CONFIGURATION
# ========================
TARGET_URL = "https://fap.fpt.edu.vn/FrontOffice/MoveSubject.aspx?id=59904"
ORIGINAL_CLASS = None  # Auto-detect on first load
CLICK_INTERVAL = 60  # seconds between each click
COOKIES_FILE = "cookies.json"
# ========================


def load_cookies():
    """Load cookies from cookies.json"""
    with open(COOKIES_FILE, "r") as f:
        return json.load(f)


def get_available_classes(driver):
    """Scan page for all class codes in the dropdown"""
    classes = []
    try:
        # The class dropdown is ddlCourse, not ddlGroupList
        select_elem = driver.find_element("css selector", "select#ctl00_mainContent_dllCourse")
        options = select_elem.find_elements("tag name", "option")
        for opt in options:
            code = opt.text.strip()
            value = opt.get_attribute("value")
            if code and code != "-- Select --":
                classes.append((code, value))
    except Exception as e:
        print(f"    Could not scan dropdown: {e}")
    return classes


def main():
    cookies = load_cookies()
    print(f"Loaded {len(cookies)} cookies from {COOKIES_FILE}")

    # Setup Chrome options
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-background-mode")
    options.add_argument("--disable-backgrounding-occluded-windows")

    print("Launching Chrome (stealth mode)...")

    # Launch browser - this patches Chrome to avoid detection
    driver = uc.Chrome(options=options, version_main=147)
    driver.get("https://fap.fpt.edu.vn")

    print(f"Adding cookies...")
    for cookie in cookies:
        try:
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

    # Detect original class
    if ORIGINAL_CLASS is None:
        try:
            initial_elem = driver.find_element("id", "ctl00_mainContent_lblOldGroup")
            original_class = initial_elem.text.strip()
            print(f"Initial class detected: {original_class}")
        except:
            print("Could not read initial class")
            original_class = "UNKNOWN"
    else:
        original_class = ORIGINAL_CLASS
        print(f"Using configured original class: {original_class}")

    # Show available classes
    print("\n" + "=" * 50)
    print("Scanning for available class codes...")
    available_classes = get_available_classes(driver)
    print(f"Found {len(available_classes)} class codes:")
    for i, (code, val) in enumerate(available_classes, 1):
        print(f"  {i}. {code}")
    print("=" * 50)

    # Ask user to choose target class
    print("\n" + "=" * 50)
    print("Type the class code you want to switch TO:")
    print("(Or press Enter to auto-detect and wait for any change)")

    valid_codes = [code for code, val in available_classes]
    while True:
        target_input = input("> ").strip()
        if not target_input:
            TARGET_CLASS = None
            print("Will stop on any class change from current")
            break
        target_input = target_input.upper()
        if target_input in valid_codes:
            TARGET_CLASS = target_input
            print(f"Target set: {TARGET_CLASS}")
            break
        print(f"  '{target_input}' not found in available classes.")
        print(f"  Available: {', '.join(valid_codes)}")
        print(f"  Try again:")

    # Map class code -> option value
    class_value_map = {code: val for code, val in available_classes}

    attempt = 0

    while True:
        attempt += 1
        current_time = time.strftime("%H:%M:%S")
        print(f"\n[{current_time}] Attempt #{attempt}")

        # Check current class status
        try:
            old_class_elem = driver.find_element("id", "ctl00_mainContent_lblOldGroup")
            old_class = old_class_elem.text.strip()
            print(f"  Current class: {old_class}")

            # SUCCESS: Class changed from original
            if original_class and old_class != original_class:
                if TARGET_CLASS is None or old_class == TARGET_CLASS:
                    print(f"\n>>> SUCCESS! Changed from {original_class} to {old_class}")
                    print("You can close the browser now.")
                    time.sleep(5)
                    break
                else:
                    print(f"  Class changed to {old_class} but waiting for {TARGET_CLASS}...")
        except Exception as e:
            print(f"  Could not read class info: {e}")
            print(f"  Page title: {driver.title}")

        # Check for error/info message
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
            # Select target class from dropdown first
            if TARGET_CLASS and TARGET_CLASS in class_value_map:
                from selenium.webdriver.support.ui import Select
                select_elem = driver.find_element("css selector", "select#ctl00_mainContent_dllCourse")
                select = Select(select_elem)
                select.select_by_value(class_value_map[TARGET_CLASS])
                # Verify selection
                selected_option = select.first_selected_option.text.strip()
                print(f"  [Dropdown] Selected: {selected_option}")
                time.sleep(0.5)

            save_btn = driver.find_element("id", "ctl00_mainContent_btSave")
            save_btn.click()
            print(f"  [Clicked] Save button pressed")
            time.sleep(5)

            # Handle alert dialog
            alert_got = None
            try:
                alert = driver.switch_to.alert
                alert_text = alert.text.replace("<br/>", " ").replace("<br>", " ")
                print(f"  --> Alert: {alert_text[:120]}")
                alert.accept()
                alert_got = alert_text
            except:
                print(f"  --> No alert popup.")

            # Also check if class changed AFTER clicking save (success might not show alert when minimized)
            try:
                check_class = driver.find_element("id", "ctl00_mainContent_lblOldGroup").text.strip()
                if check_class != old_class and check_class != original_class:
                    print(f"\n>>> SUCCESS! Class changed: {old_class} -> {check_class}")
                    try:
                        import winsound
                        winsound.MessageBeep(winsound.MB_ICONASTERISK)
                    except:
                        pass
                    print("You can close the browser now.")
                    time.sleep(5)
                    break
            except:
                pass

            # Alert-based result
            if alert_got:
                if "chấp nhận" in alert_got.lower() or "success" in alert_got.lower() or "thành công" in alert_got.lower():
                    print(f"\n>>> SUCCESS! You are now in class {TARGET_CLASS}!")
                    try:
                        import winsound
                        winsound.MessageBeep(winsound.MB_ICONASTERISK)
                    except:
                        pass
                    print("You can close the browser now.")
                    time.sleep(5)
                    break
                elif "full" in alert_got.lower() or "đầy" in alert_got.lower() or "35" in alert_got:
                    print(f"  --> Class is full. Will retry...")
                else:
                    print(f"  --> Alert (unknown). Retrying...")
        except Exception as e:
            print(f"  Click failed: {e}")

        print(f"  - Waiting {CLICK_INTERVAL}s before next click...")
        time.sleep(CLICK_INTERVAL)

    driver.quit()


if __name__ == "__main__":
    print("=" * 50)
    print("FPT Portal Auto-Clicker (Stealth Mode)")
    print("=" * 50)
    main()
