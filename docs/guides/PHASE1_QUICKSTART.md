# Phase 1 Quick Start Guide

## Running the Application

### Option 1: Using the Run Script (Recommended)
```bash
# Windows
run_app.bat

# Or double-click run_app.bat in File Explorer
```

### Option 2: Manual Launch
```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Run application
python src/main.py
```

## Using Phase 1: Extract & Analyze

### Step-by-Step Instructions

1. **Start the Application**
   - Run `run_app.bat` or use manual launch
   - The application window will open with "Phase 1: Extract & Analyze" tab

2. **Configure Domain Filter** (Optional)
   - Enter domain(s) to filter emails (e.g., `gmail.com, yahoo.com`)
   - Leave empty to include all emails
   - Use comma-separated values for multiple domains

3. **Select Mailkeeper Folder**
   - Click the "Browse..." button
   - Navigate to your Mailkeeper folder containing `.org` files
   - For testing, use: `tests/tempmail/`
   - Click "Select Folder"

4. **Scan Distribution Lists**
   - Click "Scan Distribution Lists" button
   - Progress bar will show scanning progress
   - Status label shows current file being processed

5. **Review Results**
   - Results table displays:
     - Distribution List Name
     - Total Members count
     - Matched Emails count (filtered by domain)
     - MS365 List Name (with .ms365 suffix)
     - File Path
   - Summary statistics show totals at bottom

6. **View Details** (Optional)
   - Select a row in the results table
   - Click "View Details" button
   - Dialog shows all matched email addresses

7. **Export to JSON**
   - Click "Export to JSON" button
   - Choose save location (default: `exports/` folder)
   - File contains migration configuration for Phase 2

8. **Clear Results** (Optional)
   - Click "Clear Results" to reset and scan again

## Testing with Sample Data

The project includes sample distribution lists in `tests/tempmail/`:
- `distribution.list1@example.org`
- `team.contacts@example.org`
- `vendor.list@example.org`

### Test Scenario 1: Scan All Emails
1. Set Mailkeeper Folder: `tests/tempmail/`
2. Leave Domain Filter empty
3. Click "Scan Distribution Lists"
4. Should find 3 lists with ~12 total emails

### Test Scenario 2: Filter by Domain
1. Set Mailkeeper Folder: `tests/tempmail/`
2. Set Domain Filter: `gmail.com`
3. Click "Scan Distribution Lists"
4. Should find only Gmail addresses

## JSON Export Format

The exported JSON file contains:

```json
{
  "migration_config": {
    "target_domain": "gmail.com",
    "scan_date": "2026-06-01T10:30:00",
    "mailkeeper_folder": "C:/path/to/tempmail",
    "ms365_domain": "example.org"
  },
  "distribution_lists": [
    {
      "original_name": "distribution.list1@example.org",
      "ms365_name": "distribution.list1.ms365@example.org",
      "file_path": "C:/path/to/distribution.list1@example.org",
      "matched_emails": ["user1@gmail.com", "user2@gmail.com"],
      "all_members_count": 10,
      "matched_count": 2
    }
  ],
  "summary": {
    "total_lists": 3,
    "lists_with_matches": 2,
    "total_emails_to_migrate": 5,
    "total_all_emails": 12
  }
}
```

## Troubleshooting

### Application Won't Start
- Ensure virtual environment is created: `python -m venv .venv`
- Install dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (requires 3.10+)

### No .org Files Found
- Verify folder path is correct
- Ensure folder contains files with `.org` extension
- Check that files contain `MAILINGLIST` directive

### PyQt5 Errors
- Reinstall PyQt5: `pip install --force-reinstall PyQt5`
- Check for conflicting Qt installations

### Empty Results
- Check that .org files contain `MAILINGLIST` directive
- Verify email format is valid
- Check domain filter spelling

## User Preferences

The application automatically saves:
- Last used Mailkeeper folder path
- Last used domain filter

Preferences are stored in: `~/.cbcmgroups_migration_prefs.json`

## Next Steps

After exporting JSON from Phase 1:
1. Save the JSON file in a safe location
2. Use this file as input for Phase 2 (MS365 Export) when available
3. The JSON contains all necessary configuration for migration

## Support

For issues or questions:
1. Check this guide first
2. Review the main README.md
3. Check the Development Checklist for project status
4. Review test files for usage examples
