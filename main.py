import asyncio
import os
import sys
from datetime import datetime
from rich.console import Console
from rich.table import Table
from config import SCREENING_CFG
from scanners.dex_screener import get_new_pairs
from scanners.rug_check import check_token
from scanners.birdeye import get_holder_count
from filters.liquidity import passes_liquidity, passes_market_cap, passes_age, passes_holder_count
from filters.anti_rug import passes_anti_rug
from filters.momentum import passes_momentum
from models.token import TokenInfo
from notifiers.telegram import send_alert

if sys.stdout.encoding and sys.stdout.encoding.upper() not in ("UTF-8", "UTF8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

console = Console()
seen_tokens: set[str] = set()


def build_table(tokens: list[TokenInfo]) -> Table:
    table = Table(title=f"Meme Coin Screener — {datetime.utcnow().strftime('%H:%M:%S UTC')}")
    table.add_column("Token", style="cyan")
    table.add_column("Chain", style="blue")
    table.add_column("Liq $", justify="right")
    table.add_column("MCap $", justify="right")
    table.add_column("Age", justify="right")
    table.add_column("Buy/Sell", justify="right")
    table.add_column("Holders", justify="right")
    table.add_column("Score", justify="right")
    table.add_column("Status", style="green")

    for t in tokens:
        score_color = "green" if t.score >= 80 else "yellow" if t.score >= 60 else "red"
        table.add_row(
            f"{t.symbol} ({t.name[:12]})",
            t.chain,
            f"${t.liquidity_usd:.0f}",
            f"${t.market_cap_usd:.0f}",
            f"{t.age_hours:.1f}h" if t.age_hours else "?",
            f"{t.buy_sell_ratio:.1f}",
            str(t.holder_count),
            f"[{score_color}]{t.score:.0f}[/]",
            ", ".join(t.tags) if t.tags else "—",
        )
    return table


def calculate_score(token: TokenInfo) -> float:
    score = 50.0

    if token.lp_burned:
        score += 10
    if token.lp_locked:
        score += 10
    if token.top_holder_pct < 10:
        score += 5
    if token.creator_pct < 5:
        score += 5
    if not token.mintable:
        score += 5
    if token.buy_sell_ratio > 2:
        score += 10
    if token.holder_growth_1h_pct > 50:
        score += 10
    if token.smart_wallet_count >= 1:
        score += 15
    if token.smart_wallet_count >= 3:
        score += 10
    if 5000 <= token.liquidity_usd <= 20000:
        score += 5
    if token.market_cap_usd > 50000:
        score += 5

    return min(score, 100)


def apply_all_filters(token: TokenInfo) -> tuple[bool, list[str]]:
    tags = []
    for name, fn in [
        ("liq", passes_liquidity),
        ("mcap", passes_market_cap),
        ("age", passes_age),
        ("holders", passes_holder_count),
    ]:
        ok, msg = fn(token)
        if not ok:
            return False, tags

    for name, fn in [("anti-rug", passes_anti_rug), ("momentum", passes_momentum)]:
        ok, msg = fn(token)
        if not ok:
            return False, tags

    tags.append("✅ PASS BASIC")
    return True, tags


async def process_token(pair: TokenInfo) -> TokenInfo | None:
    if pair.address in seen_tokens:
        return None
    seen_tokens.add(pair.address)

    holder_count = await get_holder_count(pair.address, pair.chain)
    if holder_count:
        pair.holder_count = holder_count

    rug = await check_token(pair.address, pair.chain)
    if rug:
        pair.lp_burned = rug.get("lp_burned", False)
        pair.lp_locked = rug.get("lp_locked", False)
        pair.mintable = rug.get("mintable", False)
        pair.top_holder_pct = rug.get("top_holder_pct", 0.0)
        pair.creator_pct = rug.get("creator_pct", 0.0)

    ok, tags = apply_all_filters(pair)
    if ok:
        pair.score = calculate_score(pair)
        pair.tags = tags

        console.print(f"[bold green]🔥 FLAGGED[/] {pair.symbol} @ {pair.chain}")
        console.print(f"   Liq=${pair.liquidity_usd:.0f} MCap=${pair.market_cap_usd:.0f} "
                      f"Buy/Sell={pair.buy_sell_ratio:.1f} Score={pair.score:.0f}")

        await send_alert(pair)
        return pair

    return None


async def health_server():
    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get("HOST", "0.0.0.0")

    async def handler(reader, writer):
        response = b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nOK"
        writer.write(response)
        await writer.drain()
        writer.close()

    server = await asyncio.start_server(handler, host, port)
    console.print(f"[dim]Health server running on {host}:{port}[/]")
    async with server:
        await server.serve_forever()


async def screening_loop():
    console.print("[bold yellow]🚀 Meme Coin Screener Started[/]")
    console.print(f"   Chains: {', '.join(SCREENING_CFG.chains)}")
    console.print(f"   Liq: ${SCREENING_CFG.liquidity_min:,}-${SCREENING_CFG.liquidity_max:,}")
    console.print(f"   MCap ≥ ${SCREENING_CFG.market_cap_min:,}")
    console.print(f"   Max Age: {SCREENING_CFG.max_age_hours}h")
    console.print(f"   Holders: {SCREENING_CFG.min_holders}+\n")

    has_telegram = bool(os.environ.get("TELEGRAM_BOT_TOKEN"))
    console.print(f"[dim]Telegram: {'✅ configured' if has_telegram else '❌ not set'}[/]\n")

    flagged_tokens: list[TokenInfo] = []
    cycle = 0

    while True:
        try:
            cycle += 1
            now = datetime.utcnow().strftime("%H:%M:%S")
            total_pairs = 0

            for chain in SCREENING_CFG.chains:
                pairs = await get_new_pairs(chain)
                total_pairs += len(pairs)
                tasks = [process_token(p) for p in pairs]
                results = await asyncio.gather(*tasks)
                for r in results:
                    if r:
                        flagged_tokens.append(r)

            console.print(f"[dim][{now}] Cycle #{cycle} — {total_pairs} new pairs checked | "
                          f"Flagged: {len(flagged_tokens)}[/]")

            if flagged_tokens:
                console.print(build_table(flagged_tokens[-20:]))

            await asyncio.sleep(SCREENING_CFG.poll_interval_seconds)

        except KeyboardInterrupt:
            console.print("\n[red]Stopped.[/]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/]")
            await asyncio.sleep(10)


async def main():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(health_server())
        tg.create_task(screening_loop())


if __name__ == "__main__":
    asyncio.run(main())
