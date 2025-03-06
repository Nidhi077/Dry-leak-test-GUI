import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import sys
from tkinter import ttk,filedialog
from tkinter import PhotoImage
from PIL import Image, ImageTk
import mysql.connector
import pandas as pd
import numpy as np
import re
# from sqlalchemy import create_engine
import xlsxwriter
import os
#PASSWORD FOR SQL=Ohmium@123
#Password for password button = Ohmium@123

class InvalidInputError(Exception):
    pass

def connect_to_database():
    return mysql.connector.connect(
        host="OHMLAP0362",
        user="ohmium",
        password="Ohmium@123",
        database="dry_leak_test_data"    
    )

def get_table_name():
    # global table_name
    table_name=None
    if len(sys.argv) >= 1:
        table_name = sys.argv[1]
        print('table:', table_name)
    else:
        messagebox.showerror("Error", "Insufficient command-line arguments provided.")
    return table_name
table_name = get_table_name()

# define function for pulling the data of selected table
def fetch_data(table_name):
    global rows,columns
    try:
        conn = connect_to_database()
        cursor = conn.cursor()

        cursor.execute(f'DESCRIBE `{table_name}`')
        all_columns = [column[0] for column in cursor.fetchall()]

        hidden_columns = {'Week', 'Month', 'Day','Start Time','End Time','Shift'}
        
        columns = [col for col in all_columns if col not in hidden_columns]

        if table_name:
            query = f"SELECT * FROM `{table_name}`"
            cursor.execute(query)

        all_rows = cursor.fetchall()

        columns_indices = [all_columns.index(col) for col in columns]
        rows = [[row[idx] for idx in columns_indices] for row in all_rows]

        cursor.close()
        conn.close()

        return columns, rows

    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None
    

def generate_shift(hour):
    if 6 <= hour < 14:
        return "A"
    elif 14 <= hour < 22:
        return "B"
    else:
        return "C"
    
# Datetime and shift generation
def generate_datetime_monthweek():
    current_datetime = datetime.now()
    month = current_datetime.strftime("%b-%Y")
    week_number = current_datetime.isocalendar()[1]
    date = current_datetime.strftime("%Y-%m-%d")
    return month, week_number, date

# Insert data function
def insert_data(table_name, data):
    conn = connect_to_database()
    cursor = conn.cursor()

    placeholders = ', '.join(['%s'] * len(data))
    columns = ', '.join([f"`{col}`" for col in data.keys()]) 
    sql = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"
    # values = tuple(data.values())
    
    # Convert all values to native Python data types
    converted_value = []
    for key, value in data.items():
        if isinstance(value, np.generic): 
            value = value.item() # Convert numpy data types to native Python types
        converted_value.append(value)

    # Attempt to execute the query
    try:
        cursor.execute(sql, converted_value)
        conn.commit()

        refresh_data(tree,table_name)
        messagebox.showinfo('Success','Row inserted in database')

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        raise
    cursor.close()
    conn.close()

def stack_dry_leak_test(start_window):
    start_window.geometry("835x575+25+25")
    start_time=None
    def update_time():
        nonlocal start_time
        now = datetime.now()
        hour = now.strftime("%H:%M:%S")
        if start_time is None:
            start_time = now.strftime("%H:%M:%S")
        start_window.after(1000, update_time)
        return start_time
    update_time()

    dimentional_field_values={}
    def generate_anode_fields(start_window, dimentional_field_values):
        anode_fields = ['CL anode @30psi', 'OBL anode @30psi', 'CL anode @50psi', 'OBL anode @50psi']
        for i, field in enumerate(anode_fields):
            label = tk.Label(start_window, text=field)
            label.grid(row=8 + i, column=0, padx=10, pady=5)     
            entry = tk.Entry(start_window)
            entry.grid(row=8 + i, column=1, padx=5, pady=5)    
            dimentional_field_values[field] = entry

    def generate_cathode_fields(start_window, dimentional_field_values):
        cathode_fields = [
            'CL cathode @30psi', 'OBL cathode @30psi', 'CL cathode @50psi', 'OBL cathode @50psi',
            'CL cathode @100psi', 'OBL cathode @100psi', 'CL cathode @150psi', 'OBL cathode @150psi',
            'CL cathode @200psi', 'OBL cathode @200psi', 'CL cathode @250psi', 'OBL cathode @250psi',
            'CL cathode @300psi', 'OBL cathode @300psi', 'CL cathode @350psi', 'OBL cathode @350psi',
            'CL cathode @400psi', 'OBL cathode @400psi', 'CL cathode @450psi', 'OBL cathode @450psi']
        for i, field in enumerate(cathode_fields):
            label = tk.Label(start_window, text=field)
            label.grid(row=5 + i if i<=9 else i-5, column=2 if i<=9 else 4, padx=10, pady=5)
            entry = tk.Entry(start_window)
            entry.grid(row=5 + i if i<=9 else i-5, column=3 if i<=9 else 5, padx=5, pady=5)
            dimentional_field_values[field] = entry

    def save_values(dimentional_field_values, final_values):
        for fieldname, entry in dimentional_field_values.items():
            if entry.get():                  
                final_values.append((entry.get()))
            else:
                messagebox.showwarning("Warning", "One or more fields are blank.", parent=start_window)
                # messagebox.showerror("Error", f"Invalid input: {entry.get()} is not a valid number",parent = start_window)
                raise InvalidInputError
    
    def generate_field_labels(start_time):

        operator_name_label = tk.Label(start_window, text="Operator Name :")
        operator_name_label.grid(row=1, column=0, padx=10, pady=5)
        operator_name_entry = tk.Entry(start_window)
        operator_name_entry.grid(row=1, column=1, padx=5, pady=5)

        stack_no_label = tk.Label(start_window, text="Stack No :")
        stack_no_label.grid(row=1, column=2, padx=10, pady=5)
        stack_no_entry = tk.Entry(start_window)
        stack_no_entry.grid(row=1, column=3, padx=5, pady=5)
        
        save_button = tk.Button(start_window, text='Save', command=lambda: save_and_close(operator_name_entry, field_list, start_time), width=6, bg='lightgrey')
        save_button.grid(row=2, column=0, columnspan=2, pady=10, padx=100)

        torque_label = tk.Label(start_window, text="Torque :")
        torque_label.grid(row=3, column=0, padx=10, pady=5)
        torque_entry = tk.Entry(start_window)
        torque_entry.grid(row=3, column=1, padx=5, pady=5)

        resistance_range_label = tk.Label(start_window, text="Resistance range \n> 5 ohms :")
        resistance_range_label.grid(row=3, column=2, padx=10, pady=5)
        resistance_range_entry = tk.Entry(start_window)
        resistance_range_entry.grid(row=3, column=3, padx=5, pady=5)

        subheading_label = tk.Label(start_window, text="Anode and Cathode", font=("Arial", 13))
        subheading_label.grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")

        generate_anode_fields(start_window, dimentional_field_values)
        generate_cathode_fields(start_window, dimentional_field_values)

        subheading_label = tk.Label(start_window, text="Observations", font=("Arial", 13))
        subheading_label.grid(row=15, column=0, columnspan=2, pady=10, sticky="ew")

        remarks_label = tk.Label(start_window, text="Remarks :")
        remarks_label.grid(row=16, column=0, padx=10, pady=5)
        remarks_entry = tk.Entry(start_window)
        remarks_entry.grid(row=16, column=1,padx=5, pady=5)

        Observations_label = tk.Label(start_window, text="Observations :")
        Observations_label.grid(row=16, column=2, padx=10, pady=5)
        Observations_entry = tk.Entry(start_window)
        Observations_entry.grid(row=16, column=3, padx=5, pady=5)

        field_list = [stack_no_entry, torque_entry, resistance_range_entry, remarks_entry, Observations_entry]


    def check_blanks(operator_name_entry, stack_no_entry, torque_entry):
        # Check if either of the fields is blank
        if not operator_name_entry.get().strip():
            messagebox.showwarning("Warning", "field 'Operator Name' cannot be blank", parent=start_window)
            raise InvalidInputError
        if not stack_no_entry.get().strip():
            messagebox.showwarning("Warning", "field 'Stack No' cannot be blank", parent=start_window)
            raise InvalidInputError
        if not torque_entry.get().strip():
            messagebox.showwarning("Warning", "field 'Torque' cannot be blank", parent=start_window)
            raise InvalidInputError

    def save_and_close(operator_name_entry, field_list, start_time):
        try:
            end_time = datetime.now().strftime("%H:%M:%S")  # end time should be when the user hits save button
            final_values=[]
            check_blanks(operator_name_entry, field_list[0], field_list[1])
            save_values(dimentional_field_values, final_values)
            current_datetime = datetime.now()
            month, week_number, date = generate_datetime_monthweek()
            day = current_datetime.strftime("%a")
            shift = generate_shift(current_datetime.hour)
             
            def accept_reject_remarks(dimentional_field_values):
                # Extract values from entry fields as floats (assuming entry fields are numeric) or 'NT'
                cl_anode_values = [entry.get() for key, entry in dimentional_field_values.items() if 'CL' in key and 'anode' in key]
                obl_anode_values = [entry.get() for key, entry in dimentional_field_values.items() if 'OBL' in key and 'anode' in key]
                cl_cathode_values = [entry.get() for key, entry in dimentional_field_values.items() if 'CL' in key and 'cathode' in key]
                obl_cathode_values = [entry.get() for key, entry in dimentional_field_values.items() if 'OBL' in key and 'cathode' in key]

                # Convert non-NT values to float for comparison
                cl_anode_values = [float(value) for value in cl_anode_values if value!='NT']
                obl_anode_values = [float(value) for value in obl_anode_values if value!='NT']
                cl_cathode_values = [float(value) for value in cl_cathode_values if value!='NT']
                obl_cathode_values = [float(value) for value in obl_cathode_values if value!='NT']

                # Define the condition for acceptance
                condition = (all(value < 50 for value in cl_anode_values) and all(value < 1 for value in obl_anode_values)
                             and(value < 100 for value in cl_cathode_values) and (value < 7 for value in obl_cathode_values))

                # Use np.where to set Accepted and Rejected based on the condition
                Accepted, Rejected = np.where(condition, (1, 0), (0, 1))

                # Set the Remarks based on Accepted and Rejected values
                Remarks = 'Accepted' if Accepted == 1 and Rejected == 0 else 'Rejected'

                # Show appropriate message box based on the result
                if Remarks == 'Accepted':
                    messagebox.showinfo("Success", "Row Accepted")
                else:
                    messagebox.showwarning("Warning", "Row Rejected")

                return Accepted, Rejected, Remarks
            Accepted, Rejected, Remarks = accept_reject_remarks(dimentional_field_values)  

            data = {
                'Month': month,
                'Week': week_number,
                'Date': date,
                'Start time': start_time,
                'End time': end_time,
                'Day': day,
                'Shift': shift,
                'Operator Name': operator_name_entry.get().strip(),
                'Stack No': field_list[0].get().strip(),
                # 'Retest' : retest,
                'Torque': field_list[1].get().strip(),

                'CL anode at 30psi' : final_values[0],
                'OBL anode at 30psi' : final_values[1],
                'CL anode at 50psi' : final_values[2],
                'OBL anode at 50psi' : final_values[3],
                
                'CL cathode at 30psi' : final_values[4],
                'OBL cathode at 30psi' : final_values[5],
                'CL cathode at 50psi' : final_values[6],
                'OBL cathode at 50psi' : final_values[7],
                'CL cathode at 100psi' : final_values[8],
                'OBL cathode at 100psi' : final_values[9],
                'CL cathode at 150psi' : final_values[10],
                'OBL cathode at 150psi' : final_values[11],
                'CL cathode at 200psi' : final_values[12],
                'OBL cathode at 200psi' : final_values[13],
                'CL cathode at 250psi' : final_values[14],
                'OBL cathode at 250psi' : final_values[15],
                'CL cathode at 300psi' : final_values[16],
                'OBL cathode at 300psi' : final_values[17],
                'CL cathode at 350psi' : final_values[18],
                'OBL cathode at 350psi' : final_values[19],
                'CL cathode at 400psi' : final_values[20],
                'OBL cathode at 400psi' : final_values[21],
                'CL cathode at 450psi' : final_values[22],
                'OBL cathode at 450psi' : final_values[23],

                'Accepted' : Accepted,
                'Rejected' : Rejected, 
                'Resistance range > 5 ohms' : field_list[2].get().strip(),
                'Status' : Remarks,

                'Remarks' : field_list[3].get().strip(),
                'Observations' : field_list[4].get().strip()
                }
            
            print(data)
            insert_data('Stack dry leak test', data)
            update_time()
            start_window.destroy()

        except InvalidInputError:
            pass    

    generate_field_labels(start_time)      


