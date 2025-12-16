import os
import google.generativeai as genai  # <--- NUEVO: Librería de Google
from flask import Flask, render_template, request, redirect, url_for, jsonify # <--- NUEVO: Añadido jsonify
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
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
# --- DEBUG: VER QUÉ MODELOS TENGO DISPONIBLES ---
#print("--- MODELOS DISPONIBLES ---")
#for m in genai.list_models():
#    if 'generateContent' in m.supported_generation_methods:
#        print(m.name)
#print("---------------------------")

# Inicializamos el modelo (Flash es rápido y gratis)
model = genai.GenerativeModel('models/gemini-2.0-flash')

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
    # Obtenemos la pregunta del JSON que envía el frontend
    data = request.get_json()
    user_question = data.get('question')
    
    # Leemos tu CV
    context_data = get_context()
    
    # Creamos el prompt para la IA
    # Le damos personalidad y le pasamos tu CV + la pregunta
    prompt = f"""
    Actúa como 'JCP_SYSTEM', una IA asistente del portafolio de José Cabezas Pulgarín.
    Tu misión es responder dudas de reclutadores sobre José.
    
    INFORMACIÓN DE CONTEXTO (CV/LinkedIn de José):
    {context_data}
    
    PREGUNTA DEL USUARIO:
    {user_question}
    
    INSTRUCCIONES OBLIGATORIAS:
    1. Responde ÚNICAMENTE basándote en la información de contexto proporcionada arriba.
    2. Si la respuesta no está en el contexto, di: "Esa información está clasificada o no disponible en mis bancos de memoria."
    3. Mantén un tono profesional, técnico y conciso. Estilo "SysAdmin/Hacker".
    4. No inventes datos.
    """

    try:
        # Llamamos a Gemini
        response = model.generate_content(prompt)
        
        # Devolvemos la respuesta en formato JSON para que JS la lea
        return jsonify({'answer': response.text})
        
    except Exception as e:
        print(f"Error Gemini: {e}")
        return jsonify({'answer': "SYSTEM_ERROR: Fallo en la conexión neuronal con el servidor."})

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG') == 'True'
    app.run(debug=debug_mode, host='0.0.0.0')