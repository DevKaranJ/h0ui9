import unittest
from core.strategy.footprint import FootprintCandle, StrategyEngine

class TestStrategy(unittest.TestCase):
    def test_footprint_candle(self):
        candle = FootprintCandle(1000)
        # add_trade(price, volume, is_buyer_maker) (is_buyer_maker=True means sell volume)
        candle.add_trade(60000, 1.5, True) # Sell volume
        candle.add_trade(60000, 2.0, False) # Buy volume

        self.assertEqual(candle.sell_volume, 1.5)
        self.assertEqual(candle.buy_volume, 2.0)
        self.assertEqual(candle.delta, 0.5)

    def test_diagonal_imbalance(self):
        candle = FootprintCandle(1000, tick_size=10.0)

        # P0: Lower price (sell volume = 1.5)
        candle.add_trade(60000, 1.5, True)

        # P1: Higher price (buy volume = 5.0) -> Buy is > 3x Sell
        candle.add_trade(60010, 5.0, False)

        imbalances = candle.check_imbalances()
        self.assertEqual(len(imbalances), 1)
        self.assertEqual(imbalances[0]['type'], 'buy_imbalance')
        self.assertEqual(imbalances[0]['price'], 60010.0)

if __name__ == '__main__':
    unittest.main()
