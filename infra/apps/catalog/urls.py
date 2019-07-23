from django.urls import path
from infra.apps.catalog import views as catalog_views

app_name = 'catalog'

urlpatterns = [
    path('', catalog_views.CatalogView.as_view(), name='list'),
    path('add/', catalog_views.AddCatalogView.as_view(), name='add'),
    path('add/<int:node>/', catalog_views.AddDistribution.as_view(), name='add_distribution'),
    path('<int:node>/distributions/',
         catalog_views.ListDistributions.as_view(),
         name='list_distributions'),
    path('success/', catalog_views.CatalogUploadSuccess.as_view(), name='upload_success')
]
