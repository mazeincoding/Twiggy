import yaml
import os
from pathlib import Path
from typing import List, Set

class Config:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_file = project_root / 'twiggy.yml'
    
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
    
    def create_default_config(self, custom_ignores: List[str] = None, sync_gitignore: bool = True):
        """Create default config file"""
        custom_ignores = custom_ignores or []
        
        # Load template
        template_path = Path(__file__).parent / 'templates' / 'twiggy.yml.template'
        with open(template_path, 'r') as f:
            template = f.read()
        
        # Fill in template
        config_content = template.format(
            ignore_list=self._format_ignore_list(custom_ignores),
            sync_gitignore=str(sync_gitignore).lower()
        )
        
        with open(self.config_file, 'w') as f:
            f.write(config_content)
    
    def _format_ignore_list(self, ignores: List[str]) -> str:
        """Format ignore list for YAML config"""
        if not ignores:
            return '  # - temp\n  # - src/old-stuff\n  # - docs/legacy/backup'
        
        formatted = []
        for ignore in ignores:
            formatted.append(f'  - {ignore}')
        return '\n'.join(formatted)
    
    def load(self) -> dict:
        """Load config from YAML file"""
        if not self.exists():
            return {}
        
        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f) or {}
            
            return {
                'ignores': config.get('ignore', []),
                'syncWithGitignore': config.get('syncWithGitignore', True)
            }
        except Exception:
            return {}
    
    def get_ignores(self) -> Set[str]:
        """Get all ignore patterns (default + custom + gitignore)"""
        config = self.load()
        all_ignores = set(self.get_default_ignores())
        
        # Add custom ignores
        custom_ignores = config.get('ignores', []) or []
        all_ignores.update(custom_ignores)
        
        # Add gitignore patterns if enabled
        if config.get('syncWithGitignore', True):
            gitignore_patterns = self._load_gitignore()
            all_ignores.update(gitignore_patterns)
        
        return all_ignores
    
    def _load_gitignore(self) -> Set[str]:
        """Load patterns from .gitignore"""
        gitignore_file = self.project_root / '.gitignore'
        if not gitignore_file.exists():
            return set()
        
        patterns = set()
        try:
            with open(gitignore_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Remove leading/trailing slashes and wildcards for directory matching
                        clean_pattern = line.strip('/*')
                        if clean_pattern:
                            patterns.add(clean_pattern)
        except Exception:
            pass
        
        return patterns
    
    def should_ignore(self, path: Path) -> bool:
        """Check if a path should be ignored"""
        ignores = self.get_ignores()
        
        # Get relative path from project root
        try:
            relative_path = path.relative_to(self.project_root)
            relative_path_str = str(relative_path).replace('\\', '/')  # Normalize for Windows
        except ValueError:
            # Path is not relative to project root
            relative_path_str = str(path).replace('\\', '/')
        
        for ignore in ignores:
            ignore = ignore.replace('\\', '/')  # Normalize ignore pattern
            
            # Check exact path match
            if relative_path_str == ignore:
                return True
            
            # Check if path starts with ignore pattern (for directories)
            if relative_path_str.startswith(ignore + '/'):
                return True
            
            # Check folder name match (any part of path)
            if '/' not in ignore:  # Simple folder name
                path_parts = relative_path_str.split('/')
                if ignore in path_parts:
                    return True
        
        return False
