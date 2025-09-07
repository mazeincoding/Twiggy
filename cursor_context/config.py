import json
import os
from pathlib import Path
from typing import List, Set

class Config:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_file = project_root / '.cursor' / 'cursor-context.json'
    
    def get_default_ignores(self) -> Set[str]:
        """Get comprehensive list of commonly ignored directories"""
        return {
            # Node.js / JavaScript / TypeScript
            'node_modules',
            '.next',
            '.nuxt',
            'dist',
            'build',
            '.output',
            '.vercel',
            '.netlify',
            'out',
            '.cache',
            '.parcel-cache',
            '.webpack',
            'coverage',
            '.nyc_output',
            '.jest',
            
            # Python
            '__pycache__',
            '.pytest_cache',
            '.mypy_cache',
            '.tox',
            'venv',
            'env',
            '.venv',
            '.env',
            'site-packages',
            '.coverage',
            'htmlcov',
            'build',
            'dist',
            '*.egg-info',
            '.eggs',
            
            # Rust
            'target',
            'Cargo.lock',
            
            # Go
            'vendor',
            
            # Java / Kotlin / Scala
            'target',
            'build',
            '.gradle',
            '.idea',
            'out',
            
            # C/C++
            'build',
            'cmake-build-debug',
            'cmake-build-release',
            '.vs',
            
            # Ruby
            '.bundle',
            'vendor',
            
            # PHP
            'vendor',
            
            # General IDE/Editor
            '.vscode',
            '.idea',
            '.vs',
            '.vscode-test',
            
            # Version control
            '.git',
            '.svn',
            '.hg',
            '.bzr',
            
            # OS
            '.DS_Store',
            'Thumbs.db',
            '.Trash',
            
            # Logs and temp
            'logs',
            'log',
            'tmp',
            'temp',
            '.tmp',
            '.temp',
            
            # Documentation builds
            '_site',
            '.docusaurus',
            'public',
            'docs/_build',
            
            # Mobile development
            'ios/build',
            'android/build',
            '.expo',
            '.gradle',
            
            # Database
            '*.db',
            '*.sqlite',
            '*.sqlite3',
            
            # Docker
            '.docker',
            
            # Cloud/Deploy
            '.terraform',
            '.serverless',
            
            # Package managers
            '.yarn',
            '.pnpm-store',
            '.rush',
            
            # Testing
            '.playwright',
            'cypress/videos',
            'cypress/screenshots',
            'test-results',
            
            # Misc
            '.sass-cache',
            '.postcssrc',
            '.eslintcache',
            '.stylelintcache'
        }
    
    def exists(self) -> bool:
        """Check if config file exists"""
        return self.config_file.exists()
    
    def load(self) -> dict:
        """Load config from file"""
        if not self.exists():
            return {}
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {}
    
    def save_ignores(self, ignores: List[str]):
        """Save ignore patterns to config"""
        config = self.load()
        config['ignores'] = ignores
        
        # Ensure .cursor directory exists
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get_ignores(self) -> Set[str]:
        """Get all ignore patterns (default + custom)"""
        config = self.load()
        return set(config.get('ignores', []))
    
    def should_ignore(self, path: Path) -> bool:
        """Check if a path should be ignored"""
        ignores = self.get_ignores()
        
        # Check if any part of the path matches ignore patterns
        path_parts = path.parts
        for ignore in ignores:
            if ignore in path_parts:
                return True
            # Also check exact path matches
            if path.name == ignore:
                return True
        
        return False
