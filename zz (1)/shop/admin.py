from django.contrib import admin
from .models import SanPham, DonHang

@admin.register(SanPham)
class SanPhamAdmin(admin.ModelAdmin):
    list_display = ("id", "ten", "gia")
    search_fields = ("ten",)

@admin.register(DonHang)
class DonHangAdmin(admin.ModelAdmin):
    list_display = ("id", "nguoi_dat", "san_pham", "so_luong", "tong_tien", "trang_thai", "tao_luc")
    list_filter = ("trang_thai", "tao_luc")
    search_fields = ("nguoi_dat__username", "san_pham__ten", "ho_ten", "sdt", "dia_chi")
