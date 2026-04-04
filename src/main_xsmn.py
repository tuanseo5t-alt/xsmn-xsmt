"""
main_xsmn.py - Điều phối thu thập dữ liệu Xổ Số Miền Nam (XSMN)

Cách dùng:
  # Lấy dữ liệu ngày hôm nay:
  python src/main_xsmn.py

  # Lấy dữ liệu từ ngày cụ thể:
  python src/main_xsmn.py --from 2024-01-01

  # Lấy khoảng ngày:
  python src/main_xsmn.py --from 2024-01-01 --to 2024-06-30

  # Lấy toàn bộ lịch sử từ 01/01/2008:
  python src/main_xsmn.py --all

  # Tắt phân tích biểu đồ:
  python src/main_xsmn.py --no-analyze

  # Điều chỉnh thời gian chờ giữa mỗi lần tải (giây):
  python src/main_xsmn.py --all --delay 2.0
"""
from __future__ import annotations

import argparse
import logging
import sys
from datetime import date
from pathlib import Path

import fetcher_xsmn
import storage
import analyzer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

PREFIX = "xsmn"
DATA_DIR = Path(__file__).parent.parent / "data" / "xsmn"
IMAGES_DIR = Path(__file__).parent.parent / "images" / "xsmn"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Thu thập dữ liệu Xổ Số Miền Nam")
    parser.add_argument(
        "--all",
        action="store_true",
        help=f"Lấy toàn bộ lịch sử từ {fetcher_xsmn.START_DATE} đến hôm nay",
    )
    parser.add_argument(
        "--from",
        dest="from_date",
        type=date.fromisoformat,
        help="Ngày bắt đầu (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--to",
        dest="to_date",
        type=date.fromisoformat,
        default=date.today(),
        help="Ngày kết thúc (YYYY-MM-DD, mặc định: hôm nay)",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.5,
        help="Thời gian chờ giữa mỗi lần tải (giây, mặc định: 1.5)",
    )
    parser.add_argument(
        "--no-analyze",
        action="store_true",
        help="Bỏ qua bước vẽ biểu đồ",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.all:
        from_date = fetcher_xsmn.START_DATE
        to_date = date.today()
    elif args.from_date:
        from_date = args.from_date
        to_date = args.to_date
    else:
        from_date = date.today()
        to_date = date.today()

    days = fetcher_xsmn.date_range(from_date, to_date)
    logger.info(
        "XSMN: Sẽ lấy dữ liệu %d ngày, từ %s đến %s",
        len(days),
        from_date,
        to_date,
    )

    all_records: list[dict] = []
    for i, day in enumerate(days, 1):
        records = fetcher_xsmn.fetch_day(day, delay=args.delay)
        if records:
            all_records.extend(records)
            logger.info(
                "[%d/%d] %s - Tìm thấy %d đài",
                i,
                len(days),
                day,
                len(records),
            )
        else:
            logger.debug("[%d/%d] %s - Không có dữ liệu", i, len(days), day)

        # Lưu theo từng batch 100 ngày để không mất dữ liệu nếu bị gián đoạn
        if len(all_records) >= 100 or i == len(days):
            if all_records:
                storage.upsert(all_records, DATA_DIR, PREFIX)
                all_records = []

    if not args.no_analyze:
        logger.info("Bắt đầu phân tích và vẽ biểu đồ XSMN...")
        analyzer.run(DATA_DIR, IMAGES_DIR, PREFIX)

    logger.info("XSMN: Hoàn tất!")


if __name__ == "__main__":
    main()
