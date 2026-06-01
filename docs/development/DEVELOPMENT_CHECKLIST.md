# DEVELOPMENT CHECKLIST
## CBCMGROUPS Email Distribution List Migration Tool

**Project Goal**: Migrate email addresses from Mailkeeper private email service to MS365, enabling gradual retirement of the private email server while maintaining email delivery reliability.

---

## Overview

This checklist breaks down the development into 11 major steps, each with detailed tasks, acceptance criteria, and dependencies. Mark items as complete using `[x]` as you progress.

**Technology Stack**: Python 3.10+, PyQt5, MS Graph API, PyInstaller, Inno Setup

---

## Phase 1: Foundation & Core Parsing

### Step 1: Setup Project Structure

**Priority**: High  
**Estimated Time**: 2 hours  
**Dependencies**: None

- [x] Create Python virtual environment (`python -m venv venv`)
- [x] Activate virtual environment (`venv\Scripts\activate` on Windows)
- [x] Create `.gitignore` file (Python, IDE, OS-specific)
- [x] Create folder structure:
  - [x] `src/` (main application code)
  - [x] `src/parsers/` (Mailkeeper parser)
  - [x] `src/services/` (MS365 integration)
  - [x] `src/ui/` (PyQt5 UI components)
  - [x] `src/models/` (data models)
  - [x] `src/utils/` (utilities)
  - [x] `docs/` (documentation)
  - [x] `tests/` (unit tests)
  - [x] `installer/` (packaging scripts)
  - [x] `backups/` (backup storage - created by app)
  - [x] `logs/` (application logs - created by app)
  - [x] `exports/` (output files - created by app)
- [x] Create `requirements.txt` with dependencies:
  ```
  PyQt5>=5.15.0
  requests>=2.31.0
  msal>=1.20.0
  python-dotenv>=1.0.0
  ```
- [x] Install dependencies (`pip install -r requirements.txt`)
- [x] Create `src/__init__.py`
- [x] Create `src/config/settings.py` with constants
- [x] Initialize Git repository (`git init`)
- [x] Create initial commit

**Acceptance Criteria**:
- ✅ Virtual environment activates successfully
- ✅ All folders created
- ✅ Dependencies installed without errors
- ✅ Git repository initialized

---

### Step 2: Implement Mailkeeper Parser

**Priority**: High  
**Estimated Time**: 6 hours  
**Dependencies**: Step 1

- [x] Create `src/parsers/__init__.py`
- [x] Create `src/parsers/mailkeeper_parser.py`
- [x] Implement `MailkeeperParser` class with methods:
  - [x] `parse_file(file_path)` - main parsing method
  - [x] `_is_mailinglist_file()` - check for MAILINGLIST directive
  - [x] `_extract_list_name()` - parse list name from MAILINGLIST
  - [x] `_extract_emails()` - get active email addresses
  - [x] `_parse_email_metadata()` - generate contact info
- [x] Parsing logic:
  - [x] Check file contains MAILINGLIST directive (skip files without it)
  - [x] Extract distribution list name from MAILINGLIST directive
  - [x] Read all lines and filter:
    - [x] Skip lines starting with `!` (commented/inactive: !ALIAS, !ACCEPT, etc.)
    - [x] Skip directive lines (MAILINGLIST, DELAYGREYLIST, NOTSENDER, etc.)
    - [x] Skip comment lines starting with `#`
    - [x] Extract only plain email addresses (active members)
  - [x] Validate email format using regex
- [x] Email metadata parsing:
  - [x] Split email into username and domain
  - [x] Generate first_name: remove all periods from username
  - [x] Generate last_name: remove periods from domain, strip TLD (.com/.org/.gov/.net)
  - [x] Generate display_name: `{first_name} {last_name}`
  - [x] Generate description: `External contact - {original_domain}`
  - [x] Example: `user.name@example.com` →
    ```json
    {
      "email": "user.name@example.com",
      "first_name": "username",
      "last_name": "example",
      "display_name": "username example",
      "description": "External contact - example.com"
    }
    ```
- [x] Handle file encoding (UTF-8 with fallback to latin-1)
- [x] Add error handling for:
  - [x] File not found
  - [x] Permission errors
  - [x] Malformed email addresses
  - [x] Invalid file format
- [x] Create `tests/test_mailkeeper_parser.py`
- [x] Write unit tests covering:
  - [x] Valid .org file parsing
  - [x] Skipping commented lines (! prefix)
  - [x] Email metadata generation
  - [x] Edge cases (empty files, no MAILINGLIST directive)
  - [x] Malformed emails
