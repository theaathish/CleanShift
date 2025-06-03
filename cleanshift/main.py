import click
import sys
import os
import platform
from rich.console import Console
from rich.table import Table

# Fix imports for PyInstaller standalone executable
def import_modules():
    """Import modules with proper fallback for different execution contexts"""
    global DiskAnalyzer, SystemCleaner, PackageMover, is_admin, format_size
    
    # Try different import strategies
    import_error = None
    
    # Strategy 1: Relative imports (when run as package)
    try:
        from .analyzer import DiskAnalyzer
        from .cleaner import SystemCleaner
        from .mover import PackageMover
        from .utils import is_admin, format_size
        return
    except ImportError as e:
        import_error = e
    
    # Strategy 2: Direct imports (when run as script or standalone)
    try:
        # Add current directory to path for standalone builds
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
            
        from analyzer import DiskAnalyzer
        from cleaner import SystemCleaner
        from mover import PackageMover
        from utils import is_admin, format_size
        return
    except ImportError:
        pass
    
    # Strategy 3: Try parent directory (PyInstaller context)
    try:
        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cleanshift_dir = os.path.join(parent_dir, 'cleanshift')
        if cleanshift_dir not in sys.path:
            sys.path.insert(0, cleanshift_dir)
            
        from analyzer import DiskAnalyzer
        from cleaner import SystemCleaner
        from mover import PackageMover
        from utils import is_admin, format_size
        return
    except ImportError:
        pass
    
    # Strategy 4: Inline fallback implementations
    try:
        # Create minimal fallback implementations
        import psutil
        import ctypes
        
        class DiskAnalyzer:
            def get_drive_info(self):
                drives = []
                for drive in psutil.disk_partitions():
                    if drive.fstype:
                        try:
                            usage = psutil.disk_usage(drive.mountpoint)
                            drives.append({
                                'drive': drive.device,
                                'total': usage.total,
                                'used': usage.used,
                                'free': usage.free,
                                'usage_percent': (usage.used / usage.total) * 100
                            })
                        except:
                            continue
                return drives
            
            def scan_directory(self, path, min_size):
                return []  # Minimal implementation
        
        class SystemCleaner:
            def clean_temp_files(self, dry_run=False): return 0
            def clean_browser_cache(self, dry_run=False): return 0
            def clean_system_cache(self, dry_run=False): return 0
        
        class PackageMover:
            def move_with_symlink(self, source, target, dry_run=False): return False
        
        def is_admin():
            try:
                return ctypes.windll.shell32.IsUserAnAdmin() if platform.system() == "Windows" else False
            except:
                return False
        
        def format_size(size_bytes):
            if size_bytes == 0: return "0 B"
            size_names = ["B", "KB", "MB", "GB", "TB"]
            i = 0
            while size_bytes >= 1024 and i < len(size_names) - 1:
                size_bytes /= 1024.0
                i += 1
            return f"{size_bytes:.1f} {size_names[i]}"
        
        return
    except ImportError:
        pass
    
    # If all strategies fail, raise the original error
    raise ImportError(f"Could not import required modules. Original error: {import_error}")

# Import modules on startup
import_modules()

console = Console()

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """CleanShift - Clean and shift C drive content to free up space"""
    if platform.system() == "Windows" and not is_admin():
        console.print("[red]Warning: Running without administrator privileges. Some operations may fail.[/red]")
    elif platform.system() != "Windows":
        console.print("[yellow]This tool is designed for Windows systems.[/yellow]")

@cli.command()
@click.option('--path', default='C:\\', help='Path to analyze (default: C:\\)')
@click.option('--min-size', default=100, help='Minimum size in MB to report (default: 100)')
def analyze(path, min_size):
    """Analyze disk usage and identify large folders"""
    console.print(f"[blue]Analyzing disk usage for {path}...[/blue]")
    
    analyzer = DiskAnalyzer()
    results = analyzer.scan_directory(path, min_size * 1024 * 1024)
    
    table = Table(title="Large Folders Found")
    table.add_column("Path", style="cyan")
    table.add_column("Size", style="green")
    table.add_column("Type", style="yellow")
    
    for result in results:
        table.add_row(result['path'], format_size(result['size']), result['type'])
    
    console.print(table)

@cli.command()
@click.option('--dry-run', is_flag=True, help='Show what would be cleaned without performing actions')
@click.option('--temp-files', is_flag=True, help='Clean temporary files')
@click.option('--browser-cache', is_flag=True, help='Clean browser caches')
@click.option('--system-cache', is_flag=True, help='Clean system caches')
def clean(dry_run, temp_files, browser_cache, system_cache):
    """Clean unnecessary files from the system"""
    cleaner = SystemCleaner()
    
    if dry_run:
        console.print("[yellow]DRY RUN MODE - No files will be deleted[/yellow]")
    
    total_freed = 0
    
    if temp_files:
        freed = cleaner.clean_temp_files(dry_run)
        total_freed += freed
        console.print(f"[green]Temp files: {format_size(freed)} freed[/green]")
    
    if browser_cache:
        freed = cleaner.clean_browser_cache(dry_run)
        total_freed += freed
        console.print(f"[green]Browser cache: {format_size(freed)} freed[/green]")
    
    if system_cache:
        freed = cleaner.clean_system_cache(dry_run)
        total_freed += freed
        console.print(f"[green]System cache: {format_size(freed)} freed[/green]")
    
    console.print(f"[bold green]Total space freed: {format_size(total_freed)}[/bold green]")

