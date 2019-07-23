from django.urls import path

from infra.apps.catalog import views as catalog_views

app_name = 'catalog'

urlpatterns = [
    path('', catalog_views.CatalogView.as_view(), name='list'),
    path('add/', catalog_views.AddCatalogView.as_view(), name='add'),
    path('nodes/', catalog_views.NodeListView.as_view(), name='nodes'),
    path('nodes/<int:id>/', catalog_views.NodeUploadsView.as_view(), name='node_catalogs')
]
