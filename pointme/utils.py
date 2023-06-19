import qrcode
from PIL import Image
from email.mime.multipart import MIMEMultipart
import io
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib


def generateQrCode(qr_code_data):
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=5
    )
    qr.add_data(qr_code_data)
    qr.make(fit=True)

    qr_image = qr.make_image(fill='black', back_color='white')
    image_buffer = io.BytesIO()
    qr_image.save(image_buffer, format='PNG')
    return image_buffer

def send_email_with_qr_code(etudiant, qr_code_path):
    # Configurer les informations d'authentification SMTP
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'scbakeli@gmail.com'
    smtp_password = 'wioeeaxuncqrmhqp'

    # Construire le message e-mail
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = etudiant.adresse_mail
    msg['Subject'] = 'Votre code QR'

    # Ajouter le texte du message
    message_text = f"Cher {etudiant.prenom},\n\nVoici votre code QR :\n\n"
    msg.attach(MIMEText(message_text, 'plain'))

    # Ajouter l'image du code QR
    with open(qr_code_path, 'rb') as f:
        qr_image = MIMEImage(f.read())
    qr_image.add_header('Content-Disposition', 'attachment', filename='qr_code.png')
    msg.attach(qr_image)

    # Envoyer l'e-mail via SMTP
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)

    print("E-mail envoyé avec succès !")