- [x] Test with sample files from `tempmail/` folder
- [x] Verify test coverage (aim for >90%)

**Acceptance Criteria**:
- ✅ Parser correctly extracts only active emails (skips ! prefixed lines)
- ✅ Metadata generated correctly for all email formats
- ✅ Unit tests pass with high coverage (23 tests passing)
- ✅ Handles edge cases gracefully

---

## Phase 2: UI - Extract & Analyze

### Step 3: Build Phase 1 UI - Extract & Analyze

**Priority**: High  
**Estimated Time**: 8 hours  
**Dependencies**: Steps 1, 2

- [x] Create `src/ui/__init__.py`
- [x] Create `src/ui/phase1_widget.py`
- [x] Implement `Phase1Widget` class (inherits from QWidget):
  - [x] Domain filter input (text field, supports comma-separated domains)
  - [x] Folder path selector with browse button (QFileDialog)
  - [x] "Scan Distribution Lists" button
  - [x] Results table (QTableWidget) with columns:
    - [x] Distribution List Name
    - [x] Total Members
    - [x] Matched Emails (filtered by domain)
    - [x] File Path
  - [x] Summary statistics panel:
    - [x] Total lists scanned
    - [x] Lists with matches
    - [x] Total emails to migrate
  - [x] "View Details" button (shows full member list in dialog)
  - [x] "Export to JSON" button
  - [x] Progress bar for scanning operation
  - [x] Status label for feedback messages
  - [x] "Clear Results" button
- [x] Implement scanning logic:
  - [x] Recursively find all .org files in selected folder
  - [x] Parse each file using MailkeeperParser
  - [x] Filter emails by domain(s)
  - [x] Populate results table
  - [x] Update summary statistics
- [x] Generate MS365 naming (append `.ms365` before domain):
  - [x] `distribution.list1@example.org` → `distribution.list1.ms365@example.org`
- [x] Export JSON structure:
  ```json
  {
    "migration_config": {
      "target_domain": "gmail.com",
      "scan_date": "ISO timestamp",
      "mailkeeper_folder": "path",
      "ms365_domain": "example.org"
    },
    "distribution_lists": [
      {
        "original_name": "distribution.list1@example.org",
        "ms365_name": "distribution.list1.ms365@example.org",
        "file_path": "C:/path/to/distribution.list1@example.org",
        "matched_emails": [...],
        "all_members_count": 150,
        "matched_count": 23
      }
    ],
    "summary": {...}
  }
  ```
- [x] Save/load last-used folder path (user preferences)
- [x] Add error handling and user feedback
- [x] Create tests for Phase1Widget

**Acceptance Criteria**:
- ✅ Can select folder and scan .org files
- ✅ Domain filtering works correctly
- ✅ Results display accurately in table
- ✅ JSON export creates valid migration config
- ✅ UI is responsive during scanning
- ✅ User preferences persist between sessions

---

## Phase 3: MS365 Integration

### Step 4: Implement MS Graph API Integration

**Priority**: High  
**Estimated Time**: 12 hours  
**Dependencies**: Step 1

- [ ] Create `src/services/__init__.py`
- [ ] Create `src/services/ms_graph_service.py`
- [ ] Implement `MSGraphService` class with methods:
  - [ ] `authenticate()` - OAuth device code flow
  - [ ] `validate_owner()` - check owner email exists in MS365
  - [ ] `get_contact()` - check if org contact exists
  - [ ] `create_contact()` - create org contact
  - [ ] `get_group()` - check if distribution group exists
  - [ ] `create_distribution_group()` - create MS365 group
  - [ ] `add_member()` - add contact to group
  - [ ] `get_group_members()` - list current members
  - [ ] `_make_request()` - generic API call handler
- [ ] OAuth device code flow:
  - [ ] Display device code and URL to user
  - [ ] Poll for token acquisition
  - [ ] Store access token securely (in-memory)
  - [ ] Handle token expiration and refresh
- [ ] Contact operations:
  - [ ] Create org contact with first_name, last_name, display_name, email, description
  - [ ] Check if contact exists by email before creating
  - [ ] Return "ALREADY_EXISTS" if contact found
  - [ ] Return "SUCCESS" if created
  - [ ] Return "ERROR" with message if failed
- [ ] Group operations:
  - [ ] Create distribution group with name, email, owner
  - [ ] Check if group exists by email before creating
  - [ ] Add contacts as members to group
  - [ ] Check if member already in group before adding
  - [ ] Handle bulk member operations
