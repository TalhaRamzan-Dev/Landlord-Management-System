import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
from db import DB_FILE

class PropertyManager:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.setup_ui()
        self.load_properties()
        
    def setup_ui(self):
        """Setup the property management UI"""
        # Main container
        main_container = tk.Frame(self.parent_frame, bg='white')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header with title and add button
        header_frame = tk.Frame(main_container, bg='white')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(header_frame, text="Property Management", 
                font=('Arial', 18, 'bold'), bg='white').pack(side='left')
        
        tk.Button(header_frame, text="Add New Property", command=self.add_property,
                 bg='#4CAF50', fg='white', padx=20).pack(side='right')
        
        # Filter frame
        filter_frame = tk.Frame(main_container, bg='white')
        filter_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(filter_frame, text="Filter by Status:", bg='white').pack(side='left')
        
        self.status_filter = ttk.Combobox(filter_frame, values=['All', 'Vacant', 'Occupied', 'Under Maintenance'])
        self.status_filter.set('All')
        self.status_filter.pack(side='left', padx=(10, 20))
        self.status_filter.bind('<<ComboboxSelected>>', self.filter_properties)
        
        tk.Button(filter_frame, text="Refresh", command=self.load_properties,
                 bg='#2196F3', fg='white').pack(side='right')
        
        # Properties list
        list_frame = tk.Frame(main_container, bg='white')
        list_frame.pack(fill='both', expand=True)
        
        # Treeview for properties
        columns = ('ID', 'Name', 'Address', 'Type', 'Size', 'Rent', 'Status', 'Created')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col)
            if col == 'ID':
                self.tree.column(col, width=50)
            elif col in ['Name', 'Address']:
                self.tree.column(col, width=200)
            elif col == 'Type':
                self.tree.column(col, width=100)
            elif col in ['Size', 'Rent']:
                self.tree.column(col, width=100)
            elif col == 'Status':
                self.tree.column(col, width=120)
            else:
                self.tree.column(col, width=120)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Bind double-click to view details
        self.tree.bind('<Double-1>', self.view_property_details)
        
        # Action buttons frame
        action_frame = tk.Frame(main_container, bg='white')
        action_frame.pack(fill='x', pady=(10, 0))
        
        tk.Button(action_frame, text="View Details", command=self.view_property_details,
                 bg='#2196F3', fg='white').pack(side='left', padx=(0, 10))
        tk.Button(action_frame, text="Edit Property", command=self.edit_property,
                 bg='#FF9800', fg='white').pack(side='left', padx=(0, 10))
        tk.Button(action_frame, text="Delete Property", command=self.delete_property,
                 bg='#f44336', fg='white').pack(side='left')
        
    def load_properties(self):
        """Load properties from database"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                
                # Get filter status
                status_filter = self.status_filter.get()
                
                if status_filter == 'All':
                    cursor.execute("""
                        SELECT id, name, address, type, size, rent_amount, status, created_at
                        FROM properties ORDER BY created_at DESC
                    """)
                else:
                    cursor.execute("""
                        SELECT id, name, address, type, size, rent_amount, status, created_at
                        FROM properties WHERE status = ? ORDER BY created_at DESC
                    """, (status_filter,))
                
                properties = cursor.fetchall()
                
                for prop in properties:
                    # Format the data for display
                    formatted_prop = list(prop)
                    if formatted_prop[4]:  # size
                        formatted_prop[4] = f"{formatted_prop[4]:.0f} sq ft"
                    if formatted_prop[5]:  # rent_amount
                        formatted_prop[5] = f"Rs {formatted_prop[5]:.2f}"
                    if formatted_prop[7]:  # created_at
                        formatted_prop[7] = formatted_prop[7][:10]  # Just the date part
                    
                    self.tree.insert('', 'end', values=formatted_prop)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load properties: {str(e)}")
            
    def filter_properties(self, event=None):
        """Filter properties by status"""
        self.load_properties()
        
    def add_property(self):
        """Open add property dialog"""
        PropertyDialog(self.parent_frame, self, "Add Property")
        
    def edit_property(self):
        """Edit selected property"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a property to edit")
            return
            
        item = self.tree.item(selection[0])
        property_id = item['values'][0]
        PropertyDialog(self.parent_frame, self, "Edit Property", property_id)
        
    def view_property_details(self, event=None):
        """View detailed information about selected property"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a property to view")
            return
            
        item = self.tree.item(selection[0])
        property_id = item['values'][0]
        PropertyDetailsDialog(self.parent_frame, property_id)
        
    def delete_property(self):
        """Delete selected property"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a property to delete")
            return
            
        item = self.tree.item(selection[0])
        property_id = item['values'][0]
        property_name = item['values'][1] or f"Property #{property_id}"
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete '{property_name}'?\n\n"
                              "This will also delete all associated tenants, leases, and payments."):
            try:
                with sqlite3.connect(DB_FILE) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM properties WHERE id = ?", (property_id,))
                    conn.commit()
                    
                messagebox.showinfo("Success", "Property deleted successfully")
                self.load_properties()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete property: {str(e)}")

