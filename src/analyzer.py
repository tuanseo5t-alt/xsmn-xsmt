"""
analyzer.py - Vẽ biểu đồ phân tích tần suất xổ số

Tạo các file ảnh JPG trong thư mục images/:
  - heatmap.jpg           : Bản đồ nhiệt tần suất lô tô (1 năm gần nhất)
  - top-10.jpg            : Top 10 số lô tô ra nhiều nhất
  - distribution.jpg      : Phân bổ tần suất 00-99
  - delta.jpg             : Số ngày từ lần ra cuối (lô tô)
  - delta_top_10.jpg      : Top 10 số lô tô lâu chưa ra
  - special_delta.jpg     : Số ngày từ lần ra cuối (giải đặc biệt)
  - special_delta_top_10.jpg : Top 10 giải đặc biệt lâu chưa ra
"""
from __future__ import annotations

import logging
from datetime import date, timedelta
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

matplotlib.use("Agg")

logger = logging.getLogger(__name__)

SPARSE_COLS = [f"{i:02d}" for i in range(100)]


def run(data_dir: Path, images_dir: Path, prefix: str) -> None:
    """
    Chạy toàn bộ phân tích và lưu biểu đồ.

    Args:
        data_dir: Thư mục chứa file CSV
        images_dir: Thư mục lưu ảnh
        prefix: Tiền tố file ('xsmn' hoặc 'xsmt')
    """
    images_dir.mkdir(parents=True, exist_ok=True)

    two_csv = data_dir / f"{prefix}-2-digits.csv"
    sparse_csv = data_dir / f"{prefix}-sparse.csv"

    if not two_csv.exists() or not sparse_csv.exists():
        logger.warning("Data files not found, skipping analysis.")
        return

    df2 = pd.read_csv(two_csv, dtype=str)
    df_sparse = pd.read_csv(sparse_csv)
    df_sparse["date"] = pd.to_datetime(df_sparse["date"])

    label = prefix.upper()

    _heatmap(df_sparse, images_dir, label)
    _top10(df_sparse, images_dir, label)
    _distribution(df_sparse, images_dir, label)
    _delta(df2, images_dir, label, "loto")
    _special_delta(df2, images_dir, label)

    logger.info("Analysis complete. Images saved to %s", images_dir)


def _heatmap(df_sparse: pd.DataFrame, images_dir: Path, label: str) -> None:
    """Bản đồ nhiệt tần suất lô tô - 1 năm gần nhất."""
    cutoff = df_sparse["date"].max() - timedelta(days=365)
    recent = df_sparse[df_sparse["date"] >= cutoff]

    freq = recent[SPARSE_COLS].sum().values.reshape(10, 10)
    labels = np.array(SPARSE_COLS).reshape(10, 10)

    fig, ax = plt.subplots(figsize=(12, 10))
    sns.heatmap(
        freq,
        annot=labels,
        fmt="",
        cmap="YlOrRd",
        ax=ax,
        linewidths=0.5,
        cbar_kws={"label": "Số lần xuất hiện"},
    )
    ax.set_title(f"{label} - Tần Suất Lô Tô (1 Năm Gần Nhất)", fontsize=14, pad=15)
    ax.set_xlabel("")
    ax.set_ylabel("")
    fig.tight_layout()
    path = images_dir / "heatmap.jpg"
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved %s", path)


def _top10(df_sparse: pd.DataFrame, images_dir: Path, label: str) -> None:
    """Top 10 số lô tô ra nhiều nhất trong 1 năm gần nhất."""
    cutoff = df_sparse["date"].max() - timedelta(days=365)
    recent = df_sparse[df_sparse["date"] >= cutoff]

    freq = recent[SPARSE_COLS].sum().sort_values(ascending=False)
    top10 = freq.head(10)

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(top10.index, top10.values, color=sns.color_palette("YlOrRd", 10))
    ax.bar_label(bars, padding=3)
    ax.set_title(f"{label} - Top 10 Số Lô Tô Ra Nhiều Nhất (1 Năm)", fontsize=14)
    ax.set_xlabel("Số")
    ax.set_ylabel("Số lần xuất hiện")
    fig.tight_layout()
    path = images_dir / "top-10.jpg"
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved %s", path)


def _distribution(df_sparse: pd.DataFrame, images_dir: Path, label: str) -> None:
    """Biểu đồ phân bổ tần suất toàn bộ lịch sử."""
    freq = df_sparse[SPARSE_COLS].sum()

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.bar(freq.index, freq.values, color="#4472C4", width=0.7)
    ax.set_title(f"{label} - Phân Bổ Tần Suất Lô Tô (Toàn Bộ Lịch Sử)", fontsize=14)
    ax.set_xlabel("Số (00-99)")
    ax.set_ylabel("Số lần xuất hiện")
    ax.set_xticks(range(0, 100, 5))
    ax.set_xticklabels([f"{i:02d}" for i in range(0, 100, 5)], rotation=45)
    fig.tight_layout()
    path = images_dir / "distribution.jpg"
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved %s", path)


