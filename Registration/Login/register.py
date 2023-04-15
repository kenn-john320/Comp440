import tkinter as tk
import sqlite3
import os

db_path = os.environ.get('DB_PATH', 'users.sqlite')
#Connecting database
conn = sqlite3.connect(db_path)
c = conn.cursor()

#Table creation if doesn't exist already
c.execute('''CREATE TABLE IF NOT EXISTS users (
             username TEXT PRIMARY KEY,
             email TEXT,
             firstName TEXT,
             lastName TEXT,
             password TEXT
             )''')

#Registration functionality
def register():
    #retrieving data from user
    username = user_entry.get()
    email = email_entry.get()
    firstName = fName_entry.get()
    lastName = lName_entry.get()
    password = pword_entry.get()
    confirmPassword = confirmPass_entry.get()
    
    #Seeing if username already exists
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    if c.fetchone() is not None:
        # Username already exists
        register_label.config(text='Username already exists!', fg='red')
        return
    
    # Check if the email already exists
    c.execute('SELECT * FROM users WHERE email = ?', (email,))
    if c.fetchone() is not None:
        #In the case it already exists
        register_label.config(text='Email already exists!', fg='red')
        return
    
   #In the case it already exists
    if password != confirmPassword:
        #Checking if passwords match
        register_label.config(text='Passwords do not match!', fg='red')
        return
    
    #Putting new user into the table
    try:
        c.execute('INSERT INTO users (username, email, firstName, lastName, password) VALUES (?, ?, ?, ?, ?)',
                  (username, email, firstName, lastName, password))
        conn.commit()
    except sqlite3.IntegrityError:
        #Registration error
        register_label.config(text='Registration failed!', fg='red')
        return
    
    register_label.config(text='Registration successful!', fg='green')
    
root = tk.Tk()
root.title('Registration')

# Creating labels and entries
user_label = tk.Label(root, text='Username:')
user_label.grid(row=0, column=0, padx=5, pady=5)
user_entry = tk.Entry(root)
user_entry.grid(row=0, column=1, padx=5, pady=5)
pword_label = tk.Label(root, text='Password:')
pword_label.grid(row=1, column=0, padx=5, pady=5)
pword_entry = tk.Entry(root, show='*')
pword_entry.grid(row=1, column=1, padx=5, pady=5)
confirmPass_label = tk.Label(root, text='Confirm Password:')
confirmPass_label.grid(row=2, column=0, padx=5, pady=5)
confirmPass_entry = tk.Entry(root, show='*')
confirmPass_entry.grid(row=2, column=1, padx=5, pady=5)
fName_label = tk.Label(root, text='First Name:')
fName_label.grid(row=3, column=0, padx=5, pady=5)
fName_entry = tk.Entry(root)
fName_entry.grid(row=3, column=1, padx=5, pady=5)
lName_label = tk.Label(root, text='Last Name:')
lName_label.grid(row=4, column=0, padx=5, pady=5)
lName_entry = tk.Entry(root)
lName_entry.grid(row=4, column=1, padx=5, pady=5)
email_label = tk.Label(root, text='Email:')
email_label.grid(row=5, column=0, padx=5, pady=5)
email_entry = tk.Entry(root)
email_entry.grid(row=5, column=1, padx=5, pady=5)
register_button = tk.Button(root, text='Register', command=register)
register_button.grid(row=6, column=0, padx=5, pady=5)
register_label = tk.Label(root, text='')
register_label.grid(row=7, column=1, padx=5, pady=5)

root.mainloop()

