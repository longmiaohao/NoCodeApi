"""ApiGate URL Configuration

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

from django.conf.urls import url
from apigate.main import http as api_view

urlpatterns = [
       url(r'DatabaseManagement', api_view.DatabaseManagement, name="api_view_DatabaseManagement"),
       url(r'DatabaseList', api_view.DatabaseList, name="api_view_DatabaseList"),
       url(r'ChangeStatus', api_view.ChangeStatus, name="api_view_ChangeStatus"),
       url(r'TestConnection', api_view.TestConnection, name="api_view_TestConnection"),
       url(r'GetTablesByDB', api_view.GetTablesByDB, name="api_view_GetTablesByDB"),
       url(r'ApiList', api_view.ApiList, name="api_view_ApiList"),
       url(r'ApiConfig', api_view.ApiConfig, name="api_view_ApiConfig"),
       url(r'DeleteConfig', api_view.delete, name="api_view_delete"),
       url(r'', api_view.base, name="api_view_base"),
]
