import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import os
import shutil
from datetime import datetime
from db import DB_FILE

class DocumentManager:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.documents_dir = "documents"
        self.setup_ui()
        self.load_documents()
        
        # Create documents directory if it doesn't exist
        if not os.path.exists(self.documents_dir):
            os.makedirs(self.documents_dir)
        
    def setup_ui(self):
        """Setup the document management UI"""
        # Main container
        main_container = tk.Frame(self.parent_frame, bg='white')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header with title and add button
        header_frame = tk.Frame(main_container, bg='white')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(header_frame, text="Document Management", 
                font=('Arial', 18, 'bold'), bg='white').pack(side='left')
        
        tk.Button(header_frame, text="Upload Document", command=self.upload_document,
                 bg='#4CAF50', fg='white', padx=20).pack(side='right')
        
        # Filter frame
        filter_frame = tk.Frame(main_container, bg='white')
        filter_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(filter_frame, text="Filter by Type:", bg='white').pack(side='left')
        
        self.type_filter = ttk.Combobox(filter_frame, values=['All', 'Property', 'Tenant', 'Lease', 'Payment', 'Expense'])
        self.type_filter.set('All')
        self.type_filter.pack(side='left', padx=(10, 20))
        self.type_filter.bind('<<ComboboxSelected>>', self.filter_documents)
        
        tk.Button(filter_frame, text="Refresh", command=self.load_documents,
                 bg='#2196F3', fg='white').pack(side='right')
        
        # Documents list
        list_frame = tk.Frame(main_container, bg='white')
        list_frame.pack(fill='both', expand=True)
        
        # Treeview for documents
        columns = ('ID', 'Type', 'Related ID', 'File Name', 'Description', 'Uploaded')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col)
            if col == 'ID':
                self.tree.column(col, width=50)
            elif col == 'Type':
                self.tree.column(col, width=80)
            elif col == 'Related ID':
                self.tree.column(col, width=80)
            elif col == 'File Name':
                self.tree.column(col, width=200)
            elif col == 'Description':
                self.tree.column(col, width=200)
            elif col == 'Uploaded':
                self.tree.column(col, width=120)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(list_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        
        # Bind double-click to open document
        self.tree.bind('<Double-1>', self.open_document)
        
        # Action buttons frame
        action_frame = tk.Frame(main_container, bg='white')
        action_frame.pack(fill='x', pady=(10, 0))
        
        tk.Button(action_frame, text="Open Document", command=self.open_document,
                 bg='#2196F3', fg='white').pack(side='left', padx=(0, 10))
        tk.Button(action_frame, text="Edit Description", command=self.edit_description,
                 bg='#FF9800', fg='white').pack(side='left', padx=(0, 10))
        tk.Button(action_frame, text="Delete Document", command=self.delete_document,
                 bg='#f44336', fg='white').pack(side='left')
        
    def load_documents(self):
        """Load documents from database"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT id, related_type, related_id, file_path, description, uploaded_at
                    FROM documents
                    ORDER BY uploaded_at DESC
                """)
                
                documents = cursor.fetchall()
                
                for doc in documents:
                    # Format the data for display
                    formatted_doc = list(doc)
                    file_name = os.path.basename(doc[3]) if doc[3] else 'Unknown'
                    formatted_doc[3] = file_name
                    if doc[5]:  # uploaded_at
                        formatted_doc[5] = doc[5][:10]  # Just the date part
                    
                    self.tree.insert('', 'end', values=formatted_doc)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load documents: {str(e)}")
            
    def filter_documents(self, event=None):
        """Filter documents by type"""
        selected_type = self.type_filter.get()
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                
                if selected_type == 'All':
                    cursor.execute("""
                        SELECT id, related_type, related_id, file_path, description, uploaded_at
                        FROM documents
                        ORDER BY uploaded_at DESC
                    """)
                else:
                    cursor.execute("""
                        SELECT id, related_type, related_id, file_path, description, uploaded_at
                        FROM documents
                        WHERE related_type = ?
                        ORDER BY uploaded_at DESC
                    """, (selected_type,))
                
                documents = cursor.fetchall()
                
                for doc in documents:
                    formatted_doc = list(doc)
                    file_name = os.path.basename(doc[3]) if doc[3] else 'Unknown'
                    formatted_doc[3] = file_name
                    if doc[5]:  # uploaded_at
                        formatted_doc[5] = doc[5][:10]
                    
                    self.tree.insert('', 'end', values=formatted_doc)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to filter documents: {str(e)}")
        
    def upload_document(self):
        """Open upload document dialog"""
        DocumentUploadDialog(self.parent_frame, self)
        
    def open_document(self, event=None):
        """Open selected document"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a document to open")
            return
            
        item = self.tree.item(selection[0])
        doc_id = item['values'][0]
        
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT file_path FROM documents WHERE id = ?", (doc_id,))
                result = cursor.fetchone()
                
                if result and result[0]:
                    file_path = result[0]
                    if os.path.exists(file_path):
                        os.startfile(file_path)  # Windows
                    else:
                        messagebox.showerror("Error", "File not found on disk")
                else:
                    messagebox.showerror("Error", "File path not found in database")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open document: {str(e)}")
        
    def edit_description(self):
        """Edit document description"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a document to edit")
            return
            
        item = self.tree.item(selection[0])
        doc_id = item['values'][0]
        current_description = item['values'][4]
        
        # Simple dialog for editing description
        dialog = tk.Toplevel(self.parent_frame)
        dialog.title("Edit Description")
        dialog.geometry("400x200")
        dialog.configure(bg='white')
        dialog.transient(self.parent_frame)
        dialog.grab_set()
        
        tk.Label(dialog, text="Document Description:", bg='white').pack(pady=10)
        
        text_widget = tk.Text(dialog, height=5, wrap='word')
        text_widget.pack(fill='both', expand=True, padx=20, pady=10)
        text_widget.insert(1.0, current_description)
        
        def save_description():
            new_description = text_widget.get(1.0, tk.END).strip()
            try:
                with sqlite3.connect(DB_FILE) as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE documents SET description = ? WHERE id = ?", 
                                 (new_description, doc_id))
                    conn.commit()
                
                messagebox.showinfo("Success", "Description updated successfully")
                dialog.destroy()
                self.load_documents()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update description: {str(e)}")
        
        button_frame = tk.Frame(dialog, bg='white')
        button_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Button(button_frame, text="Cancel", command=dialog.destroy,
                 bg='#f44336', fg='white').pack(side='right', padx=(10, 0))
        tk.Button(button_frame, text="Save", command=save_description,
                 bg='#4CAF50', fg='white').pack(side='right')
        
    def delete_document(self):
        """Delete selected document"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a document to delete")
            return
            
        item = self.tree.item(selection[0])
        doc_id = item['values'][0]
        file_name = item['values'][3]
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete '{file_name}'?\n\n"
                              "This will remove the document from the database and delete the file."):
            try:
                with sqlite3.connect(DB_FILE) as conn:
                    cursor = conn.cursor()
                    
                    # Get file path before deleting
                    cursor.execute("SELECT file_path FROM documents WHERE id = ?", (doc_id,))
                    result = cursor.fetchone()
                    
                    # Delete from database
                    cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
                    conn.commit()
                    
                    # Delete file if it exists
                    if result and result[0] and os.path.exists(result[0]):
                        os.remove(result[0])
                    
                messagebox.showinfo("Success", "Document deleted successfully")
                self.load_documents()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete document: {str(e)}")

class DocumentUploadDialog:
    def __init__(self, parent, document_manager):
        self.parent = parent
        self.document_manager = document_manager
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Upload Document")
        self.dialog.geometry("500x400")
        self.dialog.configure(bg='white')
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the upload dialog UI"""
        main_frame = tk.Frame(self.dialog, bg='white')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # File selection
        file_frame = tk.Frame(main_frame, bg='white')
        file_frame.pack(fill='x', pady=10)
        
        tk.Label(file_frame, text="Select File:", bg='white').pack(anchor='w')
        
        file_select_frame = tk.Frame(file_frame, bg='white')
        file_select_frame.pack(fill='x', pady=5)
        
        self.file_path_var = tk.StringVar()
        self.file_entry = tk.Entry(file_select_frame, textvariable=self.file_path_var, state='readonly')
        self.file_entry.pack(side='left', fill='x', expand=True)
        
        tk.Button(file_select_frame, text="Browse", command=self.browse_file,
                 bg='#2196F3', fg='white').pack(side='right', padx=(10, 0))
        
        # Document type
        type_frame = tk.Frame(main_frame, bg='white')
        type_frame.pack(fill='x', pady=10)
        
        tk.Label(type_frame, text="Document Type:", bg='white').pack(anchor='w')
        self.type_var = tk.StringVar()
        type_combo = ttk.Combobox(type_frame, textvariable=self.type_var, 
                                 values=['Property', 'Tenant', 'Lease', 'Payment', 'Expense'])
        type_combo.pack(fill='x', pady=5)
        
        # Related ID
        id_frame = tk.Frame(main_frame, bg='white')
        id_frame.pack(fill='x', pady=10)
        
        tk.Label(id_frame, text="Related ID:", bg='white').pack(anchor='w')
        self.id_entry = tk.Entry(id_frame)
        self.id_entry.pack(fill='x', pady=5)
        
        # Description
        desc_frame = tk.Frame(main_frame, bg='white')
        desc_frame.pack(fill='both', expand=True, pady=10)
        
        tk.Label(desc_frame, text="Description:", bg='white').pack(anchor='w')
        self.desc_text = tk.Text(desc_frame, height=4, wrap='word')
        self.desc_text.pack(fill='both', expand=True, pady=5)
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='white')
        button_frame.pack(fill='x', pady=(20, 0))
        
        tk.Button(button_frame, text="Cancel", command=self.dialog.destroy,
                 bg='#f44336', fg='white', padx=20).pack(side='right', padx=(10, 0))
        tk.Button(button_frame, text="Upload", command=self.upload_file,
                 bg='#4CAF50', fg='white', padx=20).pack(side='right')
        
    def browse_file(self):
        """Browse for file to upload"""
        file_path = filedialog.askopenfilename(
            title="Select Document",
            filetypes=[
                ("All Files", "*.*"),
                ("PDF Files", "*.pdf"),
                ("Word Documents", "*.doc *.docx"),
                ("Images", "*.jpg *.jpeg *.png *.gif"),
                ("Text Files", "*.txt")
            ]
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            
    def upload_file(self):
        """Upload the selected file"""
        file_path = self.file_path_var.get()
        doc_type = self.type_var.get()
        related_id = self.id_entry.get().strip()
        description = self.desc_text.get(1.0, tk.END).strip()
        
        if not file_path:
            messagebox.showerror("Error", "Please select a file to upload")
            return
            
        if not doc_type:
            messagebox.showerror("Error", "Please select a document type")
            return
            
        if not related_id:
            messagebox.showerror("Error", "Please enter a related ID")
            return
        
        try:
            # Validate related ID exists
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                
                # Check if related ID exists in the appropriate table
                table_map = {
                    'Property': 'properties',
                    'Tenant': 'tenants',
                    'Lease': 'leases',
                    'Payment': 'rent_payments',
                    'Expense': 'expenses'
                }
                
                table_name = table_map.get(doc_type)
                if table_name:
                    cursor.execute(f"SELECT id FROM {table_name} WHERE id = ?", (related_id,))
                    if not cursor.fetchone():
                        messagebox.showerror("Error", f"Invalid {doc_type} ID")
                        return
                
                # Copy file to documents directory
                file_name = os.path.basename(file_path)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_file_name = f"{timestamp}_{file_name}"
                new_file_path = os.path.join(self.document_manager.documents_dir, new_file_name)
                
                shutil.copy2(file_path, new_file_path)
                
                # Insert record into database
                cursor.execute("""
                    INSERT INTO documents (related_type, related_id, file_path, description)
                    VALUES (?, ?, ?, ?)
                """, (doc_type, related_id, new_file_path, description))
                
                conn.commit()
                
            messagebox.showinfo("Success", "Document uploaded successfully")
            self.dialog.destroy()
            self.document_manager.load_documents()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload document: {str(e)}")
