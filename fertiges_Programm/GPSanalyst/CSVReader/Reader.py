import pandas as pd
from CoordinateProjector.Projector import Projector


class Reader:

    def __init__(self, filename):
        self.raw_df = pd.read_csv(filename)
        self.processed_df = None

    def process(self, target_epsg=False):
        # convert time
        data = self.raw_df.copy()
        data.ts = pd.to_datetime(data.ts, utc=True)
        data = data.set_index('ts').tz_convert('Europe/Berlin').reset_index()

        # filter duplicates per day
        data['day_str'] = data.ts.dt.floor('d').apply(lambda x: str(x)[0:10])
        data_filtered = data.drop_duplicates(subset=['day_str', 'latitude', 'longitude'], keep='first', inplace=False)

        # project coordinates
        if target_epsg == False:
            (x, y) = Projector.project_WSG84_to_UTM33N(data_filtered.latitude, data_filtered.longitude)
        else:
            (x, y) = Projector.project_WSG84_to_EPSG(data_filtered.latitude, data_filtered.longitude, target_epsg)
        data_filtered = data_filtered.copy()
        data_filtered['x'] = x
        data_filtered['y'] = y

        # select and rename relevant columns
        relevant_columns = ['ts', 'x', 'y', 'longitude', 'latitude']
        if 'motion_score' in data_filtered.columns:
            relevant_columns.append('motion_score')

        gps_data = data_filtered[relevant_columns].copy()

        if 'motion_score' in data_filtered.columns:
            gps_data.columns = ['ts', 'x', 'y', 'lon', 'lat', 'motion_score']
        else:
            gps_data.columns = ['ts', 'x', 'y', 'lon', 'lat']

        self.processed_df = gps_data
        return self.processed_df