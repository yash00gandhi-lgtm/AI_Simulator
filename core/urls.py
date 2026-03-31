from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [

    # 🛠 Admin
    path('admin/', admin.site.urls),

    # 🔥 ROOT → SIGNUP
    path('', lambda request: redirect('/signup/')),

    # 🌐 APP ROUTES
    path('', include('app.urls')),

]