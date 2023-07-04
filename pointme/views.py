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
from qrcode import QRCode

from django.shortcuts import render, get_object_or_404
from django.utils.timezone import now
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.timezone import now
from .models import Etudiant
from django.http import JsonResponse, HttpResponse
from .models import Etudiant
import datetime
from datetime import date, datetime



from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Etudiant, EtudiantScan

from django.shortcuts import render, redirect
from .models import Etudiant
import json


from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime
import cv2
from pyzbar.pyzbar import decode



from django.core.exceptions import ObjectDoesNotExist
from .models import Etudiant, EtudiantScan
from django.http import JsonResponse
import json


from json import JSONDecodeError

import json
from json.decoder import JSONDecodeError

from django.shortcuts import get_object_or_404

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from datetime import datetime
from .models import Etudiant, EtudiantScan
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from datetime import datetime
from django.shortcuts import render, get_object_or_404

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

from qrcode import QRCode


def generateQrCode(data, etudiant_id):
    qr = QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    full_name = f"{data['nom']} {data['prenom']} ({data['telephone']}, {data['adresse_mail']})"
    json_object = json.dumps(data, indent=4)
    qr.add_data(json_object)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_file = f"qr_{etudiant_id}.png"  # Utilisation de l'ID de l'étudiant dans le nom du fichier
    img.save(img_file)
    return img_file, data['nom'], data['prenom'], data['telephone'], data['adresse_mail']



def ajout(request):
    etudiants = Etudiant.objects.all()

    if request.method == "POST":
        form = AjoutEtudiantForm(request.POST)

        if form.is_valid():
            etudiant = form.save(commit=False)
            etudiant.save()

            # Obtenir l'ID de l'étudiant ajouté
            etudiant_id = etudiant.id

            if 'image' in request.FILES:
                etudiant.image = request.FILES['image']
                etudiant.save()

            qr_code_data = {
                'id': etudiant_id,  # Ajout de l'ID de l'étudiant
                'nom': etudiant.nom,
                'prenom': etudiant.prenom,
                'telephone': etudiant.telephone,
                'adresse_mail': etudiant.adresse_mail
            }

            qr_code_path, nom, prenom, telephone, adresse_mail = generateQrCode(qr_code_data, etudiant_id)
            etudiant.qr_code.save(os.path.basename(qr_code_path), File(open(qr_code_path, 'rb')))
            
            etudiant.qr_code_data = {
                'id': etudiant_id,  # Ajout de l'ID de l'étudiant
                'nom': nom,
                'prenom': prenom,
                'telephone': telephone,
                'adresse_mail': adresse_mail
            }
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
from django.shortcuts import render


# def affiche(request):
#     etudiants_scannes = EtudiantScan.objects.all()

#     context = {
#         'etudiants_scannes': etudiants_scannes
#     }
#     return render(request, "pointme/affiche.html", context)







# def affichage(request):
#     etudiants_authentifies = Etudiant.objects.filter(authentifie=True)
#     return render(request, 'pointme/affichage.html', {'etudiants_authentifies': etudiants_authentifies})





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

from datetime import datetime
from django.http import JsonResponse
import json

def qr_scanner(request):
    if request.method == "POST":
        data = json.loads(request.body)
        print(data)

        etudiant_id = data.get('id', '')
        nom = data.get('nom', '')
        prenom = data.get('prenom', '')
        telephone = data.get('telephone', '')
        adresse_mail = data.get('adresse_mail', '')

        if not (etudiant_id and nom and prenom and telephone and adresse_mail):
            data = {
                'success': False,
                'message': "Code QR invalide. Veuillez scanner un code QR valide contenant toutes les informations nécessaires."
            }
            return JsonResponse(data)

        # Effectuer les opérations spécifiques en utilisant l'ID de l'étudiant
        # Par exemple, récupérer l'étudiant à partir de l'ID
        # etudiant = Etudiant.objects.get(id=etudiant_id)

        etudiant_scan = EtudiantScan.objects.create(
            nom=nom,
            prenom=prenom,
            telephone=telephone,
            adresse_mail=adresse_mail
        )

        now = datetime.now()
        date_scan = now.strftime("%d/%m/%Y")
        heure_scan = now.strftime("%H:%M:%S")

        data = {
            'success': True,
            'etudiant': {
                'id': etudiant_scan.id,
                'nom': etudiant_scan.nom,
                'prenom': etudiant_scan.prenom,
                'telephone': etudiant_scan.telephone,
                'adresse_mail': etudiant_scan.adresse_mail
            },
            'date_scan': date_scan,
            'heure_scan': heure_scan
        }
        return JsonResponse(data)

    return render(request, "pointme/qr_scanner.html")


