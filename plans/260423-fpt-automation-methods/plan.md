# FPT University Portal - Automation Script Plan

## Overview
Compare two Python automation methods to auto-click buttons on FAP portal (https://fap.fpt.edu.vn/MoveSubject.aspx?id=59122)

## Context
- **Goal**: Automate clicking "Save" button on FPT University portal
- **Challenge**: ASP.NET WebForms with ViewState, EventValidation, AntiXsrfToken
- **Session**: Cookie-based authentication

---

## Method 1: Playwright (Browser Automation)

### What it does
Opens a real Chromium browser, loads page, clicks elements via CSS selectors

### Pros
| ✅ | Reason |
|----|--------|
| Easy to write | Like talking to a real user - `page.click("#btn")` |
| Handles everything automatically | Cookies, ViewState, JavaScript, Cloudflare - all handled |
| Debugging easy | See the browser actually working |
| Works with complex JS | SweetAlert popups, dynamic content, React/Vue apps |
| Headless option | Run without visible browser window |

### Cons
| ❌ | Reason |
|----|--------|
| Heavy | Runs full browser (~100MB+ RAM) |
| Slower | Real browser overhead |
| Fragile to UI changes | Button moves = selector breaks |
| Detection possible | Some sites block automation |

### Best for
- Beginners
- Complex JS-heavy pages
- When you need to see what's happening

---

## Method 2: Requests (HTTP Programmatic)

### What it does
Sends raw HTTP requests with proper headers, cookies, and form data

### Pros
| ✅ | Reason |
|----|--------|
| Lightweight | No browser, just HTTP (~10MB RAM) |
| Fast | Direct server communication |
| Undetectable | Looks like normal browser traffic |
| Scriptable | Easy to loop, schedule, integrate |

### Cons
| ❌ | Reason |
|----|--------|
| Complex to write | Must handle ViewState, EventValidation manually |
| Brittle | ASP.NET postback data changes often |
| Debugging hard | Invisible - can't see what's happening |
| Security token hell | AntiXsrf, Cloudflare clearance tokens expire |

### Best for
- Production scripts
- API-only interactions
- When speed matters

---

## Comparison Matrix

| Criteria | Playwright | Requests |
|----------|-----------|----------|
| Ease of use | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| Speed | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Resource usage | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| Reliability | ⭐⭐⭐⭐ | ⭐⭐ |
| Maintainability | ⭐⭐⭐⭐ | ⭐⭐ |

---

## Recommendation

### For FPT Portal → **Playwright is BETTER**

**Reasons:**
1. ASP.NET WebForms with anti-xsrf tokens, viewstate, event validation = nightmare for requests
2. Cloudflare protection likely present (cf_clearance cookie seen)
3. Alert popups on full class (JavaScript `alert()`)
4. Simpler to maintain when selectors rarely change
5. Save button is simple CSS selector `#ctl00_mainContent_btSave`

### Only use Requests if:
- You need to run 1000+ requests per minute
- You have API access instead of web scraping
- You want hidden background service

---

## Phase 1: Playwright Implementation
- Install: `pip install playwright && playwright install chromium`
- Write script to load cookies, navigate page, click Save
- Test with visible browser first (headless=False)
- Handle errors (class full, session expired, etc.)

## Phase 2: Requests Implementation (Optional backup)
- Use browser DevTools Network tab to capture full request
- Replicate POST with proper ViewState/EventValidation
- Only if Playwright proves too slow

---

## Files to Create
```
D:/AShiroru/ProgramCode/PlaceTestSCript/
├── fpt-auto-clicker/
│   ├── playwright-version.py    # RECOMMENDED
│   ├── requests-version.py       # COMPLEX/HARD
│   ├── cookies-template.json     # Your cookies here
│   └── requirements.txt
└── plans/
    └── 260423-fpt-automation-methods/
        └── plan.md
```
