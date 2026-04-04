"""
storage.py - Lưu trữ dữ liệu xổ số vào CSV và JSON

Hỗ trợ cả XSMN và XSMT.
Tạo 3 định dạng:
  1. Raw (thô): tất cả giải theo ngày và đài
  2. 2-digits (lô tô): chỉ 2 chữ số cuối
  3. Sparse (thưa): ma trận 0/1 đếm tần suất 00-99
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

COLUMNS = [
    "date",
    "station",
    "special",
    "first",
    "second",
    "third",
    "fourth",
    "fifth",
    "sixth",
    "seventh",
    "eighth",
]

SPARSE_COLS = [f"{i:02d}" for i in range(100)]


def _last2(value: str) -> str:
    """Lấy 2 chữ số cuối của mỗi số trong chuỗi 'a, b, c'."""
    if not value:
        return ""
    parts = [p.strip() for p in value.split(",")]
    return ", ".join(p[-2:] if len(p) >= 2 else p.zfill(2) for p in parts if p)


def _to_2digits(record: dict) -> dict:
    """Chuyển đổi toàn bộ record sang 2 chữ số cuối."""
    r2 = {"date": record["date"], "station": record["station"]}
    for col in COLUMNS[2:]:
        r2[col] = _last2(record.get(col, ""))
    return r2


def _to_sparse_row(record: dict) -> dict:
    """Tạo dòng sparse (0/1) từ các số 2-chữ-số trong record."""
    row: dict = {"date": record["date"], "station": record["station"]}
    for col in SPARSE_COLS:
        row[col] = 0

    for col in COLUMNS[2:]:
        val = record.get(col, "")
        for part in val.split(","):
            part = part.strip()
            if len(part) == 2 and part.isdigit():
                row[part] = row.get(part, 0) + 1

    return row


def upsert(records: list[dict], data_dir: Path, prefix: str) -> None:
    """
    Thêm hoặc cập nhật các bản ghi vào file CSV/JSON.

    Args:
        records: Danh sách dict kết quả xổ số (mỗi dict là 1 đài 1 ngày)
        data_dir: Thư mục lưu file data/
        prefix: Tiền tố file (ví dụ: 'xsmn' hoặc 'xsmt')
    """
    if not records:
        logger.info("No records to save.")
        return

    data_dir.mkdir(parents=True, exist_ok=True)

    new_df = pd.DataFrame(records, columns=COLUMNS)
    new_df["date"] = pd.to_datetime(new_df["date"]).dt.strftime("%Y-%m-%d")

    # --- RAW ---
    raw_csv = data_dir / f"{prefix}.csv"
    raw_json = data_dir / f"{prefix}.json"
    _upsert_csv(new_df, raw_csv)
    _upsert_json(raw_csv, raw_json)
    logger.info("Saved raw: %s (%d new rows)", raw_csv, len(new_df))

    # --- 2 DIGITS ---
    new_2d = pd.DataFrame([_to_2digits(r) for r in records], columns=COLUMNS)
    two_csv = data_dir / f"{prefix}-2-digits.csv"
    two_json = data_dir / f"{prefix}-2-digits.json"
    _upsert_csv(new_2d, two_csv)
    _upsert_json(two_csv, two_json)
    logger.info("Saved 2-digits: %s", two_csv)

    # --- SPARSE ---
    sparse_cols = ["date", "station"] + SPARSE_COLS
    new_2d_for_sparse = pd.DataFrame([_to_2digits(r) for r in records], columns=COLUMNS)
    new_sparse = pd.DataFrame(
        [_to_sparse_row(r) for _, r in new_2d_for_sparse.iterrows()],
        columns=sparse_cols,
    )
    sparse_csv = data_dir / f"{prefix}-sparse.csv"
    sparse_json = data_dir / f"{prefix}-sparse.json"
    _upsert_csv(new_sparse, sparse_csv, key_cols=["date", "station"])
    _upsert_json(sparse_csv, sparse_json)
    logger.info("Saved sparse: %s", sparse_csv)


def _upsert_csv(new_df: pd.DataFrame, path: Path, key_cols: list[str] | None = None) -> None:
    """Ghép new_df vào file CSV hiện tại, loại bỏ trùng lặp theo (date, station)."""
    if key_cols is None:
        key_cols = ["date", "station"]

    if path.exists():
        existing = pd.read_csv(path, dtype=str)
        combined = pd.concat([existing, new_df], ignore_index=True)
        combined = combined.drop_duplicates(subset=key_cols, keep="last")
        combined = combined.sort_values(["date", "station"]).reset_index(drop=True)
    else:
        combined = new_df.sort_values(["date", "station"]).reset_index(drop=True)

    combined.to_csv(path, index=False)


def _upsert_json(csv_path: Path, json_path: Path) -> None:
    """Chuyển CSV thành JSON array."""
    df = pd.read_csv(csv_path, dtype=str).fillna("")
    records = df.to_dict(orient="records")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
