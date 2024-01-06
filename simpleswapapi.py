import os
from dotenv import load_dotenv
import requests

# Load the .env file
load_dotenv()

# Access the token
API_KEY = os.environ.get('SIMPLE_SWAP_API_KEY')

class SimpleSwap:
    def get_currency_list(self):
        url = f"https://api.simpleswap.io/get_all_currencies?api_key={API_KEY}"
        response = requests.get(url)
        if response.status_code == 200:
            currencies = response.json()
            return currencies
        else:
            return None
        
    def get_currency(self, symbol):
        url = f"https://api.simpleswap.io/get_currency?api_key={API_KEY}&symbol={symbol}"
        response = requests.get(url)
        if response.status_code == 200:
            currency = response.json()
            return currency
        else:
            return None
        
    def get_ranges(self, fixed, from_currency, to_currency):
        url = f"https://api.simpleswap.io/get_ranges?api_key={API_KEY}&fixed={fixed}&currency_from={from_currency['symbol']}&currency_to={to_currency['symbol']}"
        response = requests.get(url)
        if response.status_code == 200:
            ranges = response.json()
            return ranges
        else:
            return response.json()['description']
        
    def get_estimated(self, fixed, from_currency, to_currency, amount):

        print(from_currency, to_currency)

        url = f"https://api.simpleswap.io/get_estimated?api_key={API_KEY}&fixed={fixed}&currency_from={from_currency}&currency_to={to_currency}&amount={amount}"
        response = requests.get(url)
        if response.status_code == 200:
            estimated_amount = response.json()
            return estimated_amount
        else:
            return None
        
    def check_exchanges(self, fixed, from_currency, to_currency, amount):
        url = f"https://api.simpleswap.io/check_exchanges?api_key={API_KEY}&fixed={fixed}&currency_from={from_currency}&currency_to={to_currency}&amount={amount}"
        response = requests.get(url)
        if response.status_code == 200:
            available = response.json()
            return available
        else:
            return None
        
    def create_exchanges(self, data):
        print(data)
        url = f"https://api.simpleswap.io/create_exchange?api_key={API_KEY}"
        response = requests.post(url, data)
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            result = response.json()
            return result

    def get_exchange(self, exchange_id):
        print(exchange_id)
        url = f"https://api.simpleswap.io/get_exchange?api_key={API_KEY}&id={exchange_id}"
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            return None
        
    def get_currency(self, symbol):
        url = f"https://api.simpleswap.io/get_currency?api_key={API_KEY}&symbol={symbol}"
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            return None