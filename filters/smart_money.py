from models.token import TokenInfo
from config import SCREENING_CFG

SMART_WALLETS_DB: set[str] = set()

def load_smart_wallets(filepath: str = "smart_wallets.txt"):
    global SMART_WALLETS_DB
    try:
        with open(filepath) as f:
            SMART_WALLETS_DB = {line.strip() for line in f if line.strip()}
    except FileNotFoundError:
        pass


def is_smart_wallet(address: str) -> bool:
    return address.lower() in SMART_WALLETS_DB


def passes_smart_money(token: TokenInfo) -> tuple[bool, str]:
    if not SCREENING_CFG.track_smart_wallets:
        return True, "skipped"
    if token.smart_wallet_count >= SCREENING_CFG.min_smart_wallets:
        return True, f"{token.smart_wallet_count} smart wallet(s)"
    return False, f"Only {token.smart_wallet_count} smart wallet(s)"
