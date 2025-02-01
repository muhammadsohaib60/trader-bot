"""
Trading Strategy Implementation
Handles strategy execution and indicator management for multiple timeframes
"""

from dataclasses import dataclass
from typing import Dict, Optional
import pandas as pd
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class TimeframeData:
    """Container for timeframe-specific market data and indicators"""
    open: float
    high: float
    low: float
    close: float
    volume: float
    vwap: float
    sma3: float
    sl_sma3: float
    sma14: float
    sl_sma14: float
    sma50: float
    sl_sma50: float
    sma200: float
    sl_sma200: float
    bbl_14_2: float
    bbm_14_2: float
    bbu_14_2: float
    bbb_14_2: float
    bbp_14_2: float

class TradingStrategy:
    """Main trading strategy implementation"""
    
    def __init__(self, asset_symbol: str):
        self.asset_symbol = asset_symbol
        self.in_long = False
        self.in_short = False
        
        # Initialize timeframe data containers
        self.data_1m: Optional[TimeframeData] = None
        self.data_5m: Optional[TimeframeData] = None
        self.data_15m: Optional[TimeframeData] = None
        self.data_1d: Optional[TimeframeData] = None

    def is_in_position(self) -> bool:
        """Check if currently in any position"""
        return self.in_long or self.in_short

    def extract_timeframe_data(self, df: pd.DataFrame, suffix: str) -> TimeframeData:
        """Extract indicator values for a specific timeframe"""
        try:
            latest = df.iloc[-1]
            return TimeframeData(
                open=latest[f'open_{suffix}'],
                high=latest[f'high_{suffix}'],
                low=latest[f'low_{suffix}'],
                close=latest[f'close_{suffix}'],
                volume=latest[f'volume_{suffix}'],
                vwap=latest[f'vwap_{suffix}'],
                sma3=latest[f'SMA3_{suffix}'],
                sl_sma3=latest[f'Sl_SMA3_{suffix}'],
                sma14=latest[f'SMA14_{suffix}'],
                sl_sma14=latest[f'Sl_SMA14_{suffix}'],
                sma50=latest[f'SMA50_{suffix}'],
                sl_sma50=latest[f'Sl_SMA50_{suffix}'],
                sma200=latest[f'SMA200_{suffix}'],
                sl_sma200=latest[f'Sl_SMA200_{suffix}'],
                bbl_14_2=latest[f'BBL{suffix}_14_2'],
                bbm_14_2=latest[f'BBM{suffix}_14_2'],
                bbu_14_2=latest[f'BBU{suffix}_14_2'],
                bbb_14_2=latest[f'BBB{suffix}_14_2'],
                bbp_14_2=latest[f'BBP{suffix}_14_2']
            )
        except Exception as e:
            logger.error(f"Error extracting {suffix} timeframe data: {str(e)}")
            raise

    def extract_indicator_values(self, df1min: pd.DataFrame, df5min: pd.DataFrame, 
                               df15min: pd.DataFrame, df1day: pd.DataFrame):
        """Extract all timeframe indicator values"""
        try:
            self.data_1m = self.extract_timeframe_data(df1min, '1M')
            self.data_5m = self.extract_timeframe_data(df5min, '5M')
            self.data_15m = self.extract_timeframe_data(df15min, '15M')
            # Uncomment when 1day data is ready
            # self.data_1d = self.extract_timeframe_data(df1day, '1D')
        except Exception as e:
            logger.error(f"Error extracting indicator values: {str(e)}")
            raise

    def execute_trades(self, df1min: pd.DataFrame):
        """Execute trading logic based on signals"""
        try:
            latest = df1min.iloc[-1]
            in_uptrend = latest['in_uptrend']
            curr_datetime = str(latest['timestamp_1M'])
            curr_close = latest['close']

            if not self.is_in_position() and in_uptrend:
                logger.info(f"{curr_datetime}, {self.asset_symbol} bought at price {curr_close}")
                self.in_long = True
            elif self.is_in_position() and not in_uptrend:
                logger.info(f"{curr_datetime}, {self.asset_symbol} sold at price {curr_close}")
                self.in_long = False

        except Exception as e:
            logger.error(f"Error executing trades: {str(e)}")
            raise

    def evaluate_strategy(self, df1min: pd.DataFrame) -> None:
        """Evaluate and update strategy conditions"""
        try:
            latest = df1min.iloc[-1]
            df1min.loc[df1min.index[-1], 'in_uptrend'] = latest['SL_SMA14_1m'] > 0.1
            self.execute_trades(df1min)
        except Exception as e:
            logger.error(f"Error evaluating strategy: {str(e)}")
            raise

    def run(self, df1min: pd.DataFrame, df5min: pd.DataFrame, 
            df15min: pd.DataFrame, df1day: pd.DataFrame) -> None:
        """Main strategy execution loop"""
        try:
            self.extract_indicator_values(df1min, df5min, df15min, df1day)
            self.evaluate_strategy(df1min)
            logger.info("Strategy execution completed")
        except Exception as e:
            logger.error(f"Error running strategy: {str(e)}")
            raise

def main():
    """Main entry point for strategy execution"""
    try:
        # Example usage
        strategy = TradingStrategy(asset_symbol="EXAMPLE")
        # Add your dataframe initialization here
        # strategy.run(df1min, df5min, df15min, df1day)
    except Exception as e:
        logger.error(f"Main execution error: {str(e)}")
        raise

if __name__ == "__main__":
    main()