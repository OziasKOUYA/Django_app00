from django.db import connection
from .db import get_connection
from django.shortcuts import render, redirect
from django.contrib import messages
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



