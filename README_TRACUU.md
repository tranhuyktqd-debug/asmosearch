# 🔍 Ứng Dụng Tra Cứu Thông Tin Học Sinh

Chương trình độc lập để tra cứu thông tin học sinh từ file Excel, dựa trên logic của Tab 3 "Tra cứu" trong ứng dụng chính.

## ✨ Tính năng

- 📂 **Đọc file Excel**: Hỗ trợ đọc nhiều sheet từ file Excel
- 📑 **Chọn sheet**: Chọn một hoặc nhiều sheet để tra cứu
- 🔍 **Tìm kiếm linh hoạt**:
  - Tìm theo SBD (Số báo danh)
  - Tìm theo Họ tên (hỗ trợ tìm kiếm một phần)
  - Tìm theo Ngày sinh (có thể tìm theo ngày, tháng, năm riêng lẻ)
- 📋 **Hiển thị kết quả**: Bảng kết quả với thông tin cơ bản
- 👤 **Chi tiết học sinh**: 
  - Thông tin đầy đủ
  - Kết quả các môn học với màu sắc theo huy chương
  - Mã CERT
  - Ảnh học sinh (nếu có trong thư mục `photos/`)
  - QR Code chứa thông tin học sinh
- 🎨 **Giao diện đẹp**: Màu sắc trực quan, dễ sử dụng

## 🚀 Cài đặt

### Yêu cầu
- Python 3.7+
- pip

### Cài đặt thư viện

```bash
pip install pandas openpyxl qrcode[pil] pillow
```

Hoặc nếu đã có file `requirements.txt`:

```bash
pip install -r requirements.txt
```

## 📖 Hướng dẫn sử dụng

### Chạy ứng dụng

```bash
python tracuu_app.py
```

### Các bước sử dụng

1. **Chọn file dữ liệu**
   - Click nút "📂 Chọn file" để chọn file Excel
   - Click "📖 Đọc file" để đọc danh sách sheet

2. **Chọn sheet**
   - Chọn một hoặc nhiều sheet cần tra cứu (tích vào checkbox)
   - Click "✅ Load dữ liệu từ sheet đã chọn" để tải dữ liệu

3. **Tìm kiếm**
   - Nhập SBD, Họ tên, hoặc chọn Ngày sinh
   - Click "🔍 TÌM KIẾM"
   - Kết quả sẽ hiển thị trong bảng bên trái

4. **Xem chi tiết**
   - Click vào một học sinh trong bảng kết quả
   - Thông tin chi tiết sẽ hiển thị ở bên phải

5. **Xóa bộ lọc**
   - Click "🔄 XÓA BỘ LỌC" để xóa tất cả điều kiện tìm kiếm và hiển thị lại toàn bộ dữ liệu

## 📁 Cấu trúc dữ liệu

### File Excel đầu vào

File Excel cần có các cột sau (tên cột có thể khác nhau một chút):
- `SBD`: Số báo danh
- `FULL NAME` hoặc `Họ tên`: Tên học sinh
- `Ngày sinh` hoặc `D.O.B`: Ngày sinh
- `KHỐI`: Khối lớp
- `TRƯỜNG`: Tên trường
- `KQ VQG TOÁN` hoặc `TOÁN`: Kết quả môn Toán
- `KQ VQG TIẾNG ANH` hoặc `TIẾNG ANH`: Kết quả môn Tiếng Anh
- `KQ VQG KHOA HỌC` hoặc `KHOA HỌC`: Kết quả môn Khoa học
- `MÃ CERT` hoặc `MÃ CERT ĐẦY ĐỦ`: Mã chứng chỉ

### Thư mục ảnh

Nếu muốn hiển thị ảnh học sinh, đặt ảnh trong thư mục `photos/` với tên file là `{SBD}.jpg` (ví dụ: `001009872.jpg`)

## 🎨 Màu sắc huy chương

- 🥇 **Vàng**: `#f39c12`
- 🥈 **Bạc**: `#95a5a6`
- 🥉 **Đồng**: `#cd7f32`
- 🔵 **Khuyến khích**: `#3498db`
- 🟢 **Chứng nhận**: `#27ae60`

## 📝 Ghi chú

- Chương trình tự động làm sạch dữ liệu (bỏ từ "HUY CHƯƠNG" khỏi kết quả)
- Hỗ trợ tìm kiếm không phân biệt hoa thường
- Tìm kiếm theo ngày sinh linh hoạt (có thể chỉ nhập ngày, tháng, hoặc năm)
- QR Code chứa toàn bộ thông tin học sinh, có thể quét để xem

## 🔧 Xử lý lỗi

- Nếu file không tồn tại: Kiểm tra đường dẫn file
- Nếu không đọc được sheet: Kiểm tra định dạng file Excel
- Nếu không hiển thị ảnh: Kiểm tra thư mục `photos/` và tên file ảnh
- Nếu QR Code lỗi: Kiểm tra xem đã cài đặt `qrcode` và `PIL` chưa

## 📄 License

Chương trình được tạo dựa trên logic của Tab 3 "Tra cứu" trong `awards_processing_app.py`
