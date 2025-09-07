import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, date
from db import DB_FILE

class LeaseManager:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.setup_ui()
        self.load_leases()
        
    def setup_ui(self):
        """Setup the lease management UI"""
        # Main container
        main_container = tk.Frame(self.parent_frame, bg='white')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header with title and add button
        header_frame = tk.Frame(main_container, bg='white')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(header_frame, text="Lease Management", 
                font=('Arial', 18, 'bold'), bg='white').pack(side='left')
        
        tk.Button(header_frame, text="Create New Lease", command=self.create_lease,
                 bg='#4CAF50', fg='white', padx=20).pack(side='right')
        
        # Filter frame
        filter_frame = tk.Frame(main_container, bg='white')
        filter_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(filter_frame, text="Filter by Status:", bg='white').pack(side='left')
        
        self.status_filter = ttk.Combobox(filter_frame, values=['All', 'Active', 'Terminated', 'Expired'])
        self.status_filter.set('All')
        self.status_filter.pack(side='left', padx=(10, 20))
        self.status_filter.bind('<<ComboboxSelected>>', self.filter_leases)
        
        tk.Button(filter_frame, text="Refresh", command=self.load_leases,
                 bg='#2196F3', fg='white').pack(side='right')
        
        # Leases list
        list_frame = tk.Frame(main_container, bg='white')
        list_frame.pack(fill='both', expand=True)
        
        # Treeview for leases
        columns = ('ID', 'Tenant', 'Property', 'Start Date', 'End Date', 'Rent', 'Status', 'Created')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col)
            if col == 'ID':
                self.tree.column(col, width=50)
            elif col in ['Tenant', 'Property']:
                self.tree.column(col, width=150)
            elif col in ['Start Date', 'End Date', 'Created']:
                self.tree.column(col, width=100)
            elif col == 'Rent':
                self.tree.column(col, width=100)
            elif col == 'Status':
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
        self.tree.bind('<Double-1>', self.view_lease_details)
        
        # Action buttons frame
        action_frame = tk.Frame(main_container, bg='white')
        action_frame.pack(fill='x', pady=(10, 0))
        
        tk.Button(action_frame, text="View Details", command=self.view_lease_details,
                 bg='#2196F3', fg='white').pack(side='left', padx=(0, 10))
        tk.Button(action_frame, text="Edit Lease", command=self.edit_lease,
                 bg='#FF9800', fg='white').pack(side='left', padx=(0, 10))
        tk.Button(action_frame, text="Terminate Lease", command=self.terminate_lease,
                 bg='#f44336', fg='white').pack(side='left')
        
    def load_leases(self):
        """Load leases from database"""
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
                        SELECT l.id, t.name, 
                               COALESCE(p.name, 'Property #' || p.id) as property_name,
                               l.start_date, l.end_date, l.rent_amount, l.status, l.created_at
                        FROM leases l
                        JOIN tenants t ON l.tenant_id = t.id
                        JOIN properties p ON l.property_id = p.id
                        ORDER BY l.created_at DESC
                    """)
                else:
                    cursor.execute("""
                        SELECT l.id, t.name, 
                               COALESCE(p.name, 'Property #' || p.id) as property_name,
                               l.start_date, l.end_date, l.rent_amount, l.status, l.created_at
                        FROM leases l
                        JOIN tenants t ON l.tenant_id = t.id
                        JOIN properties p ON l.property_id = p.id
                        WHERE l.status = ?
                        ORDER BY l.created_at DESC
                    """, (status_filter,))
                
                leases = cursor.fetchall()
                
                for lease in leases:
                    # Format the data for display
                    formatted_lease = list(lease)
                    if formatted_lease[3]:  # start_date
                        formatted_lease[3] = formatted_lease[3][:10]
                    if formatted_lease[4]:  # end_date
                        formatted_lease[4] = formatted_lease[4][:10]
                    if formatted_lease[5]:  # rent_amount
                        formatted_lease[5] = f"Rs {formatted_lease[5]:.2f}"
                    if formatted_lease[7]:  # created_at
                        formatted_lease[7] = formatted_lease[7][:10]
                    
                    self.tree.insert('', 'end', values=formatted_lease)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load leases: {str(e)}")
            
    def filter_leases(self, event=None):
        """Filter leases by status"""
        self.load_leases()
        
    def create_lease(self):
        """Open create lease dialog"""
        LeaseDialog(self.parent_frame, self, "Create Lease")
        
    def edit_lease(self):
        """Edit selected lease"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a lease to edit")
            return
            
        item = self.tree.item(selection[0])
        lease_id = item['values'][0]
        LeaseDialog(self.parent_frame, self, "Edit Lease", lease_id)
        
    def view_lease_details(self, event=None):
        """View detailed information about selected lease"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a lease to view")
            return
            
        item = self.tree.item(selection[0])
        lease_id = item['values'][0]
        LeaseDetailsDialog(self.parent_frame, lease_id)
        
    def terminate_lease(self):
        """Terminate selected lease"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a lease to terminate")
            return
            
        item = self.tree.item(selection[0])
        lease_id = item['values'][0]
        tenant_name = item['values'][1]
        
        if messagebox.askyesno("Confirm Termination", 
                              f"Are you sure you want to terminate the lease for '{tenant_name}'?\n\n"
                              "This will mark the lease as terminated."):
            try:
                with sqlite3.connect(DB_FILE) as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE leases SET status = 'Terminated' WHERE id = ?", (lease_id,))
                    conn.commit()
                    
                messagebox.showinfo("Success", "Lease terminated successfully")
                self.load_leases()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to terminate lease: {str(e)}")

