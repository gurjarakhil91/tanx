import requests
from datetime import datetime
from django.core.cache import cache
from tanx_project.models import CryptoCurrencyPrice
from tanx_project.utility import process_current_price



def fetch_crypto_currency_price():
	url = 'https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd'
	symbol = "bitcoin"

	#url = f'https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd'
	response = requests.get(url)
	time_now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

	if response.status_code == 200:
		data = response.json()
		# Extract the current price from the response
		current_price = data.get('bitcoin', {}).get('usd')
		last_price_obj = CryptoCurrencyPrice.objects.last()
		CryptoCurrencyPrice.objects.create(price=str(current_price))
		cache.set("cp_" + str(current_price), current_price)
		cache.set("time. : =>" + time_now, time_now)
		process_current_price(current_price, last_price_obj.price)


	print("Hi")