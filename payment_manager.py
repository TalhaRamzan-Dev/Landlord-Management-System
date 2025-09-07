import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, date
import calendar
from db import DB_FILE

class PaymentManager:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.setup_ui()
        self.load_payments()
        
    def setup_ui(self):
        """Setup the payment management UI"""
        # Main container
        main_container = tk.Frame(self.parent_frame, bg='white')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header with title and add button
        header_frame = tk.Frame(main_container, bg='white')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(header_frame, text="Rent Payment Management", 
                font=('Arial', 18, 'bold'), bg='white').pack(side='left')
        
        tk.Button(header_frame, text="Record Payment", command=self.record_payment,
                 bg='#4CAF50', fg='white', padx=20).pack(side='right')
        
        # Filter frame
        filter_frame = tk.Frame(main_container, bg='white')
        filter_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(filter_frame, text="Filter by Status:", bg='white').pack(side='left')
        
        self.status_filter = ttk.Combobox(filter_frame, values=['All', 'Paid', 'Pending', 'Overdue', 'Partial'])
        self.status_filter.set('All')
        self.status_filter.pack(side='left', padx=(10, 20))
        self.status_filter.bind('<<ComboboxSelected>>', self.filter_payments)
        
        tk.Button(filter_frame, text="Generate Monthly Rent", command=self.generate_monthly_rent,
                 bg='#FF9800', fg='white', padx=15).pack(side='left', padx=(0, 10))
        tk.Button(filter_frame, text="Refresh", command=self.load_payments,
                 bg='#2196F3', fg='white').pack(side='right')
        
        # Payments list
        list_frame = tk.Frame(main_container, bg='white')
        list_frame.pack(fill='both', expand=True)
        
        # Treeview for payments
        columns = ('ID', 'Tenant', 'Property', 'Month', 'Due Date', 'Amount Due', 'Amount Paid', 'Status', 'Payment Date')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col)
            if col == 'ID':
                self.tree.column(col, width=50)
            elif col in ['Tenant', 'Property']:
                self.tree.column(col, width=120)
            elif col in ['Month', 'Due Date', 'Payment Date']:
                self.tree.column(col, width=100)
            elif col in ['Amount Due', 'Amount Paid']:
                self.tree.column(col, width=100)
            elif col == 'Status':
                self.tree.column(col, width=80)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Bind double-click to view details
        self.tree.bind('<Double-1>', self.view_payment_details)
        
        # Action buttons frame
        action_frame = tk.Frame(main_container, bg='white')
        action_frame.pack(fill='x', pady=(10, 0))
        
        tk.Button(action_frame, text="View Details", command=self.view_payment_details,
                 bg='#2196F3', fg='white').pack(side='left', padx=(0, 10))
        tk.Button(action_frame, text="Edit Payment", command=self.edit_payment,
                 bg='#FF9800', fg='white').pack(side='left', padx=(0, 10))
        tk.Button(action_frame, text="Delete Payment", command=self.delete_payment,
                 bg='#f44336', fg='white').pack(side='left')
        
    def load_payments(self):
        """Load payments from database"""
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
                        SELECT rp.id, t.name, 
                               COALESCE(p.name, 'Property #' || p.id) as property_name,
                               rp.month, rp.due_date, rp.amount_due, rp.amount_paid, 
                               rp.status, rp.payment_date
                        FROM rent_payments rp
                        JOIN tenants t ON rp.tenant_id = t.id
                        JOIN properties p ON rp.property_id = p.id
                        ORDER BY rp.due_date DESC
                    """)
                else:
                    cursor.execute("""
                        SELECT rp.id, t.name, 
                               COALESCE(p.name, 'Property #' || p.id) as property_name,
                               rp.month, rp.due_date, rp.amount_due, rp.amount_paid, 
                               rp.status, rp.payment_date
                        FROM rent_payments rp
                        JOIN tenants t ON rp.tenant_id = t.id
                        JOIN properties p ON rp.property_id = p.id
                        WHERE rp.status = ?
                        ORDER BY rp.due_date DESC
                    """, (status_filter,))
                
                payments = cursor.fetchall()
                
                for payment in payments:
                    # Format the data for display
                    formatted_payment = list(payment)
                    if formatted_payment[4]:  # due_date
                        formatted_payment[4] = formatted_payment[4][:10]
                    if formatted_payment[5]:  # amount_due
                        formatted_payment[5] = f"Rs {formatted_payment[5]:.2f}"
                    if formatted_payment[6]:  # amount_paid
                        formatted_payment[6] = f"Rs {formatted_payment[6]:.2f}"
                    if formatted_payment[8]:  # payment_date
                        formatted_payment[8] = formatted_payment[8][:10]
                    
                    self.tree.insert('', 'end', values=formatted_payment)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load payments: {str(e)}")
            
    def filter_payments(self, event=None):
        """Filter payments by status"""
        self.load_payments()
        
    def generate_monthly_rent(self):
        """Generate monthly rent due for all active leases"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                
                # Get current month and year
                current_date = date.today()
                current_month = current_date.strftime("%Y-%m")
                
                # Get all active leases
                cursor.execute("""
                    SELECT l.id, l.tenant_id, l.property_id, l.rent_amount
                    FROM leases l
                    WHERE l.status = 'Active' AND l.start_date <= ?
                """, (current_date,))
                
                active_leases = cursor.fetchall()
                
                generated_count = 0
                
                for lease in active_leases:
                    lease_id, tenant_id, property_id, rent_amount = lease
                    
                    # Check if payment already exists for this month
                    cursor.execute("""
                        SELECT id FROM rent_payments 
                        WHERE lease_id = ? AND month = ?
                    """, (lease_id, current_month))
                    
                    if not cursor.fetchone():
                        # Calculate due date (first day of next month)
                        if current_date.month == 12:
                            next_month = date(current_date.year + 1, 1, 1)
                        else:
                            next_month = date(current_date.year, current_date.month + 1, 1)
                        
                        # Insert new payment record
                        cursor.execute("""
                            INSERT INTO rent_payments 
                            (lease_id, tenant_id, property_id, month, due_date, amount_due, status)
                            VALUES (?, ?, ?, ?, ?, ?, 'Pending')
                        """, (lease_id, tenant_id, property_id, current_month, next_month, rent_amount))
                        
                        generated_count += 1
                
                conn.commit()
                
                if generated_count > 0:
                    messagebox.showinfo("Success", f"Generated {generated_count} monthly rent records")
                else:
                    messagebox.showinfo("Info", "No new rent records needed - all current month payments already exist")
                
                self.load_payments()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate monthly rent: {str(e)}")
        
    def record_payment(self):
        """Open record payment dialog"""
        PaymentDialog(self.parent_frame, self, "Record Payment")
        
    def edit_payment(self):
        """Edit selected payment"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a payment to edit")
            return
            
        item = self.tree.item(selection[0])
        payment_id = item['values'][0]
        PaymentDialog(self.parent_frame, self, "Edit Payment", payment_id)
        
    def view_payment_details(self, event=None):
        """View detailed information about selected payment"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a payment to view")
            return
            
        item = self.tree.item(selection[0])
        payment_id = item['values'][0]
        PaymentDetailsDialog(self.parent_frame, payment_id)
        
    def delete_payment(self):
        """Delete selected payment"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a payment to delete")
            return
            
        item = self.tree.item(selection[0])
        payment_id = item['values'][0]
        tenant_name = item['values'][1]
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete the payment record for '{tenant_name}'?"):
            try:
                with sqlite3.connect(DB_FILE) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM rent_payments WHERE id = ?", (payment_id,))
                    conn.commit()
                    
                messagebox.showinfo("Success", "Payment record deleted successfully")
                self.load_payments()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete payment: {str(e)}")

class PaymentDialog:
    def __init__(self, parent, payment_manager, title, payment_id=None):
        self.parent = parent
        self.payment_manager = payment_manager
        self.payment_id = payment_id
        
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
        
        if payment_id:
            self.load_payment_data()
            
    def setup_ui(self):
        """Setup the payment dialog UI"""
        main_frame = tk.Frame(self.dialog, bg='white')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Form fields
        fields = [
            ("Lease:", "lease_id"),
            ("Month:", "month"),
            ("Due Date:", "due_date"),
            ("Amount Due (Rs):", "amount_due"),
            ("Amount Paid (Rs):", "amount_paid"),
            ("Payment Date:", "payment_date"),
            ("Payment Method:", "payment_method"),
            ("Status:", "status"),
            ("Notes:", "notes")
        ]
        
        self.entries = {}
        
        for i, (label_text, field_name) in enumerate(fields):
            row_frame = tk.Frame(main_frame, bg='white')
            row_frame.pack(fill='x', pady=5)
            
            tk.Label(row_frame, text=label_text, bg='white', width=15, anchor='w').pack(side='left')
            
            if field_name == 'lease_id':
                entry = ttk.Combobox(row_frame, width=30)
                entry.pack(side='right', fill='x', expand=True, padx=(10, 0))
                self.load_lease_options(entry)
            elif field_name == 'payment_method':
                entry = ttk.Combobox(row_frame, values=['Cash', 'Bank Transfer', 'Cheque', 'Online', 'Other'])
                entry.pack(side='right', fill='x', expand=True, padx=(10, 0))
            elif field_name == 'status':
                entry = ttk.Combobox(row_frame, values=['Pending', 'Paid', 'Partial', 'Overdue'])
                entry.set('Pending')
                entry.pack(side='right', fill='x', expand=True, padx=(10, 0))
            elif field_name in ['due_date', 'payment_date']:
                entry = tk.Entry(row_frame)
                entry.pack(side='right', fill='x', expand=True, padx=(10, 0))
                if field_name == 'due_date':
                    entry.insert(0, "YYYY-MM-DD")
                else:
                    entry.insert(0, "YYYY-MM-DD")
            elif field_name == 'month':
                entry = tk.Entry(row_frame)
                entry.pack(side='right', fill='x', expand=True, padx=(10, 0))
                entry.insert(0, "YYYY-MM")
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
        tk.Button(button_frame, text="Save", command=self.save_payment,
                 bg='#4CAF50', fg='white', padx=20).pack(side='right')
        
    def load_lease_options(self, combobox):
        """Load lease options for dropdown"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT l.id, t.name, COALESCE(p.name, 'Property #' || p.id) as property_name
                    FROM leases l
                    JOIN tenants t ON l.tenant_id = t.id
                    JOIN properties p ON l.property_id = p.id
                    WHERE l.status = 'Active'
                    ORDER BY t.name
                """)
                leases = cursor.fetchall()
                
                lease_options = []
                for lease in leases:
                    lease_options.append(f"{lease[1]} - {lease[2]} (Lease ID: {lease[0]})")
                
                combobox['values'] = lease_options
                
        except Exception as e:
            print(f"Error loading lease options: {e}")
            
    def load_payment_data(self):
        """Load existing payment data for editing"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT rp.lease_id, rp.month, rp.due_date, rp.amount_due, rp.amount_paid,
                           rp.payment_date, rp.payment_method, rp.status, rp.notes
                    FROM rent_payments rp WHERE rp.id = ?
                """, (self.payment_id,))
                
                data = cursor.fetchone()
                if data:
                    field_names = ['lease_id', 'month', 'due_date', 'amount_due', 'amount_paid',
                                 'payment_date', 'payment_method', 'status', 'notes']
                    
                    for i, field_name in enumerate(field_names):
                        if data[i] is not None:
                            if field_name == 'lease_id':
                                # Load the display value for combobox
                                cursor.execute("""
                                    SELECT t.name, COALESCE(p.name, 'Property #' || p.id) as property_name
                                    FROM leases l
                                    JOIN tenants t ON l.tenant_id = t.id
                                    JOIN properties p ON l.property_id = p.id
                                    WHERE l.id = ?
                                """, (data[i],))
                                lease_data = cursor.fetchone()
                                if lease_data:
                                    self.entries[field_name].set(f"{lease_data[0]} - {lease_data[1]} (Lease ID: {data[i]})")
                            elif field_name == 'notes':
                                self.entries[field_name].insert(1.0, str(data[i]))
                            else:
                                self.entries[field_name].set(str(data[i]))
                                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load payment data: {str(e)}")
            
    def save_payment(self):
        """Save payment data"""
        try:
            # Validate required fields
            if not self.entries['lease_id'].get().strip():
                messagebox.showerror("Error", "Please select a lease")
                return
                
            if not self.entries['month'].get().strip():
                messagebox.showerror("Error", "Month is required")
                return
                
            if not self.entries['amount_due'].get().strip():
                messagebox.showerror("Error", "Amount due is required")
                return
            
            # Extract lease ID from selection
            lease_selection = self.entries['lease_id'].get()
            lease_id = int(lease_selection.split('(Lease ID: ')[1].rstrip(')'))
            
            # Get tenant and property IDs
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT tenant_id, property_id FROM leases WHERE id = ?", (lease_id,))
                lease_data = cursor.fetchone()
                if not lease_data:
                    messagebox.showerror("Error", "Invalid lease selection")
                    return
                
                tenant_id, property_id = lease_data
            
            # Get form data
            data = {
                'lease_id': lease_id,
                'tenant_id': tenant_id,
                'property_id': property_id,
                'month': self.entries['month'].get().strip(),
                'due_date': self.entries['due_date'].get().strip() or None,
                'amount_due': float(self.entries['amount_due'].get()),
                'amount_paid': float(self.entries['amount_paid'].get()) if self.entries['amount_paid'].get().strip() else 0,
                'payment_date': self.entries['payment_date'].get().strip() or None,
                'payment_method': self.entries['payment_method'].get() or None,
                'status': self.entries['status'].get(),
                'notes': self.entries['notes'].get(1.0, tk.END).strip() or None
            }
            
            if self.payment_id:
                # Update existing payment
                cursor.execute("""
                    UPDATE rent_payments SET 
                    lease_id = ?, tenant_id = ?, property_id = ?, month = ?, due_date = ?, 
                    amount_due = ?, amount_paid = ?, payment_date = ?, payment_method = ?, 
                    status = ?, notes = ?
                    WHERE id = ?
                """, (data['lease_id'], data['tenant_id'], data['property_id'], data['month'],
                     data['due_date'], data['amount_due'], data['amount_paid'], data['payment_date'],
                     data['payment_method'], data['status'], data['notes'], self.payment_id))
            else:
                # Insert new payment
                cursor.execute("""
                    INSERT INTO rent_payments 
                    (lease_id, tenant_id, property_id, month, due_date, amount_due, 
                     amount_paid, payment_date, payment_method, status, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (data['lease_id'], data['tenant_id'], data['property_id'], data['month'],
                     data['due_date'], data['amount_due'], data['amount_paid'], data['payment_date'],
                     data['payment_method'], data['status'], data['notes']))
            
            conn.commit()
            
            messagebox.showinfo("Success", "Payment saved successfully")
            self.dialog.destroy()
            self.payment_manager.load_payments()
            
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numeric values for amounts")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save payment: {str(e)}")

