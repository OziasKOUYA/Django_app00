from datetime import datetime
from venv import logger
from django.db import connection
from django.http import Http404, HttpResponse, JsonResponse
from .db import get_connection
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
import hashlib



def generer_numero_voyage():
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM Voyage")
    count = cursor.fetchone()[0]
    numero = f"VOY-{count + 1:04d}"  # Ex: VOY-0001
    db.close()
    return numero

def generer_numero_ticket():
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM ticket")
    count = cursor.fetchone()[0]
    db.close()

    next_number = count + 1
    return f"TICKET-{next_number:04d}"  # TICKET-0001, TICKET-0002, ...












def list_clients(request):
    if request.session.get('user_role') != 'admin':
        return redirect('login')
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM client")
    clients = cursor.fetchall()
    db.close()
    return render(request, 'client/list_client.html', {'clients': clients})


def add_client(request):

    if request.method == 'POST':
        nom_complet = request.POST['nom_complet']
        email = request.POST['email_client']
        mot_de_passe = request.POST['mot_de_passe']
        hashed_password = hashlib.md5(mot_de_passe.encode()).hexdigest()

        db = get_connection()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO client (nom_complet, email_client, mot_de_passe)
            VALUES (%s, %s, %s)
        """, (nom_complet, email, hashed_password))
        db.commit()
        db.close()

        messages.success(request, "Client ajouté avec succès.")
        return redirect('login')

    return render(request, 'client/add_client.html')


def edit_client(request, client_id):
    if request.session.get('user_role') != 'admin':
        return redirect('login')
    db = get_connection()
    cursor = db.cursor()
    if request.method == 'POST':
        nom_complet = request.POST['nom_complet']
        email = request.POST['email_client']
        mot_de_passe = request.POST['mot_de_passe']

        cursor.execute("""
            UPDATE client SET nom_complet=%s, email_client=%s, mot_de_passe=%s
            WHERE id_client=%s
        """, (nom_complet, email, mot_de_passe, client_id))
        db.commit()
        db.close()

        messages.success(request, "Client modifié avec succès.")
        return redirect('list_clients')
    else:
        cursor.execute("SELECT * FROM client WHERE id_client = %s", [client_id])
        client = cursor.fetchone()
        db.close()
        return render(request, 'client/edit_client.html', {'client': client})


def delete_client(request, client_id):
    if request.session.get('user_role') != 'admin':
        return redirect('login')
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM client WHERE id_client = %s", [client_id])
    db.commit()
    db.close()

    messages.success(request, "Client supprimé avec succès.")
    return redirect('list_clients')


### ---------------- ADMIN ----------------





# 🔐 Hash password (optionnel)
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

# 📋 Liste des admins
def list_admins(request):
    if request.session.get('user_role') != 'admin':
        return redirect('login')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM admin")
    admins = cursor.fetchall()
    return render(request, 'admin/ajouter_admin/liste_admin.html', {'admins': admins})

# ➕ Ajouter admin
def add_admin(request):
    if request.session.get('user_role') != 'admin':
        return redirect('login')
    if request.method == 'POST':
        nom_complet = request.POST['nom_complet']
        email_admin = request.POST['email_admin']
        mot_de_passe = request.POST['mot_de_passe']
        hashed_password = hashlib.md5(mot_de_passe.encode()).hexdigest()

        cursor = connection.cursor()
        try:
            cursor.execute("INSERT INTO admin (nom_complet, email_admin, mot_de_passe) VALUES (%s, %s, %s)", 
                           (nom_complet, email_admin, hashed_password))
            messages.success(request, "Admin ajouté avec succès.")
        except:
            messages.error(request, "Erreur : email déjà utilisé.")
        return redirect('list_admins')
    
    return render(request, 'admin/ajouter_admin/ajout_admin.html')

# ❌ Supprimer admin
def delete_admin(request, id_admin):
    if request.session.get('user_role') != 'admin':
        return redirect('login')
    cursor = connection.cursor()
    cursor.execute("DELETE FROM admin WHERE id_admin = %s", [id_admin])
    messages.success(request, "Admin supprimé.")
    return redirect('list_admins')


def login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        hashed_password = hashlib.md5(password.encode()).hexdigest()

        with connection.cursor() as cursor:
            # Check Client

            cursor.execute("SELECT * FROM admin WHERE email_admin=%s AND mot_de_passe=%s", [email, hashed_password])
            admin = cursor.fetchone()
            if admin:
                request.session['user_id'] = admin[0]
                request.session['user_name'] = admin[1]
                request.session['user_email'] = admin[2]
                request.session['user_role'] = 'admin'
                return redirect('admin_dashboard')

            cursor.execute("SELECT * FROM client WHERE email_client=%s AND mot_de_passe=%s", [email, hashed_password])
            client = cursor.fetchone()
            if client:
                request.session["id_client"] = client[0]  # id_client
                request.session["email_client"] = client[2]
                request.session["nom_complet_client"] = client[1]
                request.session["user_role"] = "client"
                return redirect('client_dashboard')

            # Check Admin
            
            messages.error(request, "Email ou mot de passe incorrect.")
            return redirect('login')

    return render(request, "login.html")



# ===============================
# 🔓 LOGOUT (général)
# ===============================
def logout(request):
    request.session.flush()
    messages.success(request, "Déconnexion réussie.")
    return redirect('login')




def admin_dashbo(request):
    if request.session.get('user_role') != 'admin':
        return redirect('login')

    total_tickets = 0
    total_voyages = 0
    total_bus = 0
    total_reservations = 0

    try:
        with connection.cursor() as cursor:
            # 🔹 1. Nombre total de tickets
            cursor.execute("SELECT COUNT(*) FROM ticket")
            total_tickets = cursor.fetchone()[0]
            print("🎫 Nombre de tickets =", total_tickets)

            # 🔹 2. Nombre total de voyages
            cursor.execute("SELECT COUNT(*) FROM voyage")
            total_voyages = cursor.fetchone()[0]
            print("🚌 Nombre de voyages =", total_voyages)

            # 🔹 3. Nombre total de bus
            cursor.execute("SELECT COUNT(*) FROM bus")
            total_bus = cursor.fetchone()[0]
            print("🚍 Nombre de bus =", total_bus)

            # 🔹 4. Nombre total de réservations
            cursor.execute("SELECT COUNT(*) FROM reservation")
            total_reservations = cursor.fetchone()[0]
            print("📦 Nombre de réservations =", total_reservations)

    except Exception as e:
        print("❌ Erreur SQL:", e)

    return render(request, 'admin/index.html', {
        'total_tickets': total_tickets,
        'total_voyages': total_voyages,
        'total_bus': total_bus,
        'total_reservations': total_reservations,
    })
def client_dashboard(request):
    if request.session.get('user_role') != 'client' or not request.session.get('id_client'):
        return redirect('login')

    client_id = request.session.get('id_client')

    print("📌 dashboard_client appelée avec client_id =", client_id)

    total_voyages = 0
    total_reservations = 0
    total_reservations_confirmees = 0

    try:
        with connection.cursor() as cursor:
            # 🔹 1. Nombre total de voyages
            cursor.execute("SELECT COUNT(*) FROM voyage")
            total_voyages = cursor.fetchone()[0]
            print("✅ Total voyages =", total_voyages)

            # 🔹 2. Nombre de réservations pour ce client
            cursor.execute("SELECT COUNT(*) FROM reservation WHERE id_client = %s", [client_id])
            total_reservations = cursor.fetchone()[0]
            print("✅ Total réservations client =", total_reservations)

            # 🔹 3. Nombre de réservations confirmées
            cursor.execute("SELECT COUNT(*) FROM reservation WHERE id_client = %s AND statut = 'confirmé'", [client_id])
            total_reservations_confirmees = cursor.fetchone()[0]
            print("✅ Réservations confirmées =", total_reservations_confirmees)

    except Exception as e:
        print("❌ Erreur dans dashboard_client :", e)
    return render(request, 'client/index.html',{
        'total_voyages': total_voyages,
        'total_reservations': total_reservations,
        'confirmed_reservations': total_reservations_confirmees
    })









# Afficher tous les bus
def list_bus(request):
    if request.session.get('user_role') != 'admin':
        return redirect('login')
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Bus")
    buses = cursor.fetchall()
    db.close()
    return render(request, 'admin/bus/liste_bus.html', {'buses': buses})

# Ajouter un bus
def add_bus(request):
    if request.session.get('user_role') != 'admin':
        return redirect('login')
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
    if request.session.get('user_role') != 'admin':
        return redirect('login')
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
    if request.session.get('user_role') != 'admin':
        return redirect('login')
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Bus WHERE id_bus = %s", (id,))
    db.commit()
    db.close()
    return redirect('list_bus')


# Liste des voyages
def list_voyages(request):
    if request.session.get('user_role') != 'admin':
        return redirect('login')
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("""
        SELECT v.id_voyage, b.nom_du_bus, v.ville_depart, v.ville_arrivee, v.date_depart,
               v.heure_depart, v.prix_ticket, v.places_disponibles,
               c.nom AS chauffeur_nom, v.statut, v.numero_voyage 
        FROM voyage v
        JOIN bus b ON v.bus_id = b.id_bus
        JOIN chauffeur c ON v.chauffeur_id = c.id_chauffeur
    """)
    voyages = cursor.fetchall()
    db.close()
    return render(request, 'admin/voyage/liste_voyage.html', {'voyages': voyages})


# Ajouter un voyage
def add_voyage(request):
    if request.session.get('user_role') != 'admin':
        return redirect('login')
    db = get_connection()
    cursor = db.cursor()

    cursor.execute("SELECT id_bus, nom_du_bus FROM bus")
    bus_list = cursor.fetchall()

    cursor.execute("SELECT id_chauffeur, nom FROM chauffeur WHERE statut = 'actif'")
    chauffeur_list = cursor.fetchall()

    if request.method == 'POST':
        numero_voyage = generer_numero_voyage()  # 👈 Génère le numéro ici

        data = (
            numero_voyage,  # 👈 On ajoute le numéro de voyage ici
            request.POST['bus_id'],
            request.POST['chauffeur_id'],
            request.POST['ville_depart'],
            request.POST['ville_arrivee'],
            request.POST['date_depart'],
            request.POST['heure_depart'],
            request.POST['prix_ticket'],
            request.POST['places_disponibles'],
            request.POST['statut']
        )

        cursor.execute("""
            INSERT INTO voyage (
                numero_voyage, bus_id, chauffeur_id, ville_depart, ville_arrivee,
                date_depart, heure_depart, prix_ticket, places_disponibles, statut
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, data)

        db.commit()
        db.close()
        return redirect('list_voyages')

    db.close()
    return render(request, 'admin/voyage/ajout_voyage.html', {
        'bus_list': bus_list,
        'chauffeur_list': chauffeur_list
    })

