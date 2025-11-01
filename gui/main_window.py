import customtkinter as ctk
from tkinter import messagebox, ttk
import tkinter as tk
from database.services import DatabaseService
from datetime import datetime

class MainWindow:
    def __init__(self, user):
        self.user = user
        self.db_service = DatabaseService()
        self.setup_window()
        self.create_widgets()
        self.show_dashboard()
        
    def setup_window(self):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title(f"EMS - Welcome {self.user['username']} ({self.user['role'].title()})")
        self.root.geometry("1200x800")
        
        # Add keyboard shortcut for adding employee (Ctrl+N)
        if self.user['role'] == 'admin':
            self.root.bind('<Control-n>', lambda e: self.show_add_employee_dialog())
            self.root.bind('<Control-N>', lambda e: self.show_add_employee_dialog())
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"1200x800+{x}+{y}")
        
    def create_widgets(self):
        # Main container
        self.main_container = ctk.CTkFrame(self.root)
        self.main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Sidebar
        self.sidebar = ctk.CTkFrame(self.main_container, width=250)
        self.sidebar.pack(side="left", fill="y", padx=(0, 10))
        self.sidebar.pack_propagate(False)
        
        # Content area
        self.content_frame = ctk.CTkFrame(self.main_container)
        self.content_frame.pack(side="right", fill="both", expand=True)
        
        self.create_sidebar()
        
    def create_sidebar(self):
        # Logo/Title
        title_label = ctk.CTkLabel(
            self.sidebar,
            text="👥 EMS",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        # User info
        user_frame = ctk.CTkFrame(self.sidebar)
        user_frame.pack(pady=(0, 20), padx=15, fill="x")
        
        ctk.CTkLabel(
            user_frame,
            text=f"👤 {self.user['username']}",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=(10, 5))
        
        ctk.CTkLabel(
            user_frame,
            text=f"Role: {self.user['role'].title()}",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        ).pack(pady=(0, 10))
        
        # Navigation buttons
        nav_buttons = [
            ("📊 Dashboard", self.show_dashboard),
            ("👥 Employees", self.show_employees) if self.user['role'] == 'admin' else None,
            ("🏢 Departments", self.show_departments) if self.user['role'] == 'admin' else None,
            ("🏖️ Leave Requests", self.show_leaves),
            ("💰 Salary Records", self.show_salaries),
            ("⚙️ Settings", self.show_settings),
        ]
        
        print(f"DEBUG: Creating navigation buttons for role: {self.user['role']}")
        
        for button_info in nav_buttons:
            if button_info:  # Skip None buttons for employees
                print(f"DEBUG: Creating button: {button_info[0]}")
                btn = ctk.CTkButton(
                    self.sidebar,
                    text=button_info[0],
                    command=button_info[1],
                    height=40,
                    font=ctk.CTkFont(size=12),
                    anchor="w"
                )
                btn.pack(pady=5, padx=15, fill="x")
        
        # Logout button at bottom
        logout_btn = ctk.CTkButton(
            self.sidebar,
            text="🚪 Logout",
            command=self.logout,
            height=40,
            font=ctk.CTkFont(size=12),
            fg_color="#EE3B3B",
            hover_color="darkred"
        )
        logout_btn.pack(side="bottom", pady=20, padx=15, fill="x")
    
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def create_stat_card(self, parent, icon, value, label, color):
        """Create a statistics card"""
        card = ctk.CTkFrame(parent, fg_color=color, corner_radius=15)
        
        ctk.CTkLabel(
            card, 
            text=icon, 
            font=ctk.CTkFont(size=50)
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            card, 
            text=value, 
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="white"
        ).pack()
        
        ctk.CTkLabel(
            card, 
            text=label, 
            font=ctk.CTkFont(size=14),
            text_color="white"
        ).pack(pady=(5, 20))
        
        return card
    
    def show_dashboard(self):
        self.clear_content()
        
        # Title
        title = ctk.CTkLabel(
            self.content_frame,
            text="Admin Dashboard",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(pady=(30, 20))
        
        stats = self.db_service.get_dashboard_stats()
        
        # First row - Employee and Department stats
        row1_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        row1_frame.pack(pady=10, padx=40, fill="x")
        
        # Total Employees card
        self.create_stat_card(
            row1_frame, 
            "👥", 
            str(stats['total_employees']), 
            "Total Employees",
            "#3b82f6"  # Blue
        ).pack(side="left", padx=10, fill="both", expand=True)
        
        # Total Departments card
        self.create_stat_card(
            row1_frame, 
            "🏢", 
            str(stats['total_departments']), 
            "Total Departments",
            "#8b5cf6"  # Purple
        ).pack(side="left", padx=10, fill="both", expand=True)
        
        # Second row - Leave statistics
        row2_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        row2_frame.pack(pady=10, padx=40, fill="x")
        
        # Leave Applied card
        self.create_stat_card(
            row2_frame, 
            "📝", 
            str(stats['leave_applied']), 
            "Leave Applied",
            "#06b6d4"  # Cyan
        ).pack(side="left", padx=10, fill="both", expand=True)
        
        # Leave Approved card
        self.create_stat_card(
            row2_frame, 
            "✅", 
            str(stats['leave_approved']), 
            "Leave Approved",
            "#10b981"  # Green
        ).pack(side="left", padx=10, fill="both", expand=True)
        
        # Third row - More leave statistics
        row3_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        row3_frame.pack(pady=10, padx=40, fill="x")
        
        # Leave Pending card
        self.create_stat_card(
            row3_frame, 
            "⏳", 
            str(stats['leave_pending']), 
            "Leave Pending",
            "#f59e0b"  # Orange
        ).pack(side="left", padx=10, fill="both", expand=True)
        
        # Leave Rejected card
        self.create_stat_card(
            row3_frame, 
            "❌", 
            str(stats['leave_rejected']), 
            "Leave Rejected",
            "#ef4444"  # Red
        ).pack(side="left", padx=10, fill="both", expand=True)
    
    def show_employees(self):
        if self.user['role'] != 'admin':
            messagebox.showerror("Access Denied", "Only admins can access employee management")
            return
        
        self.clear_content()
        
        # Debug print to verify user role
        print(f"DEBUG: User role: {self.user['role']}")
        print(f"DEBUG: User data: {self.user}")
        
        # Title and Add button
        header_frame = ctk.CTkFrame(self.content_frame)
        header_frame.pack(pady=(20, 10), padx=20, fill="x")
        
        ctk.CTkLabel(
            header_frame,
            text="  👥 Employee Management",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left", pady=15,padx=15)
        
        # Make the Add button more prominent
        add_btn = ctk.CTkButton(
            header_frame,
            text="➕ Add New Employee",
            command=self.show_add_employee_dialog,
            height=40,
            width=180,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        add_btn.pack(side="right", pady=15, padx=15)
        print("DEBUG: Add Employee button created and packed")
        
        # Employee list
        list_frame = ctk.CTkFrame(self.content_frame)
        list_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Create treeview for employee list
        tree_frame = tk.Frame(list_frame, bg="#212121")
        tree_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        columns = ("Serial", "ID", "Name", "DOB", "Email", "Department", "Position", "Salary", "Account")
        self.employee_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.employee_tree.heading("Serial", text="SL No.")
        self.employee_tree.heading("ID", text="Employee ID")
        self.employee_tree.heading("Name", text="Name")
        self.employee_tree.heading("DOB", text="Date of Birth")
        self.employee_tree.heading("Email", text="Email")
        self.employee_tree.heading("Department", text="Department")
        self.employee_tree.heading("Position", text="Position")
        self.employee_tree.heading("Salary", text="Salary")
        self.employee_tree.heading("Account", text="User Account")
        
        # Column widths
        self.employee_tree.column("Serial", width=50)
        self.employee_tree.column("ID", width=80)
        self.employee_tree.column("Name", width=140)
        self.employee_tree.column("DOB", width=100)
        self.employee_tree.column("Email", width=160)
        self.employee_tree.column("Department", width=100)
        self.employee_tree.column("Position", width=120)
        self.employee_tree.column("Salary", width=100)
        self.employee_tree.column("Account", width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.employee_tree.yview)
        self.employee_tree.configure(yscrollcommand=scrollbar.set)
        
        self.employee_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Load employees
        self.refresh_employee_list()
        
        # Buttons frame
        btn_frame = ctk.CTkFrame(self.content_frame)
        btn_frame.pack(pady=10, padx=20, fill="x")
        
        # Add Employee button (primary action)
        ctk.CTkButton(
            btn_frame,
            text="➕ Add New Employee",
            command=self.show_add_employee_dialog,
            height=40,
            width=150,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="🔄 Refresh",
            command=self.refresh_employee_list,
            height=35
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="✏️ Edit Selected",
            command=self.edit_employee,
            height=35
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="🗑️ Delete Selected",
            command=self.delete_employee,
            height=35,
            fg_color="#EE3B3B",
            hover_color="darkred"
        ).pack(side="left", padx=5)
        
        # Spacer
        ctk.CTkLabel(btn_frame, text=" | ", font=ctk.CTkFont(size=12)).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="👤 Create Account",
            command=self.create_user_account_for_employee,
            height=35,
            fg_color="orange",
            hover_color="darkorange",
            font=ctk.CTkFont(size=11)
        ).pack(side="left", padx=5)
    
    def refresh_employee_list(self):
        # Clear existing items
        for item in self.employee_tree.get_children():
            self.employee_tree.delete(item)
        
        # Load employees from all databases
        employees = self.db_service.get_all_employees()
        
        serial_number = 1
        for emp in employees:
            emp_id = emp['emp_id']
            
            # Check if employee has a user account
            user_account = self.db_service.get_user_by_emp_id(emp_id)
            account_status = f"{user_account['username']}" if user_account else "No Account"
            
            # Format date of birth
            dob = emp.get('date_of_birth', 'N/A')
            if dob and dob != 'N/A':
                # If it's a datetime object, format it
                if hasattr(dob, 'strftime'):
                    dob = dob.strftime('%Y-%m-%d')
            
            self.employee_tree.insert("", "end", values=(
                serial_number,
                emp['emp_id'],
                emp['name'],
                dob,
                emp['email'],
                emp['department'],
                emp['position'],
                f"${emp['salary']:,.2f}",
                account_status
            ))
            serial_number += 1
    
    def show_add_employee_dialog(self):
        dialog = EmployeeDialog(self.root, self.db_service)
        self.root.wait_window(dialog.dialog)
        self.refresh_employee_list()
    
    def edit_employee(self):
        selection = self.employee_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an employee to edit")
            return
        
        item = self.employee_tree.item(selection[0])
        emp_id = item['values'][1]  # Changed from 0 to 1 (Serial is now at 0, ID at 1)
        
        employee = self.db_service.get_employee(emp_id)
        if employee:
            dialog = EmployeeDialog(self.root, self.db_service, employee)
            self.root.wait_window(dialog.dialog)
            self.refresh_employee_list()
    
    def delete_employee(self):
        selection = self.employee_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an employee to delete")
            return
        
        item = self.employee_tree.item(selection[0])
        emp_id = item['values'][1]  # Changed from 0 to 1
        emp_name = item['values'][2]  # Changed from 1 to 2
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete employee {emp_name}?"):
            if self.db_service.delete_employee(emp_id):
                messagebox.showinfo("Success", "Employee deleted successfully")
                self.refresh_employee_list()
            else:
                messagebox.showerror("Error", "Failed to delete employee")
    
    def create_user_account_for_employee(self):
        selection = self.employee_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an employee to create user account for")
            return
        
        item = self.employee_tree.item(selection[0])
        emp_id = item['values'][1]  # Changed from 0 to 1
        emp_name = item['values'][2]  # Changed from 1 to 2
        account_status = item['values'][8]  # Changed from 7 to 8
        
        # Check if employee already has an account
        if "✅" in account_status:
            messagebox.showinfo("Account Exists", f"Employee {emp_name} already has a user account: {account_status.replace('✅ ', '')}")
            return
        
        # Open dialog to create user account
        dialog = UserAccountDialog(self.root, self.db_service, emp_id, emp_name)
        self.root.wait_window(dialog.dialog)
        self.refresh_employee_list()
    
    def show_departments(self):
        if self.user['role'] != 'admin':
            messagebox.showerror("Access Denied", "Only admins can access department management")
            return
        
        self.clear_content()
        
        # Header with title and Add button
        header_frame = ctk.CTkFrame(self.content_frame)
        header_frame.pack(pady=(20, 10), padx=20, fill="x")
        
        ctk.CTkLabel(
            header_frame,
            text="🏢 Manage Departments",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left", pady=15, padx=15)
        
        add_btn = ctk.CTkButton(
            header_frame,
            text="➕ Add New Department",
            command=self.show_add_department_dialog,
            height=40,
            width=180,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        add_btn.pack(side="right", pady=15, padx=15)
        
        # Search frame
        search_frame = ctk.CTkFrame(self.content_frame)
        search_frame.pack(pady=(0, 10), padx=20, fill="x")
        
        ctk.CTkLabel(
            search_frame,
            text="🔍 Search by Department:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=(15, 10), pady=10)
        
        self.dept_search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Enter department name...",
            height=35,
            width=300
        )
        self.dept_search_entry.pack(side="left", padx=(0, 10), pady=10)
        self.dept_search_entry.bind('<KeyRelease>', lambda e: self.filter_departments())
        
        ctk.CTkButton(
            search_frame,
            text="🔄 Refresh",
            command=self.refresh_departments,
            height=35,
            width=100
        ).pack(side="left", padx=5, pady=10)
        
        # Department table frame
        list_frame = ctk.CTkFrame(self.content_frame)
        list_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Create treeview for departments
        tree_frame = tk.Frame(list_frame, bg="#212121")
        tree_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        columns = ("S No", "Department", "Total Members")
        self.department_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.department_tree.heading("S No", text="S No")
        self.department_tree.heading("Department", text="Department")
        self.department_tree.heading("Total Members", text="Total Members")
        
        # Column widths
        self.department_tree.column("S No", width=80, anchor="center")
        self.department_tree.column("Department", width=400, anchor="w")
        self.department_tree.column("Total Members", width=150, anchor="center")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.department_tree.yview)
        self.department_tree.configure(yscrollcommand=scrollbar.set)
        
        self.department_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Load departments
        self.refresh_departments()
        
        # Action buttons frame
        btn_frame = ctk.CTkFrame(self.content_frame)
        btn_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkButton(
            btn_frame,
            text="✏️ Edit Selected",
            command=self.edit_department,
            height=35,
            width=120
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="🗑️ Delete Selected",
            command=self.delete_department,
            height=35,
            width=120,
            fg_color="#EE3B3B",
            hover_color="darkred"
        ).pack(side="left", padx=5)
    
    def show_add_department_dialog(self):
        dialog = DepartmentDialog(self.root, self.db_service)
        self.root.wait_window(dialog.dialog)
        self.refresh_departments()
    
    def refresh_departments(self):
        """Refresh the department list"""
        # Clear existing items
        for item in self.department_tree.get_children():
            self.department_tree.delete(item)
        
        # Load all departments
        departments = self.db_service.get_all_departments()
        
        serial_number = 1
        for dept in departments:
            # Get total members count for this department
            total_members = self.db_service.get_department_member_count(dept['name'])
            
            self.department_tree.insert("", "end", values=(
                serial_number,
                dept['name'],
                total_members
            ), tags=(dept['dept_id'],))
            serial_number += 1
    
    def filter_departments(self):
        """Filter departments based on search query"""
        search_query = self.dept_search_entry.get().strip().lower()
        
        # Clear existing items
        for item in self.department_tree.get_children():
            self.department_tree.delete(item)
        
        # Load all departments
        departments = self.db_service.get_all_departments()
        
        # Filter departments
        serial_number = 1
        for dept in departments:
            if search_query in dept['name'].lower():
                # Get total members count for this department
                total_members = self.db_service.get_department_member_count(dept['name'])
                
                self.department_tree.insert("", "end", values=(
                    serial_number,
                    dept['name'],
                    total_members
                ), tags=(dept['dept_id'],))
                serial_number += 1
    
    def edit_department(self):
        """Edit selected department"""
        selection = self.department_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a department to edit")
            return
        
        item = self.department_tree.item(selection[0])
        dept_id = self.department_tree.item(selection[0], 'tags')[0]
        
        # Get department data
        department = self.db_service.get_department(dept_id)
        if department:
            dialog = DepartmentDialog(self.root, self.db_service, department)
            self.root.wait_window(dialog.dialog)
            self.refresh_departments()
    
    def delete_department(self):
        """Delete selected department"""
        selection = self.department_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a department to delete")
            return
        
        item = self.department_tree.item(selection[0])
        dept_name = item['values'][1]
        dept_id = self.department_tree.item(selection[0], 'tags')[0]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete department '{dept_name}'?\n\nThis action cannot be undone."):
            if self.db_service.delete_department(dept_id):
                messagebox.showinfo("Success", "Department deleted successfully from all databases")
                self.refresh_departments()
            else:
                messagebox.showerror("Error", "Failed to delete department")
    
    def show_leaves(self):
        self.clear_content()
        
        # Initialize filter status if not exists
        if not hasattr(self, 'leave_filter_status'):
            self.leave_filter_status = "All"
        
        # Header with title
        header_frame = ctk.CTkFrame(self.content_frame)
        header_frame.pack(pady=(20, 10), padx=20, fill="x")
        
        ctk.CTkLabel(
            header_frame,
            text="🏖️ Manage Leaves",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(side="left", pady=15, padx=15)
        
        # Search and Filter frame
        search_filter_frame = ctk.CTkFrame(self.content_frame)
        search_filter_frame.pack(pady=(0, 10), padx=20, fill="x")
        
        # Search by Emp ID
        ctk.CTkLabel(
            search_filter_frame,
            text="🔍 Search by Emp ID:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=(15, 10), pady=10)
        
        self.leave_search_entry = ctk.CTkEntry(
            search_filter_frame,
            placeholder_text="Enter Employee ID...",
            height=35,
            width=200
        )
        self.leave_search_entry.pack(side="left", padx=(0, 10), pady=10)
        self.leave_search_entry.bind('<KeyRelease>', lambda e: self.filter_leaves())
        
        # Filter buttons
        ctk.CTkLabel(
            search_filter_frame,
            text="Filter:",
            font=ctk.CTkFont(size=12, weight="bold")
        ).pack(side="left", padx=(20, 10), pady=10)
        
        # All button
        self.all_btn = ctk.CTkButton(
            search_filter_frame,
            text="All",
            command=lambda: self.set_leave_filter("All"),
            height=35,
            width=90,
            fg_color="gray" if self.leave_filter_status != "All" else "#1f6aa5"
        )
        self.all_btn.pack(side="left", padx=2, pady=10)
        
        # Pending button
        self.pending_btn = ctk.CTkButton(
            search_filter_frame,
            text="Pending",
            command=lambda: self.set_leave_filter("Pending"),
            height=35,
            width=90,
            fg_color="gray" if self.leave_filter_status != "Pending" else "#f59e0b"
        )
        self.pending_btn.pack(side="left", padx=2, pady=10)
        
        # Approved button
        self.approved_btn = ctk.CTkButton(
            search_filter_frame,
            text="Approved",
            command=lambda: self.set_leave_filter("Approved"),
            height=35,
            width=90,
            fg_color="gray" if self.leave_filter_status != "Approved" else "#10b981"
        )
        self.approved_btn.pack(side="left", padx=2, pady=10)
        
        # Rejected button
        self.rejected_btn = ctk.CTkButton(
            search_filter_frame,
            text="Rejected",
            command=lambda: self.set_leave_filter("Rejected"),
            height=35,
            width=90,
            fg_color="gray" if self.leave_filter_status != "Rejected" else "#ef4444"
        )
        self.rejected_btn.pack(side="left", padx=2, pady=10)
        
        # Refresh button
        ctk.CTkButton(
            search_filter_frame,
            text="🔄 Refresh",
            command=self.refresh_leaves,
            height=35,
            width=100
        ).pack(side="right", padx=15, pady=10)
        
        # Leave table frame
        list_frame = ctk.CTkFrame(self.content_frame)
        list_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        # Create treeview for leaves
        tree_frame = tk.Frame(list_frame, bg="#212121")
        tree_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        columns = ("S No", "Emp ID", "Name", "Leave Type", "Department", "Days", "Status")
        self.leave_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.leave_tree.heading("S No", text="S No")
        self.leave_tree.heading("Emp ID", text="Emp ID")
        self.leave_tree.heading("Name", text="Name")
        self.leave_tree.heading("Leave Type", text="Leave Type")
        self.leave_tree.heading("Department", text="Department")
        self.leave_tree.heading("Days", text="Days")
        self.leave_tree.heading("Status", text="Status")
        
        # Column widths
        self.leave_tree.column("S No", width=50, anchor="center")
        self.leave_tree.column("Emp ID", width=80, anchor="center")
        self.leave_tree.column("Name", width=150, anchor="w")
        self.leave_tree.column("Leave Type", width=120, anchor="w")
        self.leave_tree.column("Department", width=120, anchor="w")
        self.leave_tree.column("Days", width=80, anchor="center")
        self.leave_tree.column("Status", width=100, anchor="center")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.leave_tree.yview)
        self.leave_tree.configure(yscrollcommand=scrollbar.set)
        
        self.leave_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Load leaves
        self.refresh_leaves()
        
        # Action buttons frame (for admin only)
        if self.user['role'] == 'admin':
            btn_frame = ctk.CTkFrame(self.content_frame)
            btn_frame.pack(pady=10, padx=20, fill="x")
            
            ctk.CTkButton(
                btn_frame,
                text="✅ Approve Selected",
                command=self.approve_selected_leave,
                height=35,
                width=150,
                fg_color="green",
                hover_color="darkgreen"
            ).pack(side="left", padx=5)
            
            ctk.CTkButton(
                btn_frame,
                text="❌ Reject Selected",
                command=self.reject_selected_leave,
                height=35,
                width=150,
                fg_color="#EE3B3B",
                hover_color="darkred"
            ).pack(side="left", padx=5)
    
    def set_leave_filter(self, status):
        """Set the leave filter status"""
        self.leave_filter_status = status
        self.refresh_leaves()
    
    def refresh_leaves(self):
        """Refresh the leave list"""
        # Clear existing items
        for item in self.leave_tree.get_children():
            self.leave_tree.delete(item)
        
        # Load all leaves
        leaves = self.db_service.get_all_leaves()
        
        # Apply status filter
        if self.leave_filter_status != "All":
            leaves = [l for l in leaves if l['status'] == self.leave_filter_status]
        
        # Apply search filter if any
        search_query = self.leave_search_entry.get().strip()
        if search_query:
            leaves = [l for l in leaves if str(l['emp_id']) == search_query]
        
        serial_number = 1
        for leave in leaves:
            # Get employee details
            emp_id = leave['emp_id']
            employee = self.db_service.get_employee(emp_id)
            emp_name = employee['name'] if employee else "Unknown"
            department = employee['department'] if employee else "N/A"
            
            # Calculate days
            days = self.calculate_leave_days(leave['start_date'], leave['end_date'])
            
            self.leave_tree.insert("", "end", values=(
                serial_number,
                emp_id,
                emp_name,
                leave['leave_type'],
                department,
                days,
                leave['status']
            ), tags=(str(leave['_id']),))
            serial_number += 1
        
        # Update filter button colors
        if hasattr(self, 'all_btn'):
            self.all_btn.configure(fg_color="gray" if self.leave_filter_status != "All" else "#1f6aa5")
            self.pending_btn.configure(fg_color="gray" if self.leave_filter_status != "Pending" else "#f59e0b")
            self.approved_btn.configure(fg_color="gray" if self.leave_filter_status != "Approved" else "#10b981")
            self.rejected_btn.configure(fg_color="gray" if self.leave_filter_status != "Rejected" else "#ef4444")
    
    def filter_leaves(self):
        """Filter leaves based on search query"""
        self.refresh_leaves()
    
    def calculate_leave_days(self, start_date, end_date):
        """Calculate number of days between two dates"""
        try:
            from datetime import datetime
            if isinstance(start_date, str):
                start = datetime.strptime(start_date, "%Y-%m-%d")
            else:
                start = start_date
            
            if isinstance(end_date, str):
                end = datetime.strptime(end_date, "%Y-%m-%d")
            else:
                end = end_date
            
            delta = end - start
            return delta.days + 1  # +1 to include both start and end date
        except Exception as e:
            print(f"Error calculating days: {e}")
            return 0
    
    def approve_selected_leave(self):
        """Approve selected leave request"""
        selection = self.leave_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a leave request to approve")
            return
        
        item = self.leave_tree.item(selection[0])
        leave_id_str = self.leave_tree.item(selection[0], 'tags')[0]
        emp_name = item['values'][2]
        status = item['values'][6]
        
        if status != "Pending":
            messagebox.showinfo("Already Processed", f"This leave request has already been {status}")
            return
        
        if messagebox.askyesno("Confirm Approval", f"Approve leave request for {emp_name}?"):
            # Convert string ID back to ObjectId
            from bson import ObjectId
            leave_id = ObjectId(leave_id_str)
            
            if self.db_service.approve_leave(leave_id, self.user['username']):
                messagebox.showinfo("Success", "Leave approved successfully")
                self.refresh_leaves()
            else:
                messagebox.showerror("Error", "Failed to approve leave")
    
    def reject_selected_leave(self):
        """Reject selected leave request"""
        selection = self.leave_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a leave request to reject")
            return
        
        item = self.leave_tree.item(selection[0])
        leave_id_str = self.leave_tree.item(selection[0], 'tags')[0]
        emp_name = item['values'][2]
        status = item['values'][6]
        
        if status != "Pending":
            messagebox.showinfo("Already Processed", f"This leave request has already been {status}")
            return
        
        if messagebox.askyesno("Confirm Rejection", f"Reject leave request for {emp_name}?"):
            # Convert string ID back to ObjectId
            from bson import ObjectId
            leave_id = ObjectId(leave_id_str)
            
            if self.db_service.reject_leave(leave_id, self.user['username']):
                messagebox.showinfo("Success", "Leave rejected successfully")
                self.refresh_leaves()
            else:
                messagebox.showerror("Error", "Failed to reject leave")
    
    def show_apply_leave_dialog(self):
        if not self.user.get('emp_id'):
            messagebox.showerror("Error", "Employee ID not found. Please contact admin.")
            return
        
        dialog = LeaveDialog(self.root, self.db_service, self.user['emp_id'])
        self.root.wait_window(dialog.dialog)
        self.show_leaves()  # Refresh
    
    def approve_leave(self, leave_id):
        if self.db_service.approve_leave(leave_id, self.user['username']):
            messagebox.showinfo("Success", "Leave approved successfully")
            self.show_leaves()  # Refresh
        else:
            messagebox.showerror("Error", "Failed to approve leave")
    
    def show_salaries(self):
        self.clear_content()
        
        # Title
        header_frame = ctk.CTkFrame(self.content_frame)
        header_frame.pack(pady=(20, 10), padx=20, fill="x")
        
        ctk.CTkLabel(
            header_frame,
            text="💰 Salary Management (Derived Fragmentation)",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left", pady=15)
        
        if self.user['role'] == 'admin':
            add_btn = ctk.CTkButton(
                header_frame,
                text="➕ Add Salary Record",
                command=self.show_add_salary_dialog,
                height=35,
                font=ctk.CTkFont(size=12)
            )
            add_btn.pack(side="right", pady=15, padx=15)
        
        # Content message
        content_frame = ctk.CTkFrame(self.content_frame)
        content_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        ctk.CTkLabel(
            content_frame,
            text="📊 Salary Management System",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(50, 20))
        
        ctk.CTkLabel(
            content_frame,
            text="Manage employee salary records efficiently",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        ).pack(pady=20)
    
    def show_add_salary_dialog(self):
        dialog = SalaryDialog(self.root, self.db_service)
        self.root.wait_window(dialog.dialog)
        self.show_salaries()  # Refresh
    
    def show_settings(self):
        self.clear_content()
        
        # Title
        ctk.CTkLabel(
            self.content_frame,
            text="⚙️ System Settings",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(20, 30))
        
        # Settings form
        settings_frame = ctk.CTkFrame(self.content_frame)
        settings_frame.pack(pady=20, padx=20, fill="x")
        
        ctk.CTkLabel(
            settings_frame,
            text="👤 User Profile",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(20, 15))
        
        # Current user info
        info_text = f"""Current Username: {self.user['username']}
Role: {self.user['role'].title()}
Employee ID: {self.user.get('emp_id', 'N/A')}
Account Type: {'Administrator' if self.user['role'] == 'admin' else 'Employee'}"""
        
        ctk.CTkLabel(
            settings_frame,
            text=info_text,
            font=ctk.CTkFont(size=12),
            justify="left"
        ).pack(pady=20)
        
        # System info
        system_frame = ctk.CTkFrame(self.content_frame)
        system_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        ctk.CTkLabel(
            system_frame,
            text="🖥️ System Information",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(20, 15))
        
        system_info = """Database: MongoDB Atlas
Security: bcrypt password encryption
Access Control: Role-based (Admin/Employee)
Version: 1.0.0"""
        
        ctk.CTkLabel(
            system_frame,
            text=system_info,
            font=ctk.CTkFont(size=11),
            justify="left",
            text_color="lightgray"
        ).pack(pady=20, padx=20)
    
    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            from gui.login_window import LoginWindow
            login_app = LoginWindow()
            login_app.run()
    
    def run(self):
        self.root.mainloop()


# Dialog classes
class EmployeeDialog:
    def __init__(self, parent, db_service, employee=None):
        self.db_service = db_service
        self.employee = employee
        self.is_edit = employee is not None
        
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Edit Employee" if self.is_edit else "Add Employee")
        self.dialog.geometry("500x750")  # Increased height to ensure buttons are visible
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (750 // 2)
        self.dialog.geometry(f"500x750+{x}+{y}")
        
        self.create_widgets()
        
        if self.is_edit:
            self.populate_fields()
    
    def create_widgets(self):
        # Main scrollable frame
        main_frame = ctk.CTkScrollableFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = "Edit Employee" if self.is_edit else "Add New Employee"
        ctk.CTkLabel(
            main_frame,
            text=title,
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(10, 20))
        
#         # Database routing info
#         if not self.is_edit:
#             info_frame = ctk.CTkFrame(main_frame)
#             info_frame.pack(fill="x", padx=20, pady=(0, 20))
            
#             ctk.CTkLabel(
#                 info_frame,
#                 text="🗄️ Database Routing Information",
#                 font=ctk.CTkFont(size=12, weight="bold")
#             ).pack(pady=(10, 5))
            
#             routing_text = """Employee ID Range → Database:
# 1-1000 → ems_db1  |  1001-2000 → ems_db2  |  2001-3000 → ems_db3"""
            
#             ctk.CTkLabel(
#                 info_frame,
#                 text=routing_text,
#                 font=ctk.CTkFont(size=10),
#                 text_color="cyan"
#             ).pack(pady=(0, 10))
        
        # Form fields
        # Employee ID
        ctk.CTkLabel(main_frame, text="Employee ID (1-3000)", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20)
        self.emp_id_entry = ctk.CTkEntry(main_frame, height=35)
        self.emp_id_entry.pack(fill="x", padx=20, pady=(5, 10))
        if self.is_edit:
            self.emp_id_entry.configure(state="disabled")
        
        # Name
        ctk.CTkLabel(main_frame, text="Full Name", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20)
        self.name_entry = ctk.CTkEntry(main_frame, height=35)
        self.name_entry.pack(fill="x", padx=20, pady=(5, 10))
        
        # Email
        ctk.CTkLabel(main_frame, text="Email", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20)
        self.email_entry = ctk.CTkEntry(main_frame, height=35)
        self.email_entry.pack(fill="x", padx=20, pady=(5, 10))
        
        # Phone
        ctk.CTkLabel(main_frame, text="Phone", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20)
        self.phone_entry = ctk.CTkEntry(main_frame, height=35)
        self.phone_entry.pack(fill="x", padx=20, pady=(5, 10))
        
        # Date of Birth
        ctk.CTkLabel(main_frame, text="Date of Birth (YYYY-MM-DD)", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20)
        self.dob_entry = ctk.CTkEntry(main_frame, height=35, placeholder_text="e.g., 1990-05-15")
        self.dob_entry.pack(fill="x", padx=20, pady=(5, 10))
        
        # Department
        ctk.CTkLabel(main_frame, text="Department", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20)
        departments = self.db_service.get_all_departments()
        dept_names = [dept['name'] for dept in departments] if departments else ["IT", "HR", "Finance"]
        self.department_combo = ctk.CTkComboBox(main_frame, values=dept_names, height=35)
        self.department_combo.pack(fill="x", padx=20, pady=(5, 10))
        
        # Position
        ctk.CTkLabel(main_frame, text="Position", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20)
        self.position_entry = ctk.CTkEntry(main_frame, height=35)
        self.position_entry.pack(fill="x", padx=20, pady=(5, 10))
        
        # Salary
        ctk.CTkLabel(main_frame, text="Salary", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20)
        self.salary_entry = ctk.CTkEntry(main_frame, height=35)
        self.salary_entry.pack(fill="x", padx=20, pady=(5, 10))
        
        # User Account Section (only for new employees)
        if not self.is_edit:
            # Separator
            separator = ctk.CTkFrame(main_frame, height=2)
            separator.pack(fill="x", padx=20, pady=20)
            
            ctk.CTkLabel(
                main_frame,
                text="👤 User Account Setup",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="yellow"
            ).pack(anchor="w", padx=20, pady=(10, 5))
            
            # Username
            ctk.CTkLabel(main_frame, text="Username (for login)", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20)
            self.username_entry = ctk.CTkEntry(main_frame, height=35, placeholder_text="Enter unique username")
            self.username_entry.pack(fill="x", padx=20, pady=(5, 10))
            
            # Password
            ctk.CTkLabel(main_frame, text="Password", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20)
            self.password_entry = ctk.CTkEntry(main_frame, height=35, show="*", placeholder_text="Enter secure password")
            self.password_entry.pack(fill="x", padx=20, pady=(5, 10))
            
            # Confirm Password
            ctk.CTkLabel(main_frame, text="Confirm Password", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20)
            self.confirm_password_entry = ctk.CTkEntry(main_frame, height=35, show="*", placeholder_text="Re-enter password")
            self.confirm_password_entry.pack(fill="x", padx=20, pady=(5, 30))
        
        # Buttons frame with prominent styling
        btn_frame = ctk.CTkFrame(main_frame)
        btn_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        # Submit/Save button (more prominent)
        save_btn = ctk.CTkButton(
            btn_frame,
            text="💾 Submit & Save" if not self.is_edit else "💾 Update Employee",
            command=self.save_employee,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        save_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="❌ Cancel",
            command=self.dialog.destroy,
            height=45,
            font=ctk.CTkFont(size=14),
            fg_color="#EE3B3B",
            hover_color="darkred"
        )
        cancel_btn.pack(side="right", fill="x", expand=True)
        
        # Add keyboard shortcuts
        self.dialog.bind('<Return>', lambda e: self.save_employee())
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())
        
        # # Help text at bottom
        # help_frame = ctk.CTkFrame(main_frame)
        # help_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # if self.is_edit:
        #     help_text = "💡 Update employee details and click 'Update Employee'\nPress Enter to submit or Escape to cancel"
        # else:
        #     help_text = "💡 Fill all fields including username and password to create employee account\nThe employee will be able to login with these credentials\nPress Enter to submit or Escape to cancel"
        
        # ctk.CTkLabel(
        #     help_frame,
        #     text=help_text,
        #     font=ctk.CTkFont(size=10),
        #     text_color="cyan",
        #     justify="center"
        # ).pack(pady=10)
    
    def populate_fields(self):
        if self.employee:
            self.emp_id_entry.insert(0, str(self.employee['emp_id']))
            self.name_entry.insert(0, self.employee['name'])
            self.email_entry.insert(0, self.employee['email'])
            self.phone_entry.insert(0, self.employee['phone'])
            
            # Handle date of birth
            dob = self.employee.get('date_of_birth', '')
            if dob:
                if hasattr(dob, 'strftime'):
                    dob = dob.strftime('%Y-%m-%d')
                self.dob_entry.insert(0, str(dob))
            
            self.department_combo.set(self.employee['department'])
            self.position_entry.insert(0, self.employee['position'])
            self.salary_entry.insert(0, str(self.employee['salary']))
            # Note: User account fields are not shown for editing existing employees
    
    def save_employee(self):
        # Validate fields
        # For edit mode, get emp_id from employee data since the field is disabled
        if self.is_edit:
            emp_id = str(self.employee['emp_id'])
        else:
            emp_id = self.emp_id_entry.get().strip()
            
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        dob = self.dob_entry.get().strip()
        department = self.department_combo.get()
        position = self.position_entry.get().strip()
        salary = self.salary_entry.get().strip()
        
        # For new employees, validate user account fields
        username = ""
        password = ""
        confirm_password = ""
        
        if not self.is_edit:
            username = self.username_entry.get().strip()
            password = self.password_entry.get().strip()
            confirm_password = self.confirm_password_entry.get().strip()
            
            if not all([emp_id, name, email, phone, dob, department, position, salary, username, password, confirm_password]):
                messagebox.showerror("Error", "Please fill all fields including date of birth and user account details")
                return
            
            # Validate password match
            if password != confirm_password:
                messagebox.showerror("Error", "Passwords do not match")
                return
            
            # Validate password strength
            if len(password) < 6:
                messagebox.showerror("Error", "Password must be at least 6 characters long")
                return
        else:
            if not all([name, email, phone, dob, department, position, salary]):
                messagebox.showerror("Error", "Please fill all fields including date of birth")
                return
        
        # Validate date format (only if dob is provided)
        if dob:
            try:
                from datetime import datetime
                datetime.strptime(dob, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD (e.g., 1990-05-15)")
                return
        
        try:
            emp_id = int(emp_id)
            salary = float(salary)
            
            # Check ID range
            if not (1 <= emp_id <= 3000):
                messagebox.showerror("Error", "Employee ID must be between 1 and 3000")
                return
                
        except ValueError:
            messagebox.showerror("Error", "Employee ID must be a number and salary must be a valid amount")
            return
        
        if self.is_edit:
            # Update employee
            update_data = {
                "name": name,
                "email": email,
                "phone": phone,
                "date_of_birth": dob,
                "department": department,
                "position": position,
                "salary": salary
            }
            
            if self.db_service.update_employee(emp_id, update_data):
                messagebox.showinfo("Success", "Employee updated successfully")
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to update employee")
        else:
            # Create new employee with user account
            success, message = self.db_service.create_employee_with_user(
                emp_id, name, email, phone, dob, department, position, salary, username, password
            )
            
            if success:
                success_msg = f"{message}\n\nUser account created with username: {username}\n\nThe employee can now login with these credentials!"
                messagebox.showinfo("Success", success_msg)
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", message)


class UserAccountDialog:
    def __init__(self, parent, db_service, emp_id, emp_name):
        self.db_service = db_service
        self.emp_id = emp_id
        self.emp_name = emp_name
        
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(f"Create User Account for {emp_name}")
        self.dialog.geometry("500x450")  # Increased from 400x350 to 500x450
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (450 // 2)
        self.dialog.geometry(f"500x450+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main scrollable frame
        main_frame = ctk.CTkScrollableFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(
            main_frame,
            text="👤 Create User Account",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(10, 5))
        
        ctk.CTkLabel(
            main_frame,
            text=f"Employee: {self.emp_name} (ID: {self.emp_id})",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(pady=(0, 20))
        
        # Username
        ctk.CTkLabel(main_frame, text="Username", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20)
        self.username_entry = ctk.CTkEntry(main_frame, height=35, placeholder_text="Enter unique username")
        self.username_entry.pack(fill="x", padx=20, pady=(5, 10))
        
        # Password
        ctk.CTkLabel(main_frame, text="Password", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20)
        self.password_entry = ctk.CTkEntry(main_frame, height=35, show="*", placeholder_text="Enter secure password")
        self.password_entry.pack(fill="x", padx=20, pady=(5, 10))
        
        # Confirm Password
        ctk.CTkLabel(main_frame, text="Confirm Password", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20)
        self.confirm_password_entry = ctk.CTkEntry(main_frame, height=35, show="*", placeholder_text="Re-enter password")
        self.confirm_password_entry.pack(fill="x", padx=20, pady=(5, 30))
        
        # Buttons
        btn_frame = ctk.CTkFrame(main_frame)
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        create_btn = ctk.CTkButton(
            btn_frame,
            text="👤 Create Account",
            command=self.create_account,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        create_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="❌ Cancel",
            command=self.dialog.destroy,
            height=40,
            font=ctk.CTkFont(size=12),
            fg_color="#EE3B3B",
            hover_color="darkred"
        )
        cancel_btn.pack(side="right", fill="x", expand=True)
        
        # Keyboard shortcuts
        self.dialog.bind('<Return>', lambda e: self.create_account())
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())
    
    def create_account(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()
        
        if not all([username, password, confirm_password]):
            messagebox.showerror("Error", "Please fill all fields")
            return
        
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters long")
            return
        
        # Check if username exists
        if self.db_service.check_username_exists(username):
            messagebox.showerror("Error", "Username already exists. Please choose a different username.")
            return
        
        # Create user account
        if self.db_service.create_user(username, password, "employee", self.emp_id):
            messagebox.showinfo("Success", f"User account created successfully!\n\nEmployee {self.emp_name} can now login with:\nUsername: {username}\nPassword: {password}")
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to create user account")


class DepartmentDialog:
    def __init__(self, parent, db_service, department=None):
        self.db_service = db_service
        self.department = department
        self.is_edit = department is not None
        
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Edit Department" if self.is_edit else "Add New Department")
        self.dialog.geometry("550x550")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (550 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (550 // 2)
        self.dialog.geometry(f"550x550+{x}+{y}")
        
        self.create_widgets()
        
        if self.is_edit:
            self.populate_fields()
    
    def create_widgets(self):
        # Main scrollable frame
        main_frame = ctk.CTkScrollableFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = "Edit Department" if self.is_edit else "Add New Department"
        ctk.CTkLabel(
            main_frame,
            text=f"🏢 {title}",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(10, 20))
        
        # Form fields
        # Department ID
        ctk.CTkLabel(main_frame, text="Department ID", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=20)
        self.dept_id_entry = ctk.CTkEntry(main_frame, height=35, placeholder_text="e.g., DEPT001")
        self.dept_id_entry.pack(fill="x", padx=20, pady=(5, 15))
        if self.is_edit:
            self.dept_id_entry.configure(state="disabled")
        
        # Name
        ctk.CTkLabel(main_frame, text="Department Name", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=20)
        self.name_entry = ctk.CTkEntry(main_frame, height=35, placeholder_text="e.g., Human Resources")
        self.name_entry.pack(fill="x", padx=20, pady=(5, 15))
        
        # Manager (optional)
        ctk.CTkLabel(main_frame, text="Manager (Optional)", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=20)
        self.manager_entry = ctk.CTkEntry(main_frame, height=35, placeholder_text="e.g., John Doe")
        self.manager_entry.pack(fill="x", padx=20, pady=(5, 15))
        
        # Description
        ctk.CTkLabel(main_frame, text="Description", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=20)
        self.description_entry = ctk.CTkTextbox(main_frame, height=100)
        self.description_entry.pack(fill="x", padx=20, pady=(5, 20))
        
        # Buttons
        btn_frame = ctk.CTkFrame(main_frame)
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        save_text = "💾 Update Department" if self.is_edit else "💾 Save & Replicate"
        save_btn = ctk.CTkButton(
            btn_frame,
            text=save_text,
            command=self.save_department,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        save_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="❌ Cancel",
            command=self.dialog.destroy,
            height=45,
            font=ctk.CTkFont(size=14),
            fg_color="#EE3B3B",
            hover_color="darkred"
        )
        cancel_btn.pack(side="right", fill="x", expand=True)
        
        # Add keyboard shortcuts
        self.dialog.bind('<Return>', lambda e: self.save_department())
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())
    
    def populate_fields(self):
        """Populate fields when editing"""
        if self.department:
            self.dept_id_entry.insert(0, str(self.department['dept_id']))
            self.name_entry.insert(0, self.department['name'])
            if self.department.get('manager'):
                self.manager_entry.insert(0, self.department['manager'])
            self.description_entry.insert("1.0", self.department.get('description', ''))
    
    def save_department(self):
        # For edit mode, get dept_id from department data since the field is disabled
        if self.is_edit:
            dept_id = str(self.department['dept_id'])
        else:
            dept_id = self.dept_id_entry.get().strip()
            
        name = self.name_entry.get().strip()
        manager = self.manager_entry.get().strip() or None
        description = self.description_entry.get("1.0", "end-1c").strip()
        
        if not all([dept_id, name, description]):
            messagebox.showerror("Error", "Please fill Department ID, Name, and Description fields")
            return
        
        if self.is_edit:
            # Update department
            update_data = {
                "name": name,
                "manager": manager,
                "description": description
            }
            
            if self.db_service.update_department(dept_id, update_data):
                messagebox.showinfo("Success", "Department updated successfully across all databases!")
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to update department")
        else:
            # Create new department
            if self.db_service.create_department(dept_id, name, description, manager):
                messagebox.showinfo("Success", "Department created and replicated across all databases!")
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to create department. Department ID might already exist.")


class LeaveDialog:
    def __init__(self, parent, db_service, emp_id):
        self.db_service = db_service
        self.emp_id = emp_id
        
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Apply for Leave")
        self.dialog.geometry("450x600")  # Increased height for better visibility
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (600 // 2)
        self.dialog.geometry(f"450x600+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main scrollable frame
        main_frame = ctk.CTkScrollableFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(
            main_frame,
            text="🏖️ Apply for Leave",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(10, 20))
        
        # Leave type
        ctk.CTkLabel(main_frame, text="Leave Type", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20)
        leave_types = ["Sick Leave", "Vacation", "Personal", "Emergency", "Maternity/Paternity"]
        self.leave_type_combo = ctk.CTkComboBox(main_frame, values=leave_types, height=35)
        self.leave_type_combo.pack(fill="x", padx=20, pady=(5, 10))
        
        # Start date
        ctk.CTkLabel(main_frame, text="Start Date (YYYY-MM-DD)", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20)
        self.start_date_entry = ctk.CTkEntry(main_frame, height=35, placeholder_text="2024-01-15")
        self.start_date_entry.pack(fill="x", padx=20, pady=(5, 10))
        
        # End date
        ctk.CTkLabel(main_frame, text="End Date (YYYY-MM-DD)", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20)
        self.end_date_entry = ctk.CTkEntry(main_frame, height=35, placeholder_text="2024-01-20")
        self.end_date_entry.pack(fill="x", padx=20, pady=(5, 10))
        
        # Reason
        ctk.CTkLabel(main_frame, text="Reason", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20)
        self.reason_entry = ctk.CTkTextbox(main_frame, height=80)
        self.reason_entry.pack(fill="x", padx=20, pady=(5, 30))
        
        # Buttons frame with prominent styling
        btn_frame = ctk.CTkFrame(main_frame)
        btn_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        # Submit button (more prominent)
        apply_btn = ctk.CTkButton(
            btn_frame,
            text="📝 Submit Leave Application",
            command=self.apply_leave,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="green",
            hover_color="darkgreen"
        )
        apply_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="❌ Cancel",
            command=self.dialog.destroy,
            height=45,
            font=ctk.CTkFont(size=14),
            fg_color="#EE3B3B",
            hover_color="darkred"
        )
        cancel_btn.pack(side="right", fill="x", expand=True)
        
        # Add keyboard shortcuts
        self.dialog.bind('<Return>', lambda e: self.apply_leave())
        self.dialog.bind('<Escape>', lambda e: self.dialog.destroy())
        
        # # Help text at bottom
        # help_frame = ctk.CTkFrame(main_frame)
        # help_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        # help_text = "💡 Fill all fields and click 'Submit Leave Application' to apply for leave\nPress Enter to submit or Escape to cancel"
        # ctk.CTkLabel(
        #     help_frame,
        #     text=help_text,
        #     font=ctk.CTkFont(size=10),
        #     text_color="cyan",
            
        #     ustify="center"
        # ).pack(pady=10)
    
    def apply_leave(self):
        leave_type = self.leave_type_combo.get()
        start_date = self.start_date_entry.get().strip()
        end_date = self.end_date_entry.get().strip()
        reason = self.reason_entry.get("1.0", "end-1c").strip()
        
        if not all([leave_type, start_date, end_date, reason]):
            messagebox.showerror("Error", "Please fill all fields")
            return
        
        # Validate date format (basic validation)
        try:
            datetime.strptime(start_date, "%Y-%m-%d")
            datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Please use YYYY-MM-DD format for dates")
            return
        
        if self.db_service.apply_leave(self.emp_id, start_date, end_date, leave_type, reason):
            messagebox.showinfo("Success", "Leave application submitted successfully!")
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to submit leave application")


class SalaryDialog:
    def __init__(self, parent, db_service):
        self.db_service = db_service
        
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Add Salary Record")
        self.dialog.geometry("500x600")  # Increased size
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (600 // 2)
        self.dialog.geometry(f"500x600+{x}+{y}")
        
        self.create_widgets()
    
    def create_widgets(self):
        # Main scrollable frame
        main_frame = ctk.CTkScrollableFrame(self.dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        ctk.CTkLabel(
            main_frame,
            text="Add Salary Record",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(10, 20))
        
        # Employee ID
        ctk.CTkLabel(main_frame, text="Employee ID", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20)
        self.emp_id_entry = ctk.CTkEntry(main_frame, height=35)
        self.emp_id_entry.pack(fill="x", padx=20, pady=(5, 10))
        
        # Month
        ctk.CTkLabel(main_frame, text="Month", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20)
        months = ["January", "February", "March", "April", "May", "June",
                 "July", "August", "September", "October", "November", "December"]
        self.month_combo = ctk.CTkComboBox(main_frame, values=months, height=35)
        self.month_combo.pack(fill="x", padx=20, pady=(5, 10))
        
        # Year
        ctk.CTkLabel(main_frame, text="Year", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20)
        self.year_entry = ctk.CTkEntry(main_frame, height=35)
        self.year_entry.insert(0, "2024")
        self.year_entry.pack(fill="x", padx=20, pady=(5, 10))
        
        # Base salary
        ctk.CTkLabel(main_frame, text="Base Salary", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20)
        self.base_salary_entry = ctk.CTkEntry(main_frame, height=35)
        self.base_salary_entry.pack(fill="x", padx=20, pady=(5, 10))
        
        # Bonus
        ctk.CTkLabel(main_frame, text="Bonus (optional)", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20)
        self.bonus_entry = ctk.CTkEntry(main_frame, height=35)
        self.bonus_entry.insert(0, "0")
        self.bonus_entry.pack(fill="x", padx=20, pady=(5, 10))
        
        # Deductions
        ctk.CTkLabel(main_frame, text="Deductions (optional)", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=20)
        self.deductions_entry = ctk.CTkEntry(main_frame, height=35)
        self.deductions_entry.insert(0, "0")
        self.deductions_entry.pack(fill="x", padx=20, pady=(5, 20))
        
        # Buttons
        btn_frame = ctk.CTkFrame(main_frame)
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        save_btn = ctk.CTkButton(
            btn_frame,
            text="Save Record",
            command=self.save_salary,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        save_btn.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            command=self.dialog.destroy,
            height=40,
            font=ctk.CTkFont(size=12),
            fg_color="gray",
            hover_color="darkgray"
        )
        cancel_btn.pack(side="right", fill="x", expand=True)
    
    def save_salary(self):
        emp_id = self.emp_id_entry.get().strip()
        month = self.month_combo.get()
        year = self.year_entry.get().strip()
        base_salary = self.base_salary_entry.get().strip()
        bonus = self.bonus_entry.get().strip() or "0"
        deductions = self.deductions_entry.get().strip() or "0"
        
        if not all([emp_id, month, year, base_salary]):
            messagebox.showerror("Error", "Please fill required fields")
            return
        
        try:
            emp_id = int(emp_id)
            year = int(year)
            base_salary = float(base_salary)
            bonus = float(bonus)
            deductions = float(deductions)
            
            if not (1 <= emp_id <= 3000):
                messagebox.showerror("Error", "Employee ID must be between 1 and 3000")
                return
                
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers")
            return
        
        if self.db_service.add_salary_record(emp_id, month, year, base_salary, bonus, deductions):
            messagebox.showinfo("Success", "Salary record saved successfully!")
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to save salary record")