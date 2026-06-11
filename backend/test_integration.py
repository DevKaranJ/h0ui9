import unittest
import logging
from fastapi.testclient import TestClient
from main import app, engine, portfolio

logging.basicConfig(level=logging.INFO, format="[TEST-LOG] %(message)s")

class TestIntegration(unittest.TestCase):
    def setUp(self):
        logging.info("--- Starting new integration test ---")
        self.client = TestClient(app)
        # Reset global state for clean test run
        engine.current_candle = None
        engine.closed_candles = []
        engine.cvd = 0.0
        engine.signal = None
        engine.timeframe_ms = 60000 # Set specifically for test timing
        portfolio.balance = 10000.0
        portfolio.equity = 10000.0
        portfolio.positions = []

    def test_websocket_broadcast_and_trade_flow(self):
        logging.info("Testing WebSocket broadcast and full tick-to-portfolio flow...")

        # Manually invoke the tick handler (which also triggers WebSocket broadcast)
        from main import handle_trade_tick
        import asyncio

        # We need to run the async handler in a sync wrapper for the test
        def run_tick(data):
            asyncio.run(handle_trade_tick(data))

        logging.info("Injecting Tick 1 (Previous Candle, Bearish Move, Heavy Sell)")
        run_tick({'E': 0, 'p': '49990', 'q': '1.0', 'm': False})
        run_tick({'E': 1000, 'p': '49980', 'q': '10.0', 'm': True})
        run_tick({'E': 59000, 'p': '49995', 'q': '1.0', 'm': False}) # Closes higher than the dump (Absorption)

        # Verify REST API state
        response = self.client.get("/api/state")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        logging.info(f"REST API State after Tick 1: {data}")
        self.assertEqual(data['portfolio']['balance'], 10000.0)

        logging.info("Injecting Tick 2 (Current Candle, Bullish Initiation, Buy Imbalance)")
        run_tick({'E': 60000, 'p': '49995', 'q': '1.0', 'm': True}) # Sell P0
        run_tick({'E': 65000, 'p': '50005', 'q': '5.0', 'm': False}) # Buy P1
        run_tick({'E': 119000, 'p': '50010', 'q': '1.0', 'm': False}) # Close higher

        logging.info("Injecting Tick 3 (Close current candle and execute signal)")
        run_tick({'E': 120000, 'p': '50010', 'q': '0.1', 'm': False})

        # Verify Portfolio has executed the trade
        state = portfolio.get_state()
        logging.info(f"Final Portfolio State: {state}")
        self.assertEqual(len(state['open_positions']), 1)
        active_pos = state['open_positions'][0]
        self.assertEqual(active_pos['action'], 'LONG')
        self.assertEqual(active_pos['entry_price'], 50010.0)

    def test_websocket_connection(self):
        logging.info("Testing WebSocket Connection directly...")
        with self.client.websocket_connect("/ws") as websocket:
            logging.info("WebSocket connected successfully.")
            self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
