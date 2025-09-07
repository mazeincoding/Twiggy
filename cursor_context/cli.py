import click
import os
import json
from pathlib import Path
from .scanner import DirectoryScanner
from .watcher import FileWatcher
from .config import Config
from colorama import init, Fore, Style

init()  # Initialize colorama for Windows support

@click.group()
def main():
    """Twiggy - Generate real-time directory structure for Cursor AI"""
    pass

@main.command()
@click.option('--config-only', is_flag=True, help='Only create config without scanning')
def init(config_only):
    """Initialize cursor context in the current directory"""
    current_dir = Path.cwd()
    
    click.echo(f"{Fore.GREEN}🌿 Welcome to Twiggy! Initializing in: {current_dir}{Style.RESET_ALL}")
    
    # Create .cursor directory if it doesn't exist
    cursor_dir = current_dir / '.cursor'
    rules_dir = cursor_dir / 'rules'
    rules_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize config
    config = Config(current_dir)
    
    if not config.exists() or click.confirm(f"{Fore.YELLOW}Config already exists. Reconfigure?{Style.RESET_ALL}"):
        setup_ignore_patterns(config)
    
    if not config_only:
        # Scan and generate initial structure
        scanner = DirectoryScanner(config)
        scanner.scan_and_generate()
        
        click.echo(f"{Fore.GREEN}✅ Directory structure generated!{Style.RESET_ALL}")
        
        # Ask if user wants to start watching
        if click.confirm(f"{Fore.CYAN}Start watching for changes?{Style.RESET_ALL}"):
            start_watcher(config)
    else:
        click.echo(f"{Fore.GREEN}✅ Configuration saved! Run 'twiggy watch' to start monitoring.{Style.RESET_ALL}")

@main.command()
def watch():
    """Start watching for file system changes"""
    config = Config(Path.cwd())
    if not config.exists():
        click.echo(f"{Fore.RED}❌ No config found. Run 'twiggy init' first.{Style.RESET_ALL}")
        return
    
    start_watcher(config)

@main.command()
def scan():
    """Manually trigger a directory scan"""
    config = Config(Path.cwd())
    if not config.exists():
        click.echo(f"{Fore.RED}❌ No config found. Run 'twiggy init' first.{Style.RESET_ALL}")
        return
    
    scanner = DirectoryScanner(config)
    scanner.scan_and_generate()
    click.echo(f"{Fore.GREEN}✅ Directory structure updated!{Style.RESET_ALL}")

def setup_ignore_patterns(config):
    """Interactive setup for ignore patterns"""
    click.echo(f"\n{Fore.YELLOW}📁 Setting up ignore patterns{Style.RESET_ALL}")
    
    # Ask for custom ignores with clear example
    custom_ignores = []
    click.echo(f"\n{Fore.CYAN}Add custom folders to ignore (beyond the common defaults):{Style.RESET_ALL}")
    click.echo(f"{Fore.YELLOW}Examples: 'temp', 'src/old-stuff', 'docs/legacy/backup'{Style.RESET_ALL}")
    click.echo(f"{Fore.GREEN}Note: We'll ask about .gitignore sync next, so don't add those manually{Style.RESET_ALL}")
    click.echo(f"{Fore.GREEN}You can skip this and edit twiggy.yml later{Style.RESET_ALL}")
    click.echo(f"{Fore.YELLOW}Just press Enter when done{Style.RESET_ALL}")
    
    while True:
        folder = click.prompt(f"{Fore.MAGENTA}Folder name", default="", show_default=False).strip()
        if not folder:
            break
        if folder not in custom_ignores:
            custom_ignores.append(folder)
            click.echo(f"  {Fore.GREEN}✓ Added: {folder}{Style.RESET_ALL}")
        else:
            click.echo(f"  {Fore.YELLOW}⚠ Already added: {folder}{Style.RESET_ALL}")
    
    # Ask about gitignore sync
    click.echo(f"\n{Fore.CYAN}Sync with .gitignore - automatically ignore anything in your .gitignore{Style.RESET_ALL}")
    click.echo(f"{Fore.GREEN}This keeps your ignore list in sync (you can change this later){Style.RESET_ALL}")
    sync_gitignore = click.confirm(f"{Fore.CYAN}Enable .gitignore sync?{Style.RESET_ALL}", default=True)
    
    # Create config file
    config.create_default_config(custom_ignores, sync_gitignore)
    
    click.echo(f"\n{Fore.GREEN}✅ Created twiggy.yml - you can edit this file later!{Style.RESET_ALL}")
    if custom_ignores:
        click.echo(f"{Fore.CYAN}Custom ignores added:{Style.RESET_ALL}")
        for ignore in custom_ignores:
            click.echo(f"  • {ignore}")

def start_watcher(config):
    """Start the file system watcher"""
    try:
        watcher = FileWatcher(config)
        click.echo(f"{Fore.GREEN}👀 Watching for changes... (Press Ctrl+C to stop){Style.RESET_ALL}")
        watcher.start()
    except KeyboardInterrupt:
        click.echo(f"\n{Fore.YELLOW}🛑 Stopped watching{Style.RESET_ALL}")
    except Exception as e:
        click.echo(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")

if __name__ == '__main__':
    main()
