import os
import psutil
from pathlib import Path
from typing import List, Dict
import win32api
import win32file

class DiskAnalyzer:
    """Analyzes disk usage and identifies large folders"""
    
    def __init__(self):
        self.package_patterns = {
            'node_modules': 'Node.js packages',
            '__pycache__': 'Python cache',
            '.pip': 'Python pip cache',
            '.conda': 'Conda packages',
            '.npm': 'NPM cache',
            'AppData\\Local\\Temp': 'Temporary files',
            'Downloads': 'Downloads folder',
            'Windows\\Temp': 'Windows temp files'
        }
    
    def get_drive_info(self) -> List[Dict]:
        """Get information about all available drives"""
        drives = []
        drive_bits = win32file.GetLogicalDrives()
        
        for i in range(26):
            mask = 1 << i
            if drive_bits & mask:
                drive_letter = chr(ord('A') + i) + ':\\'
                try:
                    drive_type = win32file.GetDriveType(drive_letter)
                    if drive_type == win32file.DRIVE_FIXED:  # Only fixed drives
                        usage = psutil.disk_usage(drive_letter)
                        drives.append({
                            'drive': drive_letter,
                            'total': usage.total,
                            'used': usage.used,
                            'free': usage.free,
                            'usage_percent': (usage.used / usage.total) * 100
                        })
                except:
                    continue
        
        return drives
    
    def scan_directory(self, path: str, min_size: int = 100 * 1024 * 1024) -> List[Dict]:
        """Scan directory for large folders"""
        results = []
        
        try:
            for root, dirs, files in os.walk(path):
                # Skip system-critical directories
                if self._is_system_critical(root):
                    dirs.clear()  # Don't recurse into system directories
                    continue
                
                try:
                    folder_size = self._get_folder_size(root)
                    if folder_size >= min_size:
                        folder_type = self._identify_folder_type(root)
                        results.append({
                            'path': root,
                            'size': folder_size,
                            'type': folder_type
                        })
                except (PermissionError, OSError):
                    continue
        
        except Exception as e:
            print(f"Error scanning {path}: {e}")
        
        return sorted(results, key=lambda x: x['size'], reverse=True)
    
    def _get_folder_size(self, path: str) -> int:
        """Calculate total size of a folder"""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    try:
                        total_size += os.path.getsize(filepath)
                    except (OSError, FileNotFoundError):
                        continue
        except (PermissionError, OSError):
            pass
        
        return total_size
    
    def _identify_folder_type(self, path: str) -> str:
        """Identify the type of folder based on path patterns"""
        path_lower = path.lower()
        
        for pattern, folder_type in self.package_patterns.items():
            if pattern.lower() in path_lower:
                return folder_type
        
        return "General folder"
    
    def _is_system_critical(self, path: str) -> bool:
        """Check if path is system-critical and should be avoided"""
        critical_paths = [
            'c:\\windows\\system32',
            'c:\\windows\\syswow64',
            'c:\\program files\\windows',
            'c:\\programdata\\microsoft\\windows',
            'c:\\users\\all users'
        ]
        
        path_lower = path.lower()
        return any(critical in path_lower for critical in critical_paths)
