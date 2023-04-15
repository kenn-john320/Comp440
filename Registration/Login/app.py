import runpy
import os
import sqlite3
import tkinter as tk

root = tk.Tk()
root.title('Registration/Login')
root.geometry('520x270')
root.configure(bg='#F0F0F0')

def get_root():
    current_folder = os.path.abspath(os.path.dirname(__file__))
    while not os.path.exists(os.path.join(current_folder)):
        current_folder = os.path.abspath(os.path.join(current_folder, os.pardir))
        if os.path.splitdrive(current_folder)[1] == '\\':
            raise FileNotFoundError("Can't find root!")
    return current_folder

#Getting root 
project_root = get_root()
login_path = os.path.join(project_root, 'login.py')
register_path = os.path.join(project_root, 'register.py')

# Executing scripts
def run_script(script_path, db_path=None):
    script_directory = os.path.dirname(script_path)
    script_name = os.path.basename(script_path)
    
    original_cwd = os.getcwd()
    os.chdir(script_directory)
    
    if db_path is not None:
        os.environ['DB_PATH'] = db_path
    else: 
        raise ValueError("Database not present")
    
    try:
        runpy.run_path(script_path)
    finally:
        os.chdir(original_cwd)

def init_database(db_path):
    if not os.path.exists(db_path):
        #Connecting database
        conn = sqlite3.connect(db_path)
        #Initializing table
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
             username TEXT PRIMARY KEY,
             email TEXT,
             firstName TEXT,
             lastName TEXT,
             password TEXT
             )''')

        #Populating table with dummy data
        dummy_data = [
            ('Jen1', 'Jen1@gmail.com','Jen','Kathy', 'password'),
            ('Jake', 'JakeW@gmail.com','Jake','White', 'password'),
            ('Keith', 'Keith3@gmail.com','Keith','Doer', 'password'),
            ('Zack', 'Zck@gmail.com','Zack','Dayne', 'password'),
            ('Mary', 'MarJ1@gmail.com','Mary','Jane', 'password'),
        ]

        conn.executemany('''
        INSERT INTO users (username, email, firstName, lastName, password) VALUES (?, ?, ?, ?, ?);
        ''', dummy_data)

        conn.commit()

        conn.close()

db_path = os.path.join(project_root, 'users.sqlite')

#Label and button creation
title_label = tk.Label(root, text='User Registration/Login', font=('Times New Roman', 28, 'bold'), bg='#F0F0F0', fg='#3C3C3C')
title_label.grid(row=0, column=0, columnspan=4, padx=20, pady=20)
login_button = tk.Button(root, text='Login', font=('Times New Roman', 18), bg='#3C3C3C', fg='#FFFFFF', command=lambda: run_script(login_path, db_path=db_path))
login_button.grid(row=1, column=0, padx=10, pady=10)
init_button = tk.Button(root, text='Create Database', font=('Times New Roman', 18), bg='#3C3C3C', fg='#FFFFFF', command=lambda: init_database(db_path))
init_button.grid(row=1, column=1, padx=10, pady=10)
register_button = tk.Button(root, text='Register', font=('Times New Roman', 18), bg='#3C3C3C', fg='#FFFFFF', command=lambda: run_script(register_path, db_path=db_path))
register_button.grid(row=1, column=2, padx=10, pady=10)

root.mainloop()