# Modifier un voyage
def edit_voyage(request, id):
    if request.session.get('user_role') != 'admin':
        return redirect('login')
    db = get_connection()
    cursor = db.cursor()

    cursor.execute("SELECT id_bus, nom_du_bus FROM Bus")
    bus_list = cursor.fetchall()

    cursor.execute("SELECT id_chauffeur, nom FROM Chauffeur")
    chauffeur_list = cursor.fetchall()

    statut_list = ['prévu', 'en_cours', 'terminé', 'annulé']

    if request.method == 'POST':
        data = (
            request.POST['bus_id'],
            request.POST['ville_depart'],
            request.POST['ville_arrivee'],
            request.POST['date_depart'],
            request.POST['heure_depart'],
            request.POST['prix_ticket'],
            request.POST['places_disponibles'],
            request.POST['chauffeur_id'],
            request.POST['statut'],
            id
        )
        cursor.execute("""
            UPDATE Voyage SET
                bus_id=%s, ville_depart=%s, ville_arrivee=%s, date_depart=%s,
                heure_depart=%s, prix_ticket=%s, places_disponibles=%s,
                chauffeur_id=%s, statut=%s
            WHERE id_voyage=%s
        """, data)
        db.commit()
        db.close()
        return redirect('list_voyages')

    cursor.execute("SELECT * FROM Voyage WHERE id_voyage = %s", (id,))
    voyage = cursor.fetchone()
    db.close()

    return render(request, 'admin/voyage/modifier_voyage.html', {
        'voyage': voyage,
        'bus_list': bus_list,
        'chauffeur_list': chauffeur_list,
        'statut_list': statut_list
    })


