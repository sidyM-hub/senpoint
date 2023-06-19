from django.shortcuts import render,HttpResponse
from django.contrib.auth.models import User
from .models import Etudiant
from email.mime.multipart import MIMEMultipart

from .forms import EtudiantForm
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
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



# Create your views here.

def accueil(request):
    etudiants = Etudiant.objects.all()
    return render(request, "pointme/accueil.html",{'etudiants':etudiants}) 
    # return render(request, "pointme/accueil.html") 


def base(request):
    etudiants = Etudiant.objects.all()
    return render(request, "pointme/base.html",{'etudiants':etudiants})
    # return render(request, "pointme/base.html")




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
                    response = redirect('accueil')
                    if 'messages' in request.COOKIES:
                        response.delete_cookie('messages')  # Supprimer le cookie existant s'il est présent
                    response.set_cookie("messages", "Connexion réussie.", max_age=604800)  # Exemple : le cookie expire dans 7 jours
                    return response
            messages.error(request, "Adresse e-mail ou mot de passe incorrect.")
        else:
            messages.error(request, "Adresse e-mail ou mot de passe incorrect.")

        return redirect('connexion')

    return render(request, 'pointme/connexion.html')




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

# def affiche_scan(request):
#     etudiant_scan = EtudiantScan.objects.last()  # Récupérer le dernier scan enregistré

#     context = {
#         'etudiant_scan': etudiant_scan
#     }
#     return render(request, 'pointme/affichescan.html', context)


from django.http import JsonResponse
from .models import EtudiantScan

def qr_scanner(request):
    if request.method == 'POST':
        qr_code_data = request.POST.get('qr_code_data')
        telephone = request.POST.get('telephone')
        
        # Enregistrer les informations du scan dans la base de données
        etudiant_scan = EtudiantScan.objects.create(qr_code_data=qr_code_data, telephone=telephone, date_scan=timezone.now())
        etudiant_scan.save()
        
        # Récupérer la date et l'heure du scan
        date_scan = etudiant_scan.date_scan.date()
        heure_scan = etudiant_scan.date_scan.time()
        
        # Afficher le numéro de téléphone extrait du QR code, la date et l'heure du scan
        context = {
            'telephone': telephone,
            'date_scan': date_scan,
            'heure_scan': heure_scan
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

        # Récupérer tous les pointages de l'étudiant correspondant au QR code
        pointages = EtudiantScan.objects.filter(qr_code_data=qr_code)

        # Préparer la réponse JSON
        response = {
            'valide': valide,
            'pointages': [{
                'etudiant__telephone': pointage.telephone,
                'date_pointage': pointage.date_scan.strftime('%Y-%m-%d'),
                'heure_pointage': pointage.date_scan.strftime('%H:%M:%S'),
            } for pointage in pointages]
        }

        return JsonResponse(response)

