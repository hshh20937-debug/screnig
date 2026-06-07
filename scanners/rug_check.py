import httpx
from typing import Optional


RUGCHECK_API = "https://api.rugcheck.xyz/v1"

def parse_rugcheck(data: dict) -> dict:
    result = {
        "lp_burned": False,
        "lp_locked": False,
        "mintable": False,
        "top_holder_pct": 0.0,
        "creator_pct": 0.0,
        "risks": [],
    }
    try:
        top_holders = data.get("topHolders", [])
        if top_holders:
            total = sum(h.get("pct", 0) for h in top_holders)
            result["top_holder_pct"] = total

        creator = data.get("creator")
        if creator and top_holders:
            creator_addr = creator.get("address", "")
            for h in top_holders:
                if h.get("address", "").lower() == creator_addr.lower():
                    result["creator_pct"] = h.get("pct", 0)
                    break

        for risk in data.get("risks", []):
            name = (risk.get("name") or "").lower()
            if "mint" in name:
                result["mintable"] = True
            if "lp" in name and "burn" in name:
                result["lp_burned"] = True
            if "lp" in name and ("lock" in name or "frozen" in name):
                result["lp_locked"] = True
    except Exception:
        pass
    return result


async def check_token(token_address: str, chain: str = "solana") -> Optional[dict]:
    url = f"{RUGCHECK_API}/tokens/{token_address}/report/summary"
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(url)
            if resp.status_code == 200:
                return parse_rugcheck(resp.json())
        except Exception:
            pass
    return None
