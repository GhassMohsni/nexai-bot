"""
╔══════════════════════════════════════════════════════╗
║         NexAI Store — Telegram Shop Bot              ║
║  Products: Claude Pro, ChatGPT, Canva, Gemini...     ║
╚══════════════════════════════════════════════════════╝

STEP-BY-STEP SETUP GUIDE:
─────────────────────────
1. Install Python 3.10+ on your machine or VPS
2. Install the library:  pip install python-telegram-bot==20.7
3. Create your bot via @BotFather on Telegram:
      /newbot  →  give it a name  →  get the TOKEN
4. Replace BOT_TOKEN below with your real token
5. Set your own Telegram user ID in ADMIN_IDS
      (send /start to @userinfobot to get your ID)
6. Customize PRODUCTS dict with your real catalog
7. Run:  python bot.py

FILES CREATED ON FIRST RUN:
   users.json    — stores balances, orders, referrals
   orders.json   — order history
"""

import json, os, random, asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)

# ─── CONFIGURATION ────────────────────────────────────────────────────────────
BOT_TOKEN   = "8286074552:AAHAlhDxNOvBhRHHDYydd2knEU-4NOLLZ-E"          # 👈 Replace with your token
CHANNEL_URL = "https://t.me/NexAIStore"      # 👈 Your channel link
ADMIN_IDS   = [7095427784]                    # 👈 Your Telegram user ID(s)

# ─── PRODUCT CATALOG ──────────────────────────────────────────────────────────
# Format: "product_id": { name, price, stock, description, delivery }
PRODUCTS = {
    "canva_edu_1y":   {"name": "🎨 Canva Edu — 1 Year",           "price": 1.00,  "stock": 206, "desc": "Full Canva Pro features via Education plan. Works on your own account.", "delivery": "Link sent instantly"},
    "gemini_18m":     {"name": "♊ Gemini Pro — 18 Months (Links)","price": 1.10,  "stock": 300, "desc": "Google Gemini Advanced access for 18 months via invite link.", "delivery": "Link sent instantly"},
    "nordvpn_3m":     {"name": "🔒 NordVPN — 3 Months",           "price": 3.00,  "stock": 7,   "desc": "NordVPN premium account, 3 months access.", "delivery": "Account credentials sent"},
    "notion_3m":      {"name": "📓 Notion Business — 3 Months",   "price": 2.75,  "stock": 5,   "desc": "Notion Business plan invite link, 3 months.", "delivery": "Link sent instantly"},
    "chatgpt_1m":     {"name": "🤖 ChatGPT Plus — 1 Month",       "price": 5.00,  "stock": 50,  "desc": "ChatGPT Plus shared account with GPT-4o access.", "delivery": "Credentials in 15 min"},
    "claude_pro_1m":  {"name": "🧠 Claude Pro — 1 Month",         "price": 4.50,  "stock": 30,  "desc": "Claude Pro shared account, full access to Claude 3.5 Sonnet.", "delivery": "Credentials in 15 min"},
    "midjourney_1m":  {"name": "🎭 Midjourney — 1 Month",         "price": 6.00,  "stock": 20,  "desc": "Midjourney Basic plan, access via our shared Discord server.", "delivery": "Discord invite sent"},
    "perplexity_1y":  {"name": "🔍 Perplexity Pro — 1 Year",      "price": 8.00,  "stock": 0,   "desc": "Perplexity AI Pro annual subscription.", "delivery": "Link sent instantly"},
}

ITEMS_PER_PAGE = 5

# ─── PAYMENT METHODS ──────────────────────────────────────────────────────────
PAYMENT_METHODS = {
    "binance":  {"name": "💳 Binance Pay",       "info": "Send to Binance ID: **YOUR_BINANCE_ID**\nMin deposit: $1"},
    "usdt_bep": {"name": "🟡 USDT BEP20",        "info": "Send USDT (BEP20) to:\n`YOUR_WALLET_ADDRESS`\nMin deposit: $1"},
    "crypto":   {"name": "🤖 Crypto Bot",         "info": "Pay via @CryptoBot on Telegram.\nSend to: @YourUsername"},
}

