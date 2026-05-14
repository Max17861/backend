from django.db import models
from catalog.models import Product

class CartItem(models.Model):
    user_session = models.CharField(max_length=255) # Use this if you don't have login yet
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)