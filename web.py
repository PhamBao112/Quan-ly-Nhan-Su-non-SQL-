from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nbl.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ===== MODELS =====
class NhanVien(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ho_va_ten = db.Column(db.String(100))
    gioi_tinh = db.Column(db.String(10))
    so_dien_thoai = db.Column(db.String(20))
    nhom = db.Column(db.String(100))
    phong_ban = db.Column(db.String(100))
    chuc_danh = db.Column(db.String(100))

class KhachHang(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ho_va_ten = db.Column(db.String(100))
    gioi_tinh = db.Column(db.String(10))
    so_dien_thoai = db.Column(db.String(20))
    nhom = db.Column(db.String(100))

class DoiTac(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ho_va_ten = db.Column(db.String(100))
    gioi_tinh = db.Column(db.String(10))
    so_dien_thoai = db.Column(db.String(20))
    nhom = db.Column(db.String(100))

# ===== BẢN ĐỒ CHỮ CÁI TIẾNG VIỆT =====
# Thứ tự alphabet tiếng Việt: A Ă Â B C D Đ E Ê G H I K L M N O Ô Ơ P Q R S T U Ư V X Y
VIETNAMESE_ALPHABET = {
    'a': 0, 'á': 1, 'à': 2, 'ả': 3, 'ã': 4, 'ạ': 5,
    'ă': 10, 'ắ': 11, 'ằ': 12, 'ẳ': 13, 'ẵ': 14, 'ặ': 15,
    'â': 20, 'ấ': 21, 'ầ': 22, 'ẩ': 23, 'ẫ': 24, 'ậ': 25,
    'b': 30,
    'c': 40,
    'd': 50,
    'đ': 60,
    'e': 70, 'é': 71, 'è': 72, 'ẻ': 73, 'ẽ': 74, 'ẹ': 75,
    'ê': 80, 'ế': 81, 'ề': 82, 'ể': 83, 'ễ': 84, 'ệ': 85,
    'g': 90,
    'h': 100,
    'i': 110, 'í': 111, 'ì': 112, 'ỉ': 113, 'ĩ': 114, 'ị': 115,
    'k': 120,
    'l': 130,
    'm': 140,
    'n': 150,
    'o': 160, 'ó': 161, 'ò': 162, 'ỏ': 163, 'õ': 164, 'ọ': 165,
    'ô': 170, 'ố': 171, 'ồ': 172, 'ổ': 173, 'ỗ': 174, 'ộ': 175,
    'ơ': 180, 'ớ': 181, 'ờ': 182, 'ở': 183, 'ỡ': 184, 'ợ': 185,
    'p': 190,
    'q': 200,
    'r': 210,
    's': 220,
    't': 230,
    'u': 240, 'ú': 241, 'ù': 242, 'ủ': 243, 'ũ': 244, 'ụ': 245,
    'ư': 250, 'ứ': 251, 'ừ': 252, 'ử': 253, 'ữ': 254, 'ự': 255,
    'v': 260,
    'x': 270,
    'y': 280, 'ý': 281, 'ỳ': 282, 'ỷ': 283, 'ỹ': 284, 'ỵ': 285,
}

def vietnamese_sort_key(text):
    """
    Chuyển chuỗi tiếng Việt thành tuple số để sắp xếp đúng
    Ví dụ: "Đạt" -> (60, 0, 5, 230) = đ-a-ạ-t
           "Diễm" -> (50, 110, 84, 140) = d-i-ễ-m
    """
    if not text:
        return tuple()
    
    result = []
    for char in text.lower():
        # Lấy giá trị số từ bảng chữ cái tiếng Việt
        # Nếu không có trong bảng (ký tự đặc biệt), dùng mã Unicode
        value = VIETNAMESE_ALPHABET.get(char, ord(char) + 1000)
        result.append(value)
    
    return tuple(result)

# ===== MERGE SORT IMPLEMENTATION =====
def merge_sort(arr, key_func=None, reverse=False):
    """
    Thuật toán Merge Sort để sắp xếp mảng
    Args:
        arr: Mảng cần sắp xếp
        key_func: Hàm để lấy giá trị so sánh (như lambda x: x['name'])
        reverse: True nếu sắp xếp giảm dần
    Returns:
        Mảng đã được sắp xếp
    """
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left = merge_sort(arr[:mid], key_func, reverse)
    right = merge_sort(arr[mid:], key_func, reverse)
    
    return merge(left, right, key_func, reverse)

def merge(left, right, key_func=None, reverse=False):
    """
    Hàm merge hai mảng con đã sắp xếp
    """
    result = []
    i = j = 0
    
    while i < len(left) and j < len(right):
        # Lấy giá trị để so sánh
        left_val = key_func(left[i]) if key_func else left[i]
        right_val = key_func(right[j]) if key_func else right[j]
        
        # So sánh và thêm vào kết quả
        if reverse:
            if left_val >= right_val:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
        else:
            if left_val <= right_val:
                result.append(left[i])
                i += 1
            else:
                result.append(right[j])
                j += 1
    
    # Thêm phần tử còn lại
    result.extend(left[i:])
    result.extend(right[j:])
    
    return result

# ===== ROUTES =====
@app.route('/')
def home():
    return render_template('Home_page.html')

@app.route('/nhanvien')
def nhanvien():
    return render_template('nhanvie_page.html')

@app.route('/khachhang')
def khachhang_page():
    return render_template('khachhang_page.html')

@app.route('/doitac')
def doitac():
    return render_template('doitac_page.html')

@app.route('/lienhe')
def lienhe():
    return "<h1>Trang Liên hệ</h1>"

@app.route('/taikhoan')
def taikhoan():
    return "<h1>Trang Tài khoản</h1>"

# ===== API NHÂN VIÊN =====
@app.route('/api/nhanvien', methods=['GET'])
def api_get_nhanvien():
    sort_by = request.args.get('sort_by', 'id')
    order = request.args.get('order', 'asc')
    
    nhanviens = NhanVien.query.all()
    data = [{
        'id': nv.id, 
        'ho_va_ten': nv.ho_va_ten, 
        'gioi_tinh': nv.gioi_tinh,
        'so_dien_thoai': nv.so_dien_thoai, 
        'nhom': nv.nhom,
        'phong_ban': nv.phong_ban,
        'chuc_danh': nv.chuc_danh
    } for nv in nhanviens]
    
    # Định nghĩa key function cho mergesort
    def get_sort_key(x):
        if sort_by == 'ho_va_ten':
            # Lấy tên cuối và dùng vietnamese_sort_key
            parts = str(x.get('ho_va_ten', '')).strip().split()
            last_name = parts[-1] if parts else ''
            return vietnamese_sort_key(last_name)
        elif sort_by == 'id':
            return (int(x.get('id', 0)),)  # Trả về tuple để nhất quán
        else:
            return vietnamese_sort_key(str(x.get(sort_by, '')))
    
    # SỬ DỤNG MERGE SORT
    data_sorted = merge_sort(data, key_func=get_sort_key, reverse=(order == 'desc'))
    
    return jsonify(data_sorted)

@app.route('/api/nhanvien', methods=['POST'])
def api_add_nhanvien():
    data = request.json
    nv = NhanVien(
        ho_va_ten=data['ho_va_ten'],
        gioi_tinh=data.get('gioi_tinh', ''),
        so_dien_thoai=data.get('so_dien_thoai', ''),
        nhom=data.get('nhom', ''),
        phong_ban=data.get('phong_ban', ''),
        chuc_danh=data.get('chuc_danh', '')
    )
    db.session.add(nv)
    db.session.commit()
    return jsonify({'success': True, 'id': nv.id})

@app.route('/api/nhanvien/<int:id>', methods=['PUT'])
def api_update_nhanvien(id):
    nv = NhanVien.query.get(id)
    if not nv:
        return jsonify({'success': False, 'message': 'Không tìm thấy'}), 404
    
    data = request.json
    nv.ho_va_ten = data.get('ho_va_ten', nv.ho_va_ten)
    nv.gioi_tinh = data.get('gioi_tinh', nv.gioi_tinh)
    nv.so_dien_thoai = data.get('so_dien_thoai', nv.so_dien_thoai)
    nv.nhom = data.get('nhom', nv.nhom)
    nv.phong_ban = data.get('phong_ban', nv.phong_ban)
    nv.chuc_danh = data.get('chuc_danh', nv.chuc_danh)
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/nhanvien/<int:id>', methods=['DELETE'])
def api_delete_nhanvien(id):
    nv = NhanVien.query.get(id)
    if nv:
        db.session.delete(nv)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False}), 404

# ===== API KHÁCH HÀNG =====
@app.route('/api/khachhang', methods=['GET'])
def api_get_khachhang():
    sort_by = request.args.get('sort_by', 'id')
    order = request.args.get('order', 'asc')

    khachhangs = KhachHang.query.all()
    data = [{
        'id': kh.id,
        'ho_va_ten': kh.ho_va_ten,
        'gioi_tinh': kh.gioi_tinh,
        'so_dien_thoai': kh.so_dien_thoai,
        'nhom': kh.nhom
    } for kh in khachhangs]

    # Định nghĩa key function cho mergesort
    def get_sort_key(x):
        if sort_by == 'ho_va_ten':
            # Lấy tên cuối và dùng vietnamese_sort_key
            parts = str(x.get('ho_va_ten', '')).strip().split()
            last_name = parts[-1] if parts else ''
            return vietnamese_sort_key(last_name)
        elif sort_by == 'id':
            return (int(x.get('id', 0)),)
        else:
            return vietnamese_sort_key(str(x.get(sort_by, '')))

    # SỬ DỤNG MERGE SORT
    data_sorted = merge_sort(data, key_func=get_sort_key, reverse=(order == 'desc'))

    return jsonify(data_sorted)

@app.route('/api/khachhang', methods=['POST'])
def api_add_khachhang():
    data = request.json
    kh = KhachHang(
        ho_va_ten=data['ho_va_ten'],
        gioi_tinh=data.get('gioi_tinh', ''),
        so_dien_thoai=data.get('so_dien_thoai', ''),
        nhom=data.get('nhom', '')
    )
    db.session.add(kh)
    db.session.commit()
    return jsonify({'success': True, 'id': kh.id})

@app.route('/api/khachhang/<int:id>', methods=['PUT'])
def api_update_khachhang(id):
    kh = KhachHang.query.get(id)
    if not kh:
        return jsonify({'success': False, 'message': 'Không tìm thấy'}), 404
    
    data = request.json
    kh.ho_va_ten = data.get('ho_va_ten', kh.ho_va_ten)
    kh.gioi_tinh = data.get('gioi_tinh', kh.gioi_tinh)
    kh.so_dien_thoai = data.get('so_dien_thoai', kh.so_dien_thoai)
    kh.nhom = data.get('nhom', kh.nhom)
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/khachhang/<int:id>', methods=['DELETE'])
def api_delete_khachhang(id):
    kh = KhachHang.query.get(id)
    if kh:
        db.session.delete(kh)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False}), 404

