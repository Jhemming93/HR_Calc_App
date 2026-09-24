"""Room bot: item lookup plus voluntary player trade offers."""

from highrise import BaseBot, User

from trades import ItemLookupError, OfferStore, get_item, search_items


class Bot(BaseBot):
    def __init__(self):
        super().__init__()
        self.offers = OfferStore()

    async def on_chat(self, user: User, message: str) -> None:
        if not message.strip() or message.split(maxsplit=1)[0].lower() != "!trade":
            return
        args = message.strip().split()
        command = args[1].lower() if len(args) > 1 else "help"
        try:
            if command == "help":
                reply = "!trade search NAME | !trade sell ITEM_ID PRICE | !trade find ITEM_ID [MAX_PRICE] | !trade mine | !trade remove OFFER_ID"
            elif command == "search":
                results = await search_items(" ".join(args[2:]))
                reply = "Items: " + "; ".join(f"{i.get('item_name', '?')} ({i.get('item_id', '?')})" for i in results) if results else "No matching items."
            elif command == "sell" and len(args) == 4:
                price = int(args[3])
                item = await get_item(args[2])
                if item.get("is_tradable") is not True:
                    reply = "Highrise does not mark this item as tradable. Offer not posted."
                else:
                    offer_id = self.offers.add(item, user.id, user.username, price)
                    reply = f"Offer #{offer_id}: {item['item_name']} for {price:,}g by @{user.username}. Expires in 7 days. This is a player-submitted offer, not a Marketplace listing."
            elif command == "find" and len(args) in (3, 4):
                max_price = int(args[3]) if len(args) == 4 else None
                if max_price is not None and max_price < 1:
                    raise ValueError("Maximum price must be positive.")
                item = await get_item(args[2])
                results = self.offers.find(item["item_id"], max_price)
                reply = (f"{item['item_name']} offers: " + "; ".join(
                    f"#{o['id']} {o['price']:,}g @{o['seller_name']}" for o in results)) if results else "No submitted offers match."
            elif command == "mine":
                results = self.offers.mine(user.id)
                reply = "Your offers: " + "; ".join(f"#{o['id']} {o['item_name']} {o['price']:,}g" for o in results) if results else "You have no active offers."
            elif command == "remove" and len(args) == 3:
                reply = "Offer removed." if self.offers.remove(int(args[2]), user.id) else "Offer not found or it belongs to another player."
            else:
                reply = "Try !trade help for the command list."
        except (ValueError, ItemLookupError) as exc:
            reply = str(exc) if isinstance(exc, ItemLookupError) or str(exc).startswith("Limit of 20") else "Enter a valid whole Gold amount or offer ID."
        await self.highrise.send_whisper(user.id, reply[:450])
