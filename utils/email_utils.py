# ==========================================================
# email_utils.py - Kirim notifikasi hasil quiz via email (SMTP)
# Gunakan Gmail App Password (bukan password akun biasa).
# ==========================================================
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


def send_result_email(config, to_email, student_name, module, score, status, pdf_bytes=None, pdf_filename="laporan.pdf"):
    """
    config: dict dari storage.load_email_config()
    Return: (success: bool, message: str)
    """
    if not config.get("enabled"):
        return False, "Fitur email belum diaktifkan oleh guru."
    if not config.get("sender_email") or not config.get("app_password"):
        return False, "Konfigurasi email (sender/app password) belum lengkap."
    if not to_email:
        return False, "Siswa tidak punya alamat email."

    try:
        msg = MIMEMultipart()
        msg["From"] = config["sender_email"]
        msg["To"] = to_email
        msg["Subject"] = f"Hasil Quiz: {module}"

        if status == "Menunggu Review":
            body = (
                f"Halo {student_name},\n\n"
                f"Jawaban kamu untuk modul \"{module}\" sudah kami terima.\n"
                f"Sebagian soal (essay) masih menunggu penilaian guru.\n"
                f"Nilai sementara: {score}/100\n\n"
                f"Kamu akan mendapat email lagi setelah nilai final keluar.\n\n"
                f"Semangat belajar! 🎓"
            )
        else:
            body = (
                f"Halo {student_name},\n\n"
                f"Hasil quiz kamu untuk modul \"{module}\" sudah keluar.\n"
                f"Nilai: {score}/100\n\n"
                f"Laporan lengkap terlampir. Terus semangat belajar coding! 🎓"
            )

        msg.attach(MIMEText(body, "plain"))

        if pdf_bytes:
            part = MIMEApplication(pdf_bytes, Name=pdf_filename)
            part["Content-Disposition"] = f'attachment; filename="{pdf_filename}"'
            msg.attach(part)

        with smtplib.SMTP(config.get("smtp_host", "smtp.gmail.com"), config.get("smtp_port", 587)) as server:
            server.starttls()
            server.login(config["sender_email"], config["app_password"])
            server.send_message(msg)

        return True, f"Email berhasil dikirim ke {to_email}"
    except Exception as e:
        return False, f"Gagal mengirim email: {e}"


def send_test_email(config, to_email):
    return send_result_email(
        config, to_email,
        student_name="Test User",
        module="Test Module",
        score=100,
        status="Selesai",
        pdf_bytes=None,
    )