# Start button body
def start_button_body(table_name):
    global start_window
    start_window = tk.Toplevel(window)
    start_window.title(f"{table_name}")

    if table_name == "Bundle dry leak test":
        bundle_dry_leak_test(start_window)
    elif table_name == "Stack dry leak test":
        stack_dry_leak_test(start_window)
    else:
        return    

######################################################### Bundle dry leak test #####################################################

# Bundle dry leak test
def bundle_dry_leak_test(start_window):
    start_window.geometry("560x620")
    start_time=None
    def update_time():
        nonlocal start_time
        now = datetime.now()
        hour = now.strftime("%H:%M:%S")
        if start_time is None:
            start_time = now.strftime("%H:%M:%S")
        start_window.after(1000, update_time)
        return start_time
    update_time()

    dimentional_field_values={}
    def generate_dimension_labels(start_window, dimentional_field_values):
        dimentional_fields = ['CL anode @30psi', 'OBL anode @30psi', 'CL anode @50psi', 'OBL anode @50psi',
                              'CL cathode @50psi', 'OBL cathode @50psi', 'CL cathode @100psi', 'OBL cathode @100psi',
                              'CL cathode @150psi', 'OBL cathode @150psi', 'CL cathode @200psi', 'OBL cathode @200psi',
                              'CL cathode @250psi', 'OBL cathode @250psi']
        # Creating a dictionary with keys from 0 to 7
        dimentional_field_dict = {i: field for i, field in enumerate(dimentional_fields)}
        for i, j in dimentional_field_dict.items():
            label = tk.Label(start_window, text=j)
            label.grid(row=8+i if 'anode' in j else i+1 , column=0 if 'anode' in j else 2, padx=10, pady=5)
            entry = tk.Entry(start_window)
            entry.grid(row=8+i if 'anode' in j else i+1, column=1 if 'anode' in j else 3, padx=5, pady=5)
            dimentional_field_values[j] = entry
                    

    def save_values(dimentional_field_values, final_values):
        for fieldname, entry in dimentional_field_values.items():
            if entry.get():                  
                final_values.append((entry.get()))
            else:
                messagebox.showwarning("Warning", "One or more fields are blank.", parent=start_window)
                # messagebox.showerror("Error", f"Invalid input: {entry.get()} is not a valid number",parent = start_window)
                raise InvalidInputError                                                       


    def generate_field_labels(start_time):

        operator_name_label = tk.Label(start_window, text="Operator Name :")
        operator_name_label.grid(row=1, column=0, padx=10, pady=5)
        operator_name_entry = tk.Entry(start_window)
        operator_name_entry.grid(row=1, column=1, padx=5, pady=5)

        bundle_no_label = tk.Label(start_window, text="Bundle No :")
        bundle_no_label.grid(row=2, column=0, padx=10, pady=5)
        bundle_no_entry = tk.Entry(start_window)
        bundle_no_entry.grid(row=2, column=1, padx=5, pady=5)

        bin_category_label = tk.Label(start_window, text="Bin Category :")
        bin_category_label.grid(row=3, column=0, padx=10, pady=5)
        bin_category_entry = tk.Entry(start_window)
        bin_category_entry.grid(row=3, column=1, padx=5, pady=5)

        SBAS_label = tk.Label(start_window, text="Stack Bundle \nAssembly Sequence :")
        SBAS_label.grid(row=2, column=2, padx=10, pady=5)
        SBAS_entry = tk.Entry(start_window)
        SBAS_entry.grid(row=2, column=3, padx=5, pady=5)

        plate_SIno_label = tk.Label(start_window, text="Plate SI No :")
        plate_SIno_label.grid(row=3, column=2, padx=10, pady=5)
        plate_SIno_entry = tk.Entry(start_window)
        plate_SIno_entry.grid(row=3, column=3, padx=5, pady=5)

        generate_dimension_labels(start_window, dimentional_field_values)

        subheading_label = tk.Label(start_window, text="Observations", font=("Arial", 13))
        subheading_label.grid(row=15, column=0, columnspan=2, pady=10, sticky="ew")
       
        reason_for_rej_label = tk.Label(start_window, text="Reason for Rejection :")
        reason_for_rej_label.grid(row=16, column=2, padx=10, pady=5)
        reason_for_rej_entry = tk.Entry(start_window)
        reason_for_rej_entry.grid(row=16, column=3, padx=5, pady=5)

        initial_obsv_label = tk.Label(start_window, text="Initial Observations \non the replaced \nparts/ Rejections :")
        initial_obsv_label.grid(row=17, column=0, padx=10, pady=5)
        initial_obsv_entry = tk.Entry(start_window)
        initial_obsv_entry.grid(row=17, column=1,padx=5, pady=5)

        method_changes_label = tk.Label(start_window, text="Method changes :")
        method_changes_label.grid(row=17, column=2, padx=10, pady=5)
        method_changes_entry = tk.Entry(start_window)
        method_changes_entry.grid(row=17, column=3, padx=5, pady=5)

        field_list = [bundle_no_entry, bin_category_entry, SBAS_entry, plate_SIno_entry, reason_for_rej_entry,
                    initial_obsv_entry, method_changes_entry]

        save_button = tk.Button(start_window, text='Save', command=lambda: save_and_close(operator_name_entry, field_list, start_time), width=6, bg='lightgrey')
        save_button.grid(row=4, column=0, columnspan=2, pady=10, padx=100)


    def check_blanks(operator_name_entry, bundle_no_entry, plate_SIno_entry):
        # Check if either of the fields is blank
        if not operator_name_entry.get().strip():
            messagebox.showwarning("Warning", "field 'Operator Name' cannot be blank", parent=start_window)
            raise InvalidInputError
        if not bundle_no_entry.get().strip():
            messagebox.showwarning("Warning", "field 'Bundle no' cannot be blank", parent=start_window)
            raise InvalidInputError
        if not plate_SIno_entry.get().strip():
            messagebox.showwarning("Warning", "field 'Plate SI No' cannot be blank", parent=start_window)
            raise InvalidInputError
        

    def save_and_close(operator_name_entry, field_list, start_time):
        try:
            end_time = datetime.now().strftime("%H:%M:%S")  # end time should be when the user hits save button
            final_values=[]
            check_blanks(operator_name_entry, field_list[0], field_list[3])
            save_values(dimentional_field_values, final_values)
            current_datetime = datetime.now()
            month, week_number, date = generate_datetime_monthweek()
            day = current_datetime.strftime("%a")
            shift = generate_shift(current_datetime.hour)
             
            def accept_reject_remarks(dimentional_field_values):
                # Extract values from entry fields as floats (assuming entry fields are numeric) or 'NT'
                cl_values = [entry.get() for key, entry in dimentional_field_values.items() if 'CL' in key]
                obl_values = [entry.get() for key, entry in dimentional_field_values.items() if 'OBL' in key]

                # Check if 'NT' appears in any value
                if any(value == 'NT' for value in cl_values + obl_values):
                    Accepted, Rejected = 0, 1  # Reject if 'NT' is found
                    Remarks = 'Rejected'
                    messagebox.showwarning("Warning", "Row Rejected: 'NT' value detected")
                else:
                    # Convert non-NT values to float for comparison
                    cl_values = [float(value) for value in cl_values]
                    obl_values = [float(value) for value in obl_values]

                    # Define the condition for acceptance
                    condition = (all(value < 30 for value in cl_values) and all(value < 10 for value in obl_values))

                    # Use np.where to set Accepted and Rejected based on the condition
                    Accepted, Rejected = np.where(condition, (1, 0), (0, 1))

                    # Set the Remarks based on Accepted and Rejected values
                    Remarks = 'Accepted' if Accepted == 1 and Rejected == 0 else 'Rejected'

                    # Show appropriate message box based on the result
                    if Remarks == 'Accepted':
                        messagebox.showinfo("Success", "Row Accepted")
                    else:
                        messagebox.showwarning("Warning", "Row Rejected")

                return Accepted, Rejected, Remarks
            Accepted, Rejected, Remarks = accept_reject_remarks(dimentional_field_values)

            # def Retest():
            #     Bundle_no = field_list[0].get(),
            #     try:
            #         conn = connect_to_database()
            #         cursor = conn.cursor()

            #         fetch_query = f"""
            #                 SELECT MAX(`Retest`)
            #                 FROM `{table_name}`
            #                 WHERE `Bundle no` = '{Bundle_no}'
            #             """
            #         cursor.execute(fetch_query)
            #         result = cursor.fetchone()
            #         print(f"Output row: {result}")   
                    
            #     except mysql.connector.Error as err:
            #         print(f"Error: {err}")
            #         raise
            #     finally:
            #         cursor.close()
            #         conn.close()
                
            #     if result is None: # if table is blank
            #         retest_val = 0
            #     else:    
            #         # retest_val equals (query_output + 1) if row exist & 0 if none of the rows matches
            #         retest_val = int(result[0])+1 if result[0] is not None else 0
            #     return retest_val
            # retest = Retest() 
            

            data = {
                'Month': month,
                'Week': week_number,
                'Date': date,
                'Start time': start_time,
                'End time': end_time,
                'Day': day,
                'Shift': shift,
                'Operator Name': operator_name_entry.get().strip(),
                'Bundle no': field_list[0].get().strip(),
                # 'Retest' : retest,
                'Bin Category': field_list[1].get().strip(),
                'Stack bundle assembly sequence' : field_list[2].get().strip(),
                'Plate SI No' : field_list[3].get().strip(),

                'CL anode at 30psi' : final_values[0],
                'OBL anode at 30psi' : final_values[1],
                'CL anode at 50psi' : final_values[2],
                'OBL anode at 50psi' : final_values[3],

                'CL cathode at 50psi' : final_values[4],
                'OBL cathode at 50psi' : final_values[5],
                'CL cathode at 100psi' : final_values[6],
                'OBL cathode at 100psi' : final_values[7],
                'CL cathode at 150psi' : final_values[8],
                'OBL cathode at 150psi' : final_values[9],
                'CL cathode at 200psi' : final_values[10],
                'OBL cathode at 200psi' : final_values[11],
                'CL cathode at 250psi' : final_values[12],
                'OBL cathode at 250psi' : final_values[13],

                'Accepted' : Accepted,
                'Rejected' : Rejected,  
                'Status' : Remarks,

                'Reason for rejection' : field_list[4].get().strip(),
                'Initial observations on the replaced parts/rejections' : field_list[5].get().strip(),
                'Method changes' : field_list[6].get().strip(),
                }
            
            print(data)
            insert_data('Bundle dry leak test', data)
            update_time()
            start_window.destroy()

        except InvalidInputError:
            pass    

    generate_field_labels(start_time)

