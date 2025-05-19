import json
import requests
import smtplib
import random
from email.message import EmailMessage
from config import EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER
import time

SEEN_FILE = "seen_flats.json"
URL = "https://mosaic-plaza-aanbodapi.zig365.nl/api/v1/actueel-aanbod?limit=60&locale=nl_NL&page=0&sort=%2Bcity.name"

def send_email(new_flats):
    msg = EmailMessage()
    msg["Subject"] = "📢 Nový byt na Plaza!"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    body = "🆕 Našli jsme nové byty:\n\n"
    for flat in new_flats:
        body += f"- {flat['street']} {flat['houseNumber']}, {flat['city']}\n"
        body += f"  Cena: €{flat['price']}, Velikost: {flat['size']} m²\n"
        body += f"  Odkaz: {flat['link']}\n\n"

    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.seznam.cz", 465) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
        smtp.send_message(msg)


def load_seen():
    try:
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

def main():
    seen = load_seen()
    response = requests.get(URL)
    data = response.json()["data"]

    new_flats = []

    for flat in data:
        flat_id = str(flat["id"])
        if flat_id not in seen:
            address = f'{flat["street"]} {flat["houseNumber"]}, {flat["city"]["name"]}'
            price = flat["totalRent"]
            size = flat["areaDwelling"]
            link = f'https://plaza.newnewnew.space/aanbod/huurwoningen/details/{flat["urlKey"]}'
            new_flats.append({
                "address": address,
                "price": price,
                "size": size,
                "link": link,
                "street": flat.get("street"),
                "houseNumber": flat.get("houseNumber"),
                "city": flat.get("city", {}).get("name"),
                "urlKey": flat.get("urlKey")
            })
            seen.add(flat_id)

    if new_flats:
        print("🆕 Nové byty nalezeny:")
        for f in new_flats:
            print(f"- {f.get('street')} {f.get('houseNumber')}")

        send_email(new_flats)
    else:
        print("✅ Žádné nové byty.")

    save_seen(seen)

def loop():
    while True:
        try:
            main()
        except Exception as e:
            print(f"⚠️ Chyba při provádění: {e}")
        delay = random.randint(8, 15)
        time.sleep(delay)

if __name__ == "__main__":
    loop()
