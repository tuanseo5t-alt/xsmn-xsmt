import requests
from bs4 import BeautifulSoup
from datetime import date

url = "https://www.minhngoc.net.vn/kqxs/mien-nam/" + date.today().strftime("%d-%m-%Y") + ".html"
r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
soup = BeautifulSoup(r.text, "lxml")

# Tim tat ca table co hang chua "Đặc Biệt" va so lien ke
for i, t in enumerate(soup.find_all("table")):
    rows = t.find_all("tr")
    for row in rows:
        cells = row.find_all(["td", "th"])
        texts = [c.get_text(strip=True) for c in cells]
        if any("Đặc Biệt" in x or "ĐB" in x for x in texts):
            print(f"TABLE {i} | class={t.get('class')}")
            for j, r2 in enumerate(rows[:12]):
                cc = [c.get_text(strip=True)[:25] for c in r2.find_all(["td","th"])]
                print(f"  Row {j}: {cc}")
            print()
            break