####################################################################################################################################

# Define the function to display data in a Treeview
def display_data_in_treeview(window, table_name):
    # Fetch data from the database
    columns, rows = fetch_data(table_name)

    if not columns:
        return

    # Treeview Frame
    tree_frame = tk.Frame(window, bg='light sky blue')
    tree_frame.grid(row=8, column=0, pady=0, sticky='nsew')

    # Configure tree_frame to expand with the window
    tree_frame.grid_rowconfigure(0, weight=1)
    tree_frame.grid_columnconfigure(0, weight=1)

    tree = ttk.Treeview(tree_frame, show='headings')

    # Define columns
    tree['columns'] = columns

    # Format columns (adjust width as needed)
    for col in columns:
        if 'Resistance range > 5 ohms' in col:
            tree.column(col, width=150, anchor='center')
        elif 'anode' in col or 'cathode' in col:
            tree.column(col, width=125, anchor='center')
        else:
            tree.column(col, width=100, anchor='center')
        tree.heading(col, text=col)
                
    # Insert data into the Treeview
    for row in rows:
        tree.insert("", "end", values=row)

    # Configure scrollbars
    x_scrollbar = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=tree.xview)
    y_scrollbar = tk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)

    tree.configure(xscrollcommand=x_scrollbar.set, yscrollcommand=y_scrollbar.set)

    tree.grid(row=0, column=0, sticky='nsew')
    x_scrollbar.grid(row=1, column=0, sticky='ew')
    y_scrollbar.grid(row=0, column=1, sticky='ns')

    window.grid_rowconfigure(8, weight=1)
    window.grid_columnconfigure(0, weight=1)

    # tree.bind('<<TreeViewSelect>>',open_update_row_window) 
    return tree


