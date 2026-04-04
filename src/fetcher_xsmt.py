from __future__ import annotations
import logging, re, time
from datetime import date, timedelta
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
BASE_URL = "https://www.minhngoc.net.vn/kqxs/mien-trung/{date}.html"
START_DATE = date(2009, 1, 27)
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}

PRIZE_MAP = [
    (["đặc biệt", "giải đb", "đb"], "special"),
    (["giải nhất", "nhất"], "first"),
    (["giải nhì", "nhì"], "second"),
    (["giải ba"], "third"),
    (["giải tư"], "fourth"),
    (["giải năm"], "fifth"),
    (["giải sáu"], "sixth"),
    (["giải bảy"], "seventh"),
    (["giải 8", "giải tám"], "eighth"),
]

STATION_CODE_MAP = {
    "XSTTH": "Thừa Thiên Huế", "XSDLK": "Đắk Lắk", "XSQNM": "Quảng Nam",
    "XSDNG": "Đà Nẵng", "XSQNG": "Quảng Ngãi", "XSBDI": "Bình Định",
    "XSQB": "Quảng Bình", "XSQT": "Quảng Trị", "XSGL": "Gia Lai",
    "XSNT": "Ninh Thuận", "XSKT": "Kon Tum", "XSKH": "Khánh Hòa",
    "XSPY": "Phú Yên",
}

DAY_NAMES = {"thứ hai","thứ ba","thứ tư","thứ năm","thứ sáu","thứ bảy","chủ nhật"}

def fetch_day(target_date: date, delay: float = 1.0) -> list[dict]:
    date_str = target_date.strftime("%d-%m-%Y")
    url = BASE_URL.format(date=date_str)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("Failed: %s %s", url, exc)
        return []
    time.sleep(delay)
    return _parse_page(resp.text, target_date)

def _parse_page(html, target_date):
    soup = BeautifulSoup(html, "lxml")
    results = []
    for t in soup.find_all("table", class_="bkqtinhmiennam"):
        r = _parse_station_table(t, target_date)
        if r:
            results.append(r)
    if not results:
        for idx, pt in enumerate(soup.find_all("table", class_="box_kqxs_content")):
            r = _parse_prize_table(pt, target_date, f"Đài {idx+1}")
            if r:
                results.append(r)
    return results

def _parse_station_table(station_table, target_date):
    rows = station_table.find_all("tr")
    if not rows:
        return None
    name = _extract_station_name(rows[0])
    if not name:
        return None
    pt = station_table.find("table", class_="box_kqxs_content") or station_table
    return _parse_prize_table(pt, target_date, name)

def _parse_prize_table(prize_table, target_date, station_name):
    record = {
        "date": target_date.strftime("%Y-%m-%d"), "station": station_name,
        "special":"","first":"","second":"","third":"",
        "fourth":"","fifth":"","sixth":"","seventh":"","eighth":"",
    }
    for row in prize_table.find_all("tr"):
        cells = row.find_all(["td","th"])
        if len(cells) < 2:
            continue
        key = _match_prize(cells[0].get_text(strip=True).lower())
        if not key:
            continue
        nums = re.findall(r"\d+", cells[1].get_text(" ", strip=True))
        if nums:
            record[key] = ", ".join(nums)
    has_data = any(record[k] for k in ["special","first","second","third","fourth","fifth","sixth","seventh","eighth"])
    return record if has_data else None

def _extract_station_name(header_row):
    raw = header_row.get_text(strip=True)
    for code in sorted(STATION_CODE_MAP, key=len, reverse=True):
        if code in raw:
            return STATION_CODE_MAP[code]
    for a in header_row.find_all("a"):
        name = a.get_text(strip=True)
        if name and name.lower() not in DAY_NAMES and len(name) > 3:
            return name
    m = re.search(r"Ngày:\d{2}/\d{2}/\d{4}(.+)$", raw)
    return m.group(1).strip() if m else ""

def _match_prize(label):
    for keywords, key in PRIZE_MAP:
        if any(kw in label for kw in keywords):
            return key
    return None

def date_range(from_date, to_date):
    days, cur = [], from_date
    while cur <= to_date:
        days.append(cur)
        cur += timedelta(days=1)
    return days