import subprocess

def execute_script(script):
    try:
        # Execute the command as a subprocess
        subprocess.run(["python", script], check=True)
    except subprocess.CalledProcessError as e:
        # Handle any errors that occur during the subprocess execution
        print(f"Error executing command: {e}")
    except Exception as e:
        # Handle any other exceptions
        print(f"An error occurred: {e}")

# Execute the first script
execute_script("digital_traveller_card.py")
