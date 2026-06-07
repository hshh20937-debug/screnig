from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ScreeningConfig:
    liquidity_min: float = 5_000
    liquidity_max: float = 20_000
    market_cap_min: float = 10_000
    max_age_hours: float = 24
    min_holders: int = 50
    max_holders: int = 500
    # anti-rug
    check_lp_burn: bool = True
    check_lp_lock: bool = True
    top_holder_max_pct: float = 15.0
    creator_max_pct: float = 8.0
    block_mintable: bool = True
    # momentum
    buy_ratio_min: float = 1.2
    holder_growth_min_pct: float = 10.0
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
