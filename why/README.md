# AutoClick Move Class FPT

## Mục đích (Purpose)
Tự động nhấn nút "Save" trên FPT University Portal để chuyển lớp học phần từ **SExxxx** sang **MCxxxx**.

## Vấn đề (Problem)
- Lớp **MCxxxx** hiện đã **đầy** (35 sinh viên)
- Cần chờ đến khi có slot trống
- Nhấn tay mỗi 60 giây rất mệt → Tự động hóa

---

## Cách hoạt động (How it works)

1. Mở trình duyệt Chromium với cookies của bạn
2. Load trang MoveSubject
3. Nhấn nút **Save** mỗi **60 giây**
4. Kiểm tra thông báo lỗi:
   - Nếu báo "full" → Thử lại
   - Nếu thành công (lớp đổi từ IA1906) → Dừng
5. Lặp lại cho đến khi thành công

---

## Cài đặt (Setup)

### 1. Cài đặt dependencies
```bash
cd fpt-auto-clicker
pip install -r requirements.txt
playwright install chromium
```

### 2. Cập nhật cookies
Mở `cookies.json` và thay đổi các giá trị từ DevTools:
- F12 → Application → Cookies → https://fap.fpt.edu.vn
- Copy `name` và `value` của từng cookie

**Cookies cần thiết:**
| Cookie | Mô tả |
|--------|-------|
| ASP.NET_SessionId | Session ID |
| .AspNet.cookies | Auth cookie |
| __AntiXsrfToken | CSRF token |
| __utma, __utmc, __utmb | Google Analytics |
| cf_clearance | Cloudflare clearance |

### 3. Chạy script
```bash
python playwright-version.py
```

---

## Cấu hình (Configuration)

Trong `playwright-version.py`:

```python
TARGET_URL = "https://fap.fpt.edu.vn/MoveSubject.aspx?id=59122"
CLICK_INTERVAL = 60  # Giây giữa mỗi lần click
COOKIES_FILE = "cookies.json"
```

**Lưu ý:** Thay đổi `CLICK_INTERVAL` nếu muốn nhanh hơn/chậm hơn.

---

## Phát hiện thành công (Success Detection)

Script dừng khi:
1. Label "Old Class" thay đổi từ **IA1906** → Khác
2. Không còn thông báo lỗi "class full"

---

## Giới hạn (Limitations)

- **cf_clearance cookie** hết hạn sau ~30 phút
  - Nếu script ngừng hoạt động → Lấy cookie mới từ trình duyệt thật
- **Session hết hạn** → Login lại trong trình duyệt thật, copy cookies mới

---

## So sánh Methods

| Method | Playwright | Requests |
|--------|------------|----------|
| Độ khó | Dễ ⭐⭐⭐⭐⭐ | Khó ⭐⭐ |
| ASP.NET forms | Tự xử lý ✅ | Phải gửi ViewState thủ công |
| JavaScript alerts | Bắt được ✅ | Không bắt được |
| Cloudflare | Tự xử lý ✅ | Khó khăn |
| Tốc độ | Chậm hơn | Nhanh hơn |

**Kết luận:** Playwright phù hợp hơn cho FPT Portal.

---

## Files

```
fpt-auto-clicker/
├── playwright-version.py   # Script chính
├── cookies.json            # Cookies của bạn (cần cập nhật)
└── requirements.txt        # Dependencies
```
