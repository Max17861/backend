import requests
from django.core.management.base import BaseCommand
from catalog.models import Product

class Command(BaseCommand):
    def handle(self, *args, **options):
        url = "https://fakestoreapi.com/products"
        response = requests.get(url)
        items = response.json()

        for item in items:
            Product.objects.get_or_create(
                id=item['id'],
                defaults={
                    'title': item['title'],
                    'price': item['price'],
                    'image': item['image'],
                    'category': item['category'],
                }
            )
        self.stdout.write(self.style.SUCCESS('Successfully loaded products into DB'))