import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, date
from db import DB_FILE

class MaintenanceManager:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.setup_ui()
        self.load_requests()
        
    def setup_ui(self):
        """Setup the maintenance management UI"""
        # Main container
        main_container = tk.Frame(self.parent_frame, bg='white')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header with title and add button
        header_frame = tk.Frame(main_container, bg='white')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(header_frame, text="Maintenance Request Management", 
                font=('Arial', 18, 'bold'), bg='white').pack(side='left')
        
        tk.Button(header_frame, text="Add New Request", command=self.add_request,
                 bg='#4CAF50', fg='white', padx=20).pack(side='right')
        
        # Filter frame
        filter_frame = tk.Frame(main_container, bg='white')
        filter_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(filter_frame, text="Filter by Status:", bg='white').pack(side='left')
        
        self.status_filter = ttk.Combobox(filter_frame, values=['All', 'Open', 'In Progress', 'Completed', 'Cancelled'])
        self.status_filter.set('All')
        self.status_filter.pack(side='left', padx=(10, 20))
        self.status_filter.bind('<<ComboboxSelected>>', self.filter_requests)
        
        tk.Label(filter_frame, text="Property:", bg='white').pack(side='left')
        
        self.property_filter = ttk.Combobox(filter_frame, width=30)
        self.property_filter.pack(side='left', padx=(10, 20))
        self.property_filter.bind('<<ComboboxSelected>>', self.filter_requests)
        
        tk.Button(filter_frame, text="All Properties", command=self.load_all_requests,
                 bg='#2196F3', fg='white').pack(side='left', padx=(0, 10))
        tk.Button(filter_frame, text="Refresh", command=self.load_requests,
                 bg='#2196F3', fg='white').pack(side='right')
        
        # Load property list for filter
        self.load_property_list()
        
        # Requests list
        list_frame = tk.Frame(main_container, bg='white')
        list_frame.pack(fill='both', expand=True)
        
        # Treeview for requests
        columns = ('ID', 'Property', 'Tenant', 'Request Date', 'Description', 'Status', 'Est. Cost', 'Actual Cost')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col)
            if col == 'ID':
                self.tree.column(col, width=50)
            elif col in ['Property', 'Tenant']:
                self.tree.column(col, width=120)
            elif col == 'Request Date':
                self.tree.column(col, width=100)
            elif col == 'Description':
                self.tree.column(col, width=200)
            elif col == 'Status':
                self.tree.column(col, width=100)
            elif col in ['Est. Cost', 'Actual Cost']:
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
        self.tree.bind('<Double-1>', self.view_request_details)
        
        # Action buttons frame
        action_frame = tk.Frame(main_container, bg='white')
        action_frame.pack(fill='x', pady=(10, 0))
        
        tk.Button(action_frame, text="View Details", command=self.view_request_details,
                 bg='#2196F3', fg='white').pack(side='left', padx=(0, 10))
        tk.Button(action_frame, text="Edit Request", command=self.edit_request,
                 bg='#FF9800', fg='white').pack(side='left', padx=(0, 10))
        tk.Button(action_frame, text="Update Status", command=self.update_status,
                 bg='#9C27B0', fg='white').pack(side='left', padx=(0, 10))
        tk.Button(action_frame, text="Delete Request", command=self.delete_request,
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
            
    def load_requests(self):
        """Load maintenance requests from database"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT mr.id, 
                           COALESCE(p.name, 'Property #' || p.id) as property_name,
                           COALESCE(t.name, 'N/A') as tenant_name,
                           mr.request_date, mr.description, mr.status, 
                           mr.cost_estimate, mr.actual_cost
                    FROM maintenance_requests mr
                    JOIN properties p ON mr.property_id = p.id
                    LEFT JOIN tenants t ON mr.tenant_id = t.id
                    ORDER BY mr.request_date DESC
                """)
                
                requests = cursor.fetchall()
                
                for request in requests:
                    # Format the data for display
                    formatted_request = list(request)
                    if formatted_request[3]:  # request_date
                        formatted_request[3] = formatted_request[3][:10]
                    if formatted_request[6]:  # cost_estimate
                        formatted_request[6] = f"Rs {formatted_request[6]:.2f}"
                    if formatted_request[7]:  # actual_cost
                        formatted_request[7] = f"Rs {formatted_request[7]:.2f}"
                    
                    self.tree.insert('', 'end', values=formatted_request)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load maintenance requests: {str(e)}")
            
    def load_all_requests(self):
        """Load all requests (clear filters)"""
        self.property_filter.set('All Properties')
        self.status_filter.set('All')
        self.load_requests()
        
    def filter_requests(self, event=None):
        """Filter requests by property and status"""
        selected_property = self.property_filter.get()
        selected_status = self.status_filter.get()
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                
                # Build query based on filters
                query = """
                    SELECT mr.id, 
                           COALESCE(p.name, 'Property #' || p.id) as property_name,
                           COALESCE(t.name, 'N/A') as tenant_name,
                           mr.request_date, mr.description, mr.status, 
                           mr.cost_estimate, mr.actual_cost
                    FROM maintenance_requests mr
                    JOIN properties p ON mr.property_id = p.id
                    LEFT JOIN tenants t ON mr.tenant_id = t.id
                    WHERE 1=1
                """
                params = []
                
                if selected_property != 'All Properties':
                    property_name = selected_property.split(' - ')[0]
                    if property_name.startswith('Property #'):
                        property_id = int(property_name.split('#')[1])
                        query += " AND mr.property_id = ?"
                        params.append(property_id)
                    else:
                        query += " AND p.name = ?"
                        params.append(property_name)
                
                if selected_status != 'All':
                    query += " AND mr.status = ?"
                    params.append(selected_status)
                
                query += " ORDER BY mr.request_date DESC"
                
                cursor.execute(query, params)
                requests = cursor.fetchall()
                
                for request in requests:
                    formatted_request = list(request)
                    if formatted_request[3]:  # request_date
                        formatted_request[3] = formatted_request[3][:10]
                    if formatted_request[6]:  # cost_estimate
                        formatted_request[6] = f"Rs {formatted_request[6]:.2f}"
                    if formatted_request[7]:  # actual_cost
                        formatted_request[7] = f"Rs {formatted_request[7]:.2f}"
                    
                    self.tree.insert('', 'end', values=formatted_request)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to filter requests: {str(e)}")
        
    def add_request(self):
        """Open add request dialog"""
        MaintenanceDialog(self.parent_frame, self, "Add Maintenance Request")
        
    def edit_request(self):
        """Edit selected request"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a request to edit")
            return
            
        item = self.tree.item(selection[0])
        request_id = item['values'][0]
        MaintenanceDialog(self.parent_frame, self, "Edit Maintenance Request", request_id)
        
    def view_request_details(self, event=None):
        """View detailed information about selected request"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a request to view")
            return
            
        item = self.tree.item(selection[0])
        request_id = item['values'][0]
        MaintenanceDetailsDialog(self.parent_frame, request_id)
        
    def update_status(self):
        """Update status of selected request"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a request to update")
            return
            
        item = self.tree.item(selection[0])
        request_id = item['values'][0]
        current_status = item['values'][5]
        
        StatusUpdateDialog(self.parent_frame, self, request_id, current_status)
        
    def delete_request(self):
        """Delete selected request"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a request to delete")
            return
            
        item = self.tree.item(selection[0])
        request_id = item['values'][0]
        description = item['values'][4]
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete the request '{description}'?"):
            try:
                with sqlite3.connect(DB_FILE) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM maintenance_requests WHERE id = ?", (request_id,))
                    conn.commit()
                    
                messagebox.showinfo("Success", "Maintenance request deleted successfully")
                self.load_requests()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete request: {str(e)}")

