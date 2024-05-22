import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import errorcode
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from sklearn.linear_model import LinearRegression
import os
import csv
import threading
script_dir = os.path.dirname(__file__)
os.chdir(script_dir)
DB_NAME = 'BankDB'
TABLES = {
    'Branch': (
        "CREATE TABLE IF NOT EXISTS Branch ("
        "  Branch_Name VARCHAR(100) PRIMARY KEY,"
        "  Contact_Number VARCHAR(50),"
        "  Manager VARCHAR(100),"
        "  City VARCHAR(100),"
        "  Address VARCHAR(200)"
        ") ENGINE=InnoDB"),
    'Department': (
        "CREATE TABLE IF NOT EXISTS Department ("
        "  Department_Name VARCHAR(100) NOT NULL,"
        "  Branch_Name VARCHAR(100) NOT NULL,"
        "  Contact_Number VARCHAR(50),"
        "  FOREIGN KEY (Branch_Name) REFERENCES Branch(Branch_Name) ON DELETE CASCADE"
        ") ENGINE=InnoDB"),
    'Employee': (
        "CREATE TABLE IF NOT EXISTS Employee ("
        "  Employee_ID INT PRIMARY KEY AUTO_INCREMENT,"
        "  Name VARCHAR(200),"
        "  Branch_Name VARCHAR(100) NOT NULL,"
        "  FOREIGN KEY (Branch_Name) REFERENCES Branch(Branch_Name) ON DELETE CASCADE"
        ") ENGINE=InnoDB"),
    'Customer': (
        "CREATE TABLE IF NOT EXISTS Customer ("
        "  Customer_ID INT PRIMARY KEY AUTO_INCREMENT,"
        "  Name VARCHAR(200),"
        "  Address VARCHAR(200),"
        "  Contact_Number VARCHAR(50)"
        ") ENGINE=InnoDB"),
    'Account': (
        "CREATE TABLE IF NOT EXISTS Account ("
        "  Account_Number INT PRIMARY KEY,"
        "  Account_Type VARCHAR(50),"
        "  Balance DECIMAL(10,2),"
        "  Opening_Date DATE,"
        "  Customer_ID INT NOT NULL,"
        "  FOREIGN KEY (Customer_ID) REFERENCES Customer(Customer_ID) ON DELETE CASCADE"
        ") ENGINE=InnoDB"),
    'Loan': (
        "CREATE TABLE IF NOT EXISTS Loan ("
        "  Loan_ID INT PRIMARY KEY AUTO_INCREMENT,"
        "  Loan_Type VARCHAR(100),"
        "  Loan_Date DATE,"
        "  Amount DECIMAL(10,2),"
        "  Customer_ID INT NOT NULL,"
        "  FOREIGN KEY (Customer_ID) REFERENCES Customer(Customer_ID) ON DELETE CASCADE"
        ") ENGINE=InnoDB"),
    'Transaction': (
        "CREATE TABLE IF NOT EXISTS Transaction ("
        "  Transaction_ID INT PRIMARY KEY AUTO_INCREMENT,"
        "  Transaction_Type VARCHAR(50),"
        "  Amount DECIMAL(10,2),"
        "  Transaction_Date DATE,"
        "  Account_Number INT NOT NULL,"
        "  FOREIGN KEY (Account_Number) REFERENCES Account(Account_Number) ON DELETE CASCADE"
        ") ENGINE=InnoDB")
}
def create_database(cursor):
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} DEFAULT CHARACTER SET 'utf8'")
        cursor.execute(f"USE {DB_NAME}")
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)
def connect_db():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='rajagam',
            password='1123',  
            database=DB_NAME  
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        raise
def create_tables(cursor):
    for table_name, ddl in TABLES.items():
        try:
            cursor.execute(ddl)
        except mysql.connector.Error as err:
            if err.errno != errorcode.ER_TABLE_EXISTS_ERROR:
                print(err.msg)
