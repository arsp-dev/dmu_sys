from django.urls import path, re_path
from . import views


urlpatterns = [
    path('', views.whonet_landing, name="whonet_landing"),
    path('whonet_import', views.whonet_import, name="whonet_import"),
    path('login',views.staff_login, name="staff_login"),
    path('logout',views.staff_logout, name="staff_logout"),
    re_path(r'whonet_import/data/(?P<file_id>\w{0,50})/$', views.whonet_import_data,name="whonet_import_data"),
    re_path(r'whonet_transform/data/(?P<file_id>\w{0,50})/$', views.whonet_transform_data,name="whonet_transform_data"),
    path('whonet_transform', views.whonet_transform, name="whonet_transform"),
    path('whonet_data_summary', views.whonet_data_summary, name="whonet_data_summary"),
    path('whonet_transform_year', views.whonet_transform_year, name="whonet_transform_year"),
    re_path(r'whonet_transform/(?P<site>\w{0,50})/$', views.whonet_transform_sentinel,name="whonet_transform_sentinel")
   
    
] 