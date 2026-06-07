import httpx
from typing import Optional


BIRDEYE_API = "https://public-api.birdeye.so/public"

async def get_holder_count(token_address: str, chain: str = "solana") -> Optional[int]:
    url = f"{BIRDEYE_API}/token_holders?address={token_address}&chain={chain}"
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(url, headers={"x-chain": chain})
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("data", {}).get("items", [])
                return len(items) if items else None
        except Exception:
            pass
    return None


async def get_holder_growth(token_address: str, chain: str = "solana") -> Optional[float]:
    url = f"{BIRDEYE_API}/defi/txlist?address={token_address}&chain={chain}&limit=50"
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(url, headers={"x-chain": chain})
            if resp.status_code == 200:
                data = resp.json()
                txs = data.get("data", {}).get("items", [])
                unique_buyers = set()
                seen_buyers = set()
                from collections import Counter
                for tx in txs:
                    if tx.get("type") == "buy":
                        user = tx.get("user")
                        if user:
                            unique_buyers.add(user)
                return len(unique_buyers)
        except Exception:
            pass
    return None
