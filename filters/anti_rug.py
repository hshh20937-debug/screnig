from models.token import TokenInfo
from config import SCREENING_CFG


def passes_anti_rug(token: TokenInfo) -> tuple[bool, str]:
    reasons = []

    if SCREENING_CFG.check_lp_burn and not token.lp_burned:
        reasons.append("LP not burned")
    if SCREENING_CFG.check_lp_lock and not token.lp_locked:
        reasons.append("LP not locked")
    if token.top_holder_pct > SCREENING_CFG.top_holder_max_pct:
        reasons.append(f"Top holder {token.top_holder_pct:.1f}% > {SCREENING_CFG.top_holder_max_pct}%")
    if token.creator_pct > SCREENING_CFG.creator_max_pct:
        reasons.append(f"Creator holds {token.creator_pct:.1f}% > {SCREENING_CFG.creator_max_pct}%")
    if SCREENING_CFG.block_mintable and token.mintable:
        reasons.append("Mint function active")

    if reasons:
        return False, "; ".join(reasons)
    return True, "ok"
