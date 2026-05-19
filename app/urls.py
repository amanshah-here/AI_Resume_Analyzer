from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload, name='upload'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('contact/', views.contact, name='contact'),
    path('donate/', views.donate, name='donate'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('admin-dashboard/', views.admin_dashboard, name="admin_dashboard"),
    path("donate/", views.donate, name="donate"),
path("payment-success/", views.payment_success, name="payment_success"),
]