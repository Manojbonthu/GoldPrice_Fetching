import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import os
from urllib.parse import quote

# CallMeBot credentials
CALLMEBOT_PHONE = os.environ.get("CALLMEBOT_PHONE")   # e.g. 919553734629
CALLMEBOT_APIKEY = os.environ.get("CALLMEBOT_APIKEY") # e.g. 1234567

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
            raise RuntimeError("Could not locate the FAQ answer text on the page.")

    pattern = re.compile(
        r"(?:\b(\d+kt)\b|\b(\d{3})\b)\s+gold\s+price\s+per\s+"
        r"(gram|10\s+grams)\s+in\s+Andhra\s+Pradesh\s+is\s+INR\s+([\d,]+(?:\.\d+)?)",
        re.IGNORECASE
    )
    matches = pattern.findall(answer_text)
    if not matches:
        raise RuntimeError("No gold-price patterns found in the extracted text.")

    for kt_group, digit_group, unit, price_str in matches:
        purity = kt_group if kt_group else digit_group
        if purity.lower() == "22kt" and unit.lower() == "10 grams":
            return price_str

    raise RuntimeError("22kt gold price for 10 grams not found.")


def send_whatsapp(msg: str):
    encoded_msg = quote(msg)
    url = (
        f"https://api.callmebot.com/whatsapp.php"
        f"?phone={CALLMEBOT_PHONE}&text={encoded_msg}&apikey={CALLMEBOT_APIKEY}"
    )
    response = requests.get(url)
    if response.status_code == 200:
        print("✅ WhatsApp message sent!")
    else:
        print(f"❌ Failed to send: {response.text}")


def job():
    try:
        price_str = fetch_22kt_price_str()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp} | 22kt Gold (10g): INR {price_str}")

        msg = f"🪙 22kt Gold Price (10g) in AP: INR {price_str}\n🕐 {timestamp}"
        send_whatsapp(msg)

    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{timestamp} Error: {e}")
        send_whatsapp(f"⚠️ Gold price fetch failed:\n{e}")


if __name__ == "__main__":
    job()
