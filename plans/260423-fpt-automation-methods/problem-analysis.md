# FPT Portal Auto-Clicker - Problem Analysis

**Date:** 2026-04-23
**Status:** BLOCKED

---

## Problem

Cloudflare blocks Playwright headless browser even with valid `cf_clearance` cookie.

**Error:** `403 Forbidden` with Cloudflare challenge redirect

---

## Root Cause Analysis

### Why cf_clearance Doesn't Work in Playwright

The `cf_clearance` cookie is **cryptographically bound** to the browser fingerprint that solved the challenge. This includes:

| Factor | Real Chrome | Playwright Headless |
|--------|-------------|---------------------|
| **TLS JA3 Fingerprint** | Chrome's TLS stack | Different cipher suite order |
| **User-Agent** | Real Chrome 147.x | Playwright default or overridden |
| **HTTP Headers** | Complete Sec-Fetch-* headers | Often missing or different order |
| **navigator.webdriver** | `false` | `true` (even when disabled in options) |
| **navigator.plugins** | 5-10 plugins | 0 plugins |
| **WebGL Renderer** | Real GPU info | Software renderer or masked |
| **Canvas Fingerprint** | GPU-specific anti-aliasing | CPU rendering patterns |
| **window.chrome object** | Present | Absent |

### Key Missing Elements in Our Cookies

1. **Missing `__cf_bm` cookie** - Cloudflare Bot Management cookie (some configs require this alongside `cf_clearance`)
2. **Missing `_ga_GSID` and `_gid`** - Google Analytics session cookies
3. **Domain scope issue** - `cf_clearance` is on `.fpt.edu.vn` but we may need it scoped to `.fap.fpt.edu.vn`
4. **Missing `__utmt`** - Urchin tracker cookie

### Session Binding Mismatch

Cloudflare's `cf_clearance` token contains internal state linking to:
- The specific TLS handshake that occurred
- The exact browser fingerprint at time of challenge solving
- The challenge instance (Ray ID)

When Playwright sends requests with a different TLS fingerprint, Cloudflare rejects the cookie even if it's technically valid.

---

## Solutions (In Order of Preference)

### 1. CDP Connection to Real Chrome (BEST)
Connect Playwright to user's real Chrome browser via Chrome DevTools Protocol.

**How:**
```cmd
:: Start Chrome with remote debugging
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
```

```python
# In Python
browser = p.chromium.connect_over_cdp("http://localhost:9222")
```

**Pros:** Uses real browser session with all cookies and fingerprint
**Cons:** Requires Chrome to be running with special flag

### 2. undetected-chromedriver
Uses patched ChromeDriver that masks automation signals.

**How:**
```bash
pip install undetected-chromedriver
```

```python
import undetected_chromedriver as uc
driver = uc.Chrome()
driver.get(url)
```

**Pros:** Better at evading detection
**Cons:** May still fail against Cloudflare's latest detection

### 3. curl_cffi for TLS Fingerprinting
Mimics Chrome's TLS stack exactly.

**How:**
```python
from curl_cffi import requests
response = requests.get(url, impersonate="chrome")
```

**Pros:** Matches Chrome's TLS fingerprint exactly
**Cons:** Doesn't handle JavaScript challenges or cookies well

### 4. Use Real Browser Cookies via Extension
Use a browser extension to export cookies in Playwright format.

**How:**
1. Install "EditThisCookie" extension in Chrome
2. Export cookies for fap.fpt.edu.vn
3. Convert to Playwright format

---

## Current Cookie Status

**Cookies Exported:** 8 cookies from `fap.fpt.edu.vn_cookies.txt`

**Valid Cookies:**
- `ASP.NET_SessionId` ✅
- `__AntiXsrfToken` ✅
- `.AspNet.cookies` ✅
- `cf_clearance` ⚠️ (bound to real Chrome fingerprint)
- `__utma`, `__utmc`, `__utmz`, `__utmb` ✅ (analytics)

**Missing:**
- `__cf_bm` (Bot Management)
- `_ga_GSID` (GA4 session)
- `_gid` (GA4 session)

---

## Recommendations

1. **Immediate:** Try CDP connection method - this is the most reliable
2. **If CDP fails:** Use undetected-chromedriver
3. **Long-term:** Consider using the site's API directly if available

---

## Files

- `cookies.json` - Current Playwright-format cookies
- `fap.fpt.edu.vn_cookies.txt` - Raw Netscape format cookies from Chrome
- `playwright-version.py` - Main auto-clicker script
