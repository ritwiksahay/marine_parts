from django.conf.urls import url

from . import views

urlpatterns = [
    # ex: /polls/
    url(r'^$', views.BulkUpdaterView.as_view, name='index')
]