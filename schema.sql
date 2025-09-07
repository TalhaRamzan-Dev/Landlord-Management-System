
-- Table: Admin
CREATE TABLE admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table: Properties
CREATE TABLE properties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    address TEXT NOT NULL,
    type TEXT CHECK (type IN ('Apartment','House','Shop','Office','Other')),
    size REAL,
    bedrooms INTEGER,
    bathrooms INTEGER,
    furnished BOOLEAN DEFAULT 0,
    rent_amount REAL NOT NULL,
    deposit_amount REAL DEFAULT 0,
    status TEXT DEFAULT 'Vacant' CHECK (status IN ('Vacant','Occupied','Under Maintenance')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table: Tenants
CREATE TABLE tenants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER,
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    national_id TEXT UNIQUE,
    emergency_contact TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE SET NULL
);

-- Table: Leases
CREATE TABLE leases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id INTEGER NOT NULL,
    property_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    rent_amount REAL NOT NULL,
    deposit_amount REAL,
    status TEXT DEFAULT 'Active' CHECK (status IN ('Active','Terminated','Expired')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
);

-- Table: Rent Payments
CREATE TABLE rent_payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lease_id INTEGER NOT NULL,
    tenant_id INTEGER NOT NULL,
    property_id INTEGER NOT NULL,
    month TEXT NOT NULL,
    due_date DATE NOT NULL,
    amount_due REAL NOT NULL,
    amount_paid REAL DEFAULT 0,
    status TEXT DEFAULT 'Pending' CHECK (status IN ('Pending','Paid','Partial','Overdue')),
    payment_date DATE,
    payment_method TEXT CHECK (payment_method IN ('Cash','Bank Transfer','Cheque','Online','Other')),
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lease_id) REFERENCES leases(id) ON DELETE CASCADE,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
);

-- Table: Expenses
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    category TEXT CHECK (category IN ('Maintenance','Utility','Repair','Tax','Other')),
    amount REAL NOT NULL,
    date DATE DEFAULT (DATE('now')),
    paid_by TEXT DEFAULT 'Landlord',
    invoice_number TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
);

-- Table: Documents
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    related_type TEXT NOT NULL CHECK (related_type IN ('Property','Tenant','Lease','Payment','Expense')),
    related_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    description TEXT,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Table: Maintenance Requests
CREATE TABLE maintenance_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    property_id INTEGER NOT NULL,
    tenant_id INTEGER,
    request_date DATE DEFAULT (DATE('now')),
    description TEXT NOT NULL,
    status TEXT DEFAULT 'Open' CHECK (status IN ('Open','In Progress','Completed','Cancelled')),
    cost_estimate REAL,
    actual_cost REAL,
    completed_date DATE,
    notes TEXT,
    FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE SET NULL
);