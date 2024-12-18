from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap5
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()
app = Flask(__name__)
bootstrap = Bootstrap5(app)

@app.route('/')
def index():
    return render_template('landing.html')


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'GET':
        return render_template('chat.html')

    intent = request.form.get('intent')

    
    if intent == 'Quiero tener suerte':
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Eres un chatbot que recomienda películas, te llamas 'Movienerd'. Tu rol es responder recomendaciones de manera breve y concisa.",
                },
                {
                    "role": "user",
                    "content": "Recomiéndame una película",
                }
            ],
            model="gpt-4o",
            temperature=1.2
        )
        model_recommendation = chat_completion.choices[0].message.content
        return render_template('chat.html', recommendation=model_recommendation)
    elif intent == 'Terror':
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Eres un chatbot que recomienda películas, te llamas 'Movienerd'. Tu rol es responder recomendaciones de manera breve y concisa.",
                },
                {
                    "role": "user",
                    "content": "Recomiéndame las 2 películas de terror",
                }
            ],
            model="gpt-4o",
            temperature=0.5
        )
        model_recommendation = chat_completion.choices[0].message.content
        return render_template('chat.html', recommendation=model_recommendation)
    elif intent == 'Accion':
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Eres un chatbot que recomienda películas, te llamas 'Movienerd'. Tu rol es responder recomendaciones de manera breve y concisa.",
                },
                {
                    "role": "user",
                    "content": "Recomiéndame las 2 películas de Acción",
                }
            ],
            model="gpt-4o",
            temperature=0.5
        )
        model_recommendation = chat_completion.choices[0].message.content
        return render_template('chat.html', recommendation=model_recommendation)
    elif intent == 'Terror':
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Eres un chatbot que recomienda películas, te llamas 'Next Moby'. Tu rol es responder recomendaciones de manera breve y concisa.",
                },
                {
                    "role": "user",
                    "content": "Recomiéndame las 2 películas de Comedia",
                }
            ],
            model="gpt-4o",
            temperature=0.8
        )
        model_recommendation = chat_completion.choices[0].message.content
        return render_template('chat.html', recommendation=model_recommendation)

@app.route('/user/<username>')
def user(username):
    favorite_movies = [
        'The Shawshank Redemption',
        'The Godfather',
        'The Dark Knight',
    ]
    return render_template('user.html', username=username, favorite_movies=favorite_movies)


@app.post('/recommend')
def recommend():
    data = request.get_json()
    user_message = data['message']

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "Eres un chatbot que recomienda películas, te llamas 'Next Moby'. Tu rol es responder recomendaciones de manera breve y concisa.",
            },
            {
                "role": "user",
                "content": user_message,
            }
        ],
        model="gpt-4o",
    )

    message = chat_completion.choices[0].message.content

    return {
        'recommendation': message,
        'tokens': chat_completion.usage.total_tokens,
    }
