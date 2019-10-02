import requests
import gmplot
import folium
import json
import os
import pandas as pd
from bs4 import BeautifulSoup
from geotext import GeoText
from collections import OrderedDict
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut


def delDupes(x):
    return list(OrderedDict.fromkeys(x))


def loadMap(x, y):
    with open("creds.txt", "r") as f:
        creds = f.readline()
    gmap = gmplot.GoogleMapPlotter(
        0, 0, 0, apikey=creds)  # Google Maps API Key
    gmap.heatmap(x, y)
    gmap.draw("map.html")


def main():
    page = requests.get("https://apnews.com/apf-intlnews")
    soup = BeautifulSoup(page.content, 'html.parser')
    articles = soup.find_all("div", {"class", "FeedCard c0117 c0118"})
    articleLinks = []

    for link in articles:
        url = link.find_all('a')[0]
        articleLinks.append('https://www.apnews.com' + url.get('href'))

    articleBodies = []

    for link in articleLinks:
        articleText = []
        articleBody = []
        page = requests.get(link)
        soup = BeautifulSoup(page.content, 'html.parser')
        for paragraph in soup.find_all('p'):
            articleText = paragraph.text
            if not ('__' in articleText):
                articleBody.append(articleText)
        text = ''.join(articleBody)
        articleBodies.append(text)

    cities = []

    for article in articleBodies:
        cleanCities = delDupes(GeoText(article).cities)
        if 'Un' in cleanCities:
            cleanCities.remove('Un')
        cities.append(cleanCities)

    geolocator = Nominatim(user_agent="CityFinder")

    lat = []
    long = []
    id = []
    counter = 1

    for citiesList in cities:
        for city in citiesList:
            try:
                lat.append(geolocator.geocode(city, timeout=10).latitude)
                long.append(geolocator.geocode(city, timeout=10).longitude)
                id.append(counter)
            except:
                print("Error: Geocode failed on input %s" % city)
        counter = counter + 1

    # with open("lats.json", "w") as f:
    #     json.dump(lat, f)
    # with open("longs.json", "w") as f:
    #     json.dump(long, f)

    df = pd.DataFrame(data={"lats": lat, "longs": long, "id": id})
    df.to_csv("data.csv", index=False)

    loadMap(lat, long)


# if os.path.exists('lats.json') or os.path.exists('longs.json'):
#     with open("lats.json", "r") as f:
#         lats = json.load(f)
#     with open("longs.json", "r") as f:
#         longs = json.load(f)

if os.path.exists('data.csv'):
    colnames = ["lats", "longs", "id"]
    df = pd.read_csv("data.csv", names=colnames)
    loadMap(df.lats.tolist(), df.longs.tolist())
else:
    main()