@cli.command()
@click.option('--source', required=True, help='Source directory to move')
@click.option('--target-drive', required=True, help='Target drive letter (e.g., D:)')
@click.option('--dry-run', is_flag=True, help='Show what would be moved without performing actions')
@click.option('--confirm', is_flag=True, help='Skip confirmation prompts')
def move(source, target_drive, dry_run, confirm):
    """Move packages/folders to another drive with symbolic links"""
    if not dry_run and not confirm:
        console.print(f"[yellow]About to move {source} to {target_drive}[/yellow]")
        if not click.confirm("Do you want to continue?"):
            console.print("[red]Operation cancelled[/red]")
            return
    
    mover = PackageMover()
    
    if dry_run:
        console.print("[yellow]DRY RUN MODE - No files will be moved[/yellow]")
    
    success = mover.move_with_symlink(source, target_drive, dry_run)
    
    if success:
        console.print(f"[green]Successfully moved {source} to {target_drive}[/green]")
    else:
        console.print(f"[red]Failed to move {source}[/red]")

@cli.command()
def status():
    """Show disk space status for all drives"""
    analyzer = DiskAnalyzer()
    drives = analyzer.get_drive_info()
    
    table = Table(title="Drive Status")
    table.add_column("Drive", style="cyan")
    table.add_column("Total", style="blue")
    table.add_column("Used", style="red")
    table.add_column("Free", style="green")
    table.add_column("Usage %", style="yellow")
    
    for drive in drives:
        usage_percent = f"{drive['usage_percent']:.1f}%"
        table.add_row(
            drive['drive'],
            format_size(drive['total']),
            format_size(drive['used']),
            format_size(drive['free']),
            usage_percent
        )
    
    console.print(table)

@cli.command()
def install():
    """Install CleanShift to system PATH"""
    if platform.system() != "Windows":
        console.print("[red]Install command is only available on Windows[/red]")
        console.print("[yellow]Download the Windows executable from: https://github.com/theaathish/CleanShift/releases/latest[/yellow]")
        return
    
    try:
        import shutil
        import winreg
        
        # Get current executable path
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            console.print("[red]This command only works with the compiled executable[/red]")
            console.print("[yellow]Download the Windows executable from: https://github.com/theaathish/CleanShift/releases/latest[/yellow]")
            return
        
        # Check if already installed
        install_dir = "C:\\Program Files\\CleanShift"
        target_path = os.path.join(install_dir, "cleanshift.exe")
        
        if os.path.exists(target_path):
            console.print("[yellow]CleanShift is already installed. Updating...[/yellow]")
        
        # Install to Program Files
        os.makedirs(install_dir, exist_ok=True)
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
                
                if install_dir not in path_value:
                    new_path = path_value + ";" + install_dir if path_value else install_dir
                    winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
                    console.print("[green]Added CleanShift to system PATH[/green]")
        except PermissionError:
            console.print("[yellow]Could not modify system PATH. You may need to add it manually:[/yellow]")
            console.print(f"[cyan]{install_dir}[/cyan]")
        
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
            console.print("[green]Created desktop shortcut[/green]")
        except ImportError:
            console.print("[yellow]Desktop shortcut creation skipped (pywin32 not available)[/yellow]")
        except Exception:
            pass  # Desktop shortcut is optional
        
        console.print(f"[green]CleanShift installed successfully to {install_dir}[/green]")
        console.print("[yellow]Please restart your command prompt to use 'cleanshift' command globally[/yellow]")
        console.print("\n[cyan]Quick start:[/cyan]")
        console.print("  cleanshift status       - Check drive space")
        console.print("  cleanshift analyze      - Find large folders")
        console.print("  cleanshift clean --help - See cleanup options")
        
    except Exception as e:
        console.print(f"[red]Installation failed: {e}[/red]")
        console.print("[yellow]Make sure you're running as administrator[/yellow]")

@cli.command()
def uninstall():
    """Uninstall CleanShift from system"""
    if platform.system() != "Windows":
        console.print("[red]Uninstall command is only available on Windows[/red]")
        return
    
    try:
        import winreg
        import shutil
        
        install_dir = "C:\\Program Files\\CleanShift"
        
        if not os.path.exists(install_dir):
            console.print("[yellow]CleanShift is not installed[/yellow]")
            return
        
        # Confirm uninstall
        if not click.confirm("Are you sure you want to uninstall CleanShift?"):
            console.print("[yellow]Uninstall cancelled[/yellow]")
            return
        
        # Remove from PATH
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               "SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment",
                               0, winreg.KEY_ALL_ACCESS) as key:
                path_value, _ = winreg.QueryValueEx(key, "PATH")
                if install_dir in path_value:
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
        
        console.print("[green]CleanShift uninstalled successfully[/green]")
        
    except Exception as e:
        console.print(f"[red]Uninstall failed: {e}[/red]")

@cli.command()
def gui():
    """Launch the graphical user interface"""
    try:
        from .gui import CleanShiftGUI
        app = CleanShiftGUI()
        app.run()
    except ImportError as e:
        console.print(f"[red]GUI not available: {e}[/red]")
        console.print("[yellow]Install GUI dependencies with: pip install pillow[/yellow]")

if __name__ == '__main__':
    cli()