# refresh data
def refresh_data(tree, table_name):

    print("Refresh button is pressed.....")
    try:
        conn = connect_to_database()
        cursor = conn.cursor()

        cursor.execute(f'DESCRIBE `{table_name}`')
        all_columns = [column[0] for column in cursor.fetchall()]

        cursor.close()
        conn.close()

        print(all_columns)
        hidden_columns = {'Week','Month', 'Day', 'Start Time','End Time','Shift'}
        
        visible_columns = [col for col in all_columns if col not in hidden_columns]

        # Construct the SQL query   
        query = f"SELECT {', '.join([f'`{col}`' for col in visible_columns])} FROM `{table_name}`"      

        
        # Execute the query with filter values
        conn = connect_to_database()
        with conn.cursor() as cursor:
            cursor.execute(query)
                
            # Fetch all rows from the result set
            rows = cursor.fetchall()   
                    
        # Print fetched rows to terminal for debugging
        print("Fetched Rows:")
        for row in rows:
            print(row)

        # Clear the existing treeview data
        for item in tree.get_children():
            print(item)
            tree.delete(item)
            print('existing item deleted')

        # Insert new data
        for row in rows:
            tree.insert("", "end", values=row)
            print('new row inserted')

    except mysql.connector.Error as e:
        # Handle MySQL errors
        print(f"Error connecting to MySQL: {e}")
    
    finally:
        cursor.close()
        conn.close()    

def open_update_row_window(tree, selected_item, table_name):
    item_data = tree.item(selected_item, 'values')
    update_window = tk.Toplevel(window)
    update_window.title("Update Row")
    update_window.geometry("400x230") if table_name == 'Bundle dry leak test' else update_window.geometry("400x120")

    columns = tree['columns']
    column_mapping = {column_name: index for index, column_name in enumerate(columns)}

    entries={}
    def create_label_and_entry(update_window, text, row, col, col_name):
        label = tk.Label(update_window, text=text)
        label.grid(row=row, column=col, padx=10, pady=5, sticky='e')
        entry = tk.Entry(update_window)
        entry.grid(row=row, column=col+1, padx=10, pady=5)
        if col_name in columns:     
            entry.insert(0, item_data[columns.index(col_name)])
        entries[col_name] = entry
        return entry
    
    # shift_entry = create_label_and_entry(update_window, "Shift:", 0, 0, "Shift")
    if table_name == "Bundle dry leak test":
        create_label_and_entry(update_window, "Bundle No :", 1, 0, "Bundle no")
        create_label_and_entry(update_window, "Bin Category :", 2, 0, "Bin Category")
        create_label_and_entry(update_window, "Stack Bundle \nAssembly Sequence :", 3, 0, "Stack bundle assembly sequence")
        create_label_and_entry(update_window, "Plate SI No :", 4, 0, "Plate SI No")
    if table_name == "Stack dry leak test":
        create_label_and_entry(update_window, "Stack No :", 5, 0, "Stack No")
    create_label_and_entry(update_window, "Operator Name :", 6, 0, "Operator Name")

    
    def check_blanks(entries):
        # Check if either of the fields is blank
        if not entries['Operator Name'].get().strip():
            messagebox.showwarning("Warning", "field 'Operator Name' cannot be blank", parent=update_window)
            raise InvalidInputError
        
        if table_name == "Bundle dry leak test":
            if not entries['Bundle no'].get().strip():
                messagebox.showwarning("Warning", "field 'Bundle no' cannot be blank", parent=update_window)
                raise InvalidInputError
            if not entries['Plate SI No'].get().strip():
                messagebox.showwarning("Warning", "field 'Plate SI No' cannot be blank", parent=update_window)
                raise InvalidInputError
        if table_name == "Stack dry leak test":
            if not entries['Stack No'].get().strip():
                messagebox.showwarning("Warning", "field 'Stack No' cannot be blank", parent=update_window)
                raise InvalidInputError

    def save_changes(table_name):
        try:    
            check_blanks(entries)    
            set_clause = ""
            parameters = []        
            for col_name, value in entries.items():
                set_clause += f"`{col_name}` = %s, "
                parameters.append(value.get().strip())    

            # Remove the trailing comma and space
            set_clause = set_clause.rstrip(", ") 

            SrNo_column_name = "SrNo"
            SrNo_column_index = columns.index(SrNo_column_name) if SrNo_column_name in columns else None
            if SrNo_column_index is not None:
                SrNo_value = item_data[SrNo_column_index]
            else:
                messagebox.showerror("Error", "SrNo column not found.")
                return

            try:
                conn = connect_to_database()
                cursor = conn.cursor()

                update_query = f"""
                    UPDATE `{table_name}` SET
                    {set_clause}
                    WHERE `{SrNo_column_name}` = %s
                """
                parameters.append(SrNo_value)  # Add the SrNo_value as the last parameter
                cursor.execute(update_query, parameters)

                conn.commit()
                cursor.close()
                conn.close()

                # Update the tree with new data
                refresh_data(tree, table_name)

                messagebox.showinfo("Success", "Row updated successfully in database!")
            except mysql.connector.Error as e:
                messagebox.showerror("Error", f"Failed to update row: {e}")
            update_window.destroy()
            
        except InvalidInputError:
                return    

    save_button = tk.Button(update_window, text="Save Changes", font=("Ariel", 10), width=12, command=lambda: save_changes(table_name))
    save_button.grid(row=12, column=1, pady=10, sticky="s")    
                

# update button
def update_button_click(tree, table_name):
    print("Update button clicked")
    selected_item = tree.focus()
    if not selected_item:
        messagebox.showerror("Error", "Please select a row to update.")
        return
    open_update_row_window(tree, selected_item,table_name)


def check_password():
    # Actual password
    real_password = "Ohmium@123"
    def submit_password():
        entered_password = password_entry.get()
        if entered_password == real_password:
            messagebox.showinfo("Success", "Password matched!")
            password_window.destroy()  # Close the password window
            show_edit_delete_window()  # Show the new window with 'Edit' and 'Delete' buttons
        else:
            messagebox.showerror("Error", "Password incorrect!")

    # Create a new window for entering the password
    password_window = tk.Toplevel()
    password_window.title("Enter Password")
    password_window.geometry("300x150+500+325")

    # Create label and entry for password
    password_label = tk.Label(password_window, text="Enter Password:")
    password_label.pack(pady=10)
    password_entry = tk.Entry(password_window, show="*")  # Show '*' instead of actual characters
    password_entry.pack(pady=10)

    # Create submit button
    submit_button = tk.Button(password_window, text="Submit", command=submit_password)
    submit_button.pack(pady=10)


def show_edit_delete_window():
    edit_delete_window = tk.Toplevel()
    edit_delete_window.title("Edit/Delete")
    edit_delete_window.geometry("300x120+500+325")
    def edit_action():
        selected_item = tree.selection()[0]  # Assuming 'tree' is your Treeview widget
        if table_name == "Bundle dry leak test":
            edit_row_bundle_leaktest(tree, selected_item)
        elif table_name == "Stack dry leak test":
            edit_row_stack_leaktest(tree, selected_item) 

    def delete_action():
        selected_item = tree.selection()[0]  # Assuming 'tree' is your Treeview widget
        delete_row(selected_item)

    # Create 'Edit' button
    edit_button = tk.Button(edit_delete_window, text="Edit", command=edit_action)
    edit_button.pack(pady=10)

    # Create 'Delete' button
    delete_button = tk.Button(edit_delete_window, text="Delete", command=delete_action)
    delete_button.pack(pady=10)


