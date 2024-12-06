from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("addcamera",views.addCamera, name="addCamera"),
    path("getallcameras",views.getAllCameras, name="getallcameras"),
    path("startService",views.startService, name="startService"),
    path("stopService",views.stopService, name="stopService"),

     path('createproduct', views.create_product, name='create_product'),
    path('getproduct/<int:product_id>', views.get_product, name='get_product'),
    path('getproductbyname/<str:product_name>', views.get_product_by_name, name='get_product_by_name'),
    path('getallproduct', views.get_all_products, name='get_all_products'),
    path('deleteproduct/<int:product_id>', views.soft_delete_product, name='soft_delete_product'),

    path('getallproduction', views.get_all_production, name='get_all_production'),
    path('getproductionbydate', views.get_production_by_date, name='get_production_by_date'),
    path('createproduction', views.create_production, name='get_all_production'),


    path('getcampayload', views.getCameraPayload, name='getCameraPayload'),


]