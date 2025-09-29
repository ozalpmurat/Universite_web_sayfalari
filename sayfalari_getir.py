import os
import csv
from urllib.parse import urlparse
from selenium import webdriver
from concurrent.futures import ThreadPoolExecutor, as_completed

INPUT_FILE = "urls.txt"
OUTPUT_FILE = "site_sizes.csv"
SAVE_DIR = "icerikler"
MAX_WORKERS = 4  # Aynı anda kaç site indirilecek

os.makedirs(SAVE_DIR, exist_ok=True)

def normalize_url(url: str) -> str:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url

def get_domain(url: str) -> str:
    parsed = urlparse(url)
    domain = parsed.netloc
    if domain.startswith("www."):
        domain = domain[4:]
    return domain

def save_as_mhtml(url: str) -> tuple:
    """MHT kaydet ve boyutunu MB cinsinden döndür. CSV’ye yazmak için tuple döner"""
    domain = get_domain(url)
    filepath = os.path.join(SAVE_DIR, f"{domain}.mht")
    
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)
        devtools = driver.execute_cdp_cmd("Page.captureSnapshot", {"format": "mhtml"})
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(devtools["data"])
        size_mb = round(os.path.getsize(filepath) / (1024 * 1024), 3)
        print(f"Tamamlandı: {domain} ({size_mb} MB)")
        return (url, size_mb)
    except Exception as e:
        print(f"Hata: {url} -> {e}")
        return (url, "Hata")
    finally:
        driver.quit()

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        urls = [normalize_url(line) for line in f if line.strip()]

    results = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_url = {executor.submit(save_as_mhtml, url): url for url in urls}
        for future in as_completed(future_to_url):
            results.append(future.result())

    # CSV’ye yaz
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["URL", "Boyut (MB)"])
        for row in results:
            writer.writerow(row)

    print(f"\nTamamlandı. Sonuçlar:\n- CSV: {OUTPUT_FILE}\n- MHT klasörü: {SAVE_DIR}/")

if __name__ == "__main__":
    main()

