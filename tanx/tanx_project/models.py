from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class PriceAlert(models.Model):
    CRYPTO_CHOICES = [
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        # Add more cryptocurrency options as needed
    ]

    DIRECTION_CHOICES = [
        (1, 'Up'),
        (2, 'Down'),
    ]


    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cryptocurrency = models.CharField(max_length=5, choices=CRYPTO_CHOICES)
    target_price = models.DecimalField(max_digits=20, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_triggered = models.BooleanField(default=False)
    direction = models.IntegerField(choices=DIRECTION_CHOICES) #can use Enum also
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.cryptocurrency} Alert"


class CryptoCurrencyPrice(models.Model):
    CRYPTO_CHOICES = [
        ('BTC', 'Bitcoin'),
        ('ETH', 'Ethereum'),
        # Add more cryptocurrency options as needed
    ]

    price = models.CharField()
    #cryptocurrency = models.CharField(max_length=5, choices=CRYPTO_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering = ['-created_at']