def edit_row_bundle_leaktest(tree, selected_item):
    start_time = datetime.now().strftime("%H:%M:%S")
    item_data = tree.item(selected_item, 'values')
    item_data_cols = tree["columns"]

    edit_window = tk.Toplevel()
    edit_window.title("Edit Row")
    edit_window.geometry("590x620+30+20")
    
    conn = connect_to_database()
    cursor = conn.cursor()

    cursor.execute(f'DESCRIBE `{table_name}`')
    all_columns = [column[0] for column in cursor.fetchall()]

    cursor.close()
    conn.close()

    entries={}
    def create_label_and_entry(edit_window, text, row, col, col_name):
        label = tk.Label(edit_window, text=text)
        label.grid(row=row, column=col, padx=10, pady=5, sticky='e')
        entry = tk.Entry(edit_window)
        entry.grid(row=row, column=col+1, padx=10, pady=5)
        entry.insert(0, item_data[item_data_cols.index(col_name)])
        entries[col_name] = entry    
        return entry
    
    create_label_and_entry(edit_window, "Operator Name:", 1, 0, "Operator Name")
    create_label_and_entry(edit_window, "Bundle no:", 2, 0, "Bundle no")
    create_label_and_entry(edit_window, "Bin Category:", 2, 2, "Bin Category")
    create_label_and_entry(edit_window, "Plate SI No:", 3, 0, "Plate SI No")
    create_label_and_entry(edit_window, "Stack Bundle \nAssembly Sequence :", 3, 2, "Stack bundle assembly sequence")

    create_label_and_entry(edit_window, 'CL anode @30psi:', 8, 0, 'CL anode at 30psi')
    create_label_and_entry(edit_window, 'OBL anode @30psi:', 9, 0, 'OBL anode at 30psi')
    create_label_and_entry(edit_window, 'CL anode @50psi:', 10, 0, 'CL anode at 50psi')
    create_label_and_entry(edit_window, 'OBL anode @50psi:', 11, 0, 'OBL anode at 50psi')

    create_label_and_entry(edit_window, 'CL cathode @50psi:', 5, 2, 'CL cathode at 50psi')
    create_label_and_entry(edit_window, 'OBL cathode @50psi:', 6, 2, 'OBL cathode at 50psi')
    create_label_and_entry(edit_window, 'CL cathode @100psi:', 7, 2, 'CL cathode at 100psi')
    create_label_and_entry(edit_window, 'OBL cathode @100psi:', 8, 2, 'OBL cathode at 100psi')
    create_label_and_entry(edit_window, 'CL cathode @150psi:', 9, 2, 'CL cathode at 150psi')
    create_label_and_entry(edit_window, 'OBL cathode @150psi:', 10, 2, 'OBL cathode at 150psi')
    create_label_and_entry(edit_window, 'CL cathode @200psi:', 11, 2, 'CL cathode at 200psi')
    create_label_and_entry(edit_window, 'OBL cathode @200psi:', 12, 2, 'OBL cathode at 200psi')
    create_label_and_entry(edit_window, 'CL cathode @250psi:', 13, 2, 'CL cathode at 250psi')
    create_label_and_entry(edit_window, 'OBL cathode @250psi:', 14, 2, 'OBL cathode at 250psi')

    subheading_label = tk.Label(edit_window, text="Observations", font=("Arial", 13))
    subheading_label.grid(row=15, column=0, columnspan=2, pady=10, sticky="ew")

    create_label_and_entry(edit_window, 'Reason for Rejection:', 16, 2, 'Reason for rejection')
    create_label_and_entry(edit_window, 'Initial Observations \non the replaced \nparts/ Rejections:', 17, 0, 'Initial observations on the replaced parts/rejections')
    create_label_and_entry(edit_window, 'Method changes:', 17, 2, 'Method changes')

    def check_blanks(entries):
        # Check if either of the fields is blank
        if not entries['Operator Name'].get().strip():
            messagebox.showwarning("Warning", "field 'Operator Name' cannot be blank", parent=edit_window)
            raise InvalidInputError
        if not entries['Bundle no'].get().strip():
            messagebox.showwarning("Warning", "field 'Bundle no' cannot be blank", parent=edit_window)
            raise InvalidInputError
        if not entries['Plate SI No'].get().strip():
            messagebox.showwarning("Warning", "field 'Plate SI No' cannot be blank", parent=edit_window)
            raise InvalidInputError
        for fieldname, entry in entries.items():
            if ('anode' in fieldname or 'cathode' in fieldname) and not entry.get():               
                messagebox.showwarning("Warning", "One or more required fields are blank.", parent=edit_window)
                raise InvalidInputError
            
    def save_and_close(entries):
        try:
            check_blanks(entries)
            def accept_reject_remarks(entries):
                # Extract values from entry fields as floats (assuming entry fields are numeric) or 'NT'
                cl_values = [entry.get() for key, entry in entries.items() if 'CL' in key]
                obl_values = [entry.get() for key, entry in entries.items() if 'OBL' in key]
                
                # Check if 'NT' appears in any value
                if any(value == 'NT' for value in cl_values + obl_values):
                    Accepted, Rejected = 0, 1  # Reject if 'NT' is found
                    Remarks = 'Rejected'
                    messagebox.showwarning("Warning", "Row Rejected: 'NT' value detected")
                else:
                    # Convert non-NT values to float for comparison
                    cl_values = [float(value) for value in cl_values]
                    obl_values = [float(value) for value in obl_values]

                    # Define the condition for acceptance
                    condition = (all(value < 30 for value in cl_values) and all(value < 10 for value in obl_values))

                    # Use np.where to set Accepted and Rejected based on the condition
                    Accepted, Rejected = np.where(condition, (1, 0), (0, 1))

                    # Set the Remarks based on Accepted and Rejected values
                    Remarks = 'Accepted' if Accepted == 1 and Rejected == 0 else 'Rejected'

                    # Show appropriate message box based on the result
                    if Remarks == 'Accepted':
                        messagebox.showinfo("Success", "Row Accepted")
                    else:
                        messagebox.showwarning("Warning", "Row Rejected")

                return Accepted, Rejected, Remarks
            Accepted, Rejected, Remarks = accept_reject_remarks(entries)
            entries['Accepted'] = Accepted
            entries['Rejected'] = Rejected
            entries['Status'] = Remarks       

        except InvalidInputError:
            return 

        set_clause = ""
        parameters = []

        # for col_name in all_columns:
        for col_name in entries.keys():
            if col_name in ['Accepted', 'Rejected', 'Status']:
                set_clause += f"`{col_name}` = %s, "
                parameters.append(entries[col_name])
                
            elif col_name !='SrNo':
                set_clause += f"`{col_name}` = %s, "
                parameters.append(entries[col_name].get().strip())
        
        set_clause = set_clause.rstrip(", ")  # Remove the trailing comma and space

        SrNo_column_name='SrNo'
        SrNo_column_index = all_columns.index("SrNo") if "SrNo" in all_columns else None
        if SrNo_column_index is not None:
            SrNo_value = item_data[SrNo_column_index]
        else:
            messagebox.showerror("Error", "SrNo column not found.")
            return

        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            
            update_query = f"""
                UPDATE `{table_name}` SET
                {set_clause}
                WHERE `{SrNo_column_name}` = %s
            """
            parameters.append(SrNo_value)  # Add the SrNo_value as the last parameter

             # Debugging: Print parameters and their types
            print("Parameters for query:", parameters)
            print("Parameter types:", [type(param) for param in parameters])
            
            # Convert all values in parameters list
            def convert_to_mysql_compatible(value):
                if isinstance(value, np.generic):
                    return value.item()
                elif isinstance(value, (list, dict, set)):
                    return str(value)
                elif isinstance(value, (np.ndarray)):
                    return value.tolist()
                return value

            parameters = [convert_to_mysql_compatible(value) for value in parameters]

            cursor.execute(update_query, parameters)

            conn.commit()
            cursor.close()
            conn.close()
            
            refresh_data(tree, table_name) # display new data in database
            
            messagebox.showinfo("Success", "Row updated in database successfully!")
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Failed to update row: {e}")
        edit_window.destroy()

    save_button = tk.Button(edit_window, text='Save Changes', command=lambda: save_and_close(entries), width=12, bg='lightgrey')
    save_button.grid(row=4, column=0, columnspan=2, pady=10, padx=100, sticky="s")    


