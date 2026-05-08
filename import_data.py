from web import app, db, NhanVien, KhachHang, DoiTac
import pandas as pd
import os

# ===== CẤU HÌNH THƯ MỤC =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Tạo thư mục data nếu chưa có
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
    print(f"Đã tạo thư mục: {DATA_DIR}")

with app.app_context():
    # ===== KHỞI TẠO LẠI DATABASE =====
    db.drop_all()
    db.create_all()
    print("Đã tạo lại database")

    # ===== IMPORT NHÂN VIÊN =====
    print("\n--- Import Nhân viên ---")
    try:
        file_path = os.path.join(DATA_DIR, 'dulieu_nhanvien.xlsx')
        if os.path.exists(file_path):
            # ✅ Đọc file và ép kiểu cột "Số điện thoại" thành chuỗi
            df_nv = pd.read_excel(file_path, dtype={'Số điện thoại': str})
            df_nv.columns = df_nv.columns.str.strip()

            required_cols = ['Họ và Tên', 'Giới tính', 'Số điện thoại', 'Nhóm', 'Phòng ban', 'Chức danh']
            for col in required_cols:
                if col not in df_nv.columns:
                    raise ValueError(f"Thiếu cột '{col}' trong file Nhân viên.")

            count = 0
            for _, row in df_nv.iterrows():
                if pd.isna(row['Họ và Tên']) or str(row['Họ và Tên']).strip() == '':
                    continue

                so_dien_thoai = str(row.get('Số điện thoại', '')).strip()
                if so_dien_thoai.endswith('.0'):
                    so_dien_thoai = so_dien_thoai[:-2]  # loại bỏ .0 nếu Excel tự thêm

                nv = NhanVien(
                    ho_va_ten=str(row.get('Họ và Tên', '')).strip(),
                    gioi_tinh=str(row.get('Giới tính', '')).strip(),
                    so_dien_thoai=so_dien_thoai,
                    nhom=str(row.get('Nhóm', '')).strip(),
                    phong_ban=str(row.get('Phòng ban', '')).strip(),
                    chuc_danh=str(row.get('Chức danh', '')).strip()
                )
                db.session.add(nv)
                count += 1
            db.session.commit()
            print(f"✓ Import thành công {count} nhân viên từ file Excel")
        else:
            print(f"✗ Không tìm thấy file: {file_path}")
            print("  → Vui lòng đặt file 'dulieu_nhanvien.xlsx' vào thư mục 'data'")
    except Exception as e:
        print(f"✗ Lỗi khi import nhân viên: {e}")
        import traceback
        traceback.print_exc()

    # ===== IMPORT KHÁCH HÀNG =====
    print("\n--- Import Khách hàng ---")
    try:
        file_path = os.path.join(DATA_DIR, 'dulieu_khachhang.xlsx')
        if os.path.exists(file_path):
            # ✅ Đọc file và ép kiểu cột "Số điện thoại" thành chuỗi
            df_kh = pd.read_excel(file_path, dtype={'Số điện thoại': str})
            df_kh.columns = df_kh.columns.str.strip()

            required_cols = ['Họ và Tên', 'Giới tính', 'Số điện thoại']
            for col in required_cols:
                if col not in df_kh.columns:
                    raise ValueError(f"Thiếu cột '{col}' trong file Khách hàng.")

            count = 0
            for _, row in df_kh.iterrows():
                if pd.isna(row['Họ và Tên']) or str(row['Họ và Tên']).strip() == '':
                    continue

                so_dien_thoai = str(row.get('Số điện thoại', '')).strip()
                if so_dien_thoai.endswith('.0'):
                    so_dien_thoai = so_dien_thoai[:-2]

                kh = KhachHang(
                    ho_va_ten=str(row.get('Họ và Tên', '')).strip(),
                    gioi_tinh=str(row.get('Giới tính', '')).strip(),
                    so_dien_thoai=so_dien_thoai,
                    nhom=str(row.get('Nhóm', '')).strip() if 'Nhóm' in row and pd.notna(row['Nhóm']) else ""
                )
                db.session.add(kh)
                count += 1
            db.session.commit()
            print(f"✓ Import thành công {count} khách hàng từ file Excel")
        else:
            print(f"✗ Không tìm thấy file: {file_path}")
            print("  → Vui lòng đặt file 'dulieu_khachhang.xlsx' vào thư mục 'data'")
    except Exception as e:
        print(f"✗ Lỗi khi import khách hàng: {e}")
        import traceback
        traceback.print_exc()

    # ===== IMPORT ĐỐI TÁC =====
    print("\n--- Import Đối tác ---")
    try:
        file_path = os.path.join(DATA_DIR, 'dulieu_doitac.xlsx')
        if os.path.exists(file_path):
            # ✅ Đọc file và ép kiểu cột "Số điện thoại" thành chuỗi
            df_dt = pd.read_excel(file_path, dtype={'Số điện thoại': str})
            df_dt.columns = df_dt.columns.str.strip()

            required_cols = ['Họ và Tên', 'Giới tính', 'Số điện thoại']
            for col in required_cols:
                if col not in df_dt.columns:
                    raise ValueError(f"Thiếu cột '{col}' trong file Đối tác.")

            count = 0
            for _, row in df_dt.iterrows():
                if pd.isna(row['Họ và Tên']) or str(row['Họ và Tên']).strip() == '':
                    continue

                so_dien_thoai = str(row.get('Số điện thoại', '')).strip()
                if so_dien_thoai.endswith('.0'):
                    so_dien_thoai = so_dien_thoai[:-2]

                dt = DoiTac(
                    ho_va_ten=str(row.get('Họ và Tên', '')).strip(),
                    gioi_tinh=str(row.get('Giới tính', '')).strip(),
                    so_dien_thoai=so_dien_thoai,
                    nhom=str(row.get('Nhóm', '')).strip() if 'Nhóm' in row and pd.notna(row['Nhóm']) else ""
                )
                db.session.add(dt)
                count += 1
            db.session.commit()
            print(f"✓ Import thành công {count} đối tác từ file Excel")
        else:
            print(f"✗ Không tìm thấy file: {file_path}")
            print("  → Vui lòng đặt file 'dulieu_doitac.xlsx' vào thư mục 'data'")
    except Exception as e:
        print(f"✗ Lỗi khi import đối tác: {e}")
        import traceback
        traceback.print_exc()

print("\n=== HOÀN TẤT ===")
print("Chạy lệnh: python web.py để khởi động server")
