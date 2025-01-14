from simplejustwatchapi.justwatch import search as justwatch_search
import tmdbsimple as tmdb
from dotenv import load_dotenv
from os import getenv

load_dotenv()
tmdb.API_KEY = getenv('TMDB_API_KEY')


def search(movie_name):
    search = tmdb.Search()
    response = search.multi(query=movie_name, language='es-CL')

    if not search.results:
        return None

    return search.results[0]


def search_platforms(movie_name):
    results = justwatch_search(movie_name, "CL", "es")
    platforms = []

    if not results:
        return platforms

    for offer in results[0].offers:
        platforms.append({
            'name': offer.package.name,
            'icon': offer.package.icon,
            'url': offer.url,
        })

    return platforms

def search_creditos(movie_name):
    results = tmdb.Credits(movie_name, "es")
    creditos = []

    if not results:
        return creditos

    for offer in results[0].offers:
        creditos.append({
            'name': offer.cast.name,
            'icon': offer.cast.popularity,
            'url': offer.cast.character,
        })

    return creditos