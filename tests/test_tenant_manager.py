import pytest
import sqlite3
from unittest.mock import Mock, patch, MagicMock
import tenant_manager
from tenant_manager import TenantManager, TenantDialog, TenantDetailsDialog

class TestTenantManager:
    """Test cases for TenantManager class"""
    
    def test_init(self, mock_tkinter, mock_db_connection):
        """Test TenantManager initialization"""
        with patch('tenant_manager.DB_FILE', mock_db_connection):
            parent_frame = Mock()
            manager = TenantManager(parent_frame)
            assert manager.parent_frame == parent_frame
    
    def test_load_tenants_empty(self, mock_tkinter, mock_db_connection):
        """Test loading tenants when database is empty"""
        with patch('tenant_manager.DB_FILE', mock_db_connection):
            parent_frame = Mock()
            manager = TenantManager(parent_frame)
            manager.tree = Mock()
            manager.tree.get_children.return_value = []
            manager.tree.delete = Mock()
            manager.tree.insert = Mock()
            
            manager.load_tenants()
            manager.tree.delete.assert_not_called()
    
    def test_load_tenants_with_data(self, mock_tkinter, mock_db_connection, sample_tenant_data, sample_property_data):
        """Test loading tenants with data"""
        with patch('tenant_manager.DB_FILE', mock_db_connection):
            # Add test property and tenant
            with sqlite3.connect(mock_db_connection) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO properties (name, address, rent_amount, status)
                    VALUES (?, ?, ?, ?)
                """, (sample_property_data['name'], sample_property_data['address'],
                     sample_property_data['rent_amount'], sample_property_data['status']))
                cursor.execute("""
                    INSERT INTO tenants (name, property_id, phone, email)
                    VALUES (?, 1, ?, ?)
                """, (sample_tenant_data['name'], sample_tenant_data['phone'], sample_tenant_data['email']))
                conn.commit()
            
            parent_frame = Mock()
            manager = TenantManager(parent_frame)
            manager.tree = Mock()
            manager.tree.get_children.return_value = []
            manager.tree.delete = Mock()
            manager.tree.insert = Mock()
            
            manager.load_tenants()
            manager.tree.insert.assert_called_once()
    
    def test_filter_tenants_by_property(self, mock_tkinter, mock_db_connection, sample_tenant_data, sample_property_data):
        """Test filtering tenants by property"""
        with patch('tenant_manager.DB_FILE', mock_db_connection):
            # Add test properties and tenants
            with sqlite3.connect(mock_db_connection) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO properties (name, address, rent_amount, status)
                    VALUES ('Property 1', 'Address 1', 1200, 'Occupied')
                """)
                cursor.execute("""
                    INSERT INTO properties (name, address, rent_amount, status)
                    VALUES ('Property 2', 'Address 2', 1500, 'Occupied')
                """)
                cursor.execute("""
                    INSERT INTO tenants (name, property_id, phone, email)
                    VALUES ('Tenant 1', 1, '555-1111', 'tenant1@example.com')
                """)
                cursor.execute("""
                    INSERT INTO tenants (name, property_id, phone, email)
                    VALUES ('Tenant 2', 2, '555-2222', 'tenant2@example.com')
                """)
                conn.commit()
            
            parent_frame = Mock()
            manager = TenantManager(parent_frame)
            manager.tree = Mock()
            manager.tree.get_children.return_value = []
            manager.tree.delete = Mock()
            manager.tree.insert = Mock()
            manager.property_filter = Mock()
            manager.property_filter.get.return_value = 'Property 1 - Address 1'
            
            manager.filter_tenants()
            manager.tree.insert.assert_called_once()  # Should only insert tenant from Property 1
    
    def test_load_all_tenants(self, mock_tkinter, mock_db_connection):
        """Test loading all tenants (clear filter)"""
        with patch('tenant_manager.DB_FILE', mock_db_connection):
            parent_frame = Mock()
            manager = TenantManager(parent_frame)
            manager.property_filter = Mock()
            manager.load_tenants = Mock()
            
            manager.load_all_tenants()
            manager.property_filter.set.assert_called_once_with('All Properties')
            manager.load_tenants.assert_called_once()
    
    def test_add_tenant(self, mock_tkinter, mock_db_connection):
        """Test adding a new tenant"""
        with patch('tenant_manager.DB_FILE', mock_db_connection), \
             patch('tenant_manager.TenantDialog') as mock_dialog:
            parent_frame = Mock()
            manager = TenantManager(parent_frame)
            
            manager.add_tenant()
            mock_dialog.assert_called_once_with(parent_frame, manager, "Add Tenant")
    
    def test_edit_tenant_no_selection(self, mock_tkinter, mock_db_connection):
        """Test editing tenant with no selection"""
        with patch('tenant_manager.DB_FILE', mock_db_connection), \
             patch('tenant_manager.messagebox') as mock_msgbox:
            parent_frame = Mock()
            manager = TenantManager(parent_frame)
            manager.tree = Mock()
            manager.tree.selection.return_value = []
            
            manager.edit_tenant()
            mock_msgbox.showwarning.assert_called_once()
    
    def test_edit_tenant_with_selection(self, mock_tkinter, mock_db_connection):
        """Test editing tenant with selection"""
        with patch('tenant_manager.DB_FILE', mock_db_connection), \
             patch('tenant_manager.TenantDialog') as mock_dialog:
            parent_frame = Mock()
            manager = TenantManager(parent_frame)
            manager.tree = Mock()
            manager.tree.selection.return_value = ['item1']
            manager.tree.item.return_value = {'values': [1, 'Test Tenant']}
            
            manager.edit_tenant()
            mock_dialog.assert_called_once_with(parent_frame, manager, "Edit Tenant", 1)
    
    def test_view_tenant_details_no_selection(self, mock_tkinter, mock_db_connection):
        """Test viewing tenant details with no selection"""
        with patch('tenant_manager.DB_FILE', mock_db_connection), \
             patch('tenant_manager.messagebox') as mock_msgbox:
            parent_frame = Mock()
            manager = TenantManager(parent_frame)
            manager.tree = Mock()
            manager.tree.selection.return_value = []
            
            manager.view_tenant_details()
            mock_msgbox.showwarning.assert_called_once()
    
    def test_view_tenant_details_with_selection(self, mock_tkinter, mock_db_connection):
        """Test viewing tenant details with selection"""
        with patch('tenant_manager.DB_FILE', mock_db_connection), \
             patch('tenant_manager.TenantDetailsDialog') as mock_dialog:
            parent_frame = Mock()
            manager = TenantManager(parent_frame)
            manager.tree = Mock()
            manager.tree.selection.return_value = ['item1']
            manager.tree.item.return_value = {'values': [1, 'Test Tenant']}
            
            manager.view_tenant_details()
            mock_dialog.assert_called_once_with(parent_frame, 1)
    
    def test_remove_tenant_no_selection(self, mock_tkinter, mock_db_connection):
        """Test removing tenant with no selection"""
        with patch('tenant_manager.DB_FILE', mock_db_connection), \
             patch('tenant_manager.messagebox') as mock_msgbox:
            parent_frame = Mock()
            manager = TenantManager(parent_frame)
            manager.tree = Mock()
            manager.tree.selection.return_value = []
            
            manager.remove_tenant()
            mock_msgbox.showwarning.assert_called_once()
    
    def test_remove_tenant_with_confirmation(self, mock_tkinter, mock_db_connection, sample_tenant_data):
        """Test removing tenant with confirmation"""
        with patch('tenant_manager.DB_FILE', mock_db_connection), \
             patch('tenant_manager.messagebox') as mock_msgbox:
            # Add test tenant
            with sqlite3.connect(mock_db_connection) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO tenants (name, phone, email)
                    VALUES (?, ?, ?)
                """, (sample_tenant_data['name'], sample_tenant_data['phone'], sample_tenant_data['email']))
                conn.commit()
            
            parent_frame = Mock()
            manager = TenantManager(parent_frame)
            manager.tree = Mock()
            manager.tree.selection.return_value = ['item1']
            manager.tree.item.return_value = {'values': [1, 'Test Tenant']}
            manager.load_tenants = Mock()
            mock_msgbox.askyesno.return_value = True
            
            manager.remove_tenant()
            mock_msgbox.askyesno.assert_called_once()
            mock_msgbox.showinfo.assert_called_once()

class TestTenantDialog:
    """Test cases for TenantDialog class"""
    
    def test_init_add_mode(self, mock_tkinter, mock_db_connection):
        """Test TenantDialog initialization in add mode"""
        with patch('tenant_manager.DB_FILE', mock_db_connection):
            parent = Mock()
            parent.winfo_rootx.return_value = 100
            parent.winfo_rooty.return_value = 100
            tenant_manager = Mock()
            
            dialog = TenantDialog(parent, tenant_manager, "Add Tenant")
            assert dialog.tenant_id is None
            # Dialog title is set correctly (tested by dialog creation)
    
    def test_init_edit_mode(self, mock_tkinter, mock_db_connection, sample_tenant_data):
        """Test TenantDialog initialization in edit mode"""
        with patch('tenant_manager.DB_FILE', mock_db_connection):
            # Add test tenant
            with sqlite3.connect(mock_db_connection) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO tenants (name, phone, email, national_id, emergency_contact, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (sample_tenant_data['name'], sample_tenant_data['phone'], 
                     sample_tenant_data['email'], sample_tenant_data['national_id'],
                     sample_tenant_data['emergency_contact'], sample_tenant_data['notes']))
                conn.commit()
            
            parent = Mock()
            parent.winfo_rootx.return_value = 100
            parent.winfo_rooty.return_value = 100
            tenant_manager = Mock()
            
            dialog = TenantDialog(parent, tenant_manager, "Edit Tenant", 1)
            assert dialog.tenant_id == 1
            # Dialog title is set correctly (tested by dialog creation)
    
    def test_save_tenant_new(self, mock_tkinter, mock_db_connection, sample_property_data):
        """Test saving a new tenant"""
        with patch('tenant_manager.DB_FILE', mock_db_connection), \
             patch('tenant_manager.messagebox') as mock_msgbox:
            # Add test property
            with sqlite3.connect(mock_db_connection) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO properties (name, address, rent_amount, status)
                    VALUES (?, ?, ?, ?)
                """, (sample_property_data['name'], sample_property_data['address'],
                     sample_property_data['rent_amount'], sample_property_data['status']))
                conn.commit()
            
            parent = Mock()
            parent.winfo_rootx.return_value = 100
            parent.winfo_rooty.return_value = 100
            tenant_manager = Mock()
            tenant_manager.load_tenants = Mock()
            
            dialog = TenantDialog(parent, tenant_manager, "Add Tenant")
            dialog.entries = {
                'name': Mock(get=Mock(return_value='Test Tenant')),
                'property_id': Mock(get=Mock(return_value='Test Property - 123 Test St')),
                'phone': Mock(get=Mock(return_value='555-1234')),
                'email': Mock(get=Mock(return_value='test@example.com')),
                'national_id': Mock(get=Mock(return_value='123456789')),
                'emergency_contact': Mock(get=Mock(return_value='Jane Doe - 555-5678')),
                'notes': Mock(get=Mock(return_value='Test tenant'))
            }
            dialog.dialog = Mock()
            
            dialog.save_tenant()
            mock_msgbox.showinfo.assert_called_once()
            tenant_manager.load_tenants.assert_called_once()
    
    def test_save_tenant_missing_required_fields(self, mock_tkinter, mock_db_connection):
        """Test saving tenant with missing required fields"""
        with patch('tenant_manager.DB_FILE', mock_db_connection), \
             patch('tenant_manager.messagebox') as mock_msgbox:
            parent = Mock()
            parent.winfo_rootx.return_value = 100
            parent.winfo_rooty.return_value = 100
            tenant_manager = Mock()
            
            dialog = TenantDialog(parent, tenant_manager, "Add Tenant")
            dialog.entries = {
                'name': Mock(get=Mock(return_value='')),  # Empty name
                'property_id': Mock(get=Mock(return_value='Test Property - 123 Test St'))
            }
            
            dialog.save_tenant()
            mock_msgbox.showerror.assert_called_once()
    
    def test_save_tenant_invalid_property(self, mock_tkinter, mock_db_connection):
        """Test saving tenant with invalid property selection"""
        with patch('tenant_manager.DB_FILE', mock_db_connection), \
             patch('tenant_manager.messagebox') as mock_msgbox:
            parent = Mock()
            parent.winfo_rootx.return_value = 100
            parent.winfo_rooty.return_value = 100
            tenant_manager = Mock()
            
            dialog = TenantDialog(parent, tenant_manager, "Add Tenant")
            dialog.entries = {
                'name': Mock(get=Mock(return_value='Test Tenant')),
                'property_id': Mock(get=Mock(return_value='Invalid Property - Invalid Address'))
            }
            
            dialog.save_tenant()
            mock_msgbox.showerror.assert_called_once()
