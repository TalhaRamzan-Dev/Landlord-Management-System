import pytest
import sqlite3
import hashlib
from unittest.mock import Mock, patch, MagicMock
import main
from main import PropertyManagementApp

class TestPropertyManagementApp:
    """Test cases for the main PropertyManagementApp class"""
    
    def test_init(self, mock_tkinter):
        """Test application initialization"""
        with patch('main.init_db'):
            app = PropertyManagementApp()
            assert app.current_user is None
            assert app.is_logged_in is False
            # login_frame and main_frame are created during initialization
            assert app.login_frame is not None
            assert app.main_frame is None
    
    def test_hash_password(self, mock_tkinter):
        """Test password hashing functionality"""
        with patch('main.init_db'):
            app = PropertyManagementApp()
            password = "testpassword"
            hashed = app.hash_password(password)
            expected = hashlib.sha256(password.encode()).hexdigest()
            assert hashed == expected
    
    def test_hash_password_empty(self, mock_tkinter):
        """Test password hashing with empty password"""
        with patch('main.init_db'):
            app = PropertyManagementApp()
            password = ""
            hashed = app.hash_password(password)
            expected = hashlib.sha256(password.encode()).hexdigest()
            assert hashed == expected
    
    def test_hash_password_consistency(self, mock_tkinter):
        """Test that same password always produces same hash"""
        with patch('main.init_db'):
            app = PropertyManagementApp()
            password = "consistentpassword"
            hash1 = app.hash_password(password)
            hash2 = app.hash_password(password)
            assert hash1 == hash2
    
    def test_hash_password_different_passwords(self, mock_tkinter):
        """Test that different passwords produce different hashes"""
        with patch('main.init_db'):
            app = PropertyManagementApp()
            password1 = "password1"
            password2 = "password2"
            hash1 = app.hash_password(password1)
            hash2 = app.hash_password(password2)
            assert hash1 != hash2
    
    def test_setup_admin_success(self, mock_tkinter, mock_db_connection):
        """Test successful admin account setup"""
        with patch('main.init_db'), \
             patch('main.DB_FILE', mock_db_connection), \
             patch('main.messagebox') as mock_msgbox:
            app = PropertyManagementApp()
            app.username_entry = Mock()
            app.password_entry = Mock()
            app.username_entry.get.return_value = "admin"
            app.password_entry.get.return_value = "password123"
            
            with sqlite3.connect(mock_db_connection) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM admin")
                initial_count = cursor.fetchone()[0]
            
            app.setup_admin()
            
            with sqlite3.connect(mock_db_connection) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM admin")
                final_count = cursor.fetchone()[0]
            
            assert final_count == initial_count + 1
            mock_msgbox.showinfo.assert_called_once()
    
    def test_setup_admin_duplicate(self, mock_tkinter, mock_db_connection):
        """Test admin setup with duplicate username"""
        with patch('main.init_db'), \
             patch('main.messagebox') as mock_msgbox:
            app = PropertyManagementApp()
            app.username_entry = Mock()
            app.password_entry = Mock()
            app.username_entry.get.return_value = "admin"
            app.password_entry.get.return_value = "password123"
            
            # Create initial admin
            with sqlite3.connect(mock_db_connection) as conn:
                cursor = conn.cursor()
                password_hash = app.hash_password("password123")
                cursor.execute("INSERT INTO admin (username, password_hash) VALUES (?, ?)", 
                             ("admin", password_hash))
                conn.commit()
            
            app.setup_admin()
            mock_msgbox.showerror.assert_called_once()
    
    def test_setup_admin_empty_fields(self, mock_tkinter):
        """Test admin setup with empty fields"""
        with patch('main.init_db'), \
             patch('main.messagebox') as mock_msgbox:
            app = PropertyManagementApp()
            app.username_entry = Mock()
            app.password_entry = Mock()
            app.username_entry.get.return_value = ""
            app.password_entry.get.return_value = ""
            
            app.setup_admin()
            mock_msgbox.showerror.assert_called_once()
    
    def test_login_success(self, mock_tkinter, mock_db_connection):
        """Test successful login"""
        with patch('main.init_db'), \
             patch('main.DB_FILE', mock_db_connection), \
             patch('main.messagebox') as mock_msgbox:
            app = PropertyManagementApp()
            app.username_entry = Mock()
            app.password_entry = Mock()
            app.username_entry.get.return_value = "admin"
            app.password_entry.get.return_value = "password123"
            
            # Create admin user
            with sqlite3.connect(mock_db_connection) as conn:
                cursor = conn.cursor()
                password_hash = app.hash_password("password123")
                cursor.execute("INSERT INTO admin (username, password_hash) VALUES (?, ?)", 
                             ("admin", password_hash))
                conn.commit()
            
            app.login()
            assert app.is_logged_in is True
            assert app.current_user is not None
            assert app.current_user['username'] == "admin"
    
    def test_login_invalid_credentials(self, mock_tkinter, mock_db_connection):
        """Test login with invalid credentials"""
        with patch('main.init_db'), \
             patch('main.messagebox') as mock_msgbox:
            app = PropertyManagementApp()
            app.username_entry = Mock()
            app.password_entry = Mock()
            app.username_entry.get.return_value = "admin"
            app.password_entry.get.return_value = "wrongpassword"
            
            # Create admin user
            with sqlite3.connect(mock_db_connection) as conn:
                cursor = conn.cursor()
                password_hash = app.hash_password("password123")
                cursor.execute("INSERT INTO admin (username, password_hash) VALUES (?, ?)", 
                             ("admin", password_hash))
                conn.commit()
            
            app.login()
            assert app.is_logged_in is False
            assert app.current_user is None
            mock_msgbox.showerror.assert_called_once()
    
    def test_login_empty_fields(self, mock_tkinter):
        """Test login with empty fields"""
        with patch('main.init_db'), \
             patch('main.messagebox') as mock_msgbox:
            app = PropertyManagementApp()
            app.username_entry = Mock()
            app.password_entry = Mock()
            app.username_entry.get.return_value = ""
            app.password_entry.get.return_value = ""
            
            app.login()
            assert app.is_logged_in is False
            mock_msgbox.showerror.assert_called_once()
    
    def test_logout(self, mock_tkinter):
        """Test logout functionality"""
        with patch('main.init_db'):
            app = PropertyManagementApp()
            app.current_user = {'id': 1, 'username': 'admin'}
            app.is_logged_in = True
            
            app.logout()
            assert app.current_user is None
            assert app.is_logged_in is False
    
    def test_clear_content(self, mock_tkinter):
        """Test content frame clearing"""
        with patch('main.init_db'):
            app = PropertyManagementApp()
            app.content_frame = Mock()
            app.content_frame.winfo_children.return_value = [Mock(), Mock()]
            
            app.clear_content()
            app.content_frame.winfo_children.assert_called_once()
    
    def test_show_dashboard(self, mock_tkinter, mock_db_connection):
        """Test dashboard display"""
        with patch('main.init_db'), \
             patch('main.messagebox') as mock_msgbox:
            app = PropertyManagementApp()
            app.content_frame = Mock()
            app.content_frame.winfo_children.return_value = []  # Mock empty children
            app.current_user = {'id': 1, 'username': 'admin'}
            app.is_logged_in = True
            
            # Add some test data
            with sqlite3.connect(mock_db_connection) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO properties (name, address, rent_amount, status) 
                    VALUES ('Test Property', '123 Test St', 1200, 'Occupied')
                """)
                cursor.execute("""
                    INSERT INTO tenants (name, property_id) 
                    VALUES ('Test Tenant', 1)
                """)
                conn.commit()
            
            app.show_dashboard()
            # Should not raise any exceptions
            assert True
    
    def test_show_properties(self, mock_tkinter):
        """Test properties module loading"""
        with patch('main.init_db'), \
             patch('property_manager.PropertyManager') as mock_property_manager:
            app = PropertyManagementApp()
            app.content_frame = Mock()
            app.content_frame.winfo_children.return_value = []
            
            app.show_properties()
            mock_property_manager.assert_called_once_with(app.content_frame)
    
    def test_show_tenants(self, mock_tkinter):
        """Test tenants module loading"""
        with patch('main.init_db'), \
             patch('tenant_manager.TenantManager') as mock_tenant_manager:
            app = PropertyManagementApp()
            app.content_frame = Mock()
            app.content_frame.winfo_children.return_value = []
            
            app.show_tenants()
            mock_tenant_manager.assert_called_once_with(app.content_frame)
    
    def test_show_leases(self, mock_tkinter):
        """Test leases module loading"""
        with patch('main.init_db'), \
             patch('lease_manager.LeaseManager') as mock_lease_manager:
            app = PropertyManagementApp()
            app.content_frame = Mock()
            app.content_frame.winfo_children.return_value = []
            
            app.show_leases()
            mock_lease_manager.assert_called_once_with(app.content_frame)
    
    def test_show_payments(self, mock_tkinter):
        """Test payments module loading"""
        with patch('main.init_db'), \
             patch('payment_manager.PaymentManager') as mock_payment_manager:
            app = PropertyManagementApp()
            app.content_frame = Mock()
            app.content_frame.winfo_children.return_value = []
            
            app.show_payments()
            mock_payment_manager.assert_called_once_with(app.content_frame)
    
    def test_show_expenses(self, mock_tkinter):
        """Test expenses module loading"""
        with patch('main.init_db'), \
             patch('expense_manager.ExpenseManager') as mock_expense_manager:
            app = PropertyManagementApp()
            app.content_frame = Mock()
            app.content_frame.winfo_children.return_value = []
            
            app.show_expenses()
            mock_expense_manager.assert_called_once_with(app.content_frame)
    
    def test_show_documents(self, mock_tkinter):
        """Test documents module loading"""
        with patch('main.init_db'), \
             patch('document_manager.DocumentManager') as mock_document_manager:
            app = PropertyManagementApp()
            app.content_frame = Mock()
            app.content_frame.winfo_children.return_value = []
            
            app.show_documents()
            mock_document_manager.assert_called_once_with(app.content_frame)
    
    def test_show_maintenance(self, mock_tkinter):
        """Test maintenance module loading"""
        with patch('main.init_db'), \
             patch('maintenance_manager.MaintenanceManager') as mock_maintenance_manager:
            app = PropertyManagementApp()
            app.content_frame = Mock()
            app.content_frame.winfo_children.return_value = []
            
            app.show_maintenance()
            mock_maintenance_manager.assert_called_once_with(app.content_frame)
    
    def test_show_reports(self, mock_tkinter):
        """Test reports module loading"""
        with patch('main.init_db'), \
             patch('reports_manager.ReportsManager') as mock_reports_manager:
            app = PropertyManagementApp()
            app.content_frame = Mock()
            app.content_frame.winfo_children.return_value = []
            
            app.show_reports()
            mock_reports_manager.assert_called_once_with(app.content_frame)
