import pytest
import sqlite3
import os
import tempfile
import shutil
from unittest.mock import Mock, patch
import tkinter as tk

@pytest.fixture
def temp_db():
    """Create a temporary database for testing"""
    # Create a temporary database file
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_landlord.db")
    
    # Initialize the database with schema
    with sqlite3.connect(db_path) as conn:
        with open("schema.sql", 'r') as f:
            conn.executescript(f.read())
    
    yield db_path
    
    # Cleanup
    try:
        if os.path.exists(db_path):
            os.remove(db_path)
        shutil.rmtree(temp_dir)
    except (PermissionError, OSError):
        pass

@pytest.fixture
def mock_db_connection(temp_db):
    """Mock database connection for testing"""
    with patch('db.DB_FILE', temp_db):
        yield temp_db

@pytest.fixture
def sample_property_data():
    """Sample property data for testing"""
    return {
        'name': 'Test Property',
        'address': '123 Test Street',
        'type': 'Apartment',
        'size': 1000.0,
        'bedrooms': 2,
        'bathrooms': 1,
        'furnished': True,
        'rent_amount': 1200.0,
        'deposit_amount': 1200.0,
        'status': 'Vacant'
    }

@pytest.fixture
def sample_tenant_data():
    """Sample tenant data for testing"""
    return {
        'name': 'John Doe',
        'phone': '555-1234',
        'email': 'john@example.com',
        'national_id': '123456789',
        'emergency_contact': 'Jane Doe - 555-5678',
        'notes': 'Test tenant'
    }

@pytest.fixture
def sample_lease_data():
    """Sample lease data for testing"""
    return {
        'start_date': '2024-01-01',
        'end_date': '2024-12-31',
        'rent_amount': 1200.0,
        'deposit_amount': 1200.0,
        'status': 'Active'
    }

@pytest.fixture
def sample_payment_data():
    """Sample payment data for testing"""
    return {
        'month': '2024-01',
        'due_date': '2024-02-01',
        'amount_due': 1200.0,
        'amount_paid': 1200.0,
        'status': 'Paid',
        'payment_date': '2024-01-15',
        'payment_method': 'Bank Transfer',
        'notes': 'Test payment'
    }

@pytest.fixture
def mock_tkinter():
    """Mock tkinter for testing"""
    with patch('tkinter.Tk') as mock_tk, \
         patch('tkinter.Frame') as mock_frame, \
         patch('tkinter.Label') as mock_label, \
         patch('tkinter.Button') as mock_button, \
         patch('tkinter.Entry') as mock_entry, \
         patch('tkinter.Text') as mock_text, \
         patch('tkinter.Toplevel') as mock_toplevel, \
         patch('tkinter.messagebox') as mock_msgbox, \
         patch('tkinter.ttk.Treeview') as mock_treeview, \
         patch('tkinter.ttk.Combobox') as mock_combobox, \
         patch('tkinter.ttk.Scrollbar') as mock_scrollbar:
        
        # Configure mocks to return integers for geometry calculations
        mock_toplevel.return_value.winfo_rootx.return_value = 100
        mock_toplevel.return_value.winfo_rooty.return_value = 100
        mock_toplevel.return_value.geometry = Mock()
        
        yield