class PropertyDialog:
    def __init__(self, parent, property_manager, title, property_id=None):
        self.parent = parent
        self.property_manager = property_manager
        self.property_id = property_id
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x600")
        self.dialog.configure(bg='white')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.setup_ui()
        
        if property_id:
            self.load_property_data()
            
    def setup_ui(self):
        """Setup the property dialog UI"""
        main_frame = tk.Frame(self.dialog, bg='white')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Form fields
        fields = [
            ("Property Name:", "name"),
            ("Address:", "address"),
            ("Property Type:", "type"),
            ("Size (sq ft):", "size"),
            ("Bedrooms:", "bedrooms"),
            ("Bathrooms:", "bathrooms"),
            ("Rent Amount (Rs):", "rent_amount"),
            ("Deposit Amount (Rs):", "deposit_amount"),
            ("Status:", "status"),
            ("Furnished:", "furnished")
        ]
        
        self.entries = {}
        
        for i, (label_text, field_name) in enumerate(fields):
            row_frame = tk.Frame(main_frame, bg='white')
            row_frame.pack(fill='x', pady=5)
            
            tk.Label(row_frame, text=label_text, bg='white', width=15, anchor='w').pack(side='left')
            
            if field_name == 'type':
                entry = ttk.Combobox(row_frame, values=['Apartment', 'House', 'Shop', 'Office', 'Other'])
                entry.pack(side='right', fill='x', expand=True, padx=(10, 0))
            elif field_name == 'status':
                entry = ttk.Combobox(row_frame, values=['Vacant', 'Occupied', 'Under Maintenance'])
                entry.pack(side='right', fill='x', expand=True, padx=(10, 0))
            elif field_name == 'furnished':
                entry = ttk.Combobox(row_frame, values=['Yes', 'No'])
                entry.pack(side='right', fill='x', expand=True, padx=(10, 0))
            else:
                entry = tk.Entry(row_frame)
                entry.pack(side='right', fill='x', expand=True, padx=(10, 0))
            
            self.entries[field_name] = entry
        
        # Set default values
        self.entries['status'].set('Vacant')
        self.entries['furnished'].set('No')
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill='x', pady=(20, 0))
        
        tk.Button(button_frame, text="Cancel", command=self.dialog.destroy,
                 bg='#f44336', fg='white', padx=20).pack(side='right', padx=(10, 0))
        tk.Button(button_frame, text="Save", command=self.save_property,
                 bg='#4CAF50', fg='white', padx=20).pack(side='right')
        
    def load_property_data(self):
        """Load existing property data for editing"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name, address, type, size, bedrooms, bathrooms, 
                           rent_amount, deposit_amount, status, furnished
                    FROM properties WHERE id = ?
                """, (self.property_id,))
                
                data = cursor.fetchone()
                if data:
                    field_names = ['name', 'address', 'type', 'size', 'bedrooms', 'bathrooms',
                                 'rent_amount', 'deposit_amount', 'status', 'furnished']
                    
                    for i, field_name in enumerate(field_names):
                        if data[i] is not None:
                            if field_name == 'furnished':
                                self.entries[field_name].set('Yes' if data[i] else 'No')
                            else:
                                self.entries[field_name].set(str(data[i]))
                                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load property data: {str(e)}")
            
    def save_property(self):
        """Save property data"""
        try:
            # Validate required fields
            if not self.entries['address'].get().strip():
                messagebox.showerror("Error", "Address is required")
                return
                
            if not self.entries['rent_amount'].get().strip():
                messagebox.showerror("Error", "Rent amount is required")
                return
            
            # Get form data
            data = {
                'name': self.entries['name'].get().strip() or None,
                'address': self.entries['address'].get().strip(),
                'type': self.entries['type'].get() or None,
                'size': float(self.entries['size'].get()) if self.entries['size'].get().strip() else None,
                'bedrooms': int(self.entries['bedrooms'].get()) if self.entries['bedrooms'].get().strip() else None,
                'bathrooms': int(self.entries['bathrooms'].get()) if self.entries['bathrooms'].get().strip() else None,
                'rent_amount': float(self.entries['rent_amount'].get()),
                'deposit_amount': float(self.entries['deposit_amount'].get()) if self.entries['deposit_amount'].get().strip() else 0,
                'status': self.entries['status'].get(),
                'furnished': self.entries['furnished'].get() == 'Yes'
            }
            
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                
                if self.property_id:
                    # Update existing property
                    cursor.execute("""
                        UPDATE properties SET 
                        name = ?, address = ?, type = ?, size = ?, bedrooms = ?, 
                        bathrooms = ?, rent_amount = ?, deposit_amount = ?, 
                        status = ?, furnished = ?
                        WHERE id = ?
                    """, (data['name'], data['address'], data['type'], data['size'],
                         data['bedrooms'], data['bathrooms'], data['rent_amount'],
                         data['deposit_amount'], data['status'], data['furnished'],
                         self.property_id))
                else:
                    # Insert new property
                    cursor.execute("""
                        INSERT INTO properties 
                        (name, address, type, size, bedrooms, bathrooms, 
                         rent_amount, deposit_amount, status, furnished)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (data['name'], data['address'], data['type'], data['size'],
                         data['bedrooms'], data['bathrooms'], data['rent_amount'],
                         data['deposit_amount'], data['status'], data['furnished']))
                
                conn.commit()
                
            messagebox.showinfo("Success", "Property saved successfully")
            self.dialog.destroy()
            self.property_manager.load_properties()
            
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numeric values for size, bedrooms, bathrooms, and amounts")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save property: {str(e)}")

class PropertyDetailsDialog:
    def __init__(self, parent, property_id):
        self.property_id = property_id
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Property Details")
        self.dialog.geometry("800x600")
        self.dialog.configure(bg='white')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.setup_ui()
        self.load_property_details()
        
    def setup_ui(self):
        """Setup the property details UI"""
        main_frame = tk.Frame(self.dialog, bg='white')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Property info frame
        info_frame = tk.LabelFrame(main_frame, text="Property Information", bg='white')
        info_frame.pack(fill='x', pady=(0, 20))
        
        self.info_text = tk.Text(info_frame, height=8, wrap='word', state='disabled')
        self.info_text.pack(fill='x', padx=10, pady=10)
        
        # Tenants frame
        tenants_frame = tk.LabelFrame(main_frame, text="Current Tenants", bg='white')
        tenants_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Tenants treeview
        tenant_columns = ('Name', 'Phone', 'Email', 'Emergency Contact')
        self.tenant_tree = ttk.Treeview(tenants_frame, columns=tenant_columns, show='headings', height=6)
        
        for col in tenant_columns:
            self.tenant_tree.heading(col, text=col)
            self.tenant_tree.column(col, width=150)
        
        self.tenant_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Close button
        tk.Button(main_frame, text="Close", command=self.dialog.destroy,
                 bg='#2196F3', fg='white', padx=20).pack(pady=10)
        
    def load_property_details(self):
        """Load property details and tenants"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                
                # Get property details
                cursor.execute("""
                    SELECT name, address, type, size, bedrooms, bathrooms, 
                           rent_amount, deposit_amount, status, furnished, created_at
                    FROM properties WHERE id = ?
                """, (self.property_id,))
                
                prop_data = cursor.fetchone()
                if prop_data:
                    info_text = f"""
Property ID: {self.property_id}
Name: {prop_data[0] or 'N/A'}
Address: {prop_data[1]}
Type: {prop_data[2] or 'N/A'}
Size: {prop_data[3] or 'N/A'} sq ft
Bedrooms: {prop_data[4] or 'N/A'}
Bathrooms: {prop_data[5] or 'N/A'}
Rent Amount: Rs {prop_data[6]:.2f}
Deposit Amount: Rs {prop_data[7]:.2f}
Status: {prop_data[8]}
Furnished: {'Yes' if prop_data[9] else 'No'}
Created: {prop_data[10][:10] if prop_data[10] else 'N/A'}
                    """.strip()
                    
                    self.info_text.config(state='normal')
                    self.info_text.delete(1.0, tk.END)
                    self.info_text.insert(1.0, info_text)
                    self.info_text.config(state='disabled')
                
                # Get current tenants
                cursor.execute("""
                    SELECT name, phone, email, emergency_contact
                    FROM tenants WHERE property_id = ?
                """, (self.property_id,))
                
                tenants = cursor.fetchall()
                
                for tenant in tenants:
                    self.tenant_tree.insert('', 'end', values=tenant)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load property details: {str(e)}")
