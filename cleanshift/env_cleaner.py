import os
import shutil
from pathlib import Path
from typing import List, Dict
import subprocess

class EnvironmentCleaner:
    """Handles cleaning of development environments"""
    
    def __init__(self):
        self.environments = {
            'node_modules': {
                'type': 'Node.js',
                'patterns': ['node_modules'],
                'description': 'Node.js package cache',
                'command': 'npm cache clean --force'
            },
            'python_cache': {
                'type': 'Python',
                'patterns': ['__pycache__', '.pyc'],
                'description': 'Python bytecode cache',
                'command': None
            },
            'pip_cache': {
                'type': 'Python',
                'patterns': ['.pip', 'pip-cache'],
                'description': 'Pip package cache',
                'command': 'pip cache purge'
            },
            'conda_env': {
                'type': 'Conda',
                'patterns': ['miniconda', 'anaconda', '.conda'],
                'description': 'Conda environments',
                'command': 'conda clean --all'
            },
            'npm_cache': {
                'type': 'NPM',
                'patterns': ['.npm'],
                'description': 'NPM cache directory',
                'command': 'npm cache clean --force'
            },
            'gradle_cache': {
                'type': 'Gradle',
                'patterns': ['.gradle'],
                'description': 'Gradle build cache',
                'command': None
            },
            'maven_cache': {
                'type': 'Maven',
                'patterns': ['.m2'],
                'description': 'Maven repository cache',
                'command': None
            }
        }
    
    def find_environments(self) -> List[Dict]:
        """Find all development environments on the system"""
        found_envs = []
        search_paths = [
            os.path.expanduser("~"),
            "C:\\",
            os.path.join(os.path.expanduser("~"), "AppData", "Local"),
            os.path.join(os.path.expanduser("~"), "AppData", "Roaming")
        ]
        
        for search_path in search_paths:
            if not os.path.exists(search_path):
                continue
                
            try:
                found_envs.extend(self._scan_directory(search_path))
            except (PermissionError, OSError):
                continue
        
        return sorted(found_envs, key=lambda x: x['size'], reverse=True)
    
    def _scan_directory(self, path: str, max_depth: int = 3) -> List[Dict]:
        """Scan directory for environment patterns"""
        found = []
        
        try:
            for root, dirs, files in os.walk(path):
                # Limit depth to avoid deep recursion
                depth = root[len(path):].count(os.sep)
                if depth > max_depth:
                    dirs.clear()
                    continue
                
                # Check each environment type
                for env_key, env_info in self.environments.items():
                    for pattern in env_info['patterns']:
                        if pattern in root.lower() or any(pattern in d.lower() for d in dirs):
                            try:
                                size = self._get_directory_size(root)
                                if size > 50 * 1024 * 1024:  # Only report if > 50MB
                                    found.append({
                                        'name': os.path.basename(root),
                                        'type': env_info['type'],
                                        'path': root,
                                        'size': size,
                                        'description': env_info['description'],
                                        'command': env_info['command'],
                                        'env_key': env_key
                                    })
                            except (PermissionError, OSError):
                                continue
        except (PermissionError, OSError):
            pass
        
        return found
    
    def clean_environment(self, env_info: Dict, dry_run: bool = False) -> int:
        """Clean a specific environment"""
        try:
            path = env_info['path']
            command = env_info.get('command')
            
            if dry_run:
                return env_info['size']
            
            # Try command-based cleanup first
            if command:
                try:
                    subprocess.run(command.split(), 
                                 capture_output=True, 
                                 timeout=60, 
                                 cwd=os.path.dirname(path))
                except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                    pass  # Fall back to manual deletion
            
            # Manual deletion
            if os.path.exists(path):
                size = self._get_directory_size(path)
                shutil.rmtree(path, ignore_errors=True)
                return size
            
            return 0
            
        except Exception:
            return 0
    
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
    
    def get_environment_suggestions(self, environments: List[Dict]) -> List[Dict]:
        """Get cleanup suggestions for environments"""
        suggestions = []
        
        # Group by type
        env_by_type = {}
        for env in environments:
            env_type = env['type']
            if env_type not in env_by_type:
                env_by_type[env_type] = []
            env_by_type[env_type].append(env)
        
        # Generate suggestions
        for env_type, envs in env_by_type.items():
            total_size = sum(env['size'] for env in envs)
            count = len(envs)
            
            if total_size > 1024 * 1024 * 1024:  # > 1GB
                priority = 'high'
            elif total_size > 500 * 1024 * 1024:  # > 500MB
                priority = 'medium'
            else:
                priority = 'low'
            
            suggestions.append({
                'type': env_type,
                'count': count,
                'total_size': total_size,
                'priority': priority,
                'suggestion': f"Clean {count} {env_type} environments to free {self._format_size(total_size)}"
            })
        
        return sorted(suggestions, key=lambda x: x['total_size'], reverse=True)
    
    def _format_size(self, size_bytes: int) -> str:
        """Format bytes into human readable format"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
