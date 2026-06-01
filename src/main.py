"""
CBCMGROUPS Email Distribution List Migration Tool
Main application entry point
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget

from config.settings import APP_NAME, APP_VERSION
from ui.phase1_widget import Phase1Widget


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle(f"{APP_NAME} - v{APP_VERSION}")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create tab widget
        tabs = QTabWidget()
        
        # Add Phase 1 tab
        self.phase1_widget = Phase1Widget()
        tabs.addTab(self.phase1_widget, "Phase 1: Extract && Analyze")
        
        # Placeholder tabs for future phases
        # tabs.addTab(QWidget(), "Phase 2: MS365 Export (Coming Soon)")
        # tabs.addTab(QWidget(), "Phase 3: Mailkeeper Cleanup (Coming Soon)")
        
        self.setCentralWidget(tabs)
        
        # Create menu bar
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        # Status bar
        self.statusBar().showMessage("Ready")


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
