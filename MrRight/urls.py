"""MrRight URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
# from django.conf.urls import url
# from django.contrib import admfrom django.urls import path
from django.urls import path
from index import views as index_views
from user import views as user_views

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    path('index/', index_views.index),
    path('api/user/vcode/fetch', user_views.fetch_vcode),
    path('api/user/vcode/submit', user_views.submit_vcode),
    path('api/user/profile/show', user_views.show_profile),
    path('api/user/profile/update', user_views.update_profile),
    path('qiniu/token', user_views.get_qn_token),
    path('qiniu/callback', user_views.qn_callback),
]
