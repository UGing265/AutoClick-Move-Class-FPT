import time
import json
from playwright.sync_api import sync_playwright

# ========================
# CONFIGURATION
# ========================
TARGET_URL = "https://fap.fpt.edu.vn/MoveSubject.aspx?id=59122"
CLICK_INTERVAL = 60  # seconds between each click
COOKIES_FILE = "cookies.json"  # Your cookies file
# ========================


def load_cookies():
    """Load cookies from cookies.json"""
    with open(COOKIES_FILE, "r") as f:
        return json.load(f)


def main():
    print("Connecting to Chrome via CDP...")
    cdp_url = "http://localhost:9222"

    cookies = load_cookies()
    print(f"Loaded {len(cookies)} cookies from {COOKIES_FILE}")

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(cdp_url)
            print("Connected to Chrome successfully!")
        except Exception as e:
            print(f"Failed to connect: {e}")
            return

        # Use first context (the debugged Chrome)
        context = browser.contexts[0]

        # Add our cookies to the session
        context.add_cookies(cookies)
        print(f"Added {len(cookies)} cookies to session")

        # Find or create the target page
        page = None
        for ctx in browser.contexts:
            for pg in ctx.pages:
                if "MoveSubject" in pg.url and "devtools" not in pg.url:
                    page = pg
                    break
            if page:
                break

        if not page:
            page = context.new_page()

        print(f"Using page: {page.url}")
        attempt = 0

        while True:
            attempt += 1
            current_time = time.strftime("%H:%M:%S")
            print(f"\n[{current_time}] Attempt #{attempt}")

            # Reload page
            print(f"  Loading page...")
            page.goto(TARGET_URL)
            page.wait_for_load_state("networkidle")

            # Check current class status
            try:
                old_class = page.locator("#ctl00_mainContent_lblOldGroup").inner_text()
                print(f"  Current class: {old_class}")

                # SUCCESS: Class changed from IA1906
                if old_class != "IA1906":
                    print(f"\n>>> SUCCESS! Now in class: {old_class}")
                    print("You can close the browser now.")
                    time.sleep(5)  # Give user 5 seconds to see
                    break
            except Exception as e:
                print(f"  Could not read class info: {e}")

            # Check for error message
            try:
                error_msg = page.locator("#ctl00_mainContent_lblMessage").inner_text()
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
                page.click("#ctl00_mainContent_btSave")
            except Exception as e:
                print(f"  Click failed: {e}")

            # Wait before next attempt
            print(f"  - Waiting {CLICK_INTERVAL}s before next click...")
            time.sleep(CLICK_INTERVAL)

        browser.close()


if __name__ == "__main__":
    print("=" * 50)
    print("FPT Portal Auto-Clicker")
    print("Will click Save every 5 seconds until success")
    print("=" * 50)
    main()
