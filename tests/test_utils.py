from enhancements_strategy import BrokerInterface, Position

class TrackingBroker(BrokerInterface):
    """
    Broker stub that mirrors fills into position state so PositionManager
    logic relying on current quantity can function in tests.
    After each ctx.process_symbol(...) call, invoke broker.apply_fills(fills)
    to update synthetic position state.
    """
    def __init__(self, starting_equity=100_000):
        self._equity = starting_equity
        self._positions = {}

    @property
    def equity(self):
        return self._equity

    def adjust_equity(self, new_equity):
        self._equity = new_equity

    def get_position(self, symbol: str):
        return self._positions.get(symbol)

    def open_positions(self):
        return list(self._positions.values())

    def execute(self, orders, slippage_model=None, commission_model=None):
        # Real execution happens inside strategy logic (fills list).
        return []

    def flatten_all(self):
        self._positions.clear()

    def apply_fills(self, fills):
        for f in fills:
            pos = self._positions.get(f.symbol)
            signed_qty = f.qty if f.side == "BUY" else -f.qty
            if pos is None:
                self._positions[f.symbol] = Position(
                    symbol=f.symbol,
                    qty=signed_qty,
                    avg_price=f.price,
                )
            else:
                # Same direction scale-in
                if (pos.qty > 0 and signed_qty > 0) or (pos.qty < 0 and signed_qty < 0):
                    total_val_prev = pos.avg_price * abs(pos.qty)
                    total_val_new = f.price * f.qty
                    new_qty = abs(pos.qty) + f.qty
                    pos.avg_price = (total_val_prev + total_val_new) / new_qty
                    pos.qty += signed_qty
                else:
                    # Reducing / closing / reversing
                    pos.qty += signed_qty
                    if pos.qty == 0:
                        pos.avg_price = 0.0
