from .imports import *

app_name = 'product'
urlpatterns = [
    path('media/', MediaFilesListCreateView.as_view(), name='media_files_list'),
    path('media/<str:pk>/', MediaFilesRetrieveUpdateView.as_view(), name='media_files_retrieve'),

    path('category/', CategoryListCreateView.as_view(), name='category_list'),
    path('category/<str:pk>/', CategoryRetrieveUpdateDeleteView.as_view(), name='category_retrieve'),

    path('umo/', UnitOfMeasurementListCreateView.as_view(), name='umo_list'),
    path('umo/<str:pk>/', UnitOfMeasurementRetrieveUpdateDeleteView.as_view(), name='umo_list'),

    path('product/', ProductListCreateView.as_view(), name='product_list'),
    path('product/<str:pk>/', ProductRetrieveUpdateDeleteView.as_view(), name='product_list'),

    path('tags/', ItemTagsListCreateApiView.as_view(), name='item_tags_list'),
    path('tags/<str:pk>/', ItemTagsRetrieveUpdateDeleteApiView.as_view(), name='item_tags_list'),

    path("send/", NotificationView.as_view(), name="send-notification"),

    path('logs/', ActivityLogsListApiView.as_view(), name='activity_logs_list'),
]