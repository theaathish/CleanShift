import sys
import os
import platform
import tkinter as tk
from tkinter import messagebox

def setup_imports():
    """Setup imports for standalone executable"""
    global DiskAnalyzer, SystemCleaner, PackageMover, EnvironmentCleaner, is_admin, format_size
    
    # Add current directory to path for standalone builds
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        bundle_dir = sys._MEIPASS
    else:
        # Running as script
        bundle_dir = os.path.dirname(os.path.abspath(__file__))
    
    if bundle_dir not in sys.path:
        sys.path.insert(0, bundle_dir)
    
    try:
        # Import modules directly for standalone
        from analyzer import DiskAnalyzer
        from cleaner import SystemCleaner
        from mover import PackageMover
        from env_cleaner import EnvironmentCleaner
        from utils import is_admin, format_size
        return True
    except ImportError:
        try:
            # Fallback with relative imports
            from .analyzer import DiskAnalyzer
            from .cleaner import SystemCleaner
            from .mover import PackageMover
            from .env_cleaner import EnvironmentCleaner
            from .utils import is_admin, format_size
            return True
        except ImportError:
            return False

def create_gui():
    """Create and run the GUI application"""
    if not setup_imports():
        # Show error dialog if imports fail
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", "Failed to initialize CleanShift components.\nPlease contact support.")
        return
    
    # Import GUI after successful component import
    try:
        from gui_app import CleanShiftGUI
        app = CleanShiftGUI()
        app.run()
    except ImportError as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", f"GUI components not found: {e}")

def main():
    """Main entry point for GUI-only application"""
    if platform.system() != "Windows":
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning("Platform Warning", "CleanShift is designed for Windows systems.")
        root.destroy()
        return
    
    create_gui()

if __name__ == '__main__':
    main()
