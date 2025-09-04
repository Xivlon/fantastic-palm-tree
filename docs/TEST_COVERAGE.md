# Test Coverage Overview

(See README.md "Test Coverage Summary" for a short highlight list.)

This document summarizes behaviors currently validated by the strategy test suite and highlights planned additions / gaps.

Last updated: 2025-09-04

## 1. Entry & Position Lifecycle
- Long & short entry signals (indicator gating).
- ATR-based position sizing respecting risk fraction.
- Per-symbol equity cap enforcement.
- Short selling disabled flag (blocks shorts when `allow_shorts = False`).

## 2. Partial Exit Logic
- Single partial execution per bar even if multiple thresholds surpassed.
- Partial priority over trailing stop when both would trigger in same bar.
- Short-side partial profit realization.

## 3. Trailing Stops
- Activation threshold (R-multiple gating) before trailing becomes active.
- Percent trailing variant.
- ATR trailing: dynamic distance expansion when volatility (ATR) rises.
- Dynamic ATR minimum samples respected (no premature sizing).

## 4. Risk Management / Global Guards
- Drawdown kill switch (equity based) triggers and halts new entries.
- (Planned) Daily loss limit explicit test.

## 5. Sizing & Capital Allocation
- Equity cap per symbol.
- (Planned) Max simultaneous positions across symbols.
- (Planned) ADV / liquidity gating if introduced.

## 6. Metrics & Trade Records
- Executed partial level tracking.
- Implicit R-multiple confirmation through threshold fulfillment.
- (Planned) Direct R-multiple aggregation & exposure duration tests.

## 7. Known Gaps / Future Tests
| Area | Suggested Test |
|------|----------------|
| Commission & slippage tiers | Validate adjusted fill price / PnL net of costs |
| Daily loss kill switch | Force cumulative intraday losses beyond threshold |
| Multiple symbol concurrency | Enforce `max_simultaneous_positions` |
| Reversals (long -> short same bar) | Ensure close & new open atomicity |
| Trailing after partial scaling | Validate trailing anchor after size reduction |
| ATR edge cases | Very low ATR then spike; ensure no oversizing |
| Cost aggregation metrics | Confirm gross vs net PnL metrics alignment |
| Serialization / persistence | Roundtrip state integrity (if state saved) |
| Timezone / DST handling | Ensure bar alignment across transitions |

## 8. Running Tests
```
pytest -q
pytest -k partial
pytest --cov=. --cov-report=term-missing
```

## 9. Contributing New Tests
1. Reuse fixtures from `tests/conftest.py`.
2. Prefer parametrization for config variations (partials / trailing / sides).
3. Keep internal attribute access isolated; migrate to public accessors where possible.
4. Tag slow tests with `@pytest.mark.slow`.
5. Add new gap items here when proposing new behavioral areas.

## 10. Maintenance
- Revisit gap list periodically.
- Add dedicated suite when introducing new exit or risk features.
- Remove redundant legacy tests once covered by parametrized variants.