from django.urls import path

from infra.apps.catalog import views as catalog_views

app_name = 'catalog'

urlpatterns = [
    path('',
         catalog_views.NodeListView.as_view(),
         name='nodes'),
    path('<int:node_id>/',
         catalog_views.NodeUploadsView.as_view(),
         name='node'),
    path('<int:node_id>/catalogs/add/',
         catalog_views.AddCatalogView.as_view(),
         name='add_catalog'),
    path('<int:node_id>/success/',
         catalog_views.CatalogUploadSuccess.as_view(),
         name='upload_success'),
    path('<int:node_id>/distributions/',
         catalog_views.ListDistributions.as_view(),
         name='node_distributions'),
    path('<int:node_id>/distributions/add/',
         catalog_views.AddDistributionView.as_view(),
         name='add_distribution'),
    path('<int:node_id>/distributions/<str:identifier>/',
         catalog_views.DistributionUploads.as_view(),
         name='distribution_uploads'),
    path('<int:node_id>/distributions/<int:dist_id>/',
         catalog_views.EditDistributionView.as_view(),
         name='edit_distribution')
]
