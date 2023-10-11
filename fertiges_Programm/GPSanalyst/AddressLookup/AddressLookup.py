import requests
from CoordinateProjector.Projector import Projector



API_KEY = 'S0tbkW3Dd0PtdyPfpuB5BcCfoQgKaDERnDNjILzdRrE'



class AddressLookup:

    @staticmethod
    def lookup_WSG84(lat, lon):
        URL = "https://revgeocode.search.hereapi.com/v1/revgeocode"
        
        params = {'at': f"{lat},{lon}", 'apikey': API_KEY}
        data = requests.get(url = URL, params = params).json() 

        return data['items'][0]['title']

    @staticmethod
    def lookup_UTM33N(x, y):
        (lats, lons) = Projector.project_UTM33N_to_WSG84(x, y)
        return AddressLookup.lookup_WSG84(lats[0], lons[0])