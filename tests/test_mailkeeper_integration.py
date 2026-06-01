"""
Integration test demonstrating real-world usage of MailkeeperParser.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parsers.mailkeeper_parser import MailkeeperParser


def test_sample_files_parsing():
    """Test parsing all sample files from tests/tempmail folder."""
    
    parser = MailkeeperParser()
    tempmail_dir = Path(__file__).parent / "tempmail"
    
    # Get all .org files
    org_files = list(tempmail_dir.glob("*.org"))
    
    assert len(org_files) > 0, "No .org files found in tempmail/"
    
    print("\n" + "=" * 70)
    print("INTEGRATION TEST: Sample File Parsing")
    print("=" * 70)
    
    for org_file in sorted(org_files):
        print(f"\n✓ Parsing: {org_file.name}")
        result = parser.parse_file(str(org_file))
        
        # Verify result structure
        assert "list_name" in result
        assert "emails" in result
        assert "metadata" in result
        assert "email_count" in result
        
        # Print summary
        print(f"  List: {result['list_name']}")
        print(f"  Active Emails: {result['email_count']}")
        
        # Verify metadata consistency
        assert result['email_count'] == len(result['emails'])
        assert result['email_count'] == len(result['metadata'])
        
        # Verify each metadata matches its email
        for email, metadata in zip(result['emails'], result['metadata']):
            assert email == metadata.email, \
                f"Email mismatch: {email} vs {metadata.email}"
        
        print(f"  ✓ All metadata verified")
    
    print("\n" + "=" * 70)
    print(f"✓ Successfully parsed {len(org_files)} distribution lists")
    print("=" * 70)


if __name__ == "__main__":
    test_sample_files_parsing()
