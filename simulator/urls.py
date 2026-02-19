from django.urls import path
from .views import import_data_view

from simulator import views

app_name = 'catalog'

urlpatterns = [
    path('', views.catalog, name='index'),
    path('topic/<slug:topic_slug>/', views.topic, name='topic'),
    path("import-data/", import_data_view),
]