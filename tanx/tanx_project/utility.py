from django.core.cache import cache
from .models import PriceAlert, PriceAlert
import django_rq
from django.conf import settings
from django.core.mail import send_mail


def handle_create_alert_in_cache():
	url = 'https://api.coingecko.com/api/v3/simple/price?ids=BTC&vs_currencies=usd'
	response = requests.get(url)
	print("To Do")

def process_current_price(current_price, last_price):
	last_price = float(last_price)
	if current_price > last_price:
		direction = 1
		"""alerts = PriceAlert.objects.filter(
			target_price__gt=last_price, 
			target_price__lte=current_price, 
			direction=1, 
			is_triggered=False)"""
	elif current_price < last_price:
		direction = 2
		alerts = PriceAlert.objects.filter(
			target_price__gt=current_price, 
			target_price__lte=last_price, 
			direction=2,
			is_triggered = False
			)

	alerts = PriceAlert.objects.filter(target_price__gt=67470, target_price__lte=69000, 
		#is_triggered=False
	 )
	#alerts = PriceAlert.objects.filter(target_price__gt=, target_price__lte=69000)
	for alert in alerts:
		cache.set("alert_"+str(alert.target_price), alert.target_price)
		queue = django_rq.get_queue('default', default_timeout=800)
		queue.enqueue(send_email_price_alert, args=(alert.user.email, alert.target_price, alert.direction ))
		alert.is_triggered = True
		alert.save()



	#To do
	print('Hi')

def send_email_price_alert(email, price, direction):
	subject = 'Crypto Currency Price Hit Alert !!'
	message = 'Hi User, this mail is regarding your price alert, set at ' + str(price) +"."
	email_from = settings.EMAIL_HOST_USER
	recipient_list = [email, ]
	send_mail( subject, message, email_from, recipient_list )
	cache.set("check queue.."+ email + ", price = " + str(price), price)


def update_alerts_in_cache_for_user(user):
	alerts = PriceAlert.objects.filter(
		user = user,
		is_deleted = False,
		)
	if len(alerts) > 0:
		cache_alert = []
		for alert in alerts:
			alert_dict = get_dictionary_from_alert_object(alert)
			cache_alert.append(alert_dict)

		cache.set('alert_'+str(alert.user.id), cache_alert)
		return True
	return False

def get_dictionary_from_alert_object(alert):
	response = {}
	response['user'] = alert.user.id
	response['cryptocurrency'] = alert.cryptocurrency
	response['target_price'] = float(alert.target_price)
	response['created_at'] = alert.created_at.strftime("%d/%m/%Y %H:%M:%S")
	response['is_triggered'] = alert.is_triggered
	response['direction'] = 'increasing' if alert.direction == 1 else 'decreasing'
	response['id'] = alert.id
	return response



