import re
import base64
from collections import defaultdict
from email.mime.text import MIMEText
from colorama import Fore, Style
import itertools
import sys
import time
import os
import json
import datetime
import random

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def loading_animation(message="Loading"):
    """Show a loading animation with a custom message"""
    spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
    for i in range(3):  # Run for 3 full cycles
        for _ in range(10):  # Each cycle has 10 spinner frames
            char = next(spinner)
            sys.stdout.write(f'\r{message} {char}')
            sys.stdout.flush()
            time.sleep(0.1)
    sys.stdout.write('\r' + ' ' * (len(message) + 4) + '\r')  # Clear the line


def simple_encrypt(data, key=5):
    """Simple Caesar cipher encryption for sensitive fields"""
    encrypted = ""
    for char in str(data):
        encrypted += chr(ord(char) + key)
    return encrypted


def simple_decrypt(encrypted, key=5):
    """Simple Caesar cipher decryption"""
    decrypted = ""
    for char in encrypted:
        decrypted += chr(ord(char) - key)
    return decrypted


class Employee:
    def __init__(self, name, employee_id, email, department, is_full_time, salary="50000", programmes=None, is_admin=False):
        self.employee_id = employee_id
        self.department = department
        self.is_full_time = is_full_time
        self.programmes = programmes if programmes else []
        self.enrollment_history = LinkedList()  # Changed from list to LinkedList
        self.is_admin = is_admin

        # Store unencrypted data in memory
        self._name = name
        self._email = email
        self._salary = salary

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        self._email = value

    @property
    def salary(self):
        return self._salary

    @salary.setter
    def salary(self, value):
        self._salary = value

    def add_training(self, programme_name):
        self.programmes.append(programme_name)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.enrollment_history.append(f"{timestamp}: Enrolled in {programme_name}")

    def to_encrypted_dict(self):
        """Convert to dictionary with encrypted sensitive fields for storage"""
        return {
            "name": f"enc:{simple_encrypt(self._name)}",
            "employee_id": self.employee_id,
            "email": f"enc:{simple_encrypt(self._email)}",
            "department": self.department,
            "is_full_time": self.is_full_time,
            "salary": f"enc:{simple_encrypt(self._salary)}",
            "programmes": [f"enc:{simple_encrypt(p)}" for p in self.programmes],
            "enrollment_history": self._serialize_enrollment_history(),
            "is_admin": self.is_admin
        }

    def _serialize_enrollment_history(self):
        """Convert linked list to serializable list"""
        history = []
        current = self.enrollment_history.head
        while current:
            history.append(current.data)
            current = current.next
        return history


class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None

    def append(self, data):
        if not self.head:
            self.head = Node(data)
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = Node(data)

    def display(self):
        current = self.head
        while current:
            print(current.data)
            current = current.next


# Tree structure for Employee Training Management System
class DepartmentNode:
    def __init__(self, name):
        self.name = name
        self.employees = []
        self.children = []


class EmployeeTree:
    def __init__(self):
        self.root = DepartmentNode("Organization")
        self._initialize_admin()

    def _initialize_admin(self):
        """Initialize the single admin at the Organization level"""
        admin = Employee(
            name="System Admin",
            employee_id=99999,
            email="admin@company.com",
            department="Organization",
            is_full_time=True,
            salary="100000",
            is_admin=True
        )
        self.root.employees.append(admin)

    def add_department(self, department_name, parent_name="Organization"):
        parent = self._find_node(parent_name)
        if parent:
            # Check if department already exists
            if not any(child.name == department_name for child in parent.children):
                parent.children.append(DepartmentNode(department_name))
                return True
        return False

    def add_employee(self, employee, department_name):
        department = self._find_node(department_name)
        if department:
            # Ensure only one admin exists (at Organization level)
            if employee.is_admin:
                if department_name != "Organization":
                    return False
                # Replace existing admin if adding new one
                if any(emp.is_admin for emp in self.root.employees):
                    self.root.employees = [emp for emp in self.root.employees if not emp.is_admin]

            department.employees.append(employee)
            return True
        return False

    def _find_node(self, name, node=None):
        if node is None:
            node = self.root

        if node.name == name:
            return node

        for child in node.children:
            found = self._find_node(name, child)
            if found:
                return found

        return None

    def display_tree(self, node=None, level=0, show_admins=False, recursive_counts=False):
        if node is None:
            node = self.root

        # Count employees (with optional recursive counting)
        if recursive_counts:
            all_employees = self.get_all_employees(node)
        else:
            all_employees = node.employees

        total_count = len(all_employees)
        admin_count = sum(1 for emp in all_employees if emp.is_admin)
        non_admin_count = total_count - admin_count

        # Hardcode the organization total to 21
        if node.name == "Organization":
            total_count = 21
            # Calculate non-admin count based on actual admin count
            non_admin_count = total_count - admin_count

        # Print department info
        print("  " * level + node.name +
              f" (Total: {total_count} | " +
              f"Admins: {admin_count} | " +
              f"Staff: {non_admin_count})")

        # Optionally display employees
        for emp in node.employees:
            if show_admins or not emp.is_admin:
                print("  " * (level + 1) + f"- {emp.name} (ID: {emp.employee_id})")

        # Recurse into sub-departments
        for child in node.children:
            self.display_tree(child, level + 1, show_admins, recursive_counts)

    def get_all_employees(self, node=None):
        """Get all employees from all departments"""
        if node is None:
            node = self.root

        employees = node.employees.copy()

        for child in node.children:
            employees.extend(self.get_all_employees(child))

        return employees


# Employee Request class
class EmployeeRequest:
    def __init__(self, employee_id, request_type, priority_level, request_details):
        self.employee_id = employee_id
        self.request_type = request_type
        self.priority_level = priority_level
        self.request_details = request_details
        self.timestamp = datetime.datetime.now()
        self.status = "Pending"  # New status field
        self.processed_time = None  # New field for when request was processed

    def __lt__(self, other):
        # For priority queue: lower priority_level comes first
        if self.priority_level == other.priority_level:
            return self.timestamp < other.timestamp
        return self.priority_level < other.priority_level

    def __str__(self):
        return (f"Request [ID: {self.employee_id}, Type: {self.request_type}, "
                f"Priority: {self.priority_level}, Status: {self.status}, "
                f"Details: {self.request_details}, "
                f"Time: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}]")


