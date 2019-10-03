import requests
import gmplot
import folium
import json
import os
import sys
import pandas as pd
from bs4 import BeautifulSoup
from geotext import GeoText
from collections import OrderedDict
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut


def delDupes(x):
    return list(OrderedDict.fromkeys(x))


def loadMap(x, y, z, i):
    with open("creds.txt", "r") as f:
        creds = f.readline()
    gmap = gmplot.GoogleMapPlotter(
        0, 0, 3, apikey=creds)  # Google Maps API Key
    # gmap.heatmap(x, y)

    gmap.scatter(x, y, i, '#FF0000', size=30000)

    # Connect Markers via Article Ids
    # lats = []
    # longs = []
    # change = z[0]
    # for counter in range(len(z)):
    #     if z[counter] == change:
    #         lats.append(x[counter])
    #         longs.append(y[counter])
    #     else:
    #         change = z[counter]
    #         gmap.plot(lats, longs, 'blue', edge_width=1.0)
    #         lats.clear()
    #         longs.clear()

    gmap.draw("map.html")


def getData():
    page = requests.get("https://apnews.com/apf-intlnews")
    soup = BeautifulSoup(page.content, 'html.parser')
    articles = soup.find_all("div", {"class", "FeedCard c0117 c0118"})

    articleLinks = []

    for link in articles:
        url = link.find_all('a')[0]
        articleLinks.append('https://www.apnews.com' + url.get('href'))

    articleBodies = []
    articleTitles = []

    for link in articleLinks:
        articleBody = []
        articleText = []
        page = requests.get(link)
        soup = BeautifulSoup(page.content, 'html.parser')
        for paragraph in soup.find_all('p'):
            articleText = paragraph.text
            if not ('__' in articleText):
                articleBody.append(articleText)
        text = ''.join(articleBody)
        articleBodies.append(text)
        try:
            articleTitles.append(soup.find('h1').text)
        except:
            articleTitles.append(
                soup.find('div', attrs={'class', 'c0121'}).text)

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
    articleTitle = []
    counter = 1

    for citiesList in cities:
        for city in citiesList:
            try:
                lat.append(geolocator.geocode(city, timeout=10).latitude)
                long.append(geolocator.geocode(city, timeout=10).longitude)
                id.append(counter)
                articleTitle.append(articleTitles[counter-1])
            except:
                print("Error: Geocode failed on input %s" % city)
        counter = counter + 1

    df = pd.DataFrame(data={"titles": articleTitle,
                            "lats": lat, "longs": long, "id": id})
    df.to_csv("data.csv", index=False)

    loadMap(lat, long, id, articleTitle)


param = "past"

if len(sys.argv) > 1:
    param = sys.argv[1]


if os.path.exists('data.csv') and param != "current":
    colnames = ["lats", "longs", "id"]
    df = pd.read_csv("data.csv", names=colnames, skiprows=1)
    loadMap(list(map(float, df.lats.tolist())), list(
        map(float, df.longs.tolist())), list(map(int, df.id.tolist())), list(map(str, df.titles.tolist())))
else:
    if os.path.exists('data.csv'):
        os.remove('data.csv')
    getData()
