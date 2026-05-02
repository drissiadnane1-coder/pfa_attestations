from django.contrib import admin
from .models import (
    TypeAttestation,
    ModeleAttestation,
    DemandeAttestation,
    Attestation,
    FichierPDF,
    QRCodeAttestation,
    ArchiveAttestation,
    VerificationAttestation,
    JournalAction,
)


admin.site.register(TypeAttestation)
admin.site.register(ModeleAttestation)
admin.site.register(DemandeAttestation)
admin.site.register(Attestation)
admin.site.register(FichierPDF)
admin.site.register(QRCodeAttestation)
admin.site.register(ArchiveAttestation)
admin.site.register(VerificationAttestation)
admin.site.register(JournalAction)