- [ ] Validation:
  - [ ] Validate owner email exists in MS365
  - [ ] Validate email format before API calls
  - [ ] Validate group naming convention (*.ms365@example.org)
- [ ] Error handling:
  - [ ] Retry logic with exponential backoff (3 retries)
  - [ ] Rate limiting (respect 429 throttling responses)
  - [ ] Handle common errors (401, 403, 404, 500)
  - [ ] Log all API calls for audit trail
- [ ] Required API permissions (document in Azure setup guide):
  - [ ] `Group.ReadWrite.All`
  - [ ] `Directory.ReadWrite.All`
  - [ ] `OrgContact.ReadWrite.All`
- [ ] Create `tests/test_ms_graph_service.py`
- [ ] Write unit tests with mocked API responses

**Acceptance Criteria**:
- OAuth flow completes successfully
- All operations are idempotent (check before create)
- API errors handled gracefully with retries
- Rate limiting prevents throttling
- Unit tests pass with mocked API calls
- Audit logging captures all operations

---

### Step 4.5: MS365 Credential Configuration

**Priority**: High  
**Estimated Time**: 4 hours  
**Dependencies**: Step 4

**Overview**: Implement secure credential file loading mechanism. Credentials will NOT be hardcoded in the application. Instead, users will provide a `credential.json` file that the application loads at runtime via a UI import button.

#### Credential Requirements

MS365 migration requires the following credentials for OAuth device code flow authentication:

1. **Azure AD Tenant ID** (Directory ID)
   - Unique identifier for your Azure AD tenant
   - Format: GUID (e.g., `12345678-1234-1234-1234-123456789012`)
   - Where to find: Azure Portal → Azure Active Directory → Overview → Tenant ID

2. **Azure AD Application ID** (Client ID)
   - Identifier of the registered Azure AD application
   - Format: GUID (e.g., `87654321-4321-4321-4321-210987654321`)
   - Where to find: Azure Portal → App registrations → Your App → Application (client) ID

3. **MS365 Domain** (Organization domain)
   - Your MS365 organization's domain (e.g., `cbcmgroups.org`)
   - Used to scope all API operations to your organization
   - Where to find: MS365 Admin Center → Settings → Organization profile → Domain name

#### credential.json Structure

Create a `credential.json` file with the following structure:

```json
{
  "credentials": {
    "tenant_id": "12345678-1234-1234-1234-123456789012",
    "client_id": "87654321-4321-4321-4321-210987654321",
    "ms365_domain": "cbcmgroups.org"
  }
}
```

**Field Definitions**:
- `tenant_id`: Azure AD Tenant ID (required)
- `client_id`: Azure AD Application ID (required)
- `ms365_domain`: MS365 organization domain (required)

#### Security Best Practices

**IMPORTANT**: The `credential.json` file contains sensitive information. Follow these security practices:

1. **Never commit to version control**: Add `credential*.json` to `.gitignore`
2. **Restrict file permissions**: 
   - On Windows: Use NTFS permissions to restrict to current user only
   - On Linux/Mac: Use `chmod 600 credential.json` (read/write for owner only)
3. **Store securely**: Keep credential file in a secure location (not shared network drives)
4. **Single user per file**: Each user should maintain their own credential file
5. **Audit trail**: Application logs all authentication attempts (see logs folder)

#### Implementation Tasks

- [ ] Create `src/utils/credential_loader.py` with functions:
  - [ ] `load_credentials_from_file(file_path)` - Read and validate credential.json
  - [ ] `validate_credential_file(data)` - Verify all required fields present
  - [ ] `validate_credentials_with_ms365(credentials)` - Optional: test OAuth flow with provided credentials
- [ ] Implement credential validation:
  - [ ] Check file exists
  - [ ] Parse valid JSON format
  - [ ] Verify all required fields (tenant_id, client_id, ms365_domain)
  - [ ] Validate field formats (GUID format for IDs, domain format for ms365_domain)
  - [ ] Return error messages for missing/invalid fields
- [ ] Update `MSGraphService` class:
  - [ ] Accept credentials dictionary in `__init__()`
  - [ ] Use provided tenant_id and client_id for OAuth instead of hardcoded values
  - [ ] Use provided ms365_domain for scoping API requests
- [ ] Create credential file template:
  - [ ] Create `credential.json.example` in project root
  - [ ] Include example values and field descriptions
  - [ ] Add security warnings in comments
- [ ] Error handling:
  - [ ] Handle file not found gracefully
  - [ ] Provide clear error messages for JSON parsing errors
  - [ ] Validate GUID format for tenant_id and client_id
  - [ ] Validate domain format for ms365_domain
