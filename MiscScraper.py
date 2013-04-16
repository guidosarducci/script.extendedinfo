import sys
import os, time, datetime, re, random
import xbmc, xbmcgui, xbmcaddon, xbmcplugin,xbmcvfs
from Utils import *
if sys.version_info < (2, 7):
    import simplejson
else:
    import json as simplejson
    

rottentomatoes_key = '7ndbwf7s2pa9t34tmghspyz6'
trakt_key = '7b2281f0d441ab1bf4fdc39fd6cccf15'
tvrage_key = 'VBp9BuIr5iOiBeWCFRMG'
bing_key =  'Ai8sLX5R44tf24_2CGmbxTYiIX6w826dsCVh36oBDyTmH21Y6CxYEqtrV9oYoM6O'
googlemaps_key = 'AIzaSyBESfDvQgWtWLkNiOYXdrA9aU-2hv_eprY'
Addon_Data_Path = os.path.join( xbmc.translatePath("special://profile/addon_data/%s" % xbmcaddon.Addon().getAddonInfo('id') ).decode("utf-8") )

def GetXKCDInfo():
    settings = xbmcaddon.Addon(id='script.extendedinfo')
    items = []
    for i in range(0,10):
        try:
            url = 'http://xkcd.com/%i/info.0.json' % random.randrange(1, 1190)
            response = GetStringFromUrl(url)
            results = simplejson.loads(response)
            item = {'Image': results["img"],
                    'Title': results["title"],
                    'Description':results["alt"]  }
            items.append(item)
        except:
            log("Error when setting XKCD info")
    return items

def GetCandHInfo():
    count = 1
    images = []
    for i in range(1,30):
        try:
            url = 'http://www.explosm.net/comics/%i/' % random.randrange(1, 3128)
            response = GetStringFromUrl(url)
        except:
            log("Error when fetching CandH data from net")
        if response:
            regex = ur'src="([^"]+)"'
            matches = re.findall(regex, response)
            if matches:
                for item in matches:
                    if item.startswith('http://www.explosm.net/db/files/Comics/'):
                        dateregex = '[0-9][0-9]\.[0-9][0-9]\.[0-9][0-9][0-9][0-9]'
                        datematches = re.findall(dateregex, response)
                        newitem = {'Image': item,
                                    'Title': datematches[0]  }
                        images.append(newitem)
                        count += 1                      
              #  wnd.setProperty('CyanideHappiness.%i.Title' % count, item["title"])
                if count > 10:
                    break
    return images
                     
def GetFlickrImages():
    images = []
    results = ""
    try:
        url = 'http://pipes.yahoo.com/pipes/pipe.run?_id=241a9dca1f655c6fa0616ad98288a5b2&_render=json'
        response = GetStringFromUrl(url)
        results = simplejson.loads(response)
    except:
        log("Error when fetching Flickr data from net")
    count = 1
    if results:
        for item in results["value"]["items"]:
            image = {'Background': item["link"]  }
            images.append(image)
            count += 1
    return images
    
def GetBingMap(search_string):
    try:
        log(urllib.quote(search_string))
        log(urllib.quote_plus(search_string))
        url = 'http://dev.virtualearth.net/REST/v1/Imagery/Map/AerialWithLabels/%s?mapSize=800,600&key=%s' % (urllib.quote(search_string),bing_key)
        log(url)
        return url
    except:
        log("Error when fetching Bing data from net")
        return ""      
        
def GetGoogleMap(search_string,zoomlevel,type,aspect,lat,lon):
    try:
        if not type:
            type="roadmap"
        if aspect == "square":
            log("xxxx")
            size = "640x640"
        else:
            size = "640x400"
            log("yyyy")           
        if lat:
            search_string = str(lat) + "," + str(lon)
            log("Location: " + search_string)
        else:
            search_string = urllib.quote_plus(search_string)
        base_url='http://maps.googleapis.com/maps/api/staticmap?&sensor=false&scale=2&'
        url = base_url + 'maptype=%s&center=%s&zoom=%s&markers=%s&size=%s&key=%s' % (type, search_string, zoomlevel, search_string, size, googlemaps_key)
        log("Google Maps Search:" + url)
        return url
    except:
        return ""
        
        
def GetGeoCodes(search_string):
    try:
        search_string = urllib.quote_plus(search_string)
        base_url='https://maps.googleapis.com/maps/api/geocode/json?&sensor=false&'
        url = base_url + 'address=%s' % (search_string)
        log("Google Geocodes Search:" + url)
        response = GetStringFromUrl(url)
        results = simplejson.loads(response)
        log(results)
        location = results["results"][0]["geometry"]["location"]
        return (location["lat"], location["lng"])
    except Exception,e:
        log(e)
        return ("","")
        
