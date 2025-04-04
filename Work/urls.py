from django.urls import path
from . import views

urlpatterns = [
  
   
    
    path('test/', views.test, name='test' ),
    path('test2/', views.test2, name='test2' ),

    path('list_bus/', views.list_bus, name='list_bus'),
    path('add_bus/', views.add_bus, name='add_bus'),
    path('edit/<int:id>/', views.edit_bus, name='edit_bus'),
    path('delete/<int:id>/', views.delete_bus, name='delete_bus'),

    path('voyages/', views.list_voyages, name='list_voyages'),
    path('voyages/add/', views.add_voyage, name='add_voyage'),
    path('voyages/edit/<int:id>/', views.edit_voyage, name='edit_voyage'),
    path('voyages/delete/<int:id>/', views.delete_voyage, name='delete_voyage'),

    path('chauffeurs/', views.list_chauffeurs, name='list_chauffeurs'),
    path('chauffeurs/add/', views.add_chauffeur, name='add_chauffeur'),
    path('chauffeurs/edit/<int:id>/', views.edit_chauffeur, name='edit_chauffeur'),
    path('chauffeurs/delete/<int:id>/', views.delete_chauffeur, name='delete_chauffeur'),
]

