import os
import shutil
import subprocess
from pathlib import Path

class PackageMover:
    """Handles moving packages/folders to other drives with symbolic links"""
    
    def move_with_symlink(self, source_path: str, target_drive: str, dry_run: bool = False) -> bool:
        """Move a folder to target drive and create symbolic link"""
        try:
            source = Path(source_path)
            if not source.exists():
                print(f"Source path does not exist: {source_path}")
                return False
            
            # Create target path
            target_base = Path(target_drive) / "CleanShift_Moved"
            target_path = target_base / source.name
            
            if dry_run:
                print(f"Would move: {source} -> {target_path}")
                print(f"Would create symlink: {source} -> {target_path}")
                return True
            
            # Create target directory if it doesn't exist
            target_base.mkdir(exist_ok=True)
            
            # Move the folder
            if target_path.exists():
                print(f"Target already exists: {target_path}")
                return False
            
            shutil.move(str(source), str(target_path))
            
            # Create symbolic link
            self._create_symlink(str(target_path), str(source))
            
            return True
            
        except Exception as e:
            print(f"Error moving {source_path}: {e}")
            return False
    
    def _create_symlink(self, target: str, link: str) -> bool:
        """Create a symbolic link using mklink command"""
        try:
            cmd = ['mklink', '/D', link, target]
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            print(f"Error creating symlink: {e}")
            return False
    
    def restore_symlink(self, symlink_path: str, dry_run: bool = False) -> bool:
        """Restore a moved folder by removing symlink and moving back"""
        try:
            link = Path(symlink_path)
            if not link.is_symlink():
                print(f"Path is not a symbolic link: {symlink_path}")
                return False
            
            # Get target path
            target = link.resolve()
            
            if dry_run:
                print(f"Would restore: {target} -> {link}")
                return True
            
            # Remove symlink
            link.unlink()
            
            # Move folder back
            shutil.move(str(target), str(link))
            
            return True
            
        except Exception as e:
            print(f"Error restoring {symlink_path}: {e}")
            return False