# Supprimer un voyage
def delete_voyage(request, id):
    if request.session.get('user_role') != 'admin':
        return redirect('login')
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Voyage WHERE id_voyage = %s", (id,))
    db.commit()
    db.close()
    return redirect('list_voyages')


# Lister les chauffeurs
def list_chauffeurs(request):
    if request.session.get('user_role') != 'admin':
        return redirect('login')
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM Chauffeur")
    chauffeurs = cursor.fetchall()
    db.close()
    return render(request, 'admin/chauffeur/liste_chauffeur.html', {'chauffeurs': chauffeurs})

# Ajouter un chauffeur
def add_chauffeur(request):
    if request.session.get('user_role') != 'admin':
        return redirect('login')
    if request.method == 'POST':
        data = (
            request.POST['nom'],
            request.POST['telephone'],
            request.POST.get('email', ''),
            request.POST['permis_numero'],
            request.POST['date_naissance'],
            request.POST['adresse'],
            request.POST['date_embauche'],
            request.POST['statut']
        )
        db = get_connection()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO Chauffeur (nom, telephone, email, permis_numero, date_naissance, adresse, date_embauche, statut)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, data)
        db.commit()
        db.close()
        return redirect('list_chauffeurs')
    return render(request, 'admin/chauffeur/ajout_chauffeur.html')

