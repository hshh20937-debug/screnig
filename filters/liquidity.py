from models.token import TokenInfo
from config import SCREENING_CFG


def passes_liquidity(token: TokenInfo) -> tuple[bool, str]:
    liq = token.liquidity_usd
    if liq < SCREENING_CFG.liquidity_min:
        return False, f"Liquidity ${liq:.0f} < ${SCREENING_CFG.liquidity_min:,.0f}"
    if liq > SCREENING_CFG.liquidity_max:
        return False, f"Liquidity ${liq:.0f} > ${SCREENING_CFG.liquidity_max:,.0f}"
    return True, "ok"


def passes_market_cap(token: TokenInfo) -> tuple[bool, str]:
    mc = token.market_cap_usd
    if mc < SCREENING_CFG.market_cap_min:
        return False, f"MCap ${mc:.0f} < ${SCREENING_CFG.market_cap_min:,.0f}"
    return True, "ok"


def passes_age(token: TokenInfo) -> tuple[bool, str]:
    age = token.age_hours
    if age is None:
        return True, "unknown"
    if age > SCREENING_CFG.max_age_hours:
        return False, f"Age {age:.1f}h > {SCREENING_CFG.max_age_hours}h"
    return True, "ok"


def passes_holder_count(token: TokenInfo) -> tuple[bool, str]:
    h = token.holder_count
    if h < SCREENING_CFG.min_holders:
        return False, f"Holders {h} < {SCREENING_CFG.min_holders}"
    return True, "ok"
