from django.urls import path
from . import views
from .views import *
from pointme.views import accueil,inscription,deconnexion
# from .views import qr_scanner


from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('',views.inscription, name='inscription'),  
    path('accueil/',views.accueil, name='accueil'),  
    path('base/',views.base, name='base'),  
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', deconnexion, name='deconnexion'),
    path('ajout/', views.ajout, name='ajout'),
    path('qr_scanner/', views.qr_scanner, name='qr_scanner'),
    path('affiche/', views.affiche, name='affiche'),
    path('verifier_qr_code/', verifier_qr_code, name='verifier_qr_code'),
    path('afficheqrcode/', afficheqrcode, name='afficheqrcode'),
    path('recherche_etudiant/', views.recherche_etudiant, name='recherche_etudiant'),

     




]
