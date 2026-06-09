import json
import asyncio
import websockets

class BinanceWebsocket:
    def __init__(self, symbol="btcusdt", callback=None):
        self.symbol = symbol.lower()
        self.ws_url = f"wss://fstream.binance.com/ws/{self.symbol}@aggTrade"
        self.callback = callback
        self.running = False

    async def start(self):
        self.running = True
        while self.running:
            try:
                async with websockets.connect(self.ws_url) as ws:
                    print(f"Connected to Binance WS: {self.symbol}@aggTrade")
                    while self.running:
                        msg = await ws.recv()
                        data = json.loads(msg)
                        if self.callback:
                            await self.callback(data)
            except Exception as e:
                print(f"WS Error: {e}, reconnecting in 5s...")
                await asyncio.sleep(5)

    def stop(self):
        self.running = False
