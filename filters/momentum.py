from models.token import TokenInfo
from config import SCREENING_CFG


def passes_momentum(token: TokenInfo) -> tuple[bool, str]:
    reasons = []

    bsr = token.buy_sell_ratio
    if bsr < SCREENING_CFG.buy_ratio_min:
        reasons.append(f"Buy/sell {bsr:.2f} < {SCREENING_CFG.buy_ratio_min}")

    total_tx = token.tx_count_buy + token.tx_count_sell
    if total_tx < SCREENING_CFG.min_tx_count:
        reasons.append(f"Txs {total_tx} < {SCREENING_CFG.min_tx_count}")

    if token.holder_growth_1h_pct > 0 and token.holder_growth_1h_pct < SCREENING_CFG.holder_growth_min_pct:
        reasons.append(f"Holder growth {token.holder_growth_1h_pct:.1f}% < {SCREENING_CFG.holder_growth_min_pct}%")

    if reasons:
        return False, "; ".join(reasons)
    return True, "ok"
