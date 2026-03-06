from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import models
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.utils import timezone
import datetime as dt
from .models import SanPham, DonHang

def tao_du_lieu_mau():
    ds = [
        {"ten": "Nhẫn Kim cương Vàng trắng 58,5% (14K) DD00W006266", "gia": 10_403_371, "anh": "sanpham/nhan_kimcuong.png"},
        {"ten": "Lắc tay Vàng 99% 0000Y004602", "gia": 22_130_000, "anh": "sanpham/lac_tay_9999.png"},
        {"ten": "Mặt dây chuyền Vàng trắng 41,6% (10K) Đính đá ECZ XMXMW003560", "gia": 3_990_405, "anh": "sanpham/mat_day_ecz.png"},
        {"ten": "Bộ trang sức Vàng trắng 75% (18K) 60998-60390", "gia": 15_900_000, "anh": "sanpham/bo_60998_60390.png"},
        {"ten": "Bộ trang sức Vàng trắng 75% (18K) 60125-61116", "gia": 22_200_000, "anh": "sanpham/bo_60125_61116.png"},
    ]

    for item in ds:
        SanPham.objects.get_or_create(
            ten=item["ten"],
            defaults={"gia": item["gia"], "anh": item["anh"]},
        )

def home(request):
    tao_du_lieu_mau()
    q = request.GET.get("q", "").strip()
    ds = SanPham.objects.all().order_by("id")
    if q:
        ds = ds.filter(ten__icontains=q)
    return render(request, "home.html", {"ds": ds, "q": q})

