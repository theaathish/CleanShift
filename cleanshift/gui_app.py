import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import sys
import platform
import webbrowser
import subprocess
import shutil
from pathlib import Path

# Try to import PIL for logo, fallback if not available
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# Import our modules (should be available after setup_imports)
from analyzer import DiskAnalyzer
from cleaner import SystemCleaner
from mover import PackageMover
from env_cleaner import EnvironmentCleaner
from utils import is_admin, format_size

class CleanShiftGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CleanShift - System Cleanup & Optimizer")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f8fafc")
        
        # Set window icon
        try:
            if getattr(sys, 'frozen', False):
                # Running as executable
                icon_path = os.path.join(sys._MEIPASS, 'assets', 'icon.ico')
            else:
                icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'icon.ico')
            
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass  # Ignore if icon not found
        
        # Modern color scheme (Tailwind-inspired)
        self.colors = {
            'primary': '#3b82f6',      # blue-500
            'primary_dark': '#2563eb', # blue-600
            'success': '#10b981',      # emerald-500
            'warning': '#f59e0b',      # amber-500
            'danger': '#ef4444',       # red-500
            'gray_50': '#f8fafc',
            'gray_100': '#f1f5f9',
            'gray_200': '#e2e8f0',
            'gray_300': '#cbd5e1',
            'gray_600': '#475569',
            'gray_700': '#334155',
            'gray_800': '#1e293b',
            'white': '#ffffff'
        }
        
        # Initialize components
        self.analyzer = DiskAnalyzer()
        self.cleaner = SystemCleaner()
        self.mover = PackageMover()
        self.env_cleaner = EnvironmentCleaner()
        
        # GUI state variables
        self.clean_vars = {}
        self.scan_path = tk.StringVar(value="C:\\")
        self.auto_clean = tk.BooleanVar()
        self.confirm_actions = tk.BooleanVar(value=True)
        
        self.setup_styles()
        self.create_widgets()
        self.check_admin_status()
        
    def setup_styles(self):
        """Setup modern styling for ttk widgets"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure button styles
        self.style.configure('Primary.TButton',
                           background=self.colors['primary'],
                           foreground='white',
                           borderwidth=0,
                           focuscolor='none',
                           padding=(20, 10))
        
        self.style.map('Primary.TButton',
                      background=[('active', self.colors['primary_dark'])])
        
        self.style.configure('Success.TButton',
                           background=self.colors['success'],
                           foreground='white',
                           borderwidth=0,
                           padding=(15, 8))
        
        self.style.configure('Warning.TButton',
                           background=self.colors['warning'],
                           foreground='white',
                           borderwidth=0,
                           padding=(15, 8))
        
        self.style.configure('Danger.TButton',
                           background=self.colors['danger'],
                           foreground='white',
                           borderwidth=0,
                           padding=(15, 8))
        
        # Configure frame styles
        self.style.configure('Card.TFrame',
                           background=self.colors['white'],
                           relief='solid',
                           borderwidth=1)
        
        # Configure treeview styles
        self.style.configure('Modern.Treeview',
                           background=self.colors['white'],
                           foreground=self.colors['gray_700'],
                           fieldbackground=self.colors['white'],
                           borderwidth=1,
                           relief='solid')
        
        self.style.configure('Modern.Treeview.Heading',
                           background=self.colors['gray_100'],
                           foreground=self.colors['gray_700'],
                           borderwidth=1,
                           relief='solid')
    
    def create_widgets(self):
        """Create the main GUI layout"""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['gray_50'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header with logo
        self.create_header(main_frame)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True, pady=(20, 0))
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_clean_tab()
        self.create_analyze_tab()
        self.create_move_tab()
        self.create_environments_tab()
        self.create_settings_tab()
        self.create_about_tab()
    
    def create_header(self, parent):
        """Create header with logo and title"""
        header_frame = tk.Frame(parent, bg=self.colors['white'], height=80)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Logo
        try:
            if PIL_AVAILABLE:
                if getattr(sys, 'frozen', False):
                    logo_path = os.path.join(sys._MEIPASS, 'assets', 'logo.png')
                else:
                    logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'logo.png')
                
                if os.path.exists(logo_path):
                    img = Image.open(logo_path)
                    img = img.resize((64, 64), Image.Resampling.LANCZOS)
                    self.logo = ImageTk.PhotoImage(img)
                    logo_label = tk.Label(header_frame, image=self.logo, bg=self.colors['white'])
                    logo_label.pack(side='left', padx=20, pady=8)
                else:
                    raise FileNotFoundError
            else:
                raise ImportError
        except (ImportError, FileNotFoundError, Exception):
            # Fallback logo
            logo_label = tk.Label(header_frame, text="🚀", font=('Arial', 32), bg=self.colors['white'])
            logo_label.pack(side='left', padx=20, pady=8)
        
        # Title and description
        title_frame = tk.Frame(header_frame, bg=self.colors['white'])
        title_frame.pack(side='left', fill='y', pady=8)
        
        title_label = tk.Label(title_frame, text="CleanShift", 
                              font=('Arial', 24, 'bold'), 
                              fg=self.colors['gray_800'], 
                              bg=self.colors['white'])
        title_label.pack(anchor='w')
        
        desc_label = tk.Label(title_frame, text="System Cleanup & Optimizer", 
                             font=('Arial', 12), 
                             fg=self.colors['gray_600'], 
                             bg=self.colors['white'])
        desc_label.pack(anchor='w')
        
        # Admin status
        self.admin_label = tk.Label(header_frame, text="", 
                                   font=('Arial', 10, 'bold'), 
                                   bg=self.colors['white'])
        self.admin_label.pack(side='right', padx=20, pady=8)
    
    def create_dashboard_tab(self):
        """Create dashboard overview tab"""
        tab_frame = tk.Frame(self.notebook, bg=self.colors['gray_50'])
        self.notebook.add(tab_frame, text="  📊 Dashboard  ")
        
        # Drive status cards
        drives_frame = tk.Frame(tab_frame, bg=self.colors['gray_50'])
        drives_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(drives_frame, text="Drive Status", 
                font=('Arial', 16, 'bold'), 
                fg=self.colors['gray_800'], 
                bg=self.colors['gray_50']).pack(anchor='w', pady=(0, 10))
        
        self.drives_container = tk.Frame(drives_frame, bg=self.colors['gray_50'])
        self.drives_container.pack(fill='x')
        
        # Quick actions
        actions_frame = tk.Frame(tab_frame, bg=self.colors['gray_50'])
        actions_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(actions_frame, text="Quick Actions", 
                font=('Arial', 16, 'bold'), 
                fg=self.colors['gray_800'], 
                bg=self.colors['gray_50']).pack(anchor='w', pady=(0, 10))
        
        quick_buttons = tk.Frame(actions_frame, bg=self.colors['gray_50'])
        quick_buttons.pack(fill='x')
        
        ttk.Button(quick_buttons, text="🧹 Quick Clean", 
                  style='Primary.TButton',
                  command=self.quick_clean).pack(side='left', padx=(0, 10))
        
        ttk.Button(quick_buttons, text="🔍 Analyze Disk", 
                  style='Success.TButton',
                  command=self.quick_analyze).pack(side='left', padx=(0, 10))
        
        ttk.Button(quick_buttons, text="🔄 Refresh Status", 
                  command=self.refresh_dashboard).pack(side='left')
        
        # System info
        info_frame = tk.Frame(tab_frame, bg=self.colors['gray_50'])
        info_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(info_frame, text="System Information", 
                font=('Arial', 16, 'bold'), 
                fg=self.colors['gray_800'], 
                bg=self.colors['gray_50']).pack(anchor='w', pady=(0, 10))
        
        self.system_info_label = tk.Label(info_frame, text="", 
                                         font=('Arial', 10), 
                                         fg=self.colors['gray_600'], 
                                         bg=self.colors['gray_50'],
                                         justify='left')
        self.system_info_label.pack(anchor='w')
        
        # Load initial data
        self.refresh_dashboard()
    
    def create_clean_tab(self):
        """Create cleaning options tab"""
        tab_frame = tk.Frame(self.notebook, bg=self.colors['gray_50'])
        self.notebook.add(tab_frame, text="  🧹 Clean  ")
        
        # Scrollable frame
        canvas = tk.Canvas(tab_frame, bg=self.colors['gray_50'])
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors['gray_50'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Clean options
        self.create_clean_section(scrollable_frame, "🗃️ System Files", [
            ("Temporary Files", "clean_temp", "Clean system and user temp files"),
            ("Browser Cache", "clean_browser", "Clear browser cache files"),
            ("System Cache", "clean_system", "Clear Windows system cache"),
            ("Recycle Bin", "clean_recycle", "Empty recycle bin"),
        ])
        
        self.create_clean_section(scrollable_frame, "⚡ Memory & Performance", [
            ("RAM Cache", "clean_ram", "Clear RAM cache and optimize memory"),
            ("DNS Cache", "clean_dns", "Flush DNS cache"),
            ("Registry Cleanup", "clean_registry", "Clean invalid registry entries"),
        ])
        
        # Clean all button
        clean_all_frame = tk.Frame(scrollable_frame, bg=self.colors['gray_50'])
        clean_all_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Button(clean_all_frame, text="🚀 Clean All Selected", 
                  style='Primary.TButton',
                  command=self.clean_all_selected).pack(side='left', padx=(0, 10))
        
        ttk.Button(clean_all_frame, text="👁️ Preview Changes", 
                  command=self.preview_clean).pack(side='left')
    
    def create_analyze_tab(self):
        """Create disk analysis tab"""
        tab_frame = tk.Frame(self.notebook, bg=self.colors['gray_50'])
        self.notebook.add(tab_frame, text="  🔍 Analyze  ")
        
        # Analysis options
        options_frame = tk.Frame(tab_frame, bg=self.colors['gray_50'])
        options_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(options_frame, text="Analyze Options", 
                font=('Arial', 16, 'bold'), 
                fg=self.colors['gray_800'], 
                bg=self.colors['gray_50']).pack(anchor='w', pady=(0, 10))
        
        # Min size slider
        min_size_frame = tk.Frame(options_frame, bg=self.colors['gray_50'])
        min_size_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(min_size_frame, text="Minimum Size (MB):", 
                 font=('Arial', 12), 
                 fg=self.colors['gray_700'], 
                 bg=self.colors['gray_50']).pack(side='left', anchor='w')
        
        self.min_size_var = tk.IntVar(value=100)
        min_size_slider = ttk.Scale(min_size_frame, from_=1, to=1000, 
                                    variable=self.min_size_var, 
                                    orient="horizontal",
                                    command=self.update_min_size_label)
        min_size_slider.pack(side='left', fill='x', expand=True)
        
        self.min_size_label = tk.Label(min_size_frame, text="100 MB", 
                                       font=('Arial', 12, 'bold'), 
                                       fg=self.colors['primary'], 
                                       bg=self.colors['gray_50'])
        self.min_size_label.pack(side='left', padx=(10, 0))
        
        # Analyze button
        analyze_button = ttk.Button(options_frame, text="📊 Analyze Disk", 
                                   style='Primary.TButton',
                                   command=self.analyze_disk)
        analyze_button.pack(fill='x', pady=(10, 0))
        
        # Results treeview
        results_frame = tk.Frame(tab_frame, bg=self.colors['gray_50'])
        results_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        tk.Label(results_frame, text="Analysis Results", 
                font=('Arial', 16, 'bold'), 
                fg=self.colors['gray_800'], 
                bg=self.colors['gray_50']).pack(anchor='w', pady=(0, 10))
        
        self.results_tree = ttk.Treeview(results_frame, 
                                         style="Modern.Treeview",
                                         columns=("Path", "Size", "Type"), 
                                         show="headings")
        self.results_tree.pack(fill='both', expand=True)
        
        # Define column headings
        for col in ["Path", "Size", "Type"]:
            self.results_tree.heading(col, text=col, 
                                    command=lambda c=col: self.sort_results(c))
            self.results_tree.column(col, anchor="w", width=250)
        
        # Bind double-click to open folder
        self.results_tree.bind("<Double-1>", self.open_folder)
    
    def create_move_tab(self):
        """Create tab for moving packages/folders"""
        tab_frame = tk.Frame(self.notebook, bg=self.colors['gray_50'])
        self.notebook.add(tab_frame, text="  📦 Move Apps  ")
        
        # Move options
        options_frame = tk.Frame(tab_frame, bg=self.colors['gray_50'])
        options_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(options_frame, text="Move Options", 
                font=('Arial', 16, 'bold'), 
                fg=self.colors['gray_800'], 
                bg=self.colors['gray_50']).pack(anchor='w', pady=(0, 10))
        
        # Source and target path entries
        path_frame = tk.Frame(options_frame, bg=self.colors['gray_50'])
        path_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(path_frame, text="Source Path:", 
                 font=('Arial', 12), 
                 fg=self.colors['gray_700'], 
                 bg=self.colors['gray_50']).pack(side='left', anchor='w')
        
        self.source_path_var = tk.StringVar()
        source_entry = ttk.Entry(path_frame, textvariable=self.source_path_var, 
                                font=('Arial', 12))
        source_entry.pack(side='left', fill='x', expand=True)
        
        ttk.Button(path_frame, text="Browse", 
                  command=self.browse_source_folder).pack(side='right')
        
        tk.Label(path_frame, text="Target Drive:", 
                 font=('Arial', 12), 
                 fg=self.colors['gray_700'], 
                 bg=self.colors['gray_50']).pack(side='left', anchor='w', padx=(10, 0))
        
        self.target_drive_var = tk.StringVar(value="D:")
        target_entry = ttk.Entry(path_frame, textvariable=self.target_drive_var, 
                                font=('Arial', 12))
        target_entry.pack(side='left', fill='x', expand=True)
        
        ttk.Button(path_frame, text="Browse", 
                  command=self.browse_target_drive).pack(side='right', padx=(10, 0))
        
        # Move button
        move_button = ttk.Button(options_frame, text="📦 Move Now", 
                                style='Primary.TButton',
                                command=self.move_packages)
        move_button.pack(fill='x', pady=(10, 0))
        
        # Status label
        self.status_label = tk.Label(tab_frame, text="", 
                                    font=('Arial', 12), 
                                    fg=self.colors['gray_600'], 
                                    bg=self.colors['gray_50'],
                                    wraplength=600, justify="left")
        self.status_label.pack(fill='x', padx=20, pady=(0, 20))
    
    def create_environments_tab(self):
        """Create tab for managing development environments"""
        tab_frame = tk.Frame(self.notebook, bg=self.colors['gray_50'])
        self.notebook.add(tab_frame, text="  🔧 Dev Environments  ")
        
        # Environment options
        options_frame = tk.Frame(tab_frame, bg=self.colors['gray_50'])
        options_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(options_frame, text="Environment Options", 
                font=('Arial', 16, 'bold'), 
                fg=self.colors['gray_800'], 
                bg=self.colors['gray_50']).pack(anchor='w', pady=(0, 10))
        
        # Listbox for installed environments
        list_frame = tk.Frame(tab_frame, bg=self.colors['gray_50'])
        list_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        self.env_listbox = tk.Listbox(list_frame, 
                                      bg=self.colors['white'], 
                                      fg=self.colors['gray_800'], 
                                      font=('Arial', 12),
                                      selectmode="multiple")
        self.env_listbox.pack(fill='both', expand=True)
        
        # Scrollbar for listbox
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.env_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.env_listbox.config(yscrollcommand=scrollbar.set)
        
        # Action buttons
        action_frame = tk.Frame(tab_frame, bg=self.colors['gray_50'])
        action_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        ttk.Button(action_frame, text="🗑️ Remove Selected", 
                  style='Danger.TButton',
                  command=self.remove_selected_envs).pack(side='left', padx=(0, 10))
        
        ttk.Button(action_frame, text="🔄 Refresh List", 
                  command=self.refresh_env_list).pack(side='left')
        
        # Status label
        self.env_status_label = tk.Label(tab_frame, text="", 
                                        font=('Arial', 12), 
                                        fg=self.colors['gray_600'], 
                                        bg=self.colors['gray_50'],
                                        wraplength=600, justify="left")
        self.env_status_label.pack(fill='x', padx=20, pady=(0, 20))
    
    def create_settings_tab(self):
        """Create settings and installation tab"""
        tab_frame = tk.Frame(self.notebook, bg=self.colors['gray_50'])
        self.notebook.add(tab_frame, text="  ⚙️ Settings  ")
        
        # Installation status
        install_frame = tk.Frame(tab_frame, bg=self.colors['gray_50'])
        install_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(install_frame, text="Installation Status", 
                font=('Arial', 16, 'bold'), 
                fg=self.colors['gray_800'], 
                bg=self.colors['gray_50']).pack(anchor='w', pady=(0, 10))
        
        self.install_status_label = tk.Label(install_frame, text="", 
                                            font=('Arial', 12), 
                                            fg=self.colors['gray_600'], 
                                            bg=self.colors['gray_50'],
                                            wraplength=600, justify="left")
        self.install_status_label.pack(fill='x', pady=(0, 10))
        
        ttk.Button(install_frame, text="🔄 Check Status", 
                  command=self.check_installation_status).pack(side='left', padx=(0, 10))
        
        ttk.Button(install_frame, text="📥 Install CleanShift", 
                  style='Primary.TButton',
                  command=self.install_cleanshift).pack(side='left')
        
        # Uninstall button
        uninstall_frame = tk.Frame(tab_frame, bg=self.colors['gray_50'])
        uninstall_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        ttk.Button(uninstall_frame, text="🗑️ Uninstall CleanShift", 
                  style='Danger.TButton',
                  command=self.uninstall_cleanshift).pack(fill='x')
        
        # About section
        about_frame = tk.Frame(tab_frame, bg=self.colors['gray_50'])
        about_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        tk.Label(about_frame, text="About CleanShift", 
                font=('Arial', 16, 'bold'), 
                fg=self.colors['gray_800'], 
                bg=self.colors['gray_50']).pack(anchor='w', pady=(0, 10))
        
        about_text = """CleanShift is a powerful system cleanup and optimization tool for Windows.

