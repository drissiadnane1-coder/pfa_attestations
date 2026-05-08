import uuid

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import (
    TypeAttestation,
    DemandeAttestation,
    Attestation,
    FichierPDF,
    QRCodeAttestation,
    JournalAction,
    VerificationAttestation,
)

from accounts.models import ProfilDemandeur
from .models import (
    TypeAttestation,
    DemandeAttestation,
    Attestation,
    FichierPDF,
    QRCodeAttestation,
    JournalAction,
)
from .utils import generer_pdf_attestation


@login_required
def deposer_demande(request):
    if request.user.role != 'DEMANDEUR':
        return redirect('redirect_by_role')

    types = TypeAttestation.objects.filter(statut=True)

    try:
        profil = request.user.profil_demandeur
    except ProfilDemandeur.DoesNotExist:
        return render(request, 'demandeur/deposer_demande.html', {
            'types': types,
            'error': "Votre profil demandeur n'existe pas."
        })

    if request.method == 'POST':
        type_id = request.POST.get('type_attestation')
        commentaire = request.POST.get('commentaire')

        type_attestation = get_object_or_404(TypeAttestation, id=type_id, statut=True)

        DemandeAttestation.objects.create(
            demandeur=profil,
            type_attestation=type_attestation,
            commentaire=commentaire
        )

        return render(request, 'demandeur/deposer_demande.html', {
            'types': types,
            'message': 'Votre demande a été envoyée avec succès.'
        })

    return render(request, 'demandeur/deposer_demande.html', {
        'types': types
    })


@login_required
def mes_demandes(request):
    if request.user.role != 'DEMANDEUR':
        return redirect('redirect_by_role')

    try:
        profil = request.user.profil_demandeur
    except ProfilDemandeur.DoesNotExist:
        demandes = []
    else:
        demandes = DemandeAttestation.objects.filter(
            demandeur=profil
        ).order_by('-date_depot')

    return render(request, 'demandeur/mes_demandes.html', {
        'demandes': demandes
    })


@login_required
def demandes_en_attente(request):
    if request.user.role != 'AGENT_ADMINISTRATIF':
        return redirect('redirect_by_role')

    demandes = DemandeAttestation.objects.filter(
        statut=DemandeAttestation.StatutDemande.EN_ATTENTE
    ).order_by('-date_depot')

    return render(request, 'agent/demandes_en_attente.html', {
        'demandes': demandes
    })


@login_required
def detail_demande(request, demande_id):
    if request.user.role != 'AGENT_ADMINISTRATIF':
        return redirect('redirect_by_role')

    demande = get_object_or_404(DemandeAttestation, id=demande_id)

    return render(request, 'agent/detail_demande.html', {
        'demande': demande
    })


@login_required
def valider_demande(request, demande_id):
    if request.user.role != 'AGENT_ADMINISTRATIF':
        return redirect('redirect_by_role')

    demande = get_object_or_404(DemandeAttestation, id=demande_id)

    demande.statut = DemandeAttestation.StatutDemande.VALIDEE
    demande.date_traitement = timezone.now()
    demande.save()

    attestation, created = Attestation.objects.get_or_create(
        demande=demande,
        defaults={
            'numero_unique': f"ATT-{timezone.now().year}-{uuid.uuid4().hex[:8].upper()}",
            'statut': Attestation.StatutAttestation.VALIDE,
        }
    )

    url_verification = request.build_absolute_uri(
        f"/verification/{attestation.identifiant_verification}/"
    )

    QRCodeAttestation.objects.get_or_create(
        attestation=attestation,
        defaults={
            'url_verification': url_verification
        }
    )

    nom_fichier, fichier_pdf = generer_pdf_attestation(
        attestation,
        url_verification
    )

    fichier_obj, fichier_created = FichierPDF.objects.get_or_create(
        attestation=attestation,
        defaults={
            'nom_fichier': nom_fichier
        }
    )

    if fichier_created or not fichier_obj.chemin_fichier:
        fichier_obj.chemin_fichier.save(nom_fichier, fichier_pdf)
        fichier_obj.save()

    JournalAction.objects.create(
        utilisateur=request.user,
        attestation=attestation,
        action=JournalAction.TypeActionJournal.VALIDATION,
        objet_concerne='DemandeAttestation',
        detail_contextuel=(
            f"Demande {demande.id} validée et attestation "
            f"{attestation.numero_unique} générée."
        )
    )

    return redirect('demandes_en_attente')


@login_required
def rejeter_demande(request, demande_id):
    if request.user.role != 'AGENT_ADMINISTRATIF':
        return redirect('redirect_by_role')

    demande = get_object_or_404(DemandeAttestation, id=demande_id)

    if request.method == 'POST':
        motif_rejet = request.POST.get('motif_rejet')

        demande.statut = DemandeAttestation.StatutDemande.REJETEE
        demande.motif_rejet = motif_rejet
        demande.date_traitement = timezone.now()
        demande.save()

        JournalAction.objects.create(
            utilisateur=request.user,
            action=JournalAction.TypeActionJournal.REJET,
            objet_concerne='DemandeAttestation',
            detail_contextuel=(
                f"Demande {demande.id} rejetée. "
                f"Motif : {motif_rejet}"
            )
        )

        return redirect('demandes_en_attente')

    return render(request, 'agent/rejeter_demande.html', {
        'demande': demande
    })


def verifier_attestation(request, identifiant):
    attestation = Attestation.objects.filter(
        identifiant_verification=identifiant
    ).first()

    if attestation is None:
        return render(request, 'verification/resultat_verification.html', {
            'resultat': 'INTROUVABLE',
            'message': "Aucune attestation ne correspond à cet identifiant.",
            'attestation': None
        })

    VerificationAttestation.objects.create(
        attestation=attestation,
        resultat=attestation.statut,
        adresse_ip=request.META.get('REMOTE_ADDR')
    )

    return render(request, 'verification/resultat_verification.html', {
        'resultat': attestation.statut,
        'message': "Attestation trouvée.",
        'attestation': attestation
    })