- [ ] Create `tests/test_credential_loader.py`
  - [ ] Test valid credential file loading
  - [ ] Test missing required fields error handling
  - [ ] Test invalid JSON format handling
  - [ ] Test invalid GUID format detection
  - [ ] Test invalid domain format detection

**Acceptance Criteria**:
- Credential file loads successfully when all fields valid
- Clear error messages provided for missing/invalid fields
- No credentials hardcoded in application code
- Credential loader is thoroughly tested
- Example credential.json file provided to users
- Security best practices documented

---

### Step 5: Build Phase 2 UI - MS365 Export

**Priority**: High  
**Estimated Time**: 10 hours  
**Dependencies**: Steps 3, 4

- [ ] Create `src/ui/phase2_widget.py`
- [ ] Implement `Phase2Widget` class (inherits from QWidget):
  - [ ] "Load Migration JSON" button (from Phase 1 export)
  - [ ] **Credential Management Section:**
    - [ ] "Import MS365 Credentials" button (file browser to select credential.json)
    - [ ] Credential status display showing:
      - [ ] Tenant ID (masked: show first 8 chars + *)
      - [ ] Client ID (masked: show first 8 chars + *)
      - [ ] MS365 Domain (fully visible)
      - [ ] Status indicator (✓ Loaded or ✗ Not loaded)
    - [ ] "Clear Credentials" button (remove loaded credentials from memory)
  - [ ] Display migration summary (lists count, emails count, domain)
  - [ ] Owner email configuration section:
    - [ ] Text input for owner email (required)
    - [ ] "Validate Owner" button
    - [ ] Status label (✓ Valid or ✗ Invalid)
  - [ ] "Authenticate with MS365" button (disabled until credentials loaded)
  - [ ] Authentication status display (connected/disconnected)
  - [ ] Migration preview table:
    - [ ] Columns: Original List, MS365 List, Email Count, Owner
    - [ ] Allow editing MS365 list name if needed
  - [ ] "Start Migration" button (disabled until owner validated, credentials loaded, and authenticated)
  - [ ] Progress section:
    - [ ] Overall progress bar
    - [ ] Current operation label
    - [ ] Success/error/skip counters
  - [ ] Real-time log display (QTextEdit with color coding):
    - [ ] Green for SUCCESS
    - [ ] Yellow for ALREADY_EXISTS
    - [ ] Red for ERROR
  - [ ] "Pause/Resume" button
  - [ ] "Cancel" button
  - [ ] "Export Results" button (enabled after completion)
- [ ] Migration workflow:
  - [ ] Load and parse Phase 1 JSON
  - [ ] Validate owner email via MS Graph API
  - [ ] Authenticate with MS365 (OAuth)
  - [ ] For each distribution list:
    - [ ] Check if group exists (skip creation if exists)
    - [ ] For each email:
      - [ ] Check if contact exists
      - [ ] Create contact if not exists
      - [ ] Track status: SUCCESS, ALREADY_EXISTS, or ERROR
    - [ ] Add all members to group
    - [ ] Update progress and log
  - [ ] Generate verification outputs
- [ ] Export verification JSON (SUCCESS + ALREADY_EXISTS only):
  ```json
  {
    "migration_date": "2026-05-30T10:30:00",
    "domain_filter": "gmail.com",
    "owner": "admin@example.org",
    "successfully_migrated": [
      {
        "original_list": "distribution.list1@example.org",
        "ms365_list": "distribution.list1.ms365@example.org",
        "status": "SUCCESS",
        "emails": ["contact1@example.com", "contact2@example.com"]
      }
    ]
  }
  ```
- [ ] Export CSV log (all emails with detailed status):
  ```csv
  Distribution List,Email,Status,Action,Error Message
  distribution.list1@example.org,contact1@example.com,SUCCESS,Created contact,
  distribution.list1@example.org,contact2@example.com,ALREADY_EXISTS,Reused existing contact,
  distribution.list1@example.org,contact3@example.com,ERROR,Failed to create contact,Invalid email format
  distribution.list1@example.org,GROUP,SUCCESS,Created distribution group,
  ```
- [ ] Implement pause/resume functionality
- [ ] Add summary statistics display
- [ ] Create tests for Phase2Widget

**Acceptance Criteria**:
- Owner validation works before migration
- OAuth flow completes within UI
- Progress updates in real-time
- Verification JSON contains only successful migrations
- CSV log includes all emails with detailed status
- Can pause/resume migration
- Summary statistics are accurate

---

## Phase 4: Backup & Cleanup

### Step 6: Implement Backup & Rollback System

