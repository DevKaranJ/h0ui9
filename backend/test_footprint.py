import unittest
import logging
from core.strategy.footprint import FootprintCandle, StrategyEngine

logging.basicConfig(level=logging.INFO, format="[TEST-LOG] %(message)s")

class TestStrategy(unittest.TestCase):
    def setUp(self):
        logging.info("--- Starting new test ---")

    def test_footprint_candle_basic(self):
        logging.info("Testing basic FootprintCandle aggregations...")
        candle = FootprintCandle(start_time=1000, tick_size=1.0)

        # is_buyer_maker=True means Sell volume
        candle.add_trade(price=60000, volume=1.5, is_buyer_maker=True)
        candle.add_trade(price=60000, volume=2.0, is_buyer_maker=False)
        candle.add_trade(price=60001, volume=1.0, is_buyer_maker=False)

        self.assertEqual(candle.sell_volume, 1.5)
        self.assertEqual(candle.buy_volume, 3.0)
        self.assertEqual(candle.delta, 1.5)
        self.assertEqual(candle.high, 60001)
        self.assertEqual(candle.low, 60000)

        logging.info(f"Candle verified: delta={candle.delta}, buy_vol={candle.buy_volume}, sell_vol={candle.sell_volume}")

    def test_diagonal_imbalance_detection(self):
        logging.info("Testing 3x Diagonal Imbalance Detection...")
        candle = FootprintCandle(1000, tick_size=10.0)

        # P0: Lower price (sell volume = 1.5)
        candle.add_trade(60000, 1.5, True)

        # P1: Higher price (buy volume = 5.0) -> Buy is > 3x Sell
        candle.add_trade(60010, 5.0, False)

        imbalances = candle.check_imbalances()
        logging.info(f"Imbalances detected: {imbalances}")

        self.assertEqual(len(imbalances), 1)
        self.assertEqual(imbalances[0]['type'], 'buy_imbalance')
        self.assertEqual(imbalances[0]['price'], 60010.0)

    def test_strategy_engine_signals(self):
        logging.info("Testing StrategyEngine Absorption-Initiation Pattern (AIP) logic...")
        engine = StrategyEngine(timeframe_ms=60000) # 1 minute

        # Tick 1: Previous Candle (Bullish Absorption)
        # Open low, high sell volume, but closes higher
        engine.process_tick({'E': 0, 'p': '59990', 'q': '1.0', 'm': False}) # Open
        engine.process_tick({'E': 1000, 'p': '59980', 'q': '10.0', 'm': True}) # Heavy sell
        engine.process_tick({'E': 59000, 'p': '59995', 'q': '1.0', 'm': False}) # Close higher

        # Tick 2: Current Candle (Bullish Initiation)
        # Close previous candle, start new one
        # Create buy imbalance
        engine.process_tick({'E': 60000, 'p': '59995', 'q': '1.0', 'm': True}) # Sell at P0
        engine.process_tick({'E': 65000, 'p': '60005', 'q': '5.0', 'm': False}) # Buy at P1 (imbalance)
        engine.process_tick({'E': 119000, 'p': '60010', 'q': '1.0', 'm': False}) # Close higher

        # Tick 3: Forces closure of Current Candle to evaluate
        engine.process_tick({'E': 120000, 'p': '60010', 'q': '0.1', 'm': False})

        logging.info(f"Signal generated: {engine.signal}")
        self.assertIsNotNone(engine.signal)
        self.assertEqual(engine.signal['action'], 'LONG')
        self.assertEqual(engine.signal['price'], 60010.0)

if __name__ == '__main__':
    unittest.main()
