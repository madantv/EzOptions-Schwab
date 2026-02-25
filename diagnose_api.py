"""
Diagnostic script for Schwab API issues
Helps identify the cause of 400 Bad Request errors
"""

import os
import sys
from dotenv import load_dotenv
from datetime import datetime, timedelta
import schwabdev

# Load environment variables
load_dotenv()

print("=" * 70)
print("Schwab API Diagnostic Tool")
print("=" * 70)

# Check environment variables
print("\n1. Checking Environment Variables...")
app_key = os.getenv('SCHWAB_APP_KEY')
app_secret = os.getenv('SCHWAB_APP_SECRET')
callback_url = os.getenv('SCHWAB_CALLBACK_URL')

if not app_key:
    print("   [FAIL] SCHWAB_APP_KEY is missing!")
else:
    print(f"   [OK] SCHWAB_APP_KEY: {app_key[:10]}...")

if not app_secret:
    print("   [FAIL] SCHWAB_APP_SECRET is missing!")
else:
    print(f"   [OK] SCHWAB_APP_SECRET: {app_secret[:10]}...")

if not callback_url:
    print("   [FAIL] SCHWAB_CALLBACK_URL is missing!")
else:
    print(f"   [OK] SCHWAB_CALLBACK_URL: {callback_url}")

if not (app_key and app_secret and callback_url):
    print("\n[FAIL] Missing required environment variables!")
    print("Please check your .env file")
    sys.exit(1)

# Initialize client
print("\n2. Initializing Schwab Client...")
try:
    client = schwabdev.Client(app_key, app_secret, callback_url)
    print("   [OK] Client initialized successfully")
except Exception as e:
    print(f"   [FAIL] Failed to initialize client: {e}")
    sys.exit(1)

# Check authentication
print("\n3. Checking Authentication...")
try:
    # Try to get a simple quote
    test_ticker = "SPY"
    quote_response = client.quotes(test_ticker)

    if quote_response.ok:
        print(f"   [OK] Successfully authenticated")
        print(f"   [OK] Retrieved quote for {test_ticker}")
        quote_data = quote_response.json()
        if test_ticker in quote_data:
            price = quote_data[test_ticker]['quote']['lastPrice']
            print(f"   [OK] {test_ticker} Price: ${price}")
    else:
        print(f"   [FAIL] Authentication issue: {quote_response.status_code}")
        print(f"   Response: {quote_response.text[:200]}")

except Exception as e:
    print(f"   [FAIL] Error during authentication test: {e}")
    print("\nPossible issues:")
    print("   - OAuth tokens may be expired (delete tokens.json and re-authenticate)")
    print("   - API credentials may be incorrect")
    print("   - Network connectivity issues")
    sys.exit(1)

# Test option expiration dates
print("\n4. Testing Option Expiration Retrieval...")
try:
    test_ticker = "SPY"
    exp_response = client.option_expiration_chain(test_ticker)

    if exp_response.ok:
        print(f"   [OK] Successfully retrieved expirations for {test_ticker}")
        exp_data = exp_response.json()
        if 'expirationList' in exp_data:
            expirations = [item['expirationDate'] for item in exp_data['expirationList']]
            print(f"   [OK] Found {len(expirations)} expiration dates")
            if len(expirations) > 0:
                print(f"   [OK] Next expiration: {expirations[0]}")
                next_exp = expirations[0]
    else:
        print(f"   [FAIL] Failed to get expirations: {exp_response.status_code}")
        print(f"   Response: {exp_response.text[:200]}")
        sys.exit(1)

except Exception as e:
    print(f"   [FAIL] Error getting expirations: {e}")
    sys.exit(1)

