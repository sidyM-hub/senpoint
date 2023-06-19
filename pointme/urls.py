from django.urls import path
from . import views
from .views import *
from pointme.views import accueil,inscription
from .views import verifier_qr_code


from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('',views.inscription, name='inscription'),  
    path('accueil/',views.accueil, name='accueil'),  
    path('base/',views.base, name='base'),  
    path('connexion/', views.connexion, name='connexion'),
    path('ajout/', views.ajout, name='ajout'),
    path('qr_scanner/', views.qr_scanner, name='qr_scanner'),
    # path('affichescan/', views.affiche_scan, name='affiche_scan'),
    path('verifier_qr_code/', verifier_qr_code, name='verifier_qr_code'),



]
