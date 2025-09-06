from enhancements_strategy import (
    BrokerInterface, Position, ExecutionEngine, 
    create_slippage_model, create_commission_model
)


class TrackingBroker(BrokerInterface):
    """
    Broker stub that mirrors fills into position state so PositionManager
    logic relying on current quantity can function in tests.
    After each ctx.process_symbol(...) call, invoke broker.apply_fills(fills)
    to update synthetic position state.
    
    Enhanced with realistic execution modeling for slippage and commissions.
    """

    def __init__(self, starting_equity=100_000, 
                 slippage_config: dict | None = None,
                 commission_config: dict | None = None,
                 enable_realistic_execution: bool = False):
        super().__init__(starting_equity)
        self._total_commission = 0.0  # Track total commissions paid
        
        # Set up realistic execution if enabled
        if enable_realistic_execution:
            slippage_model = create_slippage_model(slippage_config or {})
            commission_model = create_commission_model(commission_config or {})
            execution_engine = ExecutionEngine(
                slippage_model=slippage_model,
                commission_model=commission_model
            )
            self.set_execution_engine(execution_engine)

    @property
    def equity(self):
        # Adjust equity for commissions paid
        return self._equity - self._total_commission

    @property 
    def total_commission(self):
        """Get total commission paid"""
        return self._total_commission

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
        """Apply fills to position tracking and account for commissions"""
        for f in fills:
            # Track commission if present
            if hasattr(f, 'commission') and f.commission > 0:
                self._total_commission += f.commission
            
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
