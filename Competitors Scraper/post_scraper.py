from fb_graphql_scraper.facebook_graphql_scraper import FacebookGraphqlScraper
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import json
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os, sys
# ──────────────────────────────────────────────
# CONFIG
# ──────────────────────────────────────────────
MAX_PARALLEL_BROWSERS = 3  
MAX_RETRIES           = 4
RETRY_DELAY_SEC       = 5
OUTPUT_DIR            = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")

# ──────────────────────────────────────────────
# THREAD-SAFE PRINT
# ──────────────────────────────────────────────
_print_lock = threading.Lock()

def tprint(*args, **kwargs):
    with _print_lock:
        print(*args, **kwargs)


# ──────────────────────────────────────────────
# URL / PAGE HELPERS
# ──────────────────────────────────────────────
def extract_page_from_url(url: str) -> str | None:
    if not url.startswith("http"):
        return url  # already a bare username

    parsed = urlparse(url)
    path   = parsed.path.strip("/")

    if "profile.php" in path:
        qs = parse_qs(parsed.query)
        if "id" in qs:
            return qs["id"][0]

    if path:
        return path.split("/")[0]

    return None


# ──────────────────────────────────────────────
# POPUP DISMISSAL  (called inside every thread)
# ──────────────────────────────────────────────
CLOSE_BUTTON_SELECTORS = [
    # The login modal's specific close button
    (By.XPATH, "//div[@aria-label='Close'][@role='button']"),
    (By.XPATH, "//div[@aria-label='إغلاق'][@role='button']"),
    # Generic modal close buttons
    (By.CSS_SELECTOR, "[aria-label='Close'][role='button']"),
    (By.CSS_SELECTOR, "[aria-label='إغلاق'][role='button']"),
    # Fallback: first button inside any dialog
    (By.XPATH, "//div[@role='dialog']//*[@role='button'][1]"),
    # The × button by its SVG path pattern
    (By.XPATH, "//*[name()='svg'][@aria-label='Close']/.."),
]

def _try_close_popup(driver) -> bool:
    # Method 1: Try known selectors
    for by, sel in CLOSE_BUTTON_SELECTORS:
        try:
            btn = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable((by, sel))
            )
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(1)
            return True
        except Exception:
            continue

    # Method 2: JavaScript brute-force — find ALL role=button elements
    # inside any dialog and click the first one that looks like a close btn
    try:
        clicked = driver.execute_script("""
            const dialogs = document.querySelectorAll('[role="dialog"]');
            for (const dialog of dialogs) {
                const btns = dialog.querySelectorAll('[role="button"]');
                for (const btn of btns) {
                    const label = (btn.getAttribute('aria-label') || '').toLowerCase();
                    if (label.includes('close') || label.includes('إغلاق')) {
                        btn.click();
                        return true;
                    }
                }
                // If no labelled button, click the first button (usually ×)
                if (btns.length > 0) {
                    btns[0].click();
                    return true;
                }
            }
            return false;
        """)
        if clicked:
            time.sleep(1)
            return True
    except Exception:
        pass

    # Method 3: Remove the modal from DOM entirely as last resort
    try:
        removed = driver.execute_script("""
            const overlay = document.querySelector('[role="dialog"]');
            if (overlay) {
                const parent = overlay.closest('[data-visualcompletion]')
                            || overlay.parentElement;
                if (parent) parent.remove();
                else overlay.remove();
                return true;
            }
            return false;
        """)
        return bool(removed)
    except Exception:
        pass

    return False


def dismiss_popup(scraper, target_page: str, label: str = "") -> None:
    tag = f"[{label}] " if label else ""
    tprint(f"{tag}🛡️  Navigating to page + dismissing popups...")
    try:
        scraper.driver.get(f"https://www.facebook.com/{target_page}")

        # Wait for page to start loading
        time.sleep(3)

        # Attempt 1: ESC key
        try:
            scraper.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            time.sleep(1)
        except Exception:
            pass

        # Attempt 2: Check if dialog is present and close it
        try:
            WebDriverWait(scraper.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[role='dialog']"))
            )
            tprint(f"{tag}🔍 Dialog detected — attempting to close...")
            closed = _try_close_popup(scraper.driver)
            tprint(f"{tag}{'✅ Popup closed.' if closed else '⚠️ Could not close via button — removed from DOM.'}")
        except TimeoutException:
            tprint(f"{tag}ℹ️  No popup detected (probably fine).")

        # Final ESC for good measure
        try:
            scraper.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        except Exception:
            pass
        try:
            WebDriverWait(scraper.driver, 3).until(
            EC.invisibility_of_element_located((By.CSS_SELECTOR, "[role='dialog']"))
            )
            tprint(f"{tag}✅ Dialog confirmed gone.")
        except TimeoutException:
            # Force-remove it from DOM as last resort
            scraper.driver.execute_script("""
                document.querySelectorAll('[role="dialog"]').forEach(el => el.remove());
                """)
            time.sleep(1)

        time.sleep(2)
        tprint(f"{tag}✅ Pre-flight complete.")
    except Exception as e:
            tprint(f"{tag}⚠️  Pre-load issue (usually fine): {e}")


# ──────────────────────────────────────────────
# CORE SCRAPE (with retry)
# ──────────────────────────────────────────────
def scrape_page(scraper, target_page: str, days_back: int, label: str = "") -> dict | None:
    tag = f"[{label}] "
    dismiss_popup(scraper, target_page, label)

    for attempt in range(1, MAX_RETRIES + 1):
        tprint(f"{tag}🔄 Attempt {attempt}/{MAX_RETRIES}...")
        try:
            data = scraper.get_user_posts(
                fb_username_or_userid=target_page,
                days_limit=days_back,
                display_progress=True,
            )
            tprint(f"{tag}✅ Data fetched successfully!")
            return data
        except Exception as e:
            tprint(f"{tag}⚠️  Attempt {attempt} failed: {e}")
            if attempt < MAX_RETRIES:
                tprint(f"{tag}Retrying in {RETRY_DELAY_SEC}s...")
                time.sleep(RETRY_DELAY_SEC)
            else:
                tprint(f"{tag}❌ All {MAX_RETRIES} attempts exhausted.")
                return None


