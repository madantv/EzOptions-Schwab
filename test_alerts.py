"""
Test script for the alert engine
Run this to verify alert rules are working correctly
"""

import pandas as pd
from alert_engine import get_alert_engine, Alert

def test_gex_breach():
    """Test GEX wall breach detection"""
    print("\n=== Testing GEX Wall Breach ===")

    engine = get_alert_engine()

    # Create mock data with a GEX wall at 580
    calls_data = {
        'strike': [575, 580, 585],
        'GEX': [200_000_000, 800_000_000, 100_000_000],  # 800M at 580
        'volume': [1000, 5000, 500]
    }

    puts_data = {
        'strike': [575, 580, 585],
        'GEX': [100_000_000, 200_000_000, 50_000_000],
        'volume': [500, 2000, 300]
    }

    calls = pd.DataFrame(calls_data)
    puts = pd.DataFrame(puts_data)

    # Update 1: Price at 578 (below wall)
    print("Update 1: Price at 578 (below wall)")
    engine.update_data(ticker='SPY', price=578.0, calls=calls, puts=puts)
    alerts = engine.check_alerts()
    print(f"  Alerts triggered: {len(alerts)}")

    # Update 2: Price moves to 580.5 (breaches wall)
    print("Update 2: Price at 580.5 (breaches wall)")
    engine.update_data(ticker='SPY', price=580.5, calls=calls, puts=puts)
    alerts = engine.check_alerts()
    print(f"  Alerts triggered: {len(alerts)}")

    if alerts:
        for alert in alerts:
            print(f"  [OK] {alert.alert_type}: {alert.message[:80]}...")

    return len(alerts) > 0


def test_negative_gamma():
    """Test negative gamma environment detection"""
    print("\n=== Testing Negative Gamma Environment ===")

    engine = get_alert_engine()

    # Create mock data with negative net gamma
    calls_data = {
        'strike': [575, 580, 585],
        'GEX': [100_000_000, 200_000_000, 50_000_000],  # 350M total
        'volume': [1000, 2000, 500]
    }

    puts_data = {
        'strike': [575, 580, 585],
        'GEX': [400_000_000, 600_000_000, 150_000_000],  # 1.15B total
        'volume': [2000, 3000, 1000]
    }

    calls = pd.DataFrame(calls_data)
    puts = pd.DataFrame(puts_data)

    # Net gamma = 350M - 1.15B = -800M (negative!)
    print("Net GEX = 350M - 1150M = -800M (negative)")
    engine.update_data(ticker='SPY', price=580.0, calls=calls, puts=puts)
    alerts = engine.check_alerts()
    print(f"  Alerts triggered: {len(alerts)}")

    if alerts:
        for alert in alerts:
            print(f"  [OK] {alert.alert_type}: {alert.message[:80]}...")

    return len(alerts) > 0


def test_centroid_divergence():
    """Test centroid divergence detection"""
    print("\n=== Testing Centroid Divergence ===")

    engine = get_alert_engine()

    # Clear cooldown for centroid rule
    cent_rule = engine.get_rule("Centroid Divergence")
    if cent_rule:
        cent_rule.last_triggered = None

    # Create mock data where call centroid is far above current price
    calls_data = {
        'strike': [590, 595, 600, 605],  # Higher strikes for >2% divergence
        'GEX': [200_000_000, 300_000_000, 400_000_000, 100_000_000],
        'volume': [5000, 10000, 8000, 2000]  # Heavy volume at higher strikes
    }

    puts_data = {
        'strike': [575, 580, 585],
        'GEX': [100_000_000, 200_000_000, 50_000_000],
        'volume': [1000, 2000, 500]
    }

    calls = pd.DataFrame(calls_data)
    puts = pd.DataFrame(puts_data)

    # Calculate expected centroid
    total_call_volume = calls['volume'].sum()
    weighted_strikes = calls['strike'] * calls['volume']
    call_centroid = weighted_strikes.sum() / total_call_volume

    current_price = 580.0
    divergence = (call_centroid - current_price) / current_price * 100

    print(f"Call Centroid: ${call_centroid:.2f}")
    print(f"Current Price: ${current_price:.2f}")
    print(f"Divergence: {divergence:.1f}%")
    print(f"Divergence (decimal): {divergence/100:.4f}")
    print(f"Threshold: {cent_rule.divergence_threshold if cent_rule else 'N/A'}")

    engine.update_data(ticker='SPY', price=current_price, calls=calls, puts=puts)
    alerts = engine.check_alerts()
    print(f"  Alerts triggered: {len(alerts)}")

    if alerts:
        for alert in alerts:
            print(f"  [OK] {alert.alert_type}: {alert.message[:80]}...")

    return len(alerts) > 0


