import threading
import time
from datetime import datetime
from typing import Dict, List
from polygon import WebSocketClient
from polygon.websocket.models import WebSocketMessage, EquityTrade

class MarketMonitor:
    """
    A real-time market monitoring system that tracks trade activity and volume
    across different symbols using Polygon.io's WebSocket API. Updates every 15 seconds.
    """
    
    def __init__(self, api_key: str):
        # Initialize timestamps
        self.app_start_time = time.time()
        
        # 15-second snapshot data
        self.trade_counts_15s: Dict[str, int] = {}
        self.cash_volume_15s: Dict[str, float] = {}
        self.cash_traded_15s = 0.0
        
        # Running totals
        self.total_tickers_seen = 0
        self.total_trades_seen = 0
        self.total_cash_traded = 0.0
        self.total_trade_counts: Dict[str, int] = {}
        self.total_cash_volume: Dict[str, float] = {}
        
        # WebSocket client
        self.client = WebSocketClient(api_key)
        
        # Terminal display settings
        self.terminal_width = 80
        
        # Update interval in seconds
        self.update_interval = 15

    def start(self):
        """Start the market monitor with both monitoring and display threads."""
        # Create and start threads
        display_thread = threading.Thread(target=self._run_display_loop)
        websocket_thread = threading.Thread(target=self._run_websocket)
        
        display_thread.start()
        websocket_thread.start()
        
        # Wait for threads to complete
        display_thread.join()
        websocket_thread.join()

    def _run_websocket(self):
        """Initialize and run the WebSocket client."""
        self.client.subscribe("T.*")  # Subscribe to all trades
        self.client.run(self._handle_messages)

    def _handle_messages(self, msgs: List[WebSocketMessage]):
        """Process incoming WebSocket messages."""
        for msg in msgs:
            if isinstance(msg, EquityTrade):
                self._process_trade(msg)

    def _process_trade(self, trade: EquityTrade):
        """Process a single trade message and update statistics."""
        if not isinstance(trade.symbol, str):
            return
            
        # Update trade counts
        self.trade_counts_15s[trade.symbol] = self.trade_counts_15s.get(trade.symbol, 0) + 1
        self.total_trade_counts[trade.symbol] = self.total_trade_counts.get(trade.symbol, 0) + 1

        # Calculate and update cash values
        if isinstance(trade.price, float) and isinstance(trade.size, int):
            cash_value = trade.price * trade.size
            
            # Update 15-second statistics
            self.cash_traded_15s += cash_value
            self.cash_volume_15s[trade.symbol] = self.cash_volume_15s.get(trade.symbol, 0) + cash_value
            
            # Update total statistics
            self.total_cash_traded += cash_value
            self.total_cash_volume[trade.symbol] = self.total_cash_volume.get(trade.symbol, 0) + cash_value
            
            # Update counter statistics
            self.total_tickers_seen = len(self.total_trade_counts)
            self.total_trades_seen += 1

    def _print_centered(self, text: str):
        """Print text centered in the terminal."""
        print(text.center(self.terminal_width))

    def _format_duration(self, seconds: float) -> str:
        """Format seconds into HH:MM:SS string."""
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    def _display_statistics(self):
        """Display current market statistics."""
        start_time = time.time()
        
        # Clear screen
        print("\033c", end="")
        print()

        # Display 15-second snapshot
        self._print_centered("--- Past 15 seconds ---")
        self._print_centered(f"Tickers seen (15s): {len(self.trade_counts_15s)}")
        self._print_centered(f"Trades seen (15s): {sum(self.trade_counts_15s.values())}")
        self._print_centered(f"Cash traded (15s): {self.cash_traded_15s:,.0f}")
        
        # Display running totals
        print()
        self._print_centered("--- Running Totals ---")
        self._print_centered(f"Total Tickers seen: {self.total_tickers_seen}")
        self._print_centered(f"Total Trades seen: {self.total_trades_seen}")
        self._print_centered(f"Total Cash traded: {self.total_cash_traded:,.0f}")
        
        # Display table header
        print()
        self._print_centered("-" * 100 + "\n")
        self._print_centered(
            "{:<15}{:<20}{:<20}{:<20}{:<20}".format(
                "Ticker", "Trades (15s)", "Cash (15s)", "Total Trades", "Total Cash"
            )
        )

        # Display top 10 most active symbols
        sorted_symbols = sorted(self.trade_counts_15s.items(), key=lambda x: x[1], reverse=True)[:10]
        for symbol, trades in sorted_symbols:
            self._print_centered(
                "{:<15}{:<20}{:<20,.0f}{:<20}{:<20,.0f}".format(
                    symbol,
                    trades,
                    self.cash_volume_15s.get(symbol, 0),
                    self.total_trade_counts[symbol],
                    self.total_cash_volume.get(symbol, 0.0)
                )
            )

        # Display timing information
        elapsed = time.time() - self.app_start_time
        current_time = datetime.now()
        processing_time = time.time() - start_time
        
        print()
        self._print_centered(
            f"Current Time: {current_time} | "
            f"App Uptime: {self._format_duration(elapsed)} | "
            f"Time taken: {processing_time:.6f} seconds"
        )

    def _run_display_loop(self):
        """Run the display update loop."""
        while True:
            self._display_statistics()
            # Reset 15-second counters
            self.trade_counts_15s.clear()
            self.cash_volume_15s.clear()
            self.cash_traded_15s = 0
            time.sleep(self.update_interval)

def main():
    """Main entry point for the market monitor."""
    API_KEY = "6H8Lc8WQkYoX2BURIOJkqFID9rImFYop"  # Replace with your API key
    monitor = MarketMonitor(API_KEY)
    monitor.start()

if __name__ == "__main__":
    main()