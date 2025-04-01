from django.urls import path
from . import views

urlpatterns = [
  
        # Inclure les URLs de l'application
    path('test/', views.test, name='test' ),
    path('test2/', views.test2, name='test2' ),

    path('list_bus/', views.list_bus, name='list_bus'),
    path('add_bus/', views.add_bus, name='add_bus'),
    path('edit/<int:id>/', views.edit_bus, name='edit_bus'),
    path('delete/<int:id>/', views.delete_bus, name='delete_bus'),
]
