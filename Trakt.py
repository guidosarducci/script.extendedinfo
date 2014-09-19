import datetime
import sys
from Utils import *
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson

trakt_key = '7b2281f0d441ab1bf4fdc39fd6cccf15'
base_url = "http://api.trakt.tv/"


def GetTraktCalendarShows(Type):
    shows = []
    results = ""
    url = 'calendar/%s.json/%s/today/14' % (Type, trakt_key)
    try:
        results = Get_JSON_response(base_url, url, 0.5)
    except:
        log("Error when fetching Trakt data from net")
        log("Json Query: " + url)
        results = None
    count = 1
    if results is not None:
        for day in results:
            for episode in day["episodes"]:
                show = {'Title': episode["episode"]["title"],
                        'TVShowTitle': episode["show"]["title"],
                        'ID': episode["show"]["tvdb_id"],
                        'Runtime': episode["show"]["runtime"],
                        'Year': episode["show"].get("year"),
                        'Certification': episode["show"]["certification"],
                        'Studio': episode["show"]["network"],
                        'Plot': episode["show"]["overview"],
                        'Genre': " / ".join(episode["show"]["genres"]),
                        'Thumb': episode["episode"]["images"]["screen"],
                        'Art(poster)': episode["show"]["images"]["poster"],
                        'Art(banner)': episode["show"]["images"]["banner"],
                        'Art(fanart)': episode["show"]["images"]["fanart"]}
                shows.append(show)
                count += 1
                if count > 20:
                    break
    return shows


def HandleTraktMovieResult(results):
    count = 1
    movies = []
    for movie in results:
        try:
            premiered = str(datetime.datetime.fromtimestamp(int(movie["released"])))[:10]
        except:
            premiered = ""
        try:
            movie = {'Title': movie["title"],
                     'Runtime': movie["runtime"],
                     'Tagline': movie["tagline"],
                     'Trailer': ConvertYoutubeURL(movie["trailer"]),
                     'Year': movie["year"],
                     'ID': movie["tmdb_id"],
                     'mpaa': movie["certification"],
                     'Plot': movie["overview"],
                     'Premiered': premiered,
                     'Rating': movie["ratings"]["percentage"] / 10.0,
                     'Votes': movie["ratings"]["votes"],
                     'Watchers': movie["watchers"],
                     'Genre': " / ".join(movie["genres"]),
                     'Art(poster)': movie["images"]["poster"],
                     'Art(fanart)': movie["images"]["fanart"]}
            movies.append(movie)
        except Exception as e:
            log(e)
        count += 1
        if count > 20:
            break
    return movies


def HandleTraktTVShowResult(results):
    count = 1
    shows = []
    for tvshow in results:
        try:
            premiered = str(datetime.datetime.fromtimestamp(int(tvshow["first_aired"])))[:10]
        except:
            premiered = ""
        show = {'Title': tvshow["title"],
                'Label': tvshow["title"],
                'TVShowTitle': tvshow["title"],
                'Runtime': tvshow["runtime"],
                'Year': tvshow["year"],
                'Status': tvshow.get("status", ""),
                'mpaa': tvshow["certification"],
                'Studio': tvshow["network"],
                'Plot': tvshow["overview"],
                'ID': tvshow["tvdb_id"],
                'AirDay': tvshow["air_day"],
                'AirShortTime': tvshow["air_time"],
                'Label2': tvshow["air_day"] + " " + tvshow["air_time"],
                'Premiered': premiered,
                'Country': tvshow["country"],
                'Rating': tvshow["ratings"]["percentage"] / 10.0,
                'Votes': tvshow["ratings"]["votes"],
                'Watchers': tvshow.get("watchers", ""),
                'Genre': " / ".join(tvshow["genres"]),
                'Art(poster)': tvshow["images"]["poster"],
                'Poster': tvshow["images"]["poster"],
                'Art(banner)': tvshow["images"]["banner"],
                'Art(fanart)': tvshow["images"]["fanart"],
                'Fanart': tvshow["images"]["fanart"],
                'Thumb': tvshow["images"]["fanart"]}
        shows.append(show)
        count += 1
        if count > 20:
            break
    return shows


def GetTrendingShows():
    url = 'shows/trending.json/%s' % trakt_key
    results = Get_JSON_response(base_url, url)
    if results is not None:
        return HandleTraktTVShowResult(results)


def GetTVShowInfo(id):
    url = 'show/summary.json/%s/%s' % (trakt_key, id)
    results = Get_JSON_response(base_url, url)
    if results is not None:
        return HandleTraktTVShowResult([results])


def GetTrendingMovies():
    url = 'movies/trending.json/%s' % trakt_key
    results = Get_JSON_response(base_url, url)
    if results is not None:
        return HandleTraktMovieResult(results)


def GetSimilarTrakt(mediatype, imdb_id):
    if imdb_id is not None:
        if mediatype == "tvshow":
            mediatype = "show"
        url = '%s/related.json/%s/%s/' % (mediatype, trakt_key, imdb_id)
        results = Get_JSON_response(base_url, url)
        if results is not None:
            if mediatype == "show":
                return HandleTraktTVShowResult(results)
            elif mediatype == "movie":
                return HandleTraktMovieResult(results)
    else:
        Notify("Error when fetching info from Trakt.TV")
        return[]
