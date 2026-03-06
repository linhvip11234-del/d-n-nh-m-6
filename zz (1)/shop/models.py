from django.db import models
from django.contrib.auth.models import User

class SanPham(models.Model):
    ten = models.CharField(max_length=100)
    gia = models.IntegerField(default=0)
    anh = models.ImageField(upload_to="sanpham/", blank=True, null=True)

    def __str__(self):
        return self.ten

class DonHang(models.Model):
    TRANG_THAI = [
        ("Pending", "Chờ xác nhận"),
        ("Confirmed", "Đã xác nhận"),
        ("Cancelled", "Đã huỷ"),
        ("Approved", "Đã duyệt"),
        ("Rejected", "Từ chối"),
    ]

    nguoi_dat = models.ForeignKey(User, on_delete=models.CASCADE)
    san_pham = models.ForeignKey(SanPham, on_delete=models.CASCADE)

    ho_ten = models.CharField(max_length=100, default="")
    sdt = models.CharField(max_length=20, default="")
    dia_chi = models.CharField(max_length=255, default="")
    ghi_chu = models.CharField(max_length=255, blank=True, default="")
    phuong_thuc_tt = models.CharField(max_length=50, default="COD")

    so_luong = models.IntegerField(default=1)
    tong_tien = models.IntegerField(default=0)
    trang_thai = models.CharField(max_length=20, choices=TRANG_THAI, default="Pending")
    tao_luc = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Don #{self.id} - {self.nguoi_dat.username}"
