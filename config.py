from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ScreeningConfig:
    liquidity_min: float = 0
    liquidity_max: float = 50_000
    skip_liquidity_if_zero: bool = True
    market_cap_min: float = 3_000
    max_age_hours: float = 24
    min_holders: int = 5
    max_holders: int = 5000
    # anti-rug
    check_lp_burn: bool = False
    check_lp_lock: bool = False
    top_holder_max_pct: float = 30.0
    creator_max_pct: float = 15.0
    block_mintable: bool = True
    # momentum
    buy_ratio_min: float = 1.2
    holder_growth_min_pct: float = 5.0
    min_tx_count: int = 20
    # smart money
    track_smart_wallets: bool = True
    min_smart_wallets: int = 1
    # chain
    chains: list[str] = field(default_factory=lambda: ["solana"])
    # polling
    poll_interval_seconds: int = 30
    new_token_window_minutes: int = 5


SCREENING_CFG = ScreeningConfig()
