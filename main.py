import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from twilio.rest import Client
import os

# Twilio credentials
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = "whatsapp:+14155238886"
TWILIO_WHATSAPP_TO = "whatsapp:+919553734629"  # your number

if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
    raise ValueError("❌ Twilio credentials not set in environment variables.")

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


# ── Scraper ─────────────────────────────────────────────────────────────────

def fetch_22kt_price_str():
    url = "https://www.goldenchennai.com/finance/gold-rate-in-andhra-pradesh/"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html.parser")

    question_text = "What is the price of gold in Andhra Pradesh today?"
    question_tag = soup.find(lambda tag: tag.get_text(strip=True) == question_text)

    answer_text = None
    if question_tag:
        current = question_tag.find_next()
        while current:
            text = current.get_text(separator=" ", strip=True)
            if "gold price per" in text.lower() and "in andhra pradesh" in text.lower():
                answer_text = text
                break
            current = current.find_next()

    if not answer_text:
        full_text = soup.get_text(separator=" ", strip=True)
        fallback_match = re.search(
            r"Today,\s+the\s+[\dKTkt,\.\s]+in\s+Andhra\s+Pradesh(?:\s+is\s+INR\s+[\d,\.]+[.,]?)+",
            full_text
        )
        if fallback_match:
            answer_text = fallback_match.group(0)
        else:
            raise RuntimeError("❌ Could not locate the gold price on the page.")

    pattern = re.compile(
        r"(?:\b(\d+kt)\b|\b(\d{3})\b)\s+gold\s+price\s+per\s+"
        r"(gram|10\s+grams)\s+in\s+Andhra\s+Pradesh\s+is\s+INR\s+([\d,]+(?:\.\d+)?)",
        re.IGNORECASE
    )
    matches = pattern.findall(answer_text)
    if not matches:
        raise RuntimeError("❌ No gold price pattern found in page text.")

    for kt_group, digit_group, unit, price_str in matches:
        purity = kt_group if kt_group else digit_group
        if purity.lower() == "22kt" and unit.lower() == "10 grams":
            return price_str

    raise RuntimeError("❌ 22kt gold price for 10 grams not found.")


# ── WhatsApp Sender ──────────────────────────────────────────────────────────

def send_whatsapp(msg: str):
    try:
        message = twilio_client.messages.create(
            body=msg,
            from_=TWILIO_WHATSAPP_FROM,
            to=TWILIO_WHATSAPP_TO
        )
        print(f"✅ WhatsApp sent! SID: {message.sid}")
    except Exception as e:
        print(f"❌ Failed to send WhatsApp: {e}")


# ── Main Job ─────────────────────────────────────────────────────────────────

def job():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"🕐 Running at {timestamp}")

    try:
        price_str = fetch_22kt_price_str()
        print(f"✅ Price fetched: INR {price_str}")

        msg = (
            f"🪙 *Daily Gold Price Alert*\n"
            f"──────────────────\n"
            f"📍 Andhra Pradesh\n"
            f"💰 22kt Gold (10g): INR {price_str}\n"
            f"🕐 {timestamp}"
        )
        send_whatsapp(msg)

    except Exception as e:
        print(f"❌ Error: {e}")
        # Send error alert on WhatsApp too
        send_whatsapp(f"⚠️ Gold Price Bot Error:\n{e}\n🕐 {timestamp}")


if __name__ == "__main__":
    job()
