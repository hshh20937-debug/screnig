import os
import httpx
from models.token import TokenInfo

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}" if BOT_TOKEN else None


def _escape(text: str) -> str:
    return text.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("`", "\\`")


async def send_alert(token: TokenInfo) -> bool:
    if not API_URL or not CHAT_ID:
        return False

    score_icon = "🟢" if token.score >= 80 else "🟡" if token.score >= 60 else "🔴"

    text = (
        f"🔥 *TOKEN TERDETEKSI* 🔥\n\n"
        f"💰 *{_escape(token.symbol)}* ({_escape(token.name[:20])})\n"
        f"⛓ Chain: `{token.chain}`\n"
        f"🏷 Alamat:\n`{token.address}`\n\n"
        f"📊 *Data Filter:*\n"
        f"├ MCap: `${token.market_cap_usd:,.0f}`\n"
        f"├ Liq: `${token.liquidity_usd:,.0f}`\n"
        f"├ Usia: `{token.age_hours:.1f}h`\n"
        f"├ Buy/Sell: `{token.buy_sell_ratio:.2f}`\n"
        f"├ Holders: `{token.holder_count}`\n"
        f"├ Top Holder: `{token.top_holder_pct:.1f}%`\n"
        f"├ LP Burn: `{'✅' if token.lp_burned else '❌'}`\n"
        f"├ LP Lock: `{'✅' if token.lp_locked else '❌'}`\n"
        f"├ Mintable: `{'⚠️ Ya' if token.mintable else '✅ Tidak'}`\n"
        f"└ Score: {score_icon} `{token.score:.0f}/100`\n\n"
        f"🔗 [DexScreener](https://dexscreener.com/{token.chain}/{token.address})"
    )

    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": False,
    }

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.post(f"{API_URL}/sendMessage", json=payload)
            return resp.status_code == 200
        except Exception:
            return False
