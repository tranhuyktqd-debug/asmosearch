# -*- coding: utf-8 -*-
"""
WEB API cho ứng dụng tra cứu thông tin học sinh
Deploy trên Vercel
"""
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import pandas as pd
import os
import io
import base64
from datetime import datetime

try:
    import qrcode
    from PIL import Image
    HAS_QR_PIL = True
except ImportError:
    HAS_QR_PIL = False

app = Flask(__name__)
CORS(app)

# Global variable để lưu dữ liệu
df_data = None
qr_codes = {}

@app.route('/')
def index():
    """Trang chủ - trả về file HTML"""
    try:
        return send_file('index.html')
    except:
        return send_from_directory('.', 'index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload và đọc file Excel"""
    global df_data, qr_codes
    
    if 'file' not in request.files:
        return jsonify({'error': 'Không có file được upload'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Chưa chọn file'}), 400
    
    try:
        # Đọc file Excel
        xl_file = pd.ExcelFile(file)
        sheets = xl_file.sheet_names
        
        return jsonify({
            'success': True,
            'sheets': sheets,
            'message': f'Đã đọc {len(sheets)} sheet'
        })
    except Exception as e:
        return jsonify({'error': f'Lỗi đọc file: {str(e)}'}), 500

@app.route('/api/load-sheets', methods=['POST'])
def load_sheets():
    """Load dữ liệu từ các sheet đã chọn"""
    global df_data, qr_codes
    
    file = request.files.get('file')
    selected_sheets_str = request.form.get('sheets', '[]')
    
    try:
        import json
        selected_sheets = json.loads(selected_sheets_str)
    except:
        selected_sheets = []
    
    if not file or not selected_sheets:
        return jsonify({'error': 'Thiếu thông tin'}), 400
    
    try:
        # Đọc file Excel
        xl_file = pd.ExcelFile(file)
        all_data = []
        
        for sheet_name in selected_sheets:
            if sheet_name in xl_file.sheet_names:
                df = pd.read_excel(xl_file, sheet_name=sheet_name, dtype={'SBD': str})
                df['_SHEET_NAME'] = sheet_name
                all_data.append(df)
        
        if not all_data:
            return jsonify({'error': 'Không có dữ liệu'}), 400
        
        # Merge dữ liệu
        df_data = pd.concat(all_data, ignore_index=True)
        
        # Làm sạch dữ liệu
        ket_qua_cols = ['TOÁN', 'KQ VQG TOÁN', 'KHOA HỌC', 'KQ VQG KHOA HỌC', 'TIẾNG ANH', 'KQ VQG TIẾNG ANH']
        for col in ket_qua_cols:
            if col in df_data.columns:
                df_data[col] = df_data[col].apply(
                    lambda x: str(x).replace('HUY CHƯƠNG ', '').replace('HUY CHUONG ', '').replace('HUY CHƯƠNG', '').replace('HUY CHUONG', '') 
                    if pd.notna(x) and str(x).strip() != '' else x
                )
        
        # Tạo QR codes
        qr_codes = {}
        qr_count = 0
        
        if HAS_QR_PIL:
            for idx, row in df_data.iterrows():
                sbd = str(row.get('SBD', '')).strip()
                if sbd and sbd.lower() not in ['nan', '<nan>', 'none', '']:
                    try:
                        qr_data = f"CAN={sbd}"
                        qr = qrcode.QRCode(version=1, box_size=5, border=1)
                        qr.add_data(qr_data)
                        qr.make(fit=True)
                        qr_img = qr.make_image(fill_color="black", back_color="white")
                        qr_codes[sbd] = qr_img
                        qr_count += 1
                    except Exception as e:
                        print(f"Lỗi tạo QR code cho SBD {sbd}: {str(e)}")
        
        # Chuyển DataFrame sang dict để trả về
        students = df_data.to_dict('records')
        
        # Clean data trước khi trả về
        for student in students:
            for key, value in student.items():
                if pd.isna(value) or str(value).lower() in ['nan', '<nan>', 'none']:
                    student[key] = ''
                else:
                    student[key] = str(value)
        
        return jsonify({
            'success': True,
            'students': students,
            'total': len(students),
            'qr_count': qr_count,
            'message': f'Đã load {len(students)} học sinh'
        })
    except Exception as e:
        return jsonify({'error': f'Lỗi load dữ liệu: {str(e)}'}), 500

@app.route('/api/search', methods=['POST'])
def search_students():
    """Tìm kiếm học sinh"""
    global df_data
    
    if df_data is None:
        return jsonify({'error': 'Chưa load dữ liệu'}), 400
    
    data = request.json
    sbd = data.get('sbd', '').strip().lower()
    hoten = data.get('hoten', '').strip().lower()
    day = data.get('day', '')
    month = data.get('month', '')
    year = data.get('year', '')
    
    # Filter
    results = df_data.copy()
    
    if sbd:
        results = results[results['SBD'].astype(str).str.lower().str.contains(sbd, na=False)]
    
    if hoten:
        name_cols = ['FULL NAME', 'Họ tên', 'HỌ TÊN', 'Tên']
        name_mask = pd.Series([False] * len(results))
        for col in name_cols:
            if col in results.columns:
                name_mask = name_mask | results[col].astype(str).str.lower().str.contains(hoten, na=False)
        results = results[name_mask]
    
    # Filter theo ngày sinh
    if day or month or year:
        def match_dob(dob_str):
            if pd.isna(dob_str):
                return False
            dob = str(dob_str)
            
            if day:
                day_padded = str(day).zfill(2)
                if not dob.startswith(day_padded):
                    return False
            
            if month:
                month_padded = str(month).zfill(2)
                if f'-{month_padded}-' not in dob and f'/{month_padded}/' not in dob:
                    return False
            
            if year:
                if not dob.endswith(str(year)):
                    return False
            
            return True
        
        dob_cols = ['Ngày sinh', 'NGÀY SINH', 'D.O.B', 'DOB']
        dob_mask = pd.Series([False] * len(results))
        for col in dob_cols:
            if col in results.columns:
                dob_mask = dob_mask | results[col].apply(match_dob)
        results = results[dob_mask]
    
    # Chuyển sang dict
    students = results.to_dict('records')
    
    # Clean data
    for student in students:
        for key, value in student.items():
            if pd.isna(value) or str(value).lower() in ['nan', '<nan>', 'none']:
                student[key] = ''
            else:
                student[key] = str(value)
    
    return jsonify({
        'success': True,
        'students': students,
        'total': len(students)
    })

@app.route('/api/qrcode/<sbd>')
def get_qrcode(sbd):
    """Lấy QR code cho SBD"""
    global qr_codes
    
    if not HAS_QR_PIL:
        return jsonify({'error': 'QR code không khả dụng'}), 400
    
    if sbd not in qr_codes:
        return jsonify({'error': 'Không tìm thấy QR code'}), 404
    
    try:
        qr_img = qr_codes[sbd]
        # Resize
        qr_img_resized = qr_img.resize((220, 220), Image.LANCZOS if hasattr(Image, 'LANCZOS') else Image.ANTIALIAS)
        
        # Convert to base64
        buffer = io.BytesIO()
        qr_img_resized.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'qrcode': f'data:image/png;base64,{img_str}'
        })
    except Exception as e:
        return jsonify({'error': f'Lỗi tạo QR code: {str(e)}'}), 500

@app.route('/api/health')
def health():
    """Health check"""
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(debug=True)
