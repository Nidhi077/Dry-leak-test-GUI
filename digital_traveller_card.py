import subprocess
import tkinter as tk
from tkinter import messagebox

def execute_script(script, *args):
    try:
        # Execute the command as a subprocess
        subprocess.Popen(["python", script] + list(args))  # Use Popen to run the script asynchronously
    except Exception as e:
        # Handle any errors that occur during the subprocess execution
        print(f"An error occurred: {e}")

def table_selection_stage(table_name):
    # Place your etching stage logic here
    print(f"Table Name: {table_name}")

def select_table(table_var):
    table_name = table_var
    if not table_name:
        messagebox.showwarning("Warning", "Table Name must be selected")
        return
    else:
        table_selection_stage(table_name)
        # After processing, execute the upper_body.py script
        execute_script("upper_body_LeakTest.py", table_name)

def on_table_change(*args):
    selected_table = table_var

# Main function
def main():
    global table_var

    # Create main window
    root = tk.Tk()
    root.title("Digital Traveler Card")
    root.geometry("250x90+500+250") 

    # Create stage selection label
    tk.Label(root, text="Table Name:").grid(row=1, column=0, padx=10, pady=5)

    # Create dropdown menu for stage selection
    table_var = tk.StringVar(root)
    table_var.set('Select Table')  # Set default stage
    table_var.trace_add('write', on_table_change)
    table_dropdown = tk.OptionMenu(root, table_var, *['Bundle dry leak test', 'Stack dry leak test'])
    table_dropdown.grid(row=1, column=1, padx=10, pady=5)

    def on_submit_button_click():
        select_table(table_var.get())

    # Create submit button
    submit_button = tk.Button(root, text="Submit", command=on_submit_button_click)
    submit_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

    # Run the main event loop
    root.mainloop()

if __name__ == "__main__":
    main()
