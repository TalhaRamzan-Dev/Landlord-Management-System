import pytest
import sqlite3
import os
import tempfile
import shutil
from unittest.mock import patch
import db

class TestDatabase:
    """Test cases for database operations"""
    
    def test_init_db_new_database(self, temp_db):
        """Test database initialization with new database"""
        # Database should be created with schema
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            
            # Check if all tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = [
                'admin', 'properties', 'tenants', 'leases', 
                'rent_payments', 'expenses', 'documents', 'maintenance_requests'
            ]
            
            for table in expected_tables:
                assert table in tables
    
    def test_init_db_existing_database(self, temp_db):
        """Test database initialization with existing database"""
        # Database already exists, should not recreate
        with patch('builtins.print') as mock_print:
            db.init_db()
            mock_print.assert_called_with("Database already exists.")
    
    def test_admin_table_structure(self, temp_db):
        """Test admin table structure"""
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(admin)")
            columns = cursor.fetchall()
            
            # Check that key columns exist
            column_names = [col[1] for col in columns]
            expected_columns = ['id', 'username', 'password_hash', 'created_at']
            
            for col in expected_columns:
                assert col in column_names
    
    def test_properties_table_structure(self, temp_db):
        """Test properties table structure"""
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(properties)")
            columns = cursor.fetchall()
            
            # Check key columns exist
            column_names = [col[1] for col in columns]
            expected_columns = ['id', 'name', 'address', 'type', 'size', 'rent_amount', 'status']
            
            for col in expected_columns:
                assert col in column_names
    
    def test_tenants_table_structure(self, temp_db):
        """Test tenants table structure"""
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(tenants)")
            columns = cursor.fetchall()
            
            # Check key columns exist
            column_names = [col[1] for col in columns]
            expected_columns = ['id', 'property_id', 'name', 'phone', 'email', 'emergency_contact']
            
            for col in expected_columns:
                assert col in column_names
    
    def test_leases_table_structure(self, temp_db):
        """Test leases table structure"""
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(leases)")
            columns = cursor.fetchall()
            
            # Check key columns exist
            column_names = [col[1] for col in columns]
            expected_columns = ['id', 'tenant_id', 'property_id', 'start_date', 'end_date', 'rent_amount', 'status']
            
            for col in expected_columns:
                assert col in column_names
    
    def test_rent_payments_table_structure(self, temp_db):
        """Test rent_payments table structure"""
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(rent_payments)")
            columns = cursor.fetchall()
            
            # Check key columns exist
            column_names = [col[1] for col in columns]
            expected_columns = ['id', 'lease_id', 'tenant_id', 'property_id', 'month', 'amount_due', 'amount_paid', 'status']
            
            for col in expected_columns:
                assert col in column_names
    
    def test_expenses_table_structure(self, temp_db):
        """Test expenses table structure"""
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(expenses)")
            columns = cursor.fetchall()
            
            # Check key columns exist
            column_names = [col[1] for col in columns]
            expected_columns = ['id', 'property_id', 'description', 'category', 'amount', 'date']
            
            for col in expected_columns:
                assert col in column_names
    
    def test_documents_table_structure(self, temp_db):
        """Test documents table structure"""
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(documents)")
            columns = cursor.fetchall()
            
            # Check key columns exist
            column_names = [col[1] for col in columns]
            expected_columns = ['id', 'related_type', 'related_id', 'file_path', 'description']
            
            for col in expected_columns:
                assert col in column_names
    
    def test_maintenance_requests_table_structure(self, temp_db):
        """Test maintenance_requests table structure"""
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(maintenance_requests)")
            columns = cursor.fetchall()
            
            # Check key columns exist
            column_names = [col[1] for col in columns]
            expected_columns = ['id', 'property_id', 'tenant_id', 'request_date', 'description', 'status']
            
            for col in expected_columns:
                assert col in column_names
    
    def test_foreign_key_constraints(self, temp_db):
        """Test foreign key constraints"""
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            
            # Enable foreign key constraints
            cursor.execute("PRAGMA foreign_keys = ON")
            
            # Try to insert tenant with invalid property_id
            with pytest.raises(sqlite3.IntegrityError):
                cursor.execute("""
                    INSERT INTO tenants (name, property_id) 
                    VALUES ('Test Tenant', 999)
                """)
                conn.commit()
    
    def test_check_constraints(self, temp_db):
        """Test check constraints"""
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            
            # Test property status constraint
            with pytest.raises(sqlite3.IntegrityError):
                cursor.execute("""
                    INSERT INTO properties (address, rent_amount, status) 
                    VALUES ('Test Address', 1200, 'Invalid Status')
                """)
                conn.commit()
    
    def test_unique_constraints(self, temp_db):
        """Test unique constraints"""
        with sqlite3.connect(temp_db) as conn:
            cursor = conn.cursor()
            
            # Insert first admin
            cursor.execute("""
                INSERT INTO admin (username, password_hash) 
                VALUES ('admin1', 'hash1')
            """)
            conn.commit()
            
            # Try to insert duplicate username
            with pytest.raises(sqlite3.IntegrityError):
                cursor.execute("""
                    INSERT INTO admin (username, password_hash) 
                    VALUES ('admin1', 'hash2')
                """)
                conn.commit()
    
    def test_schema_file_reading(self, temp_db):
        """Test that schema file is read correctly"""
        # This test ensures the schema.sql file is properly formatted
        with open('schema.sql', 'r') as f:
            schema_content = f.read()
        
        # Check that schema contains expected table definitions
        assert 'CREATE TABLE admin' in schema_content
        assert 'CREATE TABLE properties' in schema_content
        assert 'CREATE TABLE tenants' in schema_content
        assert 'CREATE TABLE leases' in schema_content
        assert 'CREATE TABLE rent_payments' in schema_content
        assert 'CREATE TABLE expenses' in schema_content
        assert 'CREATE TABLE documents' in schema_content
        assert 'CREATE TABLE maintenance_requests' in schema_content
