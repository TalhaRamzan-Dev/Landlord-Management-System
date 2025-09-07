import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, date
from db import DB_FILE

class ExpenseManager:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.setup_ui()
        self.load_expenses()
        
    def setup_ui(self):
        """Setup the expense management UI"""
        # Main container
        main_container = tk.Frame(self.parent_frame, bg='white')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header with title and add button
        header_frame = tk.Frame(main_container, bg='white')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(header_frame, text="Expense Management", 
                font=('Arial', 18, 'bold'), bg='white').pack(side='left')
        
        tk.Button(header_frame, text="Add New Expense", command=self.add_expense,
                 bg='#4CAF50', fg='white', padx=20).pack(side='right')
        
        # Filter frame
        filter_frame = tk.Frame(main_container, bg='white')
        filter_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(filter_frame, text="Filter by Property:", bg='white').pack(side='left')
        
        self.property_filter = ttk.Combobox(filter_frame, width=30)
        self.property_filter.pack(side='left', padx=(10, 20))
        self.property_filter.bind('<<ComboboxSelected>>', self.filter_expenses)
        
        tk.Label(filter_frame, text="Category:", bg='white').pack(side='left')
        
        self.category_filter = ttk.Combobox(filter_frame, values=['All', 'Maintenance', 'Utility', 'Repair', 'Tax', 'Other'])
        self.category_filter.set('All')
        self.category_filter.pack(side='left', padx=(10, 20))
        self.category_filter.bind('<<ComboboxSelected>>', self.filter_expenses)
        
        tk.Button(filter_frame, text="All Properties", command=self.load_all_expenses,
                 bg='#2196F3', fg='white').pack(side='left', padx=(0, 10))
        tk.Button(filter_frame, text="Refresh", command=self.load_expenses,
                 bg='#2196F3', fg='white').pack(side='right')
        
        # Load property list for filter
        self.load_property_list()
        
        # Expenses list
        list_frame = tk.Frame(main_container, bg='white')
        list_frame.pack(fill='both', expand=True)
        
        # Treeview for expenses
        columns = ('ID', 'Property', 'Description', 'Category', 'Amount', 'Date', 'Paid By', 'Invoice #')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col)
            if col == 'ID':
                self.tree.column(col, width=50)
            elif col in ['Property', 'Description']:
                self.tree.column(col, width=150)
            elif col == 'Category':
                self.tree.column(col, width=100)
            elif col == 'Amount':
                self.tree.column(col, width=100)
            elif col in ['Date', 'Paid By']:
                self.tree.column(col, width=100)
            elif col == 'Invoice #':
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
        self.tree.bind('<Double-1>', self.view_expense_details)
        
        # Action buttons frame
        action_frame = tk.Frame(main_container, bg='white')
        action_frame.pack(fill='x', pady=(10, 0))
        
        tk.Button(action_frame, text="View Details", command=self.view_expense_details,
                 bg='#2196F3', fg='white').pack(side='left', padx=(0, 10))
        tk.Button(action_frame, text="Edit Expense", command=self.edit_expense,
                 bg='#FF9800', fg='white').pack(side='left', padx=(0, 10))
        tk.Button(action_frame, text="Delete Expense", command=self.delete_expense,
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
            
    def load_expenses(self):
        """Load expenses from database"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT e.id, 
                           COALESCE(p.name, 'Property #' || p.id) as property_name,
                           e.description, e.category, e.amount, e.date, e.paid_by, e.invoice_number
                    FROM expenses e
                    JOIN properties p ON e.property_id = p.id
                    ORDER BY e.date DESC
                """)
                
                expenses = cursor.fetchall()
                
                for expense in expenses:
                    # Format the data for display
                    formatted_expense = list(expense)
                    if formatted_expense[4]:  # amount
                        formatted_expense[4] = f"Rs {formatted_expense[4]:.2f}"
                    if formatted_expense[5]:  # date
                        formatted_expense[5] = formatted_expense[5][:10]
                    
                    self.tree.insert('', 'end', values=formatted_expense)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load expenses: {str(e)}")
            
    def load_all_expenses(self):
        """Load all expenses (clear filters)"""
        self.property_filter.set('All Properties')
        self.category_filter.set('All')
        self.load_expenses()
        
    def filter_expenses(self, event=None):
        """Filter expenses by property and category"""
        selected_property = self.property_filter.get()
        selected_category = self.category_filter.get()
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                
                # Build query based on filters
                query = """
                    SELECT e.id, 
                           COALESCE(p.name, 'Property #' || p.id) as property_name,
                           e.description, e.category, e.amount, e.date, e.paid_by, e.invoice_number
                    FROM expenses e
                    JOIN properties p ON e.property_id = p.id
                    WHERE 1=1
                """
                params = []
                
                if selected_property != 'All Properties':
                    property_name = selected_property.split(' - ')[0]
                    if property_name.startswith('Property #'):
                        property_id = int(property_name.split('#')[1])
                        query += " AND e.property_id = ?"
                        params.append(property_id)
                    else:
                        query += " AND p.name = ?"
                        params.append(property_name)
                
                if selected_category != 'All':
                    query += " AND e.category = ?"
                    params.append(selected_category)
                
                query += " ORDER BY e.date DESC"
                
                cursor.execute(query, params)
                expenses = cursor.fetchall()
                
                for expense in expenses:
                    formatted_expense = list(expense)
                    if formatted_expense[4]:  # amount
                        formatted_expense[4] = f"Rs {formatted_expense[4]:.2f}"
                    if formatted_expense[5]:  # date
                        formatted_expense[5] = formatted_expense[5][:10]
                    
                    self.tree.insert('', 'end', values=formatted_expense)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to filter expenses: {str(e)}")
        
    def add_expense(self):
        """Open add expense dialog"""
        ExpenseDialog(self.parent_frame, self, "Add Expense")
        
    def edit_expense(self):
        """Edit selected expense"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an expense to edit")
            return
            
        item = self.tree.item(selection[0])
        expense_id = item['values'][0]
        ExpenseDialog(self.parent_frame, self, "Edit Expense", expense_id)
        
    def view_expense_details(self, event=None):
        """View detailed information about selected expense"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an expense to view")
            return
            
        item = self.tree.item(selection[0])
        expense_id = item['values'][0]
        ExpenseDetailsDialog(self.parent_frame, expense_id)
        
    def delete_expense(self):
        """Delete selected expense"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an expense to delete")
            return
            
        item = self.tree.item(selection[0])
        expense_id = item['values'][0]
        description = item['values'][2]
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete the expense '{description}'?"):
            try:
                with sqlite3.connect(DB_FILE) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
                    conn.commit()
                    
                messagebox.showinfo("Success", "Expense deleted successfully")
                self.load_expenses()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete expense: {str(e)}")

class ExpenseDialog:
    def __init__(self, parent, expense_manager, title, expense_id=None):
        self.parent = parent
        self.expense_manager = expense_manager
        self.expense_id = expense_id
        
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
        
        if expense_id:
            self.load_expense_data()
            
    def setup_ui(self):
        """Setup the expense dialog UI"""
        main_frame = tk.Frame(self.dialog, bg='white')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Form fields
        fields = [
            ("Property:", "property_id"),
            ("Description:", "description"),
            ("Category:", "category"),
            ("Amount (Rs):", "amount"),
            ("Date:", "date"),
            ("Paid By:", "paid_by"),
            ("Invoice Number:", "invoice_number"),
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
            elif field_name == 'category':
                entry = ttk.Combobox(row_frame, values=['Maintenance', 'Utility', 'Repair', 'Tax', 'Other'])
                entry.pack(side='right', fill='x', expand=True, padx=(10, 0))
            elif field_name == 'date':
                entry = tk.Entry(row_frame)
                entry.pack(side='right', fill='x', expand=True, padx=(10, 0))
                entry.insert(0, date.today().strftime("%Y-%m-%d"))
            elif field_name == 'paid_by':
                entry = ttk.Combobox(row_frame, values=['Landlord', 'Tenant', 'Other'])
                entry.set('Landlord')
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
        tk.Button(button_frame, text="Save", command=self.save_expense,
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
            
    def load_expense_data(self):
        """Load existing expense data for editing"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT e.property_id, e.description, e.category, e.amount, e.date, 
                           e.paid_by, e.invoice_number, e.notes
                    FROM expenses e WHERE e.id = ?
                """, (self.expense_id,))
                
                data = cursor.fetchone()
                if data:
                    field_names = ['property_id', 'description', 'category', 'amount', 'date',
                                 'paid_by', 'invoice_number', 'notes']
                    
                    for i, field_name in enumerate(field_names):
                        if data[i] is not None:
                            if field_name == 'property_id':
                                # Load the display value for combobox
                                cursor.execute("SELECT name, address FROM properties WHERE id = ?", (data[i],))
                                prop_data = cursor.fetchone()
                                if prop_data:
                                    prop_name = prop_data[0] if prop_data[0] else f"Property #{data[i]}"
                                    self.entries[field_name].set(f"{prop_name} - {prop_data[1]}")
                            elif field_name == 'notes':
                                self.entries[field_name].insert(1.0, str(data[i]))
                            else:
                                self.entries[field_name].set(str(data[i]))
                                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load expense data: {str(e)}")
            
    def save_expense(self):
        """Save expense data"""
        try:
            # Validate required fields
            if not self.entries['property_id'].get().strip():
                messagebox.showerror("Error", "Please select a property")
                return
                
            if not self.entries['description'].get().strip():
                messagebox.showerror("Error", "Description is required")
                return
                
            if not self.entries['amount'].get().strip():
                messagebox.showerror("Error", "Amount is required")
                return
            
            # Extract property ID from selection
            property_selection = self.entries['property_id'].get()
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
                'property_id': property_id,
                'description': self.entries['description'].get().strip(),
                'category': self.entries['category'].get() or None,
                'amount': float(self.entries['amount'].get()),
                'date': self.entries['date'].get().strip() or date.today().strftime("%Y-%m-%d"),
                'paid_by': self.entries['paid_by'].get() or 'Landlord',
                'invoice_number': self.entries['invoice_number'].get().strip() or None,
                'notes': self.entries['notes'].get(1.0, tk.END).strip() or None
            }
            
            if self.expense_id:
                # Update existing expense
                cursor.execute("""
                    UPDATE expenses SET 
                    property_id = ?, description = ?, category = ?, amount = ?, date = ?, 
                    paid_by = ?, invoice_number = ?, notes = ?
                    WHERE id = ?
                """, (data['property_id'], data['description'], data['category'], data['amount'],
                     data['date'], data['paid_by'], data['invoice_number'], data['notes'],
                     self.expense_id))
            else:
                # Insert new expense
                cursor.execute("""
                    INSERT INTO expenses 
                    (property_id, description, category, amount, date, paid_by, invoice_number, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (data['property_id'], data['description'], data['category'], data['amount'],
                     data['date'], data['paid_by'], data['invoice_number'], data['notes']))
            
            conn.commit()
            
            messagebox.showinfo("Success", "Expense saved successfully")
            self.dialog.destroy()
            self.expense_manager.load_expenses()
            
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numeric value for amount")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save expense: {str(e)}")