def edit_row_stack_leaktest(tree, selected_item):
    start_time = datetime.now().strftime("%H:%M:%S")
    item_data = tree.item(selected_item, 'values')
    item_data_cols = tree["columns"]

    edit_window = tk.Toplevel()
    edit_window.title("Edit Row")
    edit_window.geometry("875x545+25+25")

    conn = connect_to_database()
    cursor = conn.cursor()

    cursor.execute(f'DESCRIBE `{table_name}`')
    all_columns = [column[0] for column in cursor.fetchall()]

    cursor.close()
    conn.close()

    entries={}
    def create_label_and_entry(edit_window, text, row, col, col_name):
        label = tk.Label(edit_window, text=text)
        label.grid(row=row, column=col, padx=10, pady=5, sticky='e')
        entry = tk.Entry(edit_window)
        entry.grid(row=row, column=col+1, padx=5, pady=5)
        entry.insert(0, item_data[item_data_cols.index(col_name)])
        entries[col_name] = entry    
        return entry
    
    create_label_and_entry(edit_window, "Operator Name:", 1, 0, "Operator Name")
    create_label_and_entry(edit_window, "Stack No:", 1, 2, "Stack No")

    create_label_and_entry(edit_window, 'CL anode @30psi:', 7, 0, 'CL anode at 30psi')
    create_label_and_entry(edit_window, 'OBL anode @30psi:', 8, 0, 'OBL anode at 30psi')
    create_label_and_entry(edit_window, 'CL anode @50psi:', 9, 0, 'CL anode at 50psi')
    create_label_and_entry(edit_window, 'OBL anode @50psi:', 10, 0, 'OBL anode at 50psi')

    create_label_and_entry(edit_window, 'CL cathode @30psi:', 4, 2, 'CL cathode at 30psi')
    create_label_and_entry(edit_window, 'OBL cathode @30psi:', 5, 2, 'OBL cathode at 30psi')
    create_label_and_entry(edit_window, 'CL cathode @50psi:', 6, 2, 'CL cathode at 50psi')
    create_label_and_entry(edit_window, 'OBL cathode @50psi:', 7, 2, 'OBL cathode at 50psi')
    create_label_and_entry(edit_window, 'CL cathode @100psi:', 8, 2, 'CL cathode at 100psi')
    create_label_and_entry(edit_window, 'OBL cathode @100psi:', 9, 2, 'OBL cathode at 100psi')
    create_label_and_entry(edit_window, 'CL cathode @150psi:', 10, 2, 'CL cathode at 150psi')
    create_label_and_entry(edit_window, 'OBL cathode @150psi:', 11, 2, 'OBL cathode at 150psi')
    create_label_and_entry(edit_window, 'CL cathode @200psi:', 12, 2, 'CL cathode at 200psi')
    create_label_and_entry(edit_window, 'OBL cathode @200psi:', 13, 2, 'OBL cathode at 200psi')

    create_label_and_entry(edit_window, 'CL cathode @250psi:', 4, 4, 'CL cathode at 250psi')
    create_label_and_entry(edit_window, 'OBL cathode @250psi:', 5, 4, 'OBL cathode at 250psi')
    create_label_and_entry(edit_window, 'CL cathode @300psi:', 6, 4, 'CL cathode at 300psi')
    create_label_and_entry(edit_window, 'OBL cathode @300psi:', 7, 4, 'OBL cathode at 300psi')
    create_label_and_entry(edit_window, 'CL cathode @350psi:', 8, 4, 'CL cathode at 350psi')
    create_label_and_entry(edit_window, 'OBL cathode @350psi:', 9, 4, 'OBL cathode at 350psi')
    create_label_and_entry(edit_window, 'CL cathode @400psi:', 10, 4, 'CL cathode at 400psi')
    create_label_and_entry(edit_window, 'OBL cathode @400psi:', 11, 4, 'OBL cathode at 400psi')
    create_label_and_entry(edit_window, 'CL cathode @450psi:', 12, 4, 'CL cathode at 450psi')
    create_label_and_entry(edit_window, 'OBL cathode @450psi:', 13, 4, 'OBL cathode at 450psi')

    subheading_label = tk.Label(edit_window, text="Observations", font=("Arial", 14))
    subheading_label.grid(row=14, column=0, columnspan=2, pady=10, sticky="ew")

    create_label_and_entry(edit_window, 'Torque:', 15, 0, 'Torque')
    create_label_and_entry(edit_window, 'Resistance range \n> 5 ohms:', 15, 2, 'Resistance range > 5 ohms')
    create_label_and_entry(edit_window, 'Remarks:', 16, 0, 'Remarks')
    create_label_and_entry(edit_window, 'Observations:', 16, 2, 'Observations')

    def check_blanks(entries):
        # Check if either of the fields is blank
        if not entries['Operator Name'].get().strip():
            messagebox.showwarning("Warning", "field 'Operator Name' cannot be blank", parent=edit_window)
            raise InvalidInputError
        if not entries['Stack No'].get().strip():
            messagebox.showwarning("Warning", "field 'Stack No' cannot be blank", parent=edit_window)
            raise InvalidInputError
        if not entries['Torque'].get().strip():
            messagebox.showwarning("Warning", "field 'Torque' cannot be blank", parent=edit_window)
            raise InvalidInputError
        for fieldname, entry in entries.items():
            if ('anode' in fieldname or 'cathode' in fieldname) and not entry.get():               
                messagebox.showwarning("Warning", "One or more required fields are blank.", parent=edit_window)
                raise InvalidInputError
            
    def save_and_close(entries):
        try:
            check_blanks(entries)
            # save_values(entries)
            def accept_reject_remarks(entries):
                # Extract values from entry fields as floats (assuming entry fields are numeric) or 'NT'
                cl_anode_values = [entry.get() for key, entry in entries.items() if 'CL' in key and 'anode' in key]
                obl_anode_values = [entry.get() for key, entry in entries.items() if 'OBL' in key and 'anode' in key]
                cl_cathode_values = [entry.get() for key, entry in entries.items() if 'CL' in key and 'cathode' in key]
                obl_cathode_values = [entry.get() for key, entry in entries.items() if 'OBL' in key and 'cathode' in key]

                # Convert non-NT values to float for comparison
                cl_anode_values = [float(value) for value in cl_anode_values if value!='NT']
                obl_anode_values = [float(value) for value in obl_anode_values if value!='NT']
                cl_cathode_values = [float(value) for value in cl_cathode_values if value!='NT']
                obl_cathode_values = [float(value) for value in obl_cathode_values if value!='NT']

                # Define the condition for acceptance
                condition = (all(value < 50 for value in cl_anode_values) and all(value < 1 for value in obl_anode_values)
                             and(value < 100 for value in cl_cathode_values) and (value < 7 for value in obl_cathode_values))

                # Use np.where to set Accepted and Rejected based on the condition
                Accepted, Rejected = np.where(condition, (1, 0), (0, 1))

                # Set the Remarks based on Accepted and Rejected values
                Remarks = 'Accepted' if Accepted == 1 and Rejected == 0 else 'Rejected'

                # Show appropriate message box based on the result
                if Remarks == 'Accepted':
                    messagebox.showinfo("Success", "Row Accepted")
                else:
                    messagebox.showwarning("Warning", "Row Rejected")

                return Accepted, Rejected, Remarks
            Accepted, Rejected, Remarks = accept_reject_remarks(entries)
            entries['Accepted'] = Accepted
            entries['Rejected'] = Rejected
            entries['Status'] = Remarks       

        except InvalidInputError:
            return         
        

        set_clause = ""
        parameters = []
        # for col_name in all_columns:
        for col_name in entries.keys():
            if col_name in ['Accepted', 'Rejected', 'Status']:
                set_clause += f"`{col_name}` = %s, "
                parameters.append(entries[col_name])
                
            elif col_name !='SrNo':
                set_clause += f"`{col_name}` = %s, "
                parameters.append(entries[col_name].get().strip())
        
        set_clause = set_clause.rstrip(", ")  # Remove the trailing comma and space

        SrNo_column_name='SrNo'
        SrNo_column_index = all_columns.index("SrNo") if "SrNo" in all_columns else None
        if SrNo_column_index is not None:
            SrNo_value = item_data[SrNo_column_index]
        else:
            messagebox.showerror("Error", "SrNo column not found.")
            return

        try:
            conn = connect_to_database()
            cursor = conn.cursor()
            
            update_query = f"""
                UPDATE `{table_name}` SET
                {set_clause}
                WHERE `{SrNo_column_name}` = %s
            """
            parameters.append(SrNo_value)  # Add the SrNo_value as the last parameter

             # Debugging: Print parameters and their types
            print("Parameters for query:", parameters)
            print("Parameter types:", [type(param) for param in parameters])
            
            # Convert all values in parameters list
            def convert_to_mysql_compatible(value):
                if isinstance(value, np.generic):
                    return value.item()
                elif isinstance(value, (list, dict, set)):
                    return str(value)
                elif isinstance(value, (np.ndarray)):
                    return value.tolist()
                return value

            parameters = [convert_to_mysql_compatible(value) for value in parameters]

            cursor.execute(update_query, parameters)

            conn.commit()
            cursor.close()
            conn.close()
            
            refresh_data(tree, table_name) # display new data in database
            
            messagebox.showinfo("Success", "Row updated in database successfully!")
        except mysql.connector.Error as e:
            messagebox.showerror("Error", f"Failed to update row: {e}")
        edit_window.destroy()

    save_button = tk.Button(edit_window, text='Save Changes', command=lambda: save_and_close(entries), width=12, bg='lightgrey')
    save_button.grid(row=3, column=0, columnspan=2, pady=10, padx=100, sticky="s")
        
            
    
def delete_row(selected_item):
    item_data = tree.item(selected_item, 'values')
    SrNo_column_name = "SrNo"
    SrNo_column_index = columns.index(SrNo_column_name) if SrNo_column_name in columns else None
    if SrNo_column_index is not None:
        SrNo_value = item_data[SrNo_column_index]
    else:
        messagebox.showerror("Error", "SrNo column not found.")
        return

    try:
        conn = connect_to_database()  # Replace with your database connection function
        cursor = conn.cursor()

        delete_query = f"""
            DELETE FROM `{table_name}`
            WHERE `{SrNo_column_name}` = %s
        """
        cursor.execute(delete_query, (SrNo_value,))

        conn.commit()
        cursor.close()
        conn.close()

        tree.delete(selected_item)
        messagebox.showinfo("Success", "Row deleted successfully!")
    except mysql.connector.Error as e:
        messagebox.showerror("Error", f"Failed to delete row: {e}")


