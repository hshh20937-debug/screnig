import httpx
from typing import Optional
from models.token import TokenInfo


DEXSCREENER_API = "https://api.dexscreener.com/latest/dex"
TOKEN_PROFILES_API = "https://api.dexscreener.com/token-profiles/latest/v1"


def parse_token(pair: dict) -> Optional[TokenInfo]:
    try:
        base = pair.get("baseToken", {})
        chain = pair.get("chainId", "unknown")
        age_ts = pair.get("pairCreatedAt")
        return TokenInfo(
            address=base.get("address", ""),
            chain=chain,
            symbol=base.get("symbol", ""),
            name=base.get("name", ""),
            created_at=age_ts,
            liquidity_usd=float(pair.get("liquidity", {}).get("usd", 0) or 0),
            market_cap_usd=float(pair.get("marketCap", 0) or 0),
            price_usd=float(pair.get("priceUsd", 0) or 0),
            volume_24h=float(pair.get("volume", {}).get("h24", 0) or 0),
            tx_count_buy=int(pair.get("txns", {}).get("h24", {}).get("buys", 0) or 0),
            tx_count_sell=int(pair.get("txns", {}).get("h24", {}).get("sells", 0) or 0),
        )
    except Exception:
        return None


async def get_new_pairs(chain: str = "solana") -> list[TokenInfo]:
    # 1. get latest token profiles (new tokens)
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(TOKEN_PROFILES_API)
            if resp.status_code != 200:
                return []
            profiles = resp.json()
        except Exception:
            return []

    # 2. filter by target chain
    chain_addrs = [p["tokenAddress"] for p in profiles if p.get("chainId") == chain]
    if not chain_addrs:
        return []

    # 3. batch-fetch full pair data (max 30 per call)
    all_tokens = []
    seen = set()
    for i in range(0, len(chain_addrs), 30):
        batch = chain_addrs[i:i+30]
        url = f"{DEXSCREENER_API}/tokens/{','.join(batch)}"
        async with httpx.AsyncClient(timeout=15) as client:
            try:
                resp = await client.get(url)
                if resp.status_code == 200:
                    pairs = resp.json().get("pairs", [])
                    for p in pairs:
                        tok = parse_token(p)
                        if tok and tok.address not in seen:
                            seen.add(tok.address)
                            all_tokens.append(tok)
            except Exception:
                pass

    return all_tokens


async def search_trending(query: str) -> list[TokenInfo]:
    url = f"{DEXSCREENER_API}/search?q={query}"
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            resp = await client.get(url)
            if resp.status_code != 200:
                return []
            pairs = resp.json().get("pairs", [])
            tokens = []
            seen = set()
            for p in pairs:
                tok = parse_token(p)
                if tok and tok.address not in seen:
                    seen.add(tok.address)
                    tokens.append(tok)
            return tokens
        except Exception:
            return []