class ExpenseDetailsDialog:
    def __init__(self, parent, expense_id):
        self.expense_id = expense_id
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Expense Details")
        self.dialog.geometry("600x500")
        self.dialog.configure(bg='white')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.setup_ui()
        self.load_expense_details()
        
    def setup_ui(self):
        """Setup the expense details UI"""
        main_frame = tk.Frame(self.dialog, bg='white')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Expense info frame
        info_frame = tk.LabelFrame(main_frame, text="Expense Information", bg='white')
        info_frame.pack(fill='x', pady=(0, 20))
        
        self.info_text = tk.Text(info_frame, height=10, wrap='word', state='disabled')
        self.info_text.pack(fill='x', padx=10, pady=10)
        
        # Close button
        tk.Button(main_frame, text="Close", command=self.dialog.destroy,
                 bg='#2196F3', fg='white', padx=20).pack(pady=10)
        
    def load_expense_details(self):
        """Load expense details"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                
                # Get expense details
                cursor.execute("""
                    SELECT e.description, e.category, e.amount, e.date, e.paid_by, 
                           e.invoice_number, e.notes, e.created_at,
                           COALESCE(p.name, 'Property #' || p.id) as property_name,
                           p.address
                    FROM expenses e
                    JOIN properties p ON e.property_id = p.id
                    WHERE e.id = ?
                """, (self.expense_id,))
                
                expense_data = cursor.fetchone()
                if expense_data:
                    info_text = f"""
Expense ID: {self.expense_id}
Property: {expense_data[8]}
Property Address: {expense_data[9]}
Description: {expense_data[0]}
Category: {expense_data[1] or 'N/A'}
Amount: Rs {expense_data[2]:.2f}
Date: {expense_data[3][:10] if expense_data[3] else 'N/A'}
Paid By: {expense_data[4]}
Invoice Number: {expense_data[5] or 'N/A'}
Notes: {expense_data[6] or 'N/A'}
Created: {expense_data[7][:10] if expense_data[7] else 'N/A'}
                    """.strip()
                    
                    self.info_text.config(state='normal')
                    self.info_text.delete(1.0, tk.END)
                    self.info_text.insert(1.0, info_text)
                    self.info_text.config(state='disabled')
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load expense details: {str(e)}")