Features:
• Analyze disk space usage and find large folders
• Clean temporary files, browser caches, and system caches
• Move installed packages and folders to other drives
• Manage development environments and tools

Get started by checking your disk space status on the Dashboard tab.
"""
        tk.Label(about_frame, text=about_text, 
                 font=('Arial', 12), 
                 fg=self.colors['gray_700'], 
                 bg=self.colors['gray_50'],
                 wraplength=600, justify="left").pack(anchor='w')
    
    def create_about_tab(self):
        """Create about and help tab"""
        tab_frame = tk.Frame(self.notebook, bg=self.colors['gray_50'])
        self.notebook.add(tab_frame, text="  ℹ️ About  ")
        
        # About content
        about_text = """CleanShift - CLI utility to clean and shift C drive content to other drives

Version: 1.0.0
Author: CleanShift Team

Features:
- Disk Analysis: Scan C: drive and identify large folders
- Smart Cleanup: Remove temp files, browser caches, system caches
- Package Moving: Move folders to other drives with symbolic links
- Drive Status: Monitor disk space across all drives
- Safety First: Dry run mode and system directory protection
- Standalone: No dependencies - single executable file

Usage:
- Check Drive Status: cleanshift status
- Analyze Large Folders: cleanshift analyze --min-size 500
- Clean Temporary Files: cleanshift clean --temp-files --browser-cache --dry-run
- Move Large Folders: cleanshift move --source "C:\\Users\\Username\\Downloads" --target-drive D:

