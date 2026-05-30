"""
Mailkeeper email distribution list parser.
Parses .org files from Mailkeeper private email service.
"""

import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class EmailMetadata:
    """Metadata for an email address extracted from Mailkeeper list."""
    email: str
    first_name: str
    last_name: str
    display_name: str
    description: str


class MailkeeperParseException(Exception):
    """Base exception for Mailkeeper parser errors."""
    pass


class MailkeeperParser:
    """
    Parser for Mailkeeper .org distribution list files.
    
    Extracts active email addresses and generates metadata for MS365 migration.
    """
    
    # Regex pattern for email validation
    EMAIL_REGEX = re.compile(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )
    
    # Directives to skip
    DIRECTIVES = {
        "MAILINGLIST",
        "DELAYGREYLIST",
        "NOTSENDER",
        "SENDER",
        "REPLY-TO",
        "REJECT",
        "EXPUNGE",
        "LISTSERV",
        "ARCHIVE",
        "CONFIRM",
    }
    
    # Prefixes for inactive/commented lines
    INACTIVE_PREFIXES = ("!", "#")
    
    def __init__(self):
        """Initialize the parser."""
        self.file_path: Optional[Path] = None
        self.file_content: List[str] = []
        self.list_name: Optional[str] = None
        self.active_emails: List[str] = []
        self.email_metadata_list: List[EmailMetadata] = []
    
    def parse_file(self, file_path: str) -> Dict:
        """
        Parse a Mailkeeper .org file.
        
        Args:
            file_path: Path to the .org file to parse
            
        Returns:
            Dictionary containing:
            - list_name: Distribution list name
            - emails: List of active email addresses
            - metadata: List of EmailMetadata objects
            - email_count: Count of active emails
            
        Raises:
            MailkeeperParseException: If file invalid or doesn't contain MAILINGLIST
            FileNotFoundError: If file doesn't exist
            IOError: If file cannot be read
        """
        self.file_path = Path(file_path)
        
        # Validate file exists
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not self.file_path.is_file():
            raise MailkeeperParseException(f"Path is not a file: {file_path}")
        
        # Read file content with encoding fallback
        self._read_file()
        
        # Check if this is a valid Mailkeeper file
        if not self._is_mailinglist_file():
            raise MailkeeperParseException(
                f"File does not contain MAILINGLIST directive: {file_path}"
            )
        
        # Extract list name
        self.list_name = self._extract_list_name()
        
        # Extract active emails
        self.active_emails = self._extract_emails()
        
        # Generate metadata for each email
        self.email_metadata_list = [
            self._parse_email_metadata(email) for email in self.active_emails
        ]
        
        return {
            "list_name": self.list_name,
            "emails": self.active_emails,
            "metadata": self.email_metadata_list,
            "email_count": len(self.active_emails),
            "file_path": str(self.file_path),
        }
    
    def _read_file(self) -> None:
        """
        Read file content with UTF-8 fallback to latin-1.
        
        Raises:
            IOError: If file cannot be read with either encoding
        """
        encodings = ["utf-8", "latin-1"]
        
        for encoding in encodings:
            try:
                with open(self.file_path, "r", encoding=encoding) as f:
                    self.file_content = f.readlines()
                return
            except UnicodeDecodeError:
                continue
            except IOError as e:
                raise IOError(f"Cannot read file {self.file_path}: {e}")
        
        raise IOError(
            f"Cannot decode file {self.file_path} with any supported encoding"
        )
    
    def _is_mailinglist_file(self) -> bool:
        """
        Check if file contains MAILINGLIST directive.
        
        Returns:
            True if MAILINGLIST directive found, False otherwise
        """
        for line in self.file_content:
            line = line.strip()
            if line.startswith("MAILINGLIST"):
                return True
        return False
    
    def _extract_list_name(self) -> str:
        """
        Extract distribution list name from MAILINGLIST directive.
        
        Expected format: MAILINGLIST distribution.list.name@domain.org
        Also supports bare MAILINGLIST directive by deriving list name
        from the source file name.
        
        Returns:
            Distribution list name
            
        Raises:
            MailkeeperParseException: If MAILINGLIST directive malformed
        """
        for line in self.file_content:
            line = line.strip()
            if line.startswith("MAILINGLIST"):
                parts = line.split(maxsplit=1)
                
                if len(parts) < 2:
                    if self.file_path is None:
                        raise MailkeeperParseException(
                            "MAILINGLIST directive missing list name"
                        )
                    return self.file_path.name
                
                list_name = parts[1].strip()
                
                if not list_name:
                    raise MailkeeperParseException(
                        "MAILINGLIST directive has empty list name"
                    )
                
                return list_name
        
        raise MailkeeperParseException("MAILINGLIST directive not found")
    
    def _extract_emails(self) -> List[str]:
        """
        Extract all active email addresses from the file.
        
        Rules:
        - Skip lines starting with ! (inactive/commented)
        - Skip lines starting with # (comments)
        - Skip lines that are directives
        - Extract only valid email addresses
        
        Returns:
            List of active email addresses
        """
        emails = []
        
        for line in self.file_content:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Skip inactive/commented lines
            if line.startswith(self.INACTIVE_PREFIXES):
                continue
            
            # Skip directives
            if line.split(maxsplit=1)[0] in self.DIRECTIVES:
                continue
            
            # Validate email format
            if self.EMAIL_REGEX.match(line):
                emails.append(line)
        
        return emails
    
    def _parse_email_metadata(self, email: str) -> EmailMetadata:
        """
        Parse email metadata and generate contact information.
        
        From email: user.name@example.com
        Generated:
        - first_name: "username" (username without periods)
        - last_name: "example" (domain without periods and TLD)
        - display_name: "username example"
        - description: "External contact - example.com"
        
        Args:
            email: Email address to parse
            
        Returns:
            EmailMetadata object with generated contact info
        """
        # Split email into parts
        local_part, domain = email.rsplit("@", 1)
        
        # Generate first_name: remove all periods from local part
        first_name = local_part.replace(".", "")
        
        # Generate last_name: remove periods from domain and strip TLD
        domain_parts = domain.split(".")
        
        # Remove TLD (last part) and rejoin remaining parts without periods
        if len(domain_parts) > 1:
            # Join all but the last part (TLD) and remove periods
            domain_base = "".join(domain_parts[:-1])
        else:
            # Single part domain, use it as-is
            domain_base = domain.replace(".", "")
        
        last_name = domain_base
        
        # Generate display_name
        display_name = f"{first_name} {last_name}"
        
        # Generate description
        description = f"External contact - {domain}"
        
        return EmailMetadata(
            email=email,
            first_name=first_name,
            last_name=last_name,
            display_name=display_name,
            description=description,
        )