def checking_passwd(tree):
    selected_item = tree.selection()
    if selected_item:
        check_password()
    else:
        messagebox.showinfo("No Selection", "Please select a row.")

# filter button
def open_filter_window(table_name,tree,rows,columns):

    for widget in window.winfo_children():
        if isinstance(widget, tk.Toplevel):
            widget.destroy()

    filter_window = tk.Toplevel(window)
    filter_window.title("Filter Data")
    filter_window.geometry("+35+25") 

    # Get the current date and time
    now = datetime.now()
    current_month = now.strftime("%b-%Y")  
    current_date = now.strftime("%Y-%m-%d")  
    # current_week = now.strftime("%U")  
    current_week = datetime.now().isocalendar()[1]
    
    # Create labels and entry fields for filter options
    start_date_label = tk.Label(filter_window, text="Start Date:")
    start_date_label.grid(row=0, column=0, padx=10, pady=5, sticky='e')
    start_date_entry = tk.Entry(filter_window)
    start_date_entry.grid(row=0, column=1, padx=10, pady=5)
    start_date_entry.insert(0, current_date)

    end_date_label = tk.Label(filter_window, text="End Date:")
    end_date_label.grid(row=1, column=0, padx=10, pady=5, sticky='e')
    end_date_entry = tk.Entry(filter_window)
    end_date_entry.grid(row=1, column=1, padx=10, pady=5)
    end_date_entry.insert(0, current_date)

    month_label = tk.Label(filter_window, text="Month:")
    month_label.grid(row=2, column=0, padx=10, pady=5, sticky='e')
    month_entry = tk.Entry(filter_window)
    month_entry.grid(row=2, column=1, padx=10, pady=5)
    month_entry.insert(0, current_month)

    week_no_label = tk.Label(filter_window, text="Week Number:")
    week_no_label.grid(row=3, column=0, padx=10, pady=5, sticky='e')
    week_no_entry = tk.Entry(filter_window)
    week_no_entry.grid(row=3, column=1, padx=10, pady=5)
    week_no_entry.insert(0, current_week)

    shift_label = tk.Label(filter_window, text="Shift:")
    shift_label.grid(row=4, column=0, padx=10, pady=5, sticky='e')
    
    shift_var = tk.StringVar(value="None") 
    shift_radio_A = tk.Radiobutton(filter_window, text="A", variable=shift_var, value="A")
    shift_radio_A.grid(row=4, column=1, padx=10, pady=5)
    shift_radio_B = tk.Radiobutton(filter_window, text="B", variable=shift_var, value="B")
    shift_radio_B.grid(row=4, column=2, padx=10, pady=5)
    shift_radio_C = tk.Radiobutton(filter_window, text="C", variable=shift_var, value="C")
    shift_radio_C.grid(row=4, column=3, padx=10, pady=5)
    
    operator_name_label = tk.Label(filter_window, text="Operator Name:")
    operator_name_label.grid(row=5, column=0, padx=10, pady=5, sticky='e')
    operator_name_entry = tk.Entry(filter_window)
    operator_name_entry.grid(row=5, column=1, padx=10, pady=5)

    # Conditional label display based on stage_choice
    if table_name == "Bundle dry leak test":
        bundle_no_label = tk.Label(filter_window, text="Bundle no:")
        bundle_no_label.grid(row=7, column=0, padx=10, pady=5, sticky='e')
        bundle_no_entry = tk.Entry(filter_window)
        bundle_no_entry.grid(row=7, column=1, padx=10, pady=5)
    
        bin_cat_label = tk.Label(filter_window, text="Bin Category:")
        bin_cat_label.grid(row=8, column=0, padx=10, pady=5, sticky='e')
        bin_cat_entry = tk.Entry(filter_window)
        bin_cat_entry.grid(row=8, column=1, padx=10, pady=5)

        sbas_label = tk.Label(filter_window, text="Stack bundle \nassembly sequence:")
        sbas_label.grid(row=9, column=0, padx=10, pady=5, sticky='e')
        sbas_entry = tk.Entry(filter_window)
        sbas_entry.grid(row=9, column=1, padx=10, pady=5)

        plate_si_label = tk.Label(filter_window, text="Plate SI No:")
        plate_si_label.grid(row=10, column=0, padx=10, pady=5, sticky='e')
        plate_si_entry = tk.Entry(filter_window)
        plate_si_entry.grid(row=10, column=1, padx=10, pady=5)

    if table_name == "Stack dry leak test":
        stack_no_label = tk.Label(filter_window, text="Stack No:")
        stack_no_label.grid(row=6, column=0, padx=10, pady=5, sticky='e')
        stack_no_entry = tk.Entry(filter_window)
        stack_no_entry.grid(row=6, column=1, padx=10, pady=5)

    accepted_label = tk.Label(filter_window, text="Accepted:")
    accepted_label.grid(row=11, column=0, padx=10, pady=5, sticky='e')
    accepted_entry = tk.Entry(filter_window)
    accepted_entry.grid(row=11, column=1, padx=10, pady=5)

    rejected_label = tk.Label(filter_window, text="Rejected:")
    rejected_label.grid(row=12, column=0, padx=10, pady=5, sticky='e')
    rejected_entry = tk.Entry(filter_window)
    rejected_entry.grid(row=12, column=1, padx=10, pady=5)

    remarks_label = tk.Label(filter_window, text="Status")
    remarks_label.grid(row=13, column=0, padx=10, pady=5, sticky='e')
    remarks_entry = tk.Entry(filter_window)
    remarks_entry.grid(row=13, column=1, padx=10, pady=5)
    remarks_entry.insert(0, 'Accepted')

    
    def apply_filter(table_name):
    # Define filters with their respective entry functions
        filters = {
            "Month": month_entry.get(),
            "Week": week_no_entry.get(),
            "Operator Name": operator_name_entry.get(),
        }
        # Initialize filter conditions and variables for specific table names
        filter_conditions = []
        filter_values = []

        # Build the query based on filters
        for key, value in filters.items():
            if value:
                filter_conditions.append(f"`{key.replace('`', '``')}` = %s")
                filter_values.append(value)

        # Check the table name and update filter conditions and variables accordingly
        if table_name == 'Bundle dry leak test':
            if bundle_no_entry.get().strip():
                filter_conditions.append("`Bundle no` REGEXP %s") #so that Retests are also filtered for a particular Bundle No.
                filter_values.append(f"{bundle_no_entry.get().strip()}([^0-9]|$).*") #reason same as above
            if bin_cat_entry.get().strip():
                filter_conditions.append("`Bin Category` = %s")
                filter_values.append(bin_cat_entry.get().strip())
            if sbas_entry.get().strip():
                filter_conditions.append("`Stack bundle assembly sequence` = %s")
                filter_values.append(sbas_entry.get().strip())
            if plate_si_entry.get().strip():
                filter_conditions.append("`Plate SI No` = %s")
                filter_values.append(plate_si_entry.get().strip())
        
        if table_name == 'Stack dry leak test':
            if stack_no_entry.get().strip():
                filter_conditions.append("`Stack No` REGEXP %s") #so that Retests are also filtered for a particular Stack No.
                print("Stack No Entry:", stack_no_entry.get().strip())
                # filter_values.append(f"\\b{stack_no_entry.get()}[^0-9].*") #reason same as above
                filter_values.append(f"{stack_no_entry.get().strip()}([^0-9]|$).*") #reason same as above
                
        if accepted_entry.get().strip():
            if accepted_entry.get().strip() not in ('1', '0', ''):
                messagebox.showerror("Invalid Input", "Accepted can only be 1 or 0.", parent=filter_window)
                raise InvalidInputError
            filter_conditions.append("`Accepted` = %s")
            filter_values.append(accepted_entry.get().strip())
        if rejected_entry.get().strip():
            if rejected_entry.get().strip() not in ('1', '0', ''):
                messagebox.showerror("Invalid Input", "Rejected can only be 1 or 0.", parent=filter_window)
                raise InvalidInputError
            filter_conditions.append("`Rejected` = %s")
            filter_values.append(rejected_entry.get().strip())
        if remarks_entry.get().strip():
            filter_conditions.append("`Status` = %s")
            filter_values.append(remarks_entry.get().strip())
        if shift_var.get().strip() != "None":
            filter_conditions.append("`Shift` = %s")
            filter_values.append(shift_var.get().strip())                          
        

        # Establish database connection
        conn = connect_to_database()
        with conn.cursor() as cursor:
            cursor.execute(f'DESCRIBE `{table_name}`')
            all_columns = [column[0] for column in cursor.fetchall()]

        cursor.close()
        conn.close()

        print(all_columns)

        hidden_columns = {'Week','Month', 'Day', 'Start Time','End Time','Shift'}

        print('hidden_columns: ',hidden_columns)
        visible_columns = [col for col in all_columns if col not in hidden_columns]
        
        # Retrieve the start and end dates from the entry widgets
        start_date = start_date_entry.get()
        end_date = end_date_entry.get()

        # # Construct the SQL query
        query = f"SELECT {', '.join([f'`{col}`' for col in visible_columns + list(hidden_columns)])} FROM `{table_name}`"

        # If there are existing filter conditions, append the date filter to them 
        if not filter_conditions:
            if start_date and end_date:
                date_filter = f"Date >= '{start_date}' AND Date <= '{end_date}'"
                query += " WHERE " + date_filter
                
            elif start_date and not end_date:
                date_filter = f"Date >= '{start_date}'"
                query += " WHERE " + date_filter

            elif not start_date and end_date:
                date_filter = f"Date <= '{end_date}'"
                query += " WHERE " + date_filter

            else:
                query = query

        if filter_conditions:
            if start_date and end_date:
                date_filter = f"Date >= '{start_date}' AND Date <= '{end_date}'"
                query += " WHERE " + " AND ".join(filter_conditions) + " AND " + date_filter
                
            elif start_date and not end_date:
                date_filter = f"Date >= '{start_date}'"
                query += " WHERE " + " AND ".join(filter_conditions) + " AND " + date_filter

            elif not start_date and end_date:
                date_filter = f"Date <= '{end_date}'"
                query += " WHERE " + " AND ".join(filter_conditions) + " AND " + date_filter

            else:    
                query += " WHERE " + " AND ".join(filter_conditions)
        
        print("Debug: Query -", query)
        print("Debug: Filter Values -", filter_values)
        print("Debug: Filter Values -", filter_conditions)    
         
        try:
            # Execute the query with filter values
            conn = connect_to_database()
            with conn.cursor() as cursor:
                cursor.execute(query, filter_values)
                # Fetch all rows from the result set
                filtered_rows = cursor.fetchall() 
                filtered_columns = [desc[0] for desc in cursor.description]
            
            # Clear the existing treeview data
            if tree is not None:
                for item in tree.get_children():
                    tree.delete(item)
                    print('existing treeview deleted')
            
            # Insert new data
            for row in filtered_rows:
                tree.insert("", "end", values=row)
                print('new rows inserted')

            messagebox.showinfo('Success', 'Rows filtered', parent=filter_window)    

        except mysql.connector.Error as e:
            # Handle MySQL errors
            print(f"Error connecting to MySQL: {e}")
            messagebox.showerror("Error", f"Error connecting to MySQL: {e}")
        
        finally:
            cursor.close()
            conn.close()

        return filtered_rows, filtered_columns
    
    def export_to_excel(table_name):
        try:
            filtered_rows, filtered_columns = apply_filter(table_name)
            # if filtered rows are blank
            if not filtered_rows:
                messagebox.showerror('Error', 'No data available to export.', parent=filter_window)
                return
            
            # Convert data to a DataFrame
            df = pd.DataFrame(filtered_rows, columns=filtered_columns)
 
            for col in df.select_dtypes(include=['datetime64']).columns:
                df[col] = df[col].dt.strftime('%Y-%m-%d')  # Format date as YYYY-MM-DD
 
            # Specify the output file path
            output_file = f'Exported-data_{table_name}_{datetime.now().strftime("%Y-%B-%d_%H%Mhrs")}.xlsx'
 
            with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name=table_name, index=False)
            messagebox.showinfo("Success", f"Data is exported with filename:\n'{output_file}'",parent=filter_window)
 
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting data to Excel for {table_name}:{e}")

    export_button = tk.Button(filter_window, text='Export to Excel', font=('Arial', 12),
                          command=lambda: export_to_excel(table_name))
    export_button.grid(row=16, column=0, padx=10, pady=10, sticky='s')

    filter_button = tk.Button(filter_window, text="Filter",font=("Ariel",12), command=lambda:apply_filter(table_name))
    filter_button.grid(row=16, column=1, padx=30, pady=10, sticky='s')

    refresh_button=tk.Button(filter_window, text="Refresh",font=("Ariel",12), command=lambda:refresh_data(tree,table_name))
    refresh_button.grid(row=16, column=2, padx=30, pady=10, sticky='s')


