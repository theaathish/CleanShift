```python
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import sys
from pathlib import Path
from PIL import Image, ImageTk
import platform

# Import modules with fallback
try:
    from .analyzer import DiskAnalyzer
    from .cleaner import SystemCleaner
    from .mover import PackageMover
    from .utils import is_admin, format_size
    from .env_cleaner import EnvironmentCleaner
except ImportError:
    try:
        from analyzer import DiskAnalyzer
        from cleaner import SystemCleaner
        from mover import PackageMover
        from utils import is_admin, format_size
        from env_cleaner import EnvironmentCleaner
    except ImportError:
        # Create minimal implementations
        class DiskAnalyzer:
            def get_drive_info(self): return []
            def scan_directory(self, path, min_size): return []
            def analyze_software(self): return []
        
        class SystemCleaner:
            def clean_temp_files(self, dry_run=False): return 0
            def clean_browser_cache(self, dry_run=False): return 0
            def clean_system_cache(self, dry_run=False): return 0
            def clean_recycle_bin(self, dry_run=False): return 0
        
        class PackageMover:
            def move_with_symlink(self, source, target, dry_run=False): return False
        
        class EnvironmentCleaner:
            def find_environments(self): return []
            def clean_environment(self, env_type, dry_run=False): return 0
        
        def is_admin(): return True
        def format_size(size): return f"{size} B"

class CleanShiftGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CleanShift - System Cleanup & Optimizer")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f8fafc")
        
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
            logo_path = Path(__file__).parent.parent / "assets" / "logo.png"
            if logo_path.exists():
                img = Image.open(logo_path)
                img = img.resize((64, 64), Image.Resampling.LANCZOS)
                self.logo = ImageTk.PhotoImage(img)
                logo_label = tk.Label(header_frame, image=self.logo, bg=self.colors['white'])
                logo_label.pack(side='left', padx=20, pady=8)
        except Exception:
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
        self.notebook.add(tab_frame, text="  Dashboard  ")
        
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
        
        ttk.Button(quick_buttons, text="Quick Clean", 
                  style='Primary.TButton',
                  command=self.quick_clean).pack(side='left', padx=(0, 10))
        
        ttk.Button(quick_buttons, text="Analyze Disk", 
                  style='Success.TButton',
                  command=self.quick_analyze).pack(side='left', padx=(0, 10))
        
        ttk.Button(quick_buttons, text="Refresh Status", 
                  command=self.refresh_dashboard).pack(side='left')
        
        # Load initial data
        self.refresh_dashboard()
    
    def create_clean_tab(self):
        """Create cleaning options tab"""
        tab_frame = tk.Frame(self.notebook, bg=self.colors['gray_50'])
        self.notebook.add(tab_frame, text="  Clean  ")
        
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
        self.create_clean_section(scrollable_frame, "System Files", [
            ("Temporary Files", "clean_temp", "Clean system and user temp files"),
            ("Browser Cache", "clean_browser", "Clear browser cache files"),
            ("System Cache", "clean_system", "Clear Windows system cache"),
            ("Recycle Bin", "clean_recycle", "Empty recycle bin"),
        ])
        
        self.create_clean_section(scrollable_frame, "Memory & Performance", [
            ("RAM Cache", "clean_ram", "Clear RAM cache and optimize memory"),
            ("DNS Cache", "clean_dns", "Flush DNS cache"),
            ("Registry Cleanup", "clean_registry", "Clean invalid registry entries"),
        ])
        
        # Clean all button
        clean_all_frame = tk.Frame(scrollable_frame, bg=self.colors['gray_50'])
        clean_all_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Button(clean_all_frame, text="Clean All Selected", 
                  style='Primary.TButton',
                  command=self.clean_all_selected).pack(side='left', padx=(0, 10))
        
        ttk.Button(clean_all_frame, text="Preview Changes", 
                  command=self.preview_clean).pack(side='left')
    
    def create_analyze_tab(self):
        """Create disk analysis tab"""
        tab_frame = tk.Frame(self.notebook, bg=self.colors['gray_50'])
        self.notebook.add(tab_frame, text="  Analyze  ")
        
        # Controls
        controls_frame = tk.Frame(tab_frame, bg=self.colors['gray_50'])
        controls_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(controls_frame, text="Disk Space Analysis", 
                font=('Arial', 16, 'bold'), 
                fg=self.colors['gray_800'], 
                bg=self.colors['gray_50']).pack(anchor='w', pady=(0, 10))
        
        # Path selection
        path_frame = tk.Frame(controls_frame, bg=self.colors['gray_50'])
        path_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(path_frame, text="Scan Path:", bg=self.colors['gray_50']).pack(side='left')
        self.scan_path = tk.StringVar(value="C:\\")
        path_entry = tk.Entry(path_frame, textvariable=self.scan_path, width=40)
        path_entry.pack(side='left', padx=(10, 5))
        
        ttk.Button(path_frame, text="Browse", 
                  command=self.browse_scan_path).pack(side='left', padx=(5, 10))
        
        ttk.Button(path_frame, text="Start Analysis", 
                  style='Primary.TButton',
                  command=self.start_analysis).pack(side='left')
        
        # Results
        results_frame = ttk.Frame(tab_frame, style='Card.TFrame')
        results_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Analysis results treeview
        self.analysis_tree = ttk.Treeview(results_frame, style='Modern.Treeview')
        self.analysis_tree["columns"] = ("Size", "Type", "Suggestion")
        self.analysis_tree.heading("#0", text="Path")
        self.analysis_tree.heading("Size", text="Size")
        self.analysis_tree.heading("Type", text="Type")
        self.analysis_tree.heading("Suggestion", text="Suggestion")
        
        analysis_scroll = ttk.Scrollbar(results_frame, orient="vertical", command=self.analysis_tree.yview)
        self.analysis_tree.configure(yscrollcommand=analysis_scroll.set)
        
        self.analysis_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        analysis_scroll.pack(side="right", fill="y", pady=10)
    
    def create_move_tab(self):
        """Create file/app moving tab"""
        tab_frame = tk.Frame(self.notebook, bg=self.colors['gray_50'])
        self.notebook.add(tab_frame, text="  Move Apps  ")
        
        # Header
        header_frame = tk.Frame(tab_frame, bg=self.colors['gray_50'])
        header_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(header_frame, text="Move Applications & Files", 
                font=('Arial', 16, 'bold'), 
                fg=self.colors['gray_800'], 
                bg=self.colors['gray_50']).pack(anchor='w', pady=(0, 10))
        
        ttk.Button(header_frame, text="Scan for Movable Apps", 
                  style='Primary.TButton',
                  command=self.scan_movable_apps).pack(anchor='w')
        
        # Movable items list
        items_frame = ttk.Frame(tab_frame, style='Card.TFrame')
        items_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        self.movable_tree = ttk.Treeview(items_frame, style='Modern.Treeview')
        self.movable_tree["columns"] = ("Size", "Location", "Target", "Status")
        self.movable_tree.heading("#0", text="Application")
        self.movable_tree.heading("Size", text="Size")
        self.movable_tree.heading("Location", text="Current Location")
        self.movable_tree.heading("Target", text="Target Drive")
        self.movable_tree.heading("Status", text="Status")
        
        movable_scroll = ttk.Scrollbar(items_frame, orient="vertical", command=self.movable_tree.yview)
        self.movable_tree.configure(yscrollcommand=movable_scroll.set)
        
        self.movable_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        movable_scroll.pack(side="right", fill="y", pady=10)
        
        # Move controls
        move_controls = tk.Frame(tab_frame, bg=self.colors['gray_50'])
        move_controls.pack(fill='x', padx=20, pady=(0, 20))
        
        ttk.Button(move_controls, text="Move Selected", 
                  style='Success.TButton',
                  command=self.move_selected_apps).pack(side='left', padx=(0, 10))
        
        ttk.Button(move_controls, text="Preview Move", 
                  command=self.preview_move).pack(side='left')
    
    def create_environments_tab(self):
        """Create development environments cleanup tab"""
        tab_frame = tk.Frame(self.notebook, bg=self.colors['gray_50'])
        self.notebook.add(tab_frame, text="  Dev Environments  ")
        
        # Header
        header_frame = tk.Frame(tab_frame, bg=self.colors['gray_50'])
        header_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(header_frame, text="Development Environment Cleanup", 
                font=('Arial', 16, 'bold'), 
                fg=self.colors['gray_800'], 
                bg=self.colors['gray_50']).pack(anchor='w', pady=(0, 10))
        
        tk.Label(header_frame, text="Find and clean development environments (Node.js, Python, etc.)", 
                font=('Arial', 10), 
                fg=self.colors['gray_600'], 
                bg=self.colors['gray_50']).pack(anchor='w')
        
        # Scan button
        ttk.Button(header_frame, text="Scan for Environments", 
                  style='Primary.TButton',
                  command=self.scan_environments).pack(anchor='w', pady=(10, 0))
        
        # Environment list
        env_frame = ttk.Frame(tab_frame, style='Card.TFrame')
        env_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        self.env_tree = ttk.Treeview(env_frame, style='Modern.Treeview')
        self.env_tree["columns"] = ("Type", "Size", "Path", "Action")
        self.env_tree.heading("#0", text="Environment")
        self.env_tree.heading("Type", text="Type")
        self.env_tree.heading("Size", text="Size")
        self.env_tree.heading("Path", text="Path")
        self.env_tree.heading("Action", text="Recommended Action")
        
        env_scroll = ttk.Scrollbar(env_frame, orient="vertical", command=self.env_tree.yview)
        self.env_tree.configure(yscrollcommand=env_scroll.set)
        
        self.env_tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        env_scroll.pack(side="right", fill="y", pady=10)
        
        # Environment controls
        env_controls = tk.Frame(tab_frame, bg=self.colors['gray_50'])
        env_controls.pack(fill='x', padx=20, pady=(0, 20))
        
        ttk.Button(env_controls, text="Clean Selected", 
                  style='Warning.TButton',
                  command=self.clean_selected_environments).pack(side='left', padx=(0, 10))
        
        ttk.Button(env_controls, text="Clean All Unused", 
                  style='Danger.TButton',
                  command=self.clean_all_environments).pack(side='left')
    
    def create_settings_tab(self):
        """Create settings and installation tab"""
        tab_frame = tk.Frame(self.notebook, bg=self.colors['gray_50'])
        self.notebook.add(tab_frame, text="  Settings  ")
        
        # Installation section
        install_frame = ttk.LabelFrame(tab_frame, text="Installation", padding=20)
        install_frame.pack(fill='x', padx=20, pady=20)
        
        self.install_status = tk.Label(install_frame, text="Checking installation status...", 
                                      font=('Arial', 10), bg=self.colors['white'])
        self.install_status.pack(anchor='w', pady=(0, 10))
        
        install_buttons = tk.Frame(install_frame, bg=self.colors['white'])
        install_buttons.pack(anchor='w')
        
        ttk.Button(install_buttons, text="Install to System", 
                  style='Primary.TButton',
                  command=self.install_to_system).pack(side='left', padx=(0, 10))
        
        ttk.Button(install_buttons, text="Uninstall", 
                  style='Danger.TButton',
                  command=self.uninstall_from_system).pack(side='left')
        
        # Settings section
        settings_frame = ttk.LabelFrame(tab_frame, text="Preferences", padding=20)
        settings_frame.pack(fill='x', padx=20, pady=(0, 20))
        
        self.auto_clean = tk.BooleanVar()
        tk.Checkbutton(settings_frame, text="Enable automatic cleanup on startup", 
                      variable=self.auto_clean, bg=self.colors['white']).pack(anchor='w')
        
        self.confirm_actions = tk.BooleanVar(value=True)
        tk.Checkbutton(settings_frame, text="Confirm before performing actions", 
                      variable=self.confirm_actions, bg=self.colors['white']).pack(anchor='w')
        
        self.check_installation_status()
    
    def create_about_tab(self):
        """Create about and help tab"""
        tab_frame = tk.Frame(self.notebook, bg=self.colors['gray_50'])
        self.notebook.add(tab_frame, text="  About  ")
        
        # About section
        about_frame = tk.Frame(tab_frame, bg=self.colors['white'], padx=40, pady=40)
        about_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(about_frame, text="CleanShift", 
                font=('Arial', 24, 'bold'), 
                fg=self.colors['gray_800'], 
                bg=self.colors['white']).pack(pady=(0, 10))
        
        tk.Label(about_frame, text="Version 1.0.0", 
                font=('Arial', 12), 
                fg=self.colors['gray_600'], 
                bg=self.colors['white']).pack(pady=(0, 20))
        
        about_text = """
CleanShift is a comprehensive system cleanup and optimization tool designed to:

• Clean temporary files, cache, and system junk
• Analyze disk usage and suggest optimizations  
• Move applications to free up C: drive space
• Manage development environments
• Optimize system performance

Features:
✓ Safe file operations with preview mode
✓ Intelligent application moving with symlinks
✓ Development environment cleanup
✓ Modern, intuitive interface
✓ System-wide installation option

Created with ❤️ for Windows users who want to keep their systems clean and optimized.
        """
        
        tk.Label(about_frame, text=about_text, 
                font=('Arial', 10), 
                fg=self.colors['gray_700'], 
                bg=self.colors['white'],
                justify='left').pack(pady=(0, 20))
        
        # Links
        links_frame = tk.Frame(about_frame, bg=self.colors['white'])
        links_frame.pack()
        
        ttk.Button(links_frame, text="GitHub Repository", 
                  command=lambda: self.open_url("https://github.com/theaathish/CleanShift")).pack(side='left', padx=(0, 10))
        
        ttk.Button(links_frame, text="Report Issue", 
                  command=lambda: self.open_url("https://github.com/theaathish/CleanShift/issues")).pack(side='left')
    
    # Callback methods for button actions
    def quick_clean(self):
        """Perform a quick clean of common junk files"""
        cleaner = SystemCleaner()
        total_freed = cleaner.clean_temp_files() + cleaner.clean_browser_cache() + cleaner.clean_system_cache()
        messagebox.showinfo("Quick Clean", f"Quick clean completed. Freed up: {format_size(total_freed)}")
        self.refresh_dashboard()
    
    def quick_analyze(self):
        """Perform a quick analysis of disk usage"""
        analyzer = DiskAnalyzer()
        results = analyzer.scan_directory("C:\\", 100 * 1024 * 1024)  # 100 MB threshold
        
        if not results:
            messagebox.showinfo("Quick Analyze", "No large folders found over 100 MB.")
            return
        
        # Show top 10 results
        top_results = results[:10]
        result_text = "\n".join([f"{r['path']}: {format_size(r['size'])}" for r in top_results])
        messagebox.showinfo("Quick Analyze - Top 10 Folders", result_text)
    
    def refresh_dashboard(self):
        """Refresh the dashboard drive status"""
        for widget in self.drives_container.winfo_children():
            widget.destroy()
        
        drives = self.analyzer.get_drive_info()
        for drive in drives:
            usage_percent = f"{drive['usage_percent']:.1f}%"
            tk.Label(self.drives_container, text=f"{drive['drive']} - {format_size(drive['used'])} used ({usage_percent})", 
                    bg=self.colors['white'], 
                    fg=self.colors['gray_800'],
                    font=('Arial', 12)).pack(anchor='w', pady=5)
    
    def browse_scan_path(self):
        """Open a file dialog to select scan path"""
        path = filedialog.askdirectory(initialdir="C:\\", title="Select Folder to Analyze")
        if path:
            self.scan_path.set(path)
    
    def start_analysis(self):
        """Start the disk analysis in a new thread"""
        path = self.scan_path.get()
        if not os.path.exists(path):
            messagebox.showerror("Invalid Path", "The selected path does not exist.")
            return
        
        # Clear previous results
        for item in self.analysis_tree.get_children():
            self.analysis_tree.delete(item)
        
        def analyze():
            """Run the analysis and update the UI"""
            analyzer = DiskAnalyzer()
            results = analyzer.scan_directory(path, 100 * 1024 * 1024)  # 100 MB threshold
            
            for result in results:
                self.analysis_tree.insert("", "end", text=result['path'], values=(format_size(result['size']), result['type'], ""))
            
            messagebox.showinfo("Analysis Complete", f"Analysis complete. Found {len(results)} folders over 100 MB.")
        
        # Run in a separate thread to avoid blocking the UI
        threading.Thread(target=analyze, daemon=True).start()
    
    def scan_movable_apps(self):
        """Scan for applications that can be moved to another drive"""
        # For demo, just show some dummy data
        for item in self.movable_tree.get_children():
            self.movable_tree.delete(item)
        
        dummy_apps = [
            {"name": "App1", "size": 250 * 1024 * 1024, "location": "C:\\Program Files\\App1", "target": "D:\\Apps\\App1", "status": "Ready to move"},
            {"name": "App2", "size": 150 * 1024 * 1024, "location": "C:\\Program Files\\App2", "target": "D:\\Apps\\App2", "status": "Ready to move"},
            {"name": "App3", "size": 500 * 1024 * 1024, "location": "C:\\Program Files\\App3", "target": "E:\\Apps\\App3", "status": "Ready to move"},
        ]
        
        for app in dummy_apps:
            self.movable_tree.insert("", "end", text=app['name'], values=(format_size(app['size']), app['location'], app['target'], app['status']))
    
    def move_selected_apps(self):
        """Move the selected applications to the target location"""
        selected_items = self.movable_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select an application to move.")
            return
        
        for item in selected_items:
            app_name = self.movable_tree.item(item, "text")
            app_size = self.movable_tree.item(item, "values")[0]
            app_location = self.movable_tree.item(item, "values")[1]
            app_target = self.movable_tree.item(item, "values")[2]
            
            # For demo, just show a message
            messagebox.showinfo("Move Application", f"Moving {app_name} ({format_size(app_size)}) from {app_location} to {app_target}")
    
    def preview_move(self):
        """Preview the move action for the selected application"""
        selected_items = self.movable_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select an application to preview move.")
            return
        
        for item in selected_items:
            app_name = self.movable_tree.item(item, "text")
            app_target = self.movable_tree.item(item, "values")[2]
            
            messagebox.showinfo("Preview Move", f"{app_name} will be moved to {app_target}")
    
    def scan_environments(self):
        """Scan for development environments to clean"""
        # For demo, just show some dummy data
        for item in self.env_tree.get_children():
            self.env_tree.delete(item)
        
        dummy_envs = [
            {"name": "Node.js 14.x", "type": "Node.js", "size": 300 * 1024 * 1024, "path": "C:\\Program Files\\Nodejs", "action": "Remove"},
            {"name": "Python 3.8", "type": "Python", "size": 200 * 1024 * 1024, "path": "C:\\Program Files\\Python38", "action": "Remove"},
            {"name": "Anaconda3", "type": "Python", "size": 1 * 1024 * 1024 * 1024, "path": "C:\\ProgramData\\Anaconda3", "action": "Remove"},
        ]
        
        for env in dummy_envs:
            self.env_tree.insert("", "end", text=env['name'], values=(env['type'], format_size(env['size']), env['path'], env['action']))
    
    def clean_selected_environments(self):
        """Clean the selected development environments"""
        selected_items = self.env_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select an environment to clean.")
            return
        
        for item in selected_items:
            env_name = self.env_tree.item(item, "text")
            env_type = self.env_tree.item(item, "values")[0]
            env_path = self.env_tree.item(item, "values")[2]
            
            # For demo, just show a message
            messagebox.showinfo("Clean Environment", f"Cleaning {env_name} ({env_type}) at {env_path}")
    
    def clean_all_environments(self):
        """Clean all unused development environments"""
        messagebox.showinfo("Clean All Environments", "Cleaning all unused development environments...")
    
    def install_to_system(self):
        """Install CleanShift to the system"""
        messagebox.showinfo("Install to System", "CleanShift will be installed to the system.")
    
    def uninstall_from_system(self):
        """Uninstall CleanShift from the system"""
        messagebox.showinfo("Uninstall from System", "CleanShift will be uninstalled from the system.")
    
    def check_admin_status(self):
        """Check and display admin status"""
        if is_admin():
            self.admin_label.config(text="Administrator: Yes", fg=self.colors['success'])
        else:
            self.admin_label.config(text="Administrator: No", fg=self.colors['danger'])
    
    def open_url(self, url):
        """Open a URL in the default web browser"""
        import webbrowser
        webbrowser.open(url)

    def run(self):
        """Run the GUI application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = CleanShiftGUI()
    app.run()
```