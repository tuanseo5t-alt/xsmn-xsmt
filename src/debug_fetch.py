import sys
from datetime import date
import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}

def debug(region="mien-nam", test_date=None):
    if test_date is None:
        test_date = date.today().strftime("%d-%m-%Y")
    url = f"https://www.minhngoc.net.vn/kqxs/{region}/{test_date}.html"
    print(f"URL: {url}\n")
    resp = requests.get(url, headers=HEADERS, timeout=30)
    print(f"Status: {resp.status_code}, Length: {len(resp.text)} chars\n")
    soup = BeautifulSoup(resp.text, "lxml")
    all_tables = soup.find_all("table")
    bkqxs = soup.find_all("table", class_="bkqxs")
    print(f"Tổng table: {len(all_tables)}, table.bkqxs: {len(bkqxs)}\n")
    for i, t in enumerate(all_tables[:5]):
        print(f"--- TABLE {i+1} | class={t.get('class','none')} ---")
        for j, row in enumerate(t.find_all("tr")[:6]):
            cells = [c.get_text(strip=True)[:25] for c in row.find_all(["td","th"])]
            print(f"  Row {j+1}: {cells}")
        print()

region = sys.argv[1] if len(sys.argv) > 1 else "mien-nam"
test_date = sys.argv[2] if len(sys.argv) > 2 else None
debug(region, test_date)