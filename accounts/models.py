from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    class StatutUtilisateur(models.TextChoices):
        ACTIF = 'ACTIF', 'Actif'
        INACTIF = 'INACTIF', 'Inactif'
        BLOQUE = 'BLOQUE', 'Bloqué'

    class RoleUtilisateur(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrateur'
        AGENT_ADMINISTRATIF = 'AGENT_ADMINISTRATIF', 'Agent administratif'
        DEMANDEUR = 'DEMANDEUR', 'Demandeur'

    role = models.CharField(
        max_length=30,
        choices=RoleUtilisateur.choices,
        default=RoleUtilisateur.DEMANDEUR
    )

    statut = models.CharField(
        max_length=20,
        choices=StatutUtilisateur.choices,
        default=StatutUtilisateur.ACTIF
    )

    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} - {self.role}"


class Administrateur(CustomUser):
    class Meta:
        proxy = True
        verbose_name = "Administrateur"
        verbose_name_plural = "Administrateurs"


class AgentAdministratif(CustomUser):
    class Meta:
        proxy = True
        verbose_name = "Agent administratif"
        verbose_name_plural = "Agents administratifs"


class Demandeur(CustomUser):
    class Meta:
        proxy = True
        verbose_name = "Demandeur"
        verbose_name_plural = "Demandeurs"


class ProfilDemandeur(models.Model):
    utilisateur = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profil_demandeur'
    )

    code_interne = models.CharField(max_length=50, unique=True)
    date_naissance = models.DateField(blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    structure = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Profil de {self.utilisateur.username}"