# Modifier un chauffeur
def edit_chauffeur(request, id):
    if request.session.get('user_role') != 'admin':
        return redirect('login')
    db = get_connection()
    cursor = db.cursor()
    statuts = ['actif', 'inactif', 'suspendu']
    if request.method == 'POST':
        data = (
            request.POST['nom'],
            request.POST['telephone'],
            request.POST.get('email', ''),
            request.POST['permis_numero'],
            request.POST['date_naissance'],
            request.POST['adresse'],
            request.POST['date_embauche'],
            request.POST['statut'],
            id
        )
        cursor.execute("""
            UPDATE Chauffeur SET
                nom=%s, telephone=%s, email=%s, permis_numero=%s,
                date_naissance=%s, adresse=%s, date_embauche=%s, statut=%s
            WHERE id_chauffeur=%s
        """, data)
        db.commit()
        db.close()
        return redirect('list_chauffeurs')

    cursor.execute("SELECT * FROM Chauffeur WHERE id_chauffeur = %s", (id,))
    chauffeur = cursor.fetchone()  # Renvoie un tuple avec les données du chauffeur

    
    db.close()
    return render(request, 'admin/chauffeur/modifier_chauffeur.html', {'chauffeur': chauffeur, 'statuts':statuts})

# Supprimer un chauffeur
def delete_chauffeur(request, id):
    if request.session.get('user_role') != 'admin':
        return redirect('login')
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM Chauffeur WHERE id_chauffeur = %s", (id,))
    db.commit()
    db.close()
    return redirect('liste_chauffeurs')


def get_voyage_info(request):
    if request.session.get('user_role') != 'admin':
        return redirect('login')
    numero_voyage = request.GET.get('numero_voyage')
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("""
        SELECT v.bus_id, b.nom_du_bus, v.places_disponibles
        FROM voyage v
        JOIN bus b ON v.bus_id = b.id_bus
        WHERE v.numero_voyage = %s
    """, [numero_voyage])
    row = cursor.fetchone()
    db.close()
    
    if row:
        return JsonResponse({
            'bus_nom': row[1],
            'places_disponibles': row[2]
        })
    else:
        return JsonResponse({'error': 'Voyage non trouvé'}, status=404)


def add_ticket(request):
    if request.session.get('user_role') != 'admin':
        return redirect('login')
    db = get_connection()
    cursor = db.cursor()

    if request.method == 'POST':
        numero_voyage = request.POST['numero_voyage']
        nom_voyageur = request.POST['nom_voyageur']

        # Vérifier les places disponibles
        cursor.execute("SELECT places_disponibles FROM voyage WHERE numero_voyage = %s", [numero_voyage])
        result = cursor.fetchone()

        if not result:
            messages.error(request, "Voyage introuvable.")
        elif result[0] <= 0:
            messages.error(request, "Plus de places disponibles pour ce voyage.")
        else:
            numero_ticket = generer_numero_ticket()

            # Enregistrer le ticket
            cursor.execute("""
                INSERT INTO ticket (numero_du_ticket, numero_voyage, nom_voyageur)
                VALUES (%s, %s, %s)
            """, (numero_ticket, numero_voyage, nom_voyageur))

            # Mettre à jour les places
            cursor.execute("""
                UPDATE voyage SET places_disponibles = places_disponibles - 1
                WHERE numero_voyage = %s
            """, [numero_voyage])

            db.commit()
            messages.success(request, f"Ticket généré avec succès : {numero_ticket}")
            return redirect('tickets_list')

    # Affichage du formulaire
    cursor.execute("SELECT numero_voyage FROM voyage")
    voyages = cursor.fetchall()
    db.close()

    return render(request, 'admin/ticket/ajout_ticket.html', {'voyages': voyages})