**Priority**: High  
**Estimated Time**: 6 hours  
**Dependencies**: Step 2

- [ ] Create `src/utils/__init__.py`
- [ ] Create `src/utils/backup_manager.py`
- [ ] Implement `BackupManager` class with methods:
  - [ ] `create_backup()` - backup files before modification
  - [ ] `list_backups()` - list available backups
  - [ ] `restore_backup()` - rollback to previous state
  - [ ] `verify_backup()` - integrity check
  - [ ] `_calculate_hash()` - SHA-256 file hash
  - [ ] `_create_manifest()` - backup metadata
- [ ] Backup workflow:
  - [ ] Create timestamped backup folder in `backups/`
  - [ ] Copy original .org files to backup folder
  - [ ] Generate backup manifest (JSON) with:
    - [ ] Backup date/time
    - [ ] List of backed up files
    - [ ] File paths (original and backup)
    - [ ] File hashes (SHA-256)
    - [ ] File sizes
  - [ ] Save manifest to backup folder
- [ ] Backup manifest structure:
  ```json
  {
    "backup_date": "2026-05-30T10:30:00",
    "backup_id": "backup_20260530_103000",
    "files": [
      {
        "original": "tempmail/distribution.list1@example.org",
        "backup": "backups/backup_20260530_103000/distribution.list1@example.org",
        "hash": "sha256:abcdef123456...",
        "size": 15234
      }
    ]
  }
  ```
- [ ] Rollback functionality:
  - [ ] Select backup by ID or timestamp
  - [ ] Verify backup integrity (hash check)
  - [ ] Restore files to original locations
  - [ ] Confirm restoration success
- [ ] Add optional backup compression (ZIP)
- [ ] Implement backup rotation (keep last N backups - configurable)
- [ ] Add disk space check before backup
- [ ] Create backup log file
- [ ] Create `tests/test_backup_manager.py`
- [ ] Write unit tests for backup/restore operations

**Acceptance Criteria**:
- Backups created automatically before Phase 3
- Backup manifest accurate and complete
- Integrity checks pass for all backups
- Rollback restores files correctly
- Disk space checked before backup
- Unit tests pass

---

### Step 7: Build Phase 3 UI - Mailkeeper Cleanup

**Priority**: High  
**Estimated Time**: 8 hours  
**Dependencies**: Steps 5, 6

- [ ] Create `src/ui/phase3_widget.py`
- [ ] Implement `Phase3Widget` class (inherits from QWidget):
  - [ ] "Load Verification JSON" button (from Phase 2 export)
  - [ ] Display verification summary:
    - [ ] Total lists migrated
    - [ ] Total emails migrated successfully
    - [ ] Any errors/warnings from Phase 2
  - [ ] Warning display if errors detected
  - [ ] Preview changes section:
    - [ ] Table showing: File, Changes Count, Status
    - [ ] "View Details" button (shows before/after diff)
  - [ ] Before/after preview dialog:
    - [ ] Side-by-side or unified diff view
    - [ ] Highlight added lines (MS365 list)
    - [ ] Highlight modified lines (! prefix added)
  - [ ] "Create Backup" button (trigger manual backup)
  - [ ] Backup status display
  - [ ] "Apply Cleanup" button with confirmation dialog
  - [ ] Progress bar for cleanup operation
  - [ ] Completion report:
    - [ ] Files modified count
    - [ ] Emails commented out count
    - [ ] Errors if any
  - [ ] "Rollback" button (restore from backup)
- [ ] Cleanup logic:
  - [ ] Load verification JSON (Phase 2 output)
  - [ ] Create automatic backup via BackupManager
  - [ ] For each distribution list in verification:
    - [ ] Read original .org file
    - [ ] Add MS365 distribution list as ACTIVE member:
      - [ ] Add line: `distribution.list1.ms365@example.org` (NO ! prefix)
      - [ ] Insert near top after MAILINGLIST directive
    - [ ] For each successfully migrated email:
      - [ ] Find email line in file
      - [ ] Prefix with `!ALIAS ` (comment it out)
      - [ ] Example: `contact@example.com` → `!ALIAS contact@example.com`
    - [ ] Skip emails with ERROR status (leave active)
    - [ ] Preserve file structure and other directives
    - [ ] Write modified file back
  - [ ] Log all modifications
- [ ] Example cleanup transformation:
  ```
  BEFORE:
  MAILINGLIST listname
  contact1@example.com
  contact2@example.com
  internal@example.org
  
  AFTER:
  MAILINGLIST listname
  distribution.list1.ms365@example.org
  !ALIAS contact1@example.com
  !ALIAS contact2@example.com
  internal@example.org
  ```
