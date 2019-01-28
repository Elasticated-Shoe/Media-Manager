import protected.abstractions.globals as shared
from urllib.parse import quote
import requests
import json

def fetchFilmData(film):
    movieKey = shared.globalSettings["moviedb"]["key"]
    quotedfilm = quote(film)
    print(film)
    movieUrl = "https://api.themoviedb.org/3/"
    movieQuery = movieUrl + "search/movie?api_key=" + movieKey + "&language=en&query=" + quotedfilm + "&include_adult=false"
    movieQueryResults = requests.get(movieQuery)
    movieQueryResults = json.loads(movieQueryResults.text)
    # might return multiple if there are multiple matches, needs a check
    if len(movieQueryResults["results"]) == 0:
        return False
    return movieQueryResults["results"][0]

def fetchMedia(url):
    pass