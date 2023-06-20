from django.shortcuts import render,HttpResponse
from django.contrib.auth.models import User
from .models import Etudiant
from email.mime.multipart import MIMEMultipart

from .forms import EtudiantForm
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login,logout
import os
from django.core.files import File
import qrcode
from django.conf import settings
import os
from .models import Etudiant
from .forms import AjoutEtudiantForm
from .utils import generateQrCode, send_email_with_qr_code
import cv2
from pyzbar import pyzbar
import qrcode
import numpy
import json



# Create your views here.

def accueil(request):
    etudiants = Etudiant.objects.all()
    return render(request, "pointme/accueil.html",{'etudiants':etudiants}) 
    # return render(request, "pointme/accueil.html") 


def base(request):
    etudiants = Etudiant.objects.all()
    return render(request, "pointme/base.html",{'etudiants':etudiants})
    # return render(request, "pointme/base.html")
    
def afficheqrcode(request):
    etudiants = Etudiant.objects.all()
    return render(request, "pointme/afficheqrcode.html",{'etudiants':etudiants}) 
    # return render(request, "pointme/accueil.html")     




def inscription(request):
    if request.method == 'POST':
        # Récupérer les données du formulaire
        nom = request.POST['nom']
        prenom = request.POST['prenom']
        adresse_mail = request.POST['adresse_mail']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        # Vérifier si les mots de passe correspondent
        if password1 != password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect('inscription')

        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(email=adresse_mail).exists():
            messages.error(request, "Cette adresse mail est déjà utilisée.")
            return redirect('inscription')

        # Créer l'utilisateur
        user = User.objects.create_user(username=adresse_mail, email=adresse_mail, password=password1)
        user.first_name = prenom
        user.last_name = nom
        user.save()

        # Authentifier l'utilisateur nouvellement créé
        user_auth = authenticate(request, username=adresse_mail, password=password1)
        if user_auth is not None:
            login(request, user_auth)
            messages.success(request, "Inscription réussie. Veuillez vous connecter.")
            return redirect('connexion')

    return render(request, 'pointme/inscription.html')







# def connexion(request):
#     if request.method == 'POST':
#         # Récupérer les données du formulaire
#         adresse_mail = request.POST['adresse_mail']
#         password1 = request.POST['password1']

#         # Récupérer les utilisateurs correspondant à l'adresse e-mail
#         users = User.objects.filter(email=adresse_mail)

#         if users.exists():
#             # Vérifier le mot de passe pour chaque utilisateur
#             for user in users:
#                 if user.check_password(password1):
#                     login(request, user)
#                     messages.success(request, "Connexion réussie.")
#                     response = redirect('accueil')
#                     response.set_cookie("messages", "Connexion réussie.", max_age=604800)  # Exemple : le cookie expire dans 7 jours
#                     return response
#             messages.error(request, "Adresse e-mail ou mot de passe incorrect.")
#         else:
#             messages.error(request, "Adresse e-mail ou mot de passe incorrect.")

#         return redirect('connexion')

#     return render(request, 'pointme/connexion.html')


def connexion(request):
    if request.method == 'POST':
        # Récupérer les données du formulaire
        adresse_mail = request.POST['adresse_mail']
        password1 = request.POST['password1']

        # Récupérer les utilisateurs correspondant à l'adresse e-mail
        users = User.objects.filter(email=adresse_mail)
        print(users)
        if users.exists():
            # Vérifier le mot de passe pour chaque utilisateur
            for user in users:
                if user.check_password(password1):
                    login(request, user)
                    response = redirect('qr_scanner')
                    if 'messages' in request.COOKIES:
                        response.delete_cookie('messages')  # Supprimer le cookie existant s'il est présent
                    response.set_cookie("messages", "Connexion réussie.", max_age=604800)  # Exemple : le cookie expire dans 7 jours
                    return response
            messages.error(request, "Adresse e-mail ou mot de passe incorrect.")
        else:
            messages.error(request, "Adresse e-mail ou mot de passe incorrect.")

        return redirect('connexion')

    return render(request, 'pointme/connexion.html')




def deconnexion(request):
    logout(request)
    response = redirect('connexion')
    response.delete_cookie('messages')  # Supprimer le cookie existant s'il est présent
    response.set_cookie("messages", "Déconnexion réussie.", max_age=604800)  # Exemple : le cookie expire dans 7 jours
    return response


def generateQrCode(data):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    full_name = f"{data['nom']} {data['prenom']} ({data['telephone']}, {data['adresse_mail']})"
    qr.add_data(full_name)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_file = f"{settings.MEDIA_ROOT}/qr_codes/{data['adresse_mail']}.png"
    img.save(img_file)
    return img_file



