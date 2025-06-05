import subprocess
import time
import requests
import atexit

ngrok_process = None  # Global para poder terminarlo luego

def iniciar_ngrok(puerto=5000):
    global ngrok_process

    try:
        # Ejecutar ngrok como proceso en segundo plano
        # ngrok_process = subprocess.Popen(["ngrok", "http", str(puerto)])
        ngrok_process = subprocess.Popen(["ngrok", "http", f"https://localhost:{puerto}"])
        print("🚀 Iniciando Ngrok...")

        # Asegurar que se cierre al terminar la app
        atexit.register(cerrar_ngrok)

        # Esperar a que se levante el túnel
        time.sleep(2)

        # Obtener la URL pública
        response = requests.get("http://localhost:4040/api/tunnels")
        tunnels = response.json()['tunnels']
        public_url = tunnels[0]['public_url']
        print(f"🔗 Tu API Flask está disponible públicamente en: {public_url}")

    except Exception as e:
        print("❌ Error al iniciar Ngrok:", e)

def cerrar_ngrok():
    global ngrok_process
    if ngrok_process:
        print("🛑 Cerrando Ngrok...")
        ngrok_process.terminate()