class BankApp:
    def __init__(self, root):
        self.root = root
        self.setup_ui()
        self.auto_refresh(300)
        self.dataframe = pd.DataFrame()
        self.display_data()
        self.root.title("Raj ka Bank")
        self.root.configure(bg='#333')
        self.conn = connect_db()
        self.cursor = self.conn.cursor()
        self.tabControl = ttk.Notebook(root, style='TNotebook')
        self.tabAccountCreation = ttk.Frame(self.tabControl, style='TFrame')
        self.tabCustomer = ttk.Frame(self.tabControl, style='TFrame')
        self.tabAdmin = ttk.Frame(self.tabControl, style='TFrame')
        self.tabML = ttk.Frame(self.tabControl, style='TFrame')
        self.tabControl.add(self.tabAccountCreation, text='Create Account')
        self.tabControl.add(self.tabCustomer, text='Customer Operations')
        self.tabControl.add(self.tabAdmin, text='Admin Panel')
        self.tabControl.add(self.tabML, text='ML Insights')
        self.tabControl.pack(expand=1, fill="both")
        self.create_account_creation_tab()
        self.create_customer_tab()
        self.create_admin_tab()
        self.create_ml_tab() 
    def setup_ui(self):
        refresh_button = ttk.Button(self.root, text="Refresh Data", command=self.refresh_data)
        refresh_button.pack()
    def refresh_data(self):
        self.dataframe = self.read_from_csv()
        self.display_data()
        print("Data refreshed")
    def create_account_creation_tab(self):
        ttk.Label(self.tabAccountCreation, text="Raj ka Bank", style='Title.TLabel').grid(column=0, row=0, columnspan=2, pady=10)
        ttk.Label(self.tabAccountCreation, text="Name:", style='Label.TLabel').grid(column=0, row=1, sticky=tk.W, padx=10, pady=5)
        self.name_var = ttk.Entry(self.tabAccountCreation, style='Entry.TEntry')
        self.name_var.grid(column=1, row=1, padx=10, pady=5)
        ttk.Label(self.tabAccountCreation, text="Address:", style='Label.TLabel').grid(column=0, row=2, sticky=tk.W, padx=10, pady=5)
        self.address_var = ttk.Entry(self.tabAccountCreation, style='Entry.TEntry')
        self.address_var.grid(column=1, row=2, padx=10, pady=5)
        ttk.Label(self.tabAccountCreation, text="Contact Number:", style='Label.TLabel').grid(column=0, row=3, sticky=tk.W, padx=10, pady=5)
        self.contact_var = ttk.Entry(self.tabAccountCreation, style='Entry.TEntry')
        self.contact_var.grid(column=1, row=3, padx=10, pady=5)
        ttk.Label(self.tabAccountCreation, text="Account Number:", style='Label.TLabel').grid(column=0, row=4, sticky=tk.W, padx=10, pady=5)
        self.account_number_var = ttk.Entry(self.tabAccountCreation, style='Entry.TEntry')
        self.account_number_var.grid(column=1, row=4, padx=10, pady=5)
        ttk.Label(self.tabAccountCreation, text="Account Type:", style='Label.TLabel').grid(column=0, row=5, sticky=tk.W, padx=10, pady=5)
        self.account_type_var = ttk.Entry(self.tabAccountCreation, style='Entry.TEntry')
        self.account_type_var.grid(column=1, row=5, padx=10, pady=5)
        ttk.Button(self.tabAccountCreation, text="Create Account", style='Button.TButton', command=self.create_account).grid(column=0, row=6, columnspan=2, pady=10)
    def create_customer_tab(self):
        ttk.Label(self.tabCustomer, text="Customer Operations", style='Title.TLabel').grid(column=0, row=0, columnspan=2, pady=10)
        ttk.Label(self.tabCustomer, text="Account Number:", style='Label.TLabel').grid(column=0, row=1, sticky=tk.W, padx=10, pady=5)
        self.account_number_customer_var = ttk.Entry(self.tabCustomer, style='Entry.TEntry')
        self.account_number_customer_var.grid(column=1, row=1, padx=10, pady=5)
        ttk.Label(self.tabCustomer, text="Amount:", style='Label.TLabel').grid(column=0, row=2, sticky=tk.W, padx=10, pady=5)
        self.transaction_amount_var = ttk.Entry(self.tabCustomer, style='Entry.TEntry')
        self.transaction_amount_var.grid(column=1, row=2, padx=10, pady=5)
        ttk.Button(self.tabCustomer, text="Deposit", style='Button.TButton', command=lambda: self.process_transaction("Deposit")).grid(column=0, row=3, padx=10, pady=10)
        ttk.Button(self.tabCustomer, text="Withdraw", style='Button.TButton', command=lambda: self.process_transaction("Withdraw")).grid(column=1, row=3, padx=10, pady=10)
        ttk.Button(self.tabCustomer, text="Take Loan", style='Button.TButton', command=self.take_loan).grid(column=1, row=4, padx=10, pady=10)
    def create_admin_tab(self):
        ttk.Label(self.tabAdmin, text="Admin Panel", style='Title.TLabel').grid(column=0, row=0, columnspan=4, pady=10)
        ttk.Label(self.tabAdmin, text="Account Number:", style='Label.TLabel').grid(column=0, row=1, sticky=tk.W, padx=10, pady=5)
        self.account_number_admin_var = ttk.Entry(self.tabAdmin, style='Entry.TEntry')
        self.account_number_admin_var.grid(column=1, row=1, padx=10, pady=5)
        ttk.Label(self.tabAdmin, text="Amount to Set:", style='Label.TLabel').grid(column=2, row=1, sticky=tk.W, padx=10, pady=5)
        self.set_amount_var = ttk.Entry(self.tabAdmin, style='Entry.TEntry')
        self.set_amount_var.grid(column=3, row=1, padx=10, pady=5)
        ttk.Button(self.tabAdmin, text="Remove Account", style='Button.TButton', command=self.remove_account).grid(column=0, row=2, padx=10, pady=10)
        ttk.Button(self.tabAdmin, text="Set Balance", style='Button.TButton', command=lambda: self.modify_balance(True)).grid(column=1, row=2, padx=10, pady=10)
        ttk.Button(self.tabAdmin, text="Set Loan", style='Button.TButton', command=self.set_or_update_loan).grid(column=2, row=2, padx=10, pady=10)
        self.admin_info = tk.Text(self.tabAdmin, height=10, width=50, bg='#555', fg='white')
        self.admin_info.grid(column=0, row=3, columnspan=4, pady=10)
        self.update_admin_info()
    def create_ml_tab(self):
        ttk.Label(self.tabML, text="Data Visualization", style='Title.TLabel').pack(pady=10)
        ttk.Button(self.tabML, text="Show Graph", style='Button.TButton', command=self.show_graph).pack(pady=10)
        ttk.Button(self.tabML, text="Show Word Cloud", style='Button.TButton', command=self.show_wordcloud).pack(pady=10)
    def create_account(self):
        name = self.name_var.get()
        address = self.address_var.get()
        contact = self.contact_var.get()
        account_number = int(self.account_number_var.get())
        account_type = self.account_type_var.get()
        self.cursor.execute("INSERT INTO Customer (Name, Address, Contact_Number) VALUES (%s, %s, %s)", (name, address, contact))
        self.conn.commit()
        customer_id = self.cursor.lastrowid
        self.cursor.execute("INSERT INTO Account (Account_Number, Account_Type, Balance, Opening_Date, Customer_ID) VALUES (%s, %s, 0.00, CURDATE(), %s)", (account_number, account_type, customer_id))
        self.conn.commit()
        self.export_to_csv()
        messagebox.showinfo("Success", "Account created successfully")
    def process_transaction(self, type):
        account_number = int(self.account_number_customer_var.get())
        amount = float(self.transaction_amount_var.get())
        if type == "Withdraw":
            amount = -amount
        self.cursor.execute("UPDATE Account SET Balance = Balance + %s WHERE Account_Number = %s", (amount, account_number))
        self.conn.commit()
        self.cursor.execute("INSERT INTO Transaction (Transaction_Type, Amount, Transaction_Date, Account_Number) VALUES (%s, %s, CURDATE(), %s)", (type, abs(amount), account_number))
        self.conn.commit()
        self.export_to_csv()
        messagebox.showinfo("Success", f"{type} successful")
    def auto_refresh(self, interval):
        self.dataframe = self.read_from_csv()
        self.display_data()
        self.refresh_data()
        self.root.after(interval * 1000, lambda: self.auto_refresh(interval))
        threading.Timer(interval, self.auto_refresh, [interval]).start()
    def display_data(self):
        try:
            self.dataframe = pd.read_csv('data.csv')
            print("Data loaded successfully:", self.dataframe.head())
        except Exception as e:
            print("Failed to load data:", e)
    def user_action(self):
        self.dataframe = self.read_from_csv()
        self.display_data() 
        print("User action performed")
    def take_loan(self):
        account_number = int(self.account_number_customer_var.get())
        amount = float(self.transaction_amount_var.get()) * 1.16
        self.cursor.execute("SELECT Customer_ID FROM Account WHERE Account_Number = %s", (account_number,))
        customer_id = self.cursor.fetchone()[0]
        self.cursor.execute("INSERT INTO Loan (Loan_Type, Loan_Date, Amount, Customer_ID) VALUES ('Personal', CURDATE(), %s, %s)", (amount, customer_id))
        self.conn.commit()
        self.export_to_csv()
        messagebox.showinfo("Success", "Loan taken successfully at 16% interest")
    def update_admin_info(self):
        self.cursor.execute("""
            SELECT Account.Account_Number, Customer.Name, Account.Balance, IFNULL(SUM(Loan.Amount), 0) AS Total_Loan
            FROM Account
            JOIN Customer ON Account.Customer_ID = Customer.Customer_ID
            LEFT JOIN Loan ON Account.Customer_ID = Loan.Customer_ID
            GROUP BY Account.Account_Number
        """)
        accounts = self.cursor.fetchall()
        self.admin_info.delete('1.0', tk.END)
        for acc in accounts:
            self.admin_info.insert(tk.END, f"Acc No: {acc[0]}, Name: {acc[1]}, Balance: {acc[2]}, Loan: {acc[3]}\n")
        self.root.after(5000, self.update_admin_info)
    def remove_account(self):
        account_number = int(self.account_number_admin_var.get())
        try:
            self.cursor.execute("DELETE FROM Transaction WHERE Account_Number = %s", (account_number,))
            self.cursor.execute("DELETE FROM Account WHERE Account_Number = %s", (account_number,))
            self.conn.commit()
            messagebox.showinfo("Success", "Account removed successfully along with its transactions.")
        except mysql.connector.Error as err:
            self.conn.rollback()
            messagebox.showerror("Error", f"Failed to remove account: {err}")
    def update_data(self, account_number, new_data):
        df = self.read_from_csv()
        df.to_csv('data.csv', index=False)
    def read_from_csv(self):
        try:
            df = pd.read_csv('data.csv')
            return df
        except FileNotFoundError:
            df = pd.DataFrame(columns=['Account_Number', 'Account_Type', 'Balance', 'Name', 'Total_Loan'])
            df.to_csv('data.csv', index=False)
            return df
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read from CSV: {e}")
            return pd.DataFrame()
    def modify_balance(self, is_balance):
        account_number = int(self.account_number_admin_var.get())
        new_value = float(self.set_amount_var.get())
        try:
            if is_balance:
                self.cursor.execute("UPDATE Account SET Balance = %s WHERE Account_Number = %s", (new_value, account_number))
            else:
                self.cursor.execute("UPDATE Loan SET Amount = %s WHERE Customer_ID = (SELECT Customer_ID FROM Account WHERE Account_Number = %s)", (new_value, account_number))
            self.conn.commit()
            messagebox.showinfo("Success", "Update successful")
        except mysql.connector.Error as err:
            self.conn.rollback()
            messagebox.showerror("Error", f"Failed to update: {err}")
    def set_or_update_loan(self):
        account_number = int(self.account_number_admin_var.get())
        new_value = float(self.set_amount_var.get())
        try:
            self.cursor.execute("SELECT Customer_ID FROM Account WHERE Account_Number = %s", (account_number,))
            customer_id = self.cursor.fetchone()
            if customer_id:
                customer_id = customer_id[0]
                self.cursor.execute("SELECT COUNT(*) FROM Loan WHERE Customer_ID = %s", (customer_id,))
                if self.cursor.fetchone()[0] > 0:
                    self.cursor.execute("UPDATE Loan SET Amount = %s WHERE Customer_ID = %s", (new_value, customer_id))
                else:
                    self.cursor.execute("INSERT INTO Loan (Loan_Type, Loan_Date, Amount, Customer_ID) VALUES (%s, CURDATE(), %s, %s)", ('Personal', new_value, customer_id))
                self.conn.commit()
                messagebox.showinfo("Success", "Loan updated successfully")
            else:
                messagebox.showerror("Error", "No such account found.")
        except mysql.connector.Error as err:
            self.conn.rollback()
            messagebox.showerror("Error", f"Failed to update loan: {err}")
    def show_graph(self):
        try:
            data = pd.read_csv('data.csv')
            if data.shape[0] < 2:
                messagebox.showinfo("Info", "Not enough data to create a graph.")
                return
            data['Index'] = range(1, len(data) + 1)
            X = data['Index'].values.reshape(-1, 1)
            y = data['Balance'].values
            model = LinearRegression()
            model.fit(X, y)
            plt.figure(figsize=(10, 5))
            plt.scatter(X, y, color='blue')
            plt.plot(X, model.predict(X), color='red')
            plt.title('Balance Trend Over Time')
            plt.xlabel('Index')
            plt.ylabel('Balance')
            plt.show()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display graph: {e}")
    def show_wordcloud(self):
        try:
            data = pd.read_csv('data.csv')
            text = ' '.join(data['Account_Type'].astype(str))
            wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
            plt.figure(figsize=(8, 6), facecolor=None)
            plt.imshow(wordcloud, interpolation="bilinear")
            plt.axis("off")
            plt.show()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display word cloud: {e}")
    def export_to_csv(self):
        self.cursor.execute("""
            SELECT Account.Account_Number, Account.Account_Type, Account.Balance, Customer.Name, IFNULL(SUM(Loan.Amount), 0) AS Total_Loan
            FROM Account
            JOIN Customer ON Account.Customer_ID = Customer.Customer_ID
            LEFT JOIN Loan ON Account.Customer_ID = Loan.Customer_ID
            GROUP BY Account.Account_Number
        """)
        rows = self.cursor.fetchall()
        columns = ['Account_Number', 'Account_Type', 'Balance', 'Name', 'Total_Loan']
        df = pd.DataFrame(rows, columns=columns)
        df.to_csv('data.csv', index=False)
if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    style.theme_use('alt')
    style.configure('TFrame', background='#333')
    style.configure('TButton', background='#555', foreground='white')
    style.configure('TLabel', background='#333', foreground='white')
    style.configure('TNotebook', background='#333', foreground='white')
    style.configure('Title.TLabel', font=('Poppins', 24), background='#333', foreground='white')
    style.configure('Label.TLabel', font=('Roboto', 14), background='#333', foreground='white')
    style.configure('Entry.TEntry', font=('Roboto', 14))
    style.configure('Button.TButton', font=('Poppins', 14), background='#000', foreground='white')
    app = BankApp(root)
    root.mainloop()