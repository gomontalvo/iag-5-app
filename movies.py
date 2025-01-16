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


def search_movie_id(movie_name):
    search = tmdb.Search()
    response = search.multi(query=movie_name, language='es-CL')

    if not response['results']:
        return None
    
    result = response['results'][0]
    return result['id']

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


def search_credits(movie_name):
    cast = []
    movie_id = search_movie_id(movie_name)
    if not movie_id:
        return "No se encontró resultados para este titulo"
    
    movie = tmdb.Movies(movie_id)
    creditos = movie.credits()
    
    cast = "\n".join(
        f"{cast_member['name']} como {cast_member['character']}"
        for cast_member in creditos['cast']
    )
    return cast




    #if not search.results:
    #    return creditos

    #return search.response[0]
    
    #results = tmdb.Credits(query=reponse.moviid, "es-CL",)

    #if not results:
    #    return platforms

    #for offer in results[0].offers:
    #    creditos.append({
    #       'name': offer.cast.name,
    #       'icon': offer.cast.,
    #       'url': offer.url,
    #  })

    return creditos

