from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.index, name='home'),
    path('customers/', views.customers_list, name='customers_list'),
    path('products/', views.products_list, name='products_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart, name='cart'),
    path('order-status/', views.order_status, name='order_status'),
    path('login/', views.customer_login, name='customer_login'),
    path('logout/', views.customer_logout, name='customer_logout'),
    path('register/', views.customer_register, name='customer_register'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/', views.remove_from_cart, name='remove_from_cart'),
    path('address-selection/', views.address_selection, name='address_selection'),
    path('place-order/', views.place_order, name='place_order'),
    path('order-confirmation/', views.order_confirmation, name='order_confirmation'),

]

# end urls.py