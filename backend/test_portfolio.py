import unittest
from core.portfolio import PaperPortfolio

class TestPortfolio(unittest.TestCase):
    def test_execute_trade(self):
        portfolio = PaperPortfolio(initial_balance=10000)
        signal = {
            'action': 'LONG',
            'price': 60000,
            'stop_loss': 59000,
            'timestamp': 123456789
        }
        res = portfolio.execute_trade(signal)
        self.assertEqual(res['status'], 'executed')
        self.assertEqual(len(portfolio.positions), 1)

        # Risk is 1% of 10000 = 100. Price risk is 1000. Position size = 100/1000 = 0.1
        self.assertEqual(portfolio.positions[0]['size'], 0.1)

if __name__ == '__main__':
    unittest.main()
