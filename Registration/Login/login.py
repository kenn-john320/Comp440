import os
import sqlite3
import tkinter as tk

db_path = os.environ.get('DB_PATH', 'users.sqlite')

#Connecting to database
conn = sqlite3.connect(db_path)
c = conn.cursor()
root = tk.Tk()
root.title('Login')

#Username and password gui labels. 
user_label = tk.Label(root, text='Username:', font=('Times New Roman', 14))
user_label.grid(row=0, column=0, padx=5, pady=5)
user_entry = tk.Entry(root, font=('Times New Roman', 14))
user_entry.grid(row=0, column=1, padx=5, pady=5)
pword_label = tk.Label(root, text='Password:', font=('Times New Roman', 14))
pword_label.grid(row=1, column=0, padx=5, pady=5)
pword_entry = tk.Entry(root, show='*', font=('Times New Roman', 14))
pword_entry.grid(row=1, column=1, padx=5, pady=5)

#Login 
def login():
    username = user_entry.get()
    password = pword_entry.get()

    #Checking if credentials entered by user match those in database
    c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    user = c.fetchone()
    if user is None:
        #If credentials are invalid
        login_label.config(text='Invalid credentials!', fg='red', font=('Times New Roman', 12))
    else:
        #Succesful login
        login_label.config(text='Login successful!', fg='green', font=('Times New Roman', 12))

#Login GUI button/labels
login_button = tk.Button(root, text='login', command=login, font=('Times New Roman', 14))
login_button.grid(row=2, column=0, padx=5, pady=5)
login_label = tk.Label(root, text='', font=('Times New Roman', 12))
login_label.grid(row=2, column=1, padx=5, pady=5)
root.configure(bg='#F0F0F0')

root.mainloop()



