import os
import sqlite3
import pyotp
from functools import wraps
from werkzeug.utils import secure_filename
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold # <--- NUEVO
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from flask_mail import Mail, Message
from dotenv import load_dotenv

# Cargar variables
load_dotenv()

app = Flask(__name__)

# --- CONFIGURACIÓN DE SEGURIDAD PANEL ADMINISTRATIVO ---
app.secret_key = os.getenv('SECRET_KEY', 'matrix-default-super-secret-key-1337')
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
MFA_SECRET = os.getenv('MFA_SECRET', 'RZ4AJKKEXUOMRVU5')

# Configurar ruta administrativa secreta
ADMIN_PATH = os.getenv('ADMIN_PATH', '/matrix-control-center-99')
if not ADMIN_PATH.startswith('/'):
    ADMIN_PATH = '/' + ADMIN_PATH
ADMIN_PATH = ADMIN_PATH.rstrip('/')

DATABASE = os.path.join(app.root_path, 'database.db')

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                image_url TEXT NOT NULL,
                tags TEXT NOT NULL,
                link_url TEXT,
                link_text TEXT,
                status TEXT DEFAULT 'ACTIVE',
                order_num INTEGER DEFAULT 0
            )
        ''')
        cursor.execute('SELECT COUNT(*) FROM projects')
        if cursor.fetchone()[0] == 0:
            cursor.executemany('''
                INSERT INTO projects (title, description, image_url, tags, link_url, link_text, status, order_num)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', [
                (
                    'E-Commerce Full Stack - Django',
                    '<strong>Plataforma integral de comercio electrónico</strong> escalable y segura. <br><br> <i class="fas fa-server text-success me-1"></i> <strong>Backend & Core:</strong> Arquitectura MVT con Django y Python. Gestión de autenticación y seguridad. <br> <i class="fas fa-database text-success me-1"></i> <strong>Datos & Admin:</strong> Modelado ORM avanzado, bases de datos SQL y panel de administración personalizado. <br> <i class="fas fa-shopping-cart text-success me-1"></i> <strong>Funcionalidad:</strong> Carrito persistente, gestión de pedidos y pasarela de pagos integrada.',
                    'img/tienda-django.png',
                    'Django, Python, SQL, Docker',
                    'https://neuraprint3d.com/',
                    'INICIAR SISTEMA',
                    'ACTIVE',
                    1
                ),
                (
                    '✈️ IA Predictiva de Riesgos Aéreos (End-to-End)',
                    '<strong>Pipeline completo de Machine Learning</strong> para predecir incidentes aéreos. <br><br> <i class="fas fa-check text-success me-1"></i> <strong>ETL & Data Wrangling:</strong> Depuración de datasets históricos masivos (FAA) con BeautifulSoup y Pandas. <br> <i class="fas fa-check text-success me-1"></i> <strong>Modelado:</strong> Entrenamiento de <strong>XGBoost</strong> optimizado para alta sensibilidad (Recall). <br> <i class="fas fa-check text-success me-1"></i> <strong>Despliegue:</strong> Interfaz interactiva en <strong>Streamlit</strong>.',
                    'img/aircrashcal.png',
                    'Python, Streamlit, XGBoost, PyCaret',
                    'https://aircrashcal.jose-cabezas.com/',
                    'EJECUTAR MODELO',
                    'ACTIVE',
                    2
                ),
                (
                    'DevOps Knowledge Base',
                    '<strong>[WIP] Plataforma de documentación técnica</strong> tipo Wiki para centralizar manuales de despliegue. <br><br> <i class="fas fa-sitemap text-warning me-1"></i> <strong>Arquitectura Modular:</strong> Patrón <em>Application Factory</em> y <em>Blueprints</em>. <br> <i class="fas fa-file-code text-warning me-1"></i> <strong>Motor Markdown:</strong> Renderizado dinámico de contenido técnico. <br> <i class="fas fa-tools text-warning me-1"></i> <strong>Estado:</strong> Implementando sistema de autenticación y CRUD.',
                    'img/flask-wiki.png',
                    'Flask, Jinja2, WIP',
                    'https://blog.jose-cabezas.com/',
                    'EN CONSTRUCCIÓN',
                    'WIP',
                    3
                ),
                (
                    'MatchMVP - Gamer Duo & Coaching Platform',
                    '<strong>Plataforma competitiva para jugadores de eSports</strong>. Diseñada para encontrar compañeros de equipo (Duo Q) ideales y potenciar tu rendimiento. <br><br> <i class="fas fa-users text-success me-1"></i> <strong>Comunidad & Reputación:</strong> Sistema avanzado de emparejamiento y valoración por Karma para asegurar un ambiente libre de toxicidad. <br> <i class="fas fa-brain text-success me-1"></i> <strong>Coaching con IA:</strong> Consejos y análisis dinámico en tiempo real basado en tu desempeño histórico. <br> <i class="fas fa-network-wired text-success me-1"></i> <strong>Arquitectura:</strong> Backend asíncrono con FastAPI, base de datos PostgreSQL y despliegue multi-contenedor optimizado.',
                    'img/web.jpg',
                    'FastAPI, React, PostgreSQL, Docker',
                    'https://matchmvp.win/',
                    'BUSCAR COMPAÑERO',
                    'ACTIVE',
                    4
                )
            ])
            conn.commit()