def dang_ky(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        password2 = request.POST.get("password2", "").strip()

        if not username or not password:
            return render(request, "dang_ky.html", {"loi": "Nhập tên đăng nhập và mật khẩu."})

        if password != password2:
            return render(request, "dang_ky.html", {"loi": "Mật khẩu nhập lại không khớp."})

        if User.objects.filter(username=username).exists():
            return render(request, "dang_ky.html", {"loi": "Tên đăng nhập đã tồn tại."})

        User.objects.create_user(username=username, password=password)
        return redirect("dang_nhap")

    return render(request, "dang_ky.html")

def dang_nhap(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        user = authenticate(request, username=username, password=password)
        if user is None:
            return render(request, "dang_nhap.html", {"loi": "Sai tên đăng nhập hoặc mật khẩu."})

        login(request, user)
        return redirect("home")

    return render(request, "dang_nhap.html")

def dang_xuat(request):
    logout(request)
    return redirect("home")

@login_required
def dat_hang(request, san_pham_id):
    tao_du_lieu_mau()
    sp = get_object_or_404(SanPham, id=san_pham_id)

    if request.method == "POST":
        so_luong = request.POST.get("so_luong", "1").strip()
        ho_ten = request.POST.get("ho_ten", "").strip()
        sdt = request.POST.get("sdt", "").strip()
        dia_chi = request.POST.get("dia_chi", "").strip()
        ghi_chu = request.POST.get("ghi_chu", "").strip()
        phuong_thuc_tt = request.POST.get("phuong_thuc_tt", "COD").strip()

        if not so_luong.isdigit() or int(so_luong) <= 0:
            return render(request, "dat_hang.html", {"sp": sp, "loi": "Số lượng phải là số > 0."})

        if not ho_ten or not sdt or not dia_chi:
            return render(request, "dat_hang.html", {"sp": sp, "loi": "Vui lòng nhập đầy đủ: Họ tên, SĐT, Địa chỉ."})

        if not sdt.isdigit() or len(sdt) < 9:
            return render(request, "dat_hang.html", {"sp": sp, "loi": "SĐT không hợp lệ (chỉ số, tối thiểu 9 chữ số)."})

        so_luong = int(so_luong)
        tong = so_luong * sp.gia

        DonHang.objects.create(
            nguoi_dat=request.user,
            san_pham=sp,
            so_luong=so_luong,
            tong_tien=tong,
            ho_ten=ho_ten,
            sdt=sdt,
            dia_chi=dia_chi,
            ghi_chu=ghi_chu,
            phuong_thuc_tt=phuong_thuc_tt,
            trang_thai="Pending",
        )
        return redirect("ds_don")

    # gợi ý điền nhanh từ username
    return render(request, "dat_hang.html", {"sp": sp})

@login_required
def ds_don(request):
    ds = DonHang.objects.filter(nguoi_dat=request.user).order_by("-id")
    return render(request, "don_hang.html", {"ds": ds})

@login_required
def xac_nhan_don(request, don_id):
    don = get_object_or_404(DonHang, id=don_id, nguoi_dat=request.user)
    if don.trang_thai == "Pending":
        don.trang_thai = "Confirmed"
        don.save()
    return redirect("ds_don")

@login_required
def huy_don(request, don_id):
    don = get_object_or_404(DonHang, id=don_id, nguoi_dat=request.user)
    if don.trang_thai in ["Pending", "Confirmed"]:
        don.trang_thai = "Cancelled"
        don.save()
    return redirect("ds_don")

def la_admin(user):
    return user.is_staff

@user_passes_test(la_admin)
def duyet_don(request, don_id, hanh_dong):
    # Admin duyệt/từ chối đơn (demo)
    don = get_object_or_404(DonHang, id=don_id)

    if don.trang_thai in ["Cancelled", "Rejected"]:
        return redirect("ds_don_admin")

    if hanh_dong == "approve":
        don.trang_thai = "Approved"
    elif hanh_dong == "reject":
        don.trang_thai = "Rejected"

    don.save()
    return redirect("ds_don_admin")

@user_passes_test(la_admin)
def ds_don_admin(request):
    ds = DonHang.objects.all().order_by("-id")
    return render(request, "don_hang_admin.html", {"ds": ds})



@user_passes_test(la_admin)
def admin_dashboard(request):
    # Tổng quan + số liệu cho biểu đồ
    tong_sp = SanPham.objects.count()
    tong_don = DonHang.objects.count()
    cho_xac_nhan = DonHang.objects.filter(trang_thai="Pending").count()
    da_duyet = DonHang.objects.filter(trang_thai="Approved").count()
    da_huy = DonHang.objects.filter(trang_thai="Cancelled").count()

    # Thống kê theo trạng thái
    status_rows = DonHang.objects.values("trang_thai").annotate(c=Count("id")).order_by("trang_thai")
    status_labels = [r["trang_thai"] for r in status_rows]
    status_counts = [r["c"] for r in status_rows]

    # 7 ngày gần nhất: số đơn + doanh thu
    today = timezone.localdate()
    start = today - dt.timedelta(days=6)

    daily_rows = (
        DonHang.objects.filter(tao_luc__date__gte=start, tao_luc__date__lte=today)
        .annotate(d=TruncDate("tao_luc"))
        .values("d")
        .annotate(orders=Count("id"), revenue=Sum("tong_tien"))
        .order_by("d")
    )
    daily_map = {r["d"]: r for r in daily_rows}
    days = [start + dt.timedelta(days=i) for i in range(7)]
    daily_labels = [d.strftime("%d/%m") for d in days]
    daily_orders = [int(daily_map.get(d, {}).get("orders") or 0) for d in days]
    daily_revenue = [int(daily_map.get(d, {}).get("revenue") or 0) for d in days]

    # Top sản phẩm theo số đơn (10)
    top_products = (
        DonHang.objects.values("san_pham__ten")
        .annotate(c=Count("id"))
        .order_by("-c")[:10]
    )

    return render(request, "admin_dashboard.html", {
        "tong_sp": tong_sp,
        "tong_don": tong_don,
        "cho_xac_nhan": cho_xac_nhan,
        "da_duyet": da_duyet,
        "da_huy": da_huy,

        "status_labels": status_labels,
        "status_counts": status_counts,
        "daily_labels": daily_labels,
        "daily_orders": daily_orders,
        "daily_revenue": daily_revenue,
        "top_products": top_products,
    })

@user_passes_test(la_admin)
def admin_sanpham_list(request):
    q = request.GET.get("q", "").strip()
    ds = SanPham.objects.all().order_by("-id")
    if q:
        ds = ds.filter(ten__icontains=q)
    return render(request, "admin_sanpham_list.html", {"ds": ds, "q": q})

@user_passes_test(la_admin)
def admin_sanpham_create(request):
    if request.method == "POST":
        ten = request.POST.get("ten", "").strip()
        gia = request.POST.get("gia", "0").strip()
        anh = request.FILES.get("anh")

        if not ten:
            return render(request, "admin_sanpham_form.html", {"loi": "Vui lòng nhập tên sản phẩm."})
        if not gia.isdigit() or int(gia) < 0:
            return render(request, "admin_sanpham_form.html", {"loi": "Giá phải là số >= 0."})

        sp = SanPham(ten=ten, gia=int(gia))
        if anh:
            sp.anh = anh
        sp.save()
        return redirect("admin_sanpham_list")

    return render(request, "admin_sanpham_form.html", {"mode": "create"})

@user_passes_test(la_admin)
def admin_sanpham_edit(request, sp_id):
    sp = get_object_or_404(SanPham, id=sp_id)

    if request.method == "POST":
        ten = request.POST.get("ten", "").strip()
        gia = request.POST.get("gia", "0").strip()
        anh = request.FILES.get("anh")

        if not ten:
            return render(request, "admin_sanpham_form.html", {"sp": sp, "loi": "Vui lòng nhập tên sản phẩm.", "mode": "edit"})
        if not gia.isdigit() or int(gia) < 0:
            return render(request, "admin_sanpham_form.html", {"sp": sp, "loi": "Giá phải là số >= 0.", "mode": "edit"})

        sp.ten = ten
        sp.gia = int(gia)
        if anh:
            sp.anh = anh
        sp.save()
        return redirect("admin_sanpham_list")

    return render(request, "admin_sanpham_form.html", {"sp": sp, "mode": "edit"})

@user_passes_test(la_admin)
def admin_sanpham_delete(request, sp_id):
    sp = get_object_or_404(SanPham, id=sp_id)

    if request.method == "POST":
        sp.delete()
        return redirect("admin_sanpham_list")

    return render(request, "admin_sanpham_delete.html", {"sp": sp})


@user_passes_test(la_admin)
def admin_donhang_list(request):
    # Lọc + tìm kiếm
    trang_thai = request.GET.get("trang_thai", "").strip()
    q = request.GET.get("q", "").strip()

    ds = DonHang.objects.select_related("nguoi_dat", "san_pham").all().order_by("-id")
    if trang_thai:
        ds = ds.filter(trang_thai=trang_thai)
    if q:
        ds = ds.filter(
            models.Q(nguoi_dat__username__icontains=q) |
            models.Q(ho_ten__icontains=q) |
            models.Q(sdt__icontains=q) |
            models.Q(san_pham__ten__icontains=q) |
            models.Q(dia_chi__icontains=q)
        )

    return render(request, "admin_donhang_list.html", {
        "ds": ds,
        "q": q,
        "trang_thai": trang_thai,
        "trang_thai_choices": DonHang.TRANG_THAI,
    })

@user_passes_test(la_admin)
def admin_donhang_update(request, don_id):
    don = get_object_or_404(DonHang, id=don_id)
    if request.method == "POST":
        new_status = request.POST.get("trang_thai", "").strip()
        valid = [k for k, _ in DonHang.TRANG_THAI]
        if new_status in valid:
            don.trang_thai = new_status
            don.save()
    # giữ lại querystring để quay về đúng bộ lọc
    return redirect(request.META.get("HTTP_REFERER", "admin_donhang_list"))

@user_passes_test(la_admin)
def admin_user_list(request):
    q = request.GET.get("q", "").strip()
    users = User.objects.all().order_by("-date_joined")
    if q:
        users = users.filter(models.Q(username__icontains=q) | models.Q(email__icontains=q))

    return render(request, "admin_user_list.html", {
        "users": users,
        "q": q,
    })

@user_passes_test(la_admin)
def admin_user_create(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()
        is_staff = request.POST.get("is_staff") == "on"
        is_active = request.POST.get("is_active") == "on"

        if not username or not password:
            return render(request, "admin_user_form.html", {"loi": "Vui lòng nhập username và password.", "mode": "create"})

        if User.objects.filter(username=username).exists():
            return render(request, "admin_user_form.html", {"loi": "Username đã tồn tại.", "mode": "create"})

        u = User.objects.create_user(username=username, password=password)
        u.is_staff = is_staff
        u.is_active = is_active
        u.save()
        return redirect("admin_user_list")

    return render(request, "admin_user_form.html", {"mode": "create"})

@user_passes_test(la_admin)
def admin_user_edit(request, user_id):
    u = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        is_staff = request.POST.get("is_staff") == "on"
        is_active = request.POST.get("is_active") == "on"
        new_password = request.POST.get("password", "").strip()

        u.is_staff = is_staff
        u.is_active = is_active
        if new_password:
            u.set_password(new_password)
        u.save()
        return redirect("admin_user_list")

    return render(request, "admin_user_form.html", {"mode": "edit", "u": u})
