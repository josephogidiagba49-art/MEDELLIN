import time
import requests
import feedparser
import hashlib

# -------------------
# Telegram Settings
# -------------------
TELEGRAM_TOKEN = "8488282143:AAEmofU0H6WvQCyxDusBs8uA6AL_boL8u4w"
TELEGRAM_CHAT_ID = "7296034489"

# -------------------
# Subreddits to monitor
# -------------------
SUBREDDITS = [
    "CryptoCurrency", "Bitcoin", "ethereum", "binance", "CryptoMarkets",
    "CoinBase", "Kraken", "CoinbaseSupport", "kucoin", "Gemini",
    "Metamask", "ledgerwallet", "Trezor", "trustwallet", "cardano",
    "solana", "dogecoin", "Ripple", "polkadot", "UniSwap"
]

# -------------------
# Keywords to trigger alerts
# -------------------
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

# -------------------
# Other settings
# -------------------
CHECK_INTERVAL = 120  # seconds between checks
USER_AGENT = "reddit-rss-telegram-bot"

# -------------------
# Safety check
# -------------------
if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    raise SystemExit("Missing TELEGRAM_TOKEN or TELEGRAM_CHAT_ID")

# -------------------
# Initialize requests session
# -------------------
session = requests.Session()
session.headers.update({"User-Agent": USER_AGENT})

# Keep track of already sent posts
seen = set()

# -------------------
# Helper functions
# -------------------
def rss_url(sub):
    """Return Reddit RSS feed URL for a subreddit"""
    return f"https://www.reddit.com/r/{sub}/new/.rss"

def post_id(entry):
    """Generate unique ID for a post to avoid duplicates"""
    return hashlib.sha256((entry.get("id","") + entry.get("link","")).encode()).hexdigest()

def send(msg):
    """Send a formatted message to Telegram"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    session.post(url, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "disable_web_page_preview": False,  # show link preview
        "parse_mode": "HTML"  # allow bold/italic formatting
    })

# -------------------
# Bot started
# -------------------
print("Bot started. Monitoring:", ", ".join(SUBREDDITS))

# -------------------
# Main loop
# -------------------
while True:
    for sub in SUBREDDITS:
        try:
            feed = feedparser.parse(rss_url(sub))
            for e in feed.entries[:20]:
                pid = post_id(e)
                if pid in seen:
                    continue

                # Combine title + summary
                title = e.get("title","")
                summary = e.get("summary","")
                text = (title + " " + summary).lower()

                # Check for keywords
                for kw in KEYWORDS:
                    if kw in text:
                        snippet = summary[:300] + ("..." if len(summary) > 300 else "")
                        msg = (
                            f"🔔 <b>Keyword:</b> {kw}\n"
                            f"<b>Subreddit:</b> r/{sub}\n"
                            f"<b>Title:</b> {title}\n"
                            f"<b>Snippet:</b> {snippet}\n"
                            f"<b>Link:</b> {e.get('link','')}"
                        )
                        send(msg)
                        seen.add(pid)
                        break
        except Exception as err:
            print("Error:", err)

        time.sleep(3)

    time.sleep(CHECK_INTERVAL)