class PaymentDetailsDialog:
    def __init__(self, parent, payment_id):
        self.payment_id = payment_id
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Payment Details")
        self.dialog.geometry("600x500")
        self.dialog.configure(bg='white')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.setup_ui()
        self.load_payment_details()
        
    def setup_ui(self):
        """Setup the payment details UI"""
        main_frame = tk.Frame(self.dialog, bg='white')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Payment info frame
        info_frame = tk.LabelFrame(main_frame, text="Payment Information", bg='white')
        info_frame.pack(fill='x', pady=(0, 20))
        
        self.info_text = tk.Text(info_frame, height=10, wrap='word', state='disabled')
        self.info_text.pack(fill='x', padx=10, pady=10)
        
        # Close button
        tk.Button(main_frame, text="Close", command=self.dialog.destroy,
                 bg='#2196F3', fg='white', padx=20).pack(pady=10)
        
    def load_payment_details(self):
        """Load payment details"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                
                # Get payment details
                cursor.execute("""
                    SELECT rp.month, rp.due_date, rp.amount_due, rp.amount_paid, 
                           rp.payment_date, rp.payment_method, rp.status, rp.notes, rp.created_at,
                           t.name as tenant_name, 
                           COALESCE(p.name, 'Property #' || p.id) as property_name,
                           p.address
                    FROM rent_payments rp
                    JOIN tenants t ON rp.tenant_id = t.id
                    JOIN properties p ON rp.property_id = p.id
                    WHERE rp.id = ?
                """, (self.payment_id,))
                
                payment_data = cursor.fetchone()
                if payment_data:
                    info_text = f"""
Payment ID: {self.payment_id}
Tenant: {payment_data[9]}
Property: {payment_data[10]}
Property Address: {payment_data[11]}
Month: {payment_data[0]}
Due Date: {payment_data[1][:10] if payment_data[1] else 'N/A'}
Amount Due: Rs {payment_data[2]:.2f}
Amount Paid: Rs {payment_data[3]:.2f}
Payment Date: {payment_data[4][:10] if payment_data[4] else 'N/A'}
Payment Method: {payment_data[5] or 'N/A'}
Status: {payment_data[6]}
Notes: {payment_data[7] or 'N/A'}
Created: {payment_data[8][:10] if payment_data[8] else 'N/A'}
                    """.strip()
                    
                    self.info_text.config(state='normal')
                    self.info_text.delete(1.0, tk.END)
                    self.info_text.insert(1.0, info_text)
                    self.info_text.config(state='disabled')
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load payment details: {str(e)}")
