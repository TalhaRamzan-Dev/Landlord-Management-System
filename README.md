
# Property Management System

A user-friendly Python application built with Tkinter to manage rental properties, tenants, leases, payments, expenses, and maintenance requests. Designed for landlords to streamline operations with robust data handling and reporting.

## Features

- **Authentication**: Secure admin login with password hashing and session management.
- **Property Management**: Add, edit, or delete properties with details like rent, size, and status (Vacant, Occupied, Under Maintenance).
- **Tenant Management**: Manage tenant records, including contact details and property assignments.
- **Lease Management**: Create, track, and terminate lease agreements with status tracking (Active, Expired, Terminated).
- **Rent Payments**: Record payments (cash, bank, etc.), auto-generate monthly rent, and monitor payment status.
- **Expenses**: Log and categorize expenses (e.g., maintenance, taxes) with property associations.
- **Documents**: Upload and organize contracts, IDs, and receipts with search functionality.
- **Maintenance Requests**: Track requests from creation to completion, including costs and status.
- **Reports & Dashboard**: View occupancy, financial summaries, overdue payments, and export data to CSV.

## Installation

### Prerequisites
- Python 3.7+
- Tkinter (included with Python)

### Steps
1. Clone the repository:
   ```bash
   git clone <repository-url>
   ```
2. Navigate to the project directory:
   ```bash
   cd property-management-system
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python main.py
   ```
5. Follow the on-screen setup to create an admin account.

## Usage

1. **Log In**: Use admin credentials to access the system.
2. **Dashboard**: View recent activity and key metrics.
3. **Manage Data**:
   - Add/edit properties, tenants, and leases.
   - Record payments and expenses.
   - Upload documents and track maintenance requests.
4. **Generate Reports**: Analyze occupancy, finances, and maintenance via the reports section.

## Technical Details

- **GUI**: Tkinter with a retro-inspired interface (monospace font, classic color scheme).
- **Database**: SQLite (`landlord.db`) for storing properties, tenants, leases, and more.
- **Testing**: Pytest suite with >80% code coverage.
- **File Structure**:
  ```
  ├── main.py              # Application entry point
  ├── db.py                # Database setup
  ├── modules/             # Feature-specific modules
  ├── tests/               # Test suite
  ├── documents/           # Document storage
  └── landlord.db          # SQLite database
  ```

## Support

Refer to code comments for details. For issues, submit a bug report or feature request via the repository.

## License

Developed for the CS50 Python course. For educational use only. Contact the maintainers for commercial use inquiries.
