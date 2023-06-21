from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone


class Etudiant(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, null=True)
    nom = models.CharField(max_length=100, null=True)
    prenom = models.CharField(max_length=100, null=True)
    telephone = models.CharField(max_length=20)
    adresse_mail = models.EmailField(max_length=100, unique=True, null=True)
    qr_code = models.ImageField(upload_to='qr_codes/', null=True)  
    image = models.ImageField(upload_to='etudiant_images/', null=True, blank=True)
    date_inscription = models.DateTimeField(auto_now_add=True)
    password1 = models.CharField(max_length=128, blank=True, null=True)
    password2 = models.CharField(max_length=128, blank=True, null=True)
    qr_code_data = models.CharField(max_length=200, default='')
    date_scan = models.DateField(default=timezone.now)
    heure_scan = models.TimeField(default=timezone.now)

    def __str__(self):
        return f"{self.nom} {self.prenom}"

    def save(self, *args, **kwargs):
        if not self.pk:  
            User = get_user_model()
            user = User.objects.create_user(username=self.adresse_mail, email=self.adresse_mail)
            self.user = user
        super().save(*args, **kwargs)


# from django.db import models

    
# class EtudiantScan(models.Model):
#     etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE, default=None)
#     qr_code_data = models.CharField(max_length=200)
#     telephone = models.CharField(max_length=20)
#     date_scan = models.DateField()
#     heure_scan = models.TimeField()

#     def __str__(self):
#         return f"Scan de l'étudiant le {self.date_scan} à {self.heure_scan}"