def GetGoogleStreetViewMap(search_string,aspect,zoomlevel,direction):
    try:
        if aspect == "square":
            size = "640x640"
        else:
            size = "640x400"
        direction = direction * 17
        zoom = 130 - int(zoomlevel) * 6
        log("zoomlevel ist bei " + str(zoom))
        search_string = urllib.quote_plus(search_string)
        base_url='http://maps.googleapis.com/maps/api/streetview?&sensor=false&'
        url = base_url + 'location=%s&size=%s&fov=%s&key=%s&heading=%s' % (search_string, size, str(zoom), googlemaps_key, str(direction))
        log("Google Maps Search:" + url)
        cachedthumb = xbmc.getCacheThumbName(url)
        log(cachedthumb)
        return url
    except Exception,e:
        log(e)
        return ""
        
      
def GetRottenTomatoesMovies(type):
    movies = []
    results = ""
    try:
       # url = 'http://api.rottentomatoes.com/api/public/v1.0/lists/movies/in_theaters.json?apikey=%s&country=%s' % (rottentomatoes_key,xbmc.getLanguage()[:2].lower())
        url = 'http://api.rottentomatoes.com/api/public/v1.0/lists/movies/%s.json?apikey=%s' % (type, rottentomatoes_key)
     #   url = 'http://api.rottentomatoes.com/api/public/v1.0/movies/770672122/similar.json?apikey=%s&limit=20' % (rottentomatoes_key)
        response = GetStringFromUrl(url)
        results = simplejson.loads(response)
    except:
        log("Error when fetching RottenTomatoes data from net")
    count = 1
    if results:
        log(results)
        for item in results["movies"]:
          #  Year = item["release_dates"]["theatre"]             
            movie = {'Title': item["title"],
                     'Thumb': item["posters"]["original"],
                     'Runtime': item["runtime"],
                     'Year': item["year"],
                     'mpaa': item["mpaa_rating"],
                     'Rating': item["ratings"]["critics_score"] / 10,
                     'Plot': item["synopsis"]  }
            movies.append(movie)
            count += 1
    return movies
    
def GetTraktCalendarShows(Type):
    shows = []
    results = ""
    try:
        url = 'http://api.trakt.tv/calendar/%s.json/%s' % (Type,trakt_key)
        response = GetStringFromUrl(url)
        results = simplejson.loads(response)
    except:
        log("Error when fetching Trakt data from net")
    count = 1
    if results:
        for day in results:
            for count, episode in enumerate(day["episodes"]):
                show = {'%i.Title' % (count) : episode["episode"]["title"],
                        '%i.TVShowTitle' % (count) : episode["show"]["title"],
                        '%i.Runtime' % (count) : episode["show"]["runtime"],
                        '%i.Certification' % (count) : episode["show"]["certification"],
                        '%i.Studio' % (count) : episode["show"]["network"],
                        '%i.Plot' % (count) : episode["show"]["overview"],
                        '%i.Genre' % (count) : " / ".join(episode["show"]["genres"]),
                        '%i.Thumb' % (count) : episode["episode"]["images"]["screen"],
                        '%i.Art(poster)' % (count) : episode["show"]["images"]["poster"],
                        '%i.Art(banner)' % (count) : episode["show"]["images"]["banner"],
                        '%i.Art(fanart)' % (count) : episode["show"]["images"]["fanart"]  }
                shows.append(show)
            count += 1
    return shows

def HandleTraktMovieResult(results):
    count = 1
    movies = []
    for movie in results:      
        movie = {'Title': movie["title"],
                'Runtime': movie["runtime"],
                'Tagline': movie["tagline"],
                'Play': "PlayMedia(" + ConvertYoutubeURL(movie["trailer"]) + ")",
                'Trailer': ConvertYoutubeURL(movie["trailer"]),
                'Year': movie["year"],
                'mpaa': movie["certification"],
                'Plot': movie["overview"],
                'Premiered': movie["released"],
                'Rating': movie["ratings"]["percentage"]/10,
                'Genre': " / ".join(movie["genres"]),
                'Art(poster)': movie["images"]["poster"],
                'Art(fanart)': movie["images"]["fanart"]  }
        movies.append(movie)
        count += 1
        if count > 20:
            break
    return movies

def HandleTraktTVShowResult(results):
    count = 1
    shows = []
    for tvshow in results:      
        show = {'Title': tvshow["title"],
                'Runtime': tvshow["runtime"],
                'Year': tvshow["year"],
                'mpaa': tvshow["certification"],
                'Studio': tvshow["network"],
                'Plot': tvshow["overview"],
                'NextDate': tvshow["air_day"],
                'ShortTime': tvshow["air_time"],
                'Premiered': tvshow["first_aired"],
                'Country': tvshow["country"],
                'Rating': tvshow["ratings"]["percentage"]/10,
                'Genre': " / ".join(tvshow["genres"]),
                'Art(poster)': tvshow["images"]["poster"],
                'Art(banner)': tvshow["images"]["banner"],
                'Art(fanart)': tvshow["images"]["fanart"]  }
        shows.append(show)
        count += 1
        if count > 20:
            break
    return shows
    
