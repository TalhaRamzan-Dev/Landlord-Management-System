# Property Management System

## Overview
The Property Management System is a comprehensive software solution developed using Python and Tkinter, designed to manage rental properties, tenants, leases, payments, expenses, and maintenance requests. It provides a modular, scalable, and user-friendly platform for landlords to streamline property management tasks with robust data handling and reporting capabilities.

## Features

### Authentication
- **Admin Login**: Secure single-user login with password hashing using SHA-256.
- **Session Management**: Persistent login sessions until manual logout.
- **First-time Setup**: Simplified admin account creation process.

### Property Management
- **Property Operations**: Add, edit, or delete property records with comprehensive details.
- **Property Details**: Track rent, deposit, size, number of bedrooms, bathrooms, and status.
- **Property Status**: Options include Vacant, Occupied, or Under Maintenance.
- **Property Types**: Supports Apartment, House, Shop, Office, and Other.
- **Filtering**: Filter properties by status and access detailed information.

### Tenant Management
- **Tenant Operations**: Add, edit, or remove tenant records.
- **Tenant Details**: Store name, phone, email, national ID, and emergency contact information.
- **Property Association**: Link tenants to specific properties.
- **Filtering**: Filter tenants by associated property.
- **Emergency Contacts**: Manage and access emergency contact details.

### Lease Management
- **Lease Operations**: Create, edit, or terminate lease agreements.
- **Lease Details**: Record start date, end date, rent amount, and deposit.
- **Lease Status**: Track as Active, Terminated, or Expired.
- **Lease History**: Maintain historical lease data for properties and tenants.
- **Filtering**: Filter leases by status and view detailed information.

### Rent Payment Tracking
- **Payment Recording**: Log payments via cash, bank transfer, cheque, or online methods.
- **Automated Rent Generation**: Automatically generate monthly rent due records.
- **Payment Status**: Monitor Paid, Pending, Overdue, or Partial statuses.
- **Payment History**: View payment history by lease, tenant, or property.
- **Payment Methods**: Support for multiple payment methods.
- **Income Reports**: Generate monthly income reports for financial analysis.

### Expense Management
- **Expense Logging**: Track maintenance, tax, utility, and repair costs.
- **Expense Categories**: Includes Maintenance, Utility, Repair, Tax, and Other.
- **Property Association**: Associate expenses with specific properties.
- **Filtering**: Filter expenses by property or category.
- **Invoice Tracking**: Store invoice numbers and receipts.
- **Cost Analysis**: Analyze total expenses per property.

### Document Management
- **Document Upload**: Store contracts, tenant IDs, payment proofs, and other documents.
- **Document Types**: Supports Property, Tenant, Lease, Payment, and Expense documents.
- **File Organization**: Automatic naming and organization of files.
- **Search Functionality**: Search and filter documents by property, tenant, or lease.
- **File Access**: Direct access and management of stored documents.

### Maintenance Request System
- **Request Creation**: Create maintenance requests initiated by tenants or landlords.
- **Status Tracking**: Monitor requests through Open, In Progress, and Completed stages.
- **Cost Management**: Track estimated and actual maintenance costs.
- **Completion Tracking**: Record completion dates and notes.
- **Filtering**: Filter requests by property or status.
- **Maintenance Log**: Maintain a complete maintenance history per property.

### Reports and Dashboard
- **Occupancy Summary**: Track property occupancy rates and statuses.
- **Financial Analysis**: Compare rent income against expenses per property.
- **Overdue Alerts**: Identify and monitor overdue rent payments.
- **Lease Expiration Reports**: Track upcoming lease expirations.
- **Maintenance Cost Analysis**: Analyze maintenance-related expenses.
- **Financial Summary**: Generate comprehensive financial reports.
- **Data Export**: Export data to CSV files for external analysis.
- **Recent Activity**: View recent payments and maintenance activities on the dashboard.

## Installation and Setup

### Prerequisites
- Python 3.7 or higher
- Tkinter (included with standard Python installations)

### Installation Steps
1. Clone or download the project repository to your local machine.
2. Navigate to the project directory:
3. Install dependencies (if applicable):
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python main.py
   ```
5. Complete the first-time setup:
   - Select "Setup Admin" on the login screen.
   - Enter a username and password to create an admin account.
   - Use these credentials to log in.

### Testing
The project includes a comprehensive test suite using pytest:
```bash
# Run all tests
python run_tests.py

