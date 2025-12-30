import time
import requests
import feedparser
import hashlib

TELEGRAM_TOKEN = "8488282143:AAEmofU0H6WvQCyxDusBs8uA6AL_boL8u4w"
TELEGRAM_CHAT_ID = "7296034489"

# List of subreddits to monitor
SUBREDDITS = [
    "CryptoCurrency", "Bitcoin", "ethereum", "binance", "CryptoMarkets",
    "CoinBase", "Kraken", "CoinbaseSupport", "kucoin", "Gemini",
    "Metamask", "ledgerwallet", "Trezor", "trustwallet", "cardano",
    "solana", "dogecoin", "Ripple", "polkadot", "UniSwap"
]

# List of keywords to trigger alerts
KEYWORDS = [
    "problem", "issue", "error", "bug", "glitch", "crash", "frozen", "not working",
    "broken", "malfunction", "stuck", "pending", "failed", "lost", "missing",
    "disappeared", "vanished", "not showing", "delayed", "slow", "help", "support",
    "customer service", "scammed", "hacked", "stolen", "fraud", "phishing",
    "compromised", "exploited", "locked", "suspended", "banned", "verification",
    "kyc", "login", "password", "2fa", "authentication", "access denied",
    "withdrawal", "deposit", "fee", "gas fee", "transaction fee", "high fees",
    "cannot withdraw", "cannot deposit", "balance", "funds", "urgent", "emergency",
    "frustrated", "angry", "desperate", "panicking", "stressed", "worried", "anxious",
    "helpless", "wallet", "seed phrase", "private key", "network congestion",
    "smart contract", "slippage", "liquidity", "rug pull", "api", "connection error",
    "maintenance", "downtime", "outage", "server error", "trading halted", "market order",
    "limit order", "stop loss", "leverage", "margin call", "security breach", "hack",
    "vulnerability", "exploit", "drain", "unauthorized", "suspicious", "malicious",
    "attack", "compromised", "lawsuit", "legal", "regulation", "compliance", "freeze",
    "seizure", "investigation", "subpoena", "court", "attorney"
]

CHECK_INTERVAL = 120
USER_AGENT = "reddit-rss-telegram-bot"

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    raise SystemExit("Missing TELEGRAM_TOKEN or TELEGRAM_CHAT_ID")

session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})

seen = set()

def rss_url(sub):
    return f"https://www.reddit.com/r/{sub}/new/.rss"

def send(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    session.post(url, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "disable_web_page_preview": True
    })

def post_id(entry):
    return hashlib.sha256((entry.get("id","") + entry.get("link","")).encode()).hexdigest()

print("Bot started. Monitoring:", ", ".join(SUBREDDITS))

while True:
    for sub in SUBREDDITS:
        try:
            feed = feedparser.parse(rss_url(sub))
            for e in feed.entries[:20]:
                pid = post_id(e)
                if pid in seen:
                    continue

                text = (e.get("title","") + " " + e.get("summary","")).lower()

                for kw in KEYWORDS:
                    if kw in text:
                        send(f"🔔 {kw}\nr/{sub}\n{e.get('title','')}\n{e.get('link','')}")
                        seen.add(pid)
                        break
        except Exception as err:
            print("Error:", err)

        time.sleep(3)

    time.sleep(CHECK_INTERVAL)