- [ ] Safety confirmations:
  - [ ] Confirm before applying changes (show count)
  - [ ] Confirm before rollback (show backup details)
- [ ] Display completion summary
- [ ] Create tests for Phase3Widget

**Acceptance Criteria**:
- Verification JSON loads correctly
- Preview shows accurate before/after changes
- MS365 list added as active member (no ! prefix)
- Successfully migrated emails prefixed with !ALIAS
- Failed emails remain active
- Backup created before modifications
- Rollback restores original files
- Completion report accurate

---

## Phase 5: Hardening & Quality Assurance

### Step 8: Add Validation & Error Handling

**Priority**: High  
**Estimated Time**: 6 hours  
**Dependencies**: Steps 3, 5, 7

- [ ] Create `src/utils/validator.py`
- [ ] Implement validation functions:
  - [ ] `validate_email_format()` - regex check
  - [ ] `validate_json_schema()` - migration/verification JSON
  - [ ] `validate_file_path()` - exists and readable
  - [ ] `validate_folder_path()` - exists and has .org files
  - [ ] `validate_permissions()` - read/write access
  - [ ] `validate_disk_space()` - sufficient space for backups
  - [ ] `validate_ms365_connectivity()` - test API connection
- [ ] Add validations to Phase 1:
  - [ ] Folder path exists
  - [ ] Folder contains .org files
  - [ ] Read permission on files
  - [ ] Valid domain format
- [ ] Add validations to Phase 2:
  - [ ] Migration JSON schema valid
  - [ ] Owner email format valid
  - [ ] Owner exists in MS365
  - [ ] MS365 connectivity before migration
  - [ ] Distribution list name valid
- [ ] Add validations to Phase 3:
  - [ ] Verification JSON schema valid
  - [ ] Backup folder writable
  - [ ] Sufficient disk space
  - [ ] File paths in verification exist
- [ ] Implement global error handler:
  - [ ] Catch unhandled exceptions
  - [ ] Log errors to file
  - [ ] Display user-friendly error messages
  - [ ] Option to save error report
- [ ] Add logging throughout application:
  - [ ] Create `src/utils/logger.py`
  - [ ] Log to file in `logs/` folder
  - [ ] Rotate log files daily
  - [ ] Include timestamp, level, module, message
- [ ] Create comprehensive error messages:
  - [ ] Clear description of error
  - [ ] Suggested action to resolve
  - [ ] Reference to documentation
- [ ] Create `tests/test_validator.py`
- [ ] Write unit tests for all validation functions

**Acceptance Criteria**:
- All user inputs validated before processing
- Clear error messages displayed to user
- All operations logged to file
- Unhandled exceptions caught and logged
- Unit tests pass for all validators
- Application doesn't crash on invalid input

---

### Step 9: Create Azure AD App Registration Guide

**Priority**: Medium  
**Estimated Time**: 3 hours  
**Dependencies**: None (can be done in parallel)

- [ ] Create `docs/AZURE_SETUP.md`
- [ ] Document Azure AD app registration process:
  - [ ] Navigate to Azure Portal
  - [ ] Go to Azure Active Directory
  - [ ] Select "App registrations"
  - [ ] Click "New registration"
  - [ ] Configure app settings:
    - [ ] Name: "CBCMGROUPS Migration Tool"
    - [ ] Supported account types: Single tenant
    - [ ] Redirect URI: Public client/native (recommended)
  - [ ] Copy Application (client) ID
  - [ ] Copy Directory (tenant) ID
- [ ] Document API permissions configuration:
  - [ ] Click "API permissions"
  - [ ] Add permissions:
    - [ ] Microsoft Graph → Delegated permissions
    - [ ] `Group.ReadWrite.All` (Create and manage groups)
    - [ ] `Directory.ReadWrite.All` (Read and write directory data)
    - [ ] `OrgContact.ReadWrite.All` (Read and write org contacts)
  - [ ] Click "Grant admin consent"
- [ ] Document authentication configuration:
  - [ ] Enable "Allow public client flows"
  - [ ] Configure device code flow settings
- [ ] Add screenshots for each step
- [ ] Create troubleshooting section:
  - [ ] Permission denied errors
  - [ ] Token acquisition failures
  - [ ] Common configuration mistakes
- [ ] Add security best practices:
  - [ ] Principle of least privilege
  - [ ] Regular permission audits
  - [ ] Token security guidelines
- [ ] Create quick start checklist
- [ ] Add FAQ section

