from django.contrib import admin

# Register your models here.
from django.contrib import admin

# Register your models here.
from .models import Etudiant

@admin.register(Etudiant)
class AdminEtudiant(admin.ModelAdmin):
    list_display = ('nom','prenom','telephone','adresse_mail','password1','password2')