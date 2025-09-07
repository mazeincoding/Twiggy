import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .config import Config
from .scanner import DirectoryScanner
from colorama import Fore, Style

class CursorContextHandler(FileSystemEventHandler):
    def __init__(self, config: Config):
        self.config = config
        self.scanner = DirectoryScanner(config)
        self.last_update = 0
        self.update_delay = 1.0  # Debounce updates by 1 second
        
    def should_trigger_update(self, event_path: str) -> bool:
        """Determine if this event should trigger an update"""
        path = Path(event_path)
        
        # Ignore if path should be ignored by config
        if self.config.should_ignore(path):
            return False
        
        # Ignore cursor context files themselves
        if '.cursor' in path.parts:
            return False
        
        # Ignore temporary files
        if path.name.startswith('.') and path.name not in ['.gitignore', '.env', '.env.local']:
            return False
        
        # Ignore common temp file patterns
        temp_patterns = ['.tmp', '.temp', '~', '.swp', '.swo']
        if any(path.name.endswith(pattern) for pattern in temp_patterns):
            return False
        
        return True
    
    def update_structure(self, event_type: str, path: str):
        """Update the directory structure with debouncing"""
        current_time = time.time()
        
        # Debounce rapid changes
        if current_time - self.last_update < self.update_delay:
            return
        
        self.last_update = current_time
        
        try:
            self.scanner.scan_and_generate()
            print(f"{Fore.GREEN}📁 Updated structure ({event_type}): {Path(path).name}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ Error updating structure: {e}{Style.RESET_ALL}")
    
    def on_created(self, event):
        """Handle file/directory creation"""
        if not event.is_directory and not self.should_trigger_update(event.src_path):
            return
        
        self.update_structure("created", event.src_path)
    
    def on_deleted(self, event):
        """Handle file/directory deletion"""
        if not event.is_directory and not self.should_trigger_update(event.src_path):
            return
        
        self.update_structure("deleted", event.src_path)
    
    def on_moved(self, event):
        """Handle file/directory moves/renames"""
        # Check both source and destination paths
        should_update = (
            self.should_trigger_update(event.src_path) or 
            self.should_trigger_update(event.dest_path)
        )
        
        if not should_update:
            return
        
        self.update_structure("moved", event.dest_path)
    
    def on_modified(self, event):
        """Handle directory modifications (new files added, etc.)"""
        # Only trigger on directory modifications to avoid excessive updates
        if not event.is_directory:
            return
        
        if not self.should_trigger_update(event.src_path):
            return
        
        self.update_structure("modified", event.src_path)

class FileWatcher:
    def __init__(self, config: Config):
        self.config = config
        self.observer = Observer()
        self.handler = CursorContextHandler(config)
        
    def start(self):
        """Start watching the project directory"""
        # Generate initial structure
        scanner = DirectoryScanner(self.config)
        scanner.scan_and_generate()
        print(f"{Fore.CYAN}📁 Initial structure generated{Style.RESET_ALL}")
        
        # Set up the watcher
        self.observer.schedule(
            self.handler, 
            str(self.config.project_root), 
            recursive=True
        )
        
        self.observer.start()
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop the file watcher"""
        self.observer.stop()
        self.observer.join()
        print(f"{Fore.YELLOW}🛑 File watcher stopped{Style.RESET_ALL}")
