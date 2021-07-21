from django.urls import path, re_path
from . import views


urlpatterns = [
    path('', views.whonet_landing, name="whonet_landing"),
    path('whonet_import', views.whonet_import, name="whonet_import"),
    path('login',views.staff_login, name="staff_login"),
    path('logout',views.staff_logout, name="staff_logout"),
    re_path(r'whonet_import/data/(?P<file_id>\w{0,50})/$', views.whonet_import_data,name="whonet_import_data"),
    re_path(r'whonet_transform/data/(?P<file_id>\w{0,50})/$', views.whonet_transform_data,name="whonet_transform_data"),
    re_path(r'whonet_transform/final/(?P<file_id>\w{0,50})/$', views.whonet_retrieve_final,name="whonet_retrieve_final"),
    re_path(r'whonet_data_summary/data/(?P<file_id>\w{0,50})/$', views.whonet_data_summary_report,name="whonet_data_summary_report"),
    re_path(r'whonet_data_summary/delete/(?P<file_id>\w{0,50})/$', views.delete_raw,name="delete_raw"),
    path('whonet_transform', views.whonet_transform, name="whonet_transform"),
    path('whonet_data_summary', views.whonet_data_summary, name="whonet_data_summary"),
    path('whonet_transform_year', views.whonet_transform_year, name="whonet_transform_year"),
    path('whonet_transform_year_all', views.whonet_transform_year_all, name="whonet_transform_year_all"),
    path('whonet_transform_referred', views.whonet_transform_referred, name="whonet_transform_referred"),
    path('referred_import', views.referred_import, name="referred_import"),
    path('whonet_final_import', views.final_import, name="final_import"),
    re_path(r'whonet_final_summary_report/data/(?P<file_id>\w{0,50})/$', views.final_summary_report,name="final_summary_report"),
    path('whonet_satscan', views.satscan, name="whonet_satscan"),
    path('whonet_delete_referred', views.delete_referred, name="whonet_delete_referred"),
    re_path(r'whonet_transform/(?P<site>\w{0,50})/$', views.whonet_transform_sentinel,name="whonet_transform_sentinel"),   
    
    
    
    
    #################### BIOINFORMATICS ENDPOINTS ##################################
    
    path('bioinfo_merge', views.bioinfo_merge,name="bioinfo_merge"),
    
    
    #################### END OF BIOINFORMATICS ENDPOINTS ###########################
] 