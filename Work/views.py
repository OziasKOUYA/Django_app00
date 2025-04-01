from django.db import connection
from .db import get_connection
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection 
import hashlib
import uuid

import MySQLdb










def inscription_admin(request):

    if request.method == "POST":
        nom_complet = request.POST['nom_complet']
        email = request.POST['email_admin']
        mot_de_passe = request.POST['mot_de_passe']
        hashed_password = hashlib.md5(mot_de_passe.encode()).hexdigest()

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM admin WHERE email_admin = %s", (email,))
        if cursor.fetchone():
            messages.error(request, "Cet email est déjà utilisé.")
        else:
            cursor.execute("INSERT INTO admin (nom_complet, email_admin, mot_de_passe) VALUES (%s, %s, %s)",
                           (nom_complet, email, hashed_password))
            conn.commit()
            messages.success(request, "Compte admin créé avec succès !")
            return redirect('liste_admin')

        cursor.close()
        conn.close()

    return render(request, 'admin/ajouter_admin/cree_admin.html')

def liste_admin(request):
    connection = get_connection()
    cursor = connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("SELECT * FROM admin")
    admins = cursor.fetchall()

    connection.close()

    return render(request, "admin/ajouter_admin/liste_admin.html", {
        "admins": admins
    })








def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()
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





def inscription_client(request):
    if request.method == "POST":
        # Récupération des données avec strip() pour nettoyer
        nom_complet = request.POST.get('nom_complet', '').strip()
        email = request.POST.get('email_client', '').strip().lower()  # Normalisation en minuscules
        mot_de_passe = request.POST.get('mot_de_passe', '')
        confirmation_mot_de_passe = request.POST.get('confirmation_mot_de_passe', '')

        # 1. Validation de l'email
        if not email:
            messages.error(request, "L'email est obligatoire.")
            return redirect('inscription_client')
        
        if not validate_email(email):
            messages.error(request, "Format d'email invalide. Veuillez entrer un email valide.")
            return redirect('inscription_client')

        # 2. Vérification des mots de passe
        if not mot_de_passe or len(mot_de_passe) < 8:
            messages.error(request, "Le mot de passe doit contenir au moins 8 caractères.")
            return redirect('inscription_client')
        
        if mot_de_passe != confirmation_mot_de_passe:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect('inscription_client')

        # 3. Vérification si l'email existe déjà
        with connection.cursor() as cursor:
            cursor.execute("SELECT id_client FROM client WHERE email_client = %s", [email])
            if cursor.fetchone():
                messages.error(request, "Cet email est déjà utilisé.")
                return redirect('inscription_client')

            # Tout est valide → Hachage et enregistrement
            hashed_password = hash_password(mot_de_passe)
            verification_token = str(uuid.uuid4())

            cursor.execute(
                "INSERT INTO client (nom_complet, email_client, mot_de_passe, verification_token, is_verified) "
                "VALUES (%s, %s, %s, %s, %s)",
                [nom_complet, email, hashed_password, verification_token, False]
            )

        messages.success(request, "Inscription réussie!")
        return redirect('login')

    return render(request, 'client/inscription.html')

