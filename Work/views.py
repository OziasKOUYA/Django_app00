from django.db import connection
from .db import get_connection
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection 
import MySQLdb



# Create your views here.
def test(request):
    return render(request, 'admin/index.html')

def test2(request):
    return render(request,'client/index.html')

# Afficher tous les bus
def list_bus(request):
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Bus")
    buses = cursor.fetchall()
    db.close()
    return render(request, 'admin/bus/liste_bus.html', {'buses': buses})

# Ajouter un bus
def add_bus(request):
    if request.method == 'POST':
        nom = request.POST['nom']
        plaque = request.POST['plaque']
        places = request.POST['places']

        db = get_connection()
        cursor = db.cursor()
        cursor.execute("INSERT INTO Bus (nom_du_bus, plaque_du_bus, nombre_de_place) VALUES (%s, %s, %s)", 
                       (nom, plaque, places))
        db.commit()
        db.close()
        return redirect('list_bus')
    return render(request, 'admin/bus/ajout_bus.html')

# Modifier un bus
def edit_bus(request, id):
    db = get_connection()
    cursor = db.cursor()
    if request.method == 'POST':
        nom = request.POST['nom']
        plaque = request.POST['plaque']
        places = request.POST['places']
        cursor.execute("UPDATE Bus SET nom_du_bus=%s, plaque_du_bus=%s, nombre_de_place=%s WHERE id_bus=%s",
                       (nom, plaque, places, id))
        db.commit()
        db.close()
        return redirect('list_bus')
    cursor.execute("SELECT * FROM Bus WHERE id_bus = %s", (id,))
    bus = cursor.fetchone()
    db.close()
    return render(request, 'admin/bus/modifier_bus.html', {'bus': bus})

# Supprimer un bus
def delete_bus(request, id):
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Bus WHERE id_bus = %s", (id,))
    db.commit()
    db.close()
    return redirect('list_bus')






# Liste des voyages
def list_voyages(request):
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("""
        SELECT v.id_voyage, b.nom_du_bus, v.ville_depart, v.ville_arrivee, v.date_depart,
               v.heure_depart, v.prix_ticket, v.places_disponibles, v.chauffeur, v.statut
        FROM Voyage v
        JOIN Bus b ON v.bus_id = b.id_bus
    """)
    voyages = cursor.fetchall()
    db.close()
    return render(request, 'admin/voyage/liste_voyage.html', {'voyages': voyages})

# Ajouter un voyage
def add_voyage(request):
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("SELECT id_bus, nom_du_bus FROM Bus")
    bus_list = cursor.fetchall()

    if request.method == 'POST':
        data = (
            request.POST['bus_id'],
            request.POST['ville_depart'],
            request.POST['ville_arrivee'],
            request.POST['date_depart'],
            request.POST['heure_depart'],
            request.POST['prix_ticket'],
            request.POST['places_disponibles'],
            request.POST['chauffeur'],
            request.POST['statut']
        )
        cursor.execute("""
            INSERT INTO Voyage (
                bus_id, ville_depart, ville_arrivee, date_depart,
                heure_depart, prix_ticket, places_disponibles, chauffeur, statut
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, data)
        db.commit()
        db.close()
        return redirect('list_voyages')
    
    db.close()
    return render(request, 'admin/voyage/ajout_voyage.html', {'bus_list': bus_list})

# Modifier un voyage
def edit_voyage(request, id):
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("SELECT id_bus, nom_du_bus FROM Bus")
    bus_list = cursor.fetchall()

    if request.method == 'POST':
        data = (
            request.POST['bus_id'],
            request.POST['ville_depart'],
            request.POST['ville_arrivee'],
            request.POST['date_depart'],
            request.POST['heure_depart'],
            request.POST['prix_ticket'],
            request.POST['places_disponibles'],
            request.POST['chauffeur'],
            request.POST['statut'],
            id
        )
        cursor.execute("""
            UPDATE Voyage SET
                bus_id=%s, ville_depart=%s, ville_arrivee=%s, date_depart=%s,
                heure_depart=%s, prix_ticket=%s, places_disponibles=%s,
                chauffeur=%s, statut=%s
            WHERE id_voyage=%s
        """, data)
        db.commit()
        db.close()
        return redirect('list_voyages')

    cursor.execute("SELECT * FROM Voyage WHERE id_voyage = %s", (id,))
    voyage = cursor.fetchone()
    db.close()
    return render(request, 'admin/voyage/modifier_voyage.html', {'voyage': voyage, 'bus_list': bus_list})

# Supprimer un voyage
def delete_voyage(request, id):
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Voyage WHERE id_voyage = %s", (id,))
    db.commit()
    db.close()
    return redirect('list_voyages')



