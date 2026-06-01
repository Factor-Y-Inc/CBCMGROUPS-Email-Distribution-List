# Phase 1 Filtering Rules

## Overview
Phase 1 automatically filters out certain distribution lists to optimize the migration process.

## Automatic Exclusions

### 1. Phone Number Distribution Lists
**Pattern**: 7-15 consecutive digits as the local part of the email address

**Examples**:
- `9876543210@domain.org` ✓ Skipped
- `5551234567@example.com` ✓ Skipped
- `12345678901@test.org` ✓ Skipped (11 digits)
- `team.contacts@domain.org` ✗ Not skipped (contains letters)
- `user123@domain.org` ✗ Not skipped (mixed alphanumeric)
- `123@domain.org` ✗ Not skipped (too short, <7 digits)

**Reason**: Phone number-based distribution lists are typically automated notifications, SMS gateways, or individual phone extensions rather than actual email distribution lists for migration.

**Console Output**: `Phone number lists skipped: X`

**Implementation**: Regex pattern `^\d{7,15}$` applied to local part before `@` symbol

---

### 2. Empty Distribution Lists
**Condition**: Lists with zero matching members after domain filtering is applied

**Example Scenario**:
- Distribution list has 5 members: all @yahoo.com addresses
- Domain filter applied: `gmail.com`
- Result: List skipped (0 gmail.com matches)

**Without Domain Filter**: If no domain filter is specified, lists are never skipped for being empty (all emails match)

**Reason**: Creating an empty MS365 distribution list serves no purpose and would require manual cleanup later.

**Console Output**: `Empty lists skipped (no matches): X`

**Implementation**: Checks `len(matched_emails) == 0` after domain filtering

---

## Console Logging

When scanning distribution lists, you'll see detailed statistics:

```
============================================================
Starting scan: C:\Mailkeeper\lists
Files found: 4000
Workers: 16
Domain filter: gmail.com
============================================================

Progress: 400/4000 (10%)
Progress: 800/4000 (20%)
Progress: 1200/4000 (30%)
...
Progress: 4000/4000 (100%)

============================================================
Scan complete!
Total files scanned: 4000
Distribution lists found: 3500
Phone number lists skipped: 250
Empty lists skipped (no matches): 250
Total members: 45,230
Matched members: 12,450
============================================================
```

### Understanding the Numbers

- **Total files scanned**: All `.org` files found in the folder
- **Distribution lists found**: Valid lists included in the export
- **Phone number lists skipped**: Lists matching the 7-15 digit pattern
- **Empty lists skipped**: Lists with no matching members (when domain filter applied)
- **Total members**: All email addresses across all found lists
- **Matched members**: Emails matching the domain filter (for export)

---

## Exported Data

### What Gets Exported

Only distribution lists that pass both filters are included in the JSON export:
1. ✅ Not a phone number list
2. ✅ Has at least one matching member (after domain filtering)

### Metadata Processing

Each email in the export includes:
- **Raw email**: Original address with all characters (periods, underscores, etc.)
- **Processed metadata**: Display names with periods/underscores removed

**Example**:
```json
{
  "matched_emails": ["user_name@gmail.com"],
  "metadata": [
    {
      "email": "user_name@gmail.com",        ← Raw email (underscore preserved)
      "first_name": "username",              ← Underscore removed for display
      "last_name": "gmail",
      "display_name": "username gmail",
      "description": "External contact - gmail.com"
    }
  ]
}
```

**Phase 2 Usage**: 
- MS365 import uses the raw email for the actual address
- Processed names are used for contact display names and organizational contact creation

---

## Customization

### Adjusting Phone Number Pattern

To modify the phone number detection pattern, edit `src/ui/phase1_widget.py`:

```python
def _is_phone_number_list(self, list_name: str) -> bool:
    local_part = list_name.split('@')[0] if '@' in list_name else list_name
    
    # Change the digit range here (currently 7-15)
    if re.match(r'^\d{7,15}$', local_part):
        return True
    
    return False
```

**Common adjustments**:
- US phone numbers only: `r'^\d{10}$'` (exactly 10 digits)
- Include international: `r'^\d{7,18}$'` (up to 18 digits)
- Include +prefix: `r'^\+?\d{7,15}$'` (optional + sign)

### Disabling Empty List Filtering

To disable empty list filtering, comment out this section in `_parse_single_file()`:

```python
# Skip lists with no matching members
# if len(matched_emails) == 0:
#     self.skipped_empty_lists += 1
#     return None
```

**Warning**: This may result in empty MS365 distribution groups that require manual cleanup.

---

## Troubleshooting

### Lists Not Appearing in Results

1. **Check Console Output**:
   - Look for skip statistics at the end of the scan
   - `Phone number lists skipped: X` indicates phone number filtering
   - `Empty lists skipped: X` indicates no matching members

2. **Verify List Name**:
   - Names like `7034019078@domain.org` are automatically excluded
   - Names like `team.contacts@domain.org` are included

3. **Check Domain Filter**:
   - If using a domain filter (e.g., `gmail.com`)
   - Lists with NO matching emails are excluded
   - Remove domain filter to see all lists

4. **Review .org File**:
   - Ensure file contains `MAILINGLIST` directive
   - Check that emails are valid format
   - Active emails don't start with `!` or `#`

### Expected vs Actual Results

If you expect 4000 lists but only see 3500:
- 250 might be phone number lists
- 250 might have no matching members (with domain filter)
- Check console output for exact counts

---

## Best Practices

### Initial Scan
1. First scan **without** domain filter to see all lists
2. Review total counts and identify distribution patterns
3. Determine appropriate domain filter
4. Re-scan with domain filter for final export

### Production Scanning
1. Enable console logging to monitor progress
2. Review skip statistics before exporting
3. Verify expected counts match actual results
4. Keep console output for audit trail

### Quality Assurance
1. Spot-check skipped phone number lists (should be valid)
2. Review a few "empty" lists to confirm they have no target domain members
3. Validate metadata export has both raw emails and processed names
4. Confirm total email counts align with expectations

---

## Related Documentation

- [PHASE1_QUICKSTART.md](PHASE1_QUICKSTART.md) - User guide for Phase 1
- [STEP3_SUMMARY.md](../development/STEP3_SUMMARY.md) - Implementation details
- [README.md](../../README.md) - Project overview
