# FPT Portal Auto-Clicker (Stealth Mode)

## Requirements

**No manual chromedriver download needed!** - `undetected-chromedriver` automatically downloads and patches the correct ChromeDriver version for your Chrome installation.

### Dependencies
```bash
pip install -r requirements.txt
```

Required packages:
- `undetected-chromedriver` - Auto-downloads ChromeDriver and patches automation detection
- `selenium>=4.9.0` - Already included with undetected-chromedriver

---

## How to Use

### 1. Update Cookies
Before running, update `cookies.json` with fresh cookies from your Chrome browser:

1. Open Chrome (your normal browser where you're logged into FPT portal)
2. Go to `https://fap.fpt.edu.vn/FrontOffice/MoveSubject.aspx?id=59904`
3. Install **EditThisCookie** extension in Chrome
4. Click the extension icon → Export cookies for `fap.fpt.edu.vn`
5. Replace contents of `cookies.json` with the exported JSON

### 2. Configure the Script
Edit the **CONFIGURATION** section at the top of `stealth-version.py`:

```python
# ========================
# CONFIGURATION
# ========================
TARGET_URL = "https://fap.fpt.edu.vn/FrontOffice/MoveSubject.aspx?id=59904"
ORIGINAL_CLASS = None   # Auto-detect from page, or set manually (e.g., "IA1906")
TARGET_CLASS = None     # Stop when class changes to this, or None for any change
CLICK_INTERVAL = 60     # Seconds between each click attempt = 1 minutes for 1 click
COOKIES_FILE = "cookies.json"
# ========================
```

### 3. Run the Script
```bash
cd fpt-auto-clicker
source venv/Scripts/activate
python stealth-version.py
```

---

## How It Works

1. **Launch Chrome (Stealth Mode)**
   - `undetected-chromedriver` launches a patched Chrome that bypasses Cloudflare
   - No automation flags detected by websites

2. **Load Cookies**
   - Adds cookies from `cookies.json` to the browser session
   - Cookies authenticate you on the FPT portal

3. **Navigate to Target Page**
   - Opens the MoveSubject page for the specified subject ID

4. **Detection Loop**
   - Reads current class from page element `#ctl00_mainContent_lblOldGroup`
   - Clicks Save button `#ctl00_mainContent_btSave`
   - Waits for alert dialog
   - If alert shows success → stop and notify
   - If alert shows "full" → continue retrying
   - If no change after interval → repeat

5. **Success Detection**
   - Detects success from alert text: `chấp nhận`, `success`, `thành công`
   - OR detects class change from the page element

---

## Rules Before Use

### 1. Cookie Freshness
- Cookies expire! Get fresh cookies each time before running
- Session cookies typically last 4-8 hours
- If you get 404 errors, cookies are likely expired

### 2. Session Validity
- Make sure your FPT account has access to the subject
- The subject ID (`id=59904`) must be valid for your account
- If page shows "The resource cannot be found", check the URL

### 3. Cloudflare Clearance
- `cf_clearance` cookie is bound to browser fingerprint
- Fresh cookies from Chrome work best
- Cookies exported from a different browser/profile may not work

### 4. Don't Close the Browser
- Let the script run until it shows SUCCESS
- Closing Chrome will break the automation

### 5. Check Class Code
- `ORIGINAL_CLASS = None` auto-detects starting class
- Set specific class if you know what you're switching FROM
- `TARGET_CLASS = None` stops on any class change
- Set specific class (e.g., `"MC001"`) if you want to wait for a specific target

### 6. Timing
- `CLICK_INTERVAL = 60` means it clicks every 60 seconds
- FPT portal updates class lists at random intervals
- Too frequent clicking may trigger rate limits
- 60 seconds is a safe interval

### 7. Alert Handling
- Some alerts mean success, some mean failure
- Script auto-detects:
  - Success: "chấp nhận", "success", "thành công"
  - Failure: "full", "đầy" (full in Vietnamese)

---

## Troubleshooting

### 404 Error / "The resource cannot be found"
→ Cookies expired or session invalid. Get fresh cookies.

### "Could not read class info"
→ Page didn't load properly. Check URL and cookies.

### "Click failed: No such element"
→ Save button not found. Page may not be loaded correctly.

### Cloudflare still blocking
→ Run Chrome with `--remote-debugging-port=9222` and use CDP method instead.

### Alert not detected
→ Try adding `time.sleep(2)` after clicking Save for slower-loading alerts.

---

## File Structure
```
fpt-auto-clicker/
├── stealth-version.py    # Main script (uses undetected-chromedriver)
├── playwright-version.py  # Alternative script (uses Playwright CDP)
├── cookies.json          # Your cookies (update regularly!)
├── requirements.txt      # Dependencies
└── venv/                # Virtual environment
```
