import ctypes
import os

def is_admin() -> bool:
    """Check if the current process has administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def format_size(size_bytes: int) -> str:
    """Format bytes into human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def get_available_drives():
    """Get list of available drives on Windows"""
    import win32file
    drives = []
    drive_bits = win32file.GetLogicalDrives()
    
    for i in range(26):
        mask = 1 << i
        if drive_bits & mask:
            drive_letter = chr(ord('A') + i) + ':\\'
            try:
                drive_type = win32file.GetDriveType(drive_letter)
                if drive_type == win32file.DRIVE_FIXED:
                    drives.append(drive_letter)
            except:
                continue
    
    return drives
