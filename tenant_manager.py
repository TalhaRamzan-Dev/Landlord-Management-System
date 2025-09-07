import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
from db import DB_FILE

class TenantManager:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.setup_ui()
        self.load_tenants()
        
    def setup_ui(self):
        """Setup the tenant management UI"""
        # Main container
        main_container = tk.Frame(self.parent_frame, bg='white')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header with title and add button
        header_frame = tk.Frame(main_container, bg='white')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(header_frame, text="Tenant Management", 
                font=('Arial', 18, 'bold'), bg='white').pack(side='left')
        
        tk.Button(header_frame, text="Add New Tenant", command=self.add_tenant,
                 bg='#4CAF50', fg='white', padx=20).pack(side='right')
        
        # Filter frame
        filter_frame = tk.Frame(main_container, bg='white')
        filter_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(filter_frame, text="Filter by Property:", bg='white').pack(side='left')
        
        self.property_filter = ttk.Combobox(filter_frame, width=30)
        self.property_filter.pack(side='left', padx=(10, 20))
        self.property_filter.bind('<<ComboboxSelected>>', self.filter_tenants)
        
        tk.Button(filter_frame, text="All Properties", command=self.load_all_tenants,
                 bg='#2196F3', fg='white').pack(side='left', padx=(0, 10))
        tk.Button(filter_frame, text="Refresh", command=self.load_tenants,
                 bg='#2196F3', fg='white').pack(side='right')
        
        # Load property list for filter
        self.load_property_list()
        
        # Tenants list
        list_frame = tk.Frame(main_container, bg='white')
        list_frame.pack(fill='both', expand=True)
        
        # Treeview for tenants
        columns = ('ID', 'Name', 'Property', 'Phone', 'Email', 'Emergency Contact', 'Created')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col)
            if col == 'ID':
                self.tree.column(col, width=50)
            elif col in ['Name', 'Property']:
                self.tree.column(col, width=150)
            elif col in ['Phone', 'Email']:
                self.tree.column(col, width=120)
            elif col == 'Emergency Contact':
                self.tree.column(col, width=150)
            else:
                self.tree.column(col, width=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Bind double-click to view details
        self.tree.bind('<Double-1>', self.view_tenant_details)
        
        # Action buttons frame
        action_frame = tk.Frame(main_container, bg='white')
        action_frame.pack(fill='x', pady=(10, 0))
        
        tk.Button(action_frame, text="View Details", command=self.view_tenant_details,
                 bg='#2196F3', fg='white').pack(side='left', padx=(0, 10))
        tk.Button(action_frame, text="Edit Tenant", command=self.edit_tenant,
                 bg='#FF9800', fg='white').pack(side='left', padx=(0, 10))
        tk.Button(action_frame, text="Remove Tenant", command=self.remove_tenant,
                 bg='#f44336', fg='white').pack(side='left')
        
    def load_property_list(self):
        """Load property list for filter dropdown"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name, address FROM properties ORDER BY name")
                properties = cursor.fetchall()
                
                property_list = ['All Properties']
                for prop in properties:
                    prop_name = prop[1] if prop[1] else f"Property #{prop[0]}"
                    property_list.append(f"{prop_name} - {prop[2]}")
                
                self.property_filter['values'] = property_list
                self.property_filter.set('All Properties')
                
        except Exception as e:
            print(f"Error loading property list: {e}")
            
    def load_tenants(self):
        """Load tenants from database"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT t.id, t.name, 
                           COALESCE(p.name, 'Property #' || p.id) as property_name,
                           t.phone, t.email, t.emergency_contact, t.created_at
                    FROM tenants t
                    LEFT JOIN properties p ON t.property_id = p.id
                    ORDER BY t.created_at DESC
                """)
                
                tenants = cursor.fetchall()
                
                for tenant in tenants:
                    # Format the data for display
                    formatted_tenant = list(tenant)
                    if formatted_tenant[6]:  # created_at
                        formatted_tenant[6] = formatted_tenant[6][:10]  # Just the date part
                    
                    self.tree.insert('', 'end', values=formatted_tenant)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tenants: {str(e)}")
            
    def load_all_tenants(self):
        """Load all tenants (clear filter)"""
        self.property_filter.set('All Properties')
        self.load_tenants()
        
    def filter_tenants(self, event=None):
        """Filter tenants by property"""
        selected = self.property_filter.get()
        if selected == 'All Properties':
            self.load_tenants()
            return
            
        # Extract property ID from selection
        try:
            property_name = selected.split(' - ')[0]
            
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                
                # Find property ID
                if property_name.startswith('Property #'):
                    property_id = int(property_name.split('#')[1])
                else:
                    cursor.execute("SELECT id FROM properties WHERE name = ?", (property_name,))
                    result = cursor.fetchone()
                    if not result:
                        return
                    property_id = result[0]
                
                # Clear existing items
                for item in self.tree.get_children():
                    self.tree.delete(item)
                
                # Load filtered tenants
                cursor.execute("""
                    SELECT t.id, t.name, 
                           COALESCE(p.name, 'Property #' || p.id) as property_name,
                           t.phone, t.email, t.emergency_contact, t.created_at
                    FROM tenants t
                    LEFT JOIN properties p ON t.property_id = p.id
                    WHERE t.property_id = ?
                    ORDER BY t.created_at DESC
                """, (property_id,))
                
                tenants = cursor.fetchall()
                
                for tenant in tenants:
                    formatted_tenant = list(tenant)
                    if formatted_tenant[6]:  # created_at
                        formatted_tenant[6] = formatted_tenant[6][:10]
                    self.tree.insert('', 'end', values=formatted_tenant)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to filter tenants: {str(e)}")
        
    def add_tenant(self):
        """Open add tenant dialog"""
        TenantDialog(self.parent_frame, self, "Add Tenant")
        
    def edit_tenant(self):
        """Edit selected tenant"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a tenant to edit")
            return
            
        item = self.tree.item(selection[0])
        tenant_id = item['values'][0]
        TenantDialog(self.parent_frame, self, "Edit Tenant", tenant_id)
        
    def view_tenant_details(self, event=None):
        """View detailed information about selected tenant"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a tenant to view")
            return
            
        item = self.tree.item(selection[0])
        tenant_id = item['values'][0]
        TenantDetailsDialog(self.parent_frame, tenant_id)
        
    def remove_tenant(self):
        """Remove selected tenant"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a tenant to remove")
            return
            
        item = self.tree.item(selection[0])
        tenant_id = item['values'][0]
        tenant_name = item['values'][1]
        
        if messagebox.askyesno("Confirm Remove", 
                              f"Are you sure you want to remove '{tenant_name}'?\n\n"
                              "This will also remove all associated leases and payments."):
            try:
                with sqlite3.connect(DB_FILE) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM tenants WHERE id = ?", (tenant_id,))
                    conn.commit()
                    
                messagebox.showinfo("Success", "Tenant removed successfully")
                self.load_tenants()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove tenant: {str(e)}")