# Inicializar base de datos al importar
init_db()

# Decorador de login seguro para el Admin
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

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


import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ... (existing code) ...

# Cargar contexto en memoria al inicio
try:
    with open('linkedin_data.txt', 'r', encoding='utf-8') as f:
        CONTEXT_DATA = f.read()
    logging.info("Contexto cargado correctamente desde linkedin_data.txt")
except FileNotFoundError:
    CONTEXT_DATA = "Error: No se encontró el archivo de datos (linkedin_data.txt)."
    logging.error("No se encontró linkedin_data.txt")

# Función auxiliar para obtener el contexto (ahora desde memoria)
def get_context():
    return CONTEXT_DATA

# --- RUTAS ---

@app.route('/')
def index():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM projects ORDER BY order_num ASC, id DESC')
    projects = cursor.fetchall()
    conn.close()
    return render_template('index.html', projects=projects)

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

# --- CONFIGURACIÓN E INSTRUCCIONES DE MFA ---
totp = pyotp.TOTP(MFA_SECRET)
provisioning_uri = totp.provisioning_uri(name=ADMIN_USERNAME, issuer_name="JCP_Portfolio")
logging.info("=========================================================================")
logging.info("SISTEMA DE SEGURIDAD ACTIVADO.")
logging.info(f"Ruta Administrativa Secreta: {ADMIN_PATH}")
logging.info(f"MFA Secret Key (Manual): {MFA_SECRET}")
logging.info(f"Para añadir al Authenticator, usa esta URI: {provisioning_uri}")
logging.info("=========================================================================")

# --- RUTAS DE ADMINISTRACIÓN ---

@app.route(ADMIN_PATH + '/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(ADMIN_PATH + '/dashboard')
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        mfa_token = request.form.get('mfa_token')
        
        # Validar credenciales
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            # Validar MFA
            totp_verifier = pyotp.TOTP(MFA_SECRET)
            if totp_verifier.verify(mfa_token):
                session['admin_logged_in'] = True
                logging.info(f"Admin login successful from {request.remote_addr}")
                return redirect(ADMIN_PATH + '/dashboard')
            else:
                flash("AUTENTICACIÓN TOTP FALLIDA. TOKEN DE SEGURIDAD INVÁLIDO.", "danger")
                logging.warning(f"Admin login failed: Invalid MFA token from {request.remote_addr}")
        else:
            flash("ACCESO DENEGADO. CREDENCIALES INCORRECTAS.", "danger")
            logging.warning(f"Admin login failed: Incorrect credentials from {request.remote_addr}")
            
    return render_template('admin_login.html', admin_path=ADMIN_PATH)

@app.route(ADMIN_PATH + '/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash("SESIÓN FINALIZADA CORRECTAMENTE. CONEXIÓN CERRADA.", "info")
    return redirect(url_for('index'))

@app.route(ADMIN_PATH)
@app.route(ADMIN_PATH + '/dashboard')
@login_required
def admin_dashboard():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM projects ORDER BY order_num ASC, id DESC')
    projects = cursor.fetchall()
    conn.close()
    return render_template('admin_dashboard.html', projects=projects, admin_path=ADMIN_PATH)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'ico'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route(ADMIN_PATH + '/add', methods=['GET', 'POST'])
@login_required
def admin_add():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        tags = request.form.get('tags')
        link_url = request.form.get('link_url')
        link_text = request.form.get('link_text')
        status = request.form.get('status', 'ACTIVE')
        order_num = request.form.get('order_num', 0)
        
        # Subida de imagen
        image_file = request.files.get('image')
        image_url = 'img/web.jpg' # Fallback por defecto
        
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            import time
            filename = f"{int(time.time())}_{filename}"
            upload_folder = os.path.join(app.static_folder, 'img')
            os.makedirs(upload_folder, exist_ok=True)
            image_file.save(os.path.join(upload_folder, filename))
            image_url = 'img/' + filename
            
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO projects (title, description, image_url, tags, link_url, link_text, status, order_num)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, description, image_url, tags, link_url, link_text, status, order_num))
        conn.commit()
        conn.close()
        
        flash("SISTEMA ACTUALIZADO: NUEVO PROYECTO REGISTRADO CORRECTAMENTE.", "success")
        return redirect(ADMIN_PATH + '/dashboard')
        
    return render_template('admin_form.html', action='Añadir', project=None, admin_path=ADMIN_PATH)