def GetTrendingShows():
    results = ""
    filename = Addon_Data_Path + "/trendingshows.txt"
    if xbmcvfs.exists(filename) and time.time() - os.path.getmtime(filename) < 86400:
        results = read_from_file(filename)
        log(results)
        return HandleTraktTVShowResult(results)
    else:    
        try:
            url = 'http://api.trakt.tv/shows/trending.json/%s' % trakt_key
            response = GetStringFromUrl(url)
            log(response)
            save_to_file(response,"trendingshows",Addon_Data_Path)
            results = simplejson.loads(response)
        except:
            log("Error when fetching  trending data from Trakt.tv")
        count = 1
        if results:
            return HandleTraktTVShowResult(results)
    
def GetTrendingMovies():
    results = ""
    filename = Addon_Data_Path + "/trendingmovies.txt"
    if xbmcvfs.exists(filename) and time.time() - os.path.getmtime(filename) < 86400:
        results = read_from_file(filename)
        log(results)
        return HandleTraktMovieResult(results)
    else:  
        try:
            url = 'http://api.trakt.tv/movies/trending.json/%s' % trakt_key
            response = GetStringFromUrl(url)
            log("TrendingMovies Response:")
            log(response)
            results = simplejson.loads(response)
        except:
            log("Error when fetching  trending data from Trakt.tv")
        count = 1
        if results:
            return HandleTraktMovieResult(results)
    
    
def GetSimilarRT(type,imdb_id):
    movies = []
    shows = []
    results = ""
    if type == "tvshow":
        type = "show"
    filename = Addon_Data_Path + "/similar" + type + imdb_id + ".txt"
    if xbmcvfs.exists(filename) and time.time() - os.path.getmtime(filename) < 86400:
        results = read_from_file(filename)
        if type == "show":
            return HandleTraktTVShowResult(results)
        elif type =="movie":
            return HandleTraktMovieResult(results)
    else:         
        try:
            url = 'http://api.trakt.tv/%s/related.json/%s/%s/' % (type, trakt_key, imdb_id)
            log(url)
            response = GetStringFromUrl(url)
            save_to_file(response,"similar" + type + imdb_id,Addon_Data_Path)
            results = simplejson.loads(response)
        except:
            log("Error when fetching  trending data from Trakt.tv")
        if results:
            if type == "show":
                return HandleTraktTVShowResult(results)
            elif type =="movie":
                return HandleTraktMovieResult(results)
    return[]
    
            
def GetYoutubeVideos(jsonurl,prefix = ""):
    results = []
    try:
        response = GetStringFromUrl(jsonurl)
        results = simplejson.loads(response)
    except:
        log("Error when fetching JSON data from net")
    count = 1
    log("found youtube vids: " + jsonurl)
    videos=[]
    if results:
        try:
            for item in results["value"]["items"]:
                video = {'Thumb': item["media:thumbnail"][0]["url"],
                         'Media': ConvertYoutubeURL(item["link"]),
                         'Play': "PlayMedia(" + ConvertYoutubeURL(item["link"]) + ")",
                         'Title':item["title"],
                         'Description':item["content"]["content"],
                         'Date':item["pubDate"]  }
                videos.append(video)
                count += 1
        except:
            for item in results["feed"]["entry"]:
                for entry in item["link"]:
                    if entry.get('href','').startswith('http://www.youtube.com/watch'):
                        video = {'Thumb': "http://i.ytimg.com/vi/" + ExtractYoutubeID(entry.get('href','')) + "/0.jpg",
                                 'Media': ConvertYoutubeURL(entry.get('href','')),
                                 'Play':"PlayMedia(" + ConvertYoutubeURL(entry.get('href','')) + ")",
                                 'Title':item["title"]["$t"],
                                 'Description':"To Come",
                                 'Date':"To Come"  }
                        videos.append(video)
                        count += 1
    return videos

def GetSimilarInLibrary(id): # returns similar artists from own database based on lastfm
    from OnlineMusicInfo import GetSimilarById
    simi_artists = GetSimilarById(id)
    if simi_artists == None:
         log('Last.fm didn\'t return proper response')
         return None
    xbmc_artists = GetXBMCArtists()
    artists = []
    start = time.clock()
    for (count, simi_artist) in enumerate(simi_artists):
        for (count, xbmc_artist) in enumerate(xbmc_artists):
            hit = False
            if xbmc_artist['mbid'] != '':
                #compare music brainz id
                if xbmc_artist['mbid'] == simi_artist['mbid']:
                    hit = True
            else:
                #compare names
                if xbmc_artist['Title'] == simi_artist['name']:
                    hit = True
            if hit:
         #       log('%s -> %s' % (xbmc_artist['name'], xbmc_artist['thumb']))
                artists.append(xbmc_artist)
    finish = time.clock()
    log('%i of %i artists found in last.FM is in XBMC database' % (len(artists), len(simi_artists)))
    return artists    