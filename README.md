# 🤖 NexAI Store Bot — Complete Setup Guide

---

## ✅ STEP 1 — Choose Your Channel & Group Name

### 📢 Channel Name (Public, read-only, for announcements & deals)
| Option | Handle | Why it works |
|--------|--------|-------------|
| **NexAI Store** ⭐ | `@NexAIStore` | Short, premium feel, "AI" keyword built-in |
| **AI Tools Hub** | `@AIToolsHubOfficial` | High search volume keyword |
| **ProAI Deals** | `@ProAIDeals` | Targets deal-seekers searching for discounts |
| **SmartAI Shop** | `@SmartAIShop` | Easy to remember, professional |

### 👥 Support Group Name (Where clients ask questions)
| Option | Handle |
|--------|--------|
| **NexAI Store — Support** | `@NexAISupport` |
| **AI Tools Hub — Chat** | `@AIToolsChat` |

> 🏆 **Recommended combo:** Channel = `@NexAIStore` + Group = `@NexAISupport`

---

## ✅ STEP 2 — Create Your Bot with BotFather

1. Open Telegram → search **@BotFather** → tap Start
2. Send: `/newbot`
3. Enter your bot's **display name**: `NexAI Store`
4. Enter your bot's **username** (must end in "bot"): `NexAIStoreBot`
5. BotFather gives you a **TOKEN** — copy it, keep it secret!
6. Set a description: `/setdescription` → paste:
   ```
   🤖 NexAI Store — Your #1 source for premium AI subscriptions.
   Claude Pro | ChatGPT Plus | Canva | Gemini | Midjourney
   Instant delivery | 24/7 support | Lowest prices
   ```
7. Set commands: `/setcommands` → paste:
   ```
   start - Open main menu
   ```

---

## ✅ STEP 3 — Find Your Telegram User ID (Admin ID)

1. Open Telegram → search **@userinfobot**
2. Send `/start`
3. It replies with your **ID** (a number like `123456789`)
4. Copy that number — you'll need it in the bot config

---

## ✅ STEP 4 — Install Python & Dependencies

### On Windows:
```bash
# 1. Download Python from https://python.org (3.10 or newer)
# 2. Open Command Prompt (cmd)
pip install python-telegram-bot==20.7
```

### On Linux / VPS (Ubuntu):
```bash
sudo apt update && sudo apt install python3 python3-pip -y
pip3 install python-telegram-bot==20.7
```

---

## ✅ STEP 5 — Configure bot.py

Open `bot.py` and edit these lines at the top:

```python
BOT_TOKEN   = "5823456789:AAExxxx..."   # ← paste your BotFather token
CHANNEL_URL = "https://t.me/NexAIStore" # ← your channel link
ADMIN_IDS   = [123456789]               # ← your Telegram user ID
```

Also update the support username inside the code:
- Replace `@YourSupportUsername` with your actual Telegram username
- Replace `@YourBotUsername` with `@NexAIStoreBot`

---

## ✅ STEP 6 — Edit Your Product Catalog

In `bot.py`, find the `PRODUCTS` dictionary and edit freely:

```python
PRODUCTS = {
    "product_id": {
        "name":     "🎨 Product Display Name",
        "price":    5.00,      # price in USD
        "stock":    50,        # how many available
        "desc":     "Short description of what the buyer gets",
        "delivery": "How they receive it (link, credentials, etc.)"
    },
    # Add more products here...
}
```

---

## ✅ STEP 7 — Run the Bot

```bash
# Navigate to your folder
cd /path/to/your/folder

# Run it
python bot.py       # Windows
python3 bot.py      # Linux/Mac
```

You should see: `🤖 NexAI Store Bot is running...`
Send `/start` to your bot on Telegram to test it!

---

## ✅ STEP 8 — Keep It Running 24/7 (VPS Recommended)

### Option A — Free (your PC stays on):
Just leave the terminal open.

### Option B — VPS (best for business):
Get a cheap VPS ($5/month): **Hostinger**, **Hetzner**, or **Contabo**
Then run with `screen` or `systemd`:
```bash
# Install screen
sudo apt install screen -y

# Start a session
screen -S nexaibot

# Run the bot
python3 bot.py

# Detach (Ctrl+A then D) — bot keeps running in background!
```

---

## ✅ STEP 9 — Admin Commands

Once your bot is running, send these to your bot:

| Command | What it does |
|---------|-------------|
| `/addbalance 123456789 5.00` | Add $5 to a user's balance (after they pay you) |
| `/broadcast Hello everyone!` | Send a message to ALL users |
| `/orders` | See the last 10 orders |

---

## ✅ STEP 10 — Customise Payment Info

In `bot.py`, find `PAYMENT_METHODS` and update with your real wallet addresses:

```python
PAYMENT_METHODS = {
    "binance":  {"name": "💳 Binance Pay", "info": "Send to Binance ID: 123456789"},
    "usdt_bep": {"name": "🟡 USDT BEP20",  "info": "Send to: 0xYourWalletAddress"},
    "crypto":   {"name": "🤖 Crypto Bot",   "info": "Pay via @CryptoBot to: @NexAIStoreBot"},
}
```

---

## 🗺️ Bot Feature Summary

| Feature | Status |
|---------|--------|
| 🎁 Product catalog with pagination | ✅ Built |
| 💰 Balance system | ✅ Built |
| 📦 Order history | ✅ Built |
| 👥 Referral program (+$0.25/referral) | ✅ Built |
| 🎰 Daily spin (win random balance) | ✅ Built |
| 🏷️ Coupon code system | ✅ Built (extend as needed) |
| ❓ Support section | ✅ Built |
| 📢 Admin broadcast | ✅ Built |
| ➕ Admin add balance | ✅ Built |
| 📋 Admin view orders | ✅ Built |

---

## 💡 Tips to Grow Your Channel

1. **Post daily** — deals, AI tips, product comparisons
2. **Pin your bot link** in the channel description
3. **Run flash sales** — "50% off next 2 hours!" creates urgency
4. **Screenshot happy customers** (blur names) and post as proof
5. **Cross-promote** in Facebook groups, Reddit r/ChatGPT, Arabic tech groups on Telegram
6. **Referral push** — tell members they earn $0.25 per invite

---

*Need help? Ask Claude to add new features, payment gateways, or a web dashboard!*
