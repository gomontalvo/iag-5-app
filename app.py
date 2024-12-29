from flask import Flask, render_template, request, redirect, url_for, jsonify 
from flask_bootstrap import Bootstrap5
from openai import OpenAI
from dotenv import load_dotenv
from db import db, db_config
from models import User, Message, Preferencias

load_dotenv()

client = OpenAI()
app = Flask(__name__)
bootstrap = Bootstrap5(app)
db_config(app)


@app.route('/')
def index():
    return render_template('landing.html')



@app.route('/chat', methods=['GET', 'POST'])
def chat():
    user = db.session.query(User).first()

    if not user:
        return "Usuario no encontrado", 404
   
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
        if user_message== 'Recomiéndame una película':
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
        temperature=1
    )

    model_recommendation = chat_completion.choices[0].message.content
    db.session.add(Message(content=model_recommendation, author="assistant", user=user))
    db.session.commit()

    return render_template('chat.html', messages=user.messages, user_refs=options)

@app.route('/user/<int:user_id>', methods=['GET', 'POST'])
def user_profile(user_id):
    # Obtener el usuario por su ID
    user = db.session.query(User).filter_by(id=user_id).first()
    if not user:
        return "Usuario no encontrado", 404

    mensaje_error = None  # Variable para manejar mensajes de error

    if request.method == 'POST':
        # Recuperar datos del formulario
        preferencia = request.form.get('preferencia')
        categoria = request.form.get('categoria')

        # Verificar si ya existe una preferencia igual
        existing_pref = db.session.query(Preferencias).filter_by(
            preferencia=preferencia,
            categoria=categoria,
            user_id=user.id
        ).first()

        if existing_pref:
            # Evitar duplicados
            mensaje_error = f"La preferencia '{preferencia}' ya existe en la categoría '{categoria}'."
        else:
            # Guardar nueva preferencia si no existe
            db.session.add(Preferencias(preferencia=preferencia, categoria=categoria, user=user))
            db.session.commit()
            return redirect(url_for('user_profile', user_id=user.id))

    # Obtener preferencias actuales
    preferences = db.session.query(Preferencias).filter_by(user_id=user.id).all()

    return render_template(
        'user.html', 
        username=user.email,
        user_id=user.id,
        preferences=preferences,
        mensaje_error=mensaje_error  # Pasar mensaje de error al frontend
    )
          


@app.route('/user/<int:user_id>/delete_preference', methods=['POST'])
def delete_preference(user_id):
    # Obtener el usuario por su ID
    user = db.session.query(User).filter_by(id=user_id).first()
    if not user:
        return "Usuario no encontrado", 404

    # Recuperar el ID de la preferencia a eliminar
    preference_id = request.form.get('preference_id')

    # Buscar y eliminar la preferencia correspondiente
    preference = db.session.query(Preferencias).filter_by(id=preference_id, user_id=user.id).first()
    if preference:
        db.session.delete(preference)
        db.session.commit()

    return redirect(url_for('user_profile', user_id=user.id))