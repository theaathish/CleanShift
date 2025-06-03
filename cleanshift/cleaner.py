import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List
import win32api

class SystemCleaner:
    """Handles cleaning of temporary files and system caches"""
    
    def __init__(self):
        self.temp_paths = [
            os.environ.get('TEMP', ''),
            os.environ.get('TMP', ''),
            'C:\\Windows\\Temp',
            'C:\\Windows\\Prefetch',
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Temp')
        ]
        
        self.browser_cache_paths = [
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google\\Chrome\\User Data\\Default\\Cache'),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft\\Edge\\User Data\\Default\\Cache'),
            os.path.join(os.environ.get('APPDATA', ''), 'Mozilla\\Firefox\\Profiles')
        ]
    
    def clean_temp_files(self, dry_run: bool = False) -> int:
        """Clean temporary files from system temp directories"""
        total_freed = 0
        
        for temp_path in self.temp_paths:
            if not temp_path or not os.path.exists(temp_path):
                continue
            
            try:
                for item in os.listdir(temp_path):
                    item_path = os.path.join(temp_path, item)
                    try:
                        if os.path.isfile(item_path):
                            size = os.path.getsize(item_path)
                            if not dry_run:
                                os.remove(item_path)
                            total_freed += size
                        elif os.path.isdir(item_path):
                            size = self._get_directory_size(item_path)
                            if not dry_run:
                                shutil.rmtree(item_path, ignore_errors=True)
                            total_freed += size
                    except (PermissionError, OSError):
                        continue
            except (PermissionError, OSError):
                continue
        
        return total_freed
    
    def clean_browser_cache(self, dry_run: bool = False) -> int:
        """Clean browser cache files"""
        total_freed = 0
        
        for cache_path in self.browser_cache_paths:
            if not os.path.exists(cache_path):
                continue
            
            try:
                if 'Firefox' in cache_path:
                    # Handle Firefox profiles
                    for profile in os.listdir(cache_path):
                        profile_cache = os.path.join(cache_path, profile, 'cache2')
                        if os.path.exists(profile_cache):
                            size = self._get_directory_size(profile_cache)
                            if not dry_run:
                                shutil.rmtree(profile_cache, ignore_errors=True)
                            total_freed += size
                else:
                    # Handle Chrome/Edge cache
                    size = self._get_directory_size(cache_path)
                    if not dry_run:
                        shutil.rmtree(cache_path, ignore_errors=True)
                    total_freed += size
            except (PermissionError, OSError):
                continue
        
        return total_freed
    
    def clean_system_cache(self, dry_run: bool = False) -> int:
        """Clean system caches using built-in Windows tools"""
        total_freed = 0
        
        if not dry_run:
            try:
                # Run Windows Disk Cleanup
                subprocess.run(['cleanmgr', '/sagerun:1'], check=False, timeout=300)
                
                # Clear Windows Update cache
                subprocess.run(['net', 'stop', 'wuauserv'], check=False)
                subprocess.run(['net', 'stop', 'cryptSvc'], check=False)
                subprocess.run(['net', 'stop', 'bits'], check=False)
                subprocess.run(['net', 'stop', 'msiserver'], check=False)
                
                # Clear SoftwareDistribution folder
                softwaredist_path = 'C:\\Windows\\SoftwareDistribution\\Download'
                if os.path.exists(softwaredist_path):
                    total_freed += self._get_directory_size(softwaredist_path)
                    shutil.rmtree(softwaredist_path, ignore_errors=True)
                
                # Restart services
                subprocess.run(['net', 'start', 'wuauserv'], check=False)
                subprocess.run(['net', 'start', 'cryptSvc'], check=False)
                subprocess.run(['net', 'start', 'bits'], check=False)
                subprocess.run(['net', 'start', 'msiserver'], check=False)
                
            except Exception:
                pass
        else:
            # Estimate space that would be freed
            softwaredist_path = 'C:\\Windows\\SoftwareDistribution\\Download'
            if os.path.exists(softwaredist_path):
                total_freed += self._get_directory_size(softwaredist_path)
        
        return total_freed
    
    def _get_directory_size(self, path: str) -> int:
        """Calculate total size of a directory"""
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
