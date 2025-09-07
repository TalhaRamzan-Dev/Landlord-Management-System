import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime, date, timedelta
import csv
from db import DB_FILE

class ReportsManager:
    def __init__(self, parent_frame):
        self.parent_frame = parent_frame
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the reports management UI"""
        # Main container
        main_container = tk.Frame(self.parent_frame, bg='white')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header with title
        header_frame = tk.Frame(main_container, bg='white')
        header_frame.pack(fill='x', pady=(0, 20))
        
        tk.Label(header_frame, text="Reports & Analytics", 
                font=('Arial', 18, 'bold'), bg='white').pack(side='left')
        
        # Report selection frame
        selection_frame = tk.LabelFrame(main_container, text="Select Report", bg='white')
        selection_frame.pack(fill='x', pady=(0, 20))
        
        # Report buttons
        reports_frame = tk.Frame(selection_frame, bg='white')
        reports_frame.pack(fill='x', padx=10, pady=10)
        
        reports = [
            ("Property Occupancy Report", self.property_occupancy_report),
            ("Rent Income Report", self.rent_income_report),
            ("Expense Analysis Report", self.expense_analysis_report),
            ("Overdue Rent Report", self.overdue_rent_report),
            ("Lease Expiration Report", self.lease_expiration_report),
            ("Maintenance Cost Report", self.maintenance_cost_report),
            ("Financial Summary Report", self.financial_summary_report),
            ("Export All Data", self.export_all_data)
        ]
        
        for i, (title, command) in enumerate(reports):
            btn = tk.Button(reports_frame, text=title, command=command,
                           bg='#2196F3', fg='white', padx=20, pady=10, width=25)
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky='ew')
            reports_frame.grid_columnconfigure(i%2, weight=1)
        
        # Report display area
        self.report_frame = tk.LabelFrame(main_container, text="Report Results", bg='white')
        self.report_frame.pack(fill='both', expand=True)
        
        # Text widget for report display
        self.report_text = tk.Text(self.report_frame, wrap='word', state='disabled', 
                                  font=('Courier', 10))
        scrollbar = ttk.Scrollbar(self.report_frame, orient='vertical', command=self.report_text.yview)
        self.report_text.configure(yscrollcommand=scrollbar.set)
        
        self.report_text.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        scrollbar.pack(side='right', fill='y')
        
    def display_report(self, title, content):
        """Display report content"""
        self.report_text.config(state='normal')
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(1.0, f"{title}\n{'='*len(title)}\n\n{content}")
        self.report_text.config(state='disabled')
        
    def property_occupancy_report(self):
        """Generate property occupancy report"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT p.id, COALESCE(p.name, 'Property #' || p.id) as property_name,
                           p.address, p.status, p.rent_amount,
                           COALESCE(t.name, 'No Tenant') as tenant_name,
                           l.start_date, l.end_date
                    FROM properties p
                    LEFT JOIN tenants t ON p.id = t.property_id
                    LEFT JOIN leases l ON t.id = l.tenant_id AND l.status = 'Active'
                    ORDER BY p.id
                """)
                
                properties = cursor.fetchall()
                
                report = "PROPERTY OCCUPANCY REPORT\n"
                report += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                
                occupied_count = 0
                vacant_count = 0
                total_rent = 0
                
                for prop in properties:
                    prop_id, name, address, status, rent, tenant, start_date, end_date = prop
                    
                    report += f"Property ID: {prop_id}\n"
                    report += f"Name: {name}\n"
                    report += f"Address: {address}\n"
                    report += f"Status: {status}\n"
                    report += f"Rent Amount: RS{rent:.2f}\n"
                    report += f"Current Tenant: {tenant}\n"
                    
                    if start_date:
                        report += f"Lease Start: {start_date[:10]}\n"
                    if end_date:
                        report += f"Lease End: {end_date[:10]}\n"
                    
                    report += "-" * 50 + "\n"
                    
                    if status == 'Occupied':
                        occupied_count += 1
                        total_rent += rent
                    else:
                        vacant_count += 1
                
                report += f"\nSUMMARY:\n"
                report += f"Total Properties: {len(properties)}\n"
                report += f"Occupied: {occupied_count}\n"
                report += f"Vacant: {vacant_count}\n"
                report += f"Occupancy Rate: {(occupied_count/len(properties)*100):.1f}%\n"
                report += f"Total Monthly Rent: RS{total_rent:.2f}\n"
                
                self.display_report("Property Occupancy Report", report)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def rent_income_report(self):
        """Generate rent income report"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                
                # Monthly income for last 12 months
                cursor.execute("""
                    SELECT month, SUM(amount_paid) as total_paid, COUNT(*) as payment_count
                    FROM rent_payments 
                    WHERE status = 'Paid' AND payment_date >= date('now', '-12 months')
                    GROUP BY month
                    ORDER BY month DESC
                """)
                
                monthly_data = cursor.fetchall()
                
                # Total income by status
                cursor.execute("""
                    SELECT status, SUM(amount_paid) as total, COUNT(*) as count
                    FROM rent_payments
                    GROUP BY status
                """)
                
                status_data = cursor.fetchall()
                
                report = "RENT INCOME REPORT\n"
                report += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                
                report += "MONTHLY INCOME (Last 12 Months):\n"
                report += "-" * 40 + "\n"
                
                total_monthly_income = 0
                for month, total, count in monthly_data:
                    report += f"{month}: RS{total:.2f} ({count} payments)\n"
                    total_monthly_income += total
                
                report += f"\nTotal Monthly Income: RS{total_monthly_income:.2f}\n\n"
                
                report += "PAYMENT STATUS SUMMARY:\n"
                report += "-" * 40 + "\n"
                
                for status, total, count in status_data:
                    report += f"{status}: RS{total:.2f} ({count} payments)\n"
                
                self.display_report("Rent Income Report", report)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def expense_analysis_report(self):
        """Generate expense analysis report"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                
                # Expenses by category
                cursor.execute("""
                    SELECT category, SUM(amount) as total, COUNT(*) as count
                    FROM expenses
                    GROUP BY category
                    ORDER BY total DESC
                """)
                
                category_data = cursor.fetchall()
                
                # Expenses by property
                cursor.execute("""
                    SELECT COALESCE(p.name, 'Property #' || p.id) as property_name,
                           SUM(e.amount) as total, COUNT(*) as count
                    FROM expenses e
                    JOIN properties p ON e.property_id = p.id
                    GROUP BY e.property_id, property_name
                    ORDER BY total DESC
                """)
                
                property_data = cursor.fetchall()
                
                # Monthly expenses
                cursor.execute("""
                    SELECT strftime('%Y-%m', date) as month, SUM(amount) as total
                    FROM expenses
                    WHERE date >= date('now', '-12 months')
                    GROUP BY month
                    ORDER BY month DESC
                """)
                
                monthly_data = cursor.fetchall()
                
                report = "EXPENSE ANALYSIS REPORT\n"
                report += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                
                report += "EXPENSES BY CATEGORY:\n"
                report += "-" * 40 + "\n"
                
                total_expenses = 0
                for category, total, count in category_data:
                    report += f"{category or 'Uncategorized'}: RS{total:.2f} ({count} expenses)\n"
                    total_expenses += total
                
                report += f"\nTotal Expenses: RS{total_expenses:.2f}\n\n"
                
                report += "EXPENSES BY PROPERTY:\n"
                report += "-" * 40 + "\n"
                
                for property_name, total, count in property_data:
                    report += f"{property_name}: RS{total:.2f} ({count} expenses)\n"
                
                report += "\nMONTHLY EXPENSES (Last 12 Months):\n"
                report += "-" * 40 + "\n"
                
                for month, total in monthly_data:
                    report += f"{month}: RS{total:.2f}\n"
                
                self.display_report("Expense Analysis Report", report)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def overdue_rent_report(self):
        """Generate overdue rent report"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT t.name, COALESCE(p.name, 'Property #' || p.id) as property_name,
                           rp.month, rp.due_date, rp.amount_due, rp.amount_paid,
                           (rp.amount_due - rp.amount_paid) as outstanding
                    FROM rent_payments rp
                    JOIN tenants t ON rp.tenant_id = t.id
                    JOIN properties p ON rp.property_id = p.id
                    WHERE rp.status = 'Overdue' OR (rp.amount_due > rp.amount_paid AND rp.due_date < date('now'))
                    ORDER BY rp.due_date
                """)
                
                overdue_data = cursor.fetchall()
                
                report = "OVERDUE RENT REPORT\n"
                report += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                
                if not overdue_data:
                    report += "No overdue payments found.\n"
                else:
                    report += "OVERDUE PAYMENTS:\n"
                    report += "-" * 80 + "\n"
                    report += f"{'Tenant':<20} {'Property':<20} {'Month':<10} {'Due Date':<12} {'Outstanding':<12}\n"
                    report += "-" * 80 + "\n"
                    
                    total_outstanding = 0
                    for tenant, property, month, due_date, amount_due, amount_paid, outstanding in overdue_data:
                        report += f"{tenant:<20} {property:<20} {month:<10} {due_date[:10]:<12} RS{outstanding:<11.2f}\n"
                        total_outstanding += outstanding
                    
                    report += "-" * 80 + "\n"
                    report += f"Total Outstanding: RS{total_outstanding:.2f}\n"
                
                self.display_report("Overdue Rent Report", report)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def lease_expiration_report(self):
        """Generate lease expiration report"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                
                # Upcoming expirations (next 3 months)
                cursor.execute("""
                    SELECT t.name, COALESCE(p.name, 'Property #' || p.id) as property_name,
                           l.start_date, l.end_date, l.rent_amount
                    FROM leases l
                    JOIN tenants t ON l.tenant_id = t.id
                    JOIN properties p ON l.property_id = p.id
                    WHERE l.status = 'Active' AND l.end_date BETWEEN date('now') AND date('now', '+3 months')
                    ORDER BY l.end_date
                """)
                
                upcoming_data = cursor.fetchall()
                
                # Recently expired
                cursor.execute("""
                    SELECT t.name, COALESCE(p.name, 'Property #' || p.id) as property_name,
                           l.start_date, l.end_date, l.rent_amount, l.status
                    FROM leases l
                    JOIN tenants t ON l.tenant_id = t.id
                    JOIN properties p ON l.property_id = p.id
                    WHERE l.end_date < date('now') AND l.status IN ('Active', 'Expired')
                    ORDER BY l.end_date DESC
                """)
                
                expired_data = cursor.fetchall()
                
                report = "LEASE EXPIRATION REPORT\n"
                report += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                
                report += "UPCOMING EXPIRATIONS (Next 3 Months):\n"
                report += "-" * 80 + "\n"
                
                if not upcoming_data:
                    report += "No leases expiring in the next 3 months.\n"
                else:
                    for tenant, property, start_date, end_date, rent in upcoming_data:
                        report += f"Tenant: {tenant}\n"
                        report += f"Property: {property}\n"
                        report += f"Lease Period: {start_date[:10]} to {end_date[:10]}\n"
                        report += f"Rent: RS{rent:.2f}\n"
                        report += "-" * 40 + "\n"
                
                report += "\nRECENTLY EXPIRED LEASES:\n"
                report += "-" * 80 + "\n"
                
                if not expired_data:
                    report += "No recently expired leases.\n"
                else:
                    for tenant, property, start_date, end_date, rent, status in expired_data:
                        report += f"Tenant: {tenant}\n"
                        report += f"Property: {property}\n"
                        report += f"Lease Period: {start_date[:10]} to {end_date[:10]}\n"
                        report += f"Rent: RS{rent:.2f}\n"
                        report += f"Status: {status}\n"
                        report += "-" * 40 + "\n"
                
                self.display_report("Lease Expiration Report", report)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def maintenance_cost_report(self):
        """Generate maintenance cost report"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                
                # Maintenance costs by property
                cursor.execute("""
                    SELECT COALESCE(p.name, 'Property #' || p.id) as property_name,
                           COUNT(*) as request_count,
                           SUM(COALESCE(mr.actual_cost, mr.cost_estimate, 0)) as total_cost,
                           AVG(COALESCE(mr.actual_cost, mr.cost_estimate, 0)) as avg_cost
                    FROM maintenance_requests mr
                    JOIN properties p ON mr.property_id = p.id
                    GROUP BY mr.property_id, property_name
                    ORDER BY total_cost DESC
                """)
                
                property_data = cursor.fetchall()
                
                # Maintenance by status
                cursor.execute("""
                    SELECT status, COUNT(*) as count,
                           SUM(COALESCE(actual_cost, cost_estimate, 0)) as total_cost
                    FROM maintenance_requests
                    GROUP BY status
                """)
                
                status_data = cursor.fetchall()
                
                # Recent maintenance requests
                cursor.execute("""
                    SELECT mr.description, COALESCE(p.name, 'Property #' || p.id) as property_name,
                           mr.status, mr.actual_cost, mr.cost_estimate, mr.completed_date
                    FROM maintenance_requests mr
                    JOIN properties p ON mr.property_id = p.id
                    ORDER BY mr.request_date DESC
                    LIMIT 10
                """)
                
                recent_data = cursor.fetchall()
                
                report = "MAINTENANCE COST REPORT\n"
                report += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                
                report += "MAINTENANCE COSTS BY PROPERTY:\n"
                report += "-" * 60 + "\n"
                
                total_maintenance_cost = 0
                for property_name, count, total, avg in property_data:
                    report += f"{property_name}:\n"
                    report += f"  Requests: {count}\n"
                    report += f"  Total Cost: RS{total:.2f}\n"
                    report += f"  Average Cost: RS{avg:.2f}\n"
                    report += "-" * 40 + "\n"
                    total_maintenance_cost += total
                
                report += f"Total Maintenance Cost: RS{total_maintenance_cost:.2f}\n\n"
                
                report += "MAINTENANCE BY STATUS:\n"
                report += "-" * 40 + "\n"
                
                for status, count, total in status_data:
                    report += f"{status}: {count} requests, RS{total:.2f}\n"
                
                report += "\nRECENT MAINTENANCE REQUESTS:\n"
                report += "-" * 80 + "\n"
                
                for description, property, status, actual, estimate, completed in recent_data:
                    cost = actual if actual else estimate
                    report += f"Property: {property}\n"
                    report += f"Description: {description[:50]}...\n"
                    report += f"Status: {status}\n"
                    report += f"Cost: RS{cost:.2f if cost else 0:.2f}\n"
                    if completed:
                        report += f"Completed: {completed[:10]}\n"
                    report += "-" * 40 + "\n"
                
                self.display_report("Maintenance Cost Report", report)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def financial_summary_report(self):
        """Generate comprehensive financial summary report"""
        try:
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                
                # Total income
                cursor.execute("SELECT SUM(amount_paid) FROM rent_payments WHERE status = 'Paid'")
                total_income = cursor.fetchone()[0] or 0
                
                # Total expenses
                cursor.execute("SELECT SUM(amount) FROM expenses")
                total_expenses = cursor.fetchone()[0] or 0
                
                # Outstanding rent
                cursor.execute("""
                    SELECT SUM(amount_due - amount_paid) 
                    FROM rent_payments 
                    WHERE amount_due > amount_paid
                """)
                outstanding_rent = cursor.fetchone()[0] or 0
                
                # Monthly income (current year)
                cursor.execute("""
                    SELECT strftime('%Y-%m', payment_date) as month, SUM(amount_paid)
                    FROM rent_payments 
                    WHERE status = 'Paid' AND strftime('%Y', payment_date) = strftime('%Y', 'now')
                    GROUP BY month
                    ORDER BY month
                """)
                monthly_income = cursor.fetchall()
                
                # Monthly expenses (current year)
                cursor.execute("""
                    SELECT strftime('%Y-%m', date) as month, SUM(amount)
                    FROM expenses 
                    WHERE strftime('%Y', date) = strftime('%Y', 'now')
                    GROUP BY month
                    ORDER BY month
                """)
                monthly_expenses = cursor.fetchall()
                
                report = "FINANCIAL SUMMARY REPORT\n"
                report += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                
                report += "OVERALL FINANCIAL SUMMARY:\n"
                report += "-" * 40 + "\n"
                report += f"Total Income: RS{total_income:.2f}\n"
                report += f"Total Expenses: RS{total_expenses:.2f}\n"
                report += f"Net Profit: RS{total_income - total_expenses:.2f}\n"
                report += f"Outstanding Rent: RS{outstanding_rent:.2f}\n"
                report += f"Profit Margin: {((total_income - total_expenses) / total_income * 100):.1f}%\n\n"
                
                report += "MONTHLY INCOME (Current Year):\n"
                report += "-" * 40 + "\n"
                
                for month, income in monthly_income:
                    report += f"{month}: RS{income:.2f}\n"
                
                report += "\nMONTHLY EXPENSES (Current Year):\n"
                report += "-" * 40 + "\n"
                
                for month, expenses in monthly_expenses:
                    report += f"{month}: RS{expenses:.2f}\n"
                
                self.display_report("Financial Summary Report", report)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
    
    def export_all_data(self):
        """Export all data to CSV files"""
        try:
            # Ask user for export directory
            export_dir = filedialog.askdirectory(title="Select Export Directory")
            if not export_dir:
                return
            
            with sqlite3.connect(DB_FILE) as conn:
                cursor = conn.cursor()
                
                # Export properties
                cursor.execute("SELECT * FROM properties")
                properties = cursor.fetchall()
                cursor.execute("PRAGMA table_info(properties)")
                property_columns = [col[1] for col in cursor.fetchall()]
                
                with open(f"{export_dir}/properties.csv", 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(property_columns)
                    writer.writerows(properties)
                
                # Export tenants
                cursor.execute("SELECT * FROM tenants")
                tenants = cursor.fetchall()
                cursor.execute("PRAGMA table_info(tenants)")
                tenant_columns = [col[1] for col in cursor.fetchall()]
                
                with open(f"{export_dir}/tenants.csv", 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(tenant_columns)
                    writer.writerows(tenants)
                
                # Export leases
                cursor.execute("SELECT * FROM leases")
                leases = cursor.fetchall()
                cursor.execute("PRAGMA table_info(leases)")
                lease_columns = [col[1] for col in cursor.fetchall()]
                
                with open(f"{export_dir}/leases.csv", 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(lease_columns)
                    writer.writerows(leases)
                
                # Export rent payments
                cursor.execute("SELECT * FROM rent_payments")
                payments = cursor.fetchall()
                cursor.execute("PRAGMA table_info(rent_payments)")
                payment_columns = [col[1] for col in cursor.fetchall()]
                
                with open(f"{export_dir}/rent_payments.csv", 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(payment_columns)
                    writer.writerows(payments)
                
                # Export expenses
                cursor.execute("SELECT * FROM expenses")
                expenses = cursor.fetchall()
                cursor.execute("PRAGMA table_info(expenses)")
                expense_columns = [col[1] for col in cursor.fetchall()]
                
                with open(f"{export_dir}/expenses.csv", 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(expense_columns)
                    writer.writerows(expenses)
                
                # Export maintenance requests
                cursor.execute("SELECT * FROM maintenance_requests")
                maintenance = cursor.fetchall()
                cursor.execute("PRAGMA table_info(maintenance_requests)")
                maintenance_columns = [col[1] for col in cursor.fetchall()]
                
                with open(f"{export_dir}/maintenance_requests.csv", 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(maintenance_columns)
                    writer.writerows(maintenance)
            
            messagebox.showinfo("Success", f"All data exported successfully to:\n{export_dir}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")
