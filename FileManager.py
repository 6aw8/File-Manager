import os
import json
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from datetime import datetime
from PIL import Image, ImageTk
import sys # Keep sys for exit and platform checks
import shutil # For deleting folders recursively

# --- Configuration ---
CONFIG_FILE = "name.json"
VERSION = "4.3" # Updated version with insane details in file info
STATUS = "Professional Edition"

# --- Terminal Colors (ANSI Escape) ---
RESET = "\033[0m"
BOLD = "\033[1m"
BLUE = "\033[94m"
GREEN = "\033[92m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
YELLOW = "\033[93m"
RED = "\033[91m"

# --- Helper Functions (for both Terminal & GUI) ---

def get_username():
    """Retrieves or sets the username from/to a JSON configuration file."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as file:
                data = json.load(file)
                username = data.get("username")
                if username:
                    return username
        except json.JSONDecodeError:
            print(f"{RED}[!] 'name.json' is empty or corrupted. Resetting username.{RESET}")

    username = input("What would you like to set your username as?: ").strip()
    if not username:
        username = "User"
    with open(CONFIG_FILE, "w") as file:
        json.dump({"username": username}, file)
    return username

def get_greeting(username):
    """Generates a time-based greeting for the terminal banner."""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        greeting = "Good morning"
    elif 12 <= hour < 17:
        greeting = "Good afternoon"
    elif 12 <= hour < 21:
        greeting = "Good evening"
    else:
        greeting = "Good night"
    return f"{CYAN}{greeting}, {username}!{RESET}"

def print_banner(username):
    """Prints the stylish ASCII art banner and menu options for the terminal interface."""
    os.system("cls" if os.name == "nt" else "clear")
    # Using a raw string (r"""...""") to avoid SyntaxWarning for backslashes
    print(rf"""{BLUE}
                       _____                                                             _____ 
                      ( ___ )                                                           ( ___ )
                       |   |~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|   | 
                       |   |  _____ _ _        __  __                                    |   | 
                       |   | |  ___(_) | ___  |  \/  | __ _ _ __   __ _  __ _  ___ _ __  |   | 
                       |   | | |_  | | |/ _ \ | |\/| |/ _` | '_ \ / _` |/ _` |/ _ \ '__| |   | 
                       |   | |  _| | | |  __/ | |  | | (_| | | | | (_| | (_| |  __/ |    |   | 
                       |   | |_|   |_|_|\___| |_|  |_|\__,_|_| |_|\__,_|\__, |\___|_|    |   | 
                       |   |                                            |___/            |   | 
                       |___|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~|___| 
                      (_____)                                                           (_____)

{RESET}
                      Current Directory: {os.getcwd()}

                      {YELLOW}[01]{RESET} List All Items     {YELLOW}[02]{RESET} List Root Directories  {YELLOW}[03]{RESET} List Folders Only
                      {YELLOW}[04]{RESET} Open File          {YELLOW}[05]{RESET} Delete File            {YELLOW}[06]{RESET} Find File/Folder
                      {YELLOW}[09]{RESET} Launch GUI (Beta)  {YELLOW}[00]{RESET} Exit

{get_greeting(username)}
""")

def print_tree(start_path=".", prefix="", mode="all"):
    """
    Prints a directory tree structure to the console with colored output.
    mode: 'all' (default) - print dirs and files
          'folders'       - print only folders
          'files'         - print only files
    """
    try:
        entries = sorted(os.listdir(start_path), key=lambda x: (not os.path.isdir(os.path.join(start_path, x)), x.lower()))
    except PermissionError:
        print(f"{prefix}{RED}└── [Permission Denied]{RESET}")
        return
    except FileNotFoundError:
        print(f"{prefix}{RED}└── [Path Not Found]{RESET}")
        return

    for index, entry in enumerate(entries):
        path = os.path.join(start_path, entry)
        connector = "└── " if index == len(entries) - 1 else "├── "
        try:
            is_dir = os.path.isdir(path)
            if mode == "folders" and not is_dir:
                continue
            if mode == "files" and is_dir:
                continue

            if is_dir:
                print(f"{prefix}{BLUE}{connector}{entry}/{RESET}")
                if mode != "files":
                    new_prefix = prefix + ("    " if index == len(entries) - 1 else "│   ")
                    print_tree(path, new_prefix, mode)
            else:
                if mode != "folders":
                    print(f"{prefix}{GREEN}{connector}{entry}{RESET}")

        except PermissionError:
            print(f"{prefix}{RED}{connector}[Access Denied]{RESET}")
        except Exception as e:
            print(f"{prefix}{RED}{connector}[Error: {e}]{RESET}")

# --- Terminal Menu Functions (simplified for GUI focus) ---

def list_files_terminal():
    print(f"{CYAN}----- ALL ITEMS (Tree View) -----{RESET}")
    print_tree(os.getcwd(), mode="all")
    print()

def list_roots_terminal():
    print(f"{CYAN}----- ROOT DIRECTORIES (Top Level) -----{RESET}")
    try:
        if os.name == 'nt':
            import string
            drives = ['%s:\\' % d for d in string.ascii_uppercase if os.path.exists('%s:\\' % d)] # Corrected 'd d' to 'd'
            for drive in drives:
                print(f"{BLUE}└── {drive}{RESET}")
        else:
            common_roots = ["bin", "boot", "dev", "etc", "home", "lib", "media", "mnt", "opt", "proc", "root", "run", "sbin", "srv", "sys", "tmp", "usr", "var"]
            for root_dir in common_roots:
                full_path = os.path.join('/', root_dir)
                if os.path.exists(full_path) and os.path.isdir(full_path):
                    print(f"{BLUE}└── /{root_dir}/{RESET}")
            current_top_dirs = [d for d in os.listdir(os.getcwd()) if os.path.isdir(os.path.join(os.getcwd(), d))]
            for d in current_top_dirs:
                print(f"{BLUE}└── {d}/{RESET} (in current dir)")

    except Exception as e:
        print(f"{RED}[!] Error: {e}{RESET}")
    print()

def list_folders_terminal():
    print(f"{CYAN}----- FOLDERS (Tree View) -----{RESET}")
    print_tree(os.getcwd(), mode="folders")
    print()

def open_file_terminal():
    name = input("Enter full file/folder path to open: ").strip()
    if os.path.exists(name):
        try:
            if os.name == "nt":
                os.startfile(name)
            else:
                import subprocess
                if sys.platform == "darwin":
                    subprocess.call(("open", name))
                else:
                    subprocess.call(("xdg-open", name))
            print(f"{GREEN}[+] Opened '{name}'.{RESET}")
        except Exception as e:
            print(f"{RED}[!] Error opening '{name}': {e}{RED}")
    else:
        print(f"{RED}[-] File or folder not found: '{name}'.{RESET}")
    print()

def delete_file_terminal():
    name = input("Enter full file/folder path to delete: ").strip()
    if not os.path.exists(name):
        print(f"{RED}[-] Item not found: '{name}'.{RESET}")
        return

    is_dir = os.path.isdir(name)
    item_type = "folder" if is_dir else "file"
    confirm_msg = f"Are you sure you want to delete this {item_type} '{name}'? (yes/no): "
    if is_dir:
        confirm_msg += " WARNING: This will delete all its contents and is irreversible!"

    confirm = input(confirm_msg).strip().lower()
    if confirm == "yes":
        try:
            if is_dir:
                shutil.rmtree(name)
            else:
                os.remove(name)
            print(f"{GREEN}[+] {item_type.capitalize()} deleted successfully.{RESET}")
        except PermissionError:
            print(f"{MAGENTA}[!] Permission denied. Try running as Administrator.{RESET}")
        except Exception as e:
            print(f"{RED}[!] Error deleting {item_type}: {e}{RESET}")
    else:
        print(f"{YELLOW}[-] Deletion cancelled.{RESET}")
    print()

def find_file_terminal():
    name = input("Enter file or folder name to find: ").strip()
    if not name:
        print(f"{YELLOW}[!] Search query cannot be empty.{RESET}")
        return

    found = False
    print(f"{CYAN}----- Searching for '{name}' -----{RESET}")
    try:
        for root, dirs, files in os.walk(os.getcwd()):
            if name in files:
                print(f"{GREEN}[+] Found file at: {os.path.join(root, name)}{RESET}")
                found = True
            if name in dirs:
                print(f"{BLUE}[+] Found folder at: {os.path.join(root, name)}{RESET}")
                found = True
    except Exception as e:
        print(f"{RED}[!] Error during search: {e}{RESET}")

    if not found:
        print(f"{MAGENTA}[-] File or folder '{name}' not found.{RESET}")
    print()

# --- GUI Implementation (CustomTkinter) ---

# Constants for notification stacking
NOTIFICATION_WIDTH = 300
NOTIFICATION_HEIGHT = 50
NOTIFICATION_GAP = 10
MAX_DISPLAYED_NOTIFICATIONS = 5 # Limit to prevent screen overflow
NOTIFICATION_SLOT_HEIGHT = NOTIFICATION_HEIGHT + NOTIFICATION_GAP # Height of each notification slot

class FileManagerGUI:
    """
    A CustomTkinter-based graphical user interface for the file manager.
    """
    def __init__(self, root):
        self.root = root
        self.root.title(f"📁 File Manager GUI v{VERSION} | {STATUS}")
        # Reduced window size
        self.root.geometry("1100x700") 
        self.root.minsize(800, 550) # Reduced minimum window size

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue") # Keep blue for CustomTkinter's base theme

        # Custom colors for a more polished look
        self.PRIMARY_BG = "#2a2a2a" # Dark background
        self.SECONDARY_BG = "#333333" # Slightly lighter for panels
        self.ACCENT_COLOR = "#00ffff" # Cyan for highlights and path
        self.TEXT_COLOR = "#f0f0f0" # Light text
        self.WARN_COLOR = "#ffff66" # Yellow for warnings/meta info
        self.ERROR_COLOR = "#cc3333" # Red for errors
        self.BORDER_COLOR = "#5c5c5c" # Grey for borders

        self.current_path = os.getcwd()
        self.path_history = [self.current_path]
        self.history_index = 0

        self.filter_mode = "All Files"
        self.sort_mode = "Name (A-Z)" # Default sort mode
        self.tk_img = None
        self.selected_item_path = None

        # Variables for copy/cut/paste
        self.clipboard_item = None # Stores the full path of the item to be copied/moved
        self.clipboard_mode = None # 'copy' or 'cut'

        # List to manage active notification windows for stacking
        # Each item: (ctk.CTkToplevel_instance, current_y_position, after_job_id_for_slide_out)
        self.active_notifications = [] 

        self.setup_ui()
        self.populate_file_list() # Initial population of the file list

    def go_back(self):
        """Navigates to the previous directory in the history."""
        if self.history_index > 0:
            self.history_index -= 1
            self.current_path = self.path_history[self.history_index]
            self.populate_file_list()
            self.update_path_label()
            self.update_status(f"Moved back to: {self.current_path}")
            self.show_custom_notification(f"Navigated back to {os.path.basename(self.current_path)}")
        else:
            self.update_status("Already at the beginning of history.")
            self.show_custom_notification("Already at root directory.", is_error=True)
        self.update_go_back_button_state() # Ensure button state is updated

    def change_directory(self):
        """Opens a directory chooser dialog and updates the file list."""
        new_dir = filedialog.askdirectory(initialdir=self.current_path)
        if new_dir and new_dir != self.current_path:
            self.current_path = new_dir
            self.path_label.configure(text=f"Current Directory: {self.current_path}")
            self.update_path_history(self.current_path)
            self.populate_file_list()
            self.update_status(f"Changed directory to: {self.current_path}")
            self.show_custom_notification(f"Changed directory to {os.path.basename(self.current_path)}")
        else:
            self.update_status("Directory change cancelled or same directory selected.")
            self.show_custom_notification("Directory change cancelled.", is_error=True)

    def update_path_label(self):
        """Updates the text of the path label."""
        self.path_label.configure(text=f"Current Directory: {self.current_path}")

    def update_go_back_button_state(self):
        """Enables/disables the 'Go Back' button based on history."""
        if self.history_index > 0:
            self.go_back_button.configure(state="normal")
        else:
            self.go_back_button.configure(state="disabled")

    def setup_ui(self):
        """Builds the main GUI layout and widgets using CustomTkinter."""

        # --- Top Frame: Path, Change Dir, Go Back, Search ---
        top_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        top_frame.pack(fill=ctk.X, padx=15, pady=(15, 8))

        self.go_back_button = ctk.CTkButton(top_frame, text="❮ Go Back",
                                            state="disabled",
                                            width=110,
                                            height=30,
                                            font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                                            fg_color="#0066cc", # Changed to blue
                                            hover_color="#004499", # Changed to blue
                                            corner_radius=8,
                                            border_width=1,
                                            border_color=self.BORDER_COLOR)
        self.go_back_button.configure(command=self.go_back)
        self.go_back_button.pack(side=ctk.LEFT, padx=(0, 15))

        self.path_label = ctk.CTkLabel(top_frame, text=f"Current Directory: {self.current_path}",
                                        font=ctk.CTkFont(family="Inter", size=14, weight="bold"),
                                        text_color=self.ACCENT_COLOR) # Use accent color
        self.path_label.pack(side=ctk.LEFT, expand=True, fill=ctk.X, padx=5)

        ctk.CTkButton(top_frame, text="📂 Change Dir", command=self.change_directory,
                      width=140, height=30,
                      font=ctk.CTkFont(family="Inter", size=12, weight="bold"),
                      fg_color="#0066cc", # Changed to blue
                      hover_color="#004499", # Changed to blue
                      corner_radius=8,
                      border_width=1,
                      border_color=self.BORDER_COLOR).pack(side=ctk.RIGHT, padx=5)

        # --- Filter, Sort, Search Bar ---
        control_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        control_frame.pack(fill=ctk.X, padx=15, pady=(0, 8))

        ctk.CTkLabel(control_frame, text="Filter by:", font=ctk.CTkFont(family="Inter", size=11), text_color=self.TEXT_COLOR).pack(side=ctk.LEFT, padx=(0, 5))
        filters = ["All Files", "Images", "Text Files", "Python Files"]
        self.filter_option_menu = ctk.CTkOptionMenu(control_frame, values=filters,
                                                    command=self.set_filter,
                                                    font=ctk.CTkFont(family="Inter", size=11),
                                                    width=120, height=30,
                                                    fg_color="#333333",
                                                    button_color="#0066cc", # Brighter blue for dropdown arrow
                                                    button_hover_color="#004499",
                                                    dropdown_fg_color="#333333",
                                                    dropdown_hover_color="#4da6ff",
                                                    corner_radius=8)
        self.filter_option_menu.set(self.filter_mode)
        self.filter_option_menu.pack(side=ctk.LEFT, padx=10)

        ctk.CTkLabel(control_frame, text="Sort by:", font=ctk.CTkFont(family="Inter", size=11), text_color=self.TEXT_COLOR).pack(side=ctk.LEFT, padx=(20, 5))
        sort_options = ["Name (A-Z)", "Name (Z-A)", "Size (Asc)", "Size (Desc)", "Date (Old-New)", "Date (New-Old)", "Type"]
        self.sort_option_menu = ctk.CTkOptionMenu(control_frame, values=sort_options,
                                                  command=self.set_sort,
                                                  font=ctk.CTkFont(family="Inter", size=11),
                                                  width=150, height=30,
                                                  fg_color="#333333",
                                                  button_color="#0066cc",
                                                  button_hover_color="#004499",
                                                  dropdown_fg_color="#333333",
                                                  dropdown_hover_color="#4da6ff",
                                                  corner_radius=8)
        self.sort_option_menu.set(self.sort_mode)
        self.sort_option_menu.pack(side=ctk.LEFT, padx=10)

        self.search_entry = ctk.CTkEntry(control_frame, placeholder_text="🔍 Search...",
                                         width=300, height=30,
                                         font=ctk.CTkFont(family="Inter", size=11),
                                         fg_color="#202020",
                                         border_color=self.BORDER_COLOR,
                                         corner_radius=8)
        self.search_entry.pack(side=ctk.RIGHT, padx=5)
        self.search_entry.bind('<Return>', self.perform_search)
        ctk.CTkButton(control_frame, text="Search", command=self.perform_search,
                      width=80, height=30,
                      font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                      fg_color="#0066cc", # Accent color button
                      hover_color="#004499",
                      corner_radius=8).pack(side=ctk.RIGHT)

        # --- Main Frame: File list and Preview ---
        main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        main_frame.pack(fill=ctk.BOTH, expand=True, padx=15, pady=(0, 15))

        # File list with scrollbar
        self.file_list_frame = ctk.CTkFrame(main_frame, fg_color=self.PRIMARY_BG, corner_radius=10, border_width=1, border_color=self.BORDER_COLOR)
        self.file_list_frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True, padx=(0, 15))

        self.file_list = tk.Listbox(self.file_list_frame, width=50,
                                    bg=self.PRIMARY_BG, fg=self.TEXT_COLOR,
                                    font=("Inter", 11),
                                    selectbackground="#4da6ff", selectforeground="#ffffff",
                                    highlightbackground=self.BORDER_COLOR, highlightcolor=self.ACCENT_COLOR,
                                    borderwidth=0, relief="flat", activestyle="none")

        self.file_list_scrollbar = ctk.CTkScrollbar(self.file_list_frame, command=self.file_list.yview,
                                                    button_color=self.BORDER_COLOR,
                                                    button_hover_color="#4da6ff",
                                                    corner_radius=8)
        self.file_list_scrollbar.pack(side=ctk.RIGHT, fill=ctk.Y)
        self.file_list.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True, padx=5, pady=5)

        self.file_list.bind('<<ListboxSelect>>', self.on_select)
        self.file_list.bind('<Double-1>', self.on_double_click)
        self.file_list.bind('<Button-3>', self.show_context_menu)

        # Preview frame
        preview_panel = ctk.CTkFrame(main_frame, fg_color=self.SECONDARY_BG, corner_radius=10, border_width=1, border_color=self.BORDER_COLOR)
        preview_panel.pack(fill=ctk.BOTH, expand=True, side=ctk.LEFT)

        # Frame for file details
        details_frame = ctk.CTkFrame(preview_panel, fg_color="transparent")
        details_frame.pack(fill=ctk.X, padx=15, pady=(15, 5), anchor="nw")

        self.meta_label = ctk.CTkLabel(details_frame, text="No item selected.",
                                       font=ctk.CTkFont(family="Inter", size=11, weight="bold"),
                                       text_color=self.WARN_COLOR, # Use warning color for meta info
                                       wraplength=preview_panel.winfo_width() - 30)
        self.meta_label.pack(anchor='nw')

        # Frame for actual preview content (text or image)
        preview_content_frame = ctk.CTkFrame(preview_panel, fg_color="transparent")
        preview_content_frame.pack(fill=ctk.BOTH, expand=True, padx=15, pady=(5, 10))
        
        self.preview_text = ctk.CTkTextbox(preview_content_frame,
                                          font=ctk.CTkFont(family="monospace", size=11),
                                          wrap="word",
                                          state="disabled",
                                          fg_color="#202020", # Slightly darker for text content
                                          text_color=self.TEXT_COLOR,
                                          scrollbar_button_color=self.BORDER_COLOR,
                                          scrollbar_button_hover_color="#4da6ff",
                                          corner_radius=8,
                                          border_width=1,
                                          border_color=self.BORDER_COLOR)
        self.preview_text.pack(fill=ctk.BOTH, expand=True)

        # Action Buttons below preview
        btn_frame = ctk.CTkFrame(preview_panel, fg_color="transparent")
        btn_frame.pack(fill=ctk.X, padx=15, pady=(0, 15))

        # Re-styling buttons for consistency and better look
        button_font = ctk.CTkFont(family="Inter", size=11, weight="bold")
        button_height = 30
        button_corner_radius = 8
        button_fg_color = "#0066cc" # Accent for primary actions
        button_hover_color = "#004499"

        ctk.CTkButton(btn_frame, text="▶ Open", command=self.open_selected,
                      width=90, height=button_height, font=button_font,
                      fg_color=button_fg_color, hover_color=button_hover_color, corner_radius=button_corner_radius).pack(side=ctk.LEFT, padx=5)
        ctk.CTkButton(btn_frame, text="🗑️ Delete", command=self.delete_selected,
                      width=90, height=button_height, font=button_font,
                      fg_color=self.ERROR_COLOR, hover_color="#990000", corner_radius=button_corner_radius).pack(side=ctk.LEFT, padx=5)
        ctk.CTkButton(btn_frame, text="✏️ Rename", command=self.rename_selected,
                      width=90, height=button_height, font=button_font,
                      fg_color=button_fg_color, hover_color=button_hover_color, corner_radius=button_corner_radius).pack(side=ctk.LEFT, padx=5)
        
        # New buttons for copy/cut/paste
        ctk.CTkButton(btn_frame, text="📋 Copy", command=self.copy_selected,
                      width=90, height=button_height, font=button_font,
                      fg_color=button_fg_color, hover_color=button_hover_color, corner_radius=button_corner_radius).pack(side=ctk.LEFT, padx=5)
        ctk.CTkButton(btn_frame, text="✂️ Cut", command=self.cut_selected,
                      width=90, height=button_height, font=button_font,
                      fg_color=button_fg_color, hover_color=button_hover_color, corner_radius=button_corner_radius).pack(side=ctk.LEFT, padx=5)
        self.paste_button = ctk.CTkButton(btn_frame, text="📄 Paste", command=self.paste_item,
                                          state="disabled", # Initially disabled
                                          width=90, height=button_height, font=button_font,
                                          fg_color=button_fg_color, hover_color=button_hover_color, corner_radius=button_corner_radius)
        self.paste_button.pack(side=ctk.LEFT, padx=5)

        ctk.CTkButton(btn_frame, text="📄 New File", command=self.create_new_file,
                      width=100, height=button_height, font=button_font,
                      fg_color=button_fg_color, hover_color=button_hover_color, corner_radius=button_corner_radius).pack(side=ctk.LEFT, padx=5)
        ctk.CTkButton(btn_frame, text="📁 New Folder", command=self.create_new_folder,
                      width=110, height=button_height, font=button_font,
                      fg_color=button_fg_color, hover_color=button_hover_color, corner_radius=button_corner_radius).pack(side=ctk.LEFT, padx=5)
        ctk.CTkButton(btn_frame, text="📋 Copy Path", command=self.copy_path_to_clipboard,
                      width=110, height=button_height, font=button_font,
                      fg_color=button_fg_color, hover_color=button_hover_color, corner_radius=button_corner_radius).pack(side=ctk.LEFT, padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Refresh", command=self.populate_file_list,
                      width=90, height=button_height, font=button_font,
                      fg_color=button_fg_color, hover_color=button_hover_color, corner_radius=button_corner_radius).pack(side=ctk.RIGHT, padx=5)

        # --- Status Bar ---
        self.status_bar = ctk.CTkLabel(self.root, text=f"Ready. Version {VERSION} | {STATUS}",
                                       fg_color="#1a1a1a", # Darker for status bar
                                       text_color=self.TEXT_COLOR,
                                       font=ctk.CTkFont(size=10),
                                       anchor="w",
                                       corner_radius=0,
                                       padx=10) # Added horizontal padding
        self.status_bar.pack(side=ctk.BOTTOM, fill=ctk.X)
        self.update_go_back_button_state() # Call here to set initial state
        self._update_paste_button_state() # Update paste button state on startup

    def update_status(self, message):
        """Updates the text in the status bar."""
        self.status_bar.configure(text=message)
        self.root.update_idletasks()

    def update_path_history(self, new_path):
        """Updates the navigation history and current index."""
        if self.history_index < len(self.path_history) - 1:
            self.path_history = self.path_history[:self.history_index + 1]

        self.path_history.append(new_path)
        self.history_index = len(self.path_history) - 1
        self.update_go_back_button_state()

    def set_filter(self, mode):
        """Sets the file display filter and refreshes the file list."""
        self.filter_mode = mode
        self.populate_file_list()
        self.update_status(f"Filter set to: {self.filter_mode}")
        self.show_custom_notification(f"Filter set to: {self.filter_mode}")

    def set_sort(self, mode):
        """Sets the file display sort mode and refreshes the file list."""
        self.sort_mode = mode
        self.populate_file_list()
        self.update_status(f"Sorted by: {self.sort_mode}")
        self.show_custom_notification(f"Sorted by: {self.sort_mode}")

    def get_file_info(self, path):
        """Retrieves detailed file/folder information, handling errors."""
        info = {
            "name": os.path.basename(path),
            "full_path": path,
            "type": "Folder" if os.path.isdir(path) else "File",
            "size": "N/A",
            "extension": "N/A",
            "created": "N/A",
            "modified": "N/A",
            "accessed": "N/A",
            "permissions": "N/A",
            "owner_uid": "N/A",
            "group_gid": "N/A",
            "device_id": "N/A",
            "inode": "N/A",
            "n_links": "N/A",
            "block_size": "N/A",  # Initialize as N/A
            "n_blocks": "N/A",  # Initialize as N/A
        }
        try:
            stats = os.stat(path)
            size_bytes = stats.st_size
            if size_bytes >= (1024 ** 3):
                info["size"] = f"{size_bytes / (1024 ** 3):.2f} GB"
            elif size_bytes >= (1024 ** 2):
                info["size"] = f"{size_bytes / (1024 ** 2):.2f} MB"
            elif size_bytes >= 1024:
                info["size"] = f"{size_bytes / 1024:.2f} KB"
            else:
                info["size"] = f"{size_bytes} Bytes"

            info["created"] = datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
            info["modified"] = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            info["accessed"] = datetime.fromtimestamp(stats.st_atime).strftime('%Y-%m-%d %H:%M:%S')

            mode = stats.st_mode
            info["permissions"] = oct(mode)[-3:]

            # Additional "insane" details
            info["extension"] = os.path.splitext(info['name'])[1] if os.path.isfile(path) else "N/A"
            info["owner_uid"] = stats.st_uid
            info["group_gid"] = stats.st_gid
            info["device_id"] = stats.st_dev
            info["inode"] = stats.st_ino
            info["n_links"] = stats.st_nlink

            # --- MODIFIED PART FOR st_blksize and st_blocks ---
            if hasattr(stats, 'st_blksize'):
                info["block_size"] = stats.st_blksize
            else:
                info["block_size"] = "Not available"  # Or keep "N/A"

            if hasattr(stats, 'st_blocks'):
                info["n_blocks"] = stats.st_blocks
            else:
                info["n_blocks"] = "Not available"  # Or keep "N/A"
            # --- END MODIFIED PART ---

        except (FileNotFoundError, PermissionError) as e:
            info["error"] = f"Access Error: {e}"
        except Exception as e:
            info["error"] = f"Info Error: {e}"
        return info

    def populate_file_list(self):
        """Populates the Listbox with files and folders based on current path, filter, and sort mode."""
        self.update_status("Loading directory...")
        self.file_list.delete(0, ctk.END)
        self.clear_preview()
        self.selected_item_path = None

        try:
            raw_entries = os.listdir(self.current_path)
            all_entries_info = []

            for entry in raw_entries:
                full_path = os.path.join(self.current_path, entry)
                entry_info = self.get_file_info(full_path)
                entry_info["original_name"] = entry
                all_entries_info.append(entry_info)

            # Filter entries
            filtered_entries_info = []
            for entry_info in all_entries_info:
                is_dir = entry_info["type"] == "Folder"
                ext = os.path.splitext(entry_info["name"])[1].lower() if not is_dir else ""

                if is_dir:
                    filtered_entries_info.append(entry_info)
                    continue

                if self.filter_mode == "All Files":
                    filtered_entries_info.append(entry_info)
                elif self.filter_mode == "Images" and ext in ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff'):
                    filtered_entries_info.append(entry_info)
                elif self.filter_mode == "Text Files" and ext in ('.txt', '.md', '.log', '.csv', '.json', '.xml', '.html', '.css', '.js'):
                    filtered_entries_info.append(entry_info)
                elif self.filter_mode == "Python Files" and ext == '.py':
                    filtered_entries_info.append(entry_info)
            
            # Sort entries
            def sort_key(item_info):
                is_dir = item_info["type"] == "Folder"
                if self.sort_mode == "Name (A-Z)":
                    return (not is_dir, item_info["original_name"].lower())
                elif self.sort_mode == "Name (Z-A)":
                    return (not is_dir, item_info["original_name"].lower())
                elif self.sort_mode == "Size (Asc)":
                    # Handle "N/A" for size comparison by treating it as 0 or a very small number
                    size_val = float(item_info["size"].split()[0]) if item_info["size"] != "N/A" else -1
                    return (not is_dir, size_val)
                elif self.sort_mode == "Size (Desc)":
                    size_val = float(item_info["size"].split()[0]) if item_info["size"] != "N/A" else -1
                    return (not is_dir, size_val)
                elif self.sort_mode == "Date (Old-New)":
                    return (not is_dir, datetime.strptime(item_info["modified"], '%Y-%m-%d %H:%M:%S') if item_info["modified"] != "N/A" else datetime.min)
                elif self.sort_mode == "Date (New-Old)":
                    return (not is_dir, datetime.strptime(item_info["modified"], '%Y-%m-%d %H:%M:%S') if item_info["modified"] != "N/A" else datetime.min)
                elif self.sort_mode == "Type":
                    return (not is_dir, item_info["original_name"].lower())
                return (not is_dir, item_info["original_name"].lower())

            reverse_sort = self.sort_mode in ["Name (Z-A)", "Size (Desc)", "Date (New-Old)"]
            filtered_entries_info.sort(key=sort_key, reverse=reverse_sort)

            for entry_info in filtered_entries_info:
                icon = "📁 " if entry_info["type"] == "Folder" else "📄 "
                display_name = icon + entry_info["original_name"] + ("/" if entry_info["type"] == "Folder" else "")
                self.file_list.insert(ctk.END, display_name)
            
            self.update_status(f"Displayed {len(filtered_entries_info)} items. Sorted by {self.sort_mode}.")

        except PermissionError:
            self.show_custom_notification("Permission denied to access this directory.", is_error=True)
            self.update_status("Error: Permission Denied for current directory.")
        except FileNotFoundError:
            self.show_custom_notification(f"Directory not found: {self.current_path}. Navigating to home.", is_error=True)
            self.current_path = os.path.expanduser("~")
            self.path_history = [self.current_path]
            self.history_index = 0
            self.update_path_history(self.current_path)
            self.populate_file_list()
        except Exception as e:
            self.show_custom_notification(f"Could not list directory contents: {e}", is_error=True)
            self.update_status("Error listing directory contents.")

    def clear_preview(self):
        """Clears the metadata label and preview text area."""
        self.meta_label.configure(text="No item selected.")
        self.preview_text.configure(state="normal")
        self.preview_text.delete("1.0", ctk.END)
        self.preview_text.configure(state="disabled")
        self.tk_img = None

    def on_select(self, event):
        """Event handler for single click item selection. Displays info/preview."""
        selection_indices = self.file_list.curselection()
        if not selection_indices:
            self.clear_preview()
            self.selected_item_path = None
            return

        self.update_status("Loading preview...") # Show loading status for preview
        self.root.update_idletasks() # Ensure status bar updates immediately

        selected_item_display_name_with_icon = self.file_list.get(selection_indices[0])
        selected_item_name = selected_item_display_name_with_icon[2:].rstrip("/")
        self.selected_item_path = os.path.join(self.current_path, selected_item_name)

        if os.path.exists(self.selected_item_path):
            self.display_item_info(self.selected_item_path)
        else:
            self.clear_preview()
            self.meta_label.configure(text=f"Item not found: {selected_item_name}", text_color=self.ERROR_COLOR)
            self.selected_item_path = None
            self.update_status("Error: Selected item not found.")
            self.show_custom_notification(f"Item not found: {selected_item_name}", is_error=True)


    def on_double_click(self, event):
        """Event handler for double click. Navigates into folders or opens files."""
        selection_indices = self.file_list.curselection()
        if not selection_indices:
            return

        selected_item_display_name_with_icon = self.file_list.get(selection_indices[0])
        selected_item_name = selected_item_display_name_with_icon[2:].rstrip("/")
        path = os.path.join(self.current_path, selected_item_name)

        if os.path.isdir(path):
            self.current_path = path
            self.path_label.configure(text=f"Current Directory: {self.current_path}")
            self.update_path_history(self.current_path)
            self.populate_file_list()
            self.update_status(f"Navigated into: {selected_item_name}")
            self.show_custom_notification(f"Opened folder: {selected_item_name}")
        else:
            self.open_file_with_system_app(path)

    def display_item_info(self, item_path):
        """Displays comprehensive item metadata and preview content."""
        self.clear_preview()
        item_info = self.get_file_info(item_path)

        if "error" in item_info:
            self.meta_label.configure(text=f"Error: {item_info['error']}", text_color=self.ERROR_COLOR)
            self.update_status("Error displaying item info.")
            return

        meta_text = (
            f"Name: {item_info['name']}\n"
            f"Full Path: {item_info['full_path']}\n" # Added Full Path
            f"Type: {item_info['type']}\n"
            f"Extension: {item_info['extension']}\n" # Added Extension
            f"Size: {item_info['size']}\n"
            f"Created: {item_info['created']}\n"
            f"Modified: {item_info['modified']}\n"
            f"Accessed: {item_info['accessed']}\n"
            f"Permissions: {item_info['permissions']}\n"
            f"Owner UID: {item_info['owner_uid']}\n" # Added Owner UID
            f"Group GID: {item_info['group_gid']}\n" # Added Group GID
            f"Device ID: {item_info['device_id']}\n" # Added Device ID
            f"Inode: {item_info['inode']}\n" # Added Inode
            f"Links: {item_info['n_links']}\n" # Added Number of Links
            f"Block Size: {item_info['block_size']} bytes\n" # Added Block Size
            f"Blocks: {item_info['n_blocks']}" # Added Number of Blocks
        )
        self.meta_label.configure(text=meta_text, text_color=self.WARN_COLOR if item_info["type"] == "File" else self.ACCENT_COLOR)

        self.preview_text.configure(state="normal")
        self.preview_text.delete("1.0", ctk.END)

        if item_info["type"] == "Folder":
            try:
                contents_list = os.listdir(item_path)
                display_contents = "\n".join([f"  {f}" for f in contents_list[:50]])
                if len(contents_list) > 50:
                    display_contents += "\n\n... (showing first 50 items, folder contains more)"
                self.preview_text.insert(ctk.END, f"Folder Contents ({len(contents_list)} items total):\n\n{display_contents}")
            except Exception as e:
                self.preview_text.insert(ctk.END, f"[Error listing folder contents: {e}]")
            self.update_status(f"Viewing folder: {item_info['name']}")

        else: # It's a file
            ext = os.path.splitext(item_info['name'])[1].lower()
            if ext in ['.txt', '.md', '.py', '.log', '.csv', '.json', '.xml', '.html', '.css', '.js', '.c', '.cpp', '.java', '.go', '.sh']:
                try:
                    with open(item_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(10000)
                        if len(content) == 10000:
                            content += "\n\n... (preview truncated)"
                    self.preview_text.insert(ctk.END, content)
                except Exception as text_e:
                    self.preview_text.insert(ctk.END, f"[Could not read text file for preview: {text_e}]")
                self.update_status(f"Viewing text file: {item_info['name']}")

            elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp']:
                try:
                    img = Image.open(item_path)
                    
                    self.preview_text.update_idletasks()
                    max_width = self.preview_text.winfo_width() - 20
                    max_height = self.preview_text.winfo_height() - 20

                    if max_width <= 0 or max_height <= 0:
                        max_width = 500
                        max_height = 400

                    img.thumbnail((max_width, max_height), Image.LANCZOS)
                    self.tk_img = ImageTk.PhotoImage(img)
                    self.preview_text.image_create("1.0", image=self.tk_img, padx=5, pady=5)
                    self.preview_text.insert(ctk.END, "\n\n[Image Preview Above]")
                except Exception as img_e:
                    self.preview_text.insert(ctk.END, f"[Could not display image preview: {img_e}]")
                self.update_status(f"Viewing image file: {item_info['name']}")

            elif ext in ['.mp3', '.wav', '.ogg', '.flac', '.m4a', '.mp4', '.avi', '.mkv', '.mov', '.webm']:
                self.preview_text.insert(ctk.END, f"🎵 [Media File: {item_info['name']}]\n\n"
                                                  f"This is an audio/video file. Click the 'Open' button (▶) to play it in your system's default media player for best performance.")
                self.update_status(f"Viewing media file: {item_info['name']}")
            else:
                self.preview_text.insert(ctk.END, f"❓ [No direct preview available for '{ext}' files]\n\n"
                                                  f"Click the 'Open' button (▶) to try opening this file with your system's default application.")
                self.update_status(f"Viewing unknown file type: {item_info['name']}")
        
        self.preview_text.configure(state="disabled")

    def get_selected_item_path(self):
        """Helper to get the full path of the currently selected item."""
        if not self.selected_item_path:
            self.show_custom_notification("Please select an item first.", is_error=True)
            return None
        return self.selected_item_path

    def open_file_with_system_app(self, path):
        """Opens a given path (file or folder) with the system's default application."""
        if os.path.exists(path):
            try:
                if os.name == "nt": # Windows
                    os.startfile(path)
                else: # macOS / Linux
                    import subprocess
                    if sys.platform == "darwin": # macOS
                        subprocess.call(("open", path))
                    else: # Linux/Unix
                        subprocess.call(("xdg-open", path))
                self.update_status(f"Opened: {os.path.basename(path)}")
                self.show_custom_notification(f"Opened: {os.path.basename(path)}")
            except Exception as e:
                self.show_custom_notification(f"Could not open '{os.path.basename(path)}': {e}", is_error=True)
                self.update_status(f"Error opening: {os.path.basename(path)}")
        else:
            self.show_custom_notification("File or folder does not exist.", is_error=True)
            self.update_status("Error: Item not found.")

    def open_selected(self):
        """Opens the selected file/folder (navigates if folder, opens with app if file)."""
        path = self.get_selected_item_path()
        if not path: return

        if os.path.isdir(path):
            self.current_path = path
            self.path_label.configure(text=f"Current Directory: {self.current_path}")
            self.update_path_history(self.current_path)
            self.populate_file_list()
            self.update_status(f"Navigated into folder: {os.path.basename(path)}")
            self.show_custom_notification(f"Opened folder: {os.path.basename(path)}")
        else:
            self.open_file_with_system_app(path)

    def delete_selected(self):
        """Deletes the selected file or folder after confirmation."""
        path = self.get_selected_item_path()
        if not path: return

        selected_name_display = os.path.basename(path) + ("/" if os.path.isdir(path) else "")

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{selected_name_display}'?\nThis action is irreversible!")
        if confirm:
            try:
                if os.path.isfile(path):
                    os.remove(path)
                    self.show_custom_notification(f"File '{selected_name_display}' deleted successfully.")
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                
                    self.show_custom_notification(f"Folder '{selected_name_display}' deleted successfully.")
                self.populate_file_list()
                self.update_status(f"Deleted: {selected_name_display}")
                # Clear clipboard if the deleted item was what was copied/cut
                if self.clipboard_item == path:
                    self.clipboard_item = None
                    self.clipboard_mode = None
                    self._update_paste_button_state()

            except Exception as e:
                self.show_custom_notification(f"Could not delete '{selected_name_display}': {e}", is_error=True)
                self.update_status(f"Error deleting: {selected_name_display}")
        else:
            self.update_status(f"Deletion of {selected_name_display} cancelled.")
            self.show_custom_notification("Deletion cancelled.", is_error=True)

    def rename_selected(self):
        """Renames the selected file or folder."""
        old_path = self.get_selected_item_path()
        if not old_path: return

        old_name_display = os.path.basename(old_path) + ("/" if os.path.isdir(old_path) else "")

        if not os.path.exists(old_path):
            self.show_custom_notification("Selected item does not exist.", is_error=True)
            self.populate_file_list()
            return

        new_name = simpledialog.askstring("Rename", f"Enter new name for '{old_name_display}':", parent=self.root)
        if new_name and new_name.strip() and new_name.strip() != old_name_display.rstrip("/"):
            new_path = os.path.join(self.current_path, new_name.strip())
            try:
                os.rename(old_path, new_path)
                self.show_custom_notification(f"'{old_name_display}' renamed to '{new_name.strip()}'.")
                self.populate_file_list()
                self.update_status(f"Renamed: {old_name_display} to {new_name.strip()}")
                # Update clipboard item if it was the renamed item
                if self.clipboard_item == old_path:
                    self.clipboard_item = new_path
            except FileExistsError:
                self.show_custom_notification(f"An item named '{new_name.strip()}' already exists.", is_error=True)
                self.update_status("Error: Name already exists.")
            except Exception as e:
                self.show_custom_notification(f"Could not rename: {e}", is_error=True)
                self.update_status(f"Error renaming: {old_name_display}")
        elif new_name and new_name.strip() == old_name_display.rstrip("/"):
            self.update_status("Rename cancelled: New name is the same as old name.")
            self.show_custom_notification("Rename cancelled: Same name.", is_error=True)
        else:
            self.update_status("Rename cancelled.")
            self.show_custom_notification("Rename cancelled.", is_error=True)

    def create_new_file(self):
        """Creates a new empty file in the current directory."""
        file_name = simpledialog.askstring("Create New File", "Enter new file name:", parent=self.root)
        if file_name and file_name.strip():
            file_path = os.path.join(self.current_path, file_name.strip())
            if os.path.exists(file_path):
                self.show_custom_notification(f"File '{file_name.strip()}' already exists.", is_error=True)
                self.update_status("Error: File already exists.")
                return
            try:
                with open(file_path, 'w') as f:
                    f.write("")
                self.show_custom_notification(f"File '{file_name.strip()}' created successfully.")
                self.populate_file_list()
                self.update_status(f"Created new file: {file_name.strip()}")
            except Exception as e:
                self.show_custom_notification(f"Could not create file: {e}", is_error=True)
                self.update_status("Error creating new file.")
        else:
            self.update_status("File creation cancelled.")
            self.show_custom_notification("File creation cancelled.", is_error=True)

    def create_new_folder(self):
        """Creates a new folder in the current directory."""
        folder_name = simpledialog.askstring("Create New Folder", "Enter new folder name:", parent=self.root)
        if folder_name and folder_name.strip():
            folder_path = os.path.join(self.current_path, folder_name.strip())
            if os.path.exists(folder_path):
                self.show_custom_notification(f"Folder '{folder_name.strip()}' already exists.", is_error=True)
                self.update_status("Error: Folder already exists.")
                return
            try:
                os.makedirs(folder_path)
                self.show_custom_notification(f"Folder '{folder_name.strip()}' created successfully.")
                self.populate_file_list()
                self.update_status(f"Created new folder: {folder_name.strip()}")
            except Exception as e:
                self.show_custom_notification(f"Could not create folder: {e}", is_error=True)
                self.update_status("Error creating new folder.")
        else:
            self.update_status("Folder creation cancelled.")
            self.show_custom_notification("Folder creation cancelled.", is_error=True)

    def perform_search(self, event=None):
        """Performs a search for files/folders by name within the current directory and its subdirectories."""
        search_query = self.search_entry.get().strip()
        if not search_query:
            self.populate_file_list()
            self.update_status("Search cleared. Displaying all items.")
            self.show_custom_notification("Search cleared. Displaying all items.")
            return

        self.file_list.delete(0, ctk.END)
        self.clear_preview()
        self.selected_item_path = None
        found_items = []
        self.update_status(f"Searching for '{search_query}'...")
        self.root.update_idletasks()

        try:
            for root, dirs, files in os.walk(self.current_path):
                matching_dirs = [d for d in dirs if search_query.lower() in d.lower()]
                matching_files = [f for f in files if search_query.lower() in f.lower()]

                for d_name in matching_dirs:
                    full_path = os.path.join(root, d_name)
                    display_name = os.path.relpath(full_path, self.current_path) + "/"
                    found_items.append({"name": display_name, "path": full_path, "type": "Folder"})
                for f_name in matching_files:
                    full_path = os.path.join(root, f_name)
                    display_name = os.path.relpath(full_path, self.current_path)
                    found_items.append({"name": display_name, "path": full_path, "type": "File"})
            
            found_items.sort(key=lambda x: (x["type"] != "Folder", x["name"].lower()))

            if found_items:
                for item in found_items:
                    icon = "📁 " if item["type"] == "Folder" else "� "
                    self.file_list.insert(ctk.END, icon + item["name"])
                self.update_status(f"Found {len(found_items)} items for '{search_query}'.")
                self.show_custom_notification(f"Found {len(found_items)} items.")
            else:
                self.file_list.insert(ctk.END, "No items found matching your search.")
                self.update_status(f"No items found for '{search_query}'.")
                self.show_custom_notification(f"No items found for '{search_query}'.", is_error=True)

        except PermissionError:
            self.show_custom_notification("Cannot search some directories due to permissions.", is_error=True)
            self.update_status("Search completed with permission errors.")
        except Exception as e:
            self.show_custom_notification(f"An error occurred during search: {e}", is_error=True)
            self.update_status("Search completed with errors.")

    def copy_selected(self):
        """Copies the selected item to the clipboard."""
        path = self.get_selected_item_path()
        if not path: return

        self.clipboard_item = path
        self.clipboard_mode = 'copy'
        self._update_paste_button_state()
        self.update_status(f"Copied '{os.path.basename(path)}' to clipboard.")
        self.show_custom_notification(f"Copied '{os.path.basename(path)}'.")

    def cut_selected(self):
        """Cuts the selected item to the clipboard."""
        path = self.get_selected_item_path()
        if not path: return

        self.clipboard_item = path
        self.clipboard_mode = 'cut'
        self._update_paste_button_state()
        self.update_status(f"Cut '{os.path.basename(path)}' to clipboard.")
        self.show_custom_notification(f"Cut '{os.path.basename(path)}'.")


    def paste_item(self):
        """Pastes the item from the clipboard to the current directory."""
        if not self.clipboard_item or not self.clipboard_mode:
            self.show_custom_notification("Nothing to paste.", is_error=True)
            return

        source_path = self.clipboard_item
        base_name = os.path.basename(source_path)
        target_path = os.path.join(self.current_path, base_name)
        is_source_dir = os.path.isdir(source_path)

        if not os.path.exists(source_path):
            self.show_custom_notification(f"Source item '{base_name}' no longer exists.", is_error=True)
            self.clipboard_item = None
            self.clipboard_mode = None
            self._update_paste_button_state()
            self.populate_file_list()
            return

        # Handle name conflicts
        counter = 1
        original_target_path = target_path
        while os.path.exists(target_path):
            if self.clipboard_mode == 'copy':
                name_without_ext, ext = os.path.splitext(base_name)
                target_path = os.path.join(self.current_path, f"{name_without_ext} - Copy ({counter}){ext}")
            elif self.clipboard_mode == 'cut':
                 name_without_ext, ext = os.path.splitext(base_name)
                 target_path = os.path.join(self.current_path, f"{name_without_ext} - Moved ({counter}){ext}")
            counter += 1

        try:
            if self.clipboard_mode == 'copy':
                if is_source_dir:
                    shutil.copytree(source_path, target_path)
                else:
                    shutil.copy2(source_path, target_path)
                self.update_status(f"Copied '{base_name}' to '{os.path.basename(target_path)}'.")
                self.show_custom_notification(f"Pasted: '{os.path.basename(target_path)}'.")
            elif self.clipboard_mode == 'cut':
                shutil.move(source_path, target_path)
                self.update_status(f"Moved '{base_name}' to '{os.path.basename(target_path)}'.")
                self.show_custom_notification(f"Moved: '{os.path.basename(target_path)}'.")
                # Clear clipboard after successful move
                self.clipboard_item = None
                self.clipboard_mode = None
                self._update_paste_button_state()
            
            self.populate_file_list() # Refresh target directory
            # If item was cut, also refresh the source directory if it's different
            if self.clipboard_mode == 'cut' and os.path.dirname(source_path) != self.current_path:
                 # No direct way to refresh another directory's view, relies on user navigating or re-opening
                 pass

        except shutil.Error as e:
            self.show_custom_notification(f"Paste error: {e}", is_error=True)
            self.update_status("Error during paste operation.")
        except PermissionError:
            self.show_custom_notification("Permission denied for paste operation.", is_error=True)
            self.update_status("Error: Permission denied for paste.")
        except Exception as e:
            self.show_custom_notification(f"An unexpected error occurred during paste: {e}", is_error=True)
            self.update_status("Error during paste operation.")

    def _update_paste_button_state(self):
        """Updates the state of the paste button based on clipboard content."""
        if self.clipboard_item:
            self.paste_button.configure(state="normal")
        else:
            self.paste_button.configure(state="disabled")

    def show_context_menu(self, event):
        """Displays a right-click context menu for selected items."""
        try:
            # Ensure an item is selected for the context menu to be meaningful
            self.file_list.selection_clear(0, ctk.END)
            index = self.file_list.nearest(event.y)
            self.file_list.selection_set(index)
            self.file_list.activate(index)
            
            selected_item_display_name_with_icon = self.file_list.get(index)
            selected_item_name = selected_item_display_name_with_icon[2:].rstrip("/")
            self.selected_item_path = os.path.join(self.current_path, selected_item_name)

            # Use standard tkinter.Menu for compatibility
            context_menu = tk.Menu(self.root, tearoff=0) 
            context_menu.add_command(label="Open", command=self.open_selected)
            context_menu.add_command(label="Delete", command=self.delete_selected)
            context_menu.add_command(label="Rename", command=self.rename_selected)
            context_menu.add_separator()
            context_menu.add_command(label="Copy", command=self.copy_selected)
            context_menu.add_command(label="Cut", command=self.cut_selected)
            
            # Add paste option to context menu, enable/disable based on clipboard
            if self.clipboard_item:
                context_menu.add_command(label="Paste", command=self.paste_item)
            else:
                context_menu.add_command(label="Paste", state="disabled")

            context_menu.add_separator()
            context_menu.add_command(label="Copy Path to Clipboard", command=self.copy_path_to_clipboard)
            
            context_menu.tk_popup(event.x_root, event.y_root)
        except Exception as e: # Catch any exception and print it for debugging
            self.update_status(f"Error showing context menu: {e}")
            self.show_custom_notification(f"Error showing context menu: {e}", is_error=True)
            print(f"DEBUG: Context menu error: {e}") # Print to console for detailed traceback

    def copy_path_to_clipboard(self):
        """Copies the full path of the selected item to the clipboard."""
        path = self.get_selected_item_path()
        if not path: return

        self.root.clipboard_clear()
        self.root.clipboard_append(path)
        self.update_status(f"Copied path to clipboard: {path}")
        self.show_custom_notification("Path copied to clipboard!")

    def show_custom_notification(self, message, is_error=False, duration_ms=3000):
        """Displays a custom pop-up notification with a slide-in and slide-out animation."""
        
        # Step 1: Clean up any notifications that have been manually closed or finished their cycle
        # Also remove any notifications that are already sliding out or dismissed to prevent re-triggering.
        self.active_notifications = [
            (win, current_y, slide_out_job_id) for win, current_y, slide_out_job_id in self.active_notifications
            if win.winfo_exists() and win.wm_attributes("-alpha") > 0 # Keep only visible/active ones
        ]

        # Step 2: If we are at max notifications, remove the oldest (bottom-most)
        # This ensures new notifications always have space at the top.
        if len(self.active_notifications) >= MAX_DISPLAYED_NOTIFICATIONS:
            oldest_win, _, oldest_job_id = self.active_notifications.pop(-1) # Pop the last (oldest/lowest) one
            if oldest_job_id:
                self.root.after_cancel(oldest_job_id) # Cancel its scheduled slide-out
            # Initiate immediate slide-out for the oldest notification
            self._animate_slide(oldest_win, oldest_win.winfo_x(), self.root.winfo_x() + self.root.winfo_width() + NOTIFICATION_WIDTH + 10,
                                oldest_win.winfo_y(), oldest_win.winfo_y(), # Y doesn't change during horizontal slide-out
                                direction="out", step_count=10) # Quick slide out

        # Step 3: Shift all existing notifications downwards
        # Iterate from the newest (top-most) to the oldest (bottom-most)
        for i in range(len(self.active_notifications)):
            win, current_y, slide_out_job_id = self.active_notifications[i]
            # Calculate new target Y for the notification to move down
            # It should move to the position of the notification below it (which is 0 + (i+1) * slot_height)
            new_target_y = self.root.winfo_y() + NOTIFICATION_GAP + (i + 1) * NOTIFICATION_SLOT_HEIGHT
            
            # Animate existing notifications downwards
            self._animate_slide(win, win.winfo_x(), win.winfo_x(), # X doesn't change for vertical slide
                                current_y, new_target_y,
                                direction="down", step_count=15)
            
            # Update the stored y-position for the notification
            self.active_notifications[i] = (win, new_target_y, slide_out_job_id)

        # Step 4: Create the new notification window at the top
        new_notification_window = ctk.CTkToplevel(self.root)
        new_notification_window.wm_overrideredirect(True)
        new_notification_window.wm_attributes("-topmost", True)
        new_notification_window.wm_attributes("-alpha", 0) # Start fully transparent

        margin_x = 20
        margin_y = 20

        # Initial position (off-screen to the right, at the very top of the stack)
        initial_x_start = self.root.winfo_x() + self.root.winfo_width() + 10
        target_x_in = self.root.winfo_x() + self.root.winfo_width() - NOTIFICATION_WIDTH - margin_x
        target_y_in = self.root.winfo_y() + margin_y # Always at the top for new ones

        new_notification_window.geometry(f"{NOTIFICATION_WIDTH}x{NOTIFICATION_HEIGHT}+{initial_x_start}+{target_y_in}")

        bg_color = "#33cc33" if not is_error else self.ERROR_COLOR # Use defined error color
        fg_color = self.TEXT_COLOR
        icon_char = "✅" if not is_error else "❌"

        notification_frame = ctk.CTkFrame(new_notification_window, fg_color=bg_color, corner_radius=10)
        notification_frame.pack(fill=ctk.BOTH, expand=True, padx=5, pady=5)

        notification_label = ctk.CTkLabel(notification_frame, text=f"{icon_char} {message}", text_color=fg_color,
                                          font=ctk.CTkFont(family="Inter", size=12, weight="bold"), wraplength=NOTIFICATION_WIDTH - 20)
        notification_label.pack(expand=True, pady=5)

        # Add the new notification to the active list (conceptually at the top)
        # Its y_pos is initially target_y_in, job_id is None until slide-in completes
        self.active_notifications.insert(0, (new_notification_window, target_y_in, None))


        # Start slide-in animation for the new notification
        # On completion, _schedule_slide_out will be called to set up its exit
        self._animate_slide(new_notification_window, initial_x_start, target_x_in,
                            target_y_in, target_y_in, # Y doesn't change during initial slide-in
                            direction="in", step_count=15,
                            on_complete=lambda: self._schedule_slide_out(new_notification_window, target_x_in, initial_x_start + NOTIFICATION_WIDTH + 10, target_y_in, duration_ms))

    def _animate_slide(self, window, start_x, end_x, start_y, end_y, direction, step=0, step_count=15, on_complete=None):
        """Helper to animate a window's position and alpha."""
        if not window.winfo_exists(): # Check if window still exists before animating
            return

        x_diff = end_x - start_x
        y_diff = end_y - start_y
        
        current_x = int(start_x + x_diff * (step / step_count))
        current_y = int(start_y + y_diff * (step / step_count))

        alpha = window.wm_attributes("-alpha") # Get current alpha
        if direction == "in":
            alpha = (step / step_count) if (step / step_count) <= 1 else 1
        elif direction == "out":
            alpha = (1 - (step / step_count)) if (1 - (step / step_count)) >= 0 else 0
        # For "down" movement, alpha stays constant (1) unless it's fading
        elif direction == "down":
            alpha = 1.0 # Ensure it stays fully visible while sliding down

        window.wm_attributes("-alpha", alpha)
        window.geometry(f"{NOTIFICATION_WIDTH}x{NOTIFICATION_HEIGHT}+{current_x}+{current_y}")


        if step < step_count:
            window.after(20, lambda: self._animate_slide(window, start_x, end_x, start_y, end_y, direction, step + 1, step_count, on_complete))
        else:
            # Animation complete
            if direction == "out":
                window.destroy()
                # Remove from active_notifications list
                self.active_notifications = [(w, y, j) for w, y, j in self.active_notifications if w != window]
            if on_complete:
                on_complete()


    def _schedule_slide_out(self, window, start_x, end_x_out, y_pos, duration_ms):
        """Schedules the slide-out animation for a notification after its display duration."""
        # Find the notification in active_notifications and update its job ID
        for i, (win, current_y, old_job_id) in enumerate(self.active_notifications):
            if win == window:
                # Cancel any old scheduled slide-out if it exists (e.g., if it was shifted)
                if old_job_id:
                    self.root.after_cancel(old_job_id)

                # Schedule the new slide-out
                # The 'after' job ID is returned and stored for potential cancellation later
                job_id = self.root.after(duration_ms, lambda: self._animate_slide(window, start_x, end_x_out, y_pos, y_pos, direction="out"))
                self.active_notifications[i] = (win, current_y, job_id)
                break


# --- Main Program Loop (Terminal Interface) ---
def main():
    """Main function to run the file manager, starting with terminal interface."""
    username = get_username()

    while True:
        print_banner(username)
        choice = input(f"{YELLOW}Select an option:{RESET} ").strip()

        if choice == "1":
            list_files_terminal()
        elif choice == "2":
            list_roots_terminal()
        elif choice == "3":
            list_folders_terminal()
        elif choice == "4":
            open_file_terminal()
        elif choice == "5":
            delete_file_terminal()
        elif choice == "6":
            find_file_terminal()
        elif choice == "9":
            print(f"{GREEN}Launching GUI... Close GUI window to return to terminal.{RESET}")
            run_gui()
        elif choice == "0":
            print(f"{MAGENTA}Goodbye!{RESET}")
            break
        else:
            print(f"{RED}Invalid option, try again.{RESET}")

        if choice != "9":
            input(f"{YELLOW}Press Enter to continue...{RESET}")

def run_gui():
    """Initializes and runs the CustomTkinter GUI application."""
    root = ctk.CTk()
    app = FileManagerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    try:
        from PIL import Image, ImageTk
    except ImportError:
        print(f"{RED}[!] Pillow library not found. Please install it for image preview in GUI: pip install Pillow{RESET}")
        print(f"{RED}Run: pip install Pillow{RESET}")
        sys.exit(1)

    try:
        import customtkinter as ctk
    except ImportError:
        print(f"{RED}[!] CustomTkinter library not found. Please install it for GUI: pip install customtkinter{RESET}")
        print(f"{RED}Run: pip install customtkinter{RESET}")
        sys.exit(1)

    main()
