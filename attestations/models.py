import uuid
from django.db import models
from django.conf import settings
from accounts.models import ProfilDemandeur


class TypeAttestation(models.Model):
    libelle = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    statut = models.BooleanField(default=True)

    def __str__(self):
        return self.libelle


class ModeleAttestation(models.Model):
    type_attestation = models.ForeignKey(
        TypeAttestation,
        on_delete=models.CASCADE,
        related_name='modeles'
    )

    nom_modele = models.CharField(max_length=100)
    contenu = models.TextField()
    version = models.PositiveIntegerField(default=1)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom_modele} - version {self.version}"


class DemandeAttestation(models.Model):
    class StatutDemande(models.TextChoices):
        EN_ATTENTE = 'EN_ATTENTE', 'En attente'
        EN_TRAITEMENT = 'EN_TRAITEMENT', 'En traitement'
        VALIDEE = 'VALIDEE', 'Validée'
        REJETEE = 'REJETEE', 'Rejetée'

    demandeur = models.ForeignKey(
        ProfilDemandeur,
        on_delete=models.CASCADE,
        related_name='demandes'
    )

    type_attestation = models.ForeignKey(
        TypeAttestation,
        on_delete=models.CASCADE,
        related_name='demandes'
    )

    date_depot = models.DateTimeField(auto_now_add=True)

    statut = models.CharField(
        max_length=20,
        choices=StatutDemande.choices,
        default=StatutDemande.EN_ATTENTE
    )

    commentaire = models.TextField(blank=True, null=True)
    motif_rejet = models.TextField(blank=True, null=True)
    date_traitement = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Demande {self.id} - {self.demandeur}"


class Attestation(models.Model):
    class StatutAttestation(models.TextChoices):
        VALIDE = 'VALIDE', 'Valide'
        ANNULEE = 'ANNULEE', 'Annulée'
        EXPIREE = 'EXPIREE', 'Expirée'

    demande = models.OneToOneField(
        DemandeAttestation,
        on_delete=models.CASCADE,
        related_name='attestation'
    )

    numero_unique = models.CharField(max_length=100, unique=True)
    date_generation = models.DateTimeField(auto_now_add=True)

    identifiant_verification = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
    )

    statut = models.CharField(
        max_length=20,
        choices=StatutAttestation.choices,
        default=StatutAttestation.VALIDE
    )

    date_expiration = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.numero_unique


class FichierPDF(models.Model):
    attestation = models.OneToOneField(
        Attestation,
        on_delete=models.CASCADE,
        related_name='fichier_pdf'
    )

    nom_fichier = models.CharField(max_length=150)
    chemin_fichier = models.FileField(upload_to='attestations/pdf/')
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom_fichier


class QRCodeAttestation(models.Model):
    attestation = models.OneToOneField(
        Attestation,
        on_delete=models.CASCADE,
        related_name='qr_code'
    )

    url_verification = models.URLField(max_length=255)
    date_generation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"QR Code - {self.attestation.numero_unique}"


class ArchiveAttestation(models.Model):
    attestation = models.OneToOneField(
        Attestation,
        on_delete=models.CASCADE,
        related_name='archive'
    )

    date_archivage = models.DateTimeField(auto_now_add=True)
    raison_archivage = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Archive - {self.attestation.numero_unique}"


class VerificationAttestation(models.Model):
    class StatutVerification(models.TextChoices):
        VALIDE = 'VALIDE', 'Valide'
        ANNULEE = 'ANNULEE', 'Annulée'
        EXPIREE = 'EXPIREE', 'Expirée'
        INTROUVABLE = 'INTROUVABLE', 'Introuvable'

    attestation = models.ForeignKey(
        Attestation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verifications'
    )

    date_verification = models.DateTimeField(auto_now_add=True)
    adresse_ip = models.GenericIPAddressField(blank=True, null=True)

    resultat = models.CharField(
        max_length=20,
        choices=StatutVerification.choices
    )

    def __str__(self):
        return f"Vérification - {self.resultat}"


class JournalAction(models.Model):
    class TypeActionJournal(models.TextChoices):
        CONNEXION = 'CONNEXION', 'Connexion'
        VALIDATION = 'VALIDATION', 'Validation'
        REJET = 'REJET', 'Rejet'
        GENERATION = 'GENERATION', 'Génération'
        TELECHARGEMENT = 'TELECHARGEMENT', 'Téléchargement'
        VERIFICATION = 'VERIFICATION', 'Vérification'
        ANNULATION = 'ANNULATION', 'Annulation'
        ARCHIVAGE = 'ARCHIVAGE', 'Archivage'

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actions'
    )

    attestation = models.ForeignKey(
        Attestation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='journaux'
    )

    action = models.CharField(
        max_length=30,
        choices=TypeActionJournal.choices
    )

    date_heure = models.DateTimeField(auto_now_add=True)
    objet_concerne = models.CharField(max_length=100, blank=True, null=True)
    detail_contextuel = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.action} - {self.date_heure}"