# ──────────────────────────────────────────────
# SAVE + SUMMARISE
# ──────────────────────────────────────────────
def save_data(data: dict, target_page: str, days_back: int, label: str = "") -> dict:
    tag = f"[{label}] "

    if not data or "data" not in data:
        tprint(f"{tag}⚠️  No post data to save.")
        return {"page": target_page, "status": "⚠️ No data", "posts_scraped": 0}

    posts = data["data"]

    # Print quick summary
    with _print_lock:
        print(f"\n{'='*52}")
        print(f"  {tag}POSTS — {target_page}  ({len(posts)} found)")
        print(f"{'='*52}")
        for i, post in enumerate(posts, 1):
            print(f"\n  --- Post {i} ---")
            print(f"  ID   : {post.get('post_id', 'N/A')}")
            print(f"  Date : {post.get('published_date2', post.get('published_date', 'N/A'))}")
            text = post.get("message", post.get("text", ""))
            if text:
                print(f"  Text : {text[:100]}...")

            # reactions
            rc = post.get("reaction_count", {})
            reactions = rc.get("count", 0) if isinstance(rc, dict) else post.get("reactions", 0)
            print(f"  ❤️   : {reactions}")

            # comments
            cri = post.get("comment_rendering_instance", {})
            comments = (
                cri.get("comments", {}).get("total_count", 0)
                if isinstance(cri, dict) and cri
                else post.get("comments", post.get("comment_count", 0))
            )
            print(f"  💬   : {comments}")

            # shares
            sc = post.get("share_count", {})
            shares = sc.get("count", 0) if isinstance(sc, dict) else post.get("shares", 0)
            print(f"  🔁   : {shares}")

    # Write JSON
    import os; os.makedirs(OUTPUT_DIR, exist_ok=True)
    date_str     = datetime.now().strftime("%Y%m%d")
    output_file  = f"{OUTPUT_DIR}/{target_page}_{days_back}days_{date_str}.json"
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        tprint(f"{tag}💾 Saved → {output_file}")
    except Exception as e:
        tprint(f"{tag}❌ Save failed: {e}")

    return {
        "page": target_page,
        "status": "✅ Success" if posts else "⚠️ No posts",
        "posts_scraped": len(posts),
    }


# ──────────────────────────────────────────────
# WORKER  (one per thread / browser)
# ──────────────────────────────────────────────
def worker(target_page: str, days_back: int, thread_id: int) -> dict:
    label   = f"T{thread_id}:{target_page}"
    scraper = None
    try:
        tprint(f"[{label}] 🌐 Opening browser...")
        scraper = FacebookGraphqlScraper(open_browser=True)
        data = scrape_page(scraper, target_page, days_back, label)
        if data is None:
            return {"page": target_page, "status": "❌ Failed to scrape", "posts_scraped": 0}
        return  save_data(data, target_page, days_back, label)
    except Exception as e:
        tprint(f"[{label}] 💥 Unhandled error: {e}")
        return {"page": target_page, "status": f"❌ Error: {e}", "posts_scraped": 0}
    finally:
        if scraper:
            try:
                scraper.driver.quit()  # type:ignore
                tprint(f"[{label}] 🔒 Browser closed.")
            except Exception:
                pass


# ──────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────
if __name__ == "__main__":
    print("Enter Facebook page URLs or usernames (one per line).")
    print("Press Enter on an empty line when done.\n")

    urls = []
    while True:
        line = input(f"  URL #{len(urls) + 1} (or Enter to finish): ").strip()
        if not line:
            if urls:
                break
            print("⚠️  Please enter at least one URL.")
        else:
            urls.append(line)

    days_back_input = input(f"\nDays back to scrape (default 30): ").strip()
    days_back = int(days_back_input) if days_back_input.isdigit() else 30

    # Resolve usernames
    pages = []
    for url in urls:
        page = extract_page_from_url(url)
        if page:
            pages.append(page)
            print(f"  ✅ {page}")
        else:
            print(f"  ❌ Could not parse: {url} — skipping.")

    if not pages:
        print("\n❌ No valid pages. Exiting.")
        exit(1)

    parallel = min(MAX_PARALLEL_BROWSERS, len(pages))
    print(f"\n🚀 Scraping {len(pages)} page(s) — up to {parallel} browsers in parallel...\n")

    results = []
    with ThreadPoolExecutor(max_workers=parallel) as pool:
        futures = {
            pool.submit(worker, page, days_back, tid): page
            for tid, page in enumerate(pages, 1)
        }
        for future in as_completed(futures):
            page = futures[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                tprint(f"❌ Future for '{page}' raised: {e}")
                results.append({"page": page, "status": f"❌ {e}", "posts_scraped": 0})

    # ── Final summary ──
    print(f"\n{'='*60}")
    print("📊  SCRAPING SUMMARY")
    print(f"{'='*60}")
    for r in sorted(results, key=lambda x: x["page"]):
        print(f"  {r['status']:<20}  {r['page']:<30}  {r['posts_scraped']} posts")
    print(f"{'='*60}")

''''
https://www.facebook.com/Zara
https://www.facebook.com/SutraStores
https://www.facebook.com/NEXTmart.EG
'''