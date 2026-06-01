"""
Phase 1 UI: Extract & Analyze
Scan Mailkeeper distribution lists and export to JSON.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QFileDialog,
    QProgressBar, QGroupBox, QMessageBox, QDialog, QTextEdit,
    QHeaderView
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

from parsers.mailkeeper_parser import MailkeeperParser, MailkeeperParseException
from config.settings import EXPORTS_DIR, MIN_SCAN_WORKERS, MAX_SCAN_WORKERS


class ScanWorker(QThread):
    """Background worker thread for scanning distribution lists."""
    
    progress = pyqtSignal(int, int, str)  # current, total, message
    finished = pyqtSignal(list)  # results
    error = pyqtSignal(str)  # error message
    
    def __init__(self, folder_path: str, domain_filter: str, max_workers: int = 4):
        super().__init__()
        self.folder_path = folder_path
        self.domain_filter = domain_filter
        self.max_workers = max_workers
        
    def _parse_single_file(self, org_file: Path, domains: List[str]) -> Optional[Dict]:
        """Parse a single .org file. Returns result dict or None if error."""
        try:
            parser = MailkeeperParser()
            parsed = parser.parse_file(str(org_file))
            
            # Filter emails by domain if specified
            if domains:
                matched_emails = [
                    email for email in parsed["emails"]
                    if any(email.lower().endswith(f"@{domain}") for domain in domains)
                ]
            else:
                matched_emails = parsed["emails"]
            
            # Generate MS365 list name
            original_name = parsed["list_name"]
            ms365_name = self._generate_ms365_name(original_name)
            
            return {
                "original_name": original_name,
                "ms365_name": ms365_name,
                "file_path": parsed["file_path"],
                "all_emails": parsed["emails"],
                "matched_emails": matched_emails,
                "all_members_count": parsed["email_count"],
                "matched_count": len(matched_emails),
                "metadata": parsed["metadata"]
            }
            
        except MailkeeperParseException:
            # Skip files that don't have MAILINGLIST directive
            return None
        except Exception as e:
            # Log error but continue with other files
            print(f"Warning: Error parsing {org_file.name}: {e}")
            return None
    
    def run(self):
        """Scan folder for .org files and parse them in parallel."""
        try:
            folder = Path(self.folder_path)
            org_files = list(folder.rglob("*.org"))
            
            if not org_files:
                self.error.emit(f"No .org files found in {self.folder_path}")
                return
            
            total_files = len(org_files)
            results = []
            domains = [d.strip().lower() for d in self.domain_filter.split(",") if d.strip()]
            
            # Console logging
            print(f"\n{'='*60}")
            print(f"Starting scan: {self.folder_path}")
            print(f"Files found: {total_files}")
            print(f"Workers: {self.max_workers}")
            print(f"Domain filter: {', '.join(domains) if domains else 'None (all domains)'}")
            print(f"{'='*60}\n")
            
            # Process files in parallel
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all tasks
                future_to_file = {
                    executor.submit(self._parse_single_file, org_file, domains): org_file
                    for org_file in org_files
                }
                
                # Process completed tasks as they finish
                completed = 0
                for future in as_completed(future_to_file):
                    org_file = future_to_file[future]
                    completed += 1
                    
                    # Update progress (every 10% or every 100 files for large batches)
                    if completed % max(1, total_files // 10, 100) == 0 or completed == total_files:
                        print(f"Progress: {completed}/{total_files} ({completed*100//total_files}%)")
                    
                    self.progress.emit(
                        completed, 
                        total_files, 
                        f"Processed {completed}/{total_files} files..."
                    )
                    
                    # Get result
                    try:
                        result = future.result()
                        if result is not None:
                            results.append(result)
                    except Exception as e:
                        print(f"⚠️  Error processing {org_file}: {e}")
                        continue
            
            # Summary
            print(f"\n{'='*60}")
            print(f"Scan complete!")
            print(f"Total files scanned: {total_files}")
            print(f"Distribution lists found: {len(results)}")
            if results:
                total_members = sum(r['all_members_count'] for r in results)
                total_matched = sum(r['matched_count'] for r in results)
                print(f"Total members: {total_members}")
                print(f"Matched members: {total_matched}")
            print(f"{'='*60}\n")
            
            self.finished.emit(results)
            
        except Exception as e:
            print(f"❌ Fatal error during scan: {e}")
            self.error.emit(str(e))
    
    def _generate_ms365_name(self, original_name: str) -> str:
        """Generate MS365 distribution list name."""
        # Add .ms365 before the @ symbol
        if "@" in original_name:
            local, domain = original_name.rsplit("@", 1)
            return f"{local}.ms365@{domain}"
        else:
            return f"{original_name}.ms365"


class DetailsDialog(QDialog):
    """Dialog to show detailed member list."""
    
    def __init__(self, list_name: str, emails: List[str], parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Members: {list_name}")
        self.resize(600, 400)
        
        layout = QVBoxLayout()
        
        # Email list
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText("\n".join(sorted(emails)))
        layout.addWidget(text_edit)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)


class Phase1Widget(QWidget):
    """Phase 1: Extract & Analyze distribution lists."""
    
    def __init__(self):
        super().__init__()
        self.results = []
        self.scan_worker = None
        self.init_ui()
        self.load_preferences()
        
    def init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Phase 1: Extract & Analyze")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Configuration section
        config_group = QGroupBox("Configuration")
        config_layout = QVBoxLayout()
        
        # Domain filter
        domain_layout = QHBoxLayout()
        domain_layout.addWidget(QLabel("Domain Filter:"))
        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("e.g., gmail.com, example.com (comma-separated, leave empty for all)")
        domain_layout.addWidget(self.domain_input)
        config_layout.addLayout(domain_layout)
        
        # Folder path selector
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(QLabel("Mailkeeper Folder:"))
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Select folder containing .org files")
        folder_layout.addWidget(self.folder_input)
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.browse_folder)
        folder_layout.addWidget(self.browse_btn)
        config_layout.addLayout(folder_layout)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # Action buttons
        action_layout = QHBoxLayout()
        self.scan_btn = QPushButton("Scan Distribution Lists")
        self.scan_btn.clicked.connect(self.scan_distribution_lists)
        action_layout.addWidget(self.scan_btn)
        
        self.clear_btn = QPushButton("Clear Results")
        self.clear_btn.clicked.connect(self.clear_results)
        self.clear_btn.setEnabled(False)
        action_layout.addWidget(self.clear_btn)
        
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
        # Progress section
        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        self.status_label = QLabel("")
        progress_layout.addWidget(self.status_label)
        layout.addLayout(progress_layout)
        
        # Results section
        results_group = QGroupBox("Scan Results")
        results_layout = QVBoxLayout()
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels([
            "Distribution List Name",
            "Total Members",
            "Matched Emails",
            "MS365 List Name",
            "File Path"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        results_layout.addWidget(self.results_table)
        
        # Summary statistics
        summary_layout = QHBoxLayout()
        self.stats_label = QLabel("No results yet")
        summary_layout.addWidget(self.stats_label)
        summary_layout.addStretch()
        results_layout.addLayout(summary_layout)
        
        # Result action buttons
        result_actions = QHBoxLayout()
        self.view_details_btn = QPushButton("View Details")
        self.view_details_btn.clicked.connect(self.view_details)
        self.view_details_btn.setEnabled(False)
        result_actions.addWidget(self.view_details_btn)
        
        self.export_btn = QPushButton("Export to JSON")
        self.export_btn.clicked.connect(self.export_to_json)
        self.export_btn.setEnabled(False)
        result_actions.addWidget(self.export_btn)
        
        result_actions.addStretch()
        results_layout.addLayout(result_actions)
        
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        
        self.setLayout(layout)
    
    def browse_folder(self):
        """Open folder browser dialog."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Mailkeeper Folder",
            self.folder_input.text() or str(Path.home())
        )
        if folder:
            self.folder_input.setText(folder)
    
    def scan_distribution_lists(self):
        """Start scanning distribution lists."""
        folder_path = self.folder_input.text().strip()
        
        # Validation
        if not folder_path:
            QMessageBox.warning(self, "Input Required", "Please select a Mailkeeper folder.")
            return
        
        if not Path(folder_path).exists():
            QMessageBox.warning(self, "Invalid Path", "The specified folder does not exist.")
            return
        
        if not Path(folder_path).is_dir():
            QMessageBox.warning(self, "Invalid Path", "The specified path is not a folder.")
            return
        
        # Save folder preference
        self.save_preferences()
        
        # Clear previous results
        self.results = []
        self.results_table.setRowCount(0)
        
        # Disable buttons during scan
        self.scan_btn.setEnabled(False)
        self.browse_btn.setEnabled(False)
        self.export_btn.setEnabled(False)
        self.view_details_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)
        
        # Show progress
        self.progress_bar.setVisible(True)
        self.status_label.setText("Starting scan...")
        
        # Start worker thread with parallel processing
        # Use 2x CPU cores for I/O-bound file parsing
        cpu_count = os.cpu_count() or 4
        max_workers = min(MAX_SCAN_WORKERS, max(MIN_SCAN_WORKERS, cpu_count * 2))
        domain_filter = self.domain_input.text().strip()
        self.scan_worker = ScanWorker(folder_path, domain_filter, max_workers)
        self.scan_worker.progress.connect(self.update_progress)
        self.scan_worker.finished.connect(self.scan_completed)
        self.scan_worker.error.connect(self.scan_error)
        self.scan_worker.start()
    
    def update_progress(self, current: int, total: int, message: str):
        """Update progress bar and status."""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.status_label.setText(message)
    
    def scan_completed(self, results: List[Dict]):
        """Handle scan completion."""
        self.results = results
        
        # Populate table
        self.results_table.setRowCount(len(results))
        for row, result in enumerate(results):
            self.results_table.setItem(row, 0, QTableWidgetItem(result["original_name"]))
            self.results_table.setItem(row, 1, QTableWidgetItem(str(result["all_members_count"])))
            self.results_table.setItem(row, 2, QTableWidgetItem(str(result["matched_count"])))
            self.results_table.setItem(row, 3, QTableWidgetItem(result["ms365_name"]))
            self.results_table.setItem(row, 4, QTableWidgetItem(result["file_path"]))
        
        # Update summary
        total_lists = len(results)
        lists_with_matches = sum(1 for r in results if r["matched_count"] > 0)
        total_emails = sum(r["matched_count"] for r in results)
        
        self.stats_label.setText(
            f"Total Lists: {total_lists} | "
            f"Lists with Matches: {lists_with_matches} | "
            f"Total Emails to Migrate: {total_emails}"
        )
        
        # Re-enable buttons
        self.scan_btn.setEnabled(True)
        self.browse_btn.setEnabled(True)
        self.clear_btn.setEnabled(True)
        self.export_btn.setEnabled(len(results) > 0)
        self.view_details_btn.setEnabled(len(results) > 0)
        
        # Hide progress
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Scan completed: {total_lists} distribution lists found")
        
        if total_lists == 0:
            QMessageBox.information(
                self,
                "No Results",
                "No valid distribution lists found in the selected folder."
            )
    
    def scan_error(self, error_message: str):
        """Handle scan error."""
        self.scan_btn.setEnabled(True)
        self.browse_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Scan failed")
        
        QMessageBox.critical(self, "Scan Error", f"An error occurred during scanning:\n\n{error_message}")
    
    def view_details(self):
        """Show detailed member list for selected distribution list."""
        selected_rows = self.results_table.selectionModel().selectedRows()
        
        if not selected_rows:
            QMessageBox.information(self, "No Selection", "Please select a distribution list to view details.")
            return
        
        row = selected_rows[0].row()
        result = self.results[row]
        
        # Show dialog with all emails or matched emails based on filter
        domain_filter = self.domain_input.text().strip()
        if domain_filter:
            emails = result["matched_emails"]
            title = f"{result['original_name']} (Filtered)"
        else:
            emails = result["all_emails"]
            title = result['original_name']
        
        dialog = DetailsDialog(title, emails, self)
        dialog.exec_()
    
    def export_to_json(self):
        """Export results to JSON file."""
        if not self.results:
            QMessageBox.warning(self, "No Data", "No results to export. Please scan first.")
            return
        
        # Generate default filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"migration_config_{timestamp}.json"
        default_path = EXPORTS_DIR / default_filename
        
        # Ask user for save location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Migration Configuration",
            str(default_path),
            "JSON Files (*.json);;All Files (*)"
        )
        
        if not file_path:
            return
        
        try:
            # Prepare export data
            export_data = {
                "migration_config": {
                    "target_domain": self.domain_input.text().strip(),
                    "scan_date": datetime.now().isoformat(),
                    "mailkeeper_folder": self.folder_input.text().strip(),
                    "ms365_domain": self._extract_ms365_domain()
                },
                "distribution_lists": [
                    {
                        "original_name": r["original_name"],
                        "ms365_name": r["ms365_name"],
                        "file_path": r["file_path"],
                        "matched_emails": r["matched_emails"],
                        "all_members_count": r["all_members_count"],
                        "matched_count": r["matched_count"]
                    }
                    for r in self.results
                ],
                "summary": {
                    "total_lists": len(self.results),
                    "lists_with_matches": sum(1 for r in self.results if r["matched_count"] > 0),
                    "total_emails_to_migrate": sum(r["matched_count"] for r in self.results),
                    "total_all_emails": sum(r["all_members_count"] for r in self.results)
                }
            }
            
            # Write to file
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2)
            
            self.status_label.setText(f"Exported to {Path(file_path).name}")
            QMessageBox.information(
                self,
                "Export Successful",
                f"Migration configuration exported successfully to:\n\n{file_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"Failed to export JSON:\n\n{str(e)}"
            )
    
    def _extract_ms365_domain(self) -> str:
        """Extract MS365 domain from first distribution list."""
        if self.results:
            ms365_name = self.results[0]["ms365_name"]
            if "@" in ms365_name:
                return ms365_name.split("@")[1]
        return ""
    
    def clear_results(self):
        """Clear all results."""
        self.results = []
        self.results_table.setRowCount(0)
        self.stats_label.setText("No results yet")
        self.status_label.setText("")
        self.export_btn.setEnabled(False)
        self.view_details_btn.setEnabled(False)
        self.clear_btn.setEnabled(False)
    
    def save_preferences(self):
        """Save user preferences."""
        try:
            prefs_file = Path.home() / ".cbcmgroups_migration_prefs.json"
            prefs = {
                "last_folder": self.folder_input.text().strip(),
                "last_domain_filter": self.domain_input.text().strip()
            }
            with open(prefs_file, "w") as f:
                json.dump(prefs, f)
        except Exception:
            # Silently fail if can't save preferences
            pass
    
    def load_preferences(self):
        """Load user preferences."""
        try:
            prefs_file = Path.home() / ".cbcmgroups_migration_prefs.json"
            if prefs_file.exists():
                with open(prefs_file, "r") as f:
                    prefs = json.load(f)
                    self.folder_input.setText(prefs.get("last_folder", ""))
                    self.domain_input.setText(prefs.get("last_domain_filter", ""))
        except Exception:
            # Silently fail if can't load preferences
            pass