@app.route(ADMIN_PATH + '/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
def admin_edit(project_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM projects WHERE id = ?', (project_id,))
    project = cursor.fetchone()
    
    if not project:
        conn.close()
        flash("ERROR: EL PROYECTO ESPECIFICADO NO EXISTE EN LA BASE DE DATOS.", "danger")
        return redirect(ADMIN_PATH + '/dashboard')
        
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        tags = request.form.get('tags')
        link_url = request.form.get('link_url')
        link_text = request.form.get('link_text')
        status = request.form.get('status', 'ACTIVE')
        order_num = request.form.get('order_num', 0)
        
        image_url = project['image_url']
        
        image_file = request.files.get('image')
        if image_file and allowed_file(image_file.filename):
            filename = secure_filename(image_file.filename)
            import time
            filename = f"{int(time.time())}_{filename}"
            upload_folder = os.path.join(app.static_folder, 'img')
            os.makedirs(upload_folder, exist_ok=True)
            image_file.save(os.path.join(upload_folder, filename))
            image_url = 'img/' + filename
            
        cursor.execute('''
            UPDATE projects
            SET title = ?, description = ?, image_url = ?, tags = ?, link_url = ?, link_text = ?, status = ?, order_num = ?
            WHERE id = ?
        ''', (title, description, image_url, tags, link_url, link_text, status, order_num, project_id))
        conn.commit()
        conn.close()
        
        flash("SISTEMA ACTUALIZADO: REGISTRO MODIFICADO CORRECTAMENTE.", "success")
        return redirect(ADMIN_PATH + '/dashboard')
        
    conn.close()
    return render_template('admin_form.html', action='Editar', project=project, admin_path=ADMIN_PATH)

@app.route(ADMIN_PATH + '/delete/<int:project_id>', methods=['POST'])
@login_required
def admin_delete(project_id):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT image_url FROM projects WHERE id = ?', (project_id,))
    project = cursor.fetchone()
    if project:
        image_url = project['image_url']
        cursor.execute('DELETE FROM projects WHERE id = ?', (project_id,))
        conn.commit()
        
        # Evitar borrar imágenes estáticas predefinidas
        defaults = {'img/tienda-django.png', 'img/aircrashcal.png', 'img/flask-wiki.png', 'img/web.jpg'}
        if image_url not in defaults:
            full_path = os.path.join(app.static_folder, image_url)
            if os.path.exists(full_path):
                try:
                    os.remove(full_path)
                    logging.info(f"Deleted project image file: {full_path}")
                except Exception as e:
                    logging.error(f"Error deleting image file: {e}")
                    
        flash("SISTEMA ACTUALIZADO: REGISTRO ELIMINADO COMPLETAMENTE.", "success")
    else:
        flash("ERROR: EL REGISTRO NO EXISTE.", "danger")
        
    conn.close()
    return redirect(ADMIN_PATH + '/dashboard')
    
if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG') == 'True'
    app.run(debug=debug_mode, host='0.0.0.0')