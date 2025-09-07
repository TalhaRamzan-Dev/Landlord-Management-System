import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
import os
from datetime import datetime, date
import calendar
from db import init_db, DB_FILE

class PropertyManagementApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🏠 Property Management System")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2c3e50')  # Dark blue background
        
        # Configure retro color scheme
        self.colors = {
            'primary': '#e74c3c',      # Retro red
            'secondary': '#f39c12',    # Retro orange
            'accent': '#27ae60',       # Retro green
            'background': '#2c3e50',   # Dark blue
            'surface': '#34495e',      # Darker blue
            'text': '#ecf0f1',         # Light gray
            'text_dark': '#2c3e50',    # Dark text
            'gold': '#f1c40f',         # Retro gold
            'purple': '#9b59b6'        # Retro purple
        }
        
        # Initialize database
        init_db()
        
        # Session management
        self.current_user = None
        self.is_logged_in = False
        
        # Create main frames
        self.login_frame = None
        self.main_frame = None
        
        # Start with login
        self.show_login()
        
    def show_login(self):
        """Display retro-styled login screen"""
        if self.main_frame:
            self.main_frame.destroy()
            
        self.login_frame = tk.Frame(self.root, bg=self.colors['background'])
        self.login_frame.pack(expand=True, fill='both')
        
        # Retro title
        title_frame = tk.Frame(self.login_frame, bg=self.colors['background'])
        title_frame.pack(pady=50)
        
        tk.Label(title_frame, text="🏠PROPERTY MANAGEMENT", 
                font=('Courier', 24, 'bold'), 
                bg=self.colors['background'], 
                fg=self.colors['gold']).pack()
        
        tk.Label(title_frame, text="Est. 1985 • Classic Real Estate Management", 
                font=('Courier', 12, 'italic'), 
                bg=self.colors['background'], 
                fg=self.colors['text']).pack(pady=10)
        
        # Login form with retro styling
        login_container = tk.Frame(self.login_frame, bg=self.colors['surface'], 
                                  relief='raised', bd=3)
        login_container.place(relx=0.5, rely=0.5, anchor='center')
        
        # Form title
        tk.Label(login_container, text="🔐 ADMIN ACCESS", 
                font=('Courier', 16, 'bold'), 
                bg=self.colors['surface'], 
                fg=self.colors['primary']).pack(pady=20)
        
        # Username field
        username_frame = tk.Frame(login_container, bg=self.colors['surface'])
        username_frame.pack(pady=10, padx=30, fill='x')
        
        tk.Label(username_frame, text="👤 Username:", 
                font=('Courier', 12, 'bold'), 
                bg=self.colors['surface'], 
                fg=self.colors['text']).pack(anchor='w')
        
        self.username_entry = tk.Entry(username_frame, width=30, 
                                      font=('Courier', 12),
                                      bg='white', fg=self.colors['text_dark'],
                                      relief='sunken', bd=2)
        self.username_entry.pack(pady=5, fill='x')
        
        # Password field
        password_frame = tk.Frame(login_container, bg=self.colors['surface'])
        password_frame.pack(pady=10, padx=30, fill='x')
        
        tk.Label(password_frame, text="🔑 Password:", 
                font=('Courier', 12, 'bold'), 
                bg=self.colors['surface'], 
                fg=self.colors['text']).pack(anchor='w')
        
        self.password_entry = tk.Entry(password_frame, width=30, show='*',
                                      font=('Courier', 12),
                                      bg='white', fg=self.colors['text_dark'],
                                      relief='sunken', bd=2)
        self.password_entry.pack(pady=5, fill='x')
        
        # Buttons with retro styling
        button_frame = tk.Frame(login_container, bg=self.colors['surface'])
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="🚀 LOGIN", command=self.login, 
                 bg=self.colors['accent'], fg='white', 
                 font=('Courier', 12, 'bold'),
                 width=20, height=2,
                 relief='raised', bd=3).pack(pady=5)
        
        tk.Button(button_frame, text="⚙️ SETUP ADMIN", command=self.setup_admin, 
                 bg=self.colors['secondary'], fg='white', 
                 font=('Courier', 12, 'bold'),
                 width=20, height=2,
                 relief='raised', bd=3).pack(pady=5)
        
        # Bind Enter key to login
        self.root.bind('<Return>', lambda e: self.login())
        
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
        
    def setup_admin(self):
        """Setup admin account for first time"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
            
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                
                # Check if admin already exists
                cursor.execute("SELECT id FROM admin WHERE username = ?", (username,))
                if cursor.fetchone():
                    messagebox.showerror("Error", "Admin account already exists")
                    return
                
                # Create admin account
                password_hash = self.hash_password(password)
                cursor.execute("INSERT INTO admin (username, password_hash) VALUES (?, ?)", 
                             (username, password_hash))
                conn.commit()
                
                messagebox.showinfo("Success", "Admin account created successfully!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create admin account: {str(e)}")
            
    def login(self):
        """Handle login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return
            
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                password_hash = self.hash_password(password)
                
                cursor.execute("SELECT id, username FROM admin WHERE username = ? AND password_hash = ?", 
                             (username, password_hash))
                user = cursor.fetchone()
                
                if user:
                    self.current_user = {'id': user[0], 'username': user[1]}
                    self.is_logged_in = True
                    self.show_main_app()
                else:
                    messagebox.showerror("Error", "Invalid username or password")
                    
        except Exception as e:
            messagebox.showerror("Error", f"Login failed: {str(e)}")
            
    def show_main_app(self):
        """Display main application interface"""
        if self.login_frame:
            self.login_frame.destroy()
            
        self.main_frame = tk.Frame(self.root, bg='#f0f0f0')
        self.main_frame.pack(fill='both', expand=True)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create main content area
        self.content_frame = tk.Frame(self.main_frame, bg='white')
        self.content_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Show dashboard by default
        self.show_dashboard()
        
    def create_menu_bar(self):
        """Create retro-styled navigation menu"""
        menu_frame = tk.Frame(self.main_frame, bg=self.colors['surface'], height=60)
        menu_frame.pack(fill='x')
        menu_frame.pack_propagate(False)
        
        # Welcome message
        welcome_frame = tk.Frame(menu_frame, bg=self.colors['surface'])
        welcome_frame.pack(side='left', padx=10, pady=10)
        
        tk.Label(welcome_frame, text=f"👋 Welcome, {self.current_user['username']}", 
                font=('Courier', 10, 'bold'), 
                bg=self.colors['surface'], 
                fg=self.colors['gold']).pack()
        
        # Menu buttons with retro styling
        buttons = [
            ("📊 Dashboard", self.show_dashboard, self.colors['accent']),
            ("🏠 Properties", self.show_properties, self.colors['primary']),
            ("👥 Tenants", self.show_tenants, self.colors['secondary']),
            ("📄 Leases", self.show_leases, self.colors['purple']),
            ("💰 Payments", self.show_payments, self.colors['gold']),
            ("📉 Expenses", self.show_expenses, self.colors['primary']),
            ("📂 Documents", self.show_documents, self.colors['accent']),
            ("🔧 Maintenance", self.show_maintenance, self.colors['secondary']),
            ("📈 Reports", self.show_reports, self.colors['purple'])
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(menu_frame, text=text, command=command, 
                           bg=color, fg='white', 
                           font=('Courier', 9, 'bold'),
                           relief='raised', bd=2,
                           padx=15, pady=8)
            btn.pack(side='left', padx=2)
            
        # Logout button
        logout_btn = tk.Button(menu_frame, text="🚪 LOGOUT", command=self.logout, 
                              bg=self.colors['primary'], fg='white', 
                              font=('Courier', 9, 'bold'),
                              relief='raised', bd=2,
                              padx=15, pady=8)
        logout_btn.pack(side='right', padx=10)
        
    def logout(self):
        """Handle logout"""
        self.current_user = None
        self.is_logged_in = False
        self.show_login()
        
    def clear_content(self):
        """Clear content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
    def show_dashboard(self):
        """Show retro-styled dashboard with summary information"""
        self.clear_content()
        
        # Dashboard title with retro styling
        title_frame = tk.Frame(self.content_frame, bg=self.colors['surface'])
        title_frame.pack(fill='x', pady=10)
        
        tk.Label(title_frame, text="📊 DASHBOARD", 
                font=('Courier', 20, 'bold'), 
                bg=self.colors['surface'], 
                fg=self.colors['gold']).pack(side='left')
        
        tk.Label(title_frame, text="Real-time Property Analytics", 
                font=('Courier', 10, 'italic'), 
                bg=self.colors['surface'], 
                fg=self.colors['text']).pack(side='right', pady=5)
        
        # Summary cards with retro styling
        cards_frame = tk.Frame(self.content_frame, bg=self.colors['background'])
        cards_frame.pack(fill='x', pady=20)
        
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                
                # Get summary data
                cursor.execute("SELECT COUNT(*) FROM properties")
                total_properties = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM properties WHERE status = 'Occupied'")
                occupied_properties = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM tenants")
                total_tenants = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM maintenance_requests WHERE status = 'Open'")
                open_maintenance = cursor.fetchone()[0]
                
                # Get financial data
                cursor.execute("SELECT SUM(amount_paid) FROM rent_payments WHERE status = 'Paid'")
                total_income = cursor.fetchone()[0] or 0
                
                cursor.execute("SELECT SUM(amount) FROM expenses")
                total_expenses = cursor.fetchone()[0] or 0
                
                # Get overdue payments
                cursor.execute("SELECT COUNT(*) FROM rent_payments WHERE status = 'Overdue'")
                overdue_payments = cursor.fetchone()[0]
                
                # Create retro-styled summary cards
                cards = [
                    ("🏠 Total Properties", total_properties, self.colors['primary']),
                    ("✅ Occupied Properties", occupied_properties, self.colors['accent']),
                    ("👥 Total Tenants", total_tenants, self.colors['secondary']),
                    ("🔧 Open Maintenance", open_maintenance, self.colors['purple']),
                    ("💰 Total Income", f"Rs {total_income:.2f}", self.colors['gold']),
                    ("📉 Total Expenses", f"Rs {total_expenses:.2f}", self.colors['primary']),
                    ("⚠️ Overdue Payments", overdue_payments, self.colors['primary']),
                    ("📈 Net Profit", f"Rs {total_income - total_expenses:.2f}", self.colors['accent'])
                ]
                
                for i, (title, value, color) in enumerate(cards):
                    card = tk.Frame(cards_frame, bg=color, relief='raised', bd=3)
                    card.grid(row=i//4, column=i%4, padx=8, pady=8, sticky='ew')
                    cards_frame.grid_columnconfigure(i%4, weight=1)
                    
                    tk.Label(card, text=str(value), font=('Courier', 18, 'bold'), 
                            bg=color, fg='white').pack(pady=10)
                    tk.Label(card, text=title, font=('Courier', 9, 'bold'), 
                            bg=color, fg='white').pack(pady=2)
                
                # Recent activity section with retro styling
                activity_frame = tk.LabelFrame(self.content_frame, 
                                             text="📋 RECENT ACTIVITY", 
                                             bg=self.colors['surface'],
                                             fg=self.colors['gold'],
                                             font=('Courier', 12, 'bold'))
                activity_frame.pack(fill='both', expand=True, pady=20)
                
                # Recent payments
                cursor.execute("""
                    SELECT t.name, rp.amount_paid, rp.payment_date, rp.status
                    FROM rent_payments rp
                    JOIN tenants t ON rp.tenant_id = t.id
                    ORDER BY rp.payment_date DESC
                    LIMIT 5
                """)
                recent_payments = cursor.fetchall()
                
                payments_text = "Recent Payments:\n"
                for payment in recent_payments:
                    payments_text += f"• {payment[0]}: Rs {payment[1]:.2f} ({payment[2][:10]}) - {payment[3]}\n"
                
                # Recent maintenance requests
                cursor.execute("""
                    SELECT mr.description, mr.status, mr.request_date
                    FROM maintenance_requests mr
                    ORDER BY mr.request_date DESC
                    LIMIT 5
                """)
                recent_maintenance = cursor.fetchall()
                
                maintenance_text = "\nRecent Maintenance Requests:\n"
                for maintenance in recent_maintenance:
                    maintenance_text += f"• {maintenance[0][:50]}... ({maintenance[2][:10]}) - {maintenance[1]}\n"
                
                activity_text = payments_text + maintenance_text
                
                activity_display = tk.Text(activity_frame, height=10, wrap='word', state='disabled',
                                          bg=self.colors['background'], fg=self.colors['text'],
                                          font=('Courier', 10))
                activity_display.pack(fill='both', expand=True, padx=10, pady=10)
                activity_display.config(state='normal')
                activity_display.insert(1.0, activity_text)
                activity_display.config(state='disabled')
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load dashboard: {str(e)}")
            
    def show_properties(self):
        """Show properties management interface"""
        self.clear_content()
        from property_manager import PropertyManager
        PropertyManager(self.content_frame)
        
    def show_tenants(self):
        """Show tenants management interface"""
        self.clear_content()
        from tenant_manager import TenantManager
        TenantManager(self.content_frame)
        
    def show_leases(self):
        """Show leases management interface"""
        self.clear_content()
        from lease_manager import LeaseManager
        LeaseManager(self.content_frame)
        
    def show_payments(self):
        """Show payments management interface"""
        self.clear_content()
        from payment_manager import PaymentManager
        PaymentManager(self.content_frame)
        
    def show_expenses(self):
        """Show expenses management interface"""
        self.clear_content()
        from expense_manager import ExpenseManager
        ExpenseManager(self.content_frame)
        
    def show_documents(self):
        """Show documents management interface"""
        self.clear_content()
        from document_manager import DocumentManager
        DocumentManager(self.content_frame)
        
    def show_maintenance(self):
        """Show maintenance management interface"""
        self.clear_content()
        from maintenance_manager import MaintenanceManager
        MaintenanceManager(self.content_frame)
        
    def show_reports(self):
        """Show reports interface"""
        self.clear_content()
        from reports_manager import ReportsManager
        ReportsManager(self.content_frame)
        
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = PropertyManagementApp()
    app.run()
