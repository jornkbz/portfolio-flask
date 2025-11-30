import os
from flask import Flask, render_template, request, redirect, url_for
from flask_mail import Mail, Message
from dotenv import load_dotenv

# Cargar variables
load_dotenv()
#print("--- DEBUG ---")
#print("Usuario:", os.getenv('MAIL_USER'))
#print("Pass:", os.getenv('MAIL_PASS'))
#print("-------------")
app = Flask(__name__)

# --- CONFIGURACIÓN DESDE .ENV ---

# 1. Servidor (String)
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')

# 2. Puerto (IMPORTANTE: Convertir a Entero)
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))

# 3. Seguridad (IMPORTANTE: Convertir String a Booleano)
# Explicación: os.getenv devuelve el texto "True".
# La comparación "True" == "True" devuelve el valor lógico True.
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL') == 'True'

# 4. Credenciales
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USER')
app.config['MAIL_RECIPIENT'] = os.getenv('MAIL_RECIPIENT')
mail = Mail(app)

# ... (El resto de tus rutas index y mail siguen igual) ...

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mail', methods=['GET', 'POST'])
def send_mail():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        msg = Message(
            'Hola Jose, tienes un nuevo contacto desde la web:',
            body=f'Nombre: {name} \nCorreo: <{email}> \n\nEscribió: \n\n{message}',
            sender=app.config['MAIL_USERNAME'],
            recipients=[app.config['MAIL_RECIPIENT']],
            reply_to=email          
        )
        try:
            mail.send(msg)
            return render_template('send_mail.html')
        except Exception as e:
            return f"Error al enviar: {e}"

    return redirect(url_for('index'))

if __name__ == '__main__':
    # Leemos la variable y la comparamos con el texto 'True'
    # Si en el .env pone True, esto será verdadero. Si pone False o no existe, será falso.
    debug_mode = os.getenv('FLASK_DEBUG') == 'True'
    
    app.run(debug=debug_mode, host='0.0.0.0')