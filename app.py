from flask import Flask, render_template, request, flash, jsonify,redirect, url_for
from flask_bootstrap import Bootstrap5
from openai import OpenAI
from dotenv import load_dotenv
from db import db, db_config
from models import User, Message, Preferencias
from forms import  SignUpForm, LoginForm
from flask_wtf.csrf import CSRFProtect
from os import getenv
import json
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from flask_bcrypt import Bcrypt
from bot import search_movie_or_tv_show, where_to_watch, search_movie_credits
from markdown import markdown

load_dotenv()

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = 'Inicia sesión para continuar'

client = OpenAI()
app = Flask(__name__)
app.secret_key = 'yuqita78@_'#arreglar después por variable de entonno
bootstrap = Bootstrap5(app)
app.config['WTF_CSRF_ENABLED'] = True

csrf = CSRFProtect(app)
login_manager.init_app(app)
bcrypt = Bcrypt(app)

db_config(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

tools = [
    {
        'type': 'function',
        'function': {
            "name": "where_to_watch",
            "description": "Returns a list of platforms where a specified movie can be watched.",
            "parameters": {
                "type": "object",
                "required": [
                    "name"
                ],
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the movie to search for"
                    }
                },
                "additionalProperties": False
            }
        },
    },
    {
        'type': 'function',
        'function': {
            "name": "search_movie_or_tv_show",
            "description": "Returns information about a specified movie or TV show.",
            "parameters": {
                "type": "object",
                "required": [
                    "name"
                ],
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the movie/tv show to search for"
                    }
                },
                "additionalProperties": False
            }
        },
    },
    {
        'type': 'function',
        'function': {
            "name": "search_movie_credits",
            "description": "Returns a list of credits or actors of the movie or TV show.",
            "parameters": {
                "type": "object",
                "required": [
                    "name"
                ],
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The credits of the movie or series to search for"
                    }
                },
                "additionalProperties": False
            }
        },
    }
]

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

tools = [
    {
        'type': 'function',
        'function': {
            "name": "where_to_watch",
            "description": "Returns a list of platforms where a specified movie can be watched.",
            "parameters": {
                "type": "object",
                "required": [
                    "name"
                ],
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the movie to search for"
                    }
                },
                "additionalProperties": False
            }
        },
    },
    {
        'type': 'function',
        'function': {
            "name": "search_movie_or_tv_show",
            "description": "Returns information about a specified movie or TV show.",
            "parameters": {
                "type": "object",
                "required": [
                    "name"
                ],
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The name of the movie/tv show to search for"
                    }
                },
                "additionalProperties": False
            }
        },
    },
    {
        'type': 'function',
        'function': {
            "name": "search_movie_credits",
            "description": "Returns a list of credits or actors of the movie or TV show.",
            "parameters": {
                "type": "object",
                "required": [
                    "name"
                ],
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "The credits of the movie or series to search for"
                    }
                },
                "additionalProperties": False
            }
        },
    }
]


@app.route('/')
def index():
    return render_template('landing.html')


