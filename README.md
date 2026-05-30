# CBCMGROUPS Email Distribution List Migration Tool

Migrate email addresses from Mailkeeper private email service to Microsoft 365, enabling gradual retirement of the private email server while maintaining email delivery reliability.

## Overview

This tool automates the migration of distribution lists and email addresses from Mailkeeper to MS365. It provides a three-phase workflow for safely extracting, analyzing, creating MS365 groups, and cleaning up the original Mailkeeper files.

**Current Status**: 🚧 In Development (Pre-release)

## Features

- **Phase 1: Extract & Analyze**
  - Scan Mailkeeper distribution list files (.org format)
  - Filter emails by domain(s)
  - Export migration data as JSON
  - Preview distribution lists and matched emails

- **Phase 2: MS365 Export**
  - Import MS365 credentials securely (no hardcoded credentials)
  - Authenticate with MS365 via OAuth device code flow
  - Validate distribution list owner in MS365
  - Automatically create MS365 distribution groups
  - Create organizational contacts for external emails
  - Add members to distribution groups
  - Real-time progress tracking with detailed logging
  - Export verification reports (JSON + CSV)

- **Phase 3: Mailkeeper Cleanup**
  - Automatic backup before modifications
  - Add MS365 distribution list as active member
  - Comment out successfully migrated emails
  - Preserve file structure and directives
  - Rollback capability if needed

- **Safety Features**
  - Automatic backups before any modifications
  - Rollback functionality to restore original state
  - Idempotent operations (safe to re-run)
  - Comprehensive error handling and logging
  - Audit trail of all operations

## System Requirements

- **Operating System**: Windows 10 or Windows 11
- **Python**: 3.10 or higher (for development/source installation)
- **MS365**: Active Microsoft 365 subscription with admin access
- **Network**: Internet connection for MS Graph API
- **Storage**: ~100 MB for application and backups

### Optional Requirements

- Azure AD with app registration configured
- Mailkeeper directory with .org files (distribution list files)

## Installation

### Option 1: Installer (Recommended for End Users)

1. Download the latest installer: `CBCMGROUPS-Migration-Tool-v1.0.0-Setup.exe`
2. Run the installer
3. Follow the installation wizard
4. Choose installation directory (default: `Program Files`)
5. Complete installation
6. Launch from Start menu or Desktop shortcut

### Option 2: From Source (For Development)

```bash
# Clone repository
git clone <repo-url>
cd CBCMGROUPS-Email-Distribution-List

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python src/main.py
```

## Quick Start

### Prerequisites

1. **Azure AD Setup** (one-time)
   - Register application in Azure AD
   - Configure OAuth permissions
   - Note your Tenant ID and Client ID
   - See [Azure Setup Guide](docs/AZURE_SETUP.md) for detailed steps

2. **MS365 Credentials**
   - Create `credential.json` with your Azure AD credentials
   - See [Credential Setup Guide](docs/CREDENTIAL_SETUP.md)

3. **Mailkeeper Files**
   - Locate your Mailkeeper directory with distribution list files (.org)
   - Example: `C:\Mailkeeper\distlists\`

### Basic Workflow

```
Phase 1: Extract & Analyze
  ↓
1. Select Mailkeeper folder with .org files
2. Enter domain(s) to filter (e.g., "gmail.com,hotmail.com")
3. Click "Scan Distribution Lists"
4. Review results and export JSON

Phase 2: MS365 Export
  ↓
1. Import credential.json file
2. Load migration JSON from Phase 1
3. Enter distribution list owner email
4. Click "Authenticate with MS365"
5. Click "Start Migration"
6. Wait for completion and export results

Phase 3: Mailkeeper Cleanup
  ↓
