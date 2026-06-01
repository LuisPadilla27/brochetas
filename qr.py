import qrcode
import http.server
import threading
import socket
import os

# ── CONFIGURACIÓN ────────────────────────────────────────────────
WHATSAPP_NUMBER = "526183252833"          # Ej: 5491112345678 (sin + ni espacios)
WHATSAPP_MESSAGE = "Hola, me gustaría hacer un pedido para recojer en el local"
PORT = 8080
HTML_FILE = "landing.html"
QR_OUTPUT = "qr_whatsapp.png"
# ─────────────────────────────────────────────────────────────────


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()


def start_server():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    handler = http.server.SimpleHTTPRequestHandler
    httpd = http.server.HTTPServer(("", PORT), handler)
    print(f"  Servidor corriendo en http://0.0.0.0:{PORT}")
    httpd.serve_forever()


def generate_qr(url: str):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#25D366", back_color="white")
    img.save(QR_OUTPUT)
    print(f"  QR guardado en: {QR_OUTPUT}")


def patch_landing_page():
    """Reemplaza TUNUMERO en el HTML con el número configurado."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), HTML_FILE)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if "TUNUMERO" in content:
        from urllib.parse import quote
        wa_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={quote(WHATSAPP_MESSAGE)}"
        content = content.replace(
            f"https://wa.me/TUNUMERO?text=Hola%2C%20me%20gustar%C3%ADa%20obtener%20m%C3%A1s%20informaci%C3%B3n",
            wa_url,
        )
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  HTML actualizado con número: {WHATSAPP_NUMBER}")


def main():
    if WHATSAPP_NUMBER == "TUNUMERO":
        print("⚠  Cambia WHATSAPP_NUMBER en este script antes de continuar.")
        return

    print("\n=== Generador de QR para WhatsApp Business ===\n")

    # Actualiza el HTML con el número real
    patch_landing_page()

    # Inicia servidor en hilo secundario
    t = threading.Thread(target=start_server, daemon=True)
    t.start()

    local_ip = get_local_ip()
    landing_url = f"http://{local_ip}:{PORT}/{HTML_FILE}"
    print(f"  URL de la página: {landing_url}")

    # Genera el QR apuntando a la página local
    generate_qr(landing_url)

    print("\n  Escanea el QR con tu celular (debe estar en la misma red Wi-Fi).")
    print("  Presiona Ctrl+C para detener el servidor.\n")

    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        print("\nServidor detenido.")


if __name__ == "__main__":
    main()