def ajout(request):
    etudiants = Etudiant.objects.all()

    if request.method == "POST":
        form = AjoutEtudiantForm(request.POST)

        if form.is_valid():
            etudiant = form.save(commit=False)
            etudiant.save()

            if 'image' in request.FILES:
                etudiant.image = request.FILES['image']
                etudiant.save()

            qr_code_data = {
                'nom': etudiant.nom,
                'prenom': etudiant.prenom,
                'telephone': etudiant.telephone,
                'adresse_mail': etudiant.adresse_mail
            }

            qr_code_path = generateQrCode(qr_code_data)
            etudiant.qr_code.save(os.path.basename(qr_code_path), File(open(qr_code_path, 'rb')))
            etudiant.save()

            # Envoyer l'e-mail avec le code QR à l'étudiant
            send_email_with_qr_code(etudiant, qr_code_path)

            messages.success(request, "L'étudiant a été créé avec succès !")
            return redirect('accueil')
        else:
            messages.error(request, "Erreur lors de la création de l'étudiant. Veuillez vérifier les informations.")
    else:
        form = AjoutEtudiantForm()
        etudiants = Etudiant.objects.all()

    return render(request, "pointme/ajout.html", {'form': form, 'etudiants': etudiants})




import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

def send_email_with_qr_code(etudiant, qr_code_path):
    # Configurer les informations d'authentification SMTP
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'scbakeli@gmail.com'
    smtp_password = 'wioeeaxuncqrmhqp'

    # Construire le message e-mail
    msg = MIMEMultipart()
    msg['From'] = 'scbakeli@gmail.com'
    msg['To'] = etudiant.adresse_mail
    msg['Subject'] = 'Votre code QR'

    # Ajouter le texte du message
    message_text = f"Cher {etudiant.prenom},\n\nVoici votre code QR :\n\n"
    msg.attach(MIMEText(message_text, 'plain'))

    # Ajouter l'image du code QR
    with open(qr_code_path, 'rb') as f:
        qr_image = MIMEImage(f.read())
    qr_image.add_header('Content-Disposition', 'attachment', filename='qr_code.png')
    msg.attach(qr_image)

    # Envoyer l'e-mail via SMTP
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)

    print("E-mail envoyé avec succès !")



from django.shortcuts import render
from django.utils import timezone
from .models import EtudiantScan
from django.shortcuts import render
from .models import EtudiantScan

def affiche(request):
    etudiants_scannes = EtudiantScan.objects.all()

    context = {
        'etudiants_scannes': etudiants_scannes
    }
    return render(request, "pointme/affiche.html", context)


from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Etudiant, EtudiantScan
from django.utils.timezone import now


from .models import EtudiantScan
from django.http import JsonResponse
from .models import EtudiantScan

def qr_scanner(request):
    if request.method == 'POST':
        qr_code_data = request.POST.get('qr_code_data')
        telephone = request.POST.get('telephone')

        # Vérifier si l'étudiant a déjà effectué un scan
        try:
            etudiant_scan = EtudiantScan.objects.get(telephone=telephone)
            etudiant_scan.date_scan = now().date()
            etudiant_scan.heure_scan = now().time()
            etudiant_scan.save()

            # Récupérer tous les scans d'étudiants
            etudiants_scannes = EtudiantScan.objects.all()

            # Afficher les informations mises à jour
            context = {
                'etudiants_scannes': etudiants_scannes
            }
            return render(request, 'pointme/qr_scanner.html', context)

        except EtudiantScan.DoesNotExist:
            # Enregistrer les informations du scan dans la base de données
            etudiant_scan = EtudiantScan.objects.create(qr_code_data=qr_code_data, telephone=telephone,
                                                        date_scan=now().date(), heure_scan=now().time())

            # Récupérer tous les scans d'étudiants
            etudiants_scannes = EtudiantScan.objects.all()

            # Afficher les informations
            context = {
                'etudiants_scannes': etudiants_scannes
            }
            return render(request, 'pointme/qr_scanner.html', context)

    return render(request, 'pointme/qr_scanner.html')


def verifier_qr_code(request):
    if request.method == 'POST':
        qr_code = request.POST.get('qr_code')

        # Vérifier si le QR code existe dans la base de données
        try:
            etudiant_scan = EtudiantScan.objects.get(qr_code_data=qr_code)
            valide = True
        except EtudiantScan.DoesNotExist:
            valide = False

        # Récupérer tous les scans d'étudiants
        etudiants_scannes = EtudiantScan.objects.all()

        # Préparer la réponse JSON
        response = {
            'valide': valide,
            'etudiants_scannes': [{
                'telephone': etudiant.telephone,
                'date_pointage': etudiant.date_scan.strftime('%Y-%m-%d'),
                'heure_pointage': etudiant.heure_scan.strftime('%H:%M:%S'),
            } for etudiant in etudiants_scannes]
        }

        # Mettre à jour les informations existantes si l'étudiant a déjà effectué un scan
        if valide:
            etudiant_scan.telephone = request.POST.get('telephone')
            etudiant_scan.date_scan = now().date()
            etudiant_scan.heure_scan = now().time()
            etudiant_scan.save()

        return JsonResponse(response)


from django.shortcuts import render, get_object_or_404
from .models import Etudiant

def recherche_etudiant(request):
    etudiant = None
    qr_code_url = None

    if request.method == 'POST':
        telephone = request.POST.get('telephone')
        etudiant = Etudiant.objects.filter(telephone=telephone).first()

        if etudiant:
            qr_code_url = etudiant.qr_code.url
            messages.success(request, "Étudiant trouvé avec le numéro de téléphone spécifié.")
        else:
            messages.error(request, "Aucun étudiant trouvé avec ce numéro de téléphone.")

    return render(request, 'pointme/recherche_etudiant.html', {'etudiant': etudiant, 'qr_code_url': qr_code_url})




