# EzOptions-Schwab Development Guidelines

This document provides project-specific information for developers working on the EzOptions-Schwab dashboard.

### 1. Build & Configuration

The project is built using Python 3 and Flask. It uses a SQLite database to track historical exposure data.

#### Key Configuration
- **Environment Variables**: A `.env` file is required in the root directory with the following keys:
  - `SCHWAB_APP_KEY`: Your Schwab Developer App Key.
  - `SCHWAB_APP_SECRET`: Your Schwab Developer App Secret.
  - `SCHWAB_CALLBACK_URL`: The callback URL configured in your Schwab App.
- **Database**: `options_data.db` (SQLite) is automatically initialized by `init_db()` upon start. It contains:
  - `interval_data`: Historical exposure metrics (Gamma, Delta, Vanna, etc.).
  - `centroid_data`: Market-hour volume-weighted centroids for call/put volume.

### 2. Testing

The project does not have a pre-existing complex test suite, but core mathematical logic and database initialization should be verified when making changes.

#### Running Tests
To verify core logic without live API access, you can use mocking or test isolated functions.

**Example Test (`test_core.py`):**
```python
import unittest
import numpy as np
from ezoptionsschwab import calculate_greeks, calculate_greek_exposures

class TestOptionsLogic(unittest.TestCase):
    def test_gex_calculation(self):
        # S=100, K=100, t=1 month (approx), sigma=0.2
        delta, gamma, vega, vanna = calculate_greeks('c', 100, 100, 1/12, 0.2)
        self.assertGreater(delta, 0.4)
        
    def test_exposures(self):
        option = {
            'impliedVolatility': 0.2,
            'expiration': '2026-12-31',
            'contractSymbol': 'SPY_123126C500',
            'strike': 500
        }
        exposures = calculate_greek_exposures(option, 500, 100)
        self.assertIn('GEX', exposures)

if __name__ == '__main__':
    unittest.main()
```

#### Guidelines for New Tests
- Use `unittest` or `pytest`.
- Mock `schwabdev.Client` to avoid dependency on live API credentials.
- Test both standard and Notional GEX calculations (controlled by `calculate_in_notional` parameter in exposure functions).

### 3. Additional Development Information

#### Code Style & Patterns
- **Greek Calculations**: Most Greeks are calculated using the Black-Scholes-Merton model in `calculate_greeks` and auxiliary functions like `calculate_charm`, `calculate_speed`, etc.
- **Exposure Metric weighting**: The dashboard allows switching between "Open Interest" and "Volume" for weighting exposures. Ensure any new exposure-related logic respects the `exposure_metric` parameter.
- **Timezone**: All market-related time calculations use `US/Eastern` time.
- **API Client**: The `schwabdev` client is initialized globally. Many functions rely on this global `client`.

#### Data Flow
1. **Frontend**: Plotly-based dashboard requesting updates via `/update`.
2. **Backend**: Fetches data from Schwab, computes Greeks/Exposures, saves to SQLite if within market hours, and returns JSON for Plotly.
3. **Historical Data**: The `centroid_data` and `interval_data` tables are used for the "Historical Bubble Levels" charts.
