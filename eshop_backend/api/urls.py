from django.urls import path
from .views import ProductList, RegisterView, LoginView, LogoutView, CartView

urlpatterns = [
    path('products/', ProductList.as_view(), name='product-list'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('cart/', CartView.as_view(), name='cart-dashboard'),
]