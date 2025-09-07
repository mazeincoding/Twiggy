import os
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime
from .config import Config

class DirectoryScanner:
    def __init__(self, config: Config):
        self.config = config
        self.project_root = config.project_root
        self.output_file = self.project_root / '.cursor' / 'rules' / 'file-structure.mdc'
    
    def scan_directory(self) -> Dict:
        """Scan directory structure and return organized data"""
        structure = {
            'directories': [],
            'files': [],
            'total_dirs': 0,
            'total_files': 0
        }
        
        def scan_recursive(path: Path, level: int = 0) -> List[Dict]:
            items = []
            
            try:
                # Get all items in current directory
                all_items = list(path.iterdir())
                
                # Separate directories and files
                directories = [item for item in all_items if item.is_dir() and not self.config.should_ignore(item)]
                files = [item for item in all_items if item.is_file() and not item.name.startswith('.')]
                
                # Sort both lists
                directories.sort(key=lambda x: x.name.lower())
                files.sort(key=lambda x: x.name.lower())
                
                # Process directories first
                for directory in directories:
                    relative_path = directory.relative_to(self.project_root)
                    
                    dir_info = {
                        'type': 'directory',
                        'name': directory.name,
                        'path': str(relative_path),
                        'level': level,
                        'children': scan_recursive(directory, level + 1)
                    }
                    
                    items.append(dir_info)
                    structure['total_dirs'] += 1
                
                # Process files
                for file in files:
                    relative_path = file.relative_to(self.project_root)
                    
                    file_info = {
                        'type': 'file',
                        'name': file.name,
                        'path': str(relative_path),
                        'level': level,
                        'extension': file.suffix.lower() if file.suffix else None
                    }
                    
                    items.append(file_info)
                    structure['total_files'] += 1
            
            except PermissionError:
                # Skip directories we can't access
                pass
            
            return items
        
        structure['items'] = scan_recursive(self.project_root)
        return structure
    
    def generate_tree_structure(self, items: List[Dict], level: int = 0) -> str:
        """Generate a clean tree-like structure"""
        lines = []
        
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            
            # Create the tree prefix
            if level == 0:
                prefix = ""
            else:
                prefix = "  " * (level - 1)
                if is_last:
                    prefix += "└── "
                else:
                    prefix += "├── "
            
            # Add the item
            if item['type'] == 'directory':
                lines.append(f"{prefix}{item['name']}/")
                # Add children
                if item.get('children'):
                    child_lines = self.generate_tree_structure(item['children'], level + 1)
                    lines.extend(child_lines)
            else:
                lines.append(f"{prefix}{item['name']}")
        
        return lines
    
    def generate_flat_structure(self, items: List[Dict], current_path: str = "") -> List[str]:
        """Generate a flat list of all paths"""
        paths = []
        
        for item in items:
            if item['type'] == 'directory':
                dir_path = f"{current_path}{item['name']}/"
                paths.append(dir_path)
                
                # Add children
                if item.get('children'):
                    child_paths = self.generate_flat_structure(
                        item['children'], 
                        dir_path
                    )
                    paths.extend(child_paths)
            else:
                file_path = f"{current_path}{item['name']}"
                paths.append(file_path)
        
        return paths
    
    def generate_cursor_rule(self, structure: Dict) -> str:
        """Generate the .mdc file content in Cursor rules format"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Get project name
        project_name = self.project_root.name
        
        # Generate tree structure
        tree_lines = self.generate_tree_structure(structure['items'])
        tree_content = "\n".join(tree_lines)
        
        # Generate flat structure for reference
        flat_paths = self.generate_flat_structure(structure['items'])
        
        # Count file types
        file_types = {}
        def count_types(items):
            for item in items:
                if item['type'] == 'file' and item.get('extension'):
                    ext = item['extension']
                    file_types[ext] = file_types.get(ext, 0) + 1
                elif item['type'] == 'directory' and item.get('children'):
                    count_types(item['children'])
        
        count_types(structure['items'])
        
        # Load template and create rule content
        template_path = Path(__file__).parent / 'templates' / 'file-structure.mdc.template'
        with open(template_path, 'r') as f:
            template = f.read()
        
        rule_content = template.format(
            project_name=project_name,
            tree_content=tree_content
        )
        
        return rule_content
    
    def _format_file_types(self, file_types: Dict[str, int]) -> str:
        """Format file type statistics"""
        if not file_types:
            return "No specific file types detected."
        
        sorted_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)
        lines = []
        
        for ext, count in sorted_types[:10]:  # Show top 10
            lines.append(f"- `{ext}` files: {count}")
        
        if len(sorted_types) > 10:
            remaining = sum(count for _, count in sorted_types[10:])
            lines.append(f"- Other types: {remaining} files")
        
        return "\n".join(lines)
    
    def _identify_key_directories(self, items: List[Dict]) -> str:
        """Get key directories without descriptions"""
        key_dirs = []
        
        key_names = {'src', 'lib', 'components', 'pages', 'api', 'utils', 'hooks', 'styles', 'assets', 'public', 'tests', 'test', 'docs', 'config', 'scripts', 'types', 'models', 'services', 'controllers', 'middleware', 'routes'}
        
        def find_key_dirs(items, path=""):
            for item in items:
                if item['type'] == 'directory':
                    if item['name'].lower() in key_names:
                        full_path = f"{path}{item['name']}/" if path else f"{item['name']}/"
                        key_dirs.append(f"- `{full_path}`")
                    
                    if item.get('children'):
                        find_key_dirs(item['children'], f"{path}{item['name']}/")
        
        find_key_dirs(items)
        
        if not key_dirs:
            return "None"
        
        return "\n".join(key_dirs[:10])
    
    def scan_and_generate(self):
        """Scan directory and generate the cursor rule file"""
        # Ensure output directory exists
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Scan the directory
        structure = self.scan_directory()
        
        # Generate the rule content
        rule_content = self.generate_cursor_rule(structure)
        
        # Write to file
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(rule_content)
        
        return self.output_file
