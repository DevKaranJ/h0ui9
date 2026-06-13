import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from services.binance_ws import BinanceWebsocket
from core.strategy.footprint import StrategyEngine
from core.portfolio import PaperPortfolio
import time

app = FastAPI(title="Crypto Order Flow Terminal API")

# SECURITY: Restrict CORS origins to local frontend dev environments
# allowing "*" with allow_credentials=True is highly insecure and leads to CSRF/Data leakage
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Global State
engine = StrategyEngine(timeframe_ms=5 * 60 * 1000) # 5m candles
portfolio = PaperPortfolio(initial_balance=10000.0)
ws_clients = []
binance_ws = None
last_broadcast_time = 0

async def broadcast_state():
    global last_broadcast_time
    if not ws_clients:
        return

    # Throttle broadcast to max 10 times per second (every 100ms)
    current_time = time.time()
    if current_time - last_broadcast_time < 0.1:
        return
    last_broadcast_time = current_time

    state = {
        "portfolio": portfolio.get_state(),
        "strategy": {
            "cvd": engine.cvd,
            "current_price": engine.current_candle.close if engine.current_candle else None,
            "signal": engine.signal
        }
    }

    if engine.current_candle:
        state["footprint"] = {
            "levels": engine.current_candle.volume_profile,
            "delta": engine.current_candle.delta
        }

    dead_clients = []
    for client in ws_clients:
        try:
            await client.send_json(state)
        except Exception:
            dead_clients.append(client)

    for dead_client in dead_clients:
        if dead_client in ws_clients:
            ws_clients.remove(dead_client)

async def handle_trade_tick(data):
    engine.process_tick(data)

    current_price = float(data['p'])
    portfolio.update_positions(current_price)

    if engine.signal:
        res = portfolio.execute_trade(engine.signal)
        if res and res['status'] == 'executed':
            print(f"Trade Executed: {res['position']}")
        engine.signal = None

    await broadcast_state()

@app.on_event("startup")
async def startup_event():
    global binance_ws
    binance_ws = BinanceWebsocket(symbol="btcusdt", callback=handle_trade_tick)
    asyncio.create_task(binance_ws.start())

@app.on_event("shutdown")
def shutdown_event():
    if binance_ws:
        binance_ws.stop()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    ws_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        pass
    finally:
        if websocket in ws_clients:
            ws_clients.remove(websocket)

@app.get("/api/state")
def get_state():
    return {
        "portfolio": portfolio.get_state(),
        "cvd": engine.cvd
    }