**Acceptance Criteria**:
- Complete step-by-step guide with screenshots
- All required permissions documented
- Troubleshooting section covers common issues
- Security best practices included
- Guide tested by non-technical user

---

### Step 10: Testing & Documentation

**Priority**: High  
**Estimated Time**: 12 hours  
**Dependencies**: Step 8

- [ ] **Integration Testing**:
  - [ ] Test Phase 1 (Extract & Analyze):
    - [ ] Scan folder with 10-20 test .org files
    - [ ] Verify domain filtering
    - [ ] Verify email counts match manual inspection
    - [ ] Verify JSON export structure
  - [ ] Test Phase 2 (MS365 Export):
    - [ ] Test with test MS365 tenant
    - [ ] Verify OAuth flow
    - [ ] Verify owner validation
    - [ ] Create test contacts and groups
    - [ ] Verify idempotent operations (run twice)
    - [ ] Verify verification JSON accuracy
    - [ ] Verify CSV log completeness
  - [ ] Test Phase 3 (Cleanup):
    - [ ] Verify backup creation
    - [ ] Verify .org file modifications
    - [ ] Verify MS365 list added as active
    - [ ] Verify migrated emails prefixed with !ALIAS
    - [ ] Verify failed emails remain active
    - [ ] Test rollback functionality
  - [ ] End-to-end test:
    - [ ] Complete migration for one domain
    - [ ] Verify email delivery through MS365
    - [ ] Test with 5-10 distribution lists
- [ ] **Error Handling Testing**:
  - [ ] Test with invalid JSON
  - [ ] Test with missing files
  - [ ] Test with malformed .org files
  - [ ] Test with invalid owner email
  - [ ] Test with MS365 API errors
  - [ ] Test with network disconnection
  - [ ] Test with insufficient permissions
  - [ ] Test with disk full scenario
- [ ] **Performance Testing**:
  - [ ] Test with 100+ distribution lists
  - [ ] Test with 1000+ emails per list
  - [ ] Monitor memory usage
  - [ ] Monitor API rate limiting
- [ ] **User Documentation**:
  - [ ] Create `docs/USER_MANUAL.md`:
    - [ ] Getting started guide
    - [ ] Phase 1 walkthrough with screenshots
    - [ ] Phase 2 walkthrough with screenshots
    - [ ] Phase 3 walkthrough with screenshots
    - [ ] Common workflows
    - [ ] Troubleshooting guide
    - [ ] FAQ
  - [ ] Update `README.md`:
    - [ ] Project description
    - [ ] Features list
    - [ ] System requirements
    - [ ] Installation instructions
    - [ ] Quick start guide
    - [ ] Links to detailed documentation
    - [ ] Contributing guidelines (if open source)
- [ ] **Inline Help**:
  - [ ] Add tooltips to all UI elements
  - [ ] Add help text for each phase
  - [ ] Add "Help" menu with links to documentation
  - [ ] Add "About" dialog with version info
- [ ] **Code Documentation**:
  - [ ] Add docstrings to all classes and methods
  - [ ] Add inline comments for complex logic
  - [ ] Generate API documentation (Sphinx or similar)

**Acceptance Criteria**:
- All integration tests pass
- Error handling tested for edge cases
- Performance acceptable with large datasets
- User manual complete with screenshots
- README comprehensive and clear
- All UI elements have tooltips
- Code fully documented

---

## Phase 6: Deployment & Distribution

### Step 11: Create Installation Package

**Priority**: High  
**Estimated Time**: 10 hours  
**Dependencies**: Step 10

- [ ] **PyInstaller Setup**:
  - [ ] Create `installer/build_installer.py`
  - [ ] Configure PyInstaller spec file:
    - [ ] Include all dependencies (PyQt5, msal, requests)
    - [ ] Bundle Python runtime
    - [ ] Set application icon
    - [ ] Configure one-file vs one-folder mode
    - [ ] Add version info and metadata
  - [ ] Test PyInstaller build:
    - [ ] Run `pyinstaller build_installer.py`
    - [ ] Verify executable works
    - [ ] Test on clean Windows machine (no Python)
  - [ ] Optimize build size:
    - [ ] Exclude unnecessary modules
    - [ ] Use UPX compression (if applicable)