1. Load verification JSON from Phase 2
2. Review before/after preview
3. Click "Create Backup" (automatic backup created)
4. Click "Apply Cleanup" to modify Mailkeeper files
5. Verify completion report
```

## Detailed Usage

### Phase 1: Extract & Analyze

**Purpose**: Identify and extract emails from Mailkeeper distribution lists

**How to use**:
1. Click "Select Folder" and navigate to your Mailkeeper directory
2. Enter domain filters (comma-separated, e.g., `gmail.com,yahoo.com`)
3. Click "Scan Distribution Lists"
4. Review the results table showing:
   - Distribution list name
   - Total members
   - Matched emails (filtered by domain)
5. Click "View Details" to see full member lists
6. Click "Export to JSON" to save migration data

**Output**: Migration JSON file containing:
- Migration configuration
- Distribution lists with matched emails
- Summary statistics

### Phase 2: MS365 Export

**Purpose**: Create MS365 distribution groups and organizational contacts

**Prerequisites**:
- Completed Phase 1
- Azure AD app registered
- `credential.json` file with credentials

**How to use**:
1. Click "Import MS365 Credentials" and select your `credential.json`
2. Click "Load Migration JSON" and select Phase 1 output
3. Enter distribution list owner email (required)
4. Click "Validate Owner" to confirm owner exists in MS365
5. Click "Authenticate with MS365" to login
6. Review migration preview
7. Click "Start Migration" to begin
8. Monitor progress in real-time log
9. Once complete, click "Export Results"

**Output**: 
- Verification JSON (successful migrations only)
- CSV log (detailed status for all emails)
- Real-time log display

### Phase 3: Mailkeeper Cleanup

**Purpose**: Update Mailkeeper files to reflect MS365 migration

**How to use**:
1. Click "Load Verification JSON" from Phase 2 output
2. Review "Preview Changes" showing:
   - Files to be modified
   - Number of changes per file
3. Click "View Details" for before/after diff
4. Click "Create Backup" (automatic backup also created)
5. Click "Apply Cleanup" with confirmation dialog
6. Review completion report
7. Optional: Click "Rollback" to restore original files

**Changes made**:
- MS365 distribution list added as active member (no `!` prefix)
- Successfully migrated emails commented out with `!ALIAS` prefix
- Failed emails remain active (unchanged) for manual review

## Architecture

### Technology Stack
- **Language**: Python 3.10+
- **GUI Framework**: PyQt5
- **API**: Microsoft Graph API (MS365)
- **Authentication**: OAuth 2.0 device code flow
- **Packaging**: PyInstaller + Inno Setup

### Project Structure

```
CBCMGROUPS-Email-Distribution-List/
├── src/
│   ├── main.py                 # Application entry point
│   ├── ui/
│   │   ├── main_window.py      # Main window with 3 phases
│   │   ├── phase1_widget.py    # Extract & Analyze phase
│   │   ├── phase2_widget.py    # MS365 Export phase
│   │   └── phase3_widget.py    # Cleanup phase
│   ├── parsers/
│   │   └── mailkeeper_parser.py    # Mailkeeper .org file parser
│   ├── services/
│   │   └── ms_graph_service.py     # MS Graph API integration
│   ├── utils/
│   │   ├── credential_loader.py    # Load credential.json
│   │   ├── backup_manager.py       # Backup/restore functionality
│   │   ├── validator.py            # Input validation
│   │   └── logger.py               # Logging utilities
│   ├── models/
│   │   └── migration_data.py   # Data models for JSON
│   └── config/
│       └── settings.py         # Configuration constants
├── docs/
│   ├── AZURE_SETUP.md          # Azure AD setup guide
│   ├── CREDENTIAL_SETUP.md     # Credential file guide
│   ├── USER_GUIDE.md           # Complete user manual
│   └── TROUBLESHOOTING.md      # Common issues
├── tests/                       # Unit tests
├── installer/                   # Packaging scripts
├── backups/                     # Auto-generated backup folder
├── logs/                        # Auto-generated log folder
├── exports/                     # Auto-generated export folder
├── requirements.txt             # Python dependencies
└── credential.json.example      # Example credential template
```

## Configuration

### credential.json (Required for Phase 2)

Create a `credential.json` file with your Azure AD credentials:

```json
{
  "credentials": {
    "tenant_id": "your-azure-tenant-id",
    "client_id": "your-azure-app-id",
    "ms365_domain": "your-domain.com"
  }
}
```

**Security**: Never commit `credential.json` to version control. Add to `.gitignore`.

### Preferences

The application saves user preferences including:
- Last-used Mailkeeper folder path
- Last-used domain filters
- UI window size and position

## Security

### Credential Management
- Credentials loaded from file at runtime, never hardcoded
- Credentials stored in memory only, not persisted to disk
- File permissions restricted to current user
- Credentials masked in UI display (first 8 chars only)

### Backup & Rollback
- Automatic backup before any Mailkeeper file modifications
- Backup includes metadata and file hashes
- Rollback verifies backup integrity before restoring
- Manual backup creation available before cleanup

### Audit Trail
- All operations logged with timestamp and details
- Authentication attempts logged
- API calls logged for troubleshooting
- Log files stored in `logs/` folder

### Best Practices
1. Restrict file permissions on `credential.json`
2. Store credentials in secure location
3. Review logs regularly for suspicious activity
4. Create backup before first-time migrations
5. Test with small domain first

## Documentation

- **[DEVELOPMENT_CHECKLIST.md](DEVELOPMENT_CHECKLIST.md)** - Detailed implementation steps (for developers)
- **[logic_requirement.txt](logic_requirement.txt)** - High-level requirements and architecture
- **[docs/AZURE_SETUP.md](docs/AZURE_SETUP.md)** - Azure AD configuration guide
- **[docs/CREDENTIAL_SETUP.md](docs/CREDENTIAL_SETUP.md)** - Credential file setup
- **[docs/USER_GUIDE.md](docs/USER_GUIDE.md)** - Complete user manual with screenshots
- **[docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)** - Common issues and solutions

## Troubleshooting

### "Invalid credential file" Error
- Ensure `credential.json` is valid JSON
- Verify all required fields present (tenant_id, client_id, ms365_domain)
- Check GUID format for IDs

### "Authentication Failed" Error
- Verify credentials in `credential.json` are correct
- Check Azure AD app permissions are configured
- Ensure user has MS365 admin access

### "File Not Found" Error
- Verify Mailkeeper folder path is correct
- Check file permissions (readable by current user)
- Ensure .org files exist in folder

### "Network Timeout" Error
- Check internet connection
- Verify MS365 is accessible
- Try again after a few minutes

See [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for more issues.

## Development

### Running from Source

```bash
# Activate virtual environment
venv\Scripts\activate

# Run tests
python -m pytest tests/

# Run application
python src/main.py

# Build installer
python installer/build_installer.py
```

### Testing
- Unit tests: `pytest tests/`
- Integration tests: Manual testing with test MS365 tenant
- End-to-end: Complete migration workflow

## Contributing

This project is currently in development. Contributing guidelines coming soon.

## License

[License information to be added]

## Support

For issues or questions:
1. Check [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
2. Review [USER_GUIDE.md](docs/USER_GUIDE.md)
3. Check [AZURE_SETUP.md](docs/AZURE_SETUP.md) for Azure configuration
4. Contact administrator

## Version History

**v1.0.0** (In Development)
- Initial development

---

**Last Updated**: May 30, 2026
