import httpx
from typing import Optional
from models.token import TokenInfo


DEXSCREENER_API = "https://api.dexscreener.com/latest/dex"

def parse_token(raw: dict, chain: str) -> Optional[TokenInfo]:
    try:
        pairs = raw.get("pairs", [])
        if not pairs:
            return None
        pair = pairs[0]
        base = pair.get("baseToken", {})
        age = pair.get("pairCreatedAt")
        return TokenInfo(
            address=base.get("address", ""),
            chain=chain,
            symbol=base.get("symbol", ""),
            name=base.get("name", ""),
            created_at=age,
            liquidity_usd=float(pair.get("liquidity", {}).get("usd", 0) or 0),
            market_cap_usd=float(pair.get("marketCap", 0) or 0),
            price_usd=float(pair.get("priceUsd", 0) or 0),
            volume_24h=float(pair.get("volume", {}).get("h24", 0) or 0),
            tx_count_buy=int(pair.get("txns", {}).get("h24", {}).get("buys", 0) or 0),
            tx_count_sell=int(pair.get("txns", {}).get("h24", {}).get("sells", 0) or 0),
        )
    except Exception:
        return None


async def search_token(query: str) -> list[TokenInfo]:
    url = f"{DEXSCREENER_API}/search?q={query}"
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url)
        if resp.status_code != 200:
            return []
        data = resp.json()
        pairs = data.get("pairs", [])
        results = []
        seen = set()
        for p in pairs:
            chain = p.get("chainId", "unknown")
            tok = parse_token({"pairs": [p]}, chain)
            if tok and tok.address not in seen:
                seen.add(tok.address)
                results.append(tok)
        return results


async def get_new_pairs(chain: str = "solana") -> list[TokenInfo]:
    url = f"{DEXSCREENER_API}/pairs/{chain}"
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url)
        if resp.status_code != 200:
            return []
        data = resp.json()
        pairs = data.get("pairs", [])
        tokens = []
        seen = set()
        for p in pairs:
            tok = parse_token({"pairs": [p]}, chain)
            if tok and tok.address not in seen:
                seen.add(tok.address)
                tokens.append(tok)
        return tokens
