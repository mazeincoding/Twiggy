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
        self.update_delay = 1.0
        
    def should_trigger_update(self, event_path: str) -> bool:
        path = Path(event_path)
        
        if self.config.should_ignore(path):
            return False
        
        if '.cursor' in path.parts:
            return False
        
        if self._is_temporary_file(path):
            return False
        
        return True
    
    def _is_temporary_file(self, path):
        if path.name.startswith('.') and path.name not in ['.gitignore', '.env', '.env.local']:
            return True
        
        temp_patterns = ['.tmp', '.temp', '~', '.swp', '.swo']
        return any(path.name.endswith(pattern) for pattern in temp_patterns)
    
    def update_structure(self, event_type: str, path: str):
        current_time = time.time()
        
        if current_time - self.last_update < self.update_delay:
            return
        
        self.last_update = current_time
        
        try:
            self.scanner.scan_and_generate()
            print(f"{Fore.GREEN}📁 Updated structure ({event_type}): {Path(path).name}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ Error updating structure: {e}{Style.RESET_ALL}")
    
    def on_created(self, event):
        if not event.is_directory and not self.should_trigger_update(event.src_path):
            return
        self.update_structure("created", event.src_path)
    
    def on_deleted(self, event):
        if not event.is_directory and not self.should_trigger_update(event.src_path):
            return
        self.update_structure("deleted", event.src_path)
    
    def on_moved(self, event):
        should_update = (
            self.should_trigger_update(event.src_path) or 
            self.should_trigger_update(event.dest_path)
        )
        
        if should_update:
            self.update_structure("moved", event.dest_path)
    
    def on_modified(self, event):
        if event.is_directory and self.should_trigger_update(event.src_path):
            self.update_structure("modified", event.src_path)

class FileWatcher:
    def __init__(self, config: Config):
        self.config = config
        self.observer = Observer()
        self.handler = CursorContextHandler(config)
        
    def start(self):
        self._generate_initial_structure()
        self._setup_observer()
        self._run_watcher()
    
    def _generate_initial_structure(self):
        scanner = DirectoryScanner(self.config)
        scanner.scan_and_generate()
        print(f"{Fore.CYAN}📁 Initial structure generated{Style.RESET_ALL}")
    
    def _setup_observer(self):
        self.observer.schedule(
            self.handler, 
            str(self.config.project_root), 
            recursive=True
        )
        self.observer.start()
    
    def _run_watcher(self):
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        self.observer.stop()
        self.observer.join()
        print(f"{Fore.YELLOW}🛑 File watcher stopped{Style.RESET_ALL}")
