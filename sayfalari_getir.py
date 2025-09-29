#!/usr/bin/env python3
"""
boyut_getir_multi_progress_time.py

- urls.txt içinden URL'leri okur (başında http yoksa https ekler)
- Paralel olarak her URL'yi açar, lazy-load + video tetikler
- selenium-wire ile tüm HTTP(S) isteklerini yakalar
- Tek CSV'ye yazar: domain, istek sayısı, toplam boyut (MB)
- Ekrana her tamamlanan iş için progress (i/total) formatında satır yazar
- Tüm işlemin toplam süresini özet olarak gösterir
"""

import csv
import time
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Ayarlar
INPUT_FILE = "urls.txt"
OUTPUT_FILE = "site_summary.csv"
MAX_WORKERS = 10         # Aynı anda kaç site açılsın?
SCROLL_PAUSE = 2         # her scroll sonrası bekleme (saniye)
MAX_SCROLLS = 60         # maksimum scroll denemesi
VIDEO_PLAY_WAIT = 5      # video.play() sonrası bekleme (saniye)
HEADLESS = True          # False yaparsan tarayıcı görünür açılır

# ------------------------------
# Yardımcılar
# ------------------------------
def normalize_url(url: str) -> str:
    u = url.strip()
    if not u:
        return u
    if not u.startswith(("http://", "https://")):
        u = "https://" + u
    return u

def get_domain(url: str) -> str:
    parsed = urlparse(url)
    domain = parsed.netloc
    if ':' in domain:
        domain = domain.split(':', 1)[0]
    if domain.startswith("www."):
        domain = domain[4:]
    return domain

def create_driver():
    options = Options()
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--log-level=3")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def scroll_to_bottom(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    scrolls = 0
    while scrolls < MAX_SCROLLS:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        scrolls += 1

# ------------------------------
# Her bir URL için iş
# ------------------------------
def measure_url(url: str):
    """
    Döndürür: (domain, request_count, total_mb)
    """
    domain = get_domain(url)
    driver = None
    try:
        driver = create_driver()
        driver.requests.clear()
        driver.get(url)

        scroll_to_bottom(driver)

        try:
            driver.execute_script("""
            var vids = document.getElementsByTagName('video');
            for (let v of vids) {
                try { v.play(); } catch(e) {}
            }
            """)
        except Exception:
            pass

        time.sleep(VIDEO_PLAY_WAIT)

        total_bytes = 0
        response_count = 0

        for req in driver.requests:
            resp = req.response
            if not resp:
                continue
            response_count += 1

            length = None
            try:
                cl = resp.headers.get("Content-Length") or resp.headers.get("content-length")
                if cl:
                    length = int(cl)
                else:
                    try:
                        body = resp.body
                        if body:
                            length = len(body)
                    except Exception:
                        length = None
            except Exception:
                length = None

            if length is not None:
                total_bytes += length

        total_mb = round(total_bytes / (1024 * 1024), 3)
        return domain, response_count, total_mb

    except Exception:
        return domain, 0, 0.0
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass

# ------------------------------
# Ana akış
# ------------------------------
def main():
    start_time = time.time()

    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            raw = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"'{INPUT_FILE}' bulunamadı.")
        return

    urls = [normalize_url(u) for u in raw]
    total = len(urls)
    if total == 0:
        print("urls.txt içinde URL yok.")
        return

    results = []
    completed = 0

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        future_to_url = {ex.submit(measure_url, url): url for url in urls}
        for future in as_completed(future_to_url):
            completed += 1
            domain, count, total_mb = future.result()
            print(f"({completed}/{total}) {domain}: requests={count}, size={total_mb:.3f} MB")
            results.append((domain, count, total_mb))

    # CSV yaz
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["domain", "request_count", "total_mb"])
        for domain, count, total_mb in results:
            writer.writerow([domain, count, f"{total_mb:.3f}"])

    end_time = time.time()
    elapsed = end_time - start_time
    minutes, seconds = divmod(int(elapsed), 60)

    print(f"\n✅ Tamamlandı. Çıktı: {OUTPUT_FILE}")
    print(f"Toplam işlem süresi: {minutes} dakika {seconds} saniye")

if __name__ == "__main__":
    main()

