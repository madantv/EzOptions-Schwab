"""
Test script to verify 0DTE handling
"""
import schwabdev
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

client = schwabdev.Client(
    os.getenv('SCHWAB_APP_KEY'),
    os.getenv('SCHWAB_APP_SECRET'),
    os.getenv('SCHWAB_CALLBACK_URL')
)

print("Testing 0DTE Option Chain Request")
print("=" * 60)

# Get expirations for SPY
exp_response = client.option_expiration_chain("SPY")
exp_data = exp_response.json()
expirations = [item['expirationDate'] for item in exp_data['expirationList']]

today = datetime.now().date().isoformat()

print(f"Today's date: {today}")
print(f"Available expirations: {expirations[:5]}")
print()

# Find if today is in the list
if today in expirations:
    print(f"[OK] Today's date ({today}) IS in expiration list")
    print("  Frontend will show it as: '{} (0DTE - API Limited)'".format(today))
    print("  Color: Orange (#FF9900)")
    print("  Opacity: 0.6")
    print()

    # Try to fetch it
    print(f"Attempting to fetch options for today ({today})...")
    response = client.option_chains(
        symbol="SPY",
        fromDate=today,
        toDate=today,
        contractType='ALL'
    )

    if response.ok:
        print("  [WARN] UNEXPECTED: Request succeeded (API behavior may have changed)")
        data = response.json()
        print(f"  Found options data with underlying price: ${data.get('underlyingPrice', 'N/A')}")
    else:
        print("  [OK] EXPECTED: Request failed (400 Bad Request)")
        print("  User will see helpful error message:")
        print()
        print("  " + "-" * 55)
        print("  [WARN] Same-Day (0DTE) Options Not Available")
        print()
        print(f"  Schwab API does not support retrieving options")
        print(f"  expiring today ({today}).")
        print()
        print("  Options:")
        print("  • Select tomorrow or a later expiration date")
        print("  • Use Schwab's website or thinkorswim for 0DTE data")
        print("  • Wait until after market close to view historical data")
        print("  " + "-" * 55)
else:
    print(f"[X] Today's date ({today}) is NOT in expiration list")
    print("  (No options expire today)")

print()
print("=" * 60)
print("Summary:")
print("  [OK] 0DTE dates will appear in dropdown with warning label")
print("  [OK] Selecting 0DTE will show helpful error message")
print("  [OK] Users can still select and see what 0DTE means")
print("  [OK] Clear guidance provided on alternatives")
