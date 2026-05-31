"""
Unit tests for Mailkeeper parser.
"""

import pytest
import sys
from pathlib import Path
import tempfile

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parsers.mailkeeper_parser import (
    MailkeeperParser,
    EmailMetadata,
    MailkeeperParseException,
)


class TestMailkeeperParserBasic:
    """Basic functionality tests for MailkeeperParser."""
    
    def test_parse_valid_file(self, tmp_path):
        """Test parsing a valid .org file."""
        # Create test file
        test_file = tmp_path / "test_list@example.org"
        test_file.write_text(
            "MAILINGLIST test_list@example.org\n"
            "user1@example.com\n"
            "user2@example.com\n"
        )
        
        parser = MailkeeperParser()
        result = parser.parse_file(str(test_file))
        
        assert result["list_name"] == "test_list@example.org"
        assert len(result["emails"]) == 2
        assert "user1@example.com" in result["emails"]
        assert "user2@example.com" in result["emails"]
    
    def test_file_not_found(self):
        """Test parsing non-existent file."""
        parser = MailkeeperParser()
        
        with pytest.raises(FileNotFoundError):
            parser.parse_file("/nonexistent/path/file.org")
    
    def test_file_without_mailinglist_directive(self, tmp_path):
        """Test parsing file without MAILINGLIST directive."""
        test_file = tmp_path / "invalid.org"
        test_file.write_text(
            "user1@example.com\n"
            "user2@example.com\n"
        )
        
        parser = MailkeeperParser()
        
        with pytest.raises(MailkeeperParseException):
            parser.parse_file(str(test_file))


class TestEmailExtraction:
    """Tests for email extraction logic."""
    
    def test_extract_active_emails(self, tmp_path):
        """Test extracting only active (non-commented) emails."""
        test_file = tmp_path / "test_list@example.org"
        test_file.write_text(
            "MAILINGLIST test_list@example.org\n"
            "active1@example.com\n"
            "!ALIAS inactive1@example.com\n"
            "active2@example.com\n"
            "!ACCEPT ignored@example.com\n"
            "active3@example.com\n"
        )
        
        parser = MailkeeperParser()
        result = parser.parse_file(str(test_file))
        
        assert len(result["emails"]) == 3
        assert "active1@example.com" in result["emails"]
        assert "active2@example.com" in result["emails"]
        assert "active3@example.com" in result["emails"]
        assert "inactive1@example.com" not in result["emails"]
    
    def test_skip_comment_lines(self, tmp_path):
        """Test skipping lines starting with #."""
        test_file = tmp_path / "test_list@example.org"
        test_file.write_text(
            "MAILINGLIST test_list@example.org\n"
            "# This is a comment\n"
            "user1@example.com\n"
            "# Another comment\n"
            "user2@example.com\n"
        )
        
        parser = MailkeeperParser()
        result = parser.parse_file(str(test_file))
        
        assert len(result["emails"]) == 2
        assert "user1@example.com" in result["emails"]
        assert "user2@example.com" in result["emails"]
    
    def test_skip_directives(self, tmp_path):
        """Test skipping directive lines."""
        test_file = tmp_path / "test_list@example.org"
        test_file.write_text(
            "MAILINGLIST test_list@example.org\n"
            "user1@example.com\n"
            "DELAYGREYLIST\n"
            "user2@example.com\n"
            "NOTSENDER\n"
            "user3@example.com\n"
        )
        
        parser = MailkeeperParser()
        result = parser.parse_file(str(test_file))
        
        assert len(result["emails"]) == 3
        assert "user1@example.com" in result["emails"]
        assert "user2@example.com" in result["emails"]
        assert "user3@example.com" in result["emails"]
    
    def test_skip_empty_lines(self, tmp_path):
        """Test skipping empty lines."""
        test_file = tmp_path / "test_list@example.org"
        test_file.write_text(
            "MAILINGLIST test_list@example.org\n"
            "user1@example.com\n"
            "\n"
            "user2@example.com\n"
            "\n"
            "\n"
            "user3@example.com\n"
        )
        
        parser = MailkeeperParser()
        result = parser.parse_file(str(test_file))
        
        assert len(result["emails"]) == 3
    
    def test_validate_email_format(self, tmp_path):
        """Test that only valid emails are extracted."""
        test_file = tmp_path / "test_list@example.org"
        test_file.write_text(
            "MAILINGLIST test_list@example.org\n"
            "valid.email@example.com\n"
            "invalid-email\n"
            "another.valid@example.co.uk\n"
            "missing@domain\n"
            "name@.com\n"
        )
        
        parser = MailkeeperParser()
        result = parser.parse_file(str(test_file))
        
        assert len(result["emails"]) == 2
        assert "valid.email@example.com" in result["emails"]
        assert "another.valid@example.co.uk" in result["emails"]