# ─── DATA STORAGE (JSON-based, easy to upgrade to DB later) ───────────────────
USERS_FILE  = "users.json"
ORDERS_FILE = "orders.json"

def load_json(path):
    if os.path.exists(path):
        with open(path) as f: return json.load(f)
    return {}

def save_json(path, data):
    with open(path, "w") as f: json.dump(data, f, indent=2)

def get_user(uid):
    users = load_json(USERS_FILE)
    uid = str(uid)
    if uid not in users:
        users[uid] = {"balance": 0.0, "orders": [], "referrals": 0, "referred_by": None, "spin_date": None}
        save_json(USERS_FILE, users)
    return users[uid]

def save_user(uid, data):
    users = load_json(USERS_FILE)
    users[str(uid)] = data
    save_json(USERS_FILE, users)

def log_order(uid, product_id, price):
    orders = load_json(ORDERS_FILE)
    order_id = f"ORD{random.randint(10000,99999)}"
    orders[order_id] = {
        "user": str(uid), "product": product_id,
        "price": price, "status": "Pending",
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    save_json(ORDERS_FILE, orders)
    return order_id

# ─── KEYBOARDS ────────────────────────────────────────────────────────────────
def main_menu_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎁 Products",   callback_data="products_0"),
         InlineKeyboardButton("💰 Balance",    callback_data="balance")],
        [InlineKeyboardButton("📦 My Orders",  callback_data="my_orders"),
         InlineKeyboardButton("🏷️ Coupon",     callback_data="coupon")],
        [InlineKeyboardButton("👥 Referral",   callback_data="referral"),
         InlineKeyboardButton("🎰 Daily Spin", callback_data="daily_spin")],
        [InlineKeyboardButton("❓ Support",    callback_data="support"),
         InlineKeyboardButton("⚙️ Settings",   callback_data="settings")],
    ])

def products_kb(page=0):
    product_list = list(PRODUCTS.items())
    start = page * ITEMS_PER_PAGE
    end   = start + ITEMS_PER_PAGE
    chunk = product_list[start:end]
    rows  = []
    for pid, p in chunk:
        stock_icon = "✅" if p["stock"] > 0 else "❌"
        label = f"{p['name']} • ${p['price']:.2f} {stock_icon}"
        rows.append([InlineKeyboardButton(label, callback_data=f"product_{pid}")])
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"products_{page-1}"))
    if end < len(product_list):
        nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"products_{page+1}"))
    if nav: rows.append(nav)
    rows.append([
        InlineKeyboardButton("🔄 Refresh", callback_data=f"products_{page}"),
        InlineKeyboardButton("🏠 Home",    callback_data="home")
    ])
    return InlineKeyboardMarkup(rows)

def product_detail_kb(pid, page):
    p = PRODUCTS[pid]
    rows = []
    if p["stock"] > 0:
        rows.append([InlineKeyboardButton("🛒 Buy Now", callback_data=f"buy_{pid}")])
    rows.append([InlineKeyboardButton("⬅️ Back", callback_data=f"products_{page}"),
                 InlineKeyboardButton("🏠 Home", callback_data="home")])
    return InlineKeyboardMarkup(rows)

def balance_kb():
    rows = [[InlineKeyboardButton(v["name"], callback_data=f"topup_{k}")] for k, v in PAYMENT_METHODS.items()]
    rows.append([InlineKeyboardButton("🏠 Home", callback_data="home")])
    return InlineKeyboardMarkup(rows)

def back_home_kb(back=None):
    row = []
    if back: row.append(InlineKeyboardButton("⬅️ Back", callback_data=back))
    row.append(InlineKeyboardButton("🏠 Home", callback_data="home"))
    return InlineKeyboardMarkup([row])

