import requests

API = "https://ow-api.com/v1/stats/pc/eu/"


def get_stats(battletag):
    response = requests.get(f"{API}/{battletag}/profile")
    if not response:
        return False
    return response.json()

