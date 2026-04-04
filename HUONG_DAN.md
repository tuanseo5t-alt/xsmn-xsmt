# Hướng Dẫn Chi Tiết - Dự Án Thu Thập Dữ Liệu XSMN & XSMT

> Dành cho người chưa biết gì về lập trình. Làm theo từng bước một.

---

## Mục Lục

1. [Bạn cần chuẩn bị gì?](#1-bạn-cần-chuẩn-bị-gì)
2. [Tổng quan dự án - File nào làm gì?](#2-tổng-quan-dự-án---file-nào-làm-gì)
3. [Bước 1: Tạo tài khoản GitHub](#3-bước-1-tạo-tài-khoản-github)
4. [Bước 2: Tạo repository (kho chứa code)](#4-bước-2-tạo-repository-kho-chứa-code)
5. [Bước 3: Upload code lên GitHub](#5-bước-3-upload-code-lên-github)
6. [Bước 4: Chạy lần đầu - Lấy toàn bộ lịch sử](#6-bước-4-chạy-lần-đầu---lấy-toàn-bộ-lịch-sử)
7. [Bước 5: Cài đặt tự động chạy mỗi ngày](#7-bước-5-cài-đặt-tự-động-chạy-mỗi-ngày)
8. [Cách dùng dữ liệu (API)](#8-cách-dùng-dữ-liệu-api)
9. [Giải thích từng file code](#9-giải-thích-từng-file-code)
10. [Các lỗi thường gặp](#10-các-lỗi-thường-gặp)
11. [Chạy trên máy tính cá nhân](#11-chạy-trên-máy-tính-cá-nhân)

---

## 1. Bạn Cần Chuẩn Bị Gì?

### Tài khoản cần có:
- **GitHub** (miễn phí): https://github.com - Nơi lưu code và chạy tự động

### Không cần cài gì thêm!
GitHub Actions (tính năng tự động hóa của GitHub) sẽ chạy tất cả, bạn chỉ cần tài khoản GitHub là đủ.

> **Ghi chú**: Nếu muốn chạy thử trên máy tính cá nhân, xem thêm [phần 11](#11-chạy-trên-máy-tính-cá-nhân)

---

## 2. Tổng Quan Dự Án - File Nào Làm Gì?

```
xsmn-xsmt/
│
├── src/                            ← Folder chứa code Python chính
│   ├── main_xsmn.py               ← Điều phối thu thập XSMN (Miền Nam)
│   ├── main_xsmt.py               ← Điều phối thu thập XSMT (Miền Trung)
│   ├── fetcher_xsmn.py            ← Lấy dữ liệu XSMN từ minhngoc.net.vn
│   ├── fetcher_xsmt.py            ← Lấy dữ liệu XSMT từ minhngoc.net.vn
│   ├── storage.py                 ← Lưu dữ liệu vào file CSV và JSON
│   └── analyzer.py                ← Vẽ biểu đồ phân tích
│
├── data/                          ← Folder chứa dữ liệu (tự động tạo)
│   ├── xsmn/                      ← Dữ liệu Miền Nam
│   │   ├── xsmn.csv               ← Dữ liệu thô: tất cả các giải, theo ngày và đài
│   │   ├── xsmn.json              ← Dữ liệu thô dạng JSON
│   │   ├── xsmn-2-digits.csv      ← Chỉ 2 chữ số cuối (dùng cho lô tô)
│   │   ├── xsmn-2-digits.json     ← 2 chữ số cuối dạng JSON
│   │   ├── xsmn-sparse.csv        ← Đếm tần suất: 100 cột cho 100 số
│   │   └── xsmn-sparse.json       ← Tần suất dạng JSON
│   │
│   └── xsmt/                      ← Dữ liệu Miền Trung
│       ├── xsmt.csv
│       ├── xsmt.json
│       ├── xsmt-2-digits.csv
│       ├── xsmt-2-digits.json
│       ├── xsmt-sparse.csv
│       └── xsmt-sparse.json
│
├── images/                        ← Folder chứa biểu đồ (tự động tạo)
│   ├── xsmn/                      ← Biểu đồ Miền Nam
│   │   ├── heatmap.jpg
│   │   ├── top-10.jpg
│   │   ├── distribution.jpg
│   │   ├── delta.jpg
│   │   ├── delta_top_10.jpg
│   │   ├── special_delta.jpg
│   │   └── special_delta_top_10.jpg
│   │
│   └── xsmt/                      ← Biểu đồ Miền Trung
│       └── (tương tự như xsmn)
│
├── .github/
│   └── workflows/
│       ├── fetch-xsmn.yml         ← Tự động chạy XSMN hàng ngày lúc 19:00
│       ├── fetch-xsmt.yml         ← Tự động chạy XSMT hàng ngày lúc 19:30
│       ├── backfill-xsmn.yml      ← Công cụ lấy lịch sử XSMN (từ 2008)
│       └── backfill-xsmt.yml      ← Công cụ lấy lịch sử XSMT (từ 2009)
│
├── requirements.txt               ← Danh sách thư viện Python cần cài
├── pyproject.toml                 ← Cấu hình dự án Python
├── README.md                      ← Trang giới thiệu dự án
└── HUONG_DAN.md                   ← File bạn đang đọc
```

### Quy trình hoạt động:

```
GitHub Actions chạy lúc 19:00 (XSMN) và 19:30 (XSMT) mỗi ngày
         ↓
   main_xsmn.py / main_xsmt.py được gọi
         ↓
   fetcher_xsmn.py / fetcher_xsmt.py tải trang minhngoc.net.vn
         ↓
   Phân tích HTML, trích xuất kết quả của từng đài
         ↓
   storage.py lưu vào data/xsmn/ (hoặc data/xsmt/)
         ↓
   analyzer.py vẽ biểu đồ → images/xsmn/ (hoặc images/xsmt/)
         ↓
   GitHub Actions tự commit và push lên GitHub
         ↓
   Người dùng tải file CSV/JSON qua URL công khai
```

---

## 3. Bước 1: Tạo Tài Khoản GitHub

1. Truy cập https://github.com
2. Nhấn **"Sign up"** (Đăng ký)
3. Điền email, mật khẩu, tên người dùng
4. Xác nhận email
5. Đăng nhập vào GitHub

---

## 4. Bước 2: Tạo Repository (Kho Chứa Code)

1. Sau khi đăng nhập, nhấn dấu **"+"** ở góc trên phải
2. Chọn **"New repository"**
3. Điền thông tin:
   - **Repository name**: `xsmn-xsmt` (hoặc tên khác bạn muốn)
   - **Description**: `Thu thập kết quả Xổ Số Miền Nam và Miền Trung tự động`
   - Chọn **Public** (công khai - để người khác tải dữ liệu được)
   - **Tick vào** "Add a README file"
4. Nhấn **"Create repository"**

---

## 5. Bước 3: Upload Code Lên GitHub

### Cách 1 - Dùng GitHub Desktop (Khuyến nghị cho người mới):

1. Tải GitHub Desktop tại: https://desktop.github.com
2. Đăng nhập bằng tài khoản GitHub
3. Nhấn **"Clone a repository"** → chọn repository vừa tạo
4. Chọn thư mục lưu trên máy → nhấn **"Clone"**
5. Copy **toàn bộ** thư mục `xsmn-xsmt` vào thư mục vừa clone
6. Trong GitHub Desktop:
   - Điền "Summary": `Thêm code thu thập XSMN và XSMT`
   - Nhấn **"Commit to main"**
   - Nhấn **"Push origin"**

### Cách 2 - Tạo file trực tiếp trên GitHub Web:

Vào repository → nhấn **"Add file"** → **"Create new file"**
- Gõ đường dẫn ví dụ: `src/fetcher_xsmn.py`
- Dán nội dung file vào
- Nhấn **"Commit new file"**

Lặp lại cho từng file theo cấu trúc thư mục ở trên.

> **Quan trọng**: Khi tạo file trong thư mục con, gõ tên thư mục + "/" trước tên file.
> Ví dụ: `.github/workflows/fetch-xsmn.yml`

---

## 6. Bước 4: Chạy Lần Đầu - Lấy Toàn Bộ Lịch Sử

### Lấy dữ liệu XSMN (từ 01/01/2008):

1. Vào repository trên GitHub
2. Nhấn tab **"Actions"**
3. Ở menu bên trái, tìm **"Backfill Historical XSMN Data"**
4. Nhấn **"Run workflow"** (nút bên phải)
5. Điền thông tin:
   - **from_date**: `2008-01-01`
   - **to_date**: để trống (tự động lấy đến hôm nay)
   - **delay**: `2.0`
   - **no_analyze**: `true` (tắt vẽ biểu đồ để chạy nhanh hơn)
6. Nhấn **"Run workflow"** màu xanh

### Lấy dữ liệu XSMT (từ 27/01/2009):

Làm tương tự nhưng chọn **"Backfill Historical XSMT Data"**:
- **from_date**: `2009-01-27`
- **to_date**: để trống
- **delay**: `2.0`
- **no_analyze**: `true`

> **Thời gian ước tính**:
> - XSMN: ~5-8 tiếng (hơn 6.000 ngày x nhiều đài)
> - XSMT: ~4-6 tiếng (hơn 5.500 ngày x nhiều đài)
>
> GitHub Actions miễn phí có **2.000 phút/tháng**, đủ dùng cho backfill.
> Sau đó, chạy hàng ngày chỉ tốn ~2-5 phút.

---

## 7. Bước 5: Cài Đặt Tự Động Chạy Mỗi Ngày

Các file `.github/workflows/fetch-xsmn.yml` và `fetch-xsmt.yml` đã được cấu hình để:
- **XSMN**: Tự động chạy lúc **19:00 giờ Việt Nam** mỗi ngày
- **XSMT**: Tự động chạy lúc **19:30 giờ Việt Nam** mỗi ngày

**Bạn không cần làm gì thêm!** Chỉ cần đảm bảo:

1. Workflow đã được bật:
   - Vào tab **Actions**
   - Nếu thấy thông báo "Workflows aren't being run" → nhấn **"I understand my workflows, go ahead and enable them"**

2. Repository đang ở chế độ **Public**

---

## 8. Cách Dùng Dữ Liệu (API)

Sau khi có dữ liệu, bất kỳ ai cũng có thể tải về qua URL trực tiếp.

### URL mẫu (thay YOUR_USERNAME và YOUR_REPO):

**XSMN:**
```
https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/data/xsmn/xsmn.csv
https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/data/xsmn/xsmn.json
https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/data/xsmn/xsmn-2-digits.csv
https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/data/xsmn/xsmn-sparse.csv
```

**XSMT:**
```
https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/data/xsmt/xsmt.csv
https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/data/xsmt/xsmt.json
https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/data/xsmt/xsmt-2-digits.csv
https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/data/xsmt/xsmt-sparse.csv
```

### Ví dụ dùng Python:

```python
import pandas as pd

BASE = "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/data"

# === XSMN ===
df_xsmn = pd.read_csv(f"{BASE}/xsmn/xsmn.csv")

# Xem 5 dòng đầu
print(df_xsmn.head())

# Lọc theo ngày
df_2024 = df_xsmn[df_xsmn['date'] >= '2024-01-01']

# Lọc theo đài
df_vt = df_xsmn[df_xsmn['station'].str.contains('Vũng Tàu', case=False)]

# Xem giải đặc biệt của TP.HCM
df_hcm = df_xsmn[df_xsmn['station'].str.contains('Hồ Chí Minh', case=False)]
print(df_hcm[['date', 'special']].tail(10))

# === XSMT ===
df_xsmt = pd.read_csv(f"{BASE}/xsmt/xsmt.csv")
df_hue = df_xsmt[df_xsmt['station'].str.contains('Huế', case=False)]
```

### Ví dụ dùng JavaScript/Node.js:

```javascript
const BASE = "https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/data";

// XSMN
const res = await fetch(`${BASE}/xsmn/xsmn.json`);
const data = await res.json();

// Lọc theo đài
const canTho = data.filter(r => r.station.includes('Cần Thơ'));
console.log("5 kết quả gần nhất Cần Thơ:", canTho.slice(-5));

// XSMT - lấy kết quả Đà Nẵng
const res2 = await fetch(`${BASE}/xsmt/xsmt.json`);
const data2 = await res2.json();
const daNang = data2.filter(r => r.station.includes('Đà Nẵng'));
```

### Ví dụ dùng Excel:

1. Mở Excel
2. Vào tab **Data** → **Get Data** → **From Web**
3. Dán URL của file CSV vào (ví dụ: URL của `xsmn.csv`)
4. Nhấn OK → Load

---

## 9. Giải Thích Từng File Code

### `src/fetcher_xsmn.py` và `src/fetcher_xsmt.py` - Bộ Thu Thập Dữ Liệu

**Mục đích**: Vào trang minhngoc.net.vn, đọc bảng kết quả xổ số, trích xuất số ra của từng đài.

**Cách hoạt động**:
1. Tạo URL từ ngày cần lấy:
   - XSMN: `https://www.minhngoc.net.vn/kqxs/mien-nam/01-01-2024.html`
   - XSMT: `https://www.minhngoc.net.vn/kqxs/mien-trung/01-01-2024.html`
2. Tải nội dung trang web về
3. Phân tích HTML, tìm **từng bảng** (mỗi bảng = 1 đài)
4. Trích xuất tên đài và các số trong từng giải
5. Trả về danh sách kết quả, mỗi phần tử là 1 đài

**Ví dụ dữ liệu trả về**:
```python
[
    {"date": "2024-01-01", "station": "Vũng Tàu", "special": "12345", "first": "67890", ...},
    {"date": "2024-01-01", "station": "Cần Thơ", "special": "54321", "first": "09876", ...},
]
```

**Công cụ chính**:
- `requests`: Thư viện gửi yêu cầu HTTP (như trình duyệt web nhưng không hiện giao diện)
- `BeautifulSoup` + `lxml`: Thư viện đọc và phân tích HTML

---

### `src/storage.py` - Bộ Lưu Trữ Dữ Liệu

**Mục đích**: Nhận dữ liệu từ fetcher và lưu vào 3 định dạng file.

**3 định dạng file** (ví dụ cho XSMN):

**1. `xsmn.csv` / `xsmn.json`** (Dữ liệu thô - Raw):
```
date,station,special,first,second,...
2024-01-01,Vũng Tàu,12345,67890,"11111, 22222",...
2024-01-01,Cần Thơ,54321,09876,"33333, 44444",...
```
→ Dữ liệu đầy đủ nhất, có tên đài, tất cả giải theo ngày.

**2. `xsmn-2-digits.csv`** (Chỉ 2 chữ số cuối - Lô tô):
```
date,station,special,first,...
2024-01-01,Vũng Tàu,45,90,"11, 22",...
```
→ Số 12345 → lấy 2 chữ số cuối = **45**. Dùng cho phân tích lô tô.

**3. `xsmn-sparse.csv`** (Dạng thưa - Sparse, đếm tần suất):
```
date,station,00,01,02,...,99
2024-01-01,Vũng Tàu,0,0,0,...,1,...
```
→ Số nào xuất hiện thì cột đó = 1. Dùng để tính tần suất nhanh.

**Cơ chế chống trùng lặp**: Khi thêm dữ liệu mới, tự động kiểm tra và không ghi đè nếu (date + station) đã tồn tại.

**Công cụ chính**:
- `pandas`: Thư viện mạnh nhất để xử lý bảng dữ liệu trong Python

---

### `src/analyzer.py` - Bộ Phân Tích và Vẽ Biểu Đồ

**Mục đích**: Đọc dữ liệu CSV và tạo các biểu đồ thống kê.

**Các biểu đồ tạo ra** (trong `images/xsmn/` và `images/xsmt/`):

| File ảnh | Mô tả |
|----------|-------|
| `heatmap.jpg` | Bản đồ nhiệt: màu đậm = số ra nhiều, màu nhạt = số ra ít (1 năm gần nhất) |
| `top-10.jpg` | Biểu đồ cột: 10 số Lô Tô ra nhiều nhất |
| `distribution.jpg` | Phân bổ tần suất của 100 số từ 00-99 (toàn bộ lịch sử) |
| `delta.jpg` | Số ngày kể từ lần ra cuối cùng của mỗi số lô tô |
| `delta_top_10.jpg` | Top 10 số lâu nhất chưa ra (số "nợ" nhiều nhất) |
| `special_delta.jpg` | Như delta.jpg nhưng chỉ cho 2 số cuối Giải Đặc Biệt |
| `special_delta_top_10.jpg` | Top 10 Giải Đặc Biệt lâu chưa ra |

**Công cụ chính**:
- `matplotlib`: Thư viện vẽ biểu đồ cơ bản nhất trong Python
- `seaborn`: Thư viện vẽ biểu đồ đẹp hơn (xây trên matplotlib)
- `numpy`: Thư viện tính toán số học tốc độ cao

---

### `src/main_xsmn.py` và `src/main_xsmt.py` - Điều Phối Chính

**Mục đích**: Nhận lệnh từ người dùng hoặc GitHub Actions, gọi các module theo đúng thứ tự.

**Các lệnh có thể dùng**:
```bash
# Chạy cho ngày hôm nay
python src/main_xsmn.py

# Chạy từ một ngày cụ thể đến hôm nay
python src/main_xsmn.py --from 2024-01-01

# Chạy toàn bộ lịch sử
python src/main_xsmn.py --all

# Chạy toàn bộ lịch sử, không vẽ biểu đồ (nhanh hơn)
python src/main_xsmn.py --all --no-analyze

# Tùy chỉnh thời gian chờ (giây) giữa mỗi lần tải
python src/main_xsmn.py --all --delay 2.0
```

---

### `.github/workflows/fetch-xsmn.yml` và `fetch-xsmt.yml` - Lịch Chạy Tự Động

**Mục đích**: Nói với GitHub "chạy script này mỗi ngày lúc mấy giờ".

**Cú pháp lịch (cron)**:
```
"0 12 * * *"    ← XSMN chạy lúc 12:00 UTC = 19:00 Việt Nam
"30 12 * * *"   ← XSMT chạy lúc 12:30 UTC = 19:30 Việt Nam
 │  │  │ │ └─── Ngày trong tuần (* = mọi ngày)
 │  │  │ └───── Tháng (* = mọi tháng)
 │  │  └─────── Ngày trong tháng (* = mọi ngày)
 │  └────────── Giờ (UTC)
 └──────────── Phút
```

---

### `.github/workflows/backfill-xsmn.yml` và `backfill-xsmt.yml` - Công Cụ Lấy Lịch Sử

**Mục đích**: Chạy thủ công một lần để lấy toàn bộ dữ liệu lịch sử từ năm 2008/2009.

**Các tham số có thể điền**:
- `from_date`: Ngày bắt đầu (mặc định: 2008-01-01 cho XSMN, 2009-01-27 cho XSMT)
- `to_date`: Ngày kết thúc (để trống = hôm nay)
- `delay`: Thời gian chờ giữa mỗi lần tải (mặc định: 2.0 giây)
- `no_analyze`: Có bỏ qua vẽ biểu đồ không (nên chọn `true` khi backfill)

---

### `requirements.txt` - Danh Sách Thư Viện

Liệt kê tất cả thư viện Python cần cài:

```
requests         → Gửi yêu cầu HTTP (tải trang web)
beautifulsoup4   → Đọc và phân tích HTML
lxml             → Parser HTML nhanh (dùng với BeautifulSoup)
pandas           → Xử lý dữ liệu dạng bảng (đọc/ghi CSV)
numpy            → Tính toán số học tốc độ cao
matplotlib       → Vẽ biểu đồ
seaborn          → Vẽ biểu đồ đẹp hơn
```

---

## 10. Các Lỗi Thường Gặp

### Lỗi: "Workflows aren't being run on this forked repository"

**Nguyên nhân**: GitHub tắt Actions trên repository mới để bảo mật.

**Cách sửa**:
1. Vào tab **Actions**
2. Nhấn **"I understand my workflows, go ahead and enable them"**

---

### Lỗi: "Permission denied" khi commit

**Nguyên nhân**: Workflow không có quyền push vào repository.

**Cách sửa**:
1. Vào repository → **Settings** → **Actions** → **General**
2. Phần "Workflow permissions" → chọn **"Read and write permissions"**
3. Nhấn **Save**

---

### Lỗi: Không tìm thấy dữ liệu cho một số ngày

**Nguyên nhân**: Ngày đó không có xổ số (lễ, tết) hoặc trang web thay đổi cấu trúc.

**Cách xử lý**: Code đã được viết để bỏ qua các ngày không có dữ liệu, tiếp tục với ngày tiếp theo.

---

### Lỗi: GitHub Actions bị timeout sau 6 tiếng

**Nguyên nhân**: Backfill quá nhiều ngày trong một lần chạy.

**Cách sửa**: Chia nhỏ khoảng thời gian. Ví dụ:
- Lần 1: `from_date = 2008-01-01`, `to_date = 2012-12-31`
- Lần 2: `from_date = 2013-01-01`, `to_date = 2017-12-31`
- Lần 3: `from_date = 2018-01-01`, `to_date = 2022-12-31`
- Lần 4: `from_date = 2023-01-01`, `to_date = (để trống)`

---

### Lỗi: Dữ liệu bị trùng lặp

**Giải thích**: Code đã tự xử lý. Nếu (date + station) đã tồn tại trong CSV, dữ liệu mới sẽ **ghi đè** dữ liệu cũ (không nhân đôi).

---

## 11. Chạy Trên Máy Tính Cá Nhân

Nếu muốn thử nghiệm trước khi đưa lên GitHub:

### Bước 1: Cài Python

Tải Python 3.11+ tại: https://www.python.org/downloads/

Khi cài đặt, **tick vào "Add Python to PATH"**.

### Bước 2: Mở Terminal (Command Prompt)

- Windows: Nhấn `Win + R`, gõ `cmd`, nhấn Enter
- Mac: Tìm "Terminal" trong Spotlight

### Bước 3: Di chuyển đến thư mục dự án

```bash
cd đường/dẫn/đến/thư/mục/xsmn-xsmt
```

### Bước 4: Cài thư viện

```bash
pip install -r requirements.txt
```

### Bước 5: Chạy thử

```bash
# Lấy dữ liệu XSMN hôm nay
python src/main_xsmn.py

# Lấy dữ liệu XSMT hôm nay
python src/main_xsmt.py

# Lấy dữ liệu XSMN 1 tháng gần đây
python src/main_xsmn.py --from 2024-03-01
```

---

## Tóm Tắt Nhanh

| Việc cần làm | Công cụ |
|---|---|
| Lưu code | GitHub (miễn phí) |
| Chạy tự động mỗi ngày | GitHub Actions (miễn phí, 2000 phút/tháng) |
| Lấy toàn bộ lịch sử | Workflow "Backfill" → Run workflow |
| Xem/dùng dữ liệu | URL `raw.githubusercontent.com/...` |
| Định dạng dữ liệu | CSV (Excel, Python, R) và JSON (web, app) |
| Phân biệt đài | Cột `station` trong CSV/JSON |

---

*Dự án này hoàn toàn miễn phí. Dữ liệu được lấy từ [minhngoc.net.vn](https://www.minhngoc.net.vn) theo cách hợp lệ với thời gian chờ giữa các lần tải.*
