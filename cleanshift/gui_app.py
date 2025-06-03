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
        self.create_about_tab()
    
    def create_header(self, parent):
        """Create header with logo and title"""
        header_frame = tk.Frame(parent, bg=self.colors['white'], height=80)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Logo (emoji fallback)
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
        
        # Load initial data
        self.refresh_dashboard()
    
    def create_clean_tab(self):
        """Create cleaning options tab"""
        tab_frame = tk.Frame(self.notebook, bg=self.colors['gray_50'])
        self.notebook.add(tab_frame, text="  🧹 Clean  ")
        
        # Clean options section
        clean_frame = tk.Frame(tab_frame, bg=self.colors['white'], 
                              relief='solid', borderwidth=1, padx=20, pady=15)
        clean_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(clean_frame, text="🗃️ System Files", 
                font=('Arial', 14, 'bold'), 
                fg=self.colors['gray_800'], 
                bg=self.colors['white']).pack(anchor='w', pady=(0, 10))
        
        # Create checkboxes for cleaning options
        options = [
            ("Temporary Files", "temp_files", "Clean system and user temp files"),
            ("Browser Cache", "browser_cache", "Clear browser cache files"),
            ("System Cache", "system_cache", "Clear Windows system cache"),
            ("Recycle Bin", "recycle_bin", "Empty recycle bin")
        ]
        
        for option_text, option_key, description in options:
            option_frame = tk.Frame(clean_frame, bg=self.colors['white'])
            option_frame.pack(fill='x', pady=2)
            
            var = tk.BooleanVar()
            self.clean_vars[option_key] = var
            
            cb = tk.Checkbutton(option_frame, text=option_text, 
                               variable=var, bg=self.colors['white'],
                               font=('Arial', 11))
            cb.pack(side='left')
            
            tk.Label(option_frame, text=description, 
                    font=('Arial', 9), 
                    fg=self.colors['gray_600'], 
                    bg=self.colors['white']).pack(side='left', padx=(10, 0))
        
        # Clean buttons
        clean_buttons = tk.Frame(tab_frame, bg=self.colors['gray_50'])
        clean_buttons.pack(fill='x', padx=20, pady=20)
        
        ttk.Button(clean_buttons, text="🚀 Clean Selected", 
                  style='Primary.TButton',
                  command=self.clean_selected).pack(side='left', padx=(0, 10))
        
        ttk.Button(clean_buttons, text="👁️ Preview Changes", 
                  command=self.preview_clean).pack(side='left')
    
    def create_analyze_tab(self):
        """Create disk analysis tab"""
        tab_frame = tk.Frame(self.notebook, bg=self.colors['gray_50'])
        self.notebook.add(tab_frame, text="  🔍 Analyze  ")
        
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
        path_entry = tk.Entry(path_frame, textvariable=self.scan_path, width=40)
        path_entry.pack(side='left', padx=(10, 5))
        
        ttk.Button(path_frame, text="Browse", 
                  command=self.browse_scan_path).pack(side='left', padx=(5, 10))
        
        ttk.Button(path_frame, text="Start Analysis", 
                  style='Primary.TButton',
                  command=self.start_analysis).pack(side='left')
        
        # Results area
        results_frame = tk.Frame(tab_frame, bg=self.colors['white'], 
                                relief='solid', borderwidth=1)
        results_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Results text area
        self.results_text = tk.Text(results_frame, height=20, width=80)
        results_scroll = tk.Scrollbar(results_frame, command=self.results_text.yview)
        self.results_text.config(yscrollcommand=results_scroll.set)
        
        self.results_text.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        results_scroll.pack(side='right', fill='y', pady=10)
    
    def create_about_tab(self):
        """Create about and help tab"""
        tab_frame = tk.Frame(self.notebook, bg=self.colors['gray_50'])
        self.notebook.add(tab_frame, text="  ℹ️ About  ")
        
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
                  command=lambda: webbrowser.open("https://github.com/theaathish/CleanShift")).pack(side='left', padx=(0, 10))
        
        ttk.Button(links_frame, text="Report Issue", 
                  command=lambda: webbrowser.open("https://github.com/theaathish/CleanShift/issues")).pack(side='left')
    
    # Callback methods
    def check_admin_status(self):
        """Check and display admin status"""
        if is_admin():
            self.admin_label.config(text="Administrator ✓", fg=self.colors['success'])
        else:
            self.admin_label.config(text="Limited User ⚠", fg=self.colors['warning'])
    
    def refresh_dashboard(self):
        """Refresh dashboard data"""
        def update_drives():
            # Clear existing drive cards
            for widget in self.drives_container.winfo_children():
                widget.destroy()
            
            # Get drive info
            drives = self.analyzer.get_drive_info()
            
            for i, drive in enumerate(drives):
                self.create_drive_card(self.drives_container, drive, i)
        
        threading.Thread(target=update_drives, daemon=True).start()
    
    def create_drive_card(self, parent, drive_info, index):
        """Create a drive status card"""
        card = tk.Frame(parent, bg=self.colors['white'], 
                       relief='solid', borderwidth=1, padx=15, pady=15)
        card.grid(row=0, column=index, padx=10, sticky='ew')
        
        # Drive letter
        tk.Label(card, text=drive_info['drive'], 
                font=('Arial', 16, 'bold'), 
                fg=self.colors['gray_800'], 
                bg=self.colors['white']).pack()
        
        # Usage percentage
        usage = drive_info['usage_percent']
        color = self.colors['danger'] if usage > 90 else self.colors['warning'] if usage > 75 else self.colors['success']
        
        tk.Label(card, text=f"{usage:.1f}% Used", 
                font=('Arial', 12), 
                fg=color, 
                bg=self.colors['white']).pack()
        
        # Size info
        tk.Label(card, text=f"Free: {format_size(drive_info['free'])}", 
                font=('Arial', 10), 
                fg=self.colors['gray_600'], 
                bg=self.colors['white']).pack()
        
        tk.Label(card, text=f"Total: {format_size(drive_info['total'])}", 
                font=('Arial', 10), 
                fg=self.colors['gray_600'], 
                bg=self.colors['white']).pack()
    
    def quick_clean(self):
        """Perform quick cleanup"""
        def cleanup():
            try:
                total_freed = 0
                total_freed += self.cleaner.clean_temp_files()
                total_freed += self.cleaner.clean_browser_cache()
                
                messagebox.showinfo("Success", 
                                  f"Quick cleanup completed!\nFreed: {format_size(total_freed)}")
                self.refresh_dashboard()
            except Exception as e:
                messagebox.showerror("Error", f"Cleanup failed: {str(e)}")
        
        if messagebox.askyesno("Confirm", "Perform quick cleanup of temporary files and browser cache?"):
            threading.Thread(target=cleanup, daemon=True).start()
    
    def quick_analyze(self):
        """Perform quick disk analysis"""
        self.notebook.select(2)  # Switch to analyze tab
        self.start_analysis()
    
    def clean_selected(self):
        """Clean selected options"""
        selected = [key for key, var in self.clean_vars.items() if var.get()]
        
        if not selected:
            messagebox.showwarning("Warning", "No cleaning options selected!")
            return
        
        if not messagebox.askyesno("Confirm", f"Clean {len(selected)} selected items?"):
            return
        
        def cleanup():
            try:
                total_freed = 0
                
                if 'temp_files' in selected:
                    total_freed += self.cleaner.clean_temp_files()
                if 'browser_cache' in selected:
                    total_freed += self.cleaner.clean_browser_cache()
                if 'system_cache' in selected:
                    total_freed += self.cleaner.clean_system_cache()
                
                messagebox.showinfo("Success", 
                                  f"Cleanup completed!\nFreed: {format_size(total_freed)}")
                self.refresh_dashboard()
            except Exception as e:
                messagebox.showerror("Error", f"Cleanup failed: {str(e)}")
        
        threading.Thread(target=cleanup, daemon=True).start()
    
    def preview_clean(self):
        """Preview what would be cleaned"""
        selected = [key for key, var in self.clean_vars.items() if var.get()]
        
        if not selected:
            messagebox.showwarning("Warning", "No cleaning options selected!")
            return
        
        def preview():
            try:
                total_size = 0
                details = []
                
                if 'temp_files' in selected:
                    size = self.cleaner.clean_temp_files(dry_run=True)
                    details.append(f"Temporary files: {format_size(size)}")
                    total_size += size
                if 'browser_cache' in selected:
                    size = self.cleaner.clean_browser_cache(dry_run=True)
                    details.append(f"Browser cache: {format_size(size)}")
                    total_size += size
                
                preview_text = "\n".join(details)
                preview_text += f"\n\nTotal space to be freed: {format_size(total_size)}"
                
                messagebox.showinfo("Preview", preview_text)
            except Exception as e:
                messagebox.showerror("Error", f"Preview failed: {str(e)}")
        
        threading.Thread(target=preview, daemon=True).start()
    
    def browse_scan_path(self):
        """Browse for scan path"""
        path = filedialog.askdirectory(initialdir=self.scan_path.get())
        if path:
            self.scan_path.set(path)
    
    def start_analysis(self):
        """Start disk analysis"""
        path = self.scan_path.get()
        
        def analyze():
            try:
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, f"Analyzing {path}...\n\n")
                self.results_text.update()
                
                results = self.analyzer.scan_directory(path, 50 * 1024 * 1024)  # 50MB minimum
                
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, f"Analysis Results for {path}\n")
                self.results_text.insert(tk.END, "=" * 50 + "\n\n")
                
                for result in results[:20]:  # Show top 20 results
                    self.results_text.insert(tk.END, f"📁 {result['path']}\n")
                    self.results_text.insert(tk.END, f"   Size: {format_size(result['size'])}\n")
                    self.results_text.insert(tk.END, f"   Type: {result['type']}\n")
                    self.results_text.insert(tk.END, f"   Suggestion: {self.get_suggestion(result)}\n\n")
                
                if len(results) > 20:
                    self.results_text.insert(tk.END, f"... and {len(results) - 20} more folders\n")
                
            except Exception as e:
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, f"Analysis failed: {str(e)}")
        
        threading.Thread(target=analyze, daemon=True).start()
    
    def get_suggestion(self, folder_info):
        """Get suggestion for a folder"""
        folder_type = folder_info['type'].lower()
        size = folder_info['size']
        
        if 'cache' in folder_type:
            return "Safe to clean"
        elif 'downloads' in folder_type and size > 1024*1024*1024:
            return "Review and clean old files"
        elif size > 5*1024*1024*1024:
            return "Consider moving to another drive"
        else:
            return "Review manually"
    
    def run(self):
        """Run the GUI application"""
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        
        self.root.mainloop()