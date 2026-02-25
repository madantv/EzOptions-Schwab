"""Quick test of different date formats for Schwab API"""
import schwabdev
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

client = schwabdev.Client(
    os.getenv('SCHWAB_APP_KEY'),
    os.getenv('SCHWAB_APP_SECRET'),
    os.getenv('SCHWAB_CALLBACK_URL')
)

# Get expirations
exp_response = client.option_expiration_chain("SPY")
exp_data = exp_response.json()
expirations = [item['expirationDate'] for item in exp_data['expirationList']]

print(f"Available expirations: {expirations[:5]}")
print()

# Try different expirations
for i, exp_date in enumerate(expirations[:3]):
    print(f"Test {i+1}: Trying expiration {exp_date}")

    response = client.option_chains(
        symbol="SPY",
        fromDate=exp_date,
        toDate=exp_date,
        contractType='ALL'
    )

    print(f"  Status: {response.status_code}")

    if response.ok:
        data = response.json()
        call_count = len(data.get('callExpDateMap', {}))
        print(f"  SUCCESS! Found {call_count} call expiration dates")
        break
    else:
        print(f"  FAILED: {response.text[:150]}")
    print()
