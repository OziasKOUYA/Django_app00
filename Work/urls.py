from django.urls import path
from . import views

urlpatterns = [

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

    path('add_ticket/', views.add_ticket, name='add_ticket'),
    path('add_ticket_/', views.add_ticket_, name='add_ticket_'),
    path('tickets/', views.tickets_list, name='tickets_list'),
    

    path('ticket/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('ticket/delete/<int:ticket_id>/', views.delete_ticket, name='delete_ticket'),

    path('clients/', views.list_clients, name='list_clients'),
    path('clients/ajouter/', views.add_client, name='add_client'),
    path('clients/modifier/<int:client_id>/', views.edit_client, name='edit_client'),
    path('clients/supprimer/<int:client_id>/', views.delete_client, name='delete_client'),




    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('acc/admin', views.admin_dashbo, name='admin_dashboard'),
    path('client/dashboard/', views.client_dashboard, name='client_dashboard'),



    path('admins/', views.list_admins, name='list_admins'),
    path('admins/ajouter/', views.add_admin, name='add_admin'),
    path('admins/supprimer/<int:id_admin>/', views.delete_admin, name='delete_admin'),

    path('voyages_client/', views.list_voyages_client, name='list_voyages_client'),
    path('reserver/<int:id_voyage>/', views.reserver_voyage, name='reserver_voyage'),
    path('mes-tickets/', views.client_tickets, name='client_tickets'),
    path('mon_ticket/<str:numero_ticket>/', views.detail_ticket, name='detail_ticket'),



    
]

