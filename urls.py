from django.contrib import admin
from django.urls import path,include
from .import views

urlpatterns = [
    path('',views.index,name="home-page"),
    path('userhome',views.userhome,name="userhome"),
    path('vol',views.vol,name="vol"),
    path('login',views.login,name="login"),
    path('register',views.register,name="register"),
    path('donate',views.donate,name="donate"),
    path('add_ins/', views.add_institution, name='add_institution'),
    path('donate',views.donate,name='donate'),
    path('pick_up/<int:donation_id>/', views.pick_up_donation, name='pick_up_donation'),
    path('payment/', views.process_payment, name='payment'),
    path('verify-otp/<int:payment_id>/', views.verify_otp, name='verify_otp'),
    path('add_donation/', views.add_donation, name='add_donation'),
    path('logout',views.logout,name="logout"),
    path('about',views.about,name="about"),
    path('causes',views.causes,name="causes"),
    path('add_request/', views.add_request, name='add_request'),
    
]
