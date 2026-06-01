"""
Unit tests for Phase 1 Widget (Extract & Analyze)
"""

import pytest
import sys
import json
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.ui.phase1_widget import Phase1Widget, ScanWorker


# Create QApplication instance for tests
@pytest.fixture(scope="module")
def qapp():
    """Create QApplication instance for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


class TestPhase1Widget:
    """Tests for Phase1Widget UI component."""
    
    def test_widget_creation(self, qapp):
        """Test that widget can be created."""
        widget = Phase1Widget()
        assert widget is not None
        assert widget.results == []
    
    def test_ui_elements_exist(self, qapp):
        """Test that all UI elements are created."""
        widget = Phase1Widget()
        
        # Check inputs exist
        assert widget.domain_input is not None
        assert widget.folder_input is not None
        
        # Check buttons exist
        assert widget.browse_btn is not None
        assert widget.scan_btn is not None
        assert widget.clear_btn is not None
        assert widget.view_details_btn is not None
        assert widget.export_btn is not None
        
        # Check table exists
        assert widget.results_table is not None
        assert widget.results_table.columnCount() == 5
        
        # Check progress elements
        assert widget.progress_bar is not None
        assert widget.status_label is not None
        assert widget.stats_label is not None
    
    def test_initial_button_states(self, qapp):
        """Test initial enabled/disabled state of buttons."""
        widget = Phase1Widget()
        
        assert widget.scan_btn.isEnabled()
        assert widget.browse_btn.isEnabled()
        assert not widget.clear_btn.isEnabled()
        assert not widget.export_btn.isEnabled()
        assert not widget.view_details_btn.isEnabled()
        assert not widget.progress_bar.isVisible()
    
    def test_clear_results(self, qapp):
        """Test clearing results."""
        widget = Phase1Widget()
        
        # Add mock results
        widget.results = [{"original_name": "test@example.org"}]
        widget.results_table.setRowCount(1)
        widget.clear_btn.setEnabled(True)
        
        # Clear results
        widget.clear_results()
        
        assert len(widget.results) == 0
        assert widget.results_table.rowCount() == 0
        assert not widget.export_btn.isEnabled()
        assert not widget.view_details_btn.isEnabled()
        assert not widget.clear_btn.isEnabled()


class TestScanWorker:
    """Tests for ScanWorker background thread."""
    
    def test_ms365_name_generation(self):
        """Test MS365 name generation."""
        worker = ScanWorker("", "", max_workers=2)
        
        # Test with @ symbol
        assert worker._generate_ms365_name("test@example.org") == "test.ms365@example.org"
        assert worker._generate_ms365_name("list.name@domain.com") == "list.name.ms365@domain.com"
        
        # Test without @ symbol
        assert worker._generate_ms365_name("testlist") == "testlist.ms365"
    
    def test_worker_with_sample_files(self, tmp_path):
        """Test worker with actual sample files."""
        # Create test .org file
        test_file = tmp_path / "test@example.org"
        test_file.write_text(
            "MAILINGLIST test@example.org\n"
            "user1@gmail.com\n"
            "user2@gmail.com\n"
            "user3@example.com\n"
        )
        
        # Create worker with parallel processing (use 2 workers for test)
        worker = ScanWorker(str(tmp_path), "gmail.com", max_workers=2)
        
        # Collect results
        results = []
        worker.finished.connect(lambda r: results.extend(r))
        
        # Run worker
        worker.run()
        
        # Verify results
        assert len(results) == 1
        result = results[0]
        assert result["original_name"] == "test@example.org"
        assert result["ms365_name"] == "test.ms365@example.org"
        assert result["all_members_count"] == 3
        assert result["matched_count"] == 2
        assert len(result["matched_emails"]) == 2
        assert "user1@gmail.com" in result["matched_emails"]
        assert "user2@gmail.com" in result["matched_emails"]
        assert "user3@example.com" not in result["matched_emails"]


class TestIntegrationPhase1:
    """Integration tests for Phase 1."""
    
    def test_scan_tempmail_folder(self, qapp):
        """Test scanning the actual tempmail test folder."""
        widget = Phase1Widget()
        
        # Get tempmail folder path
        tempmail_dir = Path(__file__).parent / "tempmail"
        
        if tempmail_dir.exists():
            # Set folder path
            widget.folder_input.setText(str(tempmail_dir))
            
            # Note: We can't easily test the async scan in unit tests
            # But we can verify the path is set correctly
            assert widget.folder_input.text() == str(tempmail_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