- [ ] **Inno Setup Configuration**:
  - [ ] Create `installer/setup.iss`
  - [ ] Configure installer settings:
    - [ ] Application name and version
    - [ ] Publisher information
    - [ ] Default installation directory
    - [ ] Create desktop shortcut option
    - [ ] Create start menu entry
    - [ ] License agreement (if applicable)
  - [ ] Create custom installation wizard:
    - [ ] Welcome page
    - [ ] License agreement page
    - [ ] Installation directory selection
    - [ ] Component selection (optional)
    - [ ] Ready to install page
    - [ ] Installing progress page
    - [ ] Completion page
  - [ ] Include files in installer:
    - [ ] Application executable
    - [ ] README.md
    - [ ] `docs/AZURE_SETUP.md`
    - [ ] `docs/USER_MANUAL.md`
    - [ ] License file
  - [ ] Configure post-install actions:
    - [ ] Create `backups/` folder
    - [ ] Create `exports/` folder
    - [ ] Create `logs/` folder
    - [ ] Set folder permissions
- [ ] **Create Uninstaller**:
  - [ ] Configure Inno Setup uninstall
  - [ ] Prompt to keep/delete user data (backups, logs, exports)
  - [ ] Remove shortcuts and start menu entries
  - [ ] Clean registry entries (if any)
- [ ] **Version Management**:
  - [ ] Create `VERSION` file with version number
  - [ ] Add version display in application UI
  - [ ] Include version in installer filename
  - [ ] Document versioning scheme (semantic versioning)
- [ ] **Digital Signature** (optional but recommended):
  - [ ] Obtain code signing certificate
  - [ ] Sign executable with certificate
  - [ ] Sign installer with certificate
  - [ ] Verify signature validation
- [ ] **Testing Installation Package**:
  - [ ] Test on Windows 10
  - [ ] Test on Windows 11
  - [ ] Test on clean machine (no Python installed)
  - [ ] Test installation to different directories
  - [ ] Test with non-admin user (if applicable)
  - [ ] Test uninstallation
  - [ ] Test upgrade installation (over previous version)
- [ ] **Distribution Preparation**:
  - [ ] Create release notes document
  - [ ] Create installation guide
  - [ ] Package all documentation
  - [ ] Create checksum file (SHA-256) for installer
  - [ ] Upload to distribution location
- [ ] **Update Mechanism** (optional future enhancement):
  - [ ] Add update check functionality
  - [ ] Implement auto-update or update notification
  - [ ] Version comparison logic

**Acceptance Criteria**:
- PyInstaller creates working standalone executable
- Executable runs on clean Windows machine without Python
- Inno Setup creates professional installer
- Installer creates all required folders
- Desktop shortcut and start menu entry created
- Uninstaller removes application cleanly
- Installation tested on multiple Windows versions
- All documentation included in installer
- Version displayed in application
- Digital signature valid (if implemented)

---

## Pre-Release Checklist

Before releasing to production:

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Code review completed
- [ ] Documentation reviewed and complete
- [ ] Security review completed
- [ ] Performance benchmarks acceptable
- [ ] Azure setup guide tested
- [ ] Installation package tested on clean machines
- [ ] User manual reviewed by non-technical user
- [ ] Backup/rollback tested successfully
- [ ] Error handling tested for all edge cases
- [ ] Logging verified for audit trail
- [ ] Version numbers updated
- [ ] Release notes prepared
- [ ] Support process defined
- [ ] Training materials prepared (if needed)

---

## Important Notes

### Mailkeeper Parsing Rules
- **Active emails**: Plain email addresses with no prefix
- **Inactive emails**: Lines starting with `!` (e.g., `!ALIAS`, `!ACCEPT`)
- **Directives**: Skip lines like `MAILINGLIST`, `DELAYGREYLIST`, etc.
- **Comments**: Skip lines starting with `#`

### MS365 Naming Convention
- Original: `distribution.list1@example.org`
- MS365: `distribution.list1.ms365@example.org`

### Phase 3 Cleanup Logic
1. Add MS365 distribution list as **ACTIVE** member (no `!` prefix)
2. Prefix successfully migrated emails with `!ALIAS` (comments them out)
3. Leave failed emails **active** (unchanged) for retry

### Idempotency
- Always check if contacts/groups exist before creating
- Safe to re-run across different domains
- Supports gradual migration approach

### Required API Permissions
- `Group.ReadWrite.All` - Create and manage distribution groups
- `Directory.ReadWrite.All` - Read and write directory data
- `OrgContact.ReadWrite.All` - Create and manage org contacts

---

## Progress Tracking

**Current Status**: Step 3 Complete - Phase 1 UI Working

**Next Steps**: 
1. Move to Step 4 (MS Graph API Integration)
2. Implement Step 4.5 (MS365 Credential Configuration)
3. Continue with Step 5 (Phase 2 UI)

**Blockers**: None

---

**Last Updated**: June 1, 2026