class TenantDialog:
    def __init__(self, parent, tenant_manager, title, tenant_id=None):
        self.parent = parent
        self.tenant_manager = tenant_manager
        self.tenant_id = tenant_id
        
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
        
        if tenant_id:
            self.load_tenant_data()
            
    def setup_ui(self):
        """Setup the tenant dialog UI"""
        main_frame = tk.Frame(self.dialog, bg='white')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Form fields
        fields = [
            ("Tenant Name:", "name"),
            ("Property:", "property_id"),
            ("Phone:", "phone"),
            ("Email:", "email"),
            ("National ID:", "national_id"),
            ("Emergency Contact:", "emergency_contact"),
            ("Notes:", "notes")
        ]
        
        self.entries = {}
        
        for i, (label_text, field_name) in enumerate(fields):
            row_frame = tk.Frame(main_frame, bg='white')
            row_frame.pack(fill='x', pady=5)
            
            tk.Label(row_frame, text=label_text, bg='white', width=15, anchor='w').pack(side='left')
            
            if field_name == 'property_id':
                entry = ttk.Combobox(row_frame, width=30)
                entry.pack(side='right', fill='x', expand=True, padx=(10, 0))
                self.load_property_options(entry)
            elif field_name == 'notes':
                entry = tk.Text(row_frame, height=3, wrap='word')
                entry.pack(side='right', fill='x', expand=True, padx=(10, 0))
            else:
                entry = tk.Entry(row_frame)
                entry.pack(side='right', fill='x', expand=True, padx=(10, 0))
            
            self.entries[field_name] = entry
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill='x', pady=(20, 0))
        
        tk.Button(button_frame, text="Cancel", command=self.dialog.destroy,
                 bg='#f44336', fg='white', padx=20).pack(side='right', padx=(10, 0))
        tk.Button(button_frame, text="Save", command=self.save_tenant,
                 bg='#4CAF50', fg='white', padx=20).pack(side='right')
        
    def load_property_options(self, combobox):
        """Load property options for dropdown"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name, address FROM properties ORDER BY name")
                properties = cursor.fetchall()
                
                property_options = []
                for prop in properties:
                    prop_name = prop[1] if prop[1] else f"Property #{prop[0]}"
                    property_options.append(f"{prop_name} - {prop[2]}")
                
                combobox['values'] = property_options
                
        except Exception as e:
            print(f"Error loading property options: {e}")
            
    def load_tenant_data(self):
        """Load existing tenant data for editing"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT t.name, t.property_id, t.phone, t.email, t.national_id, 
                           t.emergency_contact, t.notes
                    FROM tenants t WHERE t.id = ?
                """, (self.tenant_id,))
                
                data = cursor.fetchone()
                if data:
                    field_names = ['name', 'property_id', 'phone', 'email', 'national_id',
                                 'emergency_contact', 'notes']
                    
                    for i, field_name in enumerate(field_names):
                        if data[i] is not None:
                            if field_name == 'notes':
                                self.entries[field_name].insert(1.0, str(data[i]))
                            else:
                                self.entries[field_name].set(str(data[i]))
                                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tenant data: {str(e)}")
            
    def save_tenant(self):
        """Save tenant data"""
        try:
            # Validate required fields
            if not self.entries['name'].get().strip():
                messagebox.showerror("Error", "Tenant name is required")
                return
                
            # Get property ID
            property_selection = self.entries['property_id'].get()
            if not property_selection:
                messagebox.showerror("Error", "Please select a property")
                return
                
            # Extract property ID from selection
            property_name = property_selection.split(' - ')[0]
            property_id = None
            
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                
                if property_name.startswith('Property #'):
                    property_id = int(property_name.split('#')[1])
                else:
                    cursor.execute("SELECT id FROM properties WHERE name = ?", (property_name,))
                    result = cursor.fetchone()
                    if result:
                        property_id = result[0]
                
                if not property_id:
                    messagebox.showerror("Error", "Invalid property selection")
                    return
            
            # Get form data
            data = {
                'name': self.entries['name'].get().strip(),
                'property_id': property_id,
                'phone': self.entries['phone'].get().strip() or None,
                'email': self.entries['email'].get().strip() or None,
                'national_id': self.entries['national_id'].get().strip() or None,
                'emergency_contact': self.entries['emergency_contact'].get().strip() or None,
                'notes': self.entries['notes'].get(1.0, tk.END).strip() or None
            }
            
            if self.tenant_id:
                # Update existing tenant
                cursor.execute("""
                    UPDATE tenants SET 
                    name = ?, property_id = ?, phone = ?, email = ?, 
                    national_id = ?, emergency_contact = ?, notes = ?
                    WHERE id = ?
                """, (data['name'], data['property_id'], data['phone'], data['email'],
                     data['national_id'], data['emergency_contact'], data['notes'],
                     self.tenant_id))
            else:
                # Insert new tenant
                cursor.execute("""
                    INSERT INTO tenants 
                    (name, property_id, phone, email, national_id, emergency_contact, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (data['name'], data['property_id'], data['phone'], data['email'],
                     data['national_id'], data['emergency_contact'], data['notes']))
            
            conn.commit()
            
            messagebox.showinfo("Success", "Tenant saved successfully")
            self.dialog.destroy()
            self.tenant_manager.load_tenants()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save tenant: {str(e)}")

