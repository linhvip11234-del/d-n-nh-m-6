# Jewelry Django Demo v6 (Checkout)

Demo website bán trang sức (local) bằng Django.

## Tính năng chính
- Xem danh sách sản phẩm + tìm kiếm theo tên
- Đăng ký / Đăng nhập / Đăng xuất
- Mua hàng (thanh toán đơn giản): nhập **Họ tên + SĐT + Địa chỉ + Ghi chú**
- Quản lý đơn hàng: **Xác nhận / Huỷ**
- Admin quản lý đơn: duyệt / từ chối (demo)

## Cài đặt & chạy
```bash
py -m pip install -r requirements.txt
py manage.py migrate
py manage.py createsuperuser
py manage.py runserver
```

- Trang chủ: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

## Ghi chú
- Ảnh sản phẩm nằm trong `media/sanpham/`.
- Nếu đổi ảnh mà chưa thấy cập nhật, thử Ctrl+F5 hoặc mở tab ẩn danh (do cache).
