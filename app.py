import os
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold # <--- NUEVO
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_mail import Mail, Message
from dotenv import load_dotenv

# Cargar variables
load_dotenv()

app = Flask(__name__)

# --- CONFIGURACIÓN EMAIL (INTACTA) ---
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT'))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USER')
app.config['MAIL_RECIPIENT'] = os.getenv('MAIL_RECIPIENT')

mail = Mail(app)

# --- CONFIGURACIÓN GEMINI (NUEVO) ---
# Configura la API Key obtenida del .env
#genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
# --- DEBUG: VER QUÉ MODELOS TENGO DISPONIBLES ---
#print("--- MODELOS DISPONIBLES ---")
#for m in genai.list_models():
#    if 'generateContent' in m.supported_generation_methods:
#        print(m.name)
#print("---------------------------")

# Inicializamos el modelo (Flash es rápido y gratis)
# model = genai.GenerativeModel('models/gemini-2.0-flash')

# --- CONFIGURACIÓN GEMINI AVANZADA ---
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Usamos el modelo que te funcionó (2.0 Flash)
model = genai.GenerativeModel('models/gemini-2.5-flash-lite')

# Configuración de seguridad: PERMITIR TODO (Para que no se asuste con el rol de hacker)
safety_settings = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}


# Función auxiliar para leer tu "memoria" (CV)
def get_context():
    try:
        # Intenta leer el archivo linkedin_data.txt
        with open('linkedin_data.txt', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Error: No se encontró el archivo de datos (linkedin_data.txt)."

# --- RUTAS ---

@app.route('/')
def index():
    return render_template('index.html') # Asumo que aquí es donde tienes home.html renombrado o incluido

# Ruta para el envío de correos (INTACTA)
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

# --- NUEVA RUTA: ORACLE AI (GEMINI) ---
@app.route('/ask_oracle', methods=['POST'])
def ask_oracle():
    data = request.get_json()
    user_question = data.get('question')
    context_data = get_context()
    
    # Prompt (Mismo que tenías)
    prompt = f"""
    Actúa como 'JCP_SYSTEM', una IA asistente del portafolio de José Cabezas Pulgarín.
    
    INFORMACIÓN DE CONTEXTO:
    {context_data}
    
    PREGUNTA DEL USUARIO:
    {user_question}
    
    INSTRUCCIONES:
    1. Responde SOLO basándote en el contexto.
    2. Tono: Hacker ético, profesional, breve.
    3. Si preguntan algo fuera de lugar o confidencial, di: "Protocolo de seguridad activado. Acceso denegado."
    """

    try:
        # Enviamos la configuración de seguridad para que sea más permisivo
        response = model.generate_content(
            prompt, 
            safety_settings=safety_settings
        )
        
        # Intentamos leer el texto. Si fue bloqueado, esto fallará y saltará al 'except ValueError'
        return jsonify({'answer': response.text})
        
    except ValueError:
        # Esto ocurre cuando Gemini bloquea la respuesta por seguridad
        return jsonify({'answer': "⚠️ ALERT: La consulta ha activado los filtros de seguridad neuronal. Acceso restringido."})
        
    except Exception as e:
        # Cualquier otro error real del servidor
        print(f"Error Gemini: {e}")
        return jsonify({'answer': "SYSTEM_FAILURE: Error de enlace con el servidor central."})
    
if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG') == 'True'
    app.run(debug=debug_mode, host='0.0.0.0')