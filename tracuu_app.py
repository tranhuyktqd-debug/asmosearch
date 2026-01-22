# -*- coding: utf-8 -*-
"""
ỨNG DỤNG TRA CỨU THÔNG TIN HỌC SINH
Chương trình độc lập để tra cứu thông tin học sinh từ file Excel
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
import sys

try:
    import qrcode
    from PIL import Image, ImageTk
    HAS_QR_PIL = True
except ImportError:
    HAS_QR_PIL = False
    print("Warning: qrcode hoặc PIL không được cài đặt. Tính năng QR/Photo sẽ bị giới hạn.")


class StudentLookupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🔍 HỆ THỐNG TRA CỨU THÔNG TIN HỌC SINH")
        
        # Cấu hình cửa sổ và đặt ở giữa màn hình
        window_width = 1200
        window_height = 800
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.resizable(True, True)
        
        # Biến lưu trữ dữ liệu
        self.df_tracuu = None  # DataFrame dữ liệu tra cứu
        self.current_results = []  # Kết quả tìm kiếm hiện tại
        self.file_tracuu_var = tk.StringVar()  # Đường dẫn file tra cứu
        self.tracuu_sheets = []  # Danh sách sheet trong file
        self.sheet_checkboxes = {}  # Dictionary lưu checkbox các sheet
        self.qr_codes = {}  # Dictionary lưu QR code images: key=SBD, value=QR Image
        
        # Tạo giao diện
        self.create_widgets()
        
    def create_widgets(self):
        """Tạo các widget cho giao diện"""
        
        # ========== HEADER ==========
        header_frame = tk.Frame(self.root, bg="#2c3e50", height=70)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="🔍 HỆ THỐNG TRA CỨU THÔNG TIN HỌC SINH",
            font=("Arial", 18, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        title_label.pack(pady=20)
        
        # ========== MAIN CONTAINER ==========
        main_container = tk.Frame(self.root, bg="#ecf0f1")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Top Frame: Upload file và tìm kiếm
        top_frame = tk.Frame(main_container, bg="#ecf0f1")
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # === 1. UPLOAD FILE ===
        upload_frame = tk.LabelFrame(
            top_frame,
            text="📂 CHỌN FILE DỮ LIỆU",
            font=("Arial", 11, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50",
            padx=10,
            pady=10
        )
        upload_frame.pack(fill=tk.X, pady=(0, 10))
        
        file_frame = tk.Frame(upload_frame, bg="#ecf0f1")
        file_frame.pack(fill=tk.X)
        
        tk.Label(file_frame, text="File:", font=("Arial", 10), bg="#ecf0f1").pack(side=tk.LEFT, padx=5)
        tk.Entry(file_frame, textvariable=self.file_tracuu_var, width=60, font=("Arial", 9)).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        tk.Button(
            file_frame,
            text="📂 Chọn file",
            command=self.browse_file_tracuu,
            bg="#3498db",
            fg="white",
            font=("Arial", 9, "bold"),
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            file_frame,
            text="📖 Đọc file",
            command=self.load_file_tracuu,
            bg="#27ae60",
            fg="white",
            font=("Arial", 9, "bold"),
            cursor="hand2",
            relief=tk.RAISED,
            bd=2
        ).pack(side=tk.LEFT, padx=5)
        
        # Sheet selection frame
        self.sheet_selection_frame = tk.Frame(upload_frame, bg="#ecf0f1")
        self.sheet_selection_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Label(
            self.sheet_selection_frame,
            text="📑 Chọn sheet:",
            font=("Arial", 10, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        ).pack(side=tk.LEFT, padx=5)
        
        # Container for checkboxes (will be populated after reading file)
        self.sheet_checkbox_container = tk.Frame(self.sheet_selection_frame, bg="#ecf0f1")
        self.sheet_checkbox_container.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Load selected sheets button
        self.load_sheets_btn = tk.Button(
            self.sheet_selection_frame,
            text="✅ Load dữ liệu từ sheet đã chọn",
            command=self.load_selected_sheets,
            bg="#e67e22",
            fg="white",
            font=("Arial", 9, "bold"),
            cursor="hand2",
            relief=tk.RAISED,
            bd=2,
            state=tk.DISABLED
        )
        self.load_sheets_btn.pack(side=tk.RIGHT, padx=5)
        
        # === 2. SEARCH FORM ===
        search_frame = tk.LabelFrame(
            top_frame,
            text="🔍 TÌM KIẾM",
            font=("Arial", 11, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50",
            padx=10,
            pady=10
        )
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Row 1: SBD và Họ tên
        row1 = tk.Frame(search_frame, bg="#ecf0f1")
        row1.pack(fill=tk.X, pady=5)
        
        tk.Label(row1, text="SBD:", font=("Arial", 10), bg="#ecf0f1", width=10, anchor='w').pack(side=tk.LEFT)
        self.sbd_entry = tk.Entry(row1, font=("Arial", 10), width=20)
        self.sbd_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(row1, text="Họ tên:", font=("Arial", 10), bg="#ecf0f1", width=10, anchor='w').pack(side=tk.LEFT, padx=(20, 0))
        self.hoten_entry = tk.Entry(row1, font=("Arial", 10), width=25)
        self.hoten_entry.pack(side=tk.LEFT, padx=5)
        
        # Row 2: Ngày sinh
        row2 = tk.Frame(search_frame, bg="#ecf0f1")
        row2.pack(fill=tk.X, pady=5)
        
        tk.Label(row2, text="Ngày sinh:", font=("Arial", 10), bg="#ecf0f1", width=10, anchor='w').pack(side=tk.LEFT)
        
        self.day_var = tk.StringVar()
        self.month_var = tk.StringVar()
        self.year_var = tk.StringVar()
        
        tk.Label(row2, text="Ngày:", font=("Arial", 9), bg="#ecf0f1").pack(side=tk.LEFT, padx=(5, 2))
        day_combo = ttk.Combobox(row2, textvariable=self.day_var, width=5, state='readonly')
        day_combo['values'] = [''] + list(range(1, 32))
        day_combo.pack(side=tk.LEFT, padx=2)
        
        tk.Label(row2, text="Tháng:", font=("Arial", 9), bg="#ecf0f1").pack(side=tk.LEFT, padx=(10, 2))
        month_combo = ttk.Combobox(row2, textvariable=self.month_var, width=5, state='readonly')
        month_combo['values'] = [''] + list(range(1, 13))
        month_combo.pack(side=tk.LEFT, padx=2)
        
        tk.Label(row2, text="Năm:", font=("Arial", 9), bg="#ecf0f1").pack(side=tk.LEFT, padx=(10, 2))
        year_combo = ttk.Combobox(row2, textvariable=self.year_var, width=8, state='readonly')
        year_combo['values'] = [''] + list(range(2020, 1989, -1))
        year_combo.pack(side=tk.LEFT, padx=2)
        
        # Buttons
        btn_frame = tk.Frame(search_frame, bg="#ecf0f1")
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        tk.Button(
            btn_frame,
            text="🔍 TÌM KIẾM",
            command=self.search_students,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="🔄 XÓA BỘ LỌC",
            command=self.clear_search_form,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        # === 3. RESULTS TABLE & DETAILS ===
        content_frame = tk.Frame(main_container, bg="#ecf0f1")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Right: Student Info Panel (Simple) - Đặt trước để hiển thị bên phải
        right_frame = tk.Frame(content_frame, bg="white", relief=tk.SUNKEN, bd=2, width=350)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        right_frame.pack_propagate(False)
        
        # Info panel với 3 dòng - căn giữa
        info_panel = tk.Frame(right_frame, bg="#ecf0f1", relief=tk.RAISED, bd=2)
        info_panel.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Container cho thông tin text
        text_info_frame = tk.Frame(info_panel, bg="#ecf0f1")
        text_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Dòng 1: Họ tên - căn giữa
        name_frame = tk.Frame(text_info_frame, bg="#ecf0f1")
        name_frame.pack(fill=tk.X, pady=8)
        self.info_name_label = tk.Label(
            name_frame,
            text="(Chưa chọn)",
            font=("Arial", 11),
            bg="#ecf0f1",
            fg="#7f8c8d",
            anchor='center',
            wraplength=280,
            justify='center'
        )
        self.info_name_label.pack()
        
        # Dòng 2: Số báo danh - căn giữa
        sbd_frame = tk.Frame(text_info_frame, bg="#ecf0f1")
        sbd_frame.pack(fill=tk.X, pady=8)
        self.info_sbd_label = tk.Label(
            sbd_frame,
            text="(Chưa chọn)",
            font=("Arial", 11),
            bg="#ecf0f1",
            fg="#7f8c8d",
            anchor='center'
        )
        self.info_sbd_label.pack()
        
        # Dòng 3: Mã Cert - căn giữa
        cert_frame = tk.Frame(text_info_frame, bg="#ecf0f1")
        cert_frame.pack(fill=tk.X, pady=8)
        self.info_cert_label = tk.Label(
            cert_frame,
            text="(Chưa chọn)",
            font=("Arial", 14, "bold"),
            bg="#ecf0f1",
            fg="#7f8c8d",
            anchor='center',
            wraplength=280,
            justify='center'
        )
        self.info_cert_label.pack()
        
        # QR Code display - căn giữa
        qr_frame = tk.Frame(info_panel, bg="#ecf0f1", relief=tk.SUNKEN, bd=2)
        qr_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        self.qr_label = tk.Label(
            qr_frame,
            text="(Chưa chọn)",
            font=("Arial", 9, "italic"),
            bg="#ecf0f1",
            fg="#7f8c8d"
        )
        self.qr_label.pack(expand=True, pady=10)
        self.qr_image_ref = None  # Giữ reference để image không bị garbage collected
        
        # Left: Results Table
        left_frame = tk.Frame(content_frame, bg="white", relief=tk.SUNKEN, bd=2)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(
            left_frame,
            text="📋 KẾT QUẢ TÌM KIẾM",
            font=("Arial", 11, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(pady=5)
        
        # Treeview for results
        tree_frame = tk.Frame(left_frame, bg="white")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        tree_scroll_y = tk.Scrollbar(tree_frame)
        tree_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        tree_scroll_x = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        tree_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.results_tree = ttk.Treeview(
            tree_frame,
            columns=("SBD", "Họ tên", "Ngày sinh", "Khối", "Trường", "Cert", "Toán", "TA", "KH", "Sheet"),
            show="headings",
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            height=20
        )
        
        tree_scroll_y.config(command=self.results_tree.yview)
        tree_scroll_x.config(command=self.results_tree.xview)
        
        # Define columns với tên in hoa
        columns_config = [
            ("SBD", "SBD", 100),
            ("Họ tên", "HỌ TÊN", 150),
            ("Ngày sinh", "NGÀY SINH", 100),
            ("Khối", "KHỐI", 50),
            ("Trường", "TRƯỜNG", 200),
            ("Cert", "CERT", 150),
            ("Toán", "TOÁN", 120),
            ("TA", "TA", 120),
            ("KH", "KH", 120),
            ("Sheet", "SHEET", 120)
        ]
        
        # Cấu hình style cho Treeview header
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Treeview.Heading", 
                       background="#3498db",  # Màu nền xanh
                       foreground="white",     # Chữ màu trắng
                       font=("Arial", 10, "bold"),
                       relief="flat")
        style.map("Treeview.Heading",
                 background=[("active", "#2980b9")])  # Màu khi hover
        
        for col, display_name, width in columns_config:
            self.results_tree.heading(col, text=display_name)
            self.results_tree.column(col, width=width, anchor='center')
        
        self.results_tree.pack(fill=tk.BOTH, expand=True)
        self.results_tree.bind('<<TreeviewSelect>>', self.on_student_select)
    
    def browse_file_tracuu(self):
        """Chọn file tra cứu"""
        file_path = filedialog.askopenfilename(
            title="Chọn file dữ liệu tra cứu",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        if file_path:
            self.file_tracuu_var.set(file_path)
    
    def load_file_tracuu(self):
        """Đọc danh sách sheet từ file Excel"""
        file_path = self.file_tracuu_var.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn file hợp lệ!")
            return
        
        try:
            # Đọc danh sách sheet
            xl_file = pd.ExcelFile(file_path)
            self.tracuu_sheets = xl_file.sheet_names
            
            # Clear previous checkboxes
            for widget in self.sheet_checkbox_container.winfo_children():
                widget.destroy()
            self.sheet_checkboxes.clear()
            
            # Create checkboxes for each sheet
            for i, sheet_name in enumerate(self.tracuu_sheets):
                var = tk.BooleanVar(value=False)
                # Auto-select 'TRAO GIẢI' or first sheet
                if sheet_name == 'TRAO GIẢI' or (i == 0 and 'TRAO GIẢI' not in self.tracuu_sheets):
                    var.set(True)
                
                cb = tk.Checkbutton(
                    self.sheet_checkbox_container,
                    text=sheet_name,
                    variable=var,
                    bg="#ecf0f1",
                    font=("Arial", 9),
                    activebackground="#ecf0f1"
                )
                cb.pack(side=tk.LEFT, padx=5)
                self.sheet_checkboxes[sheet_name] = var
            
            # Enable load button
            self.load_sheets_btn.config(state=tk.NORMAL)
            
            messagebox.showinfo("Thành công", f"Đã tìm thấy {len(self.tracuu_sheets)} sheet!\n\nVui lòng chọn sheet và click 'Load dữ liệu'.")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đọc file:\n{str(e)}")
    
    def load_selected_sheets(self):
        """Load dữ liệu từ các sheet đã chọn"""
        file_path = self.file_tracuu_var.get()
        if not file_path or not os.path.exists(file_path):
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn file hợp lệ!")
            return
        
        # Get selected sheets
        selected_sheets = [name for name, var in self.sheet_checkboxes.items() if var.get()]
        
        if not selected_sheets:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn ít nhất 1 sheet!")
            return
        
        try:
            # Read data from selected sheets
            all_data = []
            total_students = 0
            
            for sheet_name in selected_sheets:
                df = pd.read_excel(file_path, sheet_name=sheet_name, dtype={'SBD': str})
                # Add sheet name column
                df['_SHEET_NAME'] = sheet_name
                all_data.append(df)
                total_students += len(df)
            
            # Merge all data
            self.df_tracuu = pd.concat(all_data, ignore_index=True)
            
            # Làm sạch dữ liệu: Bỏ từ "HUY CHƯƠNG" khỏi các cột kết quả
            ket_qua_cols = ['TOÁN', 'KQ VQG TOÁN', 'KHOA HỌC', 'KQ VQG KHOA HỌC', 'TIẾNG ANH', 'KQ VQG TIẾNG ANH']
            for col in ket_qua_cols:
                if col in self.df_tracuu.columns:
                    self.df_tracuu[col] = self.df_tracuu[col].apply(
                        lambda x: str(x).replace('HUY CHƯƠNG ', '').replace('HUY CHUONG ', '').replace('HUY CHƯƠNG', '').replace('HUY CHUONG', '') 
                        if pd.notna(x) and str(x).strip() != '' else x
                    )
            
            # Hiển thị tất cả học sinh ban đầu TRƯỚC khi tạo QR code
            self.current_results = self.df_tracuu.to_dict('records')
            self.display_search_results()
            self.root.update_idletasks()  # Cập nhật UI ngay lập tức
            
            # Tạo QR code cho mỗi học sinh (chạy sau khi hiển thị kết quả)
            self.qr_codes = {}  # Reset QR codes
            qr_count = 0
            try:
                if HAS_QR_PIL:
                    total_rows = len(self.df_tracuu)
                    for idx, row in self.df_tracuu.iterrows():
                        sbd = str(row.get('SBD', '')).strip()
                        if sbd and sbd.lower() not in ['nan', '<nan>', 'none', '']:
                            try:
                                # Tạo QR code với format CAN=SBD
                                qr_data = f"CAN={sbd}"
                                qr = qrcode.QRCode(version=1, box_size=5, border=1)
                                qr.add_data(qr_data)
                                qr.make(fit=True)
                                qr_img = qr.make_image(fill_color="black", back_color="white")
                                # Lưu QR code image vào dictionary
                                self.qr_codes[sbd] = qr_img
                                qr_count += 1
                            except Exception as e:
                                print(f"Lỗi tạo QR code cho SBD {sbd}: {str(e)}")
                        
                        # Cập nhật UI mỗi 100 dòng để không bị đơ
                        if (idx + 1) % 100 == 0:
                            self.root.update_idletasks()
            except Exception as e:
                print(f"Lỗi trong quá trình tạo QR code: {str(e)}")
            
            # Hiển thị thông báo sau khi hoàn thành
            if HAS_QR_PIL:
                messagebox.showinfo(
                    "Thành công", 
                    f"Đã load {total_students} học sinh từ {len(selected_sheets)} sheet!\n\n" +
                    f"Đã tạo {qr_count} mã QR code.\n\n" +
                    "\n".join([f"• {name}" for name in selected_sheets])
                )
            else:
                messagebox.showinfo(
                    "Thành công", 
                    f"Đã load {total_students} học sinh từ {len(selected_sheets)} sheet!\n\n" +
                    "⚠️ Không thể tạo QR code (thiếu thư viện qrcode/PIL).\n\n" +
                    "\n".join([f"• {name}" for name in selected_sheets])
                )
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đọc dữ liệu:\n{str(e)}")
            import traceback
            print(traceback.format_exc())
    
    def search_students(self):
        """Tìm kiếm học sinh"""
        if self.df_tracuu is None:
            messagebox.showwarning("Cảnh báo", "Vui lòng đọc file dữ liệu trước!")
            return
        
        # Lấy điều kiện tìm kiếm
        sbd = self.sbd_entry.get().strip().lower()
        hoten = self.hoten_entry.get().strip().lower()
        day = self.day_var.get()
        month = self.month_var.get()
        year = self.year_var.get()
        
        # Filter
        results = self.df_tracuu.copy()
        
        if sbd:
            results = results[results['SBD'].astype(str).str.lower().str.contains(sbd, na=False)]
        
        if hoten:
            # Tìm trong cột FULL NAME hoặc các cột tên khác
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
        
        self.current_results = results.to_dict('records')
        self.display_search_results()
        
        # Tự động chọn nếu chỉ có 1 kết quả
        if len(self.current_results) == 1:
            self.results_tree.selection_set(self.results_tree.get_children()[0])
            self.on_student_select(None)
    
    def display_search_results(self):
        """Hiển thị kết quả tìm kiếm trong bảng"""
        try:
            # Clear tree
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
            
            # Populate tree
            if self.current_results:
                # Helper function to clean nan values
                def clean_value(val):
                    if pd.isna(val) or str(val).lower() in ['nan', '<nan>', 'none']:
                        return ''
                    return str(val) if val else ''
                
                for student in self.current_results:
                    try:
                        values = (
                            clean_value(student.get('SBD', '')),
                            clean_value(student.get('FULL NAME', student.get('Họ tên', student.get('HỌ TÊN', '')))),
                            clean_value(student.get('Ngày sinh', student.get('NGÀY SINH', student.get('D.O.B', '')))),
                            clean_value(student.get('KHỐI', '')),
                            clean_value(student.get('TRƯỜNG', '')),
                            clean_value(student.get('MÃ CERT', student.get('MÃ CERT ĐẦY ĐỦ', ''))),
                            clean_value(student.get('TOÁN', student.get('KQ VQG TOÁN', ''))),
                            clean_value(student.get('TIẾNG ANH', student.get('KQ VQG TIẾNG ANH', ''))),
                            clean_value(student.get('KHOA HỌC', student.get('KQ VQG KHOA HỌC', ''))),
                            clean_value(student.get('_SHEET_NAME', ''))
                        )
                        self.results_tree.insert('', 'end', values=values)
                    except Exception as e:
                        print(f"Lỗi khi thêm dòng vào bảng: {str(e)}")
                        continue
        except Exception as e:
            print(f"Lỗi trong display_search_results: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def clear_search_form(self):
        """Xóa form tìm kiếm"""
        self.sbd_entry.delete(0, tk.END)
        self.hoten_entry.delete(0, tk.END)
        self.day_var.set('')
        self.month_var.set('')
        self.year_var.set('')
        
        # Hiển thị lại tất cả
        if self.df_tracuu is not None:
            self.current_results = self.df_tracuu.to_dict('records')
            self.display_search_results()
    
    def on_student_select(self, event):
        """Xử lý khi chọn học sinh trong bảng"""
        selection = self.results_tree.selection()
        if not selection:
            # Xóa thông tin khi không chọn
            self.info_name_label.config(text="(Chưa chọn)", fg="#7f8c8d")
            self.info_sbd_label.config(text="(Chưa chọn)", fg="#7f8c8d")
            self.info_cert_label.config(text="(Chưa chọn)", fg="#7f8c8d", font=("Arial", 14, "bold"))
            # Xóa QR code
            self.qr_label.config(image='', text="(Chưa chọn)", font=("Arial", 9, "italic"), fg="#7f8c8d")
            self.qr_image_ref = None
            return
        
        # Get selected index
        item = selection[0]
        index = self.results_tree.index(item)
        
        if 0 <= index < len(self.current_results):
            student = self.current_results[index]
            
            # Helper function to clean value
            def clean_value(val):
                if pd.isna(val) or str(val).lower() in ['nan', '<nan>', 'none']:
                    return ''
                return str(val) if val else ''
            
            # Cập nhật 3 label
            name = clean_value(student.get('FULL NAME', student.get('Họ tên', student.get('HỌ TÊN', ''))))
            sbd = clean_value(student.get('SBD', ''))
            cert = clean_value(student.get('MÃ CERT', student.get('MÃ CERT ĐẦY ĐỦ', '')))
            
            self.info_name_label.config(text=name if name else "(Không có)", fg="#2c3e50")
            self.info_sbd_label.config(text=sbd if sbd else "(Không có)", fg="#2c3e50")
            self.info_cert_label.config(
                text=cert if cert else "(Không có)", 
                fg="#e74c3c",
                font=("Arial", 14, "bold")
            )
            
            # Hiển thị QR code
            if HAS_QR_PIL and sbd and sbd in self.qr_codes:
                try:
                    qr_img = self.qr_codes[sbd]
                    # Resize QR code để vừa với panel (khoảng 220x220 để hiển thị rõ)
                    try:
                        # Thử dùng LANCZOS nếu có (PIL mới)
                        qr_img_resized = qr_img.resize((220, 220), Image.LANCZOS)
                    except AttributeError:
                        # Fallback cho PIL cũ
                        qr_img_resized = qr_img.resize((220, 220), Image.ANTIALIAS)
                    qr_photo = ImageTk.PhotoImage(qr_img_resized)
                    self.qr_label.config(image=qr_photo, text="")
                    self.qr_image_ref = qr_photo  # Giữ reference
                except Exception as e:
                    print(f"Lỗi hiển thị QR code: {str(e)}")
                    self.qr_label.config(image='', text="Lỗi hiển thị QR", font=("Arial", 9, "italic"), fg="#e74c3c")
                    self.qr_image_ref = None
            else:
                if not HAS_QR_PIL:
                    self.qr_label.config(image='', text="QR không khả dụng", font=("Arial", 9, "italic"), fg="#7f8c8d")
                elif not sbd:
                    self.qr_label.config(image='', text="(Không có SBD)", font=("Arial", 9, "italic"), fg="#7f8c8d")
                else:
                    self.qr_label.config(image='', text="(Không có QR)", font=("Arial", 9, "italic"), fg="#7f8c8d")
                self.qr_image_ref = None
    


def main():
    root = tk.Tk()
    app = StudentLookupApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