def test_alert_cooldown():
    """Test that alerts respect cooldown periods"""
    print("\n=== Testing Alert Cooldown ===")

    engine = get_alert_engine()

    # Get the GEX breach rule and set short cooldown for testing
    gex_rule = engine.get_rule("GEX Wall Breach")
    if gex_rule:
        original_cooldown = gex_rule.cooldown_seconds
        gex_rule.cooldown_seconds = 5  # 5 second cooldown for testing
        gex_rule.last_triggered = None  # Clear any previous trigger

        calls_data = {
            'strike': [575, 580, 585],
            'GEX': [200_000_000, 800_000_000, 100_000_000],
            'volume': [1000, 5000, 500]
        }

        puts_data = {
            'strike': [575, 580, 585],
            'GEX': [100_000_000, 200_000_000, 50_000_000],
            'volume': [500, 2000, 300]
        }

        calls = pd.DataFrame(calls_data)
        puts = pd.DataFrame(puts_data)

        # First breach
        engine.update_data(ticker='SPY', price=578.0, calls=calls, puts=puts)
        engine.update_data(ticker='SPY', price=580.5, calls=calls, puts=puts)
        alerts1 = engine.check_alerts()
        print(f"First breach: {len(alerts1)} alerts")

        # Immediate second breach (should be blocked by cooldown)
        engine.update_data(ticker='SPY', price=578.0, calls=calls, puts=puts)
        engine.update_data(ticker='SPY', price=580.5, calls=calls, puts=puts)
        alerts2 = engine.check_alerts()
        print(f"Immediate second breach (should be 0): {len(alerts2)} alerts")

        # Restore original cooldown
        gex_rule.cooldown_seconds = original_cooldown

        return len(alerts1) > 0 and len(alerts2) == 0

    return False


def test_api_endpoints():
    """Test that API endpoints would work (requires running server)"""
    print("\n=== API Endpoints Info ===")
    print("The following API endpoints are available:")
    print("  GET  /api/alerts/recent?hours=1  - Get recent alerts")
    print("  GET  /api/alerts/all              - Get all alerts")
    print("  GET  /api/alerts/config           - Get alert configuration")
    print("  POST /api/alerts/config           - Update alert configuration")
    print("  GET  /api/alerts/test             - Send a test alert")
    print("  GET  /api/alerts/check            - Manually trigger alert check")
    print("  GET  /api/alerts/clear            - Clear alert history")
    print("\nTo test these, start the Flask server and use curl or browser:")
    print("  curl http://localhost:5001/api/alerts/test")


def main():
    print("=" * 60)
    print("Alert Engine Test Suite")
    print("=" * 60)

    results = {}

    # Run tests
    results['GEX Breach'] = test_gex_breach()
    results['Negative Gamma'] = test_negative_gamma()
    results['Centroid Divergence'] = test_centroid_divergence()
    results['Cooldown'] = test_alert_cooldown()

    # Show API info
    test_api_endpoints()

    # Summary
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    for test_name, passed in results.items():
        status = "[PASSED]" if passed else "[FAILED]"
        print(f"{test_name:.<40} {status}")

    passed_count = sum(results.values())
    total_count = len(results)

    print("\n" + "=" * 60)
    print(f"Total: {passed_count}/{total_count} tests passed")
    print("=" * 60)

    if passed_count == total_count:
        print("\n[SUCCESS] All tests passed! Alert system is working correctly.")
        print("\nNext steps:")
        print("1. Start the Flask server: python ezoptionsschwab.py")
        print("2. Open http://localhost:5001 in your browser")
        print("3. Click the 'Test Alert' button to test browser notifications")
        print("4. Allow notifications when prompted by your browser")
        print("5. Start streaming data to see real alerts based on market conditions")
    else:
        print("\n[ERROR] Some tests failed. Please check the output above.")

    return passed_count == total_count


if __name__ == '__main__':
    main()