# Run a specific test file
python run_tests.py test_main.py

# Run tests with coverage report
pytest tests/ --cov=. --cov-report=html
```

**Test Coverage Includes:**
- Authentication system
- Property management
- Tenant management
- Lease management
- Payment tracking
- Expense management
- Document management
- Maintenance requests
- Database operations
- Utility functions
- UI components

## Database
The system uses an SQLite database (`landlord.db`) with the following tables:
- **admin**: Stores admin user accounts.
- **properties**: Stores property information.
- **tenants**: Stores tenant information.
- **leases**: Stores lease agreements.
- **rent_payments**: Stores rent payment records.
- **expenses**: Stores expense records.
- **documents**: Stores document metadata.
- **maintenance_requests**: Stores maintenance request records.

## File Structure
```
Final-Project/
├── main.py                 # Application entry point with UI
├── db.py                   # Database initialization
├── schema.sql              # Database schema definition
├── property_manager.py     # Property management module
├── tenant_manager.py       # Tenant management module
├── lease_manager.py        # Lease management module
├── payment_manager.py      # Payment tracking module
├── expense_manager.py      # Expense management module
├── document_manager.py     # Document management module
├── maintenance_manager.py  # Maintenance request module
├── reports_manager.py      # Reports and analytics module
├── requirements.txt        # Python dependencies
├── pytest.ini              # Pytest configuration
├── run_tests.py            # Test runner script
├── conftest.py             # Test fixtures and configuration
├── test_main.py            # Main application tests
├── test_property_manager.py
├── test_tenant_manager.py
├── test_payment_manager.py
├── test_database.py        # Database operation tests
├── test_utils.py           # Utility function tests
├── landlord.db             # SQLite database (created automatically)
├── documents/              # Document storage directory (created automatically)
└── README.md               # Project documentation
```

## Usage Guide

### Getting Started
1. **Login**: Access the system using admin credentials.
2. **Dashboard**: Review summary information and recent activity.
3. **Add Properties**: Input rental property details.
4. **Add Tenants**: Enter tenant information and associate with properties.
5. **Create Leases**: Establish lease agreements linking tenants and properties.
6. **Track Payments**: Record rent payments and generate monthly rent due records.
7. **Manage Expenses**: Log property-related expenses.
8. **Handle Maintenance**: Create and track maintenance requests.
9. **Upload Documents**: Store relevant documents and contracts.
10. **Generate Reports**: Use the reports section for financial and operational analysis.

### Key Feature Usage
- **Property Management**: Add and update property details, including status and tenant associations.
- **Tenant Management**: Manage tenant records, including emergency contacts and lease history.
- **Lease Management**: Create and track lease agreements, including status and termination.
- **Payment Tracking**: Record and monitor rent payments with automated monthly generation.
- **Expense Management**: Categorize and track expenses with property associations.
- **Maintenance Requests**: Manage maintenance workflows, costs, and completion details.
- **Document Management**: Organize and access documents related to properties, tenants, and leases.
- **Reports and Analytics**: Generate and export financial, occupancy, and maintenance reports.

## Security Features
- **Password Hashing**: Admin passwords are hashed using SHA-256.
- **Session Management**: Secure login and logout functionality.
- **Data Validation**: Input validation for all forms to ensure data integrity.
- **Error Handling**: Robust error handling across the application.

## Technical Details
- **GUI Framework**: Tkinter, designed for cross-platform compatibility.
- **Database**: SQLite with a comprehensive schema for reliable data storage.
- **File Management**: Automated organization and storage of documents.
- **Data Export**: CSV export functionality for data portability.
- **Testing**: Pytest test suite with over 80% code coverage.
- **Architecture**: Modular design with separate modules for each feature.

## User Interface
The system features a vintage-inspired interface with:
- A retro color scheme (red, orange, green, gold).
- Classic monospace font (Courier) for an authentic aesthetic.
- 3D-style raised buttons for intuitive navigation.
- Traditional desktop application layout for ease of use.

## Support
For assistance or inquiries, refer to the code comments and documentation within each module. Additional support resources may be added in future updates.

## License
This project was developed as part of the CS50 Python course final project and is intended for educational purposes.

---
