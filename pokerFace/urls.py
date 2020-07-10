"""pokerFace URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app import views as vs

urlpatterns = [
    path('app/', vs.index),
    path('admin/', admin.site.urls),
    path('app/index/', vs.index),
    path('app/register/', vs.createUser),
    path('app/login/', vs.myLogin),
    path('app/logout/', vs.myLogout),
    path('app/modify/', vs.modify),
    path('app/Camera/', vs.CMR),
    path('app/Camera2Server/', vs.CMR2server),
    path('app/text2audio/', vs.text2audio),
    path('app/rank/', vs.rank),
    path('app/history/', vs.history),
    path('app/deleteHistory/', vs.delete_history),
    path('app/updateHistory/', vs.update_history),
    path('app/thumbsUp/', vs.thumbs_up),
]
