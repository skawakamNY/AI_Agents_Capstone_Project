import requests

class TomTomTrafficClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_traffic_flow(self, lat, lon):
        url = f"https://api.tomtom.com/traffic/services/4/flowSegmentData/absolute/10/json?point={lat},{lon}&key={self.api_key}"
        r = requests.get(url)
        r.raise_for_status()
        return r.json()

    def get_incidents(self, bbox):
        url = f"https://api.tomtom.com/traffic/services/5/incidentDetails?bbox={bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}&key={self.api_key}"
        r = requests.get(url)
        r.raise_for_status()
        return r.json()

    def get_eta(self, origin, destination):
        url = f"https://api.tomtom.com/routing/1/calculateRoute/{origin}:{destination}/json?traffic=true&key={self.api_key}"
        r = requests.get(url)
        r.raise_for_status()
        return r.json()