class LeaseDialog:
    def __init__(self, parent, lease_manager, title, lease_id=None):
        self.parent = parent
        self.lease_manager = lease_manager
        self.lease_id = lease_id
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x500")
        self.dialog.configure(bg='white')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.setup_ui()
        
        if lease_id:
            self.load_lease_data()
            
    def setup_ui(self):
        """Setup the lease dialog UI"""
        main_frame = tk.Frame(self.dialog, bg='white')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Form fields
        fields = [
            ("Tenant:", "tenant_id"),
            ("Property:", "property_id"),
            ("Start Date:", "start_date"),
            ("End Date:", "end_date"),
            ("Rent Amount (Rs):", "rent_amount"),
            ("Deposit Amount (Rs):", "deposit_amount"),
            ("Status:", "status")
        ]
        
        self.entries = {}
        
        for i, (label_text, field_name) in enumerate(fields):
            row_frame = tk.Frame(main_frame, bg='white')
            row_frame.pack(fill='x', pady=5)
            
            tk.Label(row_frame, text=label_text, bg='white', width=15, anchor='w').pack(side='left')
            
            if field_name in ['tenant_id', 'property_id']:
                entry = ttk.Combobox(row_frame, width=30)
                entry.pack(side='right', fill='x', expand=True, padx=(10, 0))
                if field_name == 'tenant_id':
                    self.load_tenant_options(entry)
                else:
                    self.load_property_options(entry)
            elif field_name in ['start_date', 'end_date']:
                entry = tk.Entry(row_frame)
                entry.pack(side='right', fill='x', expand=True, padx=(10, 0))
                # Add date format hint
                if field_name == 'start_date':
                    entry.insert(0, "YYYY-MM-DD")
                else:
                    entry.insert(0, "YYYY-MM-DD")
            elif field_name == 'status':
                entry = ttk.Combobox(row_frame, values=['Active', 'Terminated', 'Expired'])
                entry.set('Active')
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
        tk.Button(button_frame, text="Save", command=self.save_lease,
                 bg='#4CAF50', fg='white', padx=20).pack(side='right')
        
    def load_tenant_options(self, combobox):
        """Load tenant options for dropdown"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name FROM tenants ORDER BY name")
                tenants = cursor.fetchall()
                
                tenant_options = []
                for tenant in tenants:
                    tenant_options.append(f"{tenant[1]} (ID: {tenant[0]})")
                
                combobox['values'] = tenant_options
                
        except Exception as e:
            print(f"Error loading tenant options: {e}")
            
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
            
    def load_lease_data(self):
        """Load existing lease data for editing"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT l.tenant_id, l.property_id, l.start_date, l.end_date, 
                           l.rent_amount, l.deposit_amount, l.status
                    FROM leases l WHERE l.id = ?
                """, (self.lease_id,))
                
                data = cursor.fetchone()
                if data:
                    field_names = ['tenant_id', 'property_id', 'start_date', 'end_date',
                                 'rent_amount', 'deposit_amount', 'status']
                    
                    for i, field_name in enumerate(field_names):
                        if data[i] is not None:
                            if field_name in ['tenant_id', 'property_id']:
                                # Load the display value for combobox
                                if field_name == 'tenant_id':
                                    cursor.execute("SELECT name FROM tenants WHERE id = ?", (data[i],))
                                    tenant_name = cursor.fetchone()[0]
                                    self.entries[field_name].set(f"{tenant_name} (ID: {data[i]})")
                                else:
                                    cursor.execute("SELECT name, address FROM properties WHERE id = ?", (data[i],))
                                    prop_data = cursor.fetchone()
                                    prop_name = prop_data[0] if prop_data[0] else f"Property #{data[i]}"
                                    self.entries[field_name].set(f"{prop_name} - {prop_data[1]}")
                            else:
                                self.entries[field_name].set(str(data[i]))
                                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load lease data: {str(e)}")
            
    def save_lease(self):
        """Save lease data"""
        try:
            # Validate required fields
            if not self.entries['tenant_id'].get().strip():
                messagebox.showerror("Error", "Please select a tenant")
                return
                
            if not self.entries['property_id'].get().strip():
                messagebox.showerror("Error", "Please select a property")
                return
                
            if not self.entries['start_date'].get().strip():
                messagebox.showerror("Error", "Start date is required")
                return
                
            if not self.entries['rent_amount'].get().strip():
                messagebox.showerror("Error", "Rent amount is required")
                return
            
            # Extract IDs from selections
            tenant_selection = self.entries['tenant_id'].get()
            tenant_id = int(tenant_selection.split('(ID: ')[1].rstrip(')'))
            
            property_selection = self.entries['property_id'].get()
            property_name = property_selection.split(' - ')[0]
            
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                
                if property_name.startswith('Property #'):
                    property_id = int(property_name.split('#')[1])
                else:
                    cursor.execute("SELECT id FROM properties WHERE name = ?", (property_name,))
                    result = cursor.fetchone()
                    if result:
                        property_id = result[0]
                    else:
                        messagebox.showerror("Error", "Invalid property selection")
                        return
            
            # Get form data
            data = {
                'tenant_id': tenant_id,
                'property_id': property_id,
                'start_date': self.entries['start_date'].get().strip(),
                'end_date': self.entries['end_date'].get().strip() or None,
                'rent_amount': float(self.entries['rent_amount'].get()),
                'deposit_amount': float(self.entries['deposit_amount'].get()) if self.entries['deposit_amount'].get().strip() else 0,
                'status': self.entries['status'].get()
            }
            
            if self.lease_id:
                # Update existing lease
                cursor.execute("""
                    UPDATE leases SET 
                    tenant_id = ?, property_id = ?, start_date = ?, end_date = ?, 
                    rent_amount = ?, deposit_amount = ?, status = ?
                    WHERE id = ?
                """, (data['tenant_id'], data['property_id'], data['start_date'], data['end_date'],
                     data['rent_amount'], data['deposit_amount'], data['status'],
                     self.lease_id))
            else:
                # Insert new lease
                cursor.execute("""
                    INSERT INTO leases 
                    (tenant_id, property_id, start_date, end_date, rent_amount, deposit_amount, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (data['tenant_id'], data['property_id'], data['start_date'], data['end_date'],
                     data['rent_amount'], data['deposit_amount'], data['status']))
            
            conn.commit()
            
            messagebox.showinfo("Success", "Lease saved successfully")
            self.dialog.destroy()
            self.lease_manager.load_leases()
            
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numeric values for amounts")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save lease: {str(e)}")

