from django.urls import path
from infra.apps.catalog import views as catalog_views

urlpatterns = [
    path('', catalog_views.CatalogView.as_view(), name='catalogs'),
    path('add', catalog_views.AddCatalogView.as_view(), name='add_catalog')
]