def add_ticket_(request):
    if request.session.get('user_role') != 'admin':
        return redirect('login')
    
    db = get_connection()
    cursor = db.cursor()

    if request.method == 'POST' and 'id_reservation' in request.POST:
        id_reservation = request.POST['id_reservation']
        
        try:
            # Récupérer les infos complètes de la réservation
            cursor.execute("""
                SELECT r.id_reservation, r.nom_complet_client, v.numero_voyage, r.id_client
                FROM reservation r
                JOIN voyage v ON r.id_voyage = v.id_voyage
                WHERE r.id_reservation = %s AND r.statut = 'en attente'
            """, [id_reservation])
            reservation = cursor.fetchone()

            if not reservation:
                messages.error(request, "Réservation introuvable ou déjà confirmée.")
            else:
                # Générer un numéro de ticket unique
                numero_ticket = f"TKT-{reservation[0]}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                # Enregistrer le ticket
                cursor.execute("""
                    INSERT INTO ticket (
                        numero_du_ticket, 
                        numero_voyage, 
                        nom_voyageur
                    ) VALUES (%s, %s, %s)
                """, (
                    numero_ticket,
                    reservation[2],  # numero_voyage
                    reservation[1]   # nom_complet_client
                ))

                # Mettre à jour le statut de la réservation
                cursor.execute("""
                    UPDATE reservation 
                    SET statut = 'confirmé'
                    WHERE id_reservation = %s
                """, [id_reservation])

                # Décrémenter le nombre de places disponibles
                cursor.execute("""
                    UPDATE voyage 
                    SET places_disponibles = places_disponibles - 1
                    WHERE numero_voyage = %s
                """, [reservation[2]])

                db.commit()
                messages.success(request, f"Ticket {numero_ticket} généré avec succès pour {reservation[1]}")
                return redirect('tickets_list')

        except Exception as e:
            db.rollback()
            messages.error(request, f"Erreur lors de la génération du ticket: {str(e)}")
            logger.error(f"Erreur génération ticket: {str(e)}")

    # Récupérer les réservations en attente avec les infos voyage
    cursor.execute("""
        SELECT r.id_reservation, r.nom_complet_client, v.numero_voyage, 
               v.date_depart, v.ville_arrivee, v.heure_depart,
               v.places_disponibles, b.nom_du_bus
        FROM reservation r
        JOIN voyage v ON r.id_voyage = v.id_voyage
        JOIN bus b ON v.bus_id = b.id_bus
        WHERE r.statut = 'en attente'
        ORDER BY v.date_depart, v.heure_depart
    """)
    reservations = cursor.fetchall()
    db.close()

    return render(request, 'admin/ticket/g.html', {
        'reservations': reservations,
        'now': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })




def tickets_list(request):
    if request.session.get('user_role') != 'admin':
        return redirect('login')
    db = get_connection()
    cursor = db.cursor()

    # Récupérer les tickets avec les informations nécessaires
    cursor.execute("""
        SELECT t.id_ticket, t.numero_du_ticket, t.nom_voyageur, t.numero_voyage, v.ville_depart, v.ville_arrivee, v.date_depart
        FROM ticket t
        JOIN voyage v ON t.numero_voyage = v.numero_voyage
        ORDER BY t.id_ticket DESC
    """)
    tickets = cursor.fetchall()
    db.close()

    return render(request, 'admin/ticket/liste_tickets.html', {'tickets': tickets})


# views.py


def delete_ticket(request, ticket_id):
    if request.session.get('user_role') != 'admin':
        return redirect('login')
    db = get_connection()
    cursor = db.cursor()

    try:
        # Récupérer les informations du ticket
        cursor.execute("""
            SELECT numero_voyage FROM ticket WHERE id_ticket = %s
        """, [ticket_id])
        ticket = cursor.fetchone()

        if not ticket:
            messages.error(request, "Ticket introuvable.")
            return redirect('tickets_list')

        numero_voyage = ticket[0]

        # Supprimer le ticket
        cursor.execute("""
            DELETE FROM ticket WHERE id_ticket = %s
        """, [ticket_id])

        # Mettre à jour le nombre de places disponibles dans le voyage
        cursor.execute("""
            UPDATE voyage SET places_disponibles = places_disponibles + 1
            WHERE numero_voyage = %s
        """, [numero_voyage])

        db.commit()
        messages.success(request, "Ticket supprimé avec succès et place réintégrée.")
    except Exception as e:
        db.rollback()
        messages.error(request, f"Erreur lors de la suppression du ticket : {str(e)}")
    finally:
        db.close()

    return redirect('tickets_list')