class LeaseDetailsDialog:
    def __init__(self, parent, lease_id):
        self.lease_id = lease_id
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Lease Details")
        self.dialog.geometry("800x600")
        self.dialog.configure(bg='white')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.setup_ui()
        self.load_lease_details()
        
    def setup_ui(self):
        """Setup the lease details UI"""
        main_frame = tk.Frame(self.dialog, bg='white')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Lease info frame
        info_frame = tk.LabelFrame(main_frame, text="Lease Information", bg='white')
        info_frame.pack(fill='x', pady=(0, 20))
        
        self.info_text = tk.Text(info_frame, height=8, wrap='word', state='disabled')
        self.info_text.pack(fill='x', padx=10, pady=10)
        
        # Payments frame
        payments_frame = tk.LabelFrame(main_frame, text="Payment History", bg='white')
        payments_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Payments treeview
        payment_columns = ('Month', 'Due Date', 'Amount Due', 'Amount Paid', 'Status', 'Payment Date')
        self.payment_tree = ttk.Treeview(payments_frame, columns=payment_columns, show='headings', height=6)
        
        for col in payment_columns:
            self.payment_tree.heading(col, text=col)
            self.payment_tree.column(col, width=120)
        
        self.payment_tree.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Close button
        tk.Button(main_frame, text="Close", command=self.dialog.destroy,
                 bg='#2196F3', fg='white', padx=20).pack(pady=10)
        
    def load_lease_details(self):
        """Load lease details and payment history"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                
                # Get lease details
                cursor.execute("""
                    SELECT l.start_date, l.end_date, l.rent_amount, l.deposit_amount, l.status, l.created_at,
                           t.name as tenant_name, 
                           COALESCE(p.name, 'Property #' || p.id) as property_name,
                           p.address
                    FROM leases l
                    JOIN tenants t ON l.tenant_id = t.id
                    JOIN properties p ON l.property_id = p.id
                    WHERE l.id = ?
                """, (self.lease_id,))
                
                lease_data = cursor.fetchone()
                if lease_data:
                    info_text = f"""
