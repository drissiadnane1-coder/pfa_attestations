from io import BytesIO
import textwrap

import qrcode
from django.core.files.base import ContentFile
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


def ecrire_texte_multiligne(pdf, texte, x, y, largeur_max=90, espace_ligne=18):
    lignes = textwrap.wrap(texte, width=largeur_max)

    for ligne in lignes:
        pdf.drawString(x, y, ligne)
        y -= espace_ligne

    return y


def generer_pdf_attestation(attestation, url_verification):
    buffer = BytesIO()

    pdf = canvas.Canvas(buffer, pagesize=A4)
    largeur, hauteur = A4

    demande = attestation.demande
    demandeur = demande.demandeur
    utilisateur = demandeur.utilisateur
    type_attestation = demande.type_attestation

    nom_complet = f"{utilisateur.first_name} {utilisateur.last_name}".strip()

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawCentredString(largeur / 2, hauteur - 80, "ATTESTATION")

    pdf.setFont("Helvetica", 12)

    y = hauteur - 150

    lignes_infos = [
        f"Numéro de l'attestation : {attestation.numero_unique}",
        f"Type d'attestation : {type_attestation.libelle}",
        f"Demandeur : {nom_complet}",
        f"Code interne : {demandeur.code_interne}",
        f"Structure : {demandeur.structure}",
        f"Date de génération : {attestation.date_generation.strftime('%d/%m/%Y %H:%M')}",
    ]

    for ligne in lignes_infos:
        pdf.drawString(80, y, ligne)
        y -= 25

    y -= 20

    texte = (
        f"Nous certifions que {nom_complet}, identifié par le code interne "
        f"{demandeur.code_interne}, appartenant à la structure {demandeur.structure}, "
        f"a obtenu le document suivant : {type_attestation.libelle}."
    )

    y = ecrire_texte_multiligne(pdf, texte, 80, y, largeur_max=85, espace_ligne=20)

    qr = qrcode.make(url_verification)
    qr_buffer = BytesIO()
    qr.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)

    qr_image = ImageReader(qr_buffer)

    pdf.drawImage(qr_image, largeur - 180, 100, width=100, height=100)

    pdf.setFont("Helvetica", 9)
    pdf.drawString(80, 80, "Ce document peut être vérifié via le QR code ou l'URL officielle de vérification.")
    pdf.drawString(80, 65, url_verification)

    pdf.showPage()
    pdf.save()

    buffer.seek(0)

    nom_fichier = f"{attestation.numero_unique}.pdf"
    return nom_fichier, ContentFile(buffer.getvalue())