@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    # Usar el usuario actual autenticado
    user = current_user

    if not user.is_authenticated:
        flash("Debes iniciar sesión para acceder al chat.", "error")
        return redirect(url_for('login'))
   
    # Obtener preferencias del usuario
    preferences = db.session.query(Preferencias).filter_by(user_id=user.id).all()

    genres = [pref.preferencia for pref in preferences if pref.categoria == 'G'][:5]
    titles = [pref.preferencia for pref in preferences if pref.categoria == 'T'][:5]
    
    # Crear dinámicamente intents a partir de las preferencias de tipo Género (G)
    intents = {genre: f"Recomiéndame una película de {genre}" for genre in genres}
    intents['Quiero tener suerte'] = 'Recomiéndame una película'
    options = list(intents.keys())

    if request.method == 'GET':
        return render_template('chat.html', messages=user.messages, user_refs=options)

    intent = request.form.get('intent')
    user_message = request.form.get('message')  # Mensaje original del usuario

    if intent in intents:
        user_message = intents[intent]
        final_message = user_message
        if user_message == 'Recomiéndame una película':
            preferences_text = " ,mis preferencias son: " + ", ".join(genres + titles)
        else:
            preferences_text = ""  # No se agregan preferencias si se selecciona Género de película
    else:
        # Crear el mensaje con contexto adicional para el modelo
        preferences_text = " ,mis preferencias son: " + ", ".join(genres + titles)
    
    final_message = user_message + preferences_text  # Mensaje con contexto

    # Guardar solo el mensaje original del usuario en la base de datos
    db.session.add(Message(content=user_message, author="user", user=user))
    db.session.commit()

    messages_for_llm = [{
        "role": "system",
        "content": "Eres un chatbot que recomienda películas, te llamas 'Movienerd'. Tu rol es responder recomendaciones de manera breve y concisa. No repitas recomendaciones.",
    }]

    for message in user.messages:
        if message.author == 'assistant':
            message.content = markdown(message.content)
        messages_for_llm.append({
            "role": message.author,
            "content": message.content,
        })

    # Incluir el mensaje con contexto adicional para el modelo
    messages_for_llm.append({
        "role": "user",
        "content": final_message
    })

    chat_completion = client.chat.completions.create(
        messages=messages_for_llm,
        model="gpt-4o",
        temperature=1,
        tools=tools,
    )

    if chat_completion.choices[0].message.tool_calls:
        tool_call = chat_completion.choices[0].message.tool_calls[0]

        if tool_call.function.name == 'where_to_watch':
            arguments = json.loads(tool_call.function.arguments)
            name = arguments['name']
            response_sf = where_to_watch(client, name, user, ", ".join(genres))
            model_recommendation  = markdown(response_sf)
        elif tool_call.function.name == 'search_movie_credits':
            arguments = json.loads(tool_call.function.arguments)
            name = arguments['name']
            model_recommendation = search_movie_credits(client, name, user, ", ".join(genres))
        elif tool_call.function.name == 'search_movie_or_tv_show':
            arguments = json.loads(tool_call.function.arguments)
            name = arguments['name']
            model_recommendation = search_movie_or_tv_show(client, name, user, ", ".join(genres))
    else:
        model_recommendation = chat_completion.choices[0].message.content

    db.session.add(Message(content=model_recommendation, author="assistant", user=user))
    db.session.commit()

    return render_template('chat.html', messages=user.messages, user_refs=options)


@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            user = User(email=email, password_hash=bcrypt.generate_password_hash(password).decode('utf-8'))
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('chat'))
    return render_template('sign-up.html', form=form)

@app.route('/log-in', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data
            user = db.session.query(User).filter_by(email=email).first()
            if user and bcrypt.check_password_hash(user.password_hash, password):
                login_user(user)
                return redirect('chat')

            flash("El correo o la contraseña es incorrecta.", "error")

    return render_template('log-in.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect('/')

@app.route('/user', methods=['GET', 'POST'])
@login_required
def user_profile():
    mensaje_error = None  # Variable para manejar mensajes de error

    if request.method == 'POST':
        # Recuperar datos del formulario
        preferencia = request.form.get('preferencia', '').strip()
        categoria = request.form.get('categoria', '').strip()

        # Validar campos obligatorios
        if not preferencia or not categoria:
            mensaje_error = "Todos los campos son obligatorios."
        else:
            # Verificar si ya existe una preferencia igual
            existing_pref = db.session.query(Preferencias).filter_by(
                preferencia=preferencia,
                categoria=categoria,
                user_id=current_user.id
            ).first()

            if existing_pref:
                mensaje_error = f"La preferencia '{preferencia}' ya existe en la categoría '{categoria}'."
            else:
                # Guardar nueva preferencia si no existe
                nueva_preferencia = Preferencias(preferencia=preferencia, categoria=categoria, user_id=current_user.id)
                db.session.add(nueva_preferencia)
                db.session.commit()
                flash("Preferencia agregada exitosamente.", "success")
                return redirect(url_for('user_profile'))

    # Obtener preferencias actuales del usuario
    preferences = db.session.query(Preferencias).filter_by(user_id=current_user.id).all()

    return render_template(
        'user.html', 
        username=current_user.email,
        preferences=preferences,
        mensaje_error=mensaje_error
    )


@app.route('/user/delete_preference', methods=['POST'])
@login_required
def delete_preference():
    # Recuperar el ID de la preferencia a eliminar
    preference_id = request.form.get('preference_id')

    if not preference_id:
        flash("No se especificó una preferencia para eliminar.", "error")
        return redirect(url_for('user_profile'))

    # Buscar y eliminar la preferencia correspondiente
    preference = db.session.query(Preferencias).filter_by(id=preference_id, user_id=current_user.id).first()
    if preference:
        db.session.delete(preference)
        db.session.commit()
        flash("Preferencia eliminada exitosamente.", "success")
    else:
        flash("No se encontró la preferencia especificada.", "error")

    return redirect(url_for('user_profile'))

