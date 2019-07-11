from django.urls import re_path
from infra.apps.catalog import views as catalog_views

urlpatterns = [
    re_path(r'^$', catalog_views.CatalogView.as_view(), name='catalogs'),
    re_path(r'^add$', catalog_views.AddCatalogView.as_view(), name='add_catalog')
]
