import os
import sys
import subprocess
import json
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from dotenv import load_dotenv, set_key
import webbrowser
from config.control import control_device
from tuya_api.auth import AuthManager# Import the AuthManager class

# Load environment variables
load_dotenv()
class ModernTuyaTokenGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Tuya Token Generator")
        self.root.geometry("1200x800")

        self.entry_widgets = {}
        # Configure a sleek, professional style
        self.style = ttk.Style(theme='superhero')  # A more modern, professional dark theme

        self.control_panel_visible = False
        self.control_panel = None
        self.list_frame = None
        
        # Custom font and styling
        self.primary_font = ('Inter', 10)
        self.header_font = ('Inter', 16, 'bold')
        
        # Enhanced button and widget styling
        self.style.configure('TButton', 
            font=self.primary_font, 
            borderwidth=0, 
            relief='flat',
            bordercolor='none'
        )
        
        # Rounded button styles with hover effects
        self.style.configure('primary.TButton', 
            font=self.primary_font, 
            padding=(15, 10),
            background='#3498db',  # Vibrant blue
            foreground='white'
        )
        self.style.map('primary.TButton',
            background=[('active', '#2980b9')],  # Darker blue on hover
            foreground=[('active', 'white')]
        )

        self.style.configure('toggle.TButton', 
            font=self.primary_font, 
            padding=(15, 10),
            background='#e74c3c',  # Red for OFF state
            foreground='white'
        )
        self.style.map('toggle.TButton',
            background=[('active', '#c0392b')],  # Darker red on hover
            foreground=[('active', 'white')]
        )
            
        self.style.configure('success.TButton', 
            font=self.primary_font, 
            padding=(15, 10),
            background='#2ecc71',  # Green
            foreground='white'
        )
        self.style.map('success.TButton',
            background=[('active', '#27ae60')],  # Darker green on hover
            foreground=[('active', 'white')]
        )
        
        # Enhanced label styling
        self.style.configure('TLabel', 
            font=self.primary_font, 
            foreground='#ecf0f1'  # Light gray for better readability
        )
        self.style.configure('header.TLabel', 
            font=self.header_font, 
            foreground='#ffffff'  # Bright white for headers
        )
        
        # Entry styling
        self.style.configure('TEntry', 
            font=self.primary_font, 
            padding=(10, 5),
            borderwidth=1,
            relief='solid',
            background='#34495e',  # Dark input background
            foreground='#ecf0f1'  # Light text
        )
        
        # Initialize AuthManager for token generation
        self.auth_manager = AuthManager()
        
        # Setup main layout first
        self.setup_main_layout()
        
        # Then generate the token after the layout is set up
        self.automatically_generate_token()

    def automatically_generate_token(self):
        """
        Automatically generate the access token when the GUI starts.
        """
        try:
            # Generate the token
            token = self.auth_manager.get_access_token()
            
            # Display the token in the output text area
            self.output_text.insert(tk.END, f"Access Token: {token}\n")
            self.output_text.insert(tk.END, "Token generated automatically on startup.\n")
            if self.auth_manager.is_token_expired():
                self.output_text.insert(tk.END, "Token is expired.\n")
            else:
                self.output_text.insert(tk.END, "Token is still valid.\n")
            
            # Start the background thread to refresh the token when it expires
            self.auth_manager.start_token_refresh_thread()
        except Exception as e:
            self.output_text.insert(tk.END, f"Failed to generate token: {str(e)}\n")

    def setup_main_layout(self):
        # Main container with modern padding and grid layout
        self.main_container = ttk.Frame(self.root, padding=(30, 30, 30, 30))
        self.main_container.pack(fill=tk.BOTH, expand=True)
        self.main_container.columnconfigure(0, weight=1)
        self.main_container.rowconfigure(0, weight=1)

        # Create a notebook with a more modern look
        self.notebook = ttk.Notebook(self.main_container, style='primary.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs with modern styling
        self.create_credentials_tab()
        self.create_config_tab()
        self.create_token_history_tab()
        self.create_help_tab()

    def create_credentials_tab(self):
        # Credentials Tab with modern design
        credentials_frame = ttk.Frame(self.notebook, padding=(30, 30, 30, 30))
        self.notebook.add(credentials_frame, text="🔑 Credentials")

        # Modern header
        title_label = ttk.Label(
            credentials_frame, 
            text="Tuya API Credentials", 
            style='header.TLabel'
        )
        title_label.pack(pady=(0, 30), anchor='w')

        # Credentials Input Frame
        input_frame = ttk.Frame(credentials_frame)
        input_frame.pack(fill=tk.X, expand=True)

        # Credentials Fields with improved layout
        credentials = [
            ("Access ID:", "access_id", False),  # Not sensitive
            ("Access Key:", "access_key", True),  # Sensitive
            ("Base URL:", "base_url", True),      # Sensitive
            # ("Device ID (optional):", "device_id", False)  # Not sensitive
        ]

        self.entry_vars = {}
        self.entry_widgets = {}
        for label_text, entry_name, is_sensitive in credentials:
            row_frame = ttk.Frame(input_frame)
            row_frame.pack(fill=tk.X, pady=10)

            label = ttk.Label(row_frame, text=label_text, width=20)
            label.pack(side=tk.LEFT, padx=(0, 15))
            
            var = tk.StringVar(value="")  # Clear old credentials
            entry = ttk.Entry(row_frame, textvariable=var, width=50)
            if is_sensitive:
                entry.config(show="*")  # Hide sensitive information by default
            entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
            
            self.entry_vars[entry_name] = var
            self.entry_widgets[entry_name] = entry

            # Add eye icon button for sensitive fields
            if is_sensitive:
                eye_btn = ttk.Button(
                    row_frame, 
                    text="👁️",  # Eye icon
                    width=3, 
                    command=lambda e=entry: self.toggle_entry_visibility(e)
                )
                eye_btn.pack(side=tk.LEFT, padx=(5, 0))

        # Action Buttons with rounded corners and modern styling
        button_frame = ttk.Frame(credentials_frame)
        button_frame.pack(fill=tk.X, pady=(30, 20))

        save_btn = ttk.Button(
            button_frame, 
            text="Save Credentials", 
            command=self.save_to_env, 
            style='success.TButton',
            width=25
        )
        save_btn.pack(side=tk.LEFT, padx=10, expand=True)

        # generate_btn = ttk.Button(
        #     button_frame, 
        #     text="Generate Token", 
        #     command=self.generate_token, 
        #     style='primary.TButton',
        #     width=25
        # )
        # generate_btn.pack(side=tk.RIGHT, padx=10, expand=True)

        # Output Section with modern scrolled text
        output_frame = ttk.LabelFrame(
            credentials_frame, 
            text="Token Output", 
            style='primary.TLabelframe'
        )
        output_frame.pack(fill=tk.BOTH, expand=True, pady=(30, 0))

        self.output_text = scrolledtext.ScrolledText(
            output_frame, 
            wrap=tk.WORD, 
            height=10, 
            font=('Consolas', 10),
            background='#2c3e50',  # Dark background for code
            foreground='#ecf0f1'   # Light text for readability
        )
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        fetch_devices_btn = ttk.Button(
            button_frame, 
            text="Fetch Devices", 
            command=self.fetch_and_select_device, 
            style='primary.TButton',
            width=25
        )
        fetch_devices_btn.pack(side=tk.LEFT, padx=10, expand=True)

    def fetch_and_select_device(self):
        """
        Fetch the list of devices and prompt the user to select one.
        """
        try:
            # Fetch the list of devices
            devices = self.get_device_list()
            
            if not devices:
                messagebox.showerror("Error", "No devices found or failed to fetch devices.")
                return
            
            # Create a selection dialog
            self.device_selection_dialog(devices)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch devices: {str(e)}")

    def get_device_list(self):
        """
        Fetch the list of devices using the get_devices_list.py script.
        """
        try:
            # Run the get_devices_list.py script
            result = subprocess.run(
                [sys.executable, os.path.join("config", "get_devices_list.py")],
                capture_output=True, 
                text=True, 
                check=True
            )
            
            # Debug: Print the raw output
            print("Raw output from get_devices_list.py:", result.stdout)
            
            # Parse the output to get the device list
            devices = json.loads(result.stdout)
            return devices
        except subprocess.CalledProcessError as e:
            print("Error running get_devices_list.py:", e.stderr)
            return []
        except json.JSONDecodeError as e:
            print("Failed to parse JSON:", e)
            return []

    def device_selection_dialog(self, devices):
        """
        Display a dialog for the user to select a device.
        """
        # Create a new top-level window
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Device")
        dialog.geometry("400x300")  # Set an initial size
        dialog.minsize(300, 200)   # Set a minimum size to ensure usability
        dialog.resizable(True, True)  # Allow resizing
        
        # Make it a proper dialog window
        dialog.transient(self.root)  # Make the dialog dependent on the main window
        dialog.grab_set()  # Prevent interaction with the main window until closed
        
        # Create main container frame
        main_container = ttk.Frame(dialog)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create content container with padding
        container = ttk.Frame(main_container, padding="10")
        container.pack(fill=tk.BOTH, expand=True)
        
        # Create a label
        label = ttk.Label(container, text="Select a device:", style='header.TLabel')
        label.pack(anchor='w')  # Align to the left
        
        # Create a frame for the listbox to control its expansion
        listbox_frame = ttk.Frame(container)
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Create a listbox with scrollbar
        scrollbar = ttk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = tk.Listbox(
            listbox_frame,
            selectmode=tk.SINGLE,
            font=('Consolas', 10),
            yscrollcommand=scrollbar.set
        )
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Add devices to the listbox
        for device in devices:
            listbox.insert(tk.END, device['name'])
        
        # Create a button container frame
        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Create a button to confirm the selection
        confirm_btn = ttk.Button(
            button_frame,
            text="OK",
            command=lambda: self.save_selected_device(listbox, devices, dialog),
            style='success.TButton'
        )
        confirm_btn.pack(side=tk.RIGHT)
        
        # Configure weights for responsiveness
        container.columnconfigure(0, weight=1)
        container.rowconfigure(1, weight=1)

    def save_selected_device(self, listbox, devices, dialog):
        """
        Save the selected device ID to the .env file and close the dialog.
        """
        selected_index = listbox.curselection()
        if not selected_index:
            messagebox.showerror("Error", "No device selected!")
            return
        
        # Get the selected device
        selected_device = devices[selected_index[0]]
        device_id = selected_device['id']
        
        # Save the device ID to the .env file
        try:
            set_key(".env", "DEVICE_ID", device_id)
            messagebox.showinfo("Success", f"Device ID '{device_id}' saved successfully!")
            
            # Update the DEVICE_ID entry in the GUI (if it exists)
            if 'device_id' in self.entry_vars:
                self.entry_vars['device_id'].set(device_id)
            
            # Close the dialog
            dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save device ID: {str(e)}")

    def toggle_entry_visibility(self, entry):
        """
        Toggle the visibility of the text in the entry widget.
        """
        if entry.cget("show") == "*":
            entry.config(show="")  # Show text
        else:
            entry.config(show="*")  # Hide text

    def create_config_tab(self):
        # Configuration Tab
        config_frame = ttk.Frame(self.notebook, padding="20 20 20 20")
        self.notebook.add(config_frame, text="⚙️ Configuration")

        # Config Folder Section
        config_label = ttk.Label(
            config_frame, 
            text="Configuration Files", 
            font=('Segoe UI', 18, 'bold'),
            style='primary.TLabel'
        )
        config_label.pack(pady=(0, 20))

        # Container for list and control panel
        container_frame = ttk.Frame(config_frame)
        container_frame.pack(fill=tk.BOTH, expand=True)

        # Listbox and Scrollbar for Config Files
        self.list_frame = ttk.Frame(container_frame)
        self.list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.file_listbox = tk.Listbox(
            self.list_frame, 
            selectmode=tk.SINGLE, 
            font=('Consolas', 10)
        )
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(
            self.list_frame, 
            orient=tk.VERTICAL, 
            command=self.file_listbox.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_listbox.config(yscrollcommand=scrollbar.set)

        # Create hidden control panel
        self.control_panel = ttk.Frame(container_frame)
        self.control_panel.pack_forget()  # Initially hidden

        # Populate the listbox
        config_folder = os.path.join(os.path.dirname(__file__), 'config')
        if os.path.exists(config_folder):
            for file in os.listdir(config_folder):
                self.file_listbox.insert(tk.END, file)

        # Action Buttons
        button_frame = ttk.Frame(config_frame)
        button_frame.pack(fill=tk.X, pady=20)

        run_btn = ttk.Button(
            button_frame, 
            text="Run Selected File", 
            command=self.run_selected_file, 
            bootstyle="primary",
            width=20,
            style='primary.TButton'
        )
        run_btn.pack(side=tk.LEFT, padx=10, expand=True)

        add_config_btn = ttk.Button(
            button_frame, 
            text="Add New Config", 
            command=self.add_new_config, 
            bootstyle="success",
            width=20,
            style='success.TButton'
        )
        add_config_btn.pack(side=tk.RIGHT, padx=10, expand=True)

        # Output Section
        output_frame = ttk.LabelFrame(config_frame, text="Output", style='primary.TLabelframe')
        output_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        self.config_output_text = scrolledtext.ScrolledText(
            output_frame, 
            wrap=tk.WORD, 
            height=10, 
            font=('Consolas', 10)
        )
        self.config_output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def create_token_history_tab(self):
        # Token History Tab
        history_frame = ttk.Frame(self.notebook, padding="20 20 20 20")
        self.notebook.add(history_frame, text="🕰️ Token History")

        # Placeholder for token history functionality
        history_label = ttk.Label(
            history_frame, 
            text="Token Generation History", 
            font=('Segoe UI', 18, 'bold'),
            style='primary.TLabel'
        )
        history_label.pack(pady=(0, 20))

        # TODO: Implement actual token history tracking
        placeholder_text = ttk.Label(
            history_frame, 
            text="Token history tracking coming soon!", 
            style='secondary.TLabel'
        )
        placeholder_text.pack(expand=True)

    def create_help_tab(self):
        # Help Tab
        help_frame = ttk.Frame(self.notebook, padding="20 20 20 20")
        self.notebook.add(help_frame, text="❓ Help")

        # Help Content
        help_title = ttk.Label(
            help_frame, 
            text="Help & Documentation", 
            font=('Segoe UI', 18, 'bold'),
            style='primary.TLabel'
        )
        help_title.pack(pady=(0, 20))

        help_content = ttk.Label(
            help_frame, 
            text=(
                "Tuya Token Generator Help:\n\n"
                "1. Enter your Tuya API Credentials in the Credentials tab\n"
                "2. Save the credentials using 'Save Credentials' button\n"
                "3. Generate token using 'Generate Token' button\n"
                "4. Check configuration files in the Configuration tab\n"
                "\nFor more information, visit Tuya's developer documentation."
            ),
            style='secondary.TLabel',
            wraplength=500,
            justify=tk.LEFT
        )
        help_content.pack(pady=20)

        # Documentation Link
        doc_link = ttk.Button(
            help_frame, 
            text="Open Tuya Developer Docs", 
            command=self.open_tuya_docs,
            bootstyle="info",
            style='info.TButton'
        )
        doc_link.pack(pady=10)

    def save_to_env(self):
        """
        Save input values to the .env file.
        """
        # Collect values from entry variables
        values = {
            "TUYA_ACCESS_ID": self.entry_vars['access_id'].get(),
            "TUYA_ACCESS_KEY": self.entry_vars['access_key'].get(),
            "TUYA_BASE_URL": self.entry_vars['base_url'].get(),
            # "DEVICE_ID": self.entry_vars['device_id'].get()
        }

        # Validate required fields
        if not all([values["TUYA_ACCESS_ID"], values["TUYA_ACCESS_KEY"], values["TUYA_BASE_URL"]]):
            messagebox.showerror("Error", "Access ID, Access Key, and Base URL are required!")
            return

        # Save to .env file
        try:
            for key, value in values.items():
                set_key(".env", key, value)
            messagebox.showinfo("Success", "Credentials saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save credentials: {str(e)}")

    # def generate_token(self):
    #     """
    #     Run the main.py script and display the output.
    #     """
    #     # Clear previous output
    #     self.output_text.delete(1.0, tk.END)

    #     # Run the main.py script
    #     try:
    #         result = subprocess.run(
    #             [sys.executable, "main.py"],
    #             capture_output=True, 
    #             text=True, 
    #             check=True
    #         )
    #         self.output_text.insert(tk.END, result.stdout)
    #     except subprocess.CalledProcessError as e:
    #         self.output_text.insert(tk.END, f"Error: {e.stderr}")
    #     except Exception as e:
    #         self.output_text.insert(tk.END, f"Unexpected error: {str(e)}")

    def run_selected_file(self):
        """
        Run the selected configuration file or display control buttons for control.py.
        """
        # Clear previous output
        self.config_output_text.delete(1.0, tk.END)

        # Get the selected file
        selected_indices = self.file_listbox.curselection()
        if not selected_indices:
            messagebox.showerror("Error", "No file selected!")
            return

        selected_file = self.file_listbox.get(selected_indices[0])
        config_folder = os.path.join(os.path.dirname(__file__), 'config')
        file_path = os.path.join(config_folder, selected_file)

        if selected_file == "control.py":
            # Display control buttons in sliding panel
            self.display_control_buttons()
        else:
            # Hide control panel if visible
            if self.control_panel_visible:
                self.hide_control_panel()
                
            # Run the selected file
            try:
                result = subprocess.run(
                    [sys.executable, file_path],
                    capture_output=True, 
                    text=True, 
                    check=True
                )
                self.config_output_text.insert(tk.END, result.stdout)
            except subprocess.CalledProcessError as e:
                self.config_output_text.insert(tk.END, f"Error: {e.stderr}")
            except Exception as e:
                self.config_output_text.insert(tk.END, f"Unexpected error: {str(e)}")

    def display_control_buttons(self):
        """
        Display buttons to control the device in a sliding panel.
        """
        # Clear any existing widgets in the control panel
        for widget in self.control_panel.winfo_children():
            widget.destroy()

        # Create header for control panel
        header = ttk.Label(
            self.control_panel,
            text="Device Controls",
            font=('Segoe UI', 14, 'bold'),
            style='primary.TLabel'
        )
        header.pack(pady=(0, 20))

        # Define the switches and their initial states
        self.switch_states = {
            "switch_1": False,
            "switch_2": False,
            "switch_3": False,
            "switch_4": False
        }

        # Create buttons for each switch
        for i,switch in enumerate(self.switch_states.keys(),1):
            btn = ttk.Button(
                self.control_panel,
                text=f"Switch {i} OFF",
                command=lambda s=switch: self.toggle_switch(s),
                style='toggle.TButton',
                width=20
            )
            btn.pack(pady=10, padx=20)
    

        # Add close button
        close_btn = ttk.Button(
            self.control_panel,
            text="Close Controls",
            command=self.hide_control_panel,
            style='success.TButton',
            width=20
        )
        close_btn.pack(pady=(20, 10), padx=20)
    # Define custom style for toggle buttons
        self.style.configure('toggle.TButton', 
            font=self.primary_font, 
            padding=(15, 10),
            background='#e74c3c',  # Red for OFF state
            foreground='white'
        )
        self.style.map('toggle.TButton',
            background=[('active', '#c0392b')],  # Darker red on hover
            foreground=[('active', 'white')]
        )

        # Show the control panel
        self.show_control_panel()

    def show_control_panel(self):
        """Show the control panel with a sliding effect."""
        if not self.control_panel_visible:
            self.control_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(20, 0))
            self.control_panel_visible = True

    def hide_control_panel(self):
        """Hide the control panel."""
        if self.control_panel_visible:
            self.control_panel.pack_forget()
            self.control_panel_visible = False

    def toggle_switch(self, switch):
        """
        Toggle the state of a switch and send the command to the device.
        """
        # Toggle the state
        self.switch_states[switch] = not self.switch_states[switch]
        command = "true" if self.switch_states[switch] else "false"

    # Update the button text and color
        for widget in self.control_panel.winfo_children():
            if isinstance(widget, ttk.Button):
                button_text = widget.cget("text").lower()
                if f"switch {switch[-1]}" in button_text:
                    if self.switch_states[switch]:
                        widget.configure(text=f"Switch {switch[-1]} ON", style='success.TButton')  # Green for ON
                    else:
                        widget.configure(text=f"Switch {switch[-1]} OFF", style='toggle.TButton')  # Red for OFF
                    break

        # Send the command to the device
        API_URL = os.getenv("TUYA_BASE_URL")
        CLIENT_ID = os.getenv("TUYA_ACCESS_ID")
        SECRET = os.getenv("TUYA_ACCESS_KEY")
        ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
        DEVICE_ID = os.getenv("DEVICE_ID")

        if not all([API_URL, CLIENT_ID, SECRET, ACCESS_TOKEN, DEVICE_ID]):
            messagebox.showerror("Error", "Missing required environment variables in .env file.")
            return

        result = control_device(API_URL, CLIENT_ID, SECRET, ACCESS_TOKEN, DEVICE_ID, switch, command)
        self.config_output_text.insert(tk.END, f"Command sent: {switch} = {command}\nResponse: {result}\n")

    def add_new_config(self):
        """
        Add a new configuration file.
        """
        config_folder = os.path.join(os.path.dirname(__file__), 'config')
        file_path = filedialog.askopenfilename(
            initialdir=config_folder, 
            title="Select a Python configuration file",
            filetypes=[("Python files", "*.py")]
        )
        
        if file_path:
            # Copy the selected file to the config folder
            try:
                import shutil
                destination = os.path.join(config_folder, os.path.basename(file_path))
                shutil.copy2(file_path, destination)
                
                # Refresh the listbox
                self.file_listbox.delete(0, tk.END)
                for file in os.listdir(config_folder):
                    self.file_listbox.insert(tk.END, file)
                
                messagebox.showinfo("Success", "Configuration file added successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add configuration file: {str(e)}")

    def open_tuya_docs(self):
        """
        Open Tuya developer documentation in the default web browser.
        """
        webbrowser.open("https://developer.tuya.com/en/docs/")


def main():
    # Use Inter font if available, fallback to system font
    try:
        import tkinter.font as tkfont
        tkfont.nametofont("TkDefaultFont").configure(family="Inter", size=10)
    except:
        pass

    root = ttk.Window(themename="superhero")  # Modern dark theme
    app = ModernTuyaTokenGenerator(root)
    root.mainloop()

if __name__ == "__main__":
    main()