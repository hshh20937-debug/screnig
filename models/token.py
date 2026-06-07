from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

try:
    UTC = timezone.UTC
except AttributeError:
    UTC = timezone.utc


@dataclass
class TokenInfo:
    address: str
    chain: str
    symbol: str
    name: str
    created_at: Optional[int] = None
    liquidity_usd: float = 0.0
    market_cap_usd: float = 0.0
    price_usd: float = 0.0
    volume_24h: float = 0.0
    tx_count_buy: int = 0
    tx_count_sell: int = 0
    holder_count: int = 0
    holder_growth_1h_pct: float = 0.0
    top_holder_pct: float = 0.0
    creator_pct: float = 0.0
    lp_burned: bool = False
    lp_locked: bool = False
    mintable: bool = False
    score: float = 0.0
    smart_wallet_count: int = 0
    tags: list[str] = field(default_factory=list)

    @property
    def buy_sell_ratio(self) -> float:
        if self.tx_count_sell == 0:
            return float("inf")
        return self.tx_count_buy / self.tx_count_sell

    @property
    def age_hours(self) -> Optional[float]:
        if self.created_at is None:
            return None
        now = datetime.now(UTC).timestamp() * 1000
        delta_ms = now - self.created_at
        return delta_ms / 3600000