class TestEmailMetadata:
    """Tests for email metadata generation."""
    
    def test_simple_email_metadata(self, tmp_path):
        """Test metadata generation for simple email."""
        test_file = tmp_path / "test_list@example.org"
        test_file.write_text(
            "MAILINGLIST test_list@example.org\n"
            "user@example.com\n"
        )
        
        parser = MailkeeperParser()
        result = parser.parse_file(str(test_file))
        
        metadata = result["metadata"][0]
        assert metadata.email == "user@example.com"
        assert metadata.first_name == "user"
        assert metadata.last_name == "example"
        assert metadata.display_name == "user example"
        assert metadata.description == "External contact - example.com"
    
    def test_email_with_periods_metadata(self, tmp_path):
        """Test metadata generation for email with periods in local part."""
        test_file = tmp_path / "test_list@example.org"
        test_file.write_text(
            "MAILINGLIST test_list@example.org\n"
            "user.name@example.com\n"
        )
        
        parser = MailkeeperParser()
        result = parser.parse_file(str(test_file))
        
        metadata = result["metadata"][0]
        assert metadata.email == "user.name@example.com"
        assert metadata.first_name == "username"  # periods removed
        assert metadata.last_name == "example"
        assert metadata.display_name == "username example"
        assert metadata.description == "External contact - example.com"
    
    def test_email_with_subdomain_metadata(self, tmp_path):
        """Test metadata generation for email with subdomain."""
        test_file = tmp_path / "test_list@example.org"
        test_file.write_text(
            "MAILINGLIST test_list@example.org\n"
            "contact@mail.example.co.uk\n"
        )
        
        parser = MailkeeperParser()
        result = parser.parse_file(str(test_file))
        
        metadata = result["metadata"][0]
        assert metadata.email == "contact@mail.example.co.uk"
        assert metadata.first_name == "contact"
        # Domain parts: mail, example, co, uk -> remove uk -> mail.example.co
        assert metadata.last_name == "mailexampleco"
        assert metadata.description == "External contact - mail.example.co.uk"
    
    def test_complex_email_metadata(self, tmp_path):
        """Test metadata generation for complex email."""
        test_file = tmp_path / "test_list@example.org"
        test_file.write_text(
            "MAILINGLIST test_list@example.org\n"
            "john.q.public@subdomain.example.com\n"
        )
        
        parser = MailkeeperParser()
        result = parser.parse_file(str(test_file))
        
        metadata = result["metadata"][0]
        assert metadata.email == "john.q.public@subdomain.example.com"
        assert metadata.first_name == "johnqpublic"  # periods removed
        assert metadata.last_name == "subdomainexample"  # domain without TLD
        assert metadata.display_name == "johnqpublic subdomainexample"


class TestListNameExtraction:
    """Tests for distribution list name extraction."""
    
    def test_extract_simple_list_name(self, tmp_path):
        """Test extracting simple distribution list name."""
        test_file = tmp_path / "test_list@example.org"
        test_file.write_text(
            "MAILINGLIST distribution.list@example.org\n"
            "user@example.com\n"
        )
        
        parser = MailkeeperParser()
        result = parser.parse_file(str(test_file))
        
        assert result["list_name"] == "distribution.list@example.org"
    
    def test_extract_list_name_with_spaces(self, tmp_path):
        """Test extracting list name with extra spaces."""
        test_file = tmp_path / "test_list@example.org"
        test_file.write_text(
            "MAILINGLIST   list.name@example.org   \n"
            "user@example.com\n"
        )
        
        parser = MailkeeperParser()
        result = parser.parse_file(str(test_file))
        
        assert result["list_name"] == "list.name@example.org"
    
    def test_mailinglist_directive_only(self, tmp_path):
        """Test handling of bare MAILINGLIST directive.
        
        When the MAILINGLIST directive exists but has no value (bare directive),
        the parser falls back to using the source filename stem (without extension)
        as the distribution list name.
        
        This behavior assumes the filename represents a valid distribution list name.
        For example, a file named "badminton@cbcmgroups.org" with a bare MAILINGLIST
        directive will derive the list name as "badminton@cbcmgroups".
        
        Args:
            tmp_path: Pytest temporary directory fixture
            
        Examples:
            File: "test_list@example.org" with "MAILINGLIST" (bare)
            Expected list_name: "test_list@example" (extension ".org" removed)
        """
        test_file = tmp_path / "test_list@example.org"
        test_file.write_text(
            "MAILINGLIST\n"
            "user@example.com\n"
        )
        
        parser = MailkeeperParser()
        result = parser.parse_file(str(test_file))

        # File stem is "test_list@example" (extension ".org" removed)
        assert result["list_name"] == "test_list@example"
    
    def test_mailinglist_directive_empty_value(self, tmp_path):
        """Test handling of MAILINGLIST directive with empty value.
        
        When the MAILINGLIST directive exists but contains only whitespace,
        the parser falls back to using the source filename stem (without extension)
        as the distribution list name.
        
        This is similar to the bare MAILINGLIST case but explicitly handles
        whitespace-only values.
        """
        test_file = tmp_path / "distribution.list@example.org"
        test_file.write_text(
            "MAILINGLIST   \n"
            "user@example.com\n"
        )
        
        parser = MailkeeperParser()
        result = parser.parse_file(str(test_file))

        # File stem is "distribution.list@example" (extension ".org" removed)
        assert result["list_name"] == "distribution.list@example"


