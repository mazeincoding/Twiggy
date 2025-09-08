import yaml
import os
from pathlib import Path
from typing import List, Set

class Config:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_file = project_root / 'twiggy.yml'
    
    def get_default_ignores(self) -> Set[str]:
        return {
            'node_modules', '.next', '.nuxt', 'dist', 'build', '.output', '.vercel', '.netlify', 'out', '.cache',
            '.parcel-cache', '.webpack', 'coverage', '.nyc_output', '.jest',
            '__pycache__', '.pytest_cache', '.mypy_cache', '.tox', 'venv', 'env', '.venv', '.env', 'site-packages',
            '.coverage', 'htmlcov', '*.egg-info', '.eggs',
            'target', 'Cargo.lock', 'vendor', '.gradle', '.idea', '.vs', 'cmake-build-debug', 'cmake-build-release',
            '.bundle', '.vscode', '.vscode-test', '.git', '.svn', '.hg', '.bzr', '.DS_Store', 'Thumbs.db', '.Trash',
            'logs', 'log', 'tmp', 'temp', '.tmp', '.temp', '_site', '.docusaurus', 'public', 'docs/_build',
            'ios/build', 'android/build', '.expo', '*.db', '*.sqlite', '*.sqlite3', '.docker', '.terraform',
            '.serverless', '.yarn', '.pnpm-store', '.rush', '.playwright', 'cypress/videos', 'cypress/screenshots',
            'test-results', '.sass-cache', '.postcssrc', '.eslintcache', '.stylelintcache', '.github', '.husky'
        }
    
    def exists(self) -> bool:
        return self.config_file.exists()
    
    def create_default_config(self, custom_ignores: List[str] = None, sync_gitignore: bool = True, format_type: str = 'xml'):
        custom_ignores = custom_ignores or []
        
        template_path = Path(__file__).parent / 'templates' / 'twiggy.yml.template'
        with open(template_path, 'r') as f:
            template = f.read()
        
        config_content = template.format(
            ignore_list=self._format_ignore_list(custom_ignores),
            sync_gitignore=str(sync_gitignore).lower(),
            format=format_type
        )
        
        with open(self.config_file, 'w') as f:
            f.write(config_content)
    
    def _format_ignore_list(self, ignores: List[str]) -> str:
        if not ignores:
            return '  # - temp\n  # - src/old-stuff\n  # - docs/legacy/backup'
        
        return '\n'.join(f'  - {ignore}' for ignore in ignores)
    
    def load(self) -> dict:
        if not self.exists():
            return {}
        
        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f) or {}
            
            return {
                'ignores': config.get('ignore', []),
                'syncWithGitignore': config.get('syncWithGitignore', True),
                'format': config.get('format', 'xml')
            }
        except Exception:
            return {}
    
    def get_ignores(self) -> Set[str]:
        config = self.load()
        all_ignores = set(self.get_default_ignores())
        
        custom_ignores = config.get('ignores', []) or []
        all_ignores.update(custom_ignores)
        
        if config.get('syncWithGitignore', True):
            gitignore_patterns = self._load_gitignore()
            all_ignores.update(gitignore_patterns)
        
        all_ignores.add('.cursor/rules/file-structure.mdc')
        
        return all_ignores
    
    def _load_gitignore(self) -> Set[str]:
        gitignore_file = self.project_root / '.gitignore'
        if not gitignore_file.exists():
            return set()
        
        patterns = set()
        try:
            with open(gitignore_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        clean_pattern = line.strip('/*')
                        if clean_pattern:
                            patterns.add(clean_pattern)
        except Exception:
            pass
        
        return patterns
    
    def should_ignore(self, path: Path) -> bool:
        ignores = self.get_ignores()
        
        try:
            relative_path = path.relative_to(self.project_root)
            relative_path_str = str(relative_path).replace('\\', '/')
        except ValueError:
            relative_path_str = str(path).replace('\\', '/')
        
        for ignore in ignores:
            ignore = ignore.replace('\\', '/')
            
            if relative_path_str == ignore:
                return True
            
            if relative_path_str.startswith(ignore + '/'):
                return True
            
            if '/' not in ignore:
                path_parts = relative_path_str.split('/')
                if ignore in path_parts:
                    return True
        
        return False
