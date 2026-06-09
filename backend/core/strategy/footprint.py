import pandas as pd
from typing import Dict, List

class FootprintCandle:
    def __init__(self, start_time: int, tick_size: float = 0.5):
        self.start_time = start_time
        self.tick_size = tick_size
        self.open = None
        self.high = float('-inf')
        self.low = float('inf')
        self.close = None
        self.volume = 0
        self.buy_volume = 0
        self.sell_volume = 0
        self.delta = 0

        # price_level -> {'buy': vol, 'sell': vol}
        self.volume_profile: Dict[float, Dict[str, float]] = {}

    def add_trade(self, price: float, volume: float, is_buyer_maker: bool):
        if self.open is None:
            self.open = price
        self.high = max(self.high, price)
        self.low = min(self.low, price)
        self.close = price
        self.volume += volume

        # Binance aggTrade: is_buyer_maker=True means the trade was executed against a resting BUY order
        # meaning the taker was a SELLER. So is_buyer_maker=True -> Sell volume.
        is_sell = is_buyer_maker

        # Round price to nearest tick
        price_level = round(price / self.tick_size) * self.tick_size

        if price_level not in self.volume_profile:
            self.volume_profile[price_level] = {'buy': 0, 'sell': 0}

        if is_sell:
            self.volume_profile[price_level]['sell'] += volume
            self.sell_volume += volume
            self.delta -= volume
        else:
            self.volume_profile[price_level]['buy'] += volume
            self.buy_volume += volume
            self.delta += volume

    def check_imbalances(self, threshold_multiplier=3.0) -> List[Dict]:
        """Check for 3x diagonal imbalances"""
        imbalances = []
        levels = sorted(self.volume_profile.keys())

        for i in range(len(levels) - 1):
            lower_price = levels[i]
            higher_price = levels[i+1]

            lower_node = self.volume_profile[lower_price]
            higher_node = self.volume_profile[higher_price]

            # Buy Imbalance: Buy Vol at P1 >= 3x Sell Vol at P0 (diagonally lower)
            if higher_node['buy'] >= (lower_node['sell'] * threshold_multiplier) and higher_node['buy'] > 0:
                # ignore small volumes to reduce noise (e.g., > 1 BTC)
                if higher_node['buy'] > 1.0:
                    imbalances.append({
                        'type': 'buy_imbalance',
                        'price': higher_price,
                        'volume': higher_node['buy'],
                        'compared_sell': lower_node['sell']
                    })

            # Sell Imbalance: Sell Vol at P1 >= 3x Buy Vol at P2 (diagonally higher)
            if lower_node['sell'] >= (higher_node['buy'] * threshold_multiplier) and lower_node['sell'] > 0:
                if lower_node['sell'] > 1.0:
                    imbalances.append({
                        'type': 'sell_imbalance',
                        'price': lower_price,
                        'volume': lower_node['sell'],
                        'compared_buy': higher_node['buy']
                    })

        return imbalances

class StrategyEngine:
    def __init__(self, timeframe_ms: int = 5 * 60 * 1000):
        self.timeframe_ms = timeframe_ms
        self.current_candle = None
        self.closed_candles = []
        self.cvd = 0.0

        # HTF Zones
        self.htf_supply_zones = []
        self.htf_demand_zones = []

        self.last_absorption = None
        self.signal = None

    def process_tick(self, trade_data: dict):
        timestamp = trade_data['E']  # Event time
        price = float(trade_data['p'])
        qty = float(trade_data['q'])
        is_buyer_maker = trade_data['m']

        candle_start = (timestamp // self.timeframe_ms) * self.timeframe_ms

        if self.current_candle is None:
            self.current_candle = FootprintCandle(candle_start)

        elif candle_start > self.current_candle.start_time:
            self.close_candle()
            self.current_candle = FootprintCandle(candle_start)

        self.current_candle.add_trade(price, qty, is_buyer_maker)

    def close_candle(self):
        if not self.current_candle:
            return

        self.cvd += self.current_candle.delta
        self.current_candle.cvd_value = self.cvd
        self.closed_candles.append(self.current_candle)

        # Limit history
        if len(self.closed_candles) > 100:
            self.closed_candles.pop(0)

        self.evaluate_strategy()

    def evaluate_strategy(self):
        if len(self.closed_candles) < 2:
            return

        prev_candle = self.closed_candles[-2]
        curr_candle = self.closed_candles[-1]

        imbalances = curr_candle.check_imbalances()

        # 1. Check for Absorption in previous candle (simplified)
        # e.g., Bullish Absorption: High sell delta but closed green
        is_bullish_absorption = prev_candle.close > prev_candle.open and prev_candle.delta < 0
        is_bearish_absorption = prev_candle.close < prev_candle.open and prev_candle.delta > 0

        # 2. Check for Initiation in current candle (simplified)
        has_buy_imbalance = any(i['type'] == 'buy_imbalance' for i in imbalances)
        has_sell_imbalance = any(i['type'] == 'sell_imbalance' for i in imbalances)

        is_bullish_initiation = curr_candle.close > curr_candle.open and has_buy_imbalance
        is_bearish_initiation = curr_candle.close < curr_candle.open and has_sell_imbalance

        # 3. CVD Divergence (simplified check against recent price vs CVD trend)

        if is_bullish_absorption and is_bullish_initiation:
            self.signal = {
                'action': 'LONG',
                'price': curr_candle.close,
                'stop_loss': prev_candle.low - 5, # Simplification
                'timestamp': curr_candle.start_time
            }

        elif is_bearish_absorption and is_bearish_initiation:
            self.signal = {
                'action': 'SHORT',
                'price': curr_candle.close,
                'stop_loss': prev_candle.high + 5,
                'timestamp': curr_candle.start_time
            }