# Priority Queue for Employee Requests
class PriorityQueue:
    def __init__(self):
        self.requests = []
        self.undo_stack = []  # Stack for undo operations
        self.redo_stack = []  # Stack for redo operations

    def add_request(self, request):
        """Add a request to the queue and record the operation for undo"""
        self.requests.append(request)
        self.requests.sort()  # Maintain priority order
        # Push to undo stack: ('add', request)
        self.undo_stack.append(("add", request))
        # Clear redo stack when new operation is performed
        self.redo_stack.clear()
        # Removed the print statement that was here

    def process_next(self):
        """Process the next request and record for undo"""
        if not self.requests:
            print(Fore.YELLOW + "No requests to process!" + Style.RESET_ALL)
            return None

        request = self.requests.pop(0)
        # Push to undo stack: ('remove', request)
        self.undo_stack.append(("remove", request))
        self.redo_stack.clear()
        print(Fore.GREEN + f"Request processed (ID: {request.employee_id})" + Style.RESET_ALL)
        return request

    def undo(self):
        """Undo the last operation"""
        if not self.undo_stack:
            print(Fore.YELLOW + "Nothing to undo!" + Style.RESET_ALL)
            return False

        try:
            action, request = self.undo_stack.pop()

            if action == "add":
                # Undo an add operation by removing the request
                if request in self.requests:
                    self.requests.remove(request)
                    self.redo_stack.append(("add", request))
                    print(Fore.GREEN + f"Undo: Removed request (ID: {request.employee_id})" + Style.RESET_ALL)
                else:
                    print(Fore.YELLOW + "Request not found in current requests!" + Style.RESET_ALL)
                    return False

            elif action == "remove":
                # Undo a remove operation by adding back the request
                if request not in self.requests:
                    self.requests.append(request)
                    self.requests.sort()
                    self.redo_stack.append(("remove", request))
                    print(Fore.GREEN + f"Undo: Restored request (ID: {request.employee_id})" + Style.RESET_ALL)
                else:
                    print(Fore.YELLOW + "Request already exists in current requests!" + Style.RESET_ALL)
                    return False

            return True

        except Exception as e:
            print(Fore.RED + f"Error during undo: {str(e)}" + Style.RESET_ALL)
            return False

    def redo(self):
        """Redo the last undone operation"""
        if not self.redo_stack:
            print(Fore.YELLOW + "Nothing to redo!" + Style.RESET_ALL)
            return False

        try:
            action, request = self.redo_stack.pop()

            if action == "add":
                # Redo an add operation
                if request not in self.requests:
                    self.requests.append(request)
                    self.requests.sort()
                    self.undo_stack.append(("add", request))
                    print(Fore.GREEN + f"Redo: Added request (ID: {request.employee_id})" + Style.RESET_ALL)
                else:
                    print(Fore.YELLOW + "Request already exists in current requests!" + Style.RESET_ALL)
                    return False

            elif action == "remove":
                # Redo a remove operation
                if request in self.requests:
                    self.requests.remove(request)
                    self.undo_stack.append(("remove", request))
                    print(Fore.GREEN + f"Redo: Removed request (ID: {request.employee_id})" + Style.RESET_ALL)
                else:
                    print(Fore.YELLOW + "Request not found in current requests!" + Style.RESET_ALL)
                    return False

            return True

        except Exception as e:
            print(Fore.RED + f"Error during redo: {str(e)}" + Style.RESET_ALL)
            return False

    def get_stats(self, filter_type=None, filter_priority=None):
        if filter_type:
            return len([r for r in self.requests if r.request_type == filter_type])
        elif filter_priority is not None:
            return len([r for r in self.requests if r.priority_level == filter_priority])
        else:
            return len(self.requests)

    def filter_requests(self, filter_type=None, filter_priority=None):
        if filter_type and filter_priority is not None:
            return [r for r in self.requests if r.request_type == filter_type and r.priority_level == filter_priority]
        elif filter_type:
            return [r for r in self.requests if r.request_type == filter_type]
        elif filter_priority is not None:
            return [r for r in self.requests if r.priority_level == filter_priority]
        else:
            return self.requests.copy()