class TenantDetailsDialog:
    def __init__(self, parent, tenant_id):
        self.tenant_id = tenant_id
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Tenant Details")
        self.dialog.geometry("800x600")
        self.dialog.configure(bg='white')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.setup_ui()
        self.load_tenant_details()
        
    def setup_ui(self):
        """Setup the tenant details UI"""
        main_frame = tk.Frame(self.dialog, bg='white')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Tenant info frame
        info_frame = tk.LabelFrame(main_frame, text="Tenant Information", bg='white')
        info_frame.pack(fill='x', pady=(0, 20))
        
        self.info_text = tk.Text(info_frame, height=8, wrap='word', state='disabled')
        self.info_text.pack(fill='x', padx=10, pady=10)
        
        # Leases frame
        leases_frame = tk.LabelFrame(main_frame, text="Lease History", bg='white')
        leases_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Leases treeview
        lease_columns = ('Start Date', 'End Date', 'Rent Amount', 'Status')
        self.lease_tree = ttk.Treeview(leases_frame, columns=lease_columns, show='headings', height=6)
        
        for col in lease_columns:
            self.lease_tree.heading(col, text=col)
            self.lease_tree.column(col, width=150)
        
        self.lease_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Close button
        tk.Button(main_frame, text="Close", command=self.dialog.destroy,
                 bg='#2196F3', fg='white', padx=20).pack(pady=10)
        
    def load_tenant_details(self):
        """Load tenant details and lease history"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                
                # Get tenant details
                cursor.execute("""
                    SELECT t.name, t.phone, t.email, t.national_id, 
                           t.emergency_contact, t.notes, t.created_at,
                           COALESCE(p.name, 'Property #' || p.id) as property_name,
                           p.address
                    FROM tenants t
                    LEFT JOIN properties p ON t.property_id = p.id
                    WHERE t.id = ?
                """, (self.tenant_id,))
                
                tenant_data = cursor.fetchone()
                if tenant_data:
                    info_text = f"""
