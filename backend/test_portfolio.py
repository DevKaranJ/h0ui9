import unittest
import logging
from core.portfolio import PaperPortfolio

logging.basicConfig(level=logging.INFO, format="[TEST-LOG] %(message)s")

class TestPortfolio(unittest.TestCase):
    def setUp(self):
        logging.info("--- Starting new portfolio test ---")

    def test_execute_trade_success_and_risk_limit(self):
        logging.info("Testing execution and risk limits...")
        portfolio = PaperPortfolio(initial_balance=10000)

        signal = {
            'action': 'LONG',
            'price': 60000,
            'stop_loss': 59000,
            'timestamp': 123456789
        }
        res = portfolio.execute_trade(signal)
        logging.info(f"Trade result: {res}")
        self.assertEqual(res['status'], 'executed')

        # Risk is 1% of 10000 = 100. Price risk is 1000. Position size = 100/1000 = 0.1
        self.assertEqual(portfolio.positions[0]['size'], 0.1)

        # Try to open another trade while one is active
        res2 = portfolio.execute_trade(signal)
        logging.info(f"Second trade result: {res2}")
        self.assertEqual(res2['status'], 'rejected')
        self.assertEqual(res2['reason'], 'Already in a position')

    def test_position_pnl_and_take_profit(self):
        logging.info("Testing PnL calculation and Take Profit execution...")
        portfolio = PaperPortfolio(initial_balance=10000)
        signal = {
            'action': 'LONG',
            'price': 60000,
            'stop_loss': 59000,
            'timestamp': 123456789
        }
        portfolio.execute_trade(signal) # Position size = 0.1, Risk = 100, TP = 62000 (1:2 RR)

        # Update price to 61000 (+$1000 per BTC * 0.1 = +$100 PnL)
        portfolio.update_positions(61000)
        active_pos = portfolio.positions[0]
        logging.info(f"Position state at 61000: {active_pos}")
        self.assertEqual(active_pos['pnl'], 100.0)
        self.assertEqual(portfolio.equity, 10100.0)
        self.assertTrue(active_pos['active'])

        # Update price to 62000 (Take Profit hit)
        portfolio.update_positions(62000)
        logging.info(f"Position state at 62000: {active_pos}")
        self.assertFalse(active_pos['active'])
        self.assertEqual(portfolio.balance, 10200.0)
        self.assertEqual(portfolio.equity, 10200.0)

    def test_max_drawdown_protection(self):
        logging.info("Testing Max Drawdown protection (10%)...")
        portfolio = PaperPortfolio(initial_balance=10000)
        # Force a massive loss to put balance below 9000
        portfolio.balance = 8900
        portfolio.equity = 8900

        signal = {'action': 'LONG', 'price': 60000, 'stop_loss': 59000, 'timestamp': 123}
        res = portfolio.execute_trade(signal)
        logging.info(f"Trade result during drawdown: {res}")
        self.assertEqual(res['status'], 'rejected')
        self.assertEqual(res['reason'], 'Max account drawdown reached')

if __name__ == '__main__':
    unittest.main()
