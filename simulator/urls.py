from django.urls import path

from simulator import views

app_name = 'catalog'

urlpatterns = [
    path('', views.catalog, name='index'),
    path('topic/<slug:topic_slug>/', views.topic, name='topic'),
]