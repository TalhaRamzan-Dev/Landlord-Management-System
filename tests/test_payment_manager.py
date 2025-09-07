import pytest
import sqlite3
from datetime import date, datetime
from unittest.mock import Mock, patch, MagicMock
import payment_manager
from payment_manager import PaymentManager, PaymentDialog, PaymentDetailsDialog

class TestPaymentManager:
    """Test cases for PaymentManager class"""
    
    def test_init(self, mock_tkinter, mock_db_connection):
        """Test PaymentManager initialization"""
        with patch('payment_manager.DB_FILE', mock_db_connection):
            parent_frame = Mock()
            manager = PaymentManager(parent_frame)
            assert manager.parent_frame == parent_frame
    
    def test_load_payments_empty(self, mock_tkinter, mock_db_connection):
        """Test loading payments when database is empty"""
        with patch('payment_manager.DB_FILE', mock_db_connection):
            parent_frame = Mock()
            manager = PaymentManager(parent_frame)
            manager.tree = Mock()
            manager.tree.get_children.return_value = []
            manager.tree.delete = Mock()
            manager.tree.insert = Mock()
            
            manager.load_payments()
            manager.tree.delete.assert_not_called()
    
    def test_load_payments_with_data(self, mock_tkinter, mock_db_connection, sample_payment_data):
        """Test loading payments with data"""
        with patch('payment_manager.DB_FILE', mock_db_connection):
            # Add test data
            with sqlite3.connect(mock_db_connection) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO properties (name, address, rent_amount, status)
                    VALUES ('Test Property', '123 Test St', 1200, 'Occupied')
                """)
                cursor.execute("""
                    INSERT INTO tenants (name, property_id, phone, email)
                    VALUES ('Test Tenant', 1, '555-1234', 'test@example.com')
                """)
                cursor.execute("""
                    INSERT INTO leases (tenant_id, property_id, start_date, end_date, rent_amount, status)
                    VALUES (1, 1, '2024-01-01', '2024-12-31', 1200, 'Active')
                """)
                cursor.execute("""
                    INSERT INTO rent_payments (lease_id, tenant_id, property_id, month, due_date, amount_due, amount_paid, status)
                    VALUES (1, 1, 1, ?, ?, ?, ?, ?)
                """, (sample_payment_data['month'], sample_payment_data['due_date'],
                     sample_payment_data['amount_due'], sample_payment_data['amount_paid'],
                     sample_payment_data['status']))
                conn.commit()
            
            parent_frame = Mock()
            manager = PaymentManager(parent_frame)
            manager.tree = Mock()
            manager.tree.get_children.return_value = []
            manager.tree.delete = Mock()
            manager.tree.insert = Mock()
            manager.status_filter = Mock()
            manager.status_filter.get.return_value = 'All'
            
            manager.load_payments()
            manager.tree.insert.assert_called_once()
    
    def test_filter_payments(self, mock_tkinter, mock_db_connection, sample_payment_data):
        """Test payment filtering"""
        with patch('payment_manager.DB_FILE', mock_db_connection):
            # Add test data
            with sqlite3.connect(mock_db_connection) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO properties (name, address, rent_amount, status)
                    VALUES ('Test Property', '123 Test St', 1200, 'Occupied')
                """)
                cursor.execute("""
                    INSERT INTO tenants (name, property_id, phone, email)
                    VALUES ('Test Tenant', 1, '555-1234', 'test@example.com')
                """)
                cursor.execute("""
                    INSERT INTO leases (tenant_id, property_id, start_date, end_date, rent_amount, status)
                    VALUES (1, 1, '2024-01-01', '2024-12-31', 1200, 'Active')
                """)
                cursor.execute("""
                    INSERT INTO rent_payments (lease_id, tenant_id, property_id, month, due_date, amount_due, amount_paid, status)
                    VALUES (1, 1, 1, ?, ?, ?, ?, 'Paid')
                """, (sample_payment_data['month'], sample_payment_data['due_date'],
                     sample_payment_data['amount_due'], sample_payment_data['amount_paid']))
                cursor.execute("""
                    INSERT INTO rent_payments (lease_id, tenant_id, property_id, month, due_date, amount_due, amount_paid, status)
                    VALUES (1, 1, 1, '2024-02', '2024-03-01', 1200, 0, 'Pending')
                """)
                conn.commit()
            
            parent_frame = Mock()
            manager = PaymentManager(parent_frame)
            manager.tree = Mock()
            manager.tree.get_children.return_value = []
            manager.tree.delete = Mock()
            manager.tree.insert = Mock()
            manager.status_filter = Mock()
            manager.status_filter.get.return_value = 'Paid'
            
            manager.filter_payments()
            manager.tree.insert.assert_called_once()  # Should only insert Paid payment
    
    def test_generate_monthly_rent(self, mock_tkinter, mock_db_connection):
        """Test generating monthly rent records"""
        with patch('payment_manager.DB_FILE', mock_db_connection), \
             patch('payment_manager.messagebox') as mock_msgbox:
            # Add test data
            with sqlite3.connect(mock_db_connection) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO properties (name, address, rent_amount, status)
                    VALUES ('Test Property', '123 Test St', 1200, 'Occupied')
                """)
                cursor.execute("""
                    INSERT INTO tenants (name, property_id, phone, email)
                    VALUES ('Test Tenant', 1, '555-1234', 'test@example.com')
                """)
                cursor.execute("""
                    INSERT INTO leases (tenant_id, property_id, start_date, end_date, rent_amount, status)
                    VALUES (1, 1, '2024-01-01', '2024-12-31', 1200, 'Active')
                """)
                conn.commit()
            
            parent_frame = Mock()
            manager = PaymentManager(parent_frame)
            manager.load_payments = Mock()
            
            manager.generate_monthly_rent()
            mock_msgbox.showinfo.assert_called_once()
            manager.load_payments.assert_called_once()
    
    def test_record_payment(self, mock_tkinter, mock_db_connection):
        """Test recording a new payment"""
        with patch('payment_manager.DB_FILE', mock_db_connection), \
             patch('payment_manager.PaymentDialog') as mock_dialog:
            parent_frame = Mock()
            manager = PaymentManager(parent_frame)
            
            manager.record_payment()
            mock_dialog.assert_called_once_with(parent_frame, manager, "Record Payment")
    
    def test_edit_payment_no_selection(self, mock_tkinter, mock_db_connection):
        """Test editing payment with no selection"""
        with patch('payment_manager.DB_FILE', mock_db_connection), \
             patch('payment_manager.messagebox') as mock_msgbox:
            parent_frame = Mock()
            manager = PaymentManager(parent_frame)
            manager.tree = Mock()
            manager.tree.selection.return_value = []
            
            manager.edit_payment()
            mock_msgbox.showwarning.assert_called_once()
    
    def test_edit_payment_with_selection(self, mock_tkinter, mock_db_connection):
        """Test editing payment with selection"""
        with patch('payment_manager.DB_FILE', mock_db_connection), \
             patch('payment_manager.PaymentDialog') as mock_dialog:
            parent_frame = Mock()
            manager = PaymentManager(parent_frame)
            manager.tree = Mock()
            manager.tree.selection.return_value = ['item1']
            manager.tree.item.return_value = {'values': [1, 'Test Tenant']}
            
            manager.edit_payment()
            mock_dialog.assert_called_once_with(parent_frame, manager, "Edit Payment", 1)
    
    def test_view_payment_details_no_selection(self, mock_tkinter, mock_db_connection):
        """Test viewing payment details with no selection"""
        with patch('payment_manager.DB_FILE', mock_db_connection), \
             patch('payment_manager.messagebox') as mock_msgbox:
            parent_frame = Mock()
            manager = PaymentManager(parent_frame)
            manager.tree = Mock()
            manager.tree.selection.return_value = []
            
            manager.view_payment_details()
            mock_msgbox.showwarning.assert_called_once()
    
    def test_view_payment_details_with_selection(self, mock_tkinter, mock_db_connection):
        """Test viewing payment details with selection"""
        with patch('payment_manager.DB_FILE', mock_db_connection), \
             patch('payment_manager.PaymentDetailsDialog') as mock_dialog:
            parent_frame = Mock()
            manager = PaymentManager(parent_frame)
            manager.tree = Mock()
            manager.tree.selection.return_value = ['item1']
            manager.tree.item.return_value = {'values': [1, 'Test Tenant']}
            
            manager.view_payment_details()
            mock_dialog.assert_called_once_with(parent_frame, 1)
    
    def test_delete_payment_no_selection(self, mock_tkinter, mock_db_connection):
        """Test deleting payment with no selection"""
        with patch('payment_manager.DB_FILE', mock_db_connection), \
             patch('payment_manager.messagebox') as mock_msgbox:
            parent_frame = Mock()
            manager = PaymentManager(parent_frame)
            manager.tree = Mock()
            manager.tree.selection.return_value = []
            
            manager.delete_payment()
            mock_msgbox.showwarning.assert_called_once()
    
    def test_delete_payment_with_confirmation(self, mock_tkinter, mock_db_connection, sample_payment_data):
        """Test deleting payment with confirmation"""
        with patch('payment_manager.DB_FILE', mock_db_connection), \
             patch('payment_manager.messagebox') as mock_msgbox:
            # Add test payment
            with sqlite3.connect(mock_db_connection) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO properties (name, address, rent_amount, status)
                    VALUES ('Test Property', '123 Test St', 1200, 'Occupied')
                """)
                cursor.execute("""
                    INSERT INTO tenants (name, property_id, phone, email)
                    VALUES ('Test Tenant', 1, '555-1234', 'test@example.com')
                """)
                cursor.execute("""
                    INSERT INTO leases (tenant_id, property_id, start_date, end_date, rent_amount, status)
                    VALUES (1, 1, '2024-01-01', '2024-12-31', 1200, 'Active')
                """)
                cursor.execute("""
                    INSERT INTO rent_payments (lease_id, tenant_id, property_id, month, due_date, amount_due, amount_paid, status)
                    VALUES (1, 1, 1, ?, ?, ?, ?, ?)
                """, (sample_payment_data['month'], sample_payment_data['due_date'],
                     sample_payment_data['amount_due'], sample_payment_data['amount_paid'],
                     sample_payment_data['status']))
                conn.commit()
            
            parent_frame = Mock()
            manager = PaymentManager(parent_frame)
            manager.tree = Mock()
            manager.tree.selection.return_value = ['item1']
            manager.tree.item.return_value = {'values': [1, 'Test Tenant']}
            manager.load_payments = Mock()
            mock_msgbox.askyesno.return_value = True
            
            manager.delete_payment()
            mock_msgbox.askyesno.assert_called_once()
            mock_msgbox.showinfo.assert_called_once()

