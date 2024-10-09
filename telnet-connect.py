import tkinter as tk
from tkinter import filedialog, messagebox
from netmiko import ConnectHandler
import sys

# Function to load credentials from a text file
def load_credentials(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            return {
                'device_type': 'cisco_ios_telnet',  # Telnet device type for Cisco
                'host': lines[0].strip(),
                'username': lines[1].strip(),
                'password': lines[2].strip()
            }
    except Exception as e:
        messagebox.showerror("Error", f"Error loading credentials: {e}")
        sys.exit()

# Function to connect to the switch and change hostname
def connect_and_configure(credentials, new_hostname):
    try:
        # Connect to the device using Telnet
        connection = ConnectHandler(
            device_type=credentials['device_type'],
            host=credentials['host'],
            username=credentials['username'],
            password=credentials['password']
        )
        log_output("Connected to the switch via Telnet.")

        # Change the hostname
        config_commands = [f'hostname {new_hostname}']
        connection.send_config_set(config_commands)
        log_output(f"Hostname changed to {new_hostname}.")

        # Retrieve the running configuration
        running_config = connection.send_command("show running-config")
        log_output("Running configuration retrieved.")

        # Save running config to a file
        output_file = f"running_config_{new_hostname}.txt"
        with open(output_file, 'w') as file:
            file.write(running_config)
        log_output(f"Running config saved to {output_file}")

        # Output running config in the log box
        log_output("\nCurrent Running Config:\n")
        log_output(running_config)

        connection.disconnect()
        log_output("Connection closed.")

    except Exception as e:
        log_output(f"An error occurred: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")

# Function to handle the 'Start' button click
def start_connection():
    try:
        # Load credentials
        credentials = load_credentials(cred_file_path.get())

        # Get the new hostname from input
        new_hostname = hostname_entry.get()

        if new_hostname:
            connect_and_configure(credentials, new_hostname)
        else:
            messagebox.showwarning("Input Error", "Please enter a new hostname.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Function to select the credentials file
def select_file():
    filename = filedialog.askopenfilename(title="Select Credentials File", filetypes=(("Text Files", "*.txt"), ("All Files", "*.*")))
    cred_file_path.set(filename)

# Function to log output in the GUI
def log_output(text):
    log_box.config(state=tk.NORMAL)
    log_box.insert(tk.END, text + '\n')
    log_box.config(state=tk.DISABLED)

# Set up the GUI
root = tk.Tk()
root.title("Telnet Switch Configuration Tool")
root.geometry("500x400")

# Credential file selection
cred_file_path = tk.StringVar()

tk.Label(root, text="Credentials File:").pack(pady=5)
tk.Entry(root, textvariable=cred_file_path, width=40).pack(pady=5)
tk.Button(root, text="Browse", command=select_file).pack(pady=5)

# New hostname input
tk.Label(root, text="New Hostname:").pack(pady=5)
hostname_entry = tk.Entry(root, width=30)
hostname_entry.pack(pady=5)

# Log output box
log_box = tk.Text(root, state=tk.DISABLED, width=60, height=10)
log_box.pack(pady=10)

# Start button
tk.Button(root, text="Start", command=start_connection).pack(pady=10)

# Start the GUI loop
root.mainloop()
