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
    genres = [pref.preferencia for pref in preferences if pref.categoria == 'G'][:5]  # Limitar a 5 géneros
    titles = [pref.preferencia for pref in preferences if pref.categoria == 'T'][:5]  # Limitar a 5 títulos

    # Crear dinámicamente intents a partir de las preferencias
    intents = {genre: f"Recomiéndame una película de {genre}" for genre in genres}
    for title in titles:
        if title not in intents:
            intents[title] = f"Recomiéndame una película similar a {title}"

    intents['Quiero tener suerte'] = 'Recomiéndame una película'
    intents['Enviar'] = request.form.get('message')

    options = list(intents.keys())

    if request.method == 'GET':
        return render_template('chat.html', messages=user.messages, user_refs=options)

    intent = request.form.get('intent')

    if intent in intents:
        user_message = intents[intent]

        # Guardar nuevo mensaje en la BD
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

        chat_completion = client.chat.completions.create(
            messages=messages_for_llm,
            model="gpt-4o",
            temperature=1
        )

        model_recommendation = chat_completion.choices[0].message.content
        db.session.add(Message(content=model_recommendation, author="assistant", user=user))
        db.session.commit()

        return render_template('chat.html', messages=user.messages, user_refs=options)

    # Manejo en caso de que el intent no sea válido
    return "Intento no válido", 400

@app.post('/recommend')
def recommend():
    user = db.session.query(User).first()

    if not user:
        return "Usuario no encontrado", 404

    data = request.get_json()
    user_message = data['message']
    new_message = Message(content=user_message, author="user", user=user)
    db.session.add(new_message)
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

    chat_completion = client.chat.completions.create(
        messages=messages_for_llm,
        model="gpt-4o",
    )

    message = chat_completion.choices[0].message.content

    return {
        'recommendation': message,
        'tokens': chat_completion.usage.total_tokens,
    }


@app.route('/user/<int:user_id>', methods=['GET', 'POST'])
def user_profile(user_id):
    # Obtener el usuario por su ID
    user = db.session.query(User).filter_by(id=user_id).first()
    if not user:
        return "Usuario no encontrado", 404

    if request.method == 'POST':
        # Recuperar datos del formulario
        preferencia = request.form.get('preferencia')
        categoria = request.form.get('categoria')

        # Actualizar o crear preferencia
        existing_pref = db.session.query(Preferencias).filter_by(user_id=user.id, categoria=categoria).first()
        if existing_pref:
            existing_pref.preferencia = preferencia
        else:
            db.session.add(Preferencias(preferencia=preferencia, categoria=categoria, user=user))

        # Guardar cambios en la base de datos
        db.session.commit()
        return redirect(url_for('user_profile', user_id=user.id))

    # Obtener preferencias actuales
    preferences = db.session.query(Preferencias).filter_by(user_id=user.id).all()

    return render_template(
        'user.html', 
        username=user.email,
        user_id=user.id,
        preferences=preferences
    )

@app.route('/user/<int:user_id>/delete_preference', methods=['POST'])
def delete_preference(user_id):
    # Obtener el usuario por su ID
    user = db.session.query(User).filter_by(id=user_id).first()
    if not user:
        return "Usuario no encontrado", 404

    # Recuperar datos del formulario para eliminar
    categoria = request.form.get('categoria')

    # Buscar y eliminar la preferencia correspondiente
    preference = db.session.query(Preferencias).filter_by(user_id=user.id, categoria=categoria).first()
    if preference:
        db.session.delete(preference)
        db.session.commit()

    return redirect(url_for('user_profile', user_id=user.id))
