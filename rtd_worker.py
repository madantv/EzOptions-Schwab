# src/rtd/rtd_worker.py
import pythoncom
import time
import threading
from queue import Queue
from src.rtd.client import RTDClient
from src.core.settings import SETTINGS
from config.quote_types import QuoteType
from src.utils.option_symbol_builder import OptionSymbolBuilder
from src.core.logger import get_logger

class RTDWorker:
    MAX_RETRIES = 5
    RETRY_DELAY_SECONDS = 3
    MAX_CONSECUTIVE_ERRORS = 10  # Force reconnect after this many data-loop errors

    def __init__(self, data_queue: Queue, stop_event: threading.Event):
        self.data_queue = data_queue
        self.stop_event = stop_event
        self.client = None
        self.initialized = False
        self.logger = get_logger("RTDWorker")

    # ------------------------------------------------------------------
    # Internal: one full connect → subscribe → poll cycle
    # ------------------------------------------------------------------
    def _run_once(self, all_symbols: list):
        """Single lifecycle: init COM, subscribe, poll until error or stop."""
        if self.initialized:
            self.logger.info("Cleaning up previous instance before reconnect…")
            self.cleanup()

        pythoncom.CoInitialize()
        time.sleep(0.1)

        self.client = RTDClient(heartbeat_ms=SETTINGS['timing']['initial_heartbeat'])
        self.client.initialize()
        self.initialized = True

        if not all_symbols:
            self.logger.warning("No symbols provided!")
            return

        # ---------- subscribe ----------
        success_count = 0
        subscription_errors = []

        for symbol in all_symbols:
            retry_count = 0
            while retry_count < 3:
                try:
                    if symbol.startswith('.'):  # Option symbols
                        if self.client.subscribe(QuoteType.GAMMA, symbol):
                            success_count += 1
                            self.logger.info(f"Subscribed to GAMMA for {symbol}")
                        if self.client.subscribe(QuoteType.OPEN_INT, symbol):
                            success_count += 1
                            self.logger.info(f"Subscribed to OPEN_INT for {symbol}")
                        if self.client.subscribe(QuoteType.VOLUME, symbol):
                            success_count += 1
                            self.logger.info(f"Subscribed to VOLUME for {symbol}")
                    else:  # Base symbol
                        if symbol.startswith('/') and ':' not in symbol:
                            exchange = OptionSymbolBuilder.FUTURES_EXCHANGES.get(symbol, "XCBT")
                            full_symbol = f"{symbol}:{exchange}"
                            self.logger.info(f"RTD Worker subscribing to LAST for futures symbol: {full_symbol}")
                            if self.client.subscribe(QuoteType.LAST, full_symbol):
                                success_count += 1
                                self.logger.info(f"Successfully subscribed to {full_symbol}")
                        else:
                            self.logger.info(f"RTD Worker subscribing to LAST for {symbol}")
                            if self.client.subscribe(QuoteType.LAST, symbol):
                                success_count += 1
                                self.logger.info(f"Successfully subscribed to {symbol}")
                    break  # Success, exit retry loop
                except Exception as sub_error:
                    retry_count += 1
                    if retry_count == 3:
                        error_msg = f"Failed to subscribe to {symbol} after 3 attempts: {str(sub_error)}"
                        subscription_errors.append(error_msg)
                        self.logger.error(error_msg)
                    time.sleep(0.1)

        if subscription_errors:
            self.data_queue.put({"error": "\n".join(subscription_errors)})
            return

        self.logger.info(f"Successfully subscribed to {success_count} topics")
        time.sleep(0.3)

        # ---------- poll loop ----------
        last_data = {}
        consecutive_errors = 0

        while not self.stop_event.is_set():
            pythoncom.PumpWaitingMessages()

            try:
                with self.client._value_lock:
                    if self.client._latest_values:
                        current_data = {}
                        for topic_str, quote in self.client._latest_values.items():
                            symbol, quote_type = topic_str
                            key = f"{symbol}:{quote_type}"
                            current_data[key] = quote.value
                            if symbol.startswith('/'):
                                self.logger.info(f"RTD Worker received data - Key: {key}, Value: {quote.value}")

                        if current_data != last_data:
                            while not self.data_queue.empty():
                                try:
                                    self.data_queue.get_nowait()
                                except:
                                    break
                            self.data_queue.put(current_data)
                            last_data = current_data.copy()

                consecutive_errors = 0  # Reset on any successful iteration

            except Exception as e:
                consecutive_errors += 1
                self.logger.error(f"Data processing error ({consecutive_errors}/{self.MAX_CONSECUTIVE_ERRORS}): {str(e)}")
                if consecutive_errors >= self.MAX_CONSECUTIVE_ERRORS:
                    raise RuntimeError(
                        f"Too many consecutive data errors ({consecutive_errors}), forcing reconnect"
                    )

            time.sleep(1)

    # ------------------------------------------------------------------
    # Public entry-point with auto-reconnect
    # ------------------------------------------------------------------
    def start(self, all_symbols: list):
        """Start RTD worker with automatic reconnection on failure."""
        attempt = 0

        while not self.stop_event.is_set():
            attempt += 1
            try:
                self.logger.info(f"RTD connection attempt {attempt}/{self.MAX_RETRIES}")
                self._run_once(all_symbols)

                # If _run_once returns normally (stop_event was set), we're done
                if self.stop_event.is_set():
                    self.logger.info("Stop event received, exiting cleanly")
                    break

            except Exception as e:
                error_msg = f"RTD Error (attempt {attempt}): {str(e)}"
                self.logger.error(error_msg)

                # Always clean up before retrying
                self.cleanup()

                if attempt >= self.MAX_RETRIES:
                    self.logger.error(f"Giving up after {self.MAX_RETRIES} attempts")
                    self.data_queue.put({"error": f"RTD connection failed after {self.MAX_RETRIES} attempts. Last error: {str(e)}"})
                    break

                # Notify UI that we are reconnecting (not a permanent error)
                self.data_queue.put({"status": f"Reconnecting… attempt {attempt + 1}/{self.MAX_RETRIES}"})
                self.logger.info(f"Waiting {self.RETRY_DELAY_SECONDS}s before retry…")
                time.sleep(self.RETRY_DELAY_SECONDS)

        # Final cleanup
        self.cleanup()
        self.logger.info("RTDWorker shutdown complete")

    def cleanup(self):
        if self.client:
            try:
                print("Disconnecting RTDClient…")
                self.client.Disconnect()
                self.client = None
            except Exception as e:
                print(f"Error during disconnect: {str(e)}")
        try:
            pythoncom.CoUninitialize()
        except Exception as e:
            print(f"Error during CoUninitialize: {str(e)}")
        self.initialized = False