class TestFileEncoding:
    """Tests for file encoding handling."""
    
    def test_utf8_encoding(self, tmp_path):
        """Test parsing UTF-8 encoded file."""
        test_file = tmp_path / "test_list@example.org"
        test_file.write_text(
            "MAILINGLIST test_list@example.org\n"
            "user1@example.com\n"
            "user2@example.com\n",
            encoding="utf-8"
        )
        
        parser = MailkeeperParser()
        result = parser.parse_file(str(test_file))
        
        assert len(result["emails"]) == 2
    
    def test_latin1_encoding(self, tmp_path):
        """Test parsing latin-1 encoded file."""
        test_file = tmp_path / "test_list@example.org"
        # Write with latin-1 encoding
        with open(test_file, "w", encoding="latin-1") as f:
            f.write("MAILINGLIST test_list@example.org\n")
            f.write("user1@example.com\n")
            f.write("user2@example.com\n")
        
        parser = MailkeeperParser()
        result = parser.parse_file(str(test_file))
        
        assert len(result["emails"]) == 2


class TestComplexScenarios:
    """Tests for complex real-world scenarios."""
    
    def test_complex_file_with_all_features(self, tmp_path):
        """Test parsing file with all features combined."""
        test_file = tmp_path / "distribution.list1@example.org"
        test_file.write_text(
            "MAILINGLIST distribution.list1@example.org\n"
            "# Distribution list for team communications\n"
            "active.member1@example.com\n"
            "!ALIAS inactive.member1@example.com\n"
            "\n"
            "active.member2@other.co.uk\n"
            "DELAYGREYLIST\n"
            "!ACCEPT unknown@domain.com\n"
            "active.member3@service.com\n"
            "# End of list\n"
        )
        
        parser = MailkeeperParser()
        result = parser.parse_file(str(test_file))
        
        assert result["list_name"] == "distribution.list1@example.org"
        assert result["email_count"] == 3
        assert len(result["metadata"]) == 3
        
        # Verify specific metadata
        emails_dict = {m.email: m for m in result["metadata"]}
        assert emails_dict["active.member1@example.com"].first_name == "activemember1"
        assert emails_dict["active.member2@other.co.uk"].last_name == "otherco"
    
    def test_large_distribution_list(self, tmp_path):
        """Test parsing file with many members."""
        test_file = tmp_path / "large_list@example.org"
        
        lines = ["MAILINGLIST large_list@example.org\n"]
        for i in range(100):
            lines.append(f"user{i}@example.com\n")
        
        test_file.write_text("".join(lines))
        
        parser = MailkeeperParser()
        result = parser.parse_file(str(test_file))
        
        assert result["email_count"] == 100
        assert len(result["metadata"]) == 100
    
    def test_mixed_inactive_markers(self, tmp_path):
        """Test parsing with various inactive markers."""
        test_file = tmp_path / "test_list@example.org"
        test_file.write_text(
            "MAILINGLIST test_list@example.org\n"
            "active1@example.com\n"
            "!ALIAS inactive1@example.com\n"
            "!ACCEPT inactive2@example.com\n"
            "active2@example.com\n"
            "!SENDER inactive3@example.com\n"
        )
        
        parser = MailkeeperParser()
        result = parser.parse_file(str(test_file))
        
        assert len(result["emails"]) == 2
        assert "active1@example.com" in result["emails"]
        assert "active2@example.com" in result["emails"]


class TestResultStructure:
    """Tests for return value structure."""
    
    def test_parse_file_return_structure(self, tmp_path):
        """Test that parse_file returns all expected fields."""
        test_file = tmp_path / "test_list@example.org"
        test_file.write_text(
            "MAILINGLIST test_list@example.org\n"
            "user1@example.com\n"
        )
        
        parser = MailkeeperParser()
        result = parser.parse_file(str(test_file))
        
        # Verify all expected keys
        assert "list_name" in result
        assert "emails" in result
        assert "metadata" in result
        assert "email_count" in result
        assert "file_path" in result
        
        # Verify types
        assert isinstance(result["list_name"], str)
        assert isinstance(result["emails"], list)
        assert isinstance(result["metadata"], list)
        assert isinstance(result["email_count"], int)
        assert isinstance(result["file_path"], str)
    
    def test_metadata_type(self, tmp_path):
        """Test that metadata items are EmailMetadata objects."""
        test_file = tmp_path / "test_list@example.org"
        test_file.write_text(
            "MAILINGLIST test_list@example.org\n"
            "user@example.com\n"
        )
        
        parser = MailkeeperParser()
        result = parser.parse_file(str(test_file))
        
        assert len(result["metadata"]) == 1
        assert isinstance(result["metadata"][0], EmailMetadata)