class MaintenanceDialog:
    def __init__(self, parent, maintenance_manager, title, request_id=None):
        self.parent = parent
        self.maintenance_manager = maintenance_manager
        self.request_id = request_id
        
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
        
        if request_id:
            self.load_request_data()
            
    def setup_ui(self):
        """Setup the maintenance dialog UI"""
        main_frame = tk.Frame(self.dialog, bg='white')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Form fields
        fields = [
            ("Property:", "property_id"),
            ("Tenant:", "tenant_id"),
            ("Request Date:", "request_date"),
            ("Description:", "description"),
            ("Status:", "status"),
            ("Cost Estimate (Rs):", "cost_estimate"),
            ("Actual Cost (Rs):", "actual_cost"),
            ("Completed Date:", "completed_date"),
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
            elif field_name == 'tenant_id':
                entry = ttk.Combobox(row_frame, width=30)
                entry.pack(side='right', fill='x', expand=True, padx=(10, 0))
                self.load_tenant_options(entry)
            elif field_name == 'status':
                entry = ttk.Combobox(row_frame, values=['Open', 'In Progress', 'Completed', 'Cancelled'])
                entry.set('Open')
                entry.pack(side='right', fill='x', expand=True, padx=(10, 0))
            elif field_name in ['request_date', 'completed_date']:
                entry = tk.Entry(row_frame)
                entry.pack(side='right', fill='x', expand=True, padx=(10, 0))
                if field_name == 'request_date':
                    entry.insert(0, date.today().strftime("%Y-%m-%d"))
                else:
                    entry.insert(0, "YYYY-MM-DD")
            elif field_name == 'description':
                entry = tk.Text(row_frame, height=3, wrap='word')
                entry.pack(side='right', fill='x', expand=True, padx=(10, 0))
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
        tk.Button(button_frame, text="Save", command=self.save_request,
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
            
    def load_tenant_options(self, combobox):
        """Load tenant options for dropdown"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name FROM tenants ORDER BY name")
                tenants = cursor.fetchall()
                
                tenant_options = ['No Tenant']
                for tenant in tenants:
                    tenant_options.append(f"{tenant[1]} (ID: {tenant[0]})")
                
                combobox['values'] = tenant_options
                combobox.set('No Tenant')
                
        except Exception as e:
            print(f"Error loading tenant options: {e}")
            
    def load_request_data(self):
        """Load existing request data for editing"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT mr.property_id, mr.tenant_id, mr.request_date, mr.description, 
                           mr.status, mr.cost_estimate, mr.actual_cost, mr.completed_date, mr.notes
                    FROM maintenance_requests mr WHERE mr.id = ?
                """, (self.request_id,))
                
                data = cursor.fetchone()
                if data:
                    field_names = ['property_id', 'tenant_id', 'request_date', 'description',
                                 'status', 'cost_estimate', 'actual_cost', 'completed_date', 'notes']
                    
                    for i, field_name in enumerate(field_names):
                        if data[i] is not None:
                            if field_name == 'property_id':
                                # Load the display value for combobox
                                cursor.execute("SELECT name, address FROM properties WHERE id = ?", (data[i],))
                                prop_data = cursor.fetchone()
                                if prop_data:
                                    prop_name = prop_data[0] if prop_data[0] else f"Property #{data[i]}"
                                    self.entries[field_name].set(f"{prop_name} - {prop_data[1]}")
                            elif field_name == 'tenant_id':
                                if data[i]:
                                    cursor.execute("SELECT name FROM tenants WHERE id = ?", (data[i],))
                                    tenant_name = cursor.fetchone()[0]
                                    self.entries[field_name].set(f"{tenant_name} (ID: {data[i]})")
                                else:
                                    self.entries[field_name].set('No Tenant')
                            elif field_name in ['description', 'notes']:
                                self.entries[field_name].insert(1.0, str(data[i]))
                            else:
                                self.entries[field_name].set(str(data[i]))
                                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load request data: {str(e)}")
            
    def save_request(self):
        """Save request data"""
        try:
            # Validate required fields
            if not self.entries['property_id'].get().strip():
                messagebox.showerror("Error", "Please select a property")
                return
                
            if not self.entries['description'].get(1.0, tk.END).strip():
                messagebox.showerror("Error", "Description is required")
                return
            
            # Extract property ID from selection
            property_selection = self.entries['property_id'].get()
            property_name = property_selection.split(' - ')[0]
            property_id = None
            
            # Extract tenant ID from selection
            tenant_selection = self.entries['tenant_id'].get()
            tenant_id = None
            if tenant_selection != 'No Tenant':
                tenant_id = int(tenant_selection.split('(ID: ')[1].rstrip(')'))
            
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
                'property_id': property_id,
                'tenant_id': tenant_id,
                'request_date': self.entries['request_date'].get().strip() or date.today().strftime("%Y-%m-%d"),
                'description': self.entries['description'].get(1.0, tk.END).strip(),
                'status': self.entries['status'].get(),
                'cost_estimate': float(self.entries['cost_estimate'].get()) if self.entries['cost_estimate'].get().strip() else None,
                'actual_cost': float(self.entries['actual_cost'].get()) if self.entries['actual_cost'].get().strip() else None,
                'completed_date': self.entries['completed_date'].get().strip() or None,
                'notes': self.entries['notes'].get(1.0, tk.END).strip() or None
            }
            
            if self.request_id:
                # Update existing request
                cursor.execute("""
                    UPDATE maintenance_requests SET 
                    property_id = ?, tenant_id = ?, request_date = ?, description = ?, 
                    status = ?, cost_estimate = ?, actual_cost = ?, completed_date = ?, notes = ?
                    WHERE id = ?
                """, (data['property_id'], data['tenant_id'], data['request_date'], data['description'],
                     data['status'], data['cost_estimate'], data['actual_cost'], data['completed_date'],
                     data['notes'], self.request_id))
            else:
                # Insert new request
                cursor.execute("""
                    INSERT INTO maintenance_requests 
                    (property_id, tenant_id, request_date, description, status, 
                     cost_estimate, actual_cost, completed_date, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (data['property_id'], data['tenant_id'], data['request_date'], data['description'],
                     data['status'], data['cost_estimate'], data['actual_cost'], data['completed_date'],
                     data['notes']))
            
            conn.commit()
            
            messagebox.showinfo("Success", "Maintenance request saved successfully")
            self.dialog.destroy()
            self.maintenance_manager.load_requests()
            
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numeric values for costs")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save request: {str(e)}")

class StatusUpdateDialog:
    def __init__(self, parent, maintenance_manager, request_id, current_status):
        self.parent = parent
        self.maintenance_manager = maintenance_manager
        self.request_id = request_id
        self.current_status = current_status
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Update Status")
        self.dialog.geometry("400x300")
        self.dialog.configure(bg='white')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 100, parent.winfo_rooty() + 100))
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the status update dialog UI"""
        main_frame = tk.Frame(self.dialog, bg='white')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(main_frame, text="Update Maintenance Request Status", 
                font=('Arial', 14, 'bold'), bg='white').pack(pady=(0, 20))
        
        tk.Label(main_frame, text=f"Current Status: {self.current_status}", 
                bg='white').pack(pady=(0, 10))
        
        tk.Label(main_frame, text="New Status:", bg='white').pack(anchor='w')
        
        self.status_var = tk.StringVar(value=self.current_status)
        status_frame = tk.Frame(main_frame, bg='white')
        status_frame.pack(fill='x', pady=5)
        
        statuses = ['Open', 'In Progress', 'Completed', 'Cancelled']
        for status in statuses:
            tk.Radiobutton(status_frame, text=status, variable=self.status_var, 
                          value=status, bg='white').pack(anchor='w')
        
        # Additional fields for completed status
        self.cost_frame = tk.Frame(main_frame, bg='white')
        self.cost_frame.pack(fill='x', pady=10)
        
        tk.Label(self.cost_frame, text="Actual Cost (Rs):", bg='white').pack(anchor='w')
        self.actual_cost_entry = tk.Entry(self.cost_frame)
        self.actual_cost_entry.pack(fill='x', pady=5)
        
        tk.Label(self.cost_frame, text="Completed Date:", bg='white').pack(anchor='w')
        self.completed_date_entry = tk.Entry(self.cost_frame)
        self.completed_date_entry.pack(fill='x', pady=5)
        self.completed_date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        
        # Bind status change to show/hide additional fields
        self.status_var.trace('w', self.on_status_change)
        self.on_status_change()
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill='x', pady=(20, 0))
        
        tk.Button(button_frame, text="Cancel", command=self.dialog.destroy,
                 bg='#f44336', fg='white', padx=20).pack(side='right', padx=(10, 0))
        tk.Button(button_frame, text="Update", command=self.update_status,
                 bg='#4CAF50', fg='white', padx=20).pack(side='right')
        
    def on_status_change(self, *args):
        """Show/hide additional fields based on status"""
        if self.status_var.get() == 'Completed':
            self.cost_frame.pack(fill='x', pady=10)
        else:
            self.cost_frame.pack_forget()
            
    def update_status(self):
        """Update the request status"""
        try:
            new_status = self.status_var.get()
            actual_cost = None
            completed_date = None
            
            if new_status == 'Completed':
                if self.actual_cost_entry.get().strip():
                    actual_cost = float(self.actual_cost_entry.get())
                completed_date = self.completed_date_entry.get().strip() or date.today().strftime("%Y-%m-%d")
            
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE maintenance_requests 
                    SET status = ?, actual_cost = ?, completed_date = ?
                    WHERE id = ?
                """, (new_status, actual_cost, completed_date, self.request_id))
                conn.commit()
            
            messagebox.showinfo("Success", "Status updated successfully")
            self.dialog.destroy()
            self.maintenance_manager.load_requests()
            
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numeric value for actual cost")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update status: {str(e)}")