# ===== API ĐỐI TÁC =====
@app.route('/api/doitac', methods=['GET'])
def api_get_doitac():
    sort_by = request.args.get('sort_by', 'id')
    order = request.args.get('order', 'asc')
    
    doitacs = DoiTac.query.all()
    data = [{
        'id': dt.id,
        'ho_va_ten': dt.ho_va_ten,
        'gioi_tinh': dt.gioi_tinh,
        'so_dien_thoai': dt.so_dien_thoai,
        'nhom': dt.nhom
    } for dt in doitacs]
    
    # Định nghĩa key function cho mergesort
    def get_sort_key(x):
        if sort_by == 'ho_va_ten':
            # Lấy tên cuối và dùng vietnamese_sort_key
            parts = str(x.get('ho_va_ten', '')).strip().split()
            last_name = parts[-1] if parts else ''
            return vietnamese_sort_key(last_name)
        elif sort_by == 'id':
            return (int(x.get('id', 0)),)
        else:
            return vietnamese_sort_key(str(x.get(sort_by, '')))
    
    # SỬ DỤNG MERGE SORT
    data_sorted = merge_sort(data, key_func=get_sort_key, reverse=(order == 'desc'))
    
    return jsonify(data_sorted)

@app.route('/api/doitac', methods=['POST'])
def api_add_doitac():
    data = request.json
    dt = DoiTac(
        ho_va_ten=data['ho_va_ten'],
        gioi_tinh=data.get('gioi_tinh', ''),
        so_dien_thoai=data.get('so_dien_thoai', ''),
        nhom=data.get('nhom', '')
    )
    db.session.add(dt)
    db.session.commit()
    return jsonify({'success': True, 'id': dt.id})

@app.route('/api/doitac/<int:id>', methods=['PUT'])
def api_update_doitac(id):
    dt = DoiTac.query.get(id)
    if not dt:
        return jsonify({'success': False, 'message': 'Không tìm thấy'}), 404
    
    data = request.json
    dt.ho_va_ten = data.get('ho_va_ten', dt.ho_va_ten)
    dt.gioi_tinh = data.get('gioi_tinh', dt.gioi_tinh)
    dt.so_dien_thoai = data.get('so_dien_thoai', dt.so_dien_thoai)
    dt.nhom = data.get('nhom', dt.nhom)
    
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/doitac/<int:id>', methods=['DELETE'])
def api_delete_doitac(id):
    dt = DoiTac.query.get(id)
    if dt:
        db.session.delete(dt)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False}), 404

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)