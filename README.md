# 🏠 Property Management System

## Overview
A **Python + Tkinter desktop application** for managing rental properties, tenants, leases, payments, expenses, and maintenance.  
Built with a **modular architecture, SQLite backend, and robust data handling**, this system helps landlords streamline property management and generate financial reports with ease.

---

## 🚀 Features
- **Authentication & Security**  
  - Admin login with SHA-256 password hashing  
  - Session management & input validation  

- **Property & Tenant Management**  
  - Add, edit, delete, and link tenants to properties  
  - Track property details (rent, status, size, type, etc.)  

- **Lease & Rent Tracking**  
  - Create and manage lease agreements  
  - Automated rent due generation  
  - Payment history and overdue alerts  

- **Expense & Document Management**  
  - Log maintenance, tax, utilities, and repairs  
  - Upload & organize contracts, invoices, and tenant IDs  

- **Maintenance Requests**  
  - Track requests with cost estimates and status updates  

- **Reports & Dashboard**  
  - Occupancy summaries, financial analysis, lease expirations  
  - Export reports to CSV for external use  

---

## 🛠️ Installation
### Prerequisites
- Python 3.7+
- Tkinter (bundled with Python)

### Setup
```bash
# Clone repository
git clone https://github.com/username/property-management-system.git
cd property-management-system

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py

First-time setup will prompt you to create an admin account.


📊 Database Schema

SQLite database (landlord.db) with normalized tables:

admin — authentication

properties, tenants, leases

rent_payments, expenses

documents, maintenance_requests


✅ Testing

Includes pytest-based test suite covering authentication, CRUD operations, database integrity, and UI components.

# Run all tests
pytest

# With coverage report
pytest --cov=. --cov-report=html



📂 Project Structure

Final-Project/
├── main.py              # Application entry point (UI)
├── db.py                # Database initialization
├── schema.sql           # Schema definition
├── managers/            # Feature modules (property, tenant, lease, etc.)
├── tests/               # Pytest test suite
├── documents/           # Uploaded documents
└── requirements.txt     # Dependencies


---

🎨 User Interface

Classic desktop-style Tkinter UI

Retro theme (red/orange/green) with Courier font

Intuitive menus & raised buttons



🔒 Security

SHA-256 password hashing

Robust input validation

Error handling across modules



📜 License

Developed as part of the CS50 Python Final Project.
Intended for educational purposes.