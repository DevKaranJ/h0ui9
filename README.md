# Fincept Crypto Trading Terminal

A highly advanced, personalized crypto trading terminal heavily inspired by Bloomberg and Fincept. This project features a custom-built order flow execution engine operating on Binance Perpetual Futures, visualizing volume footprints, and automating trades based on institutional Absorption-Initiation mechanics.

## 🏗️ Architecture

The application is split into two main components:

1. **Backend (Python / FastAPI):**
   - Connects to Binance WebSockets (`aggTrade` stream) for real-time tick data.
   - Computes **Volume Footprints** (Bid/Ask clusters inside 5-minute candles).
   - Calculates **Cumulative Volume Delta (CVD)**.
   - Executes a high-frequency order flow strategy looking for 3x Diagonal Imbalances and Absorption-Initiation Patterns.
   - Runs a **Paper Trading & Risk Management Engine** enforcing a maximum 10% account drawdown and a strict 1% risk limit per trade.

2. **Frontend (React / Next.js / Tailwind CSS):**
   - A dark-mode, advanced data grid UI (no traditional candlestick charts).
   - Connects to the backend via WebSockets to stream real-time data.
   - Displays live footprint depth, portfolio equity, active signals, and system logs.

---

## 🚀 How to Run the Application

You will need to run the backend and frontend simultaneously in two separate terminal windows.

### Prerequisites
- [Python 3.10+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/en/download/)

### 1. Start the Backend Server

Open a terminal window and execute the following:

`cd backend`

`python3 -m venv venv`

`source venv/bin/activate`

`pip install -r requirements.txt`

`python -m uvicorn main:app --host 127.0.0.1 --port 8000`

*The server will start on `http://127.0.0.1:8000` and automatically connect to Binance.*

### 2. Start the Frontend UI

Open a **second** terminal window and execute the following:

`cd frontend`

`npm install`

`npm run start` (or `npm run dev` for development)

### 3. Open the Terminal

Open your web browser and navigate to:
**[http://localhost:3000](http://localhost:3000)**

You should see the terminal UI load. Within a few seconds, the "Order Flow / Footprint" table will begin populating with live market data from Binance.

---

## 📈 The Trading Strategy & Risk

This terminal is configured to execute a specific Crypto Perpetual Futures Order Flow strategy.

### Core Mechanics
*   **Timeframes:** 5-Minute (Execution). Higher Timeframe (4H) zones are tracked.
*   **Diagonal Imbalances:** The engine looks for a 3x (300%) diagonal imbalance between Buy volume and Sell volume at adjacent price levels.
*   **Absorption-Initiation Pattern (AIP):** Looks for an "Absorption Candle" (heavy aggressive market orders trapped by limit orders, evidenced by CVD divergence) followed immediately by an "Initiation Candle" (aggressive market momentum pushing in the reversal direction with fresh imbalances).

### Risk Management (Hardcoded)
Because crypto futures are highly volatile, strict risk constraints are enforced by the Paper Portfolio engine:
*   **Starting Equity:** \$10,000.00
*   **Max Risk Per Trade:** 1.0%
*   **Max Total Account Drawdown:** 10.0%
*   **Security:** This app is designed for local, unauthenticated paper trading. It does not require API keys or logins.

---

## 🛠️ Future Iterations

*   Implementation of live automated scanning for 4H/1H Structural Supply & Demand Zones.
*   More granular configuration options for footprint tick sizes via a UI settings panel.
*   Interactive heatmaps layered into the data grid.
