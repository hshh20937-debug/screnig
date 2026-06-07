import os
import httpx
from rich.console import Console
from models.token import TokenInfo

console = Console()
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}" if BOT_TOKEN else None


async def send_alert(token: TokenInfo) -> bool:
    if not API_URL or not CHAT_ID:
        return False

    score_icon = "🟢" if token.score >= 80 else "🟡" if token.score >= 60 else "🔴"

    dex_url = f"https://dexscreener.com/{token.chain}/{token.address}"
    text = (
        f"🔥 <b>TOKEN TERDETEKSI</b> 🔥\n\n"
        f"💰 <b>{token.symbol}</b> ({token.name[:20]})\n"
        f"⛓ Chain: {token.chain}\n"
        f"🏷 Alamat:\n<code>{token.address}</code>\n\n"
        f"📊 <b>Data Filter:</b>\n"
        f"├ MCap: ${token.market_cap_usd:,.0f}\n"
        f"├ Liq: ${token.liquidity_usd:,.0f}\n"
        f"├ Usia: {token.age_hours:.1f}h\n"
        f"├ Buy/Sell: {token.buy_sell_ratio:.2f}\n"
        f"├ Holders: {token.holder_count}\n"
        f"├ Top Holder: {token.top_holder_pct:.1f}%\n"
        f"├ LP Burn: {'✅' if token.lp_burned else '❌'}\n"
        f"├ LP Lock: {'✅' if token.lp_locked else '❌'}\n"
        f"├ Mintable: {'⚠️ Ya' if token.mintable else '✅ Tidak'}\n"
        f"└ Score: {score_icon} {token.score:.0f}/100\n\n"
        f'🔗 <a href="{dex_url}">Buka di DexScreener</a>'
    )

    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.post(f"{API_URL}/sendMessage", json=payload)
            ok = resp.status_code == 200
            if not ok:
                console.print(f"[red]Telegram send failed ({resp.status_code}): {resp.text[:200]}[/]")
            return ok
        except Exception as e:
            console.print(f"[red]Telegram error: {e}[/]")
            return False
