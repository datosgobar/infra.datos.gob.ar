from django.urls import path
from infra.apps.catalog import views as catalog_views

app_name = 'catalog'

urlpatterns = [
    path('', catalog_views.CatalogView.as_view(), name='list'),
    path('add/', catalog_views.AddCatalogView.as_view(), name='add')
]