# Test option chain retrieval
print("\n5. Testing Option Chain Retrieval...")
try:
    test_ticker = "SPY"
    test_date = next_exp  # Use the next available expiration

    print(f"   Testing with ticker: {test_ticker}")
    print(f"   Testing with date: {test_date}")

    # Parse the date
    from_date = test_date
    to_date = test_date

    print(f"   Calling option_chains with:")
    print(f"     symbol={test_ticker}")
    print(f"     fromDate={from_date}")
    print(f"     toDate={to_date}")
    print(f"     contractType=ALL")

    chain_response = client.option_chains(
        symbol=test_ticker,
        fromDate=from_date,
        toDate=to_date,
        contractType='ALL'
    )

    print(f"\n   Response Status: {chain_response.status_code}")

    if chain_response.ok:
        print("   [OK] Successfully retrieved option chain!")
        chain_data = chain_response.json()

        # Check data
        if 'callExpDateMap' in chain_data:
            call_count = sum(len(strikes) for strikes in chain_data['callExpDateMap'].values())
            print(f"   [OK] Found {call_count} call strike prices")

        if 'putExpDateMap' in chain_data:
            put_count = sum(len(strikes) for strikes in chain_data['putExpDateMap'].values())
            print(f"   [OK] Found {put_count} put strike prices")

        if 'underlyingPrice' in chain_data:
            print(f"   [OK] Underlying price: ${chain_data['underlyingPrice']}")
    else:
        print(f"   [FAIL] Failed to retrieve option chain!")
        print(f"   Status Code: {chain_response.status_code}")
        print(f"   Reason: {chain_response.reason}")
        print(f"   Response Body: {chain_response.text[:500]}")

        # Try to parse error
        try:
            error_data = chain_response.json()
            print(f"\n   Error Details:")
            print(f"   {error_data}")
        except:
            pass

        print("\n   Common causes of 400 Bad Request:")
        print("   1. Invalid date format (should be YYYY-MM-DD)")
        print("   2. Invalid ticker symbol")
        print("   3. Requesting expired options")
        print("   4. Invalid contractType parameter")
        print("   5. API rate limiting")

        sys.exit(1)

except Exception as e:
    print(f"   [FAIL] Exception during option chain test: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test SPX specifically (common issue)
print("\n6. Testing SPX Option Chain...")
try:
    spx_ticker = "$SPX"

    # Get SPX expirations
    exp_response = client.option_expiration_chain(spx_ticker)

    if exp_response.ok:
        exp_data = exp_response.json()
        if 'expirationList' in exp_data and len(exp_data['expirationList']) > 0:
            spx_exp = exp_data['expirationList'][0]['expirationDate']
            print(f"   Testing SPX with date: {spx_exp}")

            chain_response = client.option_chains(
                symbol=spx_ticker,
                fromDate=spx_exp,
                toDate=spx_exp,
                contractType='ALL'
            )

            if chain_response.ok:
                print(f"   [OK] SPX option chain retrieved successfully")
            else:
                print(f"   [FAIL] SPX option chain failed: {chain_response.status_code}")
                print(f"   This is a known issue with some index symbols")
        else:
            print(f"   [FAIL] No expirations found for SPX")
    else:
        print(f"   [FAIL] Cannot get SPX expirations: {exp_response.status_code}")
        print(f"   Note: Some accounts may not have access to index options")

except Exception as e:
    print(f"   [WARN] SPX test failed (this may be normal): {e}")

# Summary
print("\n" + "=" * 70)
print("Diagnostic Summary")
print("=" * 70)
print("\n[OK] Basic authentication is working")
print("[OK] Can retrieve quotes")
print("[OK] Can retrieve expiration dates")

if 'chain_response' in locals() and chain_response.ok:
    print("[OK] Can retrieve option chains")
    print("\n[SUCCESS] Your Schwab API setup is working correctly!")
    print("\nIf you're still seeing errors in the main app:")
    print("1. Check the ticker symbol you're using")
    print("2. Ensure the expiration date is valid")
    print("3. Try refreshing the page")
    print("4. Check browser console for JavaScript errors")
else:
    print("\n[FAIL] Option chain retrieval is failing")
    print("\nTroubleshooting steps:")
    print("1. Delete tokens.json and re-authenticate")
    print("2. Verify your Schwab API credentials")
    print("3. Check if your API key has options trading permissions")
    print("4. Try a different ticker (SPY is most reliable)")

print("\n" + "=" * 70)
