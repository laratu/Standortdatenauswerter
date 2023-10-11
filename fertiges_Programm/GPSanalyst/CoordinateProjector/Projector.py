import numpy as np
import pandas as pd
import geopandas as gpd



class Projector:

    @staticmethod
    def project_WSG84_to_UTM33N(lat, lon):
        # interpret raw GPS records as WGS84 and project them onto WGS / UTM zone 33N
        geometry = gpd.points_from_xy(lon, lat)
        gdf = gpd.GeoDataFrame(pd.DataFrame(), geometry=geometry)
        gdf = gdf.set_crs('EPSG:4326')
        gdf = gdf.to_crs('EPSG:32633')

        # extract x / y values
        gdf['x'] = list(map(lambda val: val.x, gdf.geometry.values))
        gdf['y'] = list(map(lambda val: val.y, gdf.geometry.values))

        return (gdf.x.values, gdf.y.values)
    
    @staticmethod
    def project_WSG84_to_EPSG(lat, lon, target_epsg):
        # interpret raw GPS records as WGS84 and project them onto a target EPSG code
        geometry = gpd.points_from_xy(lon, lat)
        gdf = gpd.GeoDataFrame(pd.DataFrame(), geometry=geometry)
        gdf = gdf.set_crs('EPSG:4326')
        gdf = gdf.to_crs(f'EPSG:{target_epsg}')

        # extract x / y values
        gdf['x'] = list(map(lambda val: val.x, gdf.geometry.values))
        gdf['y'] = list(map(lambda val: val.y, gdf.geometry.values))

        return (gdf.x.values, gdf.y.values)

    @staticmethod
    def project_UTM33N_to_WSG84(x, y):
        if type(x) == float or type(x) == np.float64:
            x = [x]
            y = [y]

        # interpret x & y coordinates as UTM zone 33N and project them to WGS84 lat & lon values
        geometry = gpd.points_from_xy(x, y)
        gdf = gpd.GeoDataFrame(pd.DataFrame(), geometry=geometry)
        gdf = gdf.set_crs('EPSG:32633')
        gdf = gdf.to_crs('EPSG:4326')

        # extract lat / lon values
        gdf['lon'] = list(map(lambda x: x.x, gdf.geometry.values))
        gdf['lat'] = list(map(lambda x: x.y, gdf.geometry.values))

        return (gdf.lat.values, gdf.lon.values)
    
    @staticmethod
    def project_EPSG_to_WSG84(x, y, source_epsg):
        if type(x) == float or type(x) == np.float64:
            x = [x]
            y = [y]

        # interpret x & y coordinates as UTM zone 33N and project them to WGS84 lat & lon values
        geometry = gpd.points_from_xy(x, y)
        gdf = gpd.GeoDataFrame(pd.DataFrame(), geometry=geometry)
        gdf = gdf.set_crs(f'EPSG:{source_epsg}')
        gdf = gdf.to_crs('EPSG:4326')

        # extract lat / lon values
        gdf['lon'] = list(map(lambda x: x.x, gdf.geometry.values))
        gdf['lat'] = list(map(lambda x: x.y, gdf.geometry.values))

        return (gdf.lat.values, gdf.lon.values)