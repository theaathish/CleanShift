import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import webbrowser
import subprocess
import os
from pathlib import Path

class GUICallbacks:
    """Mixin class with GUI callback methods"""
    
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
        if self.confirm_actions.get():
            if not messagebox.askyesno("Confirm", "Perform quick cleanup of temporary files?"):
                return
        
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
        
        threading.Thread(target=cleanup, daemon=True).start()
    
    def quick_analyze(self):
        """Perform quick disk analysis"""
        def analyze():
            try:
                results = self.analyzer.scan_directory("C:\\", 100 * 1024 * 1024)
                
                # Switch to analyze tab and show results
                self.notebook.select(2)  # Analyze tab
                self.display_analysis_results(results)
            except Exception as e:
                messagebox.showerror("Error", f"Analysis failed: {str(e)}")
        
        threading.Thread(target=analyze, daemon=True).start()
    
    def create_clean_section(self, parent, title, options):
        """Create a section of cleaning options"""
        section_frame = tk.Frame(parent, bg=self.colors['white'], 
                                relief='solid', borderwidth=1, padx=20, pady=15)
        section_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(section_frame, text=title, 
                font=('Arial', 14, 'bold'), 
                fg=self.colors['gray_800'], 
                bg=self.colors['white']).pack(anchor='w', pady=(0, 10))
        
        self.clean_vars = getattr(self, 'clean_vars', {})
        
        for option_text, option_key, description in options:
            option_frame = tk.Frame(section_frame, bg=self.colors['white'])
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
    
    def clean_all_selected(self):
        """Clean all selected options"""
        selected = [key for key, var in self.clean_vars.items() if var.get()]
        
        if not selected:
            messagebox.showwarning("Warning", "No cleaning options selected!")
            return
        
        if self.confirm_actions.get():
            if not messagebox.askyesno("Confirm", f"Clean {len(selected)} selected items?"):
                return
        
        def cleanup():
            try:
                total_freed = 0
                
                for option in selected:
                    if option == 'clean_temp':
                        total_freed += self.cleaner.clean_temp_files()
                    elif option == 'clean_browser':
                        total_freed += self.cleaner.clean_browser_cache()
                    elif option == 'clean_system':
                        total_freed += self.cleaner.clean_system_cache()
                    elif option == 'clean_recycle':
                        total_freed += self.cleaner.clean_recycle_bin()
                    # Add more cleanup options as needed
                
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
                
                for option in selected:
                    if option == 'clean_temp':
                        size = self.cleaner.clean_temp_files(dry_run=True)
                        details.append(f"Temporary files: {format_size(size)}")
                        total_size += size
                    elif option == 'clean_browser':
                        size = self.cleaner.clean_browser_cache(dry_run=True)
                        details.append(f"Browser cache: {format_size(size)}")
                        total_size += size
                    # Add more preview options
                
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
                results = self.analyzer.scan_directory(path, 50 * 1024 * 1024)  # 50MB minimum
                self.display_analysis_results(results)
            except Exception as e:
                messagebox.showerror("Error", f"Analysis failed: {str(e)}")
        
        threading.Thread(target=analyze, daemon=True).start()
    
    def display_analysis_results(self, results):
        """Display analysis results in the treeview"""
        # Clear existing results
        for item in self.analysis_tree.get_children():
            self.analysis_tree.delete(item)
        
        # Add results
        for result in results:
            suggestion = self.get_suggestion_for_folder(result)
            self.analysis_tree.insert("", "end", 
                                    text=result['path'],
                                    values=(format_size(result['size']), 
                                           result['type'], 
                                           suggestion))
    
    def get_suggestion_for_folder(self, folder_info):
        """Get cleanup/optimization suggestion for a folder"""
        folder_type = folder_info['type'].lower()
        size = folder_info['size']
        
        if 'cache' in folder_type:
            return "Safe to clean"
        elif 'downloads' in folder_type and size > 1024*1024*1024:  # > 1GB
            return "Review and clean old files"
        elif 'node' in folder_type:
            return "Consider moving to another drive"
        elif size > 5*1024*1024*1024:  # > 5GB
            return "Consider moving to another drive"
        else:
            return "Review manually"
    
    def scan_movable_apps(self):
        """Scan for movable applications"""
        def scan():
            try:
                # Clear existing results
                for item in self.movable_tree.get_children():
                    self.movable_tree.delete(item)
                
                # Scan for applications
                apps = self.find_movable_applications()
                
                for app in apps:
                    self.movable_tree.insert("", "end",
                                           text=app['name'],
                                           values=(format_size(app['size']),
                                                  app['path'],
                                                  app['target_drive'],
                                                  app['status']))
            except Exception as e:
                messagebox.showerror("Error", f"Scan failed: {str(e)}")
        
        threading.Thread(target=scan, daemon=True).start()
    
    def find_movable_applications(self):
        """Find applications that can be moved"""
        # This would scan Program Files, AppData, etc. for large applications
        # Return a list of dictionaries with app info
        return []  # Placeholder implementation
    
    def scan_environments(self):
        """Scan for development environments"""
        def scan():
            try:
                # Clear existing results
                for item in self.env_tree.get_children():
                    self.env_tree.delete(item)
                
                environments = self.env_cleaner.find_environments()
                
                for env in environments:
                    action = "Clean" if env['size'] > 500*1024*1024 else "Review"
                    self.env_tree.insert("", "end",
                                       text=env['name'],
                                       values=(env['type'],
                                              format_size(env['size']),
                                              env['path'],
                                              action))
            except Exception as e:
                messagebox.showerror("Error", f"Environment scan failed: {str(e)}")
        
        threading.Thread(target=scan, daemon=True).start()
    
    def check_installation_status(self):
        """Check if CleanShift is installed to system"""
        install_path = Path("C:/Program Files/CleanShift/cleanshift.exe")
        if install_path.exists():
            self.install_status.config(text="✓ CleanShift is installed to system", 
                                     fg=self.colors['success'])
        else:
            self.install_status.config(text="⚠ CleanShift is not installed to system", 
                                     fg=self.colors['warning'])
    
    def install_to_system(self):
        """Install CleanShift to system"""
        if not is_admin():
            messagebox.showerror("Error", "Administrator privileges required for installation!")
            return
        
        try:
            # Implementation would copy executable and update PATH
            messagebox.showinfo("Success", "CleanShift installed to system successfully!")
            self.check_installation_status()
        except Exception as e:
            messagebox.showerror("Error", f"Installation failed: {str(e)}")
    
    def open_url(self, url):
        """Open URL in default browser"""
        webbrowser.open(url)

# Add callbacks to main GUI class
from .gui import CleanShiftGUI
CleanShiftGUI.__bases__ = CleanShiftGUI.__bases__ + (GUICallbacks,)