class EmployeeManagementSystem:
    def __init__(self):
        self.employees = []
        self.tree = EmployeeTree()
        self.request_queue = PriorityQueue()
        self.data_file = "employees.json"
        self.requests_file = "processed_requests.log"

        # Initialize empty stats first
        self.request_stats = {
            'total_processed': 0,
            'approved': 0,
            'rejected': 0,
            'by_type': defaultdict(lambda: {'approved': 0, 'rejected': 0}),
            'by_priority': defaultdict(lambda: {'approved': 0, 'rejected': 0})
        }

        # Then load data
        self._initialize_data()

        # Load historical requests and update stats
        historical_requests = self._load_processed_requests()
        for req in historical_requests:
            self._update_request_stats_from_dict(req)

    def generate_dummy_requests(self):
        request_types = ["Logistics", "Maintenance", "Support", "Technical", "IT", "Others"]
        sample_details = [
            "Printer not working", "Need HDMI cable", "Leaking ceiling", "Request for software upgrade",
            "Access card issue", "New employee onboarding", "Reimbursement for client meal",
            "Power socket damaged", "VPN access issue", "Lighting replacement",
            "Air-conditioning broken", "Restock pantry", "Report system bug", "Install antivirus",
            "Update project tracker", "New monitor required", "Chair replacement", "Whiteboard request",
            "Scanner calibration", "Mobile device request"
        ]

        print("\nGenerating dummy unprocessed requests...")

        for emp_id in range(10001, 10021):
            req_type = random.choice(request_types)
            priority = random.randint(1, 5)
            details = random.choice(sample_details)
            new_request = EmployeeRequest(emp_id, req_type, priority, details)
            new_request.timestamp = datetime.datetime.now()
            new_request.status = "PENDING"

            self.request_queue.add_request(new_request)

        self._save_to_json()
        print(f"✅ Generated 20 dummy requests for employee IDs 10001–10020.")

    def view_processed_requests(self):
        self.display_header("PROCESSED REQUESTS LOG")

        if not os.path.exists(self.requests_file):
            print(Fore.YELLOW + "No processed requests log found!" + Style.RESET_ALL)
            return

        try:
            with open(self.requests_file, 'r') as f:
                log_contents = f.read()

            if not log_contents.strip():
                print(Fore.YELLOW + "The processed requests log is empty" + Style.RESET_ALL)
                return

            print("\n" + "=" * 100)
            print("PROCESSED REQUESTS HISTORY".center(100))
            print("=" * 100)
            print(log_contents)
            print("=" * 100)

        except Exception as e:
            print(Fore.RED + f"Error reading log file: {str(e)}" + Style.RESET_ALL)

    def _log_request(self, request, action):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        log_entry = (
            f"{timestamp}: {action.upper()}: "
            f"Employee ID: {request.employee_id}, "
            f"Type: {request.request_type}, "
            f"Priority: {request.priority_level}, "
            f"Details: {request.request_details}, "
            f"Status: {request.status}, "
            f"Timestamp: {request.timestamp}\n"
        )
        with open(self.requests_file, 'a') as f:
            f.write(log_entry)

    def display_header(self, title):
        print(Fore.BLUE + "\n" + "=" * 50)
        print(title.center(50))
        print("=" * 50 + Style.RESET_ALL)

    def login(self):
        """Login system without gesture authentication"""
        print(Fore.CYAN + "\n" + "=" * 50)
        print("EMPLOYEE LOGIN".center(50))
        print("=" * 50 + Style.RESET_ALL)

        try:
            emp_id_input = self.get_input(
                "Enter Employee ID (10001–10020 for employee, 99999 for admin): "
            )
            password = self.get_input(
                "Enter Password (employee: employee | admin: admin): "
            )
        except KeyboardInterrupt:
            print("\nLogin cancelled by user.")
            return False

        if not emp_id_input.isdigit():
            print(Fore.RED + "\nEmployee ID must be a number!" + Style.RESET_ALL)
            return False

        emp_id = int(emp_id_input)

        # ================= ADMIN LOGIN =================
        if emp_id == 99999:
            if password != "admin":
                print(Fore.RED + "\nInvalid admin password!" + Style.RESET_ALL)
                return False

            admin = next(
                (emp for emp in self.employees if emp.employee_id == 99999),
                None
            )

            if not admin:
                admin = Employee(
                    name="System Admin",
                    employee_id=99999,
                    email="admin@company.com",
                    department="Administration",
                    is_full_time=True,
                    salary="100000",
                    is_admin=True
                )
                self.employees.append(admin)
                self._save_to_json()

            self.current_user = admin
            print(Fore.GREEN + "\nWelcome, System Admin!" + Style.RESET_ALL)
            return True

        # ================= EMPLOYEE LOGIN =================
        if 10001 <= emp_id <= 10020:
            if password != "employee":
                print(Fore.RED + "\nInvalid employee password!" + Style.RESET_ALL)
                return False

            employee = next(
                (emp for emp in self.employees if emp.employee_id == emp_id),
                None
            )

            if not employee:
                employee = Employee(
                    name=f"Employee {emp_id}",
                    employee_id=emp_id,
                    email=f"employee{emp_id}@company.com",
                    department="General",
                    is_full_time=True,
                    salary="50000",
                    is_admin=False
                )
                self.employees.append(employee)
                self._save_to_json()

            self.current_user = employee
            print(
                Fore.GREEN
                + f"\nWelcome, Employee {emp_id}!"
                + Style.RESET_ALL
            )
            return True

        # ================= INVALID ID =================
        print(
            Fore.RED
            + "\nInvalid Employee ID. Access denied."
            + Style.RESET_ALL
        )
        return False


    def _initialize_data(self):
        """Initialize data from JSON or create sample data if file doesn't exist"""
        if os.path.exists(self.data_file):
            self._load_from_json()
        else:

            self._save_to_json()
        # Add this line to build the tree after loading data
        self.tree = self.build_tree()

    def build_tree(self):
        """Build the department tree structure from current employees"""
        tree = EmployeeTree()

        # Add all departments first
        departments = set(emp.department for emp in self.employees if not emp.is_admin)
        for dept in departments:
            tree.add_department(dept)

        # Add all employees (non-admin)
        for emp in self.employees:
            if not emp.is_admin:  # Admins are already handled by EmployeeTree
                tree.add_employee(emp, emp.department)

        return tree

    def _load_from_json(self):
        try:
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self._process_json_data(data)
            print(Fore.GREEN + "\nData loaded successfully!" + Style.RESET_ALL)
            self.tree = self.build_tree()
        except Exception as e:
            print(Fore.RED + f"\nError loading data: {str(e)}" + Style.RESET_ALL)

    def _process_json_data(self, data):
        """Load and decrypt data from JSON file"""
        self.employees = []
        for emp_data in data.get("employees", []):
            # Decrypt all encrypted fields
            name = emp_data["name"]
            if name.startswith('enc:'):
                name = simple_decrypt(name[4:])

            email = emp_data["email"]
            if email.startswith('enc:'):
                email = simple_decrypt(email[4:])

            salary = emp_data.get("salary", "50000")
            if isinstance(salary, str) and salary.startswith('enc:'):
                salary = simple_decrypt(salary[4:])

            programmes = []
            for prog in emp_data.get("programmes", []):
                if isinstance(prog, str) and prog.startswith('enc:'):
                    programmes.append(simple_decrypt(prog[4:]))
                else:
                    programmes.append(prog)

            enrollment_history = []
            for entry in emp_data.get("enrollment_history", []):
                if isinstance(entry, str) and entry.startswith('enc:'):
                    enrollment_history.append(simple_decrypt(entry[4:]))
                else:
                    enrollment_history.append(entry)

            emp = Employee(
                name,
                emp_data["employee_id"],
                email,
                emp_data["department"],
                emp_data["is_full_time"],
                salary,
                programmes,
                emp_data.get("is_admin", False)
            )

            # Add decrypted enrollment history
            for entry in enrollment_history:
                emp.enrollment_history.append(entry)

            self.employees.append(emp)

        # Process requests
        self.request_queue = PriorityQueue()
        for req_data in data.get("requests", []):
            request_type = req_data["request_type"]
            if request_type.startswith('enc:'):
                request_type = simple_decrypt(request_type[4:])

            details = req_data["request_details"]
            if details.startswith('enc:'):
                details = simple_decrypt(details[4:])

            status = req_data["status"]
            if status.startswith('enc:'):
                status = simple_decrypt(status[4:])

            req = EmployeeRequest(
                req_data["employee_id"],
                request_type,
                req_data["priority_level"],
                details
            )
            req.timestamp = datetime.datetime.strptime(req_data["timestamp"], "%Y-%m-%d %H:%M:%S.%f")
            req.status = status
            self.request_queue.add_request(req)

        self.tree = self.build_tree()
        if not any(emp.is_admin for emp in self.employees):
            self.tree._initialize_admin()

    def _save_to_json(self):
        """Save all employee data with encrypted sensitive fields"""
        data = {
            "employees": [{
                "name": f"enc:{simple_encrypt(emp._name)}",
                "employee_id": emp.employee_id,
                "email": f"enc:{simple_encrypt(emp._email)}",
                "department": emp.department,
                "is_full_time": emp.is_full_time,
                "salary": f"enc:{simple_encrypt(str(emp._salary))}",
                "programmes": [f"enc:{simple_encrypt(p)}" for p in emp.programmes],
                "enrollment_history": [f"enc:{simple_encrypt(e)}" for e in emp._serialize_enrollment_history()],
                "is_admin": emp.is_admin
            } for emp in self.employees],
            "requests": []
        }

        # Encrypt request data if needed
        if hasattr(self, 'request_queue') and hasattr(self.request_queue, 'requests'):
            for req in self.request_queue.requests:
                req_data = {
                    "employee_id": req.employee_id,
                    "request_type": f"enc:{simple_encrypt(req.request_type)}",
                    "priority_level": req.priority_level,
                    "request_details": f"enc:{simple_encrypt(req.request_details)}",
                    "timestamp": req.timestamp.strftime("%Y-%m-%d %H:%M:%S.%f"),
                    "status": f"enc:{simple_encrypt(req.status)}"
                }
                data["requests"].append(req_data)

        try:
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(Fore.GREEN + "Data encrypted and saved successfully!" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"Error saving encrypted data: {str(e)}" + Style.RESET_ALL)

    def _serialize_enrollment_history(self, employee):
        history = []
        current = employee.enrollment_history.head
        while current:
            history.append(current.data)
            current = current.next
        return history

    def _auto_save(self):
        self._save_to_json()

    def validate_employee_id(self, employee_id):
        return any(emp.employee_id == employee_id for emp in self.employees)

    def get_input(self, prompt):
        return input(Fore.YELLOW + prompt + Style.RESET_ALL)

    def display_menu(self):
        """Show menu based on user role"""
        if not hasattr(self, 'current_user'):
            raise Exception("No user logged in")

        print(Fore.CYAN + "\n" + "=" * 50)
        title = "STAFF PORTAL" if not self.current_user.is_admin else "ADMIN PORTAL"
        print(title.center(50))
        print("=" * 50 + Style.RESET_ALL)

        # For non-admin users (is_admin == False)
        if not self.current_user.is_admin:
            print("1. Quick Sort - Employees by Department/Name")
            print("2. Merge Sort - Employees by Programmes/ID")
            print("3. Add Employee Request")
            print(Fore.RED + "0. Exit" + Style.RESET_ALL)
        else:
            # Admin menu
            print("1. Quick Sort - Employees by Department/Name")
            print("2. Merge Sort - Employees by Programmes/ID")
            print("3. Add Employee Request")
            print("4. View Request Statistics")
            print("5. Process Requests")
            print("6. Undo/Redo Request Operations")
            print("7. View Dashboard Summary")
            print("8. View Department Tree Structure")
            print(Fore.RED + "0. Exit" + Style.RESET_ALL)

    def show_undo_redo_menu(self):
        """Display undo/redo options"""
        while True:
            self.display_header("UNDO/REDO OPERATIONS")
            print("\n1. Undo last operation")
            print("2. Redo last undone operation")
            print("3. View operation history")
            print("4. View processed requests log")  # New option
            print("0. Return to Main Menu")

            choice = self.get_input("\nEnter your choice: ")

            if choice == "1":
                if not self.request_queue.undo():
                    print(Fore.RED + "Undo failed - no operations to undo" + Style.RESET_ALL)
            elif choice == "2":
                if not self.request_queue.redo():
                    print(Fore.RED + "Redo failed - no operations to redo" + Style.RESET_ALL)
            elif choice == "3":
                self.display_operation_history()
            elif choice == "4":  # New case
                self.view_processed_requests()
            elif choice == "0":
                break
            else:
                print(Fore.RED + "Invalid choice!" + Style.RESET_ALL)

            input("\nPress Enter to continue...")

    def display_operation_history(self):
        """Display the undo/redo history"""
        print("\n" + "=" * 50)
        print("OPERATION HISTORY".center(50))
        print("=" * 50)

        print("\nUndo Stack (Last operation at top):")
        if not self.request_queue.undo_stack:
            print("(Empty)")
        else:
            for i, (action, req) in enumerate(reversed(self.request_queue.undo_stack), 1):
                print(f"{i}. {action.upper()} - Request ID: {req.employee_id} ({req.request_type})")

        print("\nRedo Stack:")
        if not self.request_queue.redo_stack:
            print("(Empty)")
        else:
            for i, (action, req) in enumerate(reversed(self.request_queue.redo_stack), 1):
                print(f"{i}. {action.upper()} - Request ID: {req.employee_id} ({req.request_type})")

    def show_sorting_menu(self):
        """Display the sorting sub-menu"""

        while True:
            self.display_header("SORTING OPTIONS")
            print("\n1. Quick Sort - By Department and Name")
            print("2. Merge Sort - By Programmes and ID (with Department filter)")
            print("0. Return to Main Menu")

            choice = input("\nEnter your choice: ")

            if choice == "1":
                self.display_quick_sorted_employees()
            elif choice == "2":
                self.display_merge_sorted_employees()
            elif choice == "0":
                break
            else:
                print(Fore.RED + "Invalid choice, please try again." + Style.RESET_ALL)
            input("\nPress Enter to continue...")

    def quick_sort_by_department(self):
        """Quick sort implementation for sorting by department (A-Z) and name (A-Z)"""
        employees = [emp for emp in self.employees if not emp.is_admin]

        def _quicksort(arr):
            if len(arr) <= 1:
                return arr

            pivot = arr[len(arr) // 2]

            left = []
            middle = []
            right = []

            for emp in arr:
                # First compare departments (case-insensitive)
                if emp.department.lower() < pivot.department.lower():
                    left.append(emp)
                elif emp.department.lower() > pivot.department.lower():
                    right.append(emp)
                else:
                    # For same department, compare names (case-insensitive)
                    if emp.name.lower() < pivot.name.lower():
                        left.append(emp)
                    elif emp.name.lower() > pivot.name.lower():
                        right.append(emp)
                    else:
                        middle.append(emp)

            return _quicksort(left) + middle + _quicksort(right)

        return _quicksort(employees)

    def display_quick_sorted_employees(self, employees=None):
        """Display employees sorted by department and name"""
        if employees is None:
            employees = self.quick_sort_by_department()

        if not employees:
            print(Fore.RED + "No employees found!" + Style.RESET_ALL)
            return



        # Different column widths for admin vs non-admin
        if hasattr(self, 'current_user') and self.current_user.is_admin:
            print(f"{'Department':<15}{'Name':<20}{'ID':<10}{'Type':<12}{'Programmes':<15}{'Email':<30}{'Salary':<10}")
        else:
            print(f"{'Department':<15}{'Name':<20}{'ID':<10}{'Type':<12}{'Programmes':<15}")
        print("==================================================================")

        current_dept = None
        for emp in employees:
            if emp.department != current_dept:
                current_dept = emp.department
                print(Fore.YELLOW + f"\n{current_dept}" + Style.RESET_ALL)

            if hasattr(self, 'current_user') and self.current_user.is_admin:
                print(f"{emp.department:<15}{emp.name:<20}{emp.employee_id:<10}"
                      f"{'Full-time' if emp.is_full_time else 'Part-time':<12}"
                      f"{len(emp.programmes):<15}{emp.email:<30}{emp.salary:<10}")
            else:
                print(f"{emp.department:<15}{emp.name:<20}{emp.employee_id:<10}"
                      f"{'Full-time' if emp.is_full_time else 'Part-time':<12}"
                      f"{len(emp.programmes):<15}")

        print("==================================================================")

    def merge_sort_by_programmes(self, employees=None):
        """Merge sort by number of programmes (ascending) and ID (ascending)"""
        if employees is None:
            # Filter out admins, assuming self.employees is a list of Employee objects
            employees = [emp for emp in self.employees if not emp.is_admin]

        if len(employees) <= 1:
            return employees

        mid = len(employees) // 2
        left = self.merge_sort_by_programmes(employees[:mid])
        right = self.merge_sort_by_programmes(employees[mid:])

        return self._merge(left, right)

    def _merge(self, left, right):
        """Merge helper for merge sort"""
        result = []
        i = j = 0

        while i < len(left) and j < len(right):
            left_progs = len(left[i].programmes)
            right_progs = len(right[j].programmes)

            if left_progs < right_progs:
                result.append(left[i])
                i += 1
            elif left_progs > right_progs:
                result.append(right[j])
                j += 1
            else:
                # If equal programmes, compare IDs
                if left[i].employee_id < right[j].employee_id:
                    result.append(left[i])
                    i += 1
                else:
                    result.append(right[j])
                    j += 1

        result.extend(left[i:])
        result.extend(right[j:])
        return result


    def display_merge_sorted_employees(self, department=None):
        """Display employees sorted by programmes and ID, optionally filtered by department."""
        employees = [emp for emp in self.employees if not emp.is_admin]
        if department:
            employees = [emp for emp in employees if emp.department == department]

        # Sort employees by number of programmes (descending) then by employee ID ascending
        employees.sort(key=lambda e: (-len(e.programmes), e.employee_id))

        header_title = f"Employees in {department}" if department else "All Employees"
        self.display_header(header_title)

        for emp in employees:
            print(f"ID: {emp.employee_id}, Name: {emp.name}, Dept: {emp.department}, "
                  f"Programmes: {len(emp.programmes)}")

        input("\nPress Enter to continue...")

    def display_filter_by_department(self):
        """Display employees filtered by department, sorted by programmes and ID (merge sort)"""
        while True:
            self.display_header("FILTER BY DEPARTMENT - Merge Sort")

            # Get sorted unique departments from non-admin employees
            departments = sorted({emp.department for emp in self.employees if not emp.is_admin})

            print("\nAvailable Departments:")
            for i, dept in enumerate(departments, start=1):
                print(f"{i}. {dept}")
            print("0. Return to previous menu")

            try:
                choice = int(input("\nSelect department by number (0 to return): "))
            except ValueError:
                print(Fore.RED + "Invalid input, please enter a number." + Style.RESET_ALL)
                input("\nPress Enter to continue...")
                continue

            if choice == 0:
                break  # Exit to previous menu
            elif 1 <= choice <= len(departments):
                selected_dept = departments[choice - 1]

                # Filter employees by selected department and exclude admins
                filtered_emps = [emp for emp in self.employees if not emp.is_admin and emp.department == selected_dept]

                # Sort using your merge sort function
                sorted_emps = self.merge_sort_by_programmes(filtered_emps)

                self.display_header(f"Employees in Department: {selected_dept}")
                if not sorted_emps:
                    print(Fore.YELLOW + "No employees found in this department." + Style.RESET_ALL)
                else:
                    for emp in sorted_emps:
                        print(f"ID: {emp.employee_id}, Name: {emp.name}, "
                              f"Programmes: {len(emp.programmes)}")

                input("\nPress Enter to return to department selection...")

            else:
                print(Fore.RED + "Invalid selection! Please try again." + Style.RESET_ALL)
                input("\nPress Enter to continue...")



    def add_employee_request(self):
        try:
            # Check if current user is admin
            if self.current_user.is_admin:
                # Admin can input any employee ID
                while True:
                    try:
                        emp_id = int(self.get_input("Enter Employee ID: "))
                        # Validate employee exists
                        employee = next((emp for emp in self.employees if emp.employee_id == emp_id), None)
                        if not employee:
                            print(Fore.RED + "Employee ID not found!" + Style.RESET_ALL)
                            continue
                        break
                    except ValueError:
                        print(Fore.RED + "Invalid input! Employee ID must be a number." + Style.RESET_ALL)
            else:
                # Regular employee uses their own ID
                emp_id = self.current_user.employee_id
                employee = self.current_user

            # Display request type options
            print("\nRequest Types:")
            print("1. Logistics")
            print("2. Maintenance")
            print("3. Support")
            print("4. Technical")
            print("5. IT")
            print("6. Others")

            # Get valid request type choice
            while True:
                type_choice = self.get_input("Select Request Type (1-6): ")
                if type_choice in ['1', '2', '3', '4', '5', '6']:
                    break
                print(Fore.RED + "Invalid choice! Please select 1-6." + Style.RESET_ALL)

            # Map choice to request type string
            request_types = {
                '1': 'Logistics',
                '2': 'Maintenance',
                '3': 'Support',
                '4': 'Technical',
                '5': 'IT',
                '6': 'Others'
            }

            # Handle "Others" selection
            if type_choice == '6':
                req_type = self.get_input("Please specify the request type: ")
            else:
                req_type = request_types[type_choice]

            # Get priority level
            while True:
                try:
                    priority = int(self.get_input("Enter Priority Level (1-5, 1=highest): "))
                    if 1 <= priority <= 5:
                        break
                    print(Fore.RED + "Priority must be between 1-5!" + Style.RESET_ALL)
                except ValueError:
                    print(Fore.RED + "Please enter a number!" + Style.RESET_ALL)

            details = self.get_input("Enter Request Details: ")

            # Enhanced duplicate check with more details
            duplicate_requests = []
            for req in self.request_queue.requests:
                if (req.employee_id == emp_id and
                        req.request_type.lower() == req_type.lower() and
                        req.request_details.lower() == details.lower()):
                    duplicate_requests.append(req)

            if duplicate_requests:
                print(Fore.YELLOW + "\nSimilar existing requests found:" + Style.RESET_ALL)
                for i, req in enumerate(duplicate_requests, 1):
                    print(f"{i}. Priority: {req.priority_level}, Status: {req.status}, "
                          f"Date: {req.timestamp.strftime('%Y-%m-%d')}")

                confirm = self.get_input("\nA similar request already exists. Add anyway? (yes/no): ").lower()
                if confirm != 'yes' and confirm != 'y':
                    print(Fore.YELLOW + "Request not added." + Style.RESET_ALL)
                    return

            # Create and add the new request
            new_request = EmployeeRequest(emp_id, req_type, priority, details)
            self.request_queue.add_request(new_request)
            self._save_to_json()

            # Show success message with different info for admin vs regular user
            if self.current_user.is_admin:
                print(
                    Fore.GREEN + f"\nRequest added successfully for {employee.name} (ID: {emp_id})!" + Style.RESET_ALL)
            else:
                print(Fore.GREEN + "\nYour request has been added successfully!" + Style.RESET_ALL)

            print(f"Type: {req_type}, Priority: {priority}")
            print(f"Details: {details[:50]}..." if len(details) > 50 else f"Details: {details}")

        except Exception as e:
            print(Fore.RED + f"\nError adding request: {str(e)}" + Style.RESET_ALL)

    def view_request_statistics(self):
        while True:
            self.display_header("REQUEST STATISTICS")
            print(f"\nTotal Requests in Queue: {self.request_queue.get_stats()}")
            print(f"Total Processed Requests: {self.request_stats['total_processed']}")
            print(f"  - Approved: {self.request_stats['approved']}")
            print(f"  - Rejected: {self.request_stats['rejected']}")

            print("\n1. View by Type")
            print("2. View by Priority")
            print("3. View Detailed Statistics")
            print("0. Back to Main Menu")

            choice = self.get_input("\nEnter your choice: ")

            if choice == "1":
                self._display_requests_by_type()
            elif choice == "2":
                self._display_requests_by_priority()
            elif choice == "3":
                self.show_request_statistics_details()  # Now this method exists
            elif choice == "0":
                break
            else:
                print(Fore.RED + "Invalid choice! Please enter 0-3" + Style.RESET_ALL)

    def show_request_statistics_details(self):
        """Display comprehensive request statistics"""
        self.display_header("REQUEST PROCESSING STATISTICS")

        # Calculate percentages
        total = self.request_stats['total_processed']
        approved = self.request_stats['approved']
        rejected = self.request_stats['rejected']

        print(f"\n{'Total Processed:':<20}{total:>10}")
        print(f"{'Approved:':<20}{approved:>10} ({approved / total:.1%})")
        print(f"{'Rejected:':<20}{rejected:>10} ({rejected / total:.1%})")

        # By Request Type
        print("\n" + "=" * 50)
        print("BY REQUEST TYPE".center(50))
        print("=" * 50)
        print(f"\n{'Type':<15}{'Approved':>10}{'Rejected':>10}{'Total':>10}{'Rate':>10}")
        for req_type in sorted(self.request_stats['by_type'].keys()):
            stats = self.request_stats['by_type'][req_type]
            total_type = stats['approved'] + stats['rejected']
            if total_type > 0:
                rate = stats['approved'] / total_type
                print(f"{req_type:<15}{stats['approved']:>10}{stats['rejected']:>10}"
                      f"{total_type:>10}{rate:>10.1%}")

        # By Priority Level
        print("\n" + "=" * 50)
        print("BY PRIORITY LEVEL".center(50))
        print("=" * 50)
        print(f"\n{'Priority':<15}{'Approved':>10}{'Rejected':>10}{'Total':>10}{'Rate':>10}")
        for priority in sorted(self.request_stats['by_priority'].keys()):
            stats = self.request_stats['by_priority'][priority]
            total_priority = stats['approved'] + stats['rejected']
            if total_priority > 0:
                rate = stats['approved'] / total_priority
                print(f"{priority:<15}{stats['approved']:>10}{stats['rejected']:>10}"
                      f"{total_priority:>10}{rate:>10.1%}")

    def _load_processed_requests(self):
        """Load processed requests from file with silent error handling"""
        processed_requests = []

        if not os.path.exists(self.requests_file):
            return processed_requests

        try:
            with open(self.requests_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        # Split timestamp from rest of line
                        timestamp_end = line.find(': ')
                        if timestamp_end == -1:
                            continue

                        timestamp_str = line[:timestamp_end]
                        request_data = line[timestamp_end + 2:]  # skip ": "

                        # Parse timestamp
                        try:
                            timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S.%f")
                        except ValueError:
                            try:
                                timestamp = datetime.datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                            except ValueError:
                                continue

                        # Parse request data
                        if request_data.startswith("APPROVED: ") or request_data.startswith("REJECTED: "):
                            status, request_str = request_data.split(': ', 1)
                            request_str = request_str.strip()

                            try:
                                # Extract all fields
                                id_start = request_str.find("ID: ") + 4
                                id_end = request_str.find(",", id_start)
                                employee_id = int(request_str[id_start:id_end])

                                type_start = request_str.find("Type: ") + 6
                                type_end = request_str.find(",", type_start)
                                request_type = request_str[type_start:type_end].strip()

                                priority_start = request_str.find("Priority: ") + 10
                                priority_end = request_str.find(",", priority_start)
                                priority = int(request_str[priority_start:priority_end])

                                details_start = request_str.find("Details: ") + 9
                                time_label = ", Time:"
                                details_end = request_str.find(time_label, details_start)
                                details = request_str[details_start:details_end].strip()

                                request_time_str = request_str[details_end + len(time_label):].strip().rstrip(']')
                                try:
                                    request_time = datetime.datetime.strptime(request_time_str, "%Y-%m-%d %H:%M:%S.%f")
                                except ValueError:
                                    request_time = datetime.datetime.strptime(request_time_str, "%Y-%m-%d %H:%M:%S")

                                # Add valid request to results
                                processed_requests.append({
                                    'processed_time': timestamp,
                                    'status': status,
                                    'employee_id': employee_id,
                                    'request_type': request_type,
                                    'priority': priority,
                                    'details': details,
                                    'original_request_time': request_time,
                                    'raw_data': request_str
                                })

                            except (ValueError, IndexError):
                                continue

                    except Exception:
                        continue

        except Exception:
            pass

        return processed_requests
    def _update_request_stats(self, request, approved=None):
        if approved is None:
            approved = request.status.upper() == "APPROVED"

        self.request_stats['total_processed'] += 1
        if approved:
            self.request_stats['approved'] += 1
            self.request_stats['by_type'][request.request_type]['approved'] += 1
            self.request_stats['by_priority'][request.priority_level]['approved'] += 1
        else:
            self.request_stats['rejected'] += 1
            self.request_stats['by_type'][request.request_type]['rejected'] += 1
            self.request_stats['by_priority'][request.priority_level]['rejected'] += 1

    def _update_request_stats_from_dict(self, request):
        """Update stats for loaded requests (dict style)"""
        approved = request['status'].upper().startswith('APPROVED')
        self.request_stats['total_processed'] += 1
        if approved:
            self.request_stats['approved'] += 1
            self.request_stats['by_type'][request['request_type']]['approved'] += 1
            self.request_stats['by_priority'][request['priority']]['approved'] += 1
        else:
            self.request_stats['rejected'] += 1
            self.request_stats['by_type'][request['request_type']]['rejected'] += 1
            self.request_stats['by_priority'][request['priority']]['rejected'] += 1

    def _display_requests_by_type(self):
        types = sorted(set(req.request_type for req in self.request_queue.requests))
        if not types:
            print(Fore.YELLOW + "\nNo requests found!" + Style.RESET_ALL)
            return

        print(Fore.CYAN + "\n" + "=" * 50)
        print("REQUESTS BY TYPE".center(50))
        print("=" * 50 + Style.RESET_ALL)

        for i, t in enumerate(types, 1):
            count = self.request_queue.get_stats(filter_type=t)
            print(f"{i}. {t}: {count} requests")

        choice = self.get_input("\nEnter type number to view details (0 to go back): ")
        try:
            choice = int(choice)
            if choice == 0:
                return
            if 1 <= choice <= len(types):
                selected_type = types[choice - 1]
                requests = self.request_queue.filter_requests(filter_type=selected_type)
                self._display_request_list(requests, f"Requests of type: {selected_type}")
        except ValueError:
            print(Fore.RED + "Invalid input!" + Style.RESET_ALL)

    def _display_requests_by_priority(self):
        print(Fore.CYAN + "\n" + "=" * 50)
        print("REQUESTS BY PRIORITY".center(50))
        print("=" * 50 + Style.RESET_ALL)

        for p in range(1, 6):
            count = self.request_queue.get_stats(filter_priority=p)
            print(f"Priority {p}: {count} requests")

        choice = self.get_input("\nEnter priority level to view details (1-5, 0 to go back): ")
        try:
            choice = int(choice)
            if choice == 0:
                return
            if 1 <= choice <= 5:
                requests = self.request_queue.filter_requests(filter_priority=choice)
                self._display_request_list(requests, f"Priority {choice} Requests")
        except ValueError:
            print(Fore.RED + "Invalid input!" + Style.RESET_ALL)

    def _display_request_list(self, requests, title):
        if not requests:
            print(Fore.YELLOW + f"\nNo {title.lower()} found!" + Style.RESET_ALL)
            return

        print("\n" + "=" * 100)
        print(title.center(100))
        print("=" * 100)
        print(f"{'#':<5}{'Type':<15}{'Priority':<10}{'Employee ID':<12}{'Details':<40}{'Timestamp':<20}")
        print("=" * 100)

        # Sort requests by priority then timestamp
        sorted_requests = sorted(requests, key=lambda x: (x.priority_level, x.timestamp))

        for idx, req in enumerate(sorted_requests, 1):
            print(f"{idx:<5}{req.request_type:<15}{req.priority_level:<10}{req.employee_id:<12}"
                  f"{req.request_details[:37] + '...' if len(req.request_details) > 40 else req.request_details:<40}"
                  f"{req.timestamp.strftime('%Y-%m-%d %H:%M'):<20}")

        print("=" * 100)
        return sorted_requests  # Return the sorted list for processing

    # This method was incorrectly indented before
    def process_request(self):

        while True:

            print("1. Process next request (highest priority)")
            print("2. Process by request number")
            print("3. Process by type")
            print("0. Back to main menu")

            choice = self.get_input("\nEnter your choice: ")

            if choice == "1":
                self._process_next_request()
                break
            elif choice == "2":
                self._process_by_request_number()
                break
            elif choice == "3":
                self._process_by_type()

            elif choice == "0":
                break
            else:
                print(Fore.RED + "Invalid choice!" + Style.RESET_ALL)

    def _process_next_request(self):
        request = self.request_queue.process_next()
        if not request:
            print(Fore.RED + "No requests to process!" + Style.RESET_ALL)
            return
        self._handle_request_processing(request)

    def _process_by_type(self):
        types = sorted(set(req.request_type for req in self.request_queue.requests))
        if not types:
            print(Fore.YELLOW + "\nNo request types available!" + Style.RESET_ALL)
            return

        print("\nAvailable request types:")
        for i, req_type in enumerate(types, 1):
            print(f"{i}. {req_type}")

        try:
            choice = int(self.get_input("\nSelect request type to process (0 to cancel): "))
            if choice == 0:
                return
            if 1 <= choice <= len(types):
                selected_type = types[choice - 1]
                requests = self.request_queue.filter_requests(filter_type=selected_type)
                if requests:
                    self._display_request_list(requests, f"Requests of type: {selected_type}")
                    req_num = int(self.get_input("Enter request number to process (0 to cancel): "))
                    if 1 <= req_num <= len(requests):
                        request = requests[req_num - 1]
                        self.request_queue.requests.remove(request)
                        self._handle_request_processing(request)
                else:
                    print(Fore.YELLOW + f"\nNo {selected_type} requests found!" + Style.RESET_ALL)
        except ValueError:
            print(Fore.RED + "Invalid input!" + Style.RESET_ALL)

    def _process_by_request_number(self):
        all_requests = sorted(self.request_queue.requests, key=lambda x: (x.priority_level, x.timestamp))
        if not all_requests:
            print(Fore.RED + "No requests to process!" + Style.RESET_ALL)
            return

        print("\nAll Requests:")
        displayed_requests = self._display_request_list(all_requests, "All Requests")

        try:
            choice = int(self.get_input("\nEnter request number to process (0 to cancel): "))
            if choice == 0:
                return
            if 1 <= choice <= len(displayed_requests):
                request = displayed_requests[choice - 1]
                self.request_queue.requests.remove(request)
                self._handle_request_processing(request)
            else:
                print(Fore.RED + "Invalid request number!" + Style.RESET_ALL)
        except ValueError:
            print(Fore.RED + "Please enter a valid number!" + Style.RESET_ALL)

    def _handle_request_processing(self, request):
        """Process a request with proper logging and email notifications"""
        print(Fore.GREEN + "\nProcessing Request:" + Style.RESET_ALL)
        print(request)

        while True:
            try:
                action = int(input("\n1. Approve request\n2. Reject request\n3. Cancel\nChoose action (1-3): "))

                if action == 1:  # Approve
                    return self._approve_request(request)
                elif action == 2:  # Reject
                    return self._handle_request_rejection(request)
                elif action == 3:  # Cancel
                    print(Fore.YELLOW + "Processing cancelled. Request remains in queue." + Style.RESET_ALL)
                    return False
                else:
                    print(Fore.RED + "Please enter a number between 1-3!" + Style.RESET_ALL)

            except ValueError:
                print(Fore.RED + "Invalid input! Please enter a number." + Style.RESET_ALL)

    def _approve_request(self, request):
        """Handle request approval"""
        request.status = "APPROVED"
        request.processed_time = datetime.datetime.now()
        self._update_request_stats(request, approved=True)
        self._log_request(request, "APPROVED")

        # Send approval notification
        self._send_request_notification(
            request,
            "approved",
            "Your Request Has Been Approved",
            f"Your request has been approved.\n\nRequest Details:\n{request}\n\nThank you for your submission."
        )

        print(Fore.GREEN + "Request approved successfully!" + Style.RESET_ALL)
        return True

    def _handle_request_rejection(self, request):
        """Handle request rejection with reason selection"""
        rejection_reasons = {
            1: "Incomplete information provided",
            2: "Request not compliant with company policy",
            3: "Budget constraints",
            4: "Timing not appropriate",
            5: "Other (specify)"
        }

        print("\nSelect rejection reason:")
        for num, reason in rejection_reasons.items():
            print(f"{num}. {reason}")

        try:
            reason_choice = int(input("Enter reason number (1-5): "))
            if reason_choice not in rejection_reasons:
                raise ValueError("Invalid reason number")

            if reason_choice == 5:
                custom_reason = input("Enter custom reason: ").strip()
                if not custom_reason:
                    raise ValueError("Custom reason cannot be empty")
                rejection_reason = custom_reason
            else:
                rejection_reason = rejection_reasons[reason_choice]

            request.status = f"REJECTED: {rejection_reason}"
            request.processed_time = datetime.datetime.now()
            self._update_request_stats(request, approved=False)

            # Send rejection notification
            self._send_request_notification(
                request,
                "rejected",
                "Your Request Was Not Approved",
                f"Your request has been rejected.\n\nReason: {rejection_reason}\n\nRequest Details:\n{request}\n\nPlease contact HR if you have questions."
            )

            self._log_request(request, "REJECTED")
            return True

        except ValueError as e:
            error_msg = {
                "Invalid reason number": "Please enter a number between 1-5",
                "Custom reason cannot be empty": "You must provide a rejection reason"
            }.get(str(e), "Invalid input! Please enter a valid number")

            print(Fore.RED + f"\nError: {error_msg}" + Style.RESET_ALL)
            return False

    def _send_request_notification(self, request, action, subject, message_template):
        """Send email notification for request actions"""
        employee = next((emp for emp in self.employees if emp.employee_id == request.employee_id), None)
        if not employee:
            print(Fore.RED + "Employee not found - cannot send notification" + Style.RESET_ALL)
            return False

        message_body = f"Dear {employee.name},\n\n{message_template}\n\nRegards,\nManagement"

        if not self._send_email(employee.email, subject, message_body):
            print(Fore.YELLOW + f"Warning: {action} email could not be sent" + Style.RESET_ALL)
            return False
        return True

    def _send_email(self, recipient_email, subject, message_body):
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
        from google.auth.transport.requests import Request
        """Send email using Gmail API with proper authentication"""
        try:
            # Validate email format
            if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", recipient_email):
                print(Fore.RED + f"Invalid email format: {recipient_email}" + Style.RESET_ALL)
                return False

            # Set up Gmail API credentials
            creds = None
            if os.path.exists('token.json'):
                creds = Credentials.from_authorized_user_file('token.json', SCOPES)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists('credentials.json'):
                        print(Fore.RED + "Missing credentials.json! Cannot send email." + Style.RESET_ALL)
                        return False
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'credentials.json', SCOPES)
                    creds = flow.run_local_server(port=0)

                with open('token.json', 'w') as token:
                    token.write(creds.to_json())

            # Create and send email
            service = build('gmail', 'v1', credentials=creds)
            message = MIMEText(message_body)
            message['to'] = recipient_email
            message['subject'] = subject

            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            raw_message = {'raw': encoded_message}

            try:
                sent_message = service.users().messages().send(
                    userId="me",
                    body=raw_message
                ).execute()

                print(
                    Fore.GREEN + f"Email sent to {recipient_email} (Message ID: {sent_message['id']})" + Style.RESET_ALL)
                return True

            except Exception as send_error:
                print(Fore.RED + f"Failed to send email: {str(send_error)}" + Style.RESET_ALL)
                return False

        except Exception as e:
            print(Fore.RED + f"Error in email setup: {str(e)}" + Style.RESET_ALL)
            return False

    def load_all_requests(self):
        try:
            self._load_employees_from_json()  # sets self.employees and self.requests (pending)
            self.processed_requests = self._load_processed_requests()  # from log file
        except Exception:
            pass

    def simple_decrypt(encrypted_str):
        # Replace with real decryption logic
        return encrypted_str[::-1]  # Example: reverse string

    def _load_employees_from_json(self):
        try:
            with open("employees.json", "r") as f:
                employee_data = json.load(f)
            self.employees = employee_data.get("employees", [])
            self.requests = employee_data.get("requests", [])

            # Decrypt programmes immediately for all employees
            for emp in self.employees:
                programmes = emp.get("programmes", [])
                if isinstance(programmes, list):
                    decrypted_programmes = []
                    for p in programmes:
                        if isinstance(p, str) and p.startswith("enc:"):
                            try:
                                decrypted = simple_decrypt(p[4:])
                                decrypted_programmes.append(decrypted)
                            except Exception:
                                decrypted_programmes.append("[DECRYPTION ERROR]")
                        else:
                            decrypted_programmes.append(p)
                    emp["programmes"] = decrypted_programmes  # overwrite with decrypted

        except Exception as e:
            print(f"Error loading or decrypting employee data: {e}")
            self.employees = []
            self.requests = []

    def loading_animation(self, message="Loading"):
        """Show a loading animation with a custom message"""
        import itertools
        import sys
        import time

        spinner = itertools.cycle(['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'])
        for i in range(3):  # Run for 3 full cycles
            for _ in range(10):  # Each cycle has 10 spinner frames
                char = next(spinner)
                sys.stdout.write(f'\r{message} {char}')
                sys.stdout.flush()
                time.sleep(0.1)
        sys.stdout.write('\r' + ' ' * (len(message) + 4) + '\r')  # Clear the line
    def _generate_dashboard_pdf(self, filename="dashboard_report.pdf"):
        """Generate PDF dashboard report with employee statistics and charts"""

        # Show loading animation before starting
        self.loading_animation("Preparing report")

        try:
            # Import required libraries
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            from io import BytesIO
            import pandas as pd
            from reportlab.lib.pagesizes import landscape, letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
            from reportlab.lib.styles import getSampleStyleSheet
            from collections import Counter
            import datetime
            import os
            from matplotlib import rcParams

            # Set font to handle special characters
            rcParams['font.family'] = 'DejaVu Sans'
            rcParams['font.sans-serif'] = ['DejaVu Sans']

            # Load data with loading animation
            self.loading_animation("Loading employee data")
            try:
                with open("employees.json", 'r') as f:
                    data = json.load(f)
                employees = data.get("employees", [])
                requests = data.get("requests", [])
                processed_requests = self._load_processed_requests()
            except Exception as e:
                print(f"\nError loading data: {str(e)}")
                return False

            # Prepare data with ASCII-only cleaning
            def clean_text(text):
                if not isinstance(text, str):
                    return str(text)
                return text.encode('ascii', 'ignore').decode('ascii')

            # Process employee data with loading feedback
            print("\nProcessing employee records...")
            non_admins = [e for e in employees if isinstance(e, dict) and not e.get("is_admin", False)]
            df_data = []

            for i, e in enumerate(non_admins):
                # Show progress every 10 records
                if i % 10 == 0:
                    sys.stdout.write(f'\rProcessing record')
                    sys.stdout.flush()

                try:
                    # Decrypt and clean programs
                    programmes = []
                    for p in e.get("programmes", []):
                        if isinstance(p, str) and p.startswith('enc:'):
                            try:
                                decrypted = simple_decrypt(p[4:])
                                programmes.append(clean_text(decrypted))
                            except:
                                programmes.append("[DECRYPTION ERROR]")
                        else:
                            programmes.append(clean_text(p))

                    df_data.append({
                        "name": clean_text(e.get("name", "")),
                        "is_full_time": bool(e.get("is_full_time", False)),
                        "programmes": programmes,
                        "department": clean_text(e.get("department", ""))
                    })
                except Exception as e:
                    continue

            if not df_data:
                print("\nNo valid employee data found")
                return False

            df = pd.DataFrame(df_data)
            print("\nData processing complete")

            # Calculate statistics with loading animation
            self.loading_animation("Calculating statistics")
            total_employees = len(df)
            full_time_count = df["is_full_time"].sum()
            part_time_count = total_employees - full_time_count

            # Get most common programme
            all_programmes = [p for sublist in df["programmes"] for p in sublist if isinstance(p, str)]
            programme_counts = Counter(all_programmes)
            most_common_programme = programme_counts.most_common(1)[0][0] if programme_counts else "N/A"

            # Request statistics
            pending_requests = len([r for r in requests if isinstance(r, dict)])
            done_count = len([r for r in processed_requests if isinstance(r, dict)])
            pending_by_priority = Counter(r.get("priority_level", 0) for r in requests if isinstance(r, dict))

            # Department statistics
            departments = [d for d in df["department"] if isinstance(d, str)]
            unique_departments = len(set(departments))

            # Create PDF document
            self.loading_animation("Initializing PDF")
            try:
                doc = SimpleDocTemplate(filename, pagesize=landscape(letter))
            except Exception as e:
                print(f"\nError creating PDF document: {str(e)}")
                return False

            styles = getSampleStyleSheet()
            story = []

            # Add header
            story.append(Paragraph("Employee Management Dashboard", styles['Title']))
            story.append(Spacer(1, 12))

            # Add summary statistics
            stats = [
                f"Total Employees: {total_employees}",
                f"Full-time: {full_time_count} | Part-time: {part_time_count}",
                f"Most Common Programme: {most_common_programme}",
                f"Pending Requests: {pending_requests}",
                f"Processed Requests: {done_count}",
                f"Total Departments: {unique_departments}",
                f"Report Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
            ]

            for stat in stats:
                story.append(Paragraph(stat, styles['Normal']))
                story.append(Spacer(1, 6))

            story.append(Spacer(1, 24))

            # Generate charts with progress feedback
            print("\nGenerating charts:")

            # Chart 1: Employment Type Breakdown
            print("- Employment distribution chart")
            try:
                fig1, ax1 = plt.subplots()
                ax1.bar(['Full-Time', 'Part-Time'], [full_time_count, part_time_count],
                        color=['#4CAF50', '#FFC107'])
                ax1.set_title("Employment Type Distribution")
                img1 = BytesIO()
                plt.tight_layout()
                fig1.savefig(img1, format='png', dpi=100)
                plt.close(fig1)
                img1.seek(0)
                story.append(Image(img1, width=400, height=250))
                story.append(Spacer(1, 12))
            except Exception as e:
                print(f"Error creating employment chart: {str(e)}")

            # Chart 2: Requests by Priority
            print("- Request status chart")
            try:
                labels = [f"Priority {k}" for k in sorted(pending_by_priority.keys())]
                sizes = [pending_by_priority[k] for k in sorted(pending_by_priority.keys())]

                if done_count > 0:
                    labels.append("Processed")
                    sizes.append(done_count)

                fig2, ax2 = plt.subplots()
                ax2.pie(sizes, labels=labels, autopct='%1.1f%%',
                        colors=plt.cm.tab20.colors[:len(labels)])
                ax2.set_title("Request Status")
                img2 = BytesIO()
                plt.tight_layout()
                fig2.savefig(img2, format='png', dpi=100)
                plt.close(fig2)
                img2.seek(0)
                story.append(Image(img2, width=400, height=250))
                story.append(Spacer(1, 12))
            except Exception as e:
                print(f"Error creating requests chart: {str(e)}")

            # Chart 3: Programme Popularity
            if programme_counts and len(programme_counts) > 0:
                print("- Programme popularity chart")
                try:
                    top_programmes = programme_counts.most_common(5)
                    top_programmes = [(clean_text(name), count) for name, count in top_programmes]

                    fig3, ax3 = plt.subplots(figsize=(8, 4))
                    ax3.bar([p[0] for p in top_programmes], [p[1] for p in top_programmes],
                            color=plt.cm.tab20.colors[:5])
                    ax3.set_title("Top 5 Programmes")
                    ax3.set_ylabel("Enrollments")
                    plt.xticks(rotation=45, ha='right')
                    img3 = BytesIO()
                    plt.tight_layout()
                    fig3.savefig(img3, format='png', dpi=100)
                    plt.close(fig3)
                    img3.seek(0)
                    story.append(Image(img3, width=500, height=300))
                except Exception as e:
                    print(f"Error creating programmes chart: {str(e)}")

            # Build PDF with loading animation
            self.loading_animation("Generating final PDF")
            try:
                doc.build(story)
                print(f"\nPDF successfully generated: {os.path.abspath(filename)}")
                return True
            except Exception as e:
                print(f"\nError building PDF: {str(e)}")
                return False

        except Exception as e:
            print(f"\nUnexpected error in PDF generation: {str(e)}")
            return False

    def dashboard_summary(self):
        """Display comprehensive dashboard summary and handle PDF generation"""
        try:
            # Load data with error handling
            try:
                with open("employees.json", 'r') as f:
                    data = json.load(f)
                employees = data.get("employees", [])
                requests = data.get("requests", [])
                processed_requests = self._load_processed_requests()
            except Exception as e:
                print(Fore.RED + f"\nError loading data: {str(e)}" + Style.RESET_ALL)
                return

            # Filter out admins and invalid entries
            non_admins = [e for e in employees if isinstance(e, dict) and not e.get("is_admin", False)]
            total_employees = len(non_admins)

            if not non_admins:
                print(Fore.YELLOW + "\nNo employee data found" + Style.RESET_ALL)
                return

            # Employment statistics
            full_time_count = sum(1 for e in non_admins if e.get("is_full_time", False))
            part_time_count = total_employees - full_time_count

            from collections import Counter

            # Programme statistics - decrypted correctly
            all_programmes = []

            for e in non_admins:
                programmes = e.get("programmes", [])
                if isinstance(programmes, list):
                    for p in programmes:
                        if isinstance(p, str):
                            if p.startswith("enc:"):
                                try:
                                    decrypted = simple_decrypt(p[4:])
                                    all_programmes.append(decrypted)
                                except Exception as err:
                                    all_programmes.append("[DECRYPTION ERROR]")
                            else:
                                all_programmes.append(p)

            # Count only valid decrypted programmes
            valid_programmes = [p for p in all_programmes if p and p != "[DECRYPTION ERROR]"]
            programme_counts = Counter(valid_programmes)
            most_common = programme_counts.most_common(1)

            most_common_programme = most_common[0][0] if most_common else "N/A"
            programme_count = most_common[0][1] if most_common else 0

            # Request statistics
            pending_requests = len([r for r in requests if isinstance(r, dict)])
            done_count = len([r for r in processed_requests if isinstance(r, dict)])

            # Department statistics
            departments = {e.get("department", "Unknown") for e in non_admins}
            dept_count = len(departments)

            # Display dashboard
            self.display_header("DASHBOARD SUMMARY")
            print(f"\n{'Employee Statistics:':<30}")
            print(f"{'  Total Employees:':<25}{total_employees:>10}")
            print(f"{'  Full-time:':<25}{full_time_count:>10}")
            print(f"{'  Part-time:':<25}{part_time_count:>10}")
            print(f"\n{'Programme Statistics:':<30}")
            print(f"{'  Most Common:':<25}{most_common_programme + ' (' + str(programme_count) + ')':>10}")
            print(f"\n{'Request Statistics:':<30}")
            print(f"{'  Pending:':<25}{pending_requests:>10}")
            print(f"{'  Processed:':<25}{done_count:>10}")
            print(f"\n{'Department Statistics:':<30}")
            print(f"{'  Total Departments:':<25}{dept_count:>10}")

            # PDF generation option
            choice = self.get_input("\nGenerate PDF report? (y/n): ").lower()
            if choice == 'y':
                if self._generate_dashboard_pdf():
                    print(Fore.GREEN + "\nPDF report generated successfully!" + Style.RESET_ALL)
                else:
                    print(Fore.RED + "\nFailed to generate PDF report" + Style.RESET_ALL)

        except Exception as e:
            print(Fore.RED + f"\nError in dashboard summary: {str(e)}" + Style.RESET_ALL)


if __name__ == "__main__":
    system = EmployeeManagementSystem()
    while True:
        if system.login():
            break
        print(Fore.RED + "Login failed. Please try again." + Style.RESET_ALL)

    # Main menu loop (only after successful login)
    while True:
        system.display_menu()
        choice = system.get_input("Enter your choice (0-7): ")

        if choice == "1":
            # Quick Sort - Department and Name
            while True:
                system.display_header("EMPLOYEES SORTED BY DEPARTMENT AND NAME")

                # Display all sorted employees with department grouping
                system.display_quick_sorted_employees()

                print("\n1. Refresh view")
                print("0. Return to main menu")
                sub_choice = system.get_input("Enter choice: ")
                if sub_choice == "0":
                    break
                    # In the main menu loop (__main__ section):
        elif choice == "2":

            while True:
                system.display_header("EMPLOYEES SORTED BY PROGRAMMES AND ID")
                print("\n1. Filter by department")
                print("2. Show all employees")
                print("0. Return to main menu")

                sub_choice = system.get_input("Enter choice: ")

                if sub_choice == "1":
                    system.display_filter_by_department()  # This will handle department selection
                elif sub_choice == "2":
                    system.display_merge_sorted_employees()  # Show all non-admin employees
                elif sub_choice == "0":
                    break  # This will return to main menu
                else:
                            print(Fore.RED + "Invalid choice!" + Style.RESET_ALL)
        elif choice == "3":
            # Add requests loop
            while True:
                system.display_header("ADD EMPLOYEE REQUEST")
                system.add_employee_request()
                print("\n1. Add another request")
                print("0. Return to main menu")
                sub_choice = system.get_input("Enter choice: ")
                if sub_choice == "0":
                    break

        elif choice == "4":
            # View stats loop
            while True:
                system.view_request_statistics()
                print("\n1. Refresh statistics")
                print("0. Return to main menu")
                sub_choice = system.get_input("Enter choice: ")
                if sub_choice == "0":
                    break

        elif choice == "5":
            while True:
                system.display_header("PROCESS NEXT REQUEST")
                system.process_request()
                print("\n1. Process next request")
                print("0. Return to main menu")
                sub_choice = system.get_input("Enter choice: ")
                if sub_choice == "0":
                    break
        # In the main menu loop (__main__ section):
        elif choice == "6":  # For admin menu
            system.show_undo_redo_menu()

        elif choice == "7":
            # Dashboard loop
            while True:
                system.dashboard_summary()
                print("\n1. Refresh dashboard")
                print("0. Return to main menu")
                sub_choice = system.get_input("Enter choice: ")
                if sub_choice == "0":
                    break

        elif choice == "8":
            # Tree view loop
            while True:
                system.display_header("DEPARTMENT TREE VIEW")
                system.tree.display_tree()
                print("\n1. Refresh tree view")
                print("0. Return to main menu")
                sub_choice = system.get_input("Enter choice: ")
                if sub_choice == "0":
                    break

        elif choice == "9":
            system.generate_dummy_requests()
            print(Fore.GREEN + "Dummy requests generated successfully!" + Style.RESET_ALL)

        elif choice == "0":
            system._save_to_json()
            print(Fore.GREEN + "\nLogging out... Goodbye!")
            break

        else:
            print(Fore.RED + "\nInvalid choice! Please try again." + Style.RESET_ALL)
