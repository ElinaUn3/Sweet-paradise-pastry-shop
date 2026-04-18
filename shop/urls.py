from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    path('', views.catalog_view, name='catalog'),
    path('products/<int:pk>/', views.product_detail_view, name='product_detail'),
    path('products/add/', views.product_create_view, name='product_create'),
    path('products/<int:pk>/edit/', views.product_edit_view, name='product_edit'),
    path('products/<int:pk>/delete/', views.product_delete_view, name='product_delete'),

    path('orders/', views.orders_view, name='orders'),
    path('orders/<int:pk>/', views.order_detail_view, name='order_detail'),
    path('orders/add/', views.order_create_view, name='order_create'),
    path('orders/<int:pk>/edit/', views.order_edit_view, name='order_edit'),
    path('orders/<int:pk>/delete/', views.order_delete_view, name='order_delete'),

    path('users/', views.users_view, name='users'),
    path('users/add/', views.user_create_view, name='user_create'),
    path('users/<int:pk>/edit/', views.user_edit_view, name='user_edit'),
    path('users/<int:pk>/delete/', views.user_delete_view, name='user_delete'),
]
