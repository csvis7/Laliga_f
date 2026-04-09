import requests

url = "https://football-logos.cc/spain/la-liga/"
html = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"}).text

for token in html.split('"'):
    if ".png" in token.lower():
        print(token)