# views.py
def ticket_detail(request, ticket_id):
    if request.session.get('user_role') != 'admin':
        return redirect('login')
    db = get_connection()
    cursor = db.cursor()

    # Récupérer les détails du ticket à partir de l'ID du ticket
    cursor.execute("""
        SELECT t.numero_du_ticket, t.nom_voyageur, t.numero_voyage, v.ville_depart, v.ville_arrivee, v.date_depart, v.heure_depart
        FROM ticket t
        JOIN voyage v ON t.numero_voyage = v.numero_voyage
        WHERE t.id_ticket = %s
    """, [ticket_id])
    ticket = cursor.fetchone()

    if not ticket:
        raise Http404("Ticket introuvable.")

    db.close()

    # Passer les informations du ticket au template
    return render(request, 'admin/ticket/detail_ticket.html', {'ticket': ticket})






def list_voyages_client(request):
    if request.session.get('user_role') != 'client':
        return redirect('login')
    db = get_connection()
    cursor = db.cursor()
    cursor.execute("""
        SELECT v.id_voyage, b.nom_du_bus, v.ville_depart, v.ville_arrivee, v.date_depart,
               v.heure_depart, v.prix_ticket, v.places_disponibles,
               c.nom AS chauffeur_nom, v.statut, v.numero_voyage 
        FROM voyage v
        JOIN bus b ON v.bus_id = b.id_bus
        JOIN chauffeur c ON v.chauffeur_id = c.id_chauffeur
    """)
    voyages = cursor.fetchall()
    db.close()
    return render(request, 'client/liste_voyage.html', {'voyages': voyages})


def reserver_voyage(request, id_voyage):
    if request.session.get('user_role') != 'client':
        return redirect('login')

    id_client = request.session.get('id_client')
    nom_complet_client = request.session.get('nom_complet_client')
    email_client = request.session.get('email_client')

    # Sécurité : vérifier que les infos sont bien présentes
    if not id_client or not nom_complet_client or not email_client:
        messages.error(request, "Session expirée. Veuillez vous reconnecter.")
        return redirect('login')

    if request.method == 'POST':
        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO reservation (id_client, id_voyage, nom_complet_client, email_client)
                VALUES (%s, %s, %s, %s)
            """, [id_client, id_voyage, nom_complet_client, email_client])

        messages.success(request, "Réservation effectuée avec succès !")
        return redirect('list_voyages_client')


def client_tickets(request):
    # Vérification si l'utilisateur est connecté en tant que client
    if request.session.get('user_role') != 'client' or not request.session.get('id_client'):
        return redirect('login')

    client_id = request.session.get('id_client')

    if not client_id:
        return redirect('login')

    with connection.cursor() as cursor:
        try:
            # Requête modifiée pour filtrer les réservations confirmées
            cursor.execute("""
                SELECT DISTINCT t.numero_du_ticket, v.numero_voyage, t.nom_voyageur, 
                    t.date_creation, v.ville_depart, v.ville_arrivee,
                    v.date_depart, v.heure_depart, r.statut
                FROM ticket t
                JOIN reservation r ON t.nom_voyageur = r.nom_complet_client
                JOIN voyage v ON r.id_voyage = v.id_voyage
                WHERE r.id_client = %s AND r.statut = 'confirmé'
                ORDER BY t.date_creation DESC
            """, [client_id])

            
            tickets = cursor.fetchall()
            
        except Exception as e:
            tickets = []
            print(f"Erreur: {e}")

    return render(request, 'client/mes_tickets.html', {
        'tickets': tickets,
        'has_tickets': bool(tickets)
    })




def detail_ticket(request, numero_ticket):
    if request.session.get('user_role') != 'client' or not request.session.get('id_client'):
        return redirect('login')

    client_id = request.session.get('id_client')
    if not client_id:
        return redirect('login')

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT t.numero_du_ticket, v.numero_voyage, t.nom_voyageur, 
                   t.date_creation, v.ville_depart, v.ville_arrivee,
                   v.date_depart, v.heure_depart, r.statut
            FROM ticket t
            JOIN reservation r ON t.nom_voyageur = r.nom_complet_client
            JOIN voyage v ON r.id_voyage = v.id_voyage
            WHERE t.numero_du_ticket = %s AND r.id_client = %s
        """, [numero_ticket, client_id])

        ticket = cursor.fetchone()

    if not ticket:
        messages.error(request, "Ticket introuvable ou accès refusé.")
        return redirect('client_tickets')

    return render(request, 'client/t.html', {'ticket': ticket})






