import requests
# import os
import gmplot
from bs4 import BeautifulSoup
from geotext import GeoText
from collections import OrderedDict
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

def delDupes(x):
    return list(OrderedDict.fromkeys(x))

page = requests.get("https://apnews.com/apf-intlnews")
soup = BeautifulSoup(page.content, 'html.parser')
articles = soup.find_all("div", {"class", "FeedCard c0117 c0118"})
articleLinks = []

for link in articles:
    url = link.contents[0].find_all('a')[0]
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

# print(cities)

geolocator = Nominatim(user_agent="CityFinder")
latlongAllArticles = []
latlongCurrentArticle = []

lat = []
long = []

for citiesList in cities:
    for city in citiesList:
        try:
            lat.append(geolocator.geocode(city, timeout=10).latitude)
            long.append(geolocator.geocode(city, timeout=10).longitude)
        except GeocoderTimedOut as g:
            print("Error: Geocode failed on input %s" % city)

gmap = gmplot.GoogleMapPlotter(0,0,0, apikey="AIzaSyCxguPgxGT_UXEDJFE1deqJ3_hdt3JnQA4")
gmap.heatmap(lat,long)
gmap.draw("map.html")

##########################
# Write Articles to File
##########################
# if os.path.exists('news.txt'):
#     os.remove('news.txt')
#
# with open('news.txt', 'w', encoding='utf-8') as f:
#     n = 1
#     for article in articleBodies:
#         f.write("Article {}\n".format(n))
#         n = n + 1
#         f.write("%s\n\n" % article)
