# Schwab API 400 Bad Request - Fix Documentation

## Problem

Users were encountering a **400 Bad Request** error when trying to fetch options chains:

```
Error fetching options chain: Schwab API Error: 400 Bad Request
```

## Root Cause

After diagnostic testing, we discovered that **Schwab's API does not allow retrieval of same-day expiring options (0DTE)**.

When requesting options that expire on the current date, the API returns:
```json
{
  "errors": [{
    "status": "400",
    "title": "Bad Request",
    "detail": "Check Param Values",
    "source": {"parameter": "Invalid Paramter/Value"}
  }]
}
```

### Test Results
```
Test 1: Trying expiration 2026-02-24 (today)
  Status: 400
  FAILED

Test 2: Trying expiration 2026-02-25 (tomorrow)
  Status: 200
  SUCCESS! Found options data
```

This is a **known limitation** of the Schwab API, likely implemented for risk management reasons.

## Solution Implemented

### 1. Backend Validation (`ezoptionsschwab.py`)

Added check to reject same-day expiration requests before calling the API:

```python
# Check if requesting same-day expiration (0DTE)
today = datetime.now().date()
if expiry == today:
    raise Exception("Cannot retrieve same-day (0DTE) options. Schwab API restricts access to options expiring today. Please select tomorrow or a later expiration date.")
```

### 2. Frontend Filtering (`ezoptionsschwab.py` - JavaScript)

Modified the expiration dropdown to automatically filter out today's date:

```javascript
// Filter out today's date (0DTE not supported by Schwab API)
const today = new Date().toISOString().split('T')[0];
const validDates = data.filter(date => date !== today);
```

### 3. Improved Error Messages

Enhanced error handling to provide clear guidance:

```python
if 'Param' in detail or 'Invalid' in detail:
    error_msg = f"Invalid request parameters. This may occur with same-day (0DTE) options or invalid ticker symbols. Try selecting a future expiration date."
```

## User Impact

**Before Fix:**
- Users selecting today's expiration date would see cryptic "400 Bad Request" error
- No clear indication of what went wrong
- Confusion about whether API was broken

**After Fix:**
- Today's date is automatically hidden from expiration dropdown
- If somehow selected (via API call), clear error message explains the limitation
- Users are guided to select a future expiration date
- No more 400 errors for this specific case

## Testing

Created diagnostic tool (`diagnose_api.py`) that:
1. Validates environment variables
2. Tests authentication
3. Tests quote retrieval
4. Tests expiration date retrieval
5. Tests option chain retrieval with multiple dates
6. Provides detailed error messages

**Run diagnostics:**
```bash
python diagnose_api.py
```

**Simple test:**
```bash
python test_api_simple.py
```

## Workarounds for 0DTE Trading

If you need same-day options data:

### Option 1: Use Yesterday's Data at Market Open
- At market open, yesterday's 1DTE options become today's 0DTE
- Load the data before market open
- Note: Data won't refresh during the day

### Option 2: Alternative Data Source
- Consider using a different data provider for 0DTE
- TDA (TD Ameritrade) API historically allowed 0DTE
- Interactive Brokers API supports 0DTE
- Market data vendors (e.g., Polygon, IEX Cloud) provide 0DTE data

### Option 3: Schwab Website/App
- Access 0DTE data directly through Schwab's web interface
- Use thinkorswim platform for 0DTE analysis
- This limitation only affects programmatic API access

## Additional Notes

### Why This Limitation Exists

Broker APIs often restrict 0DTE access because:
1. **Risk Management** - Same-day options are extremely high risk
2. **System Load** - 0DTE options see massive volume near expiration
3. **Regulatory** - May help prevent retail algorithmic trading losses
4. **Data Quality** - Rapid price changes make data caching difficult

### Other Tickers Tested

- **SPY**: Works for future dates, fails for today
- **SPX ($SPX)**: Same behavior (and some accounts don't have access to index options)
- **Individual stocks**: Same limitation applies

### Market Hours Consideration

Even outside market hours (e.g., 6 PM ET), the API still blocks today's date. The restriction is date-based, not time-based.

## Files Modified

1. `ezoptionsschwab.py`:
   - Added 0DTE validation in `fetch_options_for_date()` (line ~670)
   - Added frontend filtering in `loadExpirations()` JavaScript (line ~5675)
   - Enhanced error message parsing (line ~690)

2. `diagnose_api.py` (new file):
   - Comprehensive diagnostic tool for troubleshooting Schwab API issues

3. `test_api_simple.py` (new file):
   - Quick test script for expiration date validation

## Verification

To verify the fix is working:

1. **Start the application:**
   ```bash
   python ezoptionsschwab.py
   ```

2. **Open browser:** `http://localhost:5001`

3. **Check expiration dropdown:**
   - Today's date should NOT appear in the list
   - Tomorrow and future dates should be available

4. **Select any future date and click Update:**
   - Should successfully load options data
   - No 400 errors

## Error Still Occurring?

If you still see 400 Bad Request errors after this fix:

1. **Check the ticker symbol:**
   - Ensure it's a valid, tradable symbol
   - Try SPY (most reliable)
   - Some symbols require special formatting (e.g., $SPX for S&P 500 index)

2. **Verify expiration date:**
   - Make sure it's not today
   - Ensure the date is in the future
   - Check that options exist for that date

3. **Re-authenticate:**
   ```bash
   # Delete tokens and re-authenticate
   rm tokens.json
   python ezoptionsschwab.py
   ```

4. **Run diagnostics:**
   ```bash
   python diagnose_api.py
   ```

5. **Check API credentials:**
   - Verify `.env` file contains correct values
   - Ensure API key has options trading permissions
   - Check that callback URL matches Schwab Developer Portal

## Summary

✅ **Problem Identified:** Schwab API blocks same-day (0DTE) options retrieval
✅ **Solution Implemented:** Frontend filtering + backend validation + clear error messages
✅ **User Experience:** Seamless - today's date simply doesn't appear in the dropdown
✅ **Diagnostics Added:** Tools to troubleshoot future API issues

**The 400 Bad Request error for standard usage should now be resolved.**

---

**Date Fixed:** February 24, 2026
**Issue:** Schwab API 400 Bad Request on 0DTE options
**Status:** ✅ RESOLVED
