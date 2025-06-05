from app import create_app
from ng_runner import  iniciar_ngrok
from flasgger import  Flasgger

app = create_app()

if __name__ == '__main__':

    # iniciar_ngrok(puerto=5000)  # Lanza ngrok y muestra la URL

    # app.run(debug=True)
    # app.run(host='0.0.0.0', port=5000, debug=True)
    app.run(host='0.0.0.0', port=5000, ssl_context=('cert.pem', 'key.pem'))