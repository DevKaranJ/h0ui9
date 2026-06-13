class PaperPortfolio:
    def __init__(self, initial_balance=10000.0):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.equity = initial_balance
        self.positions = []
        self.trades_history = []

        # Risk Management Rules
        self.max_account_risk_pct = 0.10  # 10% overall
        self.risk_per_trade_pct = 0.01    # 1% per trade

    def execute_trade(self, signal):
        """Execute a trade based on signal if risk parameters allow"""
        if not signal:
            return None

        action = signal['action']
        entry_price = signal['price']
        stop_loss = signal['stop_loss']

        # Check active positions
        if any(p['active'] for p in self.positions):
            return {"status": "rejected", "reason": "Already in a position"}

        # Calculate Risk and Position Size
        risk_amount = self.equity * self.risk_per_trade_pct
        price_risk = abs(entry_price - stop_loss)

        if price_risk <= 0:
            return {"status": "rejected", "reason": "Invalid Stop Loss"}

        # Position size = Risk Amount / Risk per unit
        position_size = risk_amount / price_risk

        # Check against total account risk (Drawdown protection)
        if self.equity < self.initial_balance * (1 - self.max_account_risk_pct):
            return {"status": "rejected", "reason": "Max account drawdown reached"}

        position = {
            'action': action,
            'entry_price': entry_price,
            'size': position_size,
            'stop_loss': stop_loss,
            'take_profit': entry_price + (price_risk * 2) if action == 'LONG' else entry_price - (price_risk * 2), # 1:2 RR
            'active': True,
            'pnl': 0.0
        }

        self.positions.append(position)
        return {"status": "executed", "position": position}

    def update_positions(self, current_price):
        """Update active positions based on current market price"""
        for p in self.positions:
            if not p['active']:
                continue

            if p['action'] == 'LONG':
                p['pnl'] = (current_price - p['entry_price']) * p['size']
                if current_price <= p['stop_loss'] or current_price >= p['take_profit']:
                    self.close_position(p, current_price)
            else:
                p['pnl'] = (p['entry_price'] - current_price) * p['size']
                if current_price >= p['stop_loss'] or current_price <= p['take_profit']:
                    self.close_position(p, current_price)

        # Performance optimization: Prune closed positions from `self.positions` array
        # `trades_history` natively handles full historical tracking of closed trades
        # This prevents an O(N) iteration scaling problem on every single tick
        self.positions = [p for p in self.positions if p['active']]

        # Update Equity
        active_pnl = sum(p['pnl'] for p in self.positions)
        self.equity = self.balance + active_pnl

    def close_position(self, position, exit_price):
        position['active'] = False
        position['exit_price'] = exit_price
        self.balance += position['pnl']
        self.trades_history.append(position)

    def get_state(self):
        return {
            "balance": self.balance,
            "equity": self.equity,
            "open_positions": [p for p in self.positions if p['active']],
            "total_trades": len(self.trades_history)
        }
