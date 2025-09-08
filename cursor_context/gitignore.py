from pathlib import Path


def ensure_gitignore_entry(project_root):
    """Add Twiggy rule file to .gitignore if not already present"""
    gitignore_path = project_root / '.gitignore'
    entry = '.cursor/rules/file-structure.mdc'
    
    if gitignore_path.exists():
        if _entry_exists(gitignore_path, entry):
            return
        _append_entry(gitignore_path, entry)
    else:
        _create_gitignore_with_entry(gitignore_path, entry)


def _entry_exists(gitignore_path, entry):
    with open(gitignore_path, 'r') as f:
        return entry in f.read()


def _append_entry(gitignore_path, entry):
    with open(gitignore_path, 'a') as f:
        f.write(f'\n# Twiggy\n{entry}\n')


def _create_gitignore_with_entry(gitignore_path, entry):
    with open(gitignore_path, 'w') as f:
        f.write(f'# Twiggy\n{entry}\n')