#close button
def close_window():
    window.destroy()

#minimize button
def minimize_window():
    window.iconify()

def dry_leak_test_data_system(table_name):
    # Create main window
    global window
    window = tk.Tk()
    window.configure(bg="lightblue")
    window.title("Dry Leak Test data")
    window.attributes("-fullscreen", True)
    # image_path = r"Untitled design.png"  # Change this to your image file path
    # set_background_image(window, image_path)

    window.grid_rowconfigure(8, weight=1)
    window.grid_columnconfigure(0, weight=1)

    global tree
    tree=display_data_in_treeview(window, table_name)

    # Create font obtjects
    heading_font = ("Arial Black", 24)
    sub_heading_font=("Aharoni",20,"bold")
    label_font = ("Amasis MT Pro Black", 14)
    button_font=("Ariel",12)
    logo_font=("Aptos ExtraBold",40,"bold")
    # logo_font=("Nutino",40,"bold")

    # Create heading label
    heading_label = tk.Label(window, text="Dry Leak Test data", font=heading_font)
    heading_label.grid(row=0, column=0, pady=0, sticky="nw")

    logo_label = tk.Label(window, text="ohmium", font=logo_font)
    logo_label.grid(row=0, column=0, pady=0,sticky="ne")
 
    sub_heading_frame = tk.Frame(window)
    if table_name == 'Bundle dry leak test':
        sub_heading_frame.grid(row=6, column=0, pady=(70,6), padx=(495,150), sticky="w")
    elif table_name == 'Stack dry leak test' :
        sub_heading_frame.grid(row=6, column=0, pady=(70,6), padx=(505,150), sticky="w")     

    sub_heading_text = f"{table_name}"
    sub_heading_label = tk.Label(sub_heading_frame, text=sub_heading_text, font=sub_heading_font)
    sub_heading_label.pack()
    
    ## Date and Time Frame
    time_frame = tk.Frame(window)
    time_frame.grid(row=5, column=0, pady=(70,6), padx=(1000,0), sticky="ew")

    time_label = tk.Label(time_frame, text="", font=("Arial", 11),bg='lightgrey')
    time_label.pack(expand=True, fill='both')
    time_label.config(anchor='w')

    def update_time():
        """
        This function updates the label displaying date and time.
        """
        now = datetime.now().strftime(" %A, %d %B %Y - %H:%M:%S ")
        time_label.config(text=now)
        # Call again after 1 second to keep updating
        time_label.after(1000, update_time)

    update_time()  # Call initially to display time

    window.bind('<Return>', lambda event: start_button_body(table_name))

    # Create buttons
    button_frame= tk.Frame(window)
    button_frame.grid(row=7, column=0, pady=0, padx=20, sticky='nsew')
 
    update_button = tk.Button(button_frame, text="Update", font=('Ariel',12),width=5,bg='lightgray',command=lambda:update_button_click(tree, table_name))
    update_button.grid(row=7, column=1, pady=10, padx=(225,6),sticky='s')

    password_button = tk.Button(button_frame,text='PASSWORD',font=('Ariel',12),bg='lightgray',command=lambda:checking_passwd(tree))
    password_button.grid(row=7,column=3,pady=10,padx=(400,6),sticky='se')

    filter_button = tk.Button(button_frame,text='FILTER',font=('Ariel',12),width=6,bg='lightgray',command=lambda: open_filter_window(table_name, tree, rows, columns))
    filter_button.grid(row=7,column=0,pady=10,padx=(5,6),sticky='sw')

    refresh_button = tk.Button(button_frame,text='Refresh',font=('Ariel',12),width=6,bg='lightgray',command=lambda:refresh_data(tree, table_name))
    refresh_button.grid(row=7,column=0,pady=10,padx=(75,6),sticky='sw')

    close_button = tk.Button(button_frame, text="CLOSE",font=('Ariel',12),bg='lightgray',width=6, command=close_window)
    close_button.grid(row=7, column=1, pady=10,padx=(355,6),sticky='s')

    minimize_button = tk.Button(button_frame, text="Minimize",font=('Ariel',12),bg='lightgray',width=6, command=minimize_window)
    minimize_button.grid(row=7, column=1, pady=10,padx=(495,6),sticky='s')

    return window

# Main function to start the application
def main():
    window = dry_leak_test_data_system(table_name)
    window.mainloop()

#calling of the main function
if __name__ == "__main__":
    main()