Tenant ID: {self.tenant_id}
Name: {tenant_data[0]}
Phone: {tenant_data[1] or 'N/A'}
Email: {tenant_data[2] or 'N/A'}
National ID: {tenant_data[3] or 'N/A'}
Emergency Contact: {tenant_data[4] or 'N/A'}
Property: {tenant_data[7] or 'N/A'}
Property Address: {tenant_data[8] or 'N/A'}
Created: {tenant_data[6][:10] if tenant_data[6] else 'N/A'}
Notes: {tenant_data[5] or 'N/A'}
                    """.strip()
                    
                    self.info_text.config(state='normal')
                    self.info_text.delete(1.0, tk.END)
                    self.info_text.insert(1.0, info_text)
                    self.info_text.config(state='disabled')
                
                # Get lease history
                cursor.execute("""
                    SELECT start_date, end_date, rent_amount, status
                    FROM leases WHERE tenant_id = ?
                    ORDER BY start_date DESC
                """, (self.tenant_id,))
                
                leases = cursor.fetchall()
                
                for lease in leases:
                    formatted_lease = list(lease)
                    if formatted_lease[1]:  # end_date
                        formatted_lease[1] = formatted_lease[1][:10]
                    if formatted_lease[0]:  # start_date
                        formatted_lease[0] = formatted_lease[0][:10]
                    if formatted_lease[2]:  # rent_amount
                        formatted_lease[2] = f"RS{formatted_lease[2]:.2f}"
                    
                    self.lease_tree.insert('', 'end', values=formatted_lease)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tenant details: {str(e)}")
