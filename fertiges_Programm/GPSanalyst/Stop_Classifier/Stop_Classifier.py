import pandas as pd
import osmnx as ox
from shapely.geometry import Point


class Stop_Classifier:


    health = {'amenity':['training','pharmacy','hospital','doctors','hospital','dentist','clinic'],'leisure':['dance','fitness_centre','fitness_station','golf_course','sports_centre','sports_hall','pitch','swimming_area','swimming_pool','track'],'building':['stadium','sports_hall','hospital'],'sport':True, 'healthcare':True}
    shopping = {'shop':True}
    education = {'amenity':['college','language_school','library','music_school','school','university'],'building':['university']}
    free_time = {'cuisine':True,'leisure':['adult_gaming_centre','amusement_arcade','beach_resort','bowling_alley','dance','dog_park','escape_game','garden','park','outdoor_seating','playground','sauna'],'amenity':['bar','biergarten','cafe','fast_food','food_court','ice_cream','pub','restaurant','arts_centre','brothel','casino','cinema','community_centre','events_venue','exhibition_centre','love_hotel','music_venue','night_club','planetarium','stripclub','theatre'],'tourism':['museum','zoo','aquarium','gallery','theme_park']}



    @staticmethod
    def get_poi_from_class(lat, lon, taglist):
    


        #identify POI from OSMNX
        geom = ox.geometries.geometries_from_point((lat,lon), taglist, dist=50)

        # POI found?
        if(len(geom) > 0):

            # add distance
            #p = Point(stop[1], stop[0])
            p = Point(lon, lat)
            geom['dist'] = p.distance(geom['geometry'])

            # return nearest POI
            geom = geom[geom['dist'] == geom['dist'].min()]

        return geom





    # * return: OSM Informationen (GDF) über den gefundenen POI mit Klassifizierung
    # Klassifizierung: geom['class'][0]
    @staticmethod
    def classify_stop(lat,lon):#(stop):

        # define tags
        health = {'amenity':['training','pharmacy','hospital','doctors','hospital','dentist','clinic'],'leisure':['dance','fitness_centre','fitness_station','golf_course','sports_centre','sports_hall','pitch','swimming_area','swimming_pool','track'],'building':['stadium','sports_hall','hospital'],'sport':True, 'healthcare':True}
        shopping = {'shop':True}
        education = {'amenity':['college','language_school','library','music_school','school','university'],'building':['university']}
        free_time = {'cuisine':True,'leisure':['adult_gaming_centre','amusement_arcade','beach_resort','bowling_alley','dance','dog_park','escape_game','garden','park','outdoor_seating','playground','sauna'],'amenity':['bar','biergarten','cafe','fast_food','food_court','ice_cream','pub','restaurant','arts_centre','brothel','casino','cinema','community_centre','events_venue','exhibition_centre','love_hotel','music_venue','night_club','planetarium','stripclub','theatre'],'tourism':['museum','zoo','aquarium','gallery','theme_park']}
    
        # health:
        geom_h = Stop_Classifier.get_poi_from_class(lat, lon, health)
        geom_h['class'] = 'health'
        geom = geom_h

        # shopping
        geom_s = Stop_Classifier.get_poi_from_class(lat, lon, shopping)
        geom_s['class'] = 'shopping'
        geom = pd.concat([geom, geom_s])

        # health:
        geom_e = Stop_Classifier.get_poi_from_class(lat, lon, education)
        geom_e['class'] = 'work_education'
        geom = pd.concat([geom, geom_e])

        # shopping
        geom_f = Stop_Classifier.get_poi_from_class(lat, lon, free_time)
        geom_f['class'] = 'free_time'
        geom = pd.concat([geom, geom_f])


        # return only nearest POI
        if(len(geom) > 0):
            geom = geom[geom['dist'] == geom['dist'].min()]
            # befindet sich der POI in zwei Polgonen? -> größeren auswählen
            geom = geom[geom['geometry'].area == geom['geometry'].area.max()]
            # NaN Werte löschen
            geom = geom.dropna(axis=1, how='all')



        ## return values: classification and name of POI
        ## does POI is found? Does the POI has a name?
        if(geom.empty):
            return ('no classification', 'no name')
        
        if('name' not in geom.columns):
            return (geom['class'].iloc[0], 'no name')

    
        return (geom['class'].iloc[0], geom['name'].iloc[0])