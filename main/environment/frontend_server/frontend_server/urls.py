"""frontend_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path, re_path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from translator import views as translator_views

urlpatterns = [
    re_path(r'^$', translator_views.landing, name='landing'),
    re_path(r'^simulator_home$', translator_views.home, name='home'),
    re_path(r'^demo/(?P<sim_code>[\w-]+)/(?P<step>[\w-]+)/(?P<play_speed>[\w-]+)/$', translator_views.demo, name='demo'),
    re_path(r'^replay/(?P<sim_code>[\w-]+)/(?P<step>[\w-]+)/$', translator_views.replay, name='replay'),
    re_path(r'^replay_persona_state/(?P<sim_code>[\w-]+)/(?P<step>[\w-]+)/(?P<persona_name>[\w-]+)/$', translator_views.replay_persona_state, name='replay_persona_state'),
    re_path(r'^process_environment/$', translator_views.process_environment, name='process_environment'),
    re_path(r'^update_environment/$', translator_views.update_environment, name='update_environment'),
    re_path(r'^path_tester/$', translator_views.path_tester, name='path_tester'),
    re_path(r'^path_tester_update/$', translator_views.path_tester_update, name='path_tester_update'),
    path('admin/', admin.site.urls),
]
