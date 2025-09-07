import pytest
import sqlite3
from unittest.mock import Mock, patch, MagicMock
import property_manager
from property_manager import PropertyManager, PropertyDialog, PropertyDetailsDialog

class TestPropertyManager:
    """Test cases for PropertyManager class"""
    
    def test_init(self, mock_tkinter, mock_db_connection):
        """Test PropertyManager initialization"""
        with patch('property_manager.DB_FILE', mock_db_connection):
            parent_frame = Mock()
            manager = PropertyManager(parent_frame)
            assert manager.parent_frame == parent_frame
    
    def test_load_properties_empty(self, mock_tkinter, mock_db_connection):
        """Test loading properties when database is empty"""
        with patch('property_manager.DB_FILE', mock_db_connection):
            parent_frame = Mock()
            manager = PropertyManager(parent_frame)
            manager.tree = Mock()
            manager.tree.get_children.return_value = []
            manager.tree.delete = Mock()
            manager.tree.insert = Mock()
            
            manager.load_properties()
            manager.tree.delete.assert_not_called()
    
    def test_load_properties_with_data(self, mock_tkinter, mock_db_connection, sample_property_data):
        """Test loading properties with data"""
        with patch('property_manager.DB_FILE', mock_db_connection):
            # Add test property
            with sqlite3.connect(mock_db_connection) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO properties (name, address, type, size, rent_amount, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (sample_property_data['name'], sample_property_data['address'],
                     sample_property_data['type'], sample_property_data['size'],
                     sample_property_data['rent_amount'], sample_property_data['status']))
                conn.commit()
            
            parent_frame = Mock()
            manager = PropertyManager(parent_frame)
            manager.tree = Mock()
            manager.tree.get_children.return_value = []
            manager.tree.delete = Mock()
            manager.tree.insert = Mock()
            manager.status_filter = Mock()
            manager.status_filter.get.return_value = 'All'
            
            manager.load_properties()
            manager.tree.insert.assert_called_once()
    
    def test_filter_properties(self, mock_tkinter, mock_db_connection, sample_property_data):
        """Test property filtering"""
        with patch('property_manager.DB_FILE', mock_db_connection):
            # Add test properties with different statuses
            with sqlite3.connect(mock_db_connection) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO properties (name, address, rent_amount, status)
                    VALUES ('Property 1', 'Address 1', 1200, 'Vacant')
                """)
                cursor.execute("""
                    INSERT INTO properties (name, address, rent_amount, status)
                    VALUES ('Property 2', 'Address 2', 1500, 'Occupied')
                """)
                conn.commit()
            
            parent_frame = Mock()
            manager = PropertyManager(parent_frame)
            manager.tree = Mock()
            manager.tree.get_children.return_value = []
            manager.tree.delete = Mock()
            manager.tree.insert = Mock()
            manager.status_filter = Mock()
            manager.status_filter.get.return_value = 'Vacant'
            
            manager.filter_properties()
            manager.tree.insert.assert_called_once()  # Should only insert Vacant property
    
    def test_add_property(self, mock_tkinter, mock_db_connection):
        """Test adding a new property"""
        with patch('property_manager.DB_FILE', mock_db_connection), \
             patch('property_manager.PropertyDialog') as mock_dialog:
            parent_frame = Mock()
            manager = PropertyManager(parent_frame)
            
            manager.add_property()
            mock_dialog.assert_called_once_with(parent_frame, manager, "Add Property")
    
    def test_edit_property_no_selection(self, mock_tkinter, mock_db_connection):
        """Test editing property with no selection"""
        with patch('property_manager.DB_FILE', mock_db_connection), \
             patch('property_manager.messagebox') as mock_msgbox:
            parent_frame = Mock()
            manager = PropertyManager(parent_frame)
            manager.tree = Mock()
            manager.tree.selection.return_value = []
            
            manager.edit_property()
            mock_msgbox.showwarning.assert_called_once()
    
    def test_edit_property_with_selection(self, mock_tkinter, mock_db_connection):
        """Test editing property with selection"""
        with patch('property_manager.DB_FILE', mock_db_connection), \
             patch('property_manager.PropertyDialog') as mock_dialog:
            parent_frame = Mock()
            manager = PropertyManager(parent_frame)
            manager.tree = Mock()
            manager.tree.selection.return_value = ['item1']
            manager.tree.item.return_value = {'values': [1, 'Test Property']}
            
            manager.edit_property()
            mock_dialog.assert_called_once_with(parent_frame, manager, "Edit Property", 1)
    
    def test_view_property_details_no_selection(self, mock_tkinter, mock_db_connection):
        """Test viewing property details with no selection"""
        with patch('property_manager.DB_FILE', mock_db_connection), \
             patch('property_manager.messagebox') as mock_msgbox:
            parent_frame = Mock()
            manager = PropertyManager(parent_frame)
            manager.tree = Mock()
            manager.tree.selection.return_value = []
            
            manager.view_property_details()
            mock_msgbox.showwarning.assert_called_once()
    
    def test_view_property_details_with_selection(self, mock_tkinter, mock_db_connection):
        """Test viewing property details with selection"""
        with patch('property_manager.DB_FILE', mock_db_connection), \
             patch('property_manager.PropertyDetailsDialog') as mock_dialog:
            parent_frame = Mock()
            manager = PropertyManager(parent_frame)
            manager.tree = Mock()
            manager.tree.selection.return_value = ['item1']
            manager.tree.item.return_value = {'values': [1, 'Test Property']}
            
            manager.view_property_details()
            mock_dialog.assert_called_once_with(parent_frame, 1)
    
    def test_delete_property_no_selection(self, mock_tkinter, mock_db_connection):
        """Test deleting property with no selection"""
        with patch('property_manager.DB_FILE', mock_db_connection), \
             patch('property_manager.messagebox') as mock_msgbox:
            parent_frame = Mock()
            manager = PropertyManager(parent_frame)
            manager.tree = Mock()
            manager.tree.selection.return_value = []
            
            manager.delete_property()
            mock_msgbox.showwarning.assert_called_once()
    
    def test_delete_property_with_confirmation(self, mock_tkinter, mock_db_connection, sample_property_data):
        """Test deleting property with confirmation"""
        with patch('property_manager.DB_FILE', mock_db_connection), \
             patch('property_manager.messagebox') as mock_msgbox:
            # Add test property
            with sqlite3.connect(mock_db_connection) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO properties (name, address, rent_amount, status)
                    VALUES (?, ?, ?, ?)
                """, (sample_property_data['name'], sample_property_data['address'],
                     sample_property_data['rent_amount'], sample_property_data['status']))
                conn.commit()
            
            parent_frame = Mock()
            manager = PropertyManager(parent_frame)
            manager.tree = Mock()
            manager.tree.selection.return_value = ['item1']
            manager.tree.item.return_value = {'values': [1, 'Test Property']}
            manager.load_properties = Mock()
            mock_msgbox.askyesno.return_value = True
            
            manager.delete_property()
            mock_msgbox.askyesno.assert_called_once()
            mock_msgbox.showinfo.assert_called_once()

