from movies import search, search_platforms, search_creditos
from openai import OpenAI
from models import User
from db import db
from models import User, Message, Preferencias


def build_prompt(user: User, context: str):
    system_prompt = '''Eres un chatbot que recomienda películas, te llamas 'Movienerd'.
    - Tu rol es responder recomendaciones de manera breve y concisa.
    - No repitas recomendaciones.
    '''
    preferences = db.session.query(Preferencias).filter_by(user_id=user.id).all()

    genres = [pref.preferencia for pref in preferences if pref.categoria == 'G'][:5]
    titles = [pref.preferencia for pref in preferences if pref.categoria == 'T'][:5]
    #genres = ["drama","comedia"]
    #titles = []

    if genres.count > 0:
        system_prompt = " , Los generos favoritos de usuario son: " + ", ".join(genres)
    if titles.count > 0:
        system_prompt += f', Los títulos favoritos de usuario son: ' + ", ".join(titles)
    # Incluir preferencias del usuario
    #if user.favorite_genre:
    #    system_prompt += f'- El género favorito del usuario es: {genres}.\n'
    #if user.disliked_genre:
    #    system_prompt += f'- El género a evitar del usuario es: {user.disliked_genre}.\n'

    if context:
        system_prompt += f'Además considera el siguiente contenido: {context}\n'

    return system_prompt


def where_to_watch(client: OpenAI, search_term: str, user: User):
    movie_or_tv_show = search_platforms(search_term)

    if not movie_or_tv_show:
        return f'No estoy seguro de dónde puedes ver esta película o serie :(, pero quizas puedes revisar en JustWatch: https://www.themoviedb.org/search?query={search_term}'

    system_prompt = build_prompt(user, str(movie_or_tv_show))

    messages_for_llm = [{"role": "system", "content": system_prompt}]

    for message in user.messages:
        messages_for_llm.append({
            "role": message.author,
            "content": message.content,
        })

    chat_completion = client.chat.completions.create(
        messages=messages_for_llm,
        model="gpt-4o",
        temperature=1,
    )

    return chat_completion.choices[0].message.content



def search_movie_or_tv_show(client: OpenAI, search_term: str, user: User):
    movie_or_tv_show = search(search_term)

    if movie_or_tv_show:
        system_prompt = build_prompt(user, str(movie_or_tv_show))
    else:
        system_prompt = build_prompt(user, '')

    messages_for_llm = [{"role": "system", "content": system_prompt}]

    for message in user.messages:
        messages_for_llm.append({
            "role": message.author,
            "content": message.content,
        })

    chat_completion = client.chat.completions.create(
        messages=messages_for_llm,
        model="gpt-4o",
        temperature=1,
    )

    return chat_completion.choices[0].message.content

def movie_creditos(client: OpenAI, search_term: str, user: User):
    creditos = search_creditos(search_term)

    if not creditos:
        return f'No estoy seguro de dónde puedes ver esta película o serie :(, pero quizas puedes revisar en JustWatch: https://www.themoviedb.org/search?query={search_term}'

    system_prompt = build_prompt(user, str(creditos))

    messages_for_llm = [{"role": "system", "content": system_prompt}]

    for message in user.messages:
        messages_for_llm.append({
            "role": message.author,
            "content": message.content,
        })

    chat_completion = client.chat.completions.create(
        messages=messages_for_llm,
        model="gpt-4o",
        temperature=1,
    )

    return chat_completion.choices[0].message.content
