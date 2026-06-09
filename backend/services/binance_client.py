import ccxt
import pandas as pd

class BinanceClient:
    def __init__(self, testnet=True):
        self.exchange = ccxt.binanceusdm({
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',
            }
        })
        if testnet:
            self.exchange.set_sandbox_mode(True)

    def fetch_htf_candles(self, symbol="BTC/USDT", timeframe="1h", limit=100):
        """Fetch Higher Timeframe candles for Structural Zones"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            print(f"Error fetching HTF candles: {e}")
            return None