# ─── HANDLERS ─────────────────────────────────────────────────────────────────
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid  = update.effective_user.id
    name = update.effective_user.first_name or "Friend"
    user = get_user(uid)

    # Handle referral link: /start ref_USERID
    args = ctx.args
    if args and args[0].startswith("ref_") and user["referred_by"] is None:
        ref_id = args[0][4:]
        if ref_id != str(uid):
            user["referred_by"] = ref_id
            save_user(uid, user)
            ref_user = get_user(ref_id)
            ref_user["referrals"] += 1
            ref_user["balance"]   += 0.25   # reward referrer $0.25
            save_user(ref_id, ref_user)

    text = (
        f"👋 Welcome to *NexAI Store*, {name}!\n\n"
        f"🤖 Your one-stop shop for premium AI tools at the best prices.\n"
        f"💎 Claude Pro · ChatGPT Plus · Canva · Gemini · and more!\n\n"
        f"Your balance: *${user['balance']:.2f}*\n"
        f"Your ID: `{uid}`\n\n"
        f"Choose an option below 👇"
    )
    kb = main_menu_kb()
    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=kb)
    else:
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=kb)

async def button_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q   = update.callback_query
    uid = q.from_user.id
    await q.answer()
    data = q.data

    # ── HOME ──────────────────────────────────────────────────────────────────
    if data == "home":
        await start(update, ctx)

    # ── PRODUCTS LIST ─────────────────────────────────────────────────────────
    elif data.startswith("products_"):
        page = int(data.split("_")[1])
        total = len(PRODUCTS)
        pages = (total + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
        await q.edit_message_text(
            f"🎁 *Products* ({min(ITEMS_PER_PAGE, total - page*ITEMS_PER_PAGE)} shown / {total} total)\n"
            f"Page {page+1}/{pages}\n\n"
            f"Tap a product to see details & buy:",
            parse_mode="Markdown",
            reply_markup=products_kb(page)
        )

    # ── PRODUCT DETAIL ────────────────────────────────────────────────────────
    elif data.startswith("product_"):
        pid  = data[8:]
        p    = PRODUCTS[pid]
        page = 0
        stock_text = f"✅ {p['stock']} left" if p["stock"] > 0 else "❌ Out of Stock"
        text = (
            f"*{p['name']}*\n\n"
            f"💰 Price: *${p['price']:.2f}*\n"
            f"📦 Stock: {stock_text}\n"
            f"📋 {p['desc']}\n"
            f"📬 Delivery: _{p['delivery']}_"
        )
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=product_detail_kb(pid, page))

    # ── BUY ───────────────────────────────────────────────────────────────────
    elif data.startswith("buy_"):
        pid  = data[4:]
        p    = PRODUCTS[pid]
        user = get_user(uid)
        if p["stock"] <= 0:
            await q.edit_message_text("❌ This product is out of stock.", reply_markup=back_home_kb())
        elif user["balance"] < p["price"]:
            needed = p["price"] - user["balance"]
            await q.edit_message_text(
                f"💸 *Insufficient balance!*\n\n"
                f"Product: {p['name']}\n"
                f"Price: ${p['price']:.2f}\n"
                f"Your balance: ${user['balance']:.2f}\n"
                f"You need: *${needed:.2f}* more\n\n"
                f"Top up your balance to continue:",
                parse_mode="Markdown",
                reply_markup=balance_kb()
            )
        else:
            # Deduct balance and process order
            user["balance"] -= p["price"]
            order_id = log_order(uid, pid, p["price"])
            user["orders"].append(order_id)
            save_user(uid, user)
            PRODUCTS[pid]["stock"] -= 1
            await q.edit_message_text(
                f"✅ *Order Placed Successfully!*\n\n"
                f"🆔 Order ID: `{order_id}`\n"
                f"📦 Product: {p['name']}\n"
                f"💰 Paid: ${p['price']:.2f}\n"
                f"💳 Remaining balance: ${user['balance']:.2f}\n\n"
                f"📬 Delivery: _{p['delivery']}_\n\n"
                f"⏳ You'll receive your product shortly. Contact support if needed.",
                parse_mode="Markdown",
                reply_markup=back_home_kb()
            )
            # Notify admin
            for admin_id in ADMIN_IDS:
                try:
                    await ctx.bot.send_message(
                        admin_id,
                        f"🛒 *New Order!*\n"
                        f"User: `{uid}` | Product: {p['name']}\n"
                        f"Order ID: `{order_id}` | Amount: ${p['price']:.2f}",
                        parse_mode="Markdown"
                    )
                except: pass

    # ── BALANCE ───────────────────────────────────────────────────────────────
    elif data == "balance":
        user = get_user(uid)
        await q.edit_message_text(
            f"💰 *Your Balance: ${user['balance']:.2f}*\n"
            f"🆔 Your User ID: `{uid}`\n\n"
            f"Choose a payment method to top up:",
            parse_mode="Markdown",
            reply_markup=balance_kb()
        )

    elif data.startswith("topup_"):
        method_key = data[6:]
        method = PAYMENT_METHODS[method_key]
        await q.edit_message_text(
            f"{method['name']}\n\n"
            f"{method['info']}\n\n"
            f"After sending, forward your payment proof to @YourSupportUsername\n"
            f"Your balance will be updated within 30 minutes.",
            parse_mode="Markdown",
            reply_markup=back_home_kb("balance")
        )

    # ── MY ORDERS ─────────────────────────────────────────────────────────────
    elif data == "my_orders":
        user   = get_user(uid)
        orders = load_json(ORDERS_FILE)
        my     = [orders[oid] for oid in user["orders"] if oid in orders]
        if not my:
            text = "📦 *My Orders*\n\nYou haven't placed any orders yet."
        else:
            lines = [f"📦 *My Orders* ({len(my)} total)\n"]
            for oid in user["orders"][-5:]:   # show last 5
                if oid in orders:
                    o = orders[oid]
                    status_icon = "✅" if o["status"] == "Completed" else "⏳"
                    lines.append(f"{status_icon} `{oid}` — {PRODUCTS.get(o['product'], {}).get('name', o['product'])}\n"
                                 f"   ${o['price']:.2f} • {o['date']} • {o['status']}")
            text = "\n".join(lines)
        await q.edit_message_text(text, parse_mode="Markdown", reply_markup=back_home_kb())

    # ── REFERRAL ──────────────────────────────────────────────────────────────
    elif data == "referral":
        user    = get_user(uid)
        ref_url = f"https://t.me/YourBotUsername?start=ref_{uid}"
        await q.edit_message_text(
            f"👥 *Referral Program*\n\n"
            f"💵 Earn *$0.25* for every friend you invite!\n"
            f"👤 Total referrals: *{user['referrals']}*\n"
            f"💰 Earnings from referrals: *${user['referrals'] * 0.25:.2f}*\n\n"
            f"🔗 Your referral link:\n`{ref_url}`\n\n"
            f"Share this link — when your friend signs up and makes a purchase, you earn automatically!",
            parse_mode="Markdown",
            reply_markup=back_home_kb()
        )

    # ── COUPON ────────────────────────────────────────────────────────────────
    elif data == "coupon":
        await q.edit_message_text(
            "🏷️ *Coupon Code*\n\n"
            "Enter your coupon code below.\n"
            "Type it and send as a message.\n\n"
            "_(Example: NEXAI10 for 10% off)_",
            parse_mode="Markdown",
            reply_markup=back_home_kb()
        )

    # ── DAILY SPIN ────────────────────────────────────────────────────────────
    elif data == "daily_spin":
        user  = get_user(uid)
        today = datetime.now().strftime("%Y-%m-%d")
        if user["spin_date"] == today:
            await q.edit_message_text(
                "🎰 *Daily Spin*\n\n⏳ You've already spun today!\nCome back tomorrow for another chance.",
                parse_mode="Markdown", reply_markup=back_home_kb()
            )
        else:
            prizes = [0.05, 0.10, 0.25, 0.50, 0.00, 0.00, 0.15, 0.00]
            prize  = random.choice(prizes)
            user["balance"]  += prize
            user["spin_date"] = today
            save_user(uid, user)
            result = f"🎉 You won *${prize:.2f}*! Added to your balance." if prize > 0 else "😔 Better luck tomorrow! No prize this time."
            await q.edit_message_text(
                f"🎰 *Daily Spin Result*\n\n{result}\n\n💰 New balance: *${user['balance']:.2f}*",
                parse_mode="Markdown", reply_markup=back_home_kb()
            )

    # ── SUPPORT ───────────────────────────────────────────────────────────────
    elif data == "support":
        await q.edit_message_text(
            "❓ *Support*\n\n"
            "Need help? Contact us:\n\n"
            "👤 Admin: @YourSupportUsername\n"
            "📢 Channel: @NexAIStore\n"
            "⏱️ Response time: under 1 hour\n\n"
            "Common issues:\n"
            "• Order not received → send Order ID to admin\n"
            "• Balance not updated → send payment proof\n"
            "• Account not working → we replace for free",
            parse_mode="Markdown",
            reply_markup=back_home_kb()
        )

    # ── SETTINGS ──────────────────────────────────────────────────────────────
    elif data == "settings":
        await q.edit_message_text(
            f"⚙️ *Settings*\n\n"
            f"🆔 Your ID: `{uid}`\n"
            f"🌐 Language: English 🇬🇧\n"
            f"🔔 Notifications: On\n\n"
            f"To change language or settings, contact @YourSupportUsername",
            parse_mode="Markdown",
            reply_markup=back_home_kb()
        )

# ── ADMIN COMMANDS ────────────────────────────────────────────────────────────
async def admin_add_balance(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Admin: /addbalance USER_ID AMOUNT"""
    if update.effective_user.id not in ADMIN_IDS:
        return
    try:
        target_uid, amount = ctx.args[0], float(ctx.args[1])
        user = get_user(target_uid)
        user["balance"] += amount
        save_user(target_uid, user)
        await update.message.reply_text(f"✅ Added ${amount:.2f} to user {target_uid}. New balance: ${user['balance']:.2f}")
    except:
        await update.message.reply_text("Usage: /addbalance USER_ID AMOUNT")

async def admin_broadcast(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Admin: /broadcast MESSAGE — sends to all users"""
    if update.effective_user.id not in ADMIN_IDS:
        return
    msg = " ".join(ctx.args)
    if not msg:
        await update.message.reply_text("Usage: /broadcast Your message here")
        return
    users = load_json(USERS_FILE)
    sent = 0
    for uid in users:
        try:
            await ctx.bot.send_message(uid, f"📢 *Announcement:*\n\n{msg}", parse_mode="Markdown")
            sent += 1
        except: pass
    await update.message.reply_text(f"✅ Broadcast sent to {sent} users.")

async def admin_orders(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Admin: /orders — show recent orders"""
    if update.effective_user.id not in ADMIN_IDS:
        return
    orders = load_json(ORDERS_FILE)
    if not orders:
        await update.message.reply_text("No orders yet.")
        return
    lines = ["📦 *Recent Orders:*\n"]
    for oid, o in list(orders.items())[-10:]:
        lines.append(f"`{oid}` | User:{o['user']} | {o['product']} | ${o['price']} | {o['status']}")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",        start))
    app.add_handler(CommandHandler("addbalance",   admin_add_balance))
    app.add_handler(CommandHandler("broadcast",    admin_broadcast))
    app.add_handler(CommandHandler("orders",       admin_orders))
    app.add_handler(CallbackQueryHandler(button_handler))
    print("🤖 NexAI Store Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