Lease ID: {self.lease_id}
Tenant: {lease_data[6]}
Property: {lease_data[7]}
Property Address: {lease_data[8]}
Start Date: {lease_data[0][:10] if lease_data[0] else 'N/A'}
End Date: {lease_data[1][:10] if lease_data[1] else 'N/A'}
Rent Amount: Rs {lease_data[2]:.2f}
Deposit Amount: Rs {lease_data[3]:.2f}
Status: {lease_data[4]}
Created: {lease_data[5][:10] if lease_data[5] else 'N/A'}
                    """.strip()
                    
                    self.info_text.config(state='normal')
                    self.info_text.delete(1.0, tk.END)
                    self.info_text.insert(1.0, info_text)
                    self.info_text.config(state='disabled')
                
                # Get payment history
                cursor.execute("""
                    SELECT month, due_date, amount_due, amount_paid, status, payment_date
                    FROM rent_payments WHERE lease_id = ?
                    ORDER BY due_date DESC
                """, (self.lease_id,))
                
                payments = cursor.fetchall()
                
                for payment in payments:
                    formatted_payment = list(payment)
                    if formatted_payment[1]:  # due_date
                        formatted_payment[1] = formatted_payment[1][:10]
                    if formatted_payment[2]:  # amount_due
                        formatted_payment[2] = f"Rs {formatted_payment[2]:.2f}"
                    if formatted_payment[3]:  # amount_paid
                        formatted_payment[3] = f"Rs {formatted_payment[3]:.2f}"
                    if formatted_payment[5]:  # payment_date
                        formatted_payment[5] = formatted_payment[5][:10]
                    
                    self.payment_tree.insert('', 'end', values=formatted_payment)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load lease details: {str(e)}")