class MaintenanceDetailsDialog:
    def __init__(self, parent, request_id):
        self.request_id = request_id
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Maintenance Request Details")
        self.dialog.geometry("800x600")
        self.dialog.configure(bg='white')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.setup_ui()
        self.load_request_details()
        
    def setup_ui(self):
        """Setup the request details UI"""
        main_frame = tk.Frame(self.dialog, bg='white')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Request info frame
        info_frame = tk.LabelFrame(main_frame, text="Request Information", bg='white')
        info_frame.pack(fill='x', pady=(0, 20))
        
        self.info_text = tk.Text(info_frame, height=10, wrap='word', state='disabled')
        self.info_text.pack(fill='x', padx=10, pady=10)
        
        # Close button
        tk.Button(main_frame, text="Close", command=self.dialog.destroy,
                 bg='#2196F3', fg='white', padx=20).pack(pady=10)
        
    def load_request_details(self):
        """Load request details"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                
                # Get request details
                cursor.execute("""
                    SELECT mr.request_date, mr.description, mr.status, mr.cost_estimate, 
                           mr.actual_cost, mr.completed_date, mr.notes,
                           COALESCE(p.name, 'Property #' || p.id) as property_name,
                           p.address, COALESCE(t.name, 'N/A') as tenant_name
                    FROM maintenance_requests mr
                    JOIN properties p ON mr.property_id = p.id
                    LEFT JOIN tenants t ON mr.tenant_id = t.id
                    WHERE mr.id = ?
                """, (self.request_id,))
                
                request_data = cursor.fetchone()
                if request_data:
                    info_text = f"""
Request ID: {self.request_id}
Property: {request_data[7]}
Property Address: {request_data[8]}
Tenant: {request_data[9]}
Request Date: {request_data[0][:10] if request_data[0] else 'N/A'}
Status: {request_data[2]}
Description: {request_data[1]}
Cost Estimate: Rs {request_data[3]:.2f if request_data[3] else 'N/A'}
Actual Cost: Rs {request_data[4]:.2f if request_data[4] else 'N/A'}
Completed Date: {request_data[5][:10] if request_data[5] else 'N/A'}
Notes: {request_data[6] or 'N/A'}
                    """.strip()
                    
                    self.info_text.config(state='normal')
                    self.info_text.delete(1.0, tk.END)
                    self.info_text.insert(1.0, info_text)
                    self.info_text.config(state='disabled')
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load request details: {str(e)}")
