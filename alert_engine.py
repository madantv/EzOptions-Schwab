"""
Alert Engine for EzOptions-Schwab
Monitors gamma exposure and other metrics to generate real-time trading alerts
"""

import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import pandas as pd


class Alert:
    """Represents a single alert"""
    def __init__(self, alert_type: str, ticker: str, urgency: str,
                 message: str, data: Dict[str, Any]):
        self.alert_type = alert_type
        self.ticker = ticker
        self.urgency = urgency  # CRITICAL, HIGH, MEDIUM, LOW
        self.message = message
        self.data = data
        self.timestamp = datetime.now()
        self.id = f"{alert_type}_{ticker}_{int(self.timestamp.timestamp())}"

    def to_dict(self) -> Dict:
        """Convert alert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'alert_type': self.alert_type,
            'ticker': self.ticker,
            'urgency': self.urgency,
            'message': self.message,
            'data': self.data,
            'timestamp': self.timestamp.isoformat()
        }


class AlertRule:
    """Base class for all alert rules"""
    def __init__(self, name: str, enabled: bool = True, cooldown_seconds: int = 300):
        self.name = name
        self.enabled = enabled
        self.last_triggered = None
        self.cooldown_seconds = cooldown_seconds

    def can_trigger(self) -> bool:
        """Check if cooldown period has elapsed"""
        if self.last_triggered is None:
            return True
        elapsed = (datetime.now() - self.last_triggered).total_seconds()
        return elapsed >= self.cooldown_seconds

    def evaluate(self, current_data: Dict, historical_data: List) -> Optional[Alert]:
        """Override in subclass to implement rule logic"""
        raise NotImplementedError

    def mark_triggered(self):
        """Mark this rule as triggered"""
        self.last_triggered = datetime.now()


class GEXWallBreachRule(AlertRule):
    """Alert when price breaches a major gamma wall"""
    def __init__(self, threshold_gex: float = 500_000_000, enabled: bool = True):
        super().__init__("GEX Wall Breach", enabled=enabled, cooldown_seconds=300)
        self.threshold_gex = threshold_gex

    def evaluate(self, current_data: Dict, historical_data: List) -> Optional[Alert]:
        if not self.enabled or not self.can_trigger():
            return None

        try:
            calls = current_data.get('calls')
            puts = current_data.get('puts')
            price = current_data.get('price')
            ticker = current_data.get('ticker')

            if calls is None or puts is None or price is None:
                return None

            if calls.empty or puts.empty:
                return None

            # Calculate net GEX by strike
            strikes = {}
            for _, row in calls.iterrows():
                strike = row['strike']
                gex = row.get('GEX', 0)
                strikes[strike] = strikes.get(strike, 0) + gex

            for _, row in puts.iterrows():
                strike = row['strike']
                gex = row.get('GEX', 0)
                strikes[strike] = strikes.get(strike, 0) - gex

            if not strikes:
                return None

            # Find max GEX strike
            max_strike = max(strikes.keys(), key=lambda k: abs(strikes[k]))
            max_gex = strikes[max_strike]

            if abs(max_gex) < self.threshold_gex:
                return None

            # Check if price just crossed this strike
            if len(historical_data) < 1:
                return None

            prev_data = historical_data[-1]
            prev_price = prev_data.get('price')

            if prev_price is None:
                return None

            # Detect breach
            breached = False
            direction = ""

            if prev_price < max_strike <= price:
                breached = True
                direction = "Bullish"
            elif prev_price > max_strike >= price:
                breached = True
                direction = "Bearish"

            if not breached:
                return None

            # Breach confirmed!
            self.mark_triggered()

            message = f"""GEX WALL BREACH
{ticker} broke through ${max_strike:.2f} gamma wall (${abs(max_gex)/1e9:.2f}B GEX)
Price: ${price:.2f} | Direction: {direction}
Action: Consider {'long call' if direction == 'Bullish' else 'long put'} entry"""

            return Alert(
                alert_type="gex_breach",
                ticker=ticker,
                urgency="HIGH",
                message=message,
                data={
                    'strike': max_strike,
                    'gex': max_gex,
                    'price': price,
                    'direction': direction
                }
            )

        except Exception as e:
            print(f"Error in GEXWallBreachRule: {e}")
            return None


class NegativeGammaRule(AlertRule):
    """Alert when net gamma turns negative"""
    def __init__(self, threshold: float = -500_000_000, enabled: bool = True):
        super().__init__("Negative Gamma Environment", enabled=enabled, cooldown_seconds=600)
        self.threshold = threshold

    def evaluate(self, current_data: Dict, historical_data: List) -> Optional[Alert]:
        if not self.enabled or not self.can_trigger():
            return None

        try:
            calls = current_data.get('calls')
            puts = current_data.get('puts')
            price = current_data.get('price')
            ticker = current_data.get('ticker')

            if calls is None or puts is None:
                return None

            if calls.empty or puts.empty:
                return None

            # Calculate total net gamma
            total_call_gex = calls.get('GEX', pd.Series()).sum() if 'GEX' in calls.columns else 0
            total_put_gex = puts.get('GEX', pd.Series()).sum() if 'GEX' in puts.columns else 0
            net_gex = total_call_gex - total_put_gex

            # Check if negative and below threshold
            if net_gex >= self.threshold:
                return None

            # Check if this is a transition from positive to negative
            was_positive = True
            if len(historical_data) >= 1:
                prev_data = historical_data[-1]
                prev_calls = prev_data.get('calls')
                prev_puts = prev_data.get('puts')
                if prev_calls is not None and prev_puts is not None:
                    prev_net = prev_calls.get('GEX', pd.Series()).sum() - prev_puts.get('GEX', pd.Series()).sum()
                    was_positive = prev_net > 0

            # Only alert on transition or very negative values
            if not was_positive and net_gex > -1_000_000_000:
                return None

            self.mark_triggered()

            message = f"""NEGATIVE GAMMA ENVIRONMENT
{ticker} net GEX: ${net_gex/1e9:.2f}B
Price: ${price:.2f}
Implication: Dealers will amplify moves (buy rallies, sell dips)
Action: Consider straddles/strangles or directional momentum plays"""

            return Alert(
                alert_type="negative_gamma",
                ticker=ticker,
                urgency="HIGH",
                message=message,
                data={
                    'net_gex': net_gex,
                    'call_gex': total_call_gex,
                    'put_gex': total_put_gex,
                    'price': price
                }
            )

        except Exception as e:
            print(f"Error in NegativeGammaRule: {e}")
            return None


class CentroidDivergenceRule(AlertRule):
    """Alert when volume-weighted centroid diverges from spot price"""
    def __init__(self, divergence_threshold: float = 0.02, enabled: bool = True):
        super().__init__("Centroid Divergence", enabled=enabled, cooldown_seconds=900)
        self.divergence_threshold = divergence_threshold

    def evaluate(self, current_data: Dict, historical_data: List) -> Optional[Alert]:
        if not self.enabled or not self.can_trigger():
            return None

        try:
            calls = current_data.get('calls')
            puts = current_data.get('puts')
            price = current_data.get('price')
            ticker = current_data.get('ticker')

            if calls is None or puts is None or price is None:
                return None

            if calls.empty or puts.empty:
                return None

            # Calculate call centroid
            call_centroid = None
            if 'volume' in calls.columns and 'strike' in calls.columns:
                calls_with_volume = calls[calls['volume'] > 0]
                if not calls_with_volume.empty:
                    total_call_volume = calls_with_volume['volume'].sum()
                    if total_call_volume > 0:
                        weighted_strikes = calls_with_volume['strike'] * calls_with_volume['volume']
                        call_centroid = weighted_strikes.sum() / total_call_volume

            # Calculate put centroid
            put_centroid = None
            if 'volume' in puts.columns and 'strike' in puts.columns:
                puts_with_volume = puts[puts['volume'] > 0]
                if not puts_with_volume.empty:
                    total_put_volume = puts_with_volume['volume'].sum()
                    if total_put_volume > 0:
                        weighted_strikes = puts_with_volume['strike'] * puts_with_volume['volume']
                        put_centroid = weighted_strikes.sum() / total_put_volume

            # Check for significant divergence
            alert_triggered = False
            direction = ""
            divergence = 0
            centroid_value = 0

            if call_centroid is not None:
                divergence = (call_centroid - price) / price
                if divergence >= self.divergence_threshold:
                    alert_triggered = True
                    direction = "Bullish"
                    centroid_value = call_centroid

            if put_centroid is not None and not alert_triggered:
                divergence = (price - put_centroid) / price
                if divergence >= self.divergence_threshold:
                    alert_triggered = True
                    direction = "Bearish"
                    centroid_value = put_centroid

            if not alert_triggered:
                return None

            self.mark_triggered()

            message = f"""SMART MONEY SIGNAL
{'Call' if direction == 'Bullish' else 'Put'} Centroid: ${centroid_value:.2f}
{ticker} Price: ${price:.2f}
Divergence: {divergence*100:+.1f}% {'above' if direction == 'Bullish' else 'below'} price
Implication: Institutions loading {'upside calls' if direction == 'Bullish' else 'downside puts'}
Action: Consider {'call' if direction == 'Bullish' else 'put'} positions targeting ${centroid_value:.2f}"""

            return Alert(
                alert_type="centroid_divergence",
                ticker=ticker,
                urgency="HIGH",
                message=message,
                data={
                    'centroid': centroid_value,
                    'price': price,
                    'divergence': divergence,
                    'direction': direction
                }
            )

        except Exception as e:
            print(f"Error in CentroidDivergenceRule: {e}")
            return None


class AlertEngine:
    """Main alert engine that monitors data and triggers alerts"""
    def __init__(self):
        self.rules: List[AlertRule] = []
        self.alert_history: List[Alert] = []
        self.max_history_size = 100  # Keep last 100 alerts
        self.running = False
        self.thread = None
        self._lock = threading.Lock()

        # Data storage
        self.current_data: Dict = {}
        self.historical_data: List[Dict] = []
        self.max_historical_size = 20  # Keep last 20 data points

    def add_rule(self, rule: AlertRule):
        """Add an alert rule"""
        with self._lock:
            self.rules.append(rule)

    def remove_rule(self, rule_name: str):
        """Remove an alert rule by name"""
        with self._lock:
            self.rules = [r for r in self.rules if r.name != rule_name]

    def get_rule(self, rule_name: str) -> Optional[AlertRule]:
        """Get a rule by name"""
        with self._lock:
            for rule in self.rules:
                if rule.name == rule_name:
                    return rule
        return None

    def update_data(self, ticker: str, price: float, calls: pd.DataFrame,
                    puts: pd.DataFrame, **extra_data):
        """Update current market data for monitoring"""
        with self._lock:
            # Store current data
            data_point = {
                'ticker': ticker,
                'price': price,
                'calls': calls.copy() if calls is not None else pd.DataFrame(),
                'puts': puts.copy() if puts is not None else pd.DataFrame(),
                'timestamp': datetime.now(),
                **extra_data
            }

            # Move current to historical
            if self.current_data:
                self.historical_data.append(self.current_data)
                # Trim historical data
                if len(self.historical_data) > self.max_historical_size:
                    self.historical_data = self.historical_data[-self.max_historical_size:]

            self.current_data = data_point

    def check_alerts(self) -> List[Alert]:
        """Manually check all rules and return any triggered alerts"""
        alerts = []

        with self._lock:
            if not self.current_data:
                return alerts

            for rule in self.rules:
                if not rule.enabled:
                    continue

                try:
                    alert = rule.evaluate(self.current_data, self.historical_data)
                    if alert:
                        alerts.append(alert)
                        self.alert_history.append(alert)

                        # Trim history
                        if len(self.alert_history) > self.max_history_size:
                            self.alert_history = self.alert_history[-self.max_history_size:]

                        print(f"[ALERT] {alert.urgency}: {alert.alert_type} - {alert.ticker}")

                except Exception as e:
                    print(f"Error evaluating rule {rule.name}: {e}")

        return alerts

    def get_recent_alerts(self, hours: int = 1) -> List[Alert]:
        """Get alerts from the last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        with self._lock:
            return [alert for alert in self.alert_history if alert.timestamp >= cutoff]

    def get_all_alerts(self) -> List[Alert]:
        """Get all alerts in history"""
        with self._lock:
            return self.alert_history.copy()

    def clear_history(self):
        """Clear alert history"""
        with self._lock:
            self.alert_history.clear()

    def get_config(self) -> Dict:
        """Get current alert configuration"""
        with self._lock:
            return {
                'rules': [
                    {
                        'name': rule.name,
                        'enabled': rule.enabled,
                        'cooldown_seconds': rule.cooldown_seconds,
                        'last_triggered': rule.last_triggered.isoformat() if rule.last_triggered else None
                    }
                    for rule in self.rules
                ]
            }

    def update_config(self, config: Dict):
        """Update alert configuration"""
        with self._lock:
            for rule_config in config.get('rules', []):
                rule_name = rule_config.get('name')
                for rule in self.rules:
                    if rule.name == rule_name:
                        rule.enabled = rule_config.get('enabled', rule.enabled)
                        rule.cooldown_seconds = rule_config.get('cooldown_seconds', rule.cooldown_seconds)


# Global alert engine instance
_global_alert_engine = None


def get_alert_engine() -> AlertEngine:
    """Get or create the global alert engine instance"""
    global _global_alert_engine
    if _global_alert_engine is None:
        _global_alert_engine = AlertEngine()
        # Add default rules
        _global_alert_engine.add_rule(GEXWallBreachRule(threshold_gex=500_000_000))
        _global_alert_engine.add_rule(NegativeGammaRule(threshold=-500_000_000))
        _global_alert_engine.add_rule(CentroidDivergenceRule(divergence_threshold=0.02))
    return _global_alert_engine
