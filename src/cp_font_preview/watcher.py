"""File watching for auto-reload functionality."""

import time
from collections.abc import Callable
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from watchdog.observers.api import BaseObserver


class FontFileHandler(FileSystemEventHandler):
    """Handler for font file change events."""

    def __init__(self, manifest_path: str, callback):
        """Initialize handler.

        Args:
            manifest_path: Path to manifest file to monitor
            callback: Function to call when changes detected
        """
        self.manifest_path = Path(manifest_path)
        self.manifest_dir = self.manifest_path.parent
        self.callback = callback
        self.last_modified = time.time()
        self.debounce_seconds = 0.5  # Avoid multiple rapid updates

    def on_modified(self, event):
        """Handle file modification events."""
        if event.is_directory:
            return

        # Check if a font file or manifest was modified
        event_path = Path(event.src_path)

        # Check if it's a font file or manifest in the watched directory
        if event_path.parent == self.manifest_dir and (
            event_path.suffix in [".pcf", ".bdf"] or event_path.name.endswith("-manifest.json")
        ):
            # Debounce rapid changes
            now = time.time()
            if now - self.last_modified > self.debounce_seconds:
                self.last_modified = now
                self.callback()


class FontWatcher:
    """Watch font directory for changes."""

    def __init__(self, manifest_path: str, callback: Callable[[], None]):
        """Initialize watcher.

        Args:
            manifest_path: Path to manifest file
            callback: Function to call on changes
        """
        self.manifest_path = Path(manifest_path)
        self.watch_dir = self.manifest_path.parent
        self.callback = callback
        self.observer: BaseObserver | None = None

    def start(self):
        """Start watching for file changes."""
        event_handler = FontFileHandler(str(self.manifest_path), self.callback)
        self.observer = Observer()
        if self.observer is not None:
            self.observer.schedule(event_handler, str(self.watch_dir), recursive=False)
            self.observer.start()
        print(f"Watching directory: {self.watch_dir}")
        print("Edit and regenerate fonts to see updates...")

    def stop(self):
        """Stop watching."""
        if self.observer:
            self.observer.stop()
            self.observer.join()
