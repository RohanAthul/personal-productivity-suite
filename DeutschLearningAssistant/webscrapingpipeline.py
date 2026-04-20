# A "Flex" Scraper Example for Yahoo Finance
import random
from box import Box # Simple dot-notation for dictionaries
import requests
from bs4 import BeautifulSoup

def get_live_price(symbol):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...'
    }
    url = f"https://finance.yahoo.com/quote/{symbol}"
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Locate the price element (class names change, so use data-attributes if possible)
    price = soup.find('fin-streamer', {'data-field': 'regularMarketPrice'}).text
    return float(price.replace(',', ''))

# This is your "IoT Sensor" Loop
symbols = ['AAPL', 'TSLA', 'GOOGL', 'BTC-USD']
while True:
    ticker = random.choice(symbols)
    price = get_live_price(ticker)
    # Now send this 'price' to your Redpanda 'iot_topic'!
    print(f"📡 Sensor {ticker} reading: ${price}")
    time.sleep(random.uniform(2, 5))
    