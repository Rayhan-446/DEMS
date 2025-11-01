from database.connection_manager import DatabaseManager
from config.database_config import DatabaseConfig
from models.user import User
from models.employee import Employee
from models.department import Department
from models.leave import Leave
from datetime import datetime
import bcrypt

class DatabaseService:
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    # User Management (Replicated across all DBs)
    def create_user(self, username, password, role="employee", emp_id=None):
        """Create user in all databases (replication)"""
        user = User(username, password, role, emp_id)
        user_data = user.to_dict()
        
        try:
            for db in self.db_manager.get_all_databases():
                # Check if user already exists in this database
                existing = db[DatabaseConfig.USERS_COLLECTION].find_one({"username": username})
                if not existing:
                    db[DatabaseConfig.USERS_COLLECTION].insert_one(user_data)
            return True
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def authenticate_user(self, username, password):
        """Authenticate user from any database"""
        try:
            # Check first database (since users are replicated)
            db = self.db_manager.databases['db1']
            user_data = db[DatabaseConfig.USERS_COLLECTION].find_one({"username": username})
            
            if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data['password'].encode('utf-8')):
                return user_data
            return None
        except Exception as e:
            print(f"Authentication error: {e}")
            return None
    
    def get_user_by_emp_id(self, emp_id):
        """Get user account details for an employee"""
        try:
            db = self.db_manager.databases['db1']  # Users are replicated, so check any database
            user_data = db[DatabaseConfig.USERS_COLLECTION].find_one({"emp_id": emp_id})
            return user_data
        except Exception as e:
            print(f"Error getting user by emp_id: {e}")
            return None
    
    def check_username_exists(self, username):
        """Check if username already exists"""
        try:
            db = self.db_manager.databases['db1']
            return db[DatabaseConfig.USERS_COLLECTION].find_one({"username": username}) is not None
        except Exception as e:
            print(f"Error checking username: {e}")
            return False
    
    def change_user_password(self, username, new_password):
        """Change user password in all databases (since users are replicated)"""
        try:
            # Hash the new password
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Update password in all databases
            for db in self.db_manager.get_all_databases():
                db[DatabaseConfig.USERS_COLLECTION].update_one(
                    {"username": username},
                    {"$set": {"password": hashed_password}}
                )
            return True
        except Exception as e:
            print(f"Error changing password: {e}")
            return False
    
    # Employee Management (Range-based Horizontal Fragmentation)
    def create_employee(self, emp_id, name, email, phone, date_of_birth, department, position, salary):
        """Create employee in appropriate database based on ID range"""
        try:
            employee = Employee(emp_id, name, email, phone, department, position, salary, date_of_birth)
            db = self.db_manager.get_database_for_employee(emp_id)
            
            # Check if employee already exists
            if db[DatabaseConfig.EMPLOYEES_COLLECTION].find_one({"emp_id": emp_id}):
                return False, "Employee ID already exists"
            
            db[DatabaseConfig.EMPLOYEES_COLLECTION].insert_one(employee.to_dict())
            return True, "Employee created successfully"
        except Exception as e:
            return False, f"Error creating employee: {e}"
    
    def create_employee_with_user(self, emp_id, name, email, phone, date_of_birth, department, position, salary, username, password):
        """Create employee and associated user account"""
        try:
            # First check if username already exists
            db1 = self.db_manager.databases['db1']
            if db1[DatabaseConfig.USERS_COLLECTION].find_one({"username": username}):
                return False, "Username already exists. Please choose a different username."
            
            # Check if employee ID already exists
            db = self.db_manager.get_database_for_employee(emp_id)
            if db[DatabaseConfig.EMPLOYEES_COLLECTION].find_one({"emp_id": emp_id}):
                return False, "Employee ID already exists"
            
            # Create employee
            employee = Employee(emp_id, name, email, phone, department, position, salary, date_of_birth)
            db[DatabaseConfig.EMPLOYEES_COLLECTION].insert_one(employee.to_dict())
            
            # Create user account (replicated across all databases)
            user_created = self.create_user(username, password, "employee", emp_id)
            
            if not user_created:
                # Rollback employee creation if user creation fails
                db[DatabaseConfig.EMPLOYEES_COLLECTION].delete_one({"emp_id": emp_id})
                return False, "Failed to create user account. Employee creation rolled back."
            
            return True, f"Employee and user account created successfully"
            
        except Exception as e:
            return False, f"Error creating employee with user account: {e}"
    
    def get_employee(self, emp_id):
        """Get employee from appropriate database"""
        try:
            db = self.db_manager.get_database_for_employee(emp_id)
            return db[DatabaseConfig.EMPLOYEES_COLLECTION].find_one({"emp_id": int(emp_id)})
        except Exception as e:
            print(f"Error getting employee: {e}")
            return None
    
    def get_all_employees(self):
        """Get all employees from all databases (transparency)"""
        all_employees = []
        try:
            for db in self.db_manager.get_all_databases():
                employees = list(db[DatabaseConfig.EMPLOYEES_COLLECTION].find())
                all_employees.extend(employees)
            return sorted(all_employees, key=lambda x: x['emp_id'])
        except Exception as e:
            print(f"Error getting all employees: {e}")
            return []
    
    def update_employee(self, emp_id, update_data):
        """Update employee in appropriate database"""
        try:
            db = self.db_manager.get_database_for_employee(emp_id)
            result = db[DatabaseConfig.EMPLOYEES_COLLECTION].update_one(
                {"emp_id": int(emp_id)}, 
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating employee: {e}")
            return False
    
    def delete_employee(self, emp_id):
        """Delete employee from appropriate database"""
        try:
            db = self.db_manager.get_database_for_employee(emp_id)
            result = db[DatabaseConfig.EMPLOYEES_COLLECTION].delete_one({"emp_id": int(emp_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting employee: {e}")
            return False
    
    # Department Management (Replicated across all DBs)
    def create_department(self, dept_id, name, description, manager=None):
        """Create department in all databases (replication)"""
        try:
            department = Department(dept_id, name, description, manager)
            dept_data = department.to_dict()
            
            for db in self.db_manager.get_all_databases():
                # Check if department exists
                if not db[DatabaseConfig.DEPARTMENTS_COLLECTION].find_one({"dept_id": dept_id}):
                    db[DatabaseConfig.DEPARTMENTS_COLLECTION].insert_one(dept_data)
            return True
        except Exception as e:
            print(f"Error creating department: {e}")
            return False
    
    def get_all_departments(self):
        """Get all departments from first database (since replicated)"""
        try:
            db = self.db_manager.databases['db1']
            return list(db[DatabaseConfig.DEPARTMENTS_COLLECTION].find())
        except Exception as e:
            print(f"Error getting departments: {e}")
            return []
    
    def get_department(self, dept_id):
        """Get a specific department by ID"""
        try:
            db = self.db_manager.databases['db1']
            return db[DatabaseConfig.DEPARTMENTS_COLLECTION].find_one({"dept_id": dept_id})
        except Exception as e:
            print(f"Error getting department: {e}")
            return None
    
    def update_department(self, dept_id, update_data):
        """Update department in all databases (replication)"""
        try:
            for db in self.db_manager.get_all_databases():
                db[DatabaseConfig.DEPARTMENTS_COLLECTION].update_one(
                    {"dept_id": dept_id},
                    {"$set": update_data}
                )
            return True
        except Exception as e:
            print(f"Error updating department: {e}")
            return False
    
    def delete_department(self, dept_id):
        """Delete department from all databases (replication)"""
        try:
            for db in self.db_manager.get_all_databases():
                db[DatabaseConfig.DEPARTMENTS_COLLECTION].delete_one({"dept_id": dept_id})
            return True
        except Exception as e:
            print(f"Error deleting department: {e}")
            return False
    
    def get_department_member_count(self, department_name):
        """Get total number of employees in a department across all databases"""
        try:
            total_count = 0
            for db in self.db_manager.get_all_databases():
                count = db[DatabaseConfig.EMPLOYEES_COLLECTION].count_documents({"department": department_name})
                total_count += count
            return total_count
        except Exception as e:
            print(f"Error getting department member count: {e}")
            return 0
    
    # Leave Management (Derived Horizontal Fragmentation)
    def apply_leave(self, emp_id, start_date, end_date, leave_type, reason):
        """Apply leave in same database as employee (derived fragmentation)"""
        try:
            db = self.db_manager.get_database_for_employee(emp_id)
            leave = Leave(emp_id, start_date, end_date, leave_type, reason)
            db[DatabaseConfig.LEAVES_COLLECTION].insert_one(leave.to_dict())
            return True
        except Exception as e:
            print(f"Error applying leave: {e}")
            return False
    
    def get_employee_leaves(self, emp_id):
        """Get leaves for specific employee"""
        try:
            db = self.db_manager.get_database_for_employee(emp_id)
            return list(db[DatabaseConfig.LEAVES_COLLECTION].find({"emp_id": int(emp_id)}))
        except Exception as e:
            print(f"Error getting employee leaves: {e}")
            return []
    
    def get_all_leaves(self):
        """Get all leaves from all databases"""
        all_leaves = []
        try:
            for db in self.db_manager.get_all_databases():
                leaves = list(db[DatabaseConfig.LEAVES_COLLECTION].find())
                all_leaves.extend(leaves)
            return sorted(all_leaves, key=lambda x: x['applied_date'], reverse=True)
        except Exception as e:
            print(f"Error getting all leaves: {e}")
            return []
    
    def approve_leave(self, leave_id, approved_by):
        """Approve leave"""
        try:
            # Find leave in all databases
            for db in self.db_manager.get_all_databases():
                result = db[DatabaseConfig.LEAVES_COLLECTION].update_one(
                    {"_id": leave_id},
                    {"$set": {
                        "status": "Approved",
                        "approved_by": approved_by,
                        "approved_date": datetime.now()
                    }}
                )
                if result.modified_count > 0:
                    return True
            return False
        except Exception as e:
            print(f"Error approving leave: {e}")
            return False
    
    def reject_leave(self, leave_id, rejected_by):
        """Reject leave"""
        try:
            # Find leave in all databases
            for db in self.db_manager.get_all_databases():
                result = db[DatabaseConfig.LEAVES_COLLECTION].update_one(
                    {"_id": leave_id},
                    {"$set": {
                        "status": "Rejected",
                        "rejected_by": rejected_by,
                        "rejected_date": datetime.now()
                    }}
                )
                if result.modified_count > 0:
                    return True
            return False
        except Exception as e:
            print(f"Error rejecting leave: {e}")
            return False
    
    # Salary Management (Derived Horizontal Fragmentation)
    def add_salary_record(self, emp_id, month, year, base_salary, bonus=0, deductions=0):
        """Add salary record in same database as employee"""
        try:
            db = self.db_manager.get_database_for_employee(emp_id)
            salary_data = {
                "emp_id": int(emp_id),
                "month": month,
                "year": year,
                "base_salary": float(base_salary),
                "bonus": float(bonus),
                "deductions": float(deductions),
                "net_salary": float(base_salary) + float(bonus) - float(deductions),
                "created_at": datetime.now()
            }
            db[DatabaseConfig.SALARIES_COLLECTION].insert_one(salary_data)
            return True
        except Exception as e:
            print(f"Error adding salary record: {e}")
            return False
    
    def add_salary_record_with_date(self, emp_id, pay_date, base_salary, allowances=0, deductions=0):
        """Add salary record with specific pay date in same database as employee"""
        try:
            db = self.db_manager.get_database_for_employee(emp_id)
            
            # Parse date
            if isinstance(pay_date, str):
                pay_date_obj = datetime.strptime(pay_date, '%Y-%m-%d')
            else:
                pay_date_obj = pay_date
            
            net_salary = float(base_salary) + float(allowances) - float(deductions)
            
            salary_data = {
                "emp_id": int(emp_id),
                "pay_date": pay_date_obj,
                "month": pay_date_obj.strftime("%B"),
                "year": pay_date_obj.year,
                "base_salary": float(base_salary),
                "allowances": float(allowances),
                "deductions": float(deductions),
                "net_salary": net_salary,
                "created_at": datetime.now()
            }
            db[DatabaseConfig.SALARIES_COLLECTION].insert_one(salary_data)
            return True
        except Exception as e:
            print(f"Error adding salary record: {e}")
            return False
    
    def get_employee_salaries(self, emp_id):
        """Get salary records for specific employee"""
        try:
            db = self.db_manager.get_database_for_employee(emp_id)
            return list(db[DatabaseConfig.SALARIES_COLLECTION].find({"emp_id": int(emp_id)}))
        except Exception as e:
            print(f"Error getting employee salaries: {e}")
            return []
    
    def get_all_salary_records(self):
        """Get all salary records from all databases"""
        all_salaries = []
        try:
            for db in self.db_manager.get_all_databases():
                salaries = list(db[DatabaseConfig.SALARIES_COLLECTION].find())
                all_salaries.extend(salaries)
            # Sort by pay date (most recent first)
            return sorted(all_salaries, key=lambda x: x.get('pay_date', x.get('created_at', datetime.now())), reverse=True)
        except Exception as e:
            print(f"Error getting all salary records: {e}")
            return []
    
    # Statistics
    def get_dashboard_stats(self):
        """Get dashboard statistics"""
        try:
            all_leaves = self.get_all_leaves()
            
            total_employees = len(self.get_all_employees())
            total_departments = len(self.get_all_departments())
            
            # Leave statistics
            leave_applied = len(all_leaves)
            leave_pending = len([l for l in all_leaves if l['status'] == 'Pending'])
            leave_approved = len([l for l in all_leaves if l['status'] == 'Approved'])
            leave_rejected = len([l for l in all_leaves if l['status'] == 'Rejected'])
            
            # Get distribution stats
            db1_count = len(list(self.db_manager.databases['db1'][DatabaseConfig.EMPLOYEES_COLLECTION].find()))
            db2_count = len(list(self.db_manager.databases['db2'][DatabaseConfig.EMPLOYEES_COLLECTION].find()))
            db3_count = len(list(self.db_manager.databases['db3'][DatabaseConfig.EMPLOYEES_COLLECTION].find()))
            
            return {
                "total_employees": total_employees,
                "total_departments": total_departments,
                "leave_applied": leave_applied,
                "leave_pending": leave_pending,
                "leave_approved": leave_approved,
                "leave_rejected": leave_rejected,
                "db_distribution": {
                    "db1": db1_count,
                    "db2": db2_count,
                    "db3": db3_count
                }
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {
                "total_employees": 0, 
                "total_departments": 0,
                "leave_applied": 0,
                "leave_pending": 0, 
                "leave_approved": 0,
                "leave_rejected": 0,
                "db_distribution": {"db1": 0, "db2": 0, "db3": 0}
            }