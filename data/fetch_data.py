import requests

def get_match_data():
    url = "https://site.api.espn.com/apis/site/v2/sports/cricket/8048/scoreboard"
    response = requests.get(url)
    return response.json()