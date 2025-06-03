import click
import sys
import os
from rich.console import Console
from rich.table import Table
from .analyzer import DiskAnalyzer
from .cleaner import SystemCleaner
from .mover import PackageMover
from .utils import is_admin, format_size

console = Console()

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """CleanShift - Clean and shift C drive content to free up space"""
    if not is_admin():
        console.print("[red]Warning: Running without administrator privileges. Some operations may fail.[/red]")

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
    import shutil
    import winreg
    
    try:
        # Get current executable path
        if getattr(sys, 'frozen', False):
            exe_path = sys.executable
        else:
            console.print("[red]This command only works with the compiled executable[/red]")
            return
        
        # Install to Program Files
        install_dir = "C:\\Program Files\\CleanShift"
        os.makedirs(install_dir, exist_ok=True)
        
        target_path = os.path.join(install_dir, "cleanshift.exe")
        shutil.copy2(exe_path, target_path)
        
        # Add to PATH
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                           "SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment",
                           0, winreg.KEY_ALL_ACCESS) as key:
            path_value, _ = winreg.QueryValueEx(key, "PATH")
            if install_dir not in path_value:
                new_path = path_value + ";" + install_dir
                winreg.SetValueEx(key, "PATH", 0, winreg.REG_EXPAND_SZ, new_path)
        
        console.print(f"[green]CleanShift installed successfully to {install_dir}[/green]")
        console.print("[yellow]Please restart your command prompt or reboot to use 'cleanshift' command globally[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Installation failed: {e}[/red]")
        console.print("[yellow]Try running as administrator[/yellow]")

if __name__ == '__main__':
    cli()