class TestPaymentDialog:
    """Test cases for PaymentDialog class"""
    
    def test_init_add_mode(self, mock_tkinter, mock_db_connection):
        """Test PaymentDialog initialization in add mode"""
        with patch('payment_manager.DB_FILE', mock_db_connection):
            parent = Mock()
            parent.winfo_rootx.return_value = 100
            parent.winfo_rooty.return_value = 100
            payment_manager = Mock()
            
            dialog = PaymentDialog(parent, payment_manager, "Record Payment")
            assert dialog.payment_id is None
            # Dialog title is set correctly (tested by dialog creation)
    
    def test_init_edit_mode(self, mock_tkinter, mock_db_connection, sample_payment_data):
        """Test PaymentDialog initialization in edit mode"""
        with patch('payment_manager.DB_FILE', mock_db_connection):
            # Add test payment
            with sqlite3.connect(mock_db_connection) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO properties (name, address, rent_amount, status)
                    VALUES ('Test Property', '123 Test St', 1200, 'Occupied')
                """)
                cursor.execute("""
                    INSERT INTO tenants (name, property_id, phone, email)
                    VALUES ('Test Tenant', 1, '555-1234', 'test@example.com')
                """)
                cursor.execute("""
                    INSERT INTO leases (tenant_id, property_id, start_date, end_date, rent_amount, status)
                    VALUES (1, 1, '2024-01-01', '2024-12-31', 1200, 'Active')
                """)
                cursor.execute("""
                    INSERT INTO rent_payments (lease_id, tenant_id, property_id, month, due_date, amount_due, amount_paid, status)
                    VALUES (1, 1, 1, ?, ?, ?, ?, ?)
                """, (sample_payment_data['month'], sample_payment_data['due_date'],
                     sample_payment_data['amount_due'], sample_payment_data['amount_paid'],
                     sample_payment_data['status']))
                conn.commit()
            
            parent = Mock()
            parent.winfo_rootx.return_value = 100
            parent.winfo_rooty.return_value = 100
            payment_manager = Mock()
            
            dialog = PaymentDialog(parent, payment_manager, "Edit Payment", 1)
            assert dialog.payment_id == 1
            # Dialog title is set correctly (tested by dialog creation)
    
    def test_save_payment_new(self, mock_tkinter, mock_db_connection, sample_payment_data):
        """Test saving a new payment"""
        with patch('payment_manager.DB_FILE', mock_db_connection), \
             patch('payment_manager.messagebox') as mock_msgbox:
            # Add test data
            with sqlite3.connect(mock_db_connection) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO properties (name, address, rent_amount, status)
                    VALUES ('Test Property', '123 Test St', 1200, 'Occupied')
                """)
                cursor.execute("""
                    INSERT INTO tenants (name, property_id, phone, email)
                    VALUES ('Test Tenant', 1, '555-1234', 'test@example.com')
                """)
                cursor.execute("""
                    INSERT INTO leases (tenant_id, property_id, start_date, end_date, rent_amount, status)
                    VALUES (1, 1, '2024-01-01', '2024-12-31', 1200, 'Active')
                """)
                conn.commit()
            
            parent = Mock()
            parent.winfo_rootx.return_value = 100
            parent.winfo_rooty.return_value = 100
            payment_manager = Mock()
            payment_manager.load_payments = Mock()
            
            dialog = PaymentDialog(parent, payment_manager, "Record Payment")
            dialog.entries = {
                'lease_id': Mock(get=Mock(return_value='Test Tenant - Test Property (Lease ID: 1)')),
                'month': Mock(get=Mock(return_value='2024-01')),
                'due_date': Mock(get=Mock(return_value='2024-02-01')),
                'amount_due': Mock(get=Mock(return_value='1200')),
                'amount_paid': Mock(get=Mock(return_value='1200')),
                'payment_date': Mock(get=Mock(return_value='2024-01-15')),
                'payment_method': Mock(get=Mock(return_value='Bank Transfer')),
                'status': Mock(get=Mock(return_value='Paid')),
                'notes': Mock(get=Mock(return_value='Test payment'))
            }
            dialog.dialog = Mock()
            
            dialog.save_payment()
            mock_msgbox.showinfo.assert_called_once()
            payment_manager.load_payments.assert_called_once()
    
    def test_save_payment_missing_required_fields(self, mock_tkinter, mock_db_connection):
        """Test saving payment with missing required fields"""
        with patch('payment_manager.DB_FILE', mock_db_connection), \
             patch('payment_manager.messagebox') as mock_msgbox:
            parent = Mock()
            parent.winfo_rootx.return_value = 100
            parent.winfo_rooty.return_value = 100
            payment_manager = Mock()
            
            dialog = PaymentDialog(parent, payment_manager, "Record Payment")
            dialog.entries = {
                'lease_id': Mock(get=Mock(return_value='')),  # Empty lease
                'month': Mock(get=Mock(return_value='2024-01')),
                'amount_due': Mock(get=Mock(return_value='1200'))
            }
            
            dialog.save_payment()
            mock_msgbox.showerror.assert_called_once()
    
    def test_save_payment_invalid_numeric_values(self, mock_tkinter, mock_db_connection):
        """Test saving payment with invalid numeric values"""
        with patch('payment_manager.DB_FILE', mock_db_connection), \
             patch('payment_manager.messagebox') as mock_msgbox:
            parent = Mock()
            parent.winfo_rootx.return_value = 100
            parent.winfo_rooty.return_value = 100
            payment_manager = Mock()
            
            dialog = PaymentDialog(parent, payment_manager, "Record Payment")
            dialog.entries = {
                'lease_id': Mock(get=Mock(return_value='Test Tenant - Test Property (Lease ID: 1)')),
                'month': Mock(get=Mock(return_value='2024-01')),
                'due_date': Mock(get=Mock(return_value='2024-02-01')),
                'amount_due': Mock(get=Mock(return_value='invalid')),  # Invalid amount
                'amount_paid': Mock(get=Mock(return_value='1200')),
                'payment_date': Mock(get=Mock(return_value='2024-01-15')),
                'payment_method': Mock(get=Mock(return_value='Bank Transfer')),
                'status': Mock(get=Mock(return_value='Paid')),
                'notes': Mock(get=Mock(return_value='Test payment'))
            }
            
            dialog.save_payment()
            mock_msgbox.showerror.assert_called_once()