def _delta(df2: pd.DataFrame, images_dir: Path, label: str, mode: str) -> None:
    """Số ngày kể từ lần ra cuối cùng của mỗi số lô tô."""
    today = date.today()
    last_seen: dict[str, date | None] = {col: None for col in SPARSE_COLS}

    df2_sorted = df2.sort_values("date")
    for _, row in df2_sorted.iterrows():
        row_date_str = str(row.get("date", ""))
        try:
            row_date = date.fromisoformat(row_date_str)
        except ValueError:
            continue

        for col in ["special", "first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth"]:
            val = str(row.get(col, ""))
            for part in val.split(","):
                part = part.strip()
                if len(part) == 2 and part.isdigit():
                    if last_seen[part] is None or row_date > last_seen[part]:
                        last_seen[part] = row_date

    deltas = {}
    for num, last_date in last_seen.items():
        if last_date:
            deltas[num] = (today - last_date).days
        else:
            deltas[num] = 9999

    delta_series = pd.Series(deltas).sort_index()

    fig, ax = plt.subplots(figsize=(14, 5))
    colors = ["#d62728" if v > 30 else "#ff7f0e" if v > 14 else "#2ca02c" for v in delta_series.values]
    ax.bar(delta_series.index, delta_series.values, color=colors, width=0.7)
    ax.axhline(y=30, color="red", linestyle="--", alpha=0.5, label="30 ngày")
    ax.set_title(f"{label} - Số Ngày Từ Lần Ra Cuối (Lô Tô)", fontsize=14)
    ax.set_xlabel("Số (00-99)")
    ax.set_ylabel("Số ngày chưa ra")
    ax.set_xticks(range(0, 100, 5))
    ax.set_xticklabels([f"{i:02d}" for i in range(0, 100, 5)], rotation=45)
    ax.legend()
    fig.tight_layout()
    path = images_dir / "delta.jpg"
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved %s", path)

    # Top 10 lâu nhất
    top10 = delta_series[delta_series < 9999].sort_values(ascending=False).head(10)
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    bars = ax2.bar(top10.index, top10.values, color="#d62728")
    ax2.bar_label(bars, padding=3, fmt="%d ngày")
    ax2.set_title(f"{label} - Top 10 Số Lô Tô Lâu Chưa Ra", fontsize=14)
    ax2.set_xlabel("Số")
    ax2.set_ylabel("Số ngày")
    fig2.tight_layout()
    path2 = images_dir / "delta_top_10.jpg"
    fig2.savefig(path2, dpi=120, bbox_inches="tight")
    plt.close(fig2)
    logger.info("Saved %s", path2)


def _special_delta(df2: pd.DataFrame, images_dir: Path, label: str) -> None:
    """Số ngày từ lần ra cuối của từng cặp số 2-chữ-số giải đặc biệt."""
    today = date.today()
    last_seen: dict[str, date | None] = {col: None for col in SPARSE_COLS}

    df2_sorted = df2.sort_values("date")
    for _, row in df2_sorted.iterrows():
        row_date_str = str(row.get("date", ""))
        try:
            row_date = date.fromisoformat(row_date_str)
        except ValueError:
            continue

        val = str(row.get("special", ""))
        for part in val.split(","):
            part = part.strip()
            if len(part) == 2 and part.isdigit():
                if last_seen[part] is None or row_date > last_seen[part]:
                    last_seen[part] = row_date

    deltas = {}
    for num, last_date in last_seen.items():
        if last_date:
            deltas[num] = (today - last_date).days
        else:
            deltas[num] = 9999

    delta_series = pd.Series(deltas).sort_index()

    fig, ax = plt.subplots(figsize=(14, 5))
    colors = ["#d62728" if v > 60 else "#ff7f0e" if v > 30 else "#2ca02c" for v in delta_series.values]
    ax.bar(delta_series.index, delta_series.values, color=colors, width=0.7)
    ax.axhline(y=60, color="red", linestyle="--", alpha=0.5, label="60 ngày")
    ax.set_title(f"{label} - Số Ngày Từ Lần Ra Cuối (Giải Đặc Biệt - 2 Số Cuối)", fontsize=14)
    ax.set_xlabel("2 Số Cuối Giải Đặc Biệt")
    ax.set_ylabel("Số ngày")
    ax.set_xticks(range(0, 100, 5))
    ax.set_xticklabels([f"{i:02d}" for i in range(0, 100, 5)], rotation=45)
    ax.legend()
    fig.tight_layout()
    path = images_dir / "special_delta.jpg"
    fig.savefig(path, dpi=120, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved %s", path)

    top10 = delta_series[delta_series < 9999].sort_values(ascending=False).head(10)
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    bars = ax2.bar(top10.index, top10.values, color="#d62728")
    ax2.bar_label(bars, padding=3, fmt="%d ngày")
    ax2.set_title(f"{label} - Top 10 Giải Đặc Biệt Lâu Chưa Ra", fontsize=14)
    ax2.set_xlabel("2 Số Cuối")
    ax2.set_ylabel("Số ngày")
    fig2.tight_layout()
    path2 = images_dir / "special_delta_top_10.jpg"
    fig2.savefig(path2, dpi=120, bbox_inches="tight")
    plt.close(fig2)
    logger.info("Saved %s", path2)
