# Gold Lab trade offer bot

This bot queries Highrise's **public item catalog** to verify item names and `is_tradable`, then searches **offers submitted by players in its room**. It cannot discover active Marketplace listings, verify ownership, execute trades, or verify that a submitted offer is still available. Highrise's documented public Web API has no active Marketplace listing endpoint. Do not describe these offers as live Marketplace prices.

## Commands in the bot's room

| Command | Action |
| --- | --- |
| `!trade search moon` | Find a catalog item and its ID. |
| `!trade sell ITEM_ID 1200` | Post your offer at 1200g for 7 days. |
| `!trade find ITEM_ID 1500` | Find up to five submitted offers at or below 1500g. Omit the ceiling to see the cheapest. |
| `!trade mine` | Show your five most recent active offers. |
| `!trade remove 12` | Remove your own offer #12. |

Replies are whispered to the command sender. The bot stores a seller's Highrise ID and username with each offer; it never takes custody of items or Gold. Users arrange any trade themselves and should confirm price and tradeability in Highrise.

## Run locally (Python 3.11)

1. Give your bot **designer rights** in the room. Use **Share this Room** to find its Room ID.
2. From this `bot` folder, run `python -m venv .venv`, activate the environment, then `pip install -r requirements.txt`.
3. Set `HIGHRISE_ROOM_ID` and `HIGHRISE_BOT_TOKEN` in your local terminal or hosting provider's secret environment variables. **Never put the token in code or a GitHub commit.**
4. Run `highrise market_bot:Bot "$HIGHRISE_ROOM_ID" "$HIGHRISE_BOT_TOKEN"` in a Unix shell, or `highrise market_bot:Bot $env:HIGHRISE_ROOM_ID $env:HIGHRISE_BOT_TOKEN` in PowerShell.

The current SDK pins an older Pendulum dependency that fails to build under Python 3.12 in our verification environment. Use Python 3.11 for this version of the bot.

The bot must stay running to respond to commands. SQLite saves offers to `data/offers.sqlite3` by default. Use `GOLD_LAB_DB` to choose a persistent disk path if hosting it elsewhere. Offers on one host are not yet synced to the Gold Lab website; the site is static and would need a hosted API/database for shared listings. For multiple bot instances, migrate this store to a hosted database before scaling.

The public catalog requests need no Web API key. Your existing bot token is only for connecting the room bot. Highrise rate limits the Web API; the bot returns a temporary lookup error if it is unavailable.
