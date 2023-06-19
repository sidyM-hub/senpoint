from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Etudiant

class EtudiantForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Etudiant
        fields = ['nom', 'prenom', 'telephone', 'adresse_mail', 'image', 'password1', 'password2']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'required': False}),
        }

class AjoutEtudiantForm(forms.ModelForm):
    class Meta:
        model = Etudiant
        fields = ['nom', 'prenom', 'telephone', 'adresse_mail', 'image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'required': False}),
        }