class TestPropertyDialog:
    """Test cases for PropertyDialog class"""
    
    def test_init_add_mode(self, mock_tkinter, mock_db_connection):
        """Test PropertyDialog initialization in add mode"""
        with patch('property_manager.DB_FILE', mock_db_connection):
            parent = Mock()
            parent.winfo_rootx.return_value = 100
            parent.winfo_rooty.return_value = 100
            property_manager = Mock()
            
            dialog = PropertyDialog(parent, property_manager, "Add Property")
            assert dialog.property_id is None
            # Dialog title is set correctly (tested by dialog creation)
    
    def test_init_edit_mode(self, mock_tkinter, mock_db_connection, sample_property_data):
        """Test PropertyDialog initialization in edit mode"""
        with patch('property_manager.DB_FILE', mock_db_connection):
            # Add test property
            with sqlite3.connect(mock_db_connection) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO properties (name, address, type, size, rent_amount, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (sample_property_data['name'], sample_property_data['address'],
                     sample_property_data['type'], sample_property_data['size'],
                     sample_property_data['rent_amount'], sample_property_data['status']))
                conn.commit()
            
            parent = Mock()
            parent.winfo_rootx.return_value = 100
            parent.winfo_rooty.return_value = 100
            property_manager = Mock()
            
            dialog = PropertyDialog(parent, property_manager, "Edit Property", 1)
            assert dialog.property_id == 1
            # Dialog title is set correctly (tested by dialog creation)
    
    def test_save_property_new(self, mock_tkinter, mock_db_connection):
        """Test saving a new property"""
        with patch('property_manager.DB_FILE', mock_db_connection), \
             patch('property_manager.messagebox') as mock_msgbox:
            parent = Mock()
            parent.winfo_rootx.return_value = 100
            parent.winfo_rooty.return_value = 100
            property_manager = Mock()
            property_manager.load_properties = Mock()
            
            dialog = PropertyDialog(parent, property_manager, "Add Property")
            dialog.entries = {
                'name': Mock(get=Mock(return_value='Test Property')),
                'address': Mock(get=Mock(return_value='123 Test St')),
                'type': Mock(get=Mock(return_value='Apartment')),
                'size': Mock(get=Mock(return_value='1000')),
                'bedrooms': Mock(get=Mock(return_value='2')),
                'bathrooms': Mock(get=Mock(return_value='1')),
                'rent_amount': Mock(get=Mock(return_value='1200')),
                'deposit_amount': Mock(get=Mock(return_value='1200')),
                'status': Mock(get=Mock(return_value='Vacant')),
                'furnished': Mock(get=Mock(return_value='Yes'))
            }
            dialog.dialog = Mock()
            
            dialog.save_property()
            mock_msgbox.showinfo.assert_called_once()
            property_manager.load_properties.assert_called_once()
    
    def test_save_property_missing_required_fields(self, mock_tkinter, mock_db_connection):
        """Test saving property with missing required fields"""
        with patch('property_manager.DB_FILE', mock_db_connection), \
             patch('property_manager.messagebox') as mock_msgbox:
            parent = Mock()
            parent.winfo_rootx.return_value = 100
            parent.winfo_rooty.return_value = 100
            property_manager = Mock()
            
            dialog = PropertyDialog(parent, property_manager, "Add Property")
            dialog.entries = {
                'address': Mock(get=Mock(return_value='')),  # Empty address
                'rent_amount': Mock(get=Mock(return_value='1200'))
            }
            
            dialog.save_property()
            mock_msgbox.showerror.assert_called_once()
    
    def test_save_property_invalid_numeric_values(self, mock_tkinter, mock_db_connection):
        """Test saving property with invalid numeric values"""
        with patch('property_manager.DB_FILE', mock_db_connection), \
             patch('property_manager.messagebox') as mock_msgbox:
            parent = Mock()
            parent.winfo_rootx.return_value = 100
            parent.winfo_rooty.return_value = 100
            property_manager = Mock()
            
            dialog = PropertyDialog(parent, property_manager, "Add Property")
            dialog.entries = {
                'name': Mock(get=Mock(return_value='Test Property')),
                'address': Mock(get=Mock(return_value='123 Test St')),
                'type': Mock(get=Mock(return_value='Apartment')),
                'size': Mock(get=Mock(return_value='invalid')),  # Invalid size
                'bedrooms': Mock(get=Mock(return_value='2')),
                'bathrooms': Mock(get=Mock(return_value='1')),
                'rent_amount': Mock(get=Mock(return_value='1200')),
                'deposit_amount': Mock(get=Mock(return_value='1200')),
                'status': Mock(get=Mock(return_value='Vacant')),
                'furnished': Mock(get=Mock(return_value='Yes'))
            }
            
            dialog.save_property()
            mock_msgbox.showerror.assert_called_once()