For more information, visit the [CleanShift GitHub page](https://github.com/theaathish/CleanShift).
"""
        tk.Label(tab_frame, text=about_text, 
                 font=('Arial', 12), 
                 fg=self.colors['gray_700'], 
                 bg=self.colors['gray_50'],
                 wraplength=600, justify="left").pack(anchor='w', padx=20, pady=20)
        
        # Links frame
        links_frame = tk.Frame(tab_frame, bg=self.colors['gray_50'])
        links_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        # GitHub link
        github_link = ttk.Label(links_frame, text="GitHub Repository", 
                               foreground=self.colors['primary'],
                               cursor="hand2",
                               font=('Arial', 12, 'underline'))
        github_link.pack(side='left', padx=(0, 10))
        github_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/theaathish/CleanShift"))
        
        # License link
        license_link = ttk.Label(links_frame, text="MIT License", 
                                foreground=self.colors['primary'],
                                cursor="hand2",
                                font=('Arial', 12, 'underline'))
        license_link.pack(side='left', padx=(0, 10))
        license_link.bind("<Button-1>", lambda e: webbrowser.open("https://opensource.org/licenses/MIT"))
        
        # Issues link
        issues_link = ttk.Label(links_frame, text="Report an Issue", 
                               foreground=self.colors['primary'],
                               cursor="hand2",
                               font=('Arial', 12, 'underline'))
        issues_link.pack(side='left')
        issues_link.bind("<Button-1>", lambda e: webbrowser.open("https://github.com/theaathish/CleanShift/issues"))
    
    def check_admin_status(self):
        """Check and display admin status"""
        if is_admin():
            self.admin_label.config(text="Administrator ✓", fg=self.colors['success'])
        else:
            self.admin_label.config(text="Limited User ⚠", fg=self.colors['warning'])
        
        # Update system info
        self.update_system_info()
    
    def update_system_info(self):
        """Update system information display"""
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            info_text = f"""OS: {platform.system()} {platform.release()}
CPU Usage: {cpu_percent}%
Memory: {format_size(memory.used)} / {format_size(memory.total)} ({memory.percent}% used)
Administrator: {'Yes' if is_admin() else 'No'}"""
            
            self.system_info_label.config(text=info_text)
        except Exception:
            self.system_info_label.config(text="System information unavailable")
    
    def refresh_dashboard(self):
        """Refresh the dashboard data"""
        # Update drive status cards
        for widget in self.drives_container.winfo_children():
            widget.destroy()
        
        drives = self.analyzer.get_drive_info()
        for drive in drives:
            drive_card = tk.Frame(self.drives_container, 
                                 bg=self.colors['white'],
                                 relief='solid',
                                 borderwidth=1)
            drive_card.pack(fill='x', pady=5)
            
            tk.Label(drive_card, text=drive['drive'], 
                     font=('Arial', 14, 'bold'), 
                     fg=self.colors['gray_800'], 
                     bg=self.colors['white']).pack(side='left', padx=10, pady=10)
            
            usage_percent = f"{drive['usage_percent']:.1f}%"
            tk.Label(drive_card, text=usage_percent, 
                     font=('Arial', 14, 'bold'), 
                     fg=self.colors['primary'], 
                     bg=self.colors['white']).pack(side='right', padx=10, pady=10)
        
        # Update system info
        self.update_system_info()
    
    def quick_clean(self):
        """Perform a quick clean of common areas"""
        self.cleaner.clean_temp_files()
        self.cleaner.clean_browser_cache()
        self.cleaner.clean_system_cache()
        
        messagebox.showinfo("Quick Clean", "Quick clean completed successfully.")
        self.refresh_dashboard()
    
    def quick_analyze(self):
        """Perform a quick analysis of disk usage"""
        self.analyzer.scan_directory("C:\\", 100 * 1024 * 1024)
        messagebox.showinfo("Quick Analyze", "Quick analysis completed. Check the Analyze tab for details.")
        self.refresh_dashboard()
    
    def update_min_size_label(self, value):
        """Update the minimum size label for analysis"""
        min_size_mb = int(float(value))
        self.min_size_label.config(text=f"{min_size_mb} MB")
    
    def analyze_disk(self):
        """Analyze disk usage and update results treeview"""
        min_size = self.min_size_var.get() * 1024 * 1024  # Convert to bytes
        results = self.analyzer.scan_directory("C:\\", min_size)
        
        # Clear existing results
        self.results_tree.delete(*self.results_tree.get_children())
        
        # Insert new results
        for result in results:
            self.results_tree.insert("", "end", values=(result['path'], format_size(result['size']), result['type']))
        
        messagebox.showinfo("Analyze Disk", "Disk analysis completed. Check the results below.")
    
    def sort_results(self, column):
        """Sort the results treeview by column"""
        try {
            # Get current sorting order
            current_order = self.results_tree.heading(column, "sort")
            new_order = "ascending" if current_order == "descending" else "descending"
            
            # Sort data
            data = [(self.results_tree.item(item)["values"], item) for item in self.results_tree.get_children("")]
            data.sort(reverse=new_order=="descending")
            
            # Update treeview
            for index, (values, item) in enumerate(data):
                self.results_tree.item(item, text="", values=values)
            
            # Update column heading
            self.results_tree.heading(column, command=lambda: self.sort_results(column))
        } except Exception as e {
            print(f"Error sorting results: {e}")
        }
    
    def open_folder(self, event):
        """Open the selected folder in File Explorer"""
        try:
            item = self.results_tree.selection()[0]
            folder_path = self.results_tree.item(item, "values")[0]
            subprocess.Popen(f'explorer "{folder_path}"')
        except Exception as e:
            print(f"Error opening folder: {e}")
    
    def browse_source_folder(self):
        """Open a folder dialog to select the source folder"""
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.source_path_var.set(folder_path)
    
    def browse_target_drive(self):
        """Open a folder dialog to select the target drive"""
        drive_path = filedialog.askdirectory()
        if drive_path:
            # Ensure the selected path is a drive letter
            drive_letter = os.path.splitdrive(drive_path)[0]
            self.target_drive_var.set(drive_letter)
    
    def move_packages(self):
        """Move the selected packages/folders to the target drive"""
        source = self.source_path_var.get()
        target_drive = self.target_drive_var.get()
        
        if not source or not target_drive:
            messagebox.showwarning("Missing Information", "Please specify both source and target drive.")
            return
        
        # Confirm action
        if self.confirm_actions.get() and not messagebox.askyesno("Confirm Move", f"Move {source} to {target_drive}?"):
            return
        
        # Perform the move
        success = self.mover.move_with_symlink(source, target_drive)
        
        if success:
            messagebox.showinfo("Move Successful", f"Successfully moved {source} to {target_drive}.")
            self.refresh_dashboard()
        else:
            messagebox.showerror("Move Failed", f"Failed to move {source}.")
    
    def remove_selected_envs(self):
        """Remove the selected development environments"""
        selected = self.env_listbox.curselection()
        if not selected:
            return
        
        # Confirm action
        if not messagebox.askyesno("Confirm Removal", "Remove selected environments?"):
            return
        
        for index in selected:
            env_name = self.env_listbox.get(index)
            success = self.env_cleaner.remove_environment(env_name)
            
            if success:
                self.env_listbox.delete(index)
        
        messagebox.showinfo("Removal Complete", "Selected environments have been removed.")
    
    def refresh_env_list(self):
        """Refresh the list of installed environments"""
        self.env_listbox.delete(0, tk.END)
        
        envs = self.env_cleaner.get_installed_environments()
        for env in envs:
            self.env_listbox.insert(tk.END, env)
    
    def check_installation_status(self):
        """Check and display the installation status of CleanShift"""
        try:
            import winreg
            
            # Check if CleanShift is installed
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall",
                               0, winreg.KEY_READ | winreg.KEY_WOW64_64KEY) as key:
                try:
                    display_name, _ = winreg.QueryValueEx(key, "DisplayName")
                    if "CleanShift" in display_name:
                        self.install_status_label.config(text="CleanShift is installed.", 
                                                        fg=self.colors['success'])
                        return True
                except FileNotFoundError:
                    pass
            
            self.install_status_label.config(text="CleanShift is not installed.", 
                                            fg=self.colors['danger'])
            return False
        except Exception as e:
            self.install_status_label.config(text=f"Error checking status: {e}", 
                                            fg=self.colors['danger'])
            return False
    
    def install_cleanshift(self):
        """Install CleanShift to the system"""
        try:
            import shutil
            import winreg
            
            # Get current executable path
            if getattr(sys, 'frozen', False):
                exe_path = sys.executable
            else:
                messagebox.showerror("Installation Error", "This command only works with the compiled executable.")
                return
            
            # Install to Program Files
            install_dir = "C:\\Program Files\\CleanShift"
            os.makedirs(install_dir, exist_ok=True)
            target_path = os.path.join(install_dir, "cleanshift.exe")
            
            # Copy executable
            shutil.copy2(exe_path, target_path)
            
            # Add to PATH
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                   "SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment",
                                   0, winreg.KEY_ALL_ACCESS) as key:
                    try:
                        path_value, _ = winreg.QueryValueEx(key, "PATH")
                    except FileNotFoundError:
                        path_value = ""
                    
                    new_path = path_value + ";" + install_dir if path_value else install_dir
                    winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
                    self.install_status_label.config(text="CleanShift installed successfully.", 
                                                    fg=self.colors['success'])
            except PermissionError:
                self.install_status_label.config(text="Could not modify system PATH. Manual addition required.", 
                                                fg=self.colors['warning'])
            
            # Create desktop shortcut (optional)
            try:
                import win32com.client
                desktop = os.path.join(os.path.expanduser("~"), "Desktop")
                shortcut_path = os.path.join(desktop, "CleanShift.lnk")
                
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(shortcut_path)
                shortcut.Targetpath = target_path
                shortcut.WorkingDirectory = install_dir
                shortcut.IconLocation = target_path
                shortcut.save()
                self.install_status_label.config(text="Desktop shortcut created.", 
                                                fg=self.colors['success'])
            except Exception:
                pass  # Desktop shortcut is optional
            
            messagebox.showinfo("Installation Complete", "CleanShift has been installed. Please restart your command prompt.")
        except Exception as e:
            messagebox.showerror("Installation Error", str(e))
    
    def uninstall_cleanshift(self):
        """Uninstall CleanShift from the system"""
        try:
            import winreg
            import shutil
            
            install_dir = "C:\\Program Files\\CleanShift"
            
            if not os.path.exists(install_dir):
                messagebox.showinfo("Uninstall CleanShift", "CleanShift is not installed.")
                return
            
            # Confirm uninstall
            if not messagebox.askyesno("Confirm Uninstall", "Uninstall CleanShift?"):
                return
            
            # Remove from PATH
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                   "SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment",
                                   0, winreg.KEY_ALL_ACCESS) as key:
                    path_value, _ = winreg.QueryValueEx(key, "PATH")
                    new_path = path_value.replace(f";{install_dir}", "").replace(install_dir, "")
                    winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
            except:
                pass
            
            # Remove installation directory
            shutil.rmtree(install_dir, ignore_errors=True)
            
            # Remove desktop shortcut
            desktop_shortcut = os.path.join(os.path.expanduser("~"), "Desktop", "CleanShift.lnk")
            if os.path.exists(desktop_shortcut):
                os.remove(desktop_shortcut)
            
            messagebox.showinfo("Uninstall CleanShift", "CleanShift has been uninstalled.")
            self.install_status_label.config(text="CleanShift is not installed.", 
                                            fg=self.colors['danger'])
        except Exception as e:
            messagebox.showerror("Uninstall Error", str(e))
    
    def run(self):
        """Run the GUI application"""
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        
        # Show welcome message for first-time users
        if not self.check_installation_status():
            self.show_welcome_dialog()
        
        self.root.mainloop()
    
    def show_welcome_dialog(self):
        """Show welcome dialog for new users"""
        welcome_text = """Welcome to CleanShift!

This is your first time running CleanShift. Here's what you can do:

• 📊 Dashboard: View drive status and system info
• 🧹 Clean: Remove temporary files and optimize system
• 🔍 Analyze: Find large files and folders consuming space
• 📦 Move Apps: Relocate applications to free up C: drive
• 🔧 Dev Environments: Clean development tools and caches

For full functionality, consider installing CleanShift to your system from the Settings tab.

Enjoy using CleanShift!"""
        
        messagebox.showinfo("Welcome to CleanShift", welcome_text)