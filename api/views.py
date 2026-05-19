from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ProductSerializer
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from .models import Product, Cart, CartItem
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authentication import TokenAuthentication
import requests


class ProductList(APIView):
    def get(self, request):
        # 1. Check if our database is completely empty
        if not Product.objects.exists():
            try:
                print("Database is empty. Seeding products directly from FakeStoreAPI...")
                response = requests.get("https://fakestoreapi.com/products/", timeout=10)

                if response.status_code == 200:
                    external_products = response.json()

                    for item in external_products:
                        category_raw = item.get('category')
                        category_formatted = category_raw.upper() if category_raw else "UNKNOWN"

                        # Safe string string parsing for Decimal field conversion
                        raw_price = item.get('price')
                        str_price = str(raw_price) if raw_price is not None else "0.00"

                        Product.objects.get_or_create(
                            id=item.get('id'),
                            defaults={
                                'title': item.get('title', '')[:250],
                                'price': str_price,
                                'category': category_formatted[:100],
                                'image': item.get('image', '')
                            }
                        )
                    print(f"Successfully seeded database with {Product.objects.count()} items.")
                else:
                    print(f"API Error: Status code {response.status_code}")

            except Exception as e:
                print(f"!!! SEEDING CRASHED DUE TO: {e} !!!")

        # 2. Return data from database to our React frontend
        category_name = request.query_params.get('category', None)
        if category_name:
            products = Product.objects.filter(category__iexact=category_name)
        else:
            products = Product.objects.all()

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response({'error': 'Provide both fields'}, status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username taken'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password)
        Cart.objects.create(user=user)  # Automatically give them a DB cart
        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'username': user.username}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            Cart.objects.get_or_create(user=user)
            return Response({'token': token.key, 'username': user.username}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()  # Revoke token validation
        return Response({'message': 'Logged out'}, status=status.HTTP_200_OK)



class CartView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_cart_data(self, cart):
        return [
            {
                'cart_item_id': item.id,
                'id': item.product.id,
                'title': item.product.title,
                'price': float(item.product.price),
                'image': item.product.image,
                'quantity': item.quantity
            } for item in cart.items.all()
        ]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return Response(self.get_cart_data(cart))

    def post(self, request):
        product_id = request.data.get('product_id') or request.data.get('id')

        if not product_id:
            return Response({'error': 'Product ID payload missing'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return Response(self.get_cart_data(cart))

    def delete(self, request):
        try:
            cart = Cart.objects.get(user=request.user)
            cart.items.all().delete()
            return Response({'message': 'Purchase successful! Cart cleared.'}, status=status.HTTP_200_OK)
        except Cart.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)