# 🪙 Daily 22kt Gold Price WhatsApp Notifier (Andhra Pradesh)

This Python script fetches the **daily 22kt gold price (per 10 grams)** from the GoldenChennai website and sends it to your **WhatsApp** using **Twilio's WhatsApp API**.

---

## 📌 Features

- Automatically fetches the latest **22kt gold rate in Andhra Pradesh**
- Sends the update via **WhatsApp daily at a scheduled time**
- Uses **BeautifulSoup** for scraping and **Twilio API** for messaging
- Logs output to the console with timestamps

---

## 🔧 Requirements

- Python 3.6+
- Twilio account (with WhatsApp sandbox configured)
- A verified WhatsApp number in Twilio

---

## 📦 Installation

1. **Clone the repository or download the script**

2. **Install dependencies**
   ```bash
   pip install requests beautifulsoup4 schedule twilio



# Configure your Twilio credentials in the script  
TWILIO_ACCOUNT_SID = "Your_Twilio_Account_SID"
TWILIO_AUTH_TOKEN = "Your_Twilio_Auth_Token"
TWILIO_WHATSAPP_FROM = "whatsapp:+14155238886"  # Twilio sandbox number
TWILIO_WHATSAPP_TO = "whatsapp:+91XXXXXXXXXX"   # Your verified number

