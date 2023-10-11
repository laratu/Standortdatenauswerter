from CSVReader.Reader import Reader
from Helper.Helper import Helper
from CoordinateProjector.Projector import Projector
from LocationComparison.LocationComparison import LocationComparison
from StopGoClassifier.StopGoClassifier import StopGoClassifier
from AddressLookup.AddressLookup import AddressLookup
from Stop_Classifier.Stop_Classifier import Stop_Classifier

from datetime import timedelta
from scipy import spatial
from tqdm import tqdm
import datetime
import numpy as np
import pandas as pd
import pytz
import os



class StopGoAnalysis:

    @staticmethod
    def analyse(current_file, output):

        ##########################################################################
        #* fetch & preprocess samples
        ##########################################################################
        current_file = current_file
        filepath = '/'.join(current_file.split('/')[:-1])
        filename = current_file.split('/')[-1]
        reader = Reader(f'{filepath}/{filename}')
        df = reader.process()




        filename_wo_ext = filename.split(".")[0]

        #creating output path
        outputpath = f'{output}/{filename_wo_ext}'
        if not os.path.exists(outputpath):
            os.makedirs(outputpath)


        ##########################################################################
        #* pre-processing
        ##########################################################################
        # classifiy stop and trip intervals
        classifier = StopGoClassifier()
        classifier.read(df.ts, df.x, df.y).run()

        # get list of all identified stop intervals
        stop_df = classifier.stop_df

        # get list of all identified trip intervals
        trip_df = classifier.trip_df

        # get all trip-accociated samples
        trip_samples_df = classifier.trip_samples_df
        trip_samples_df = trip_samples_df.sort_values('ts')
        trip_alldata_df = trip_samples_df

        # add lat lon
        projected_coordinates = trip_alldata_df.apply(lambda r: Projector.project_UTM33N_to_WSG84(r.x, r.y), axis=1)
        trip_alldata_df['lat'] = projected_coordinates.apply(lambda x: x[0][0])
        trip_alldata_df['lon'] = projected_coordinates.apply(lambda x: x[1][0])
        trip_point_df = Helper.add_distance_to_next(trip_alldata_df)

        # identify unique places
        stop_df['unique_id'] = LocationComparison.generate_unique_ids(stop_df)



        ##########################################################################
        #* analysis
        ##########################################################################
        def generate_results(points, stops, trips, trip_point_df, time_interval = 86400):
            points = points.sort_values('ts')
            stops = stops.sort_values('start')
            trips = trips.sort_values('start')
            trip_point_df = trip_point_df.sort_values('ts')

            results = dict()
            results['interval (sec)'] = (points.ts.iloc[-1] - points.ts.iloc[0]).total_seconds()

            # prepare
            if len(stops) > 0:
                stops.duration = stops.apply(lambda row: (row.stop - row.start).total_seconds(), axis=1)
                uid_group = stops.groupby('unique_id')
                unique_locations = pd.DataFrame()
                unique_locations['x'] = uid_group.x.mean()
                unique_locations['y'] = uid_group.y.mean()
                unique_locations['duration'] = uid_group.duration.sum()
                unique_locations['stop_count'] = uid_group.duration.count()
            if len(trip_point_df) > 1:
                trip_point_df = Helper.add_distance_to_next(trip_point_df)

            # revisited locations
            results['stops'] = stops.shape[0]
            if len(stops) > 0:
                results['unique revisited locations'] = unique_locations[unique_locations.stop_count > 1].shape[0]
                results['revisited location visits'] = unique_locations[unique_locations.stop_count > 1].stop_count.sum()
                results['total unique locations'] = unique_locations[unique_locations.stop_count == 1].stop_count.sum()
            else:
                results['unique revisited locations'] = 0
                results['revisited location visits'] = 0
                results['total unique locations'] = 0

            # trip details
            results['trips'] = trips.shape[0]
            if len(trip_point_df) > 1:
                results['total trip path distance (km)'] = round(trip_point_df.distance_to_next.sum() / 1000.0, 3)
                results['mean trip path distance (km)'] = round((trip_point_df.distance_to_next.sum() / 1000.0) / trips.shape[0], 3)
                results['total trip duration (min)'] = round(trips.duration.sum() / 60.0, 1)
                results['mean trip duration (min)'] = round((trips.duration.sum() / 60.0) / trips.shape[0], 1)
            else:
                results['total trip path distance (km)'] = 0.0
                results['mean trip path distance (km)'] = 0.0
                results['total trip duration (min)'] = 0.0
                results['mean trip duration (min)'] = 0.0

            # first move
            if len(trip_point_df) > 0:
                timestamp = trip_point_df.iloc[0].ts
                results['time first move'] = (timestamp + timedelta(hours=0)).strftime('%H:%M')
                
                timestamp = trip_point_df.iloc[-1].ts
                results['time last move'] = (timestamp + timedelta(hours=0)).strftime('%H:%M')
            else:
                results['time first move'] = 'no trip'

            # convex hull area & perimeter
            if len(trip_point_df) > 0:
                trip_point_pairs = np.array(trip_point_df[['x', 'y']])
                if trip_point_pairs.shape[0] > 2:
                    chull = spatial.ConvexHull(trip_point_pairs)
                    results['area convex hull (km2)'] = str(round(chull.volume / 1000000.0, 3))
                    results['perimeter convex hull (km)'] = str(round(chull.area / 1000.0, 3))
            else:
                results['area convex hull (km2)'] = 'no trip'
                results['perimeter convex hull (km)'] = 'no trip'

            return results


        ##########################################################################
        #* generate results table
        ##########################################################################
        # analyse all data for an analysis of all days together
        whole_time_interval = (df.ts.iloc[-1] - df.ts.iloc[0]).total_seconds()
        #trip_samples_df.to_csv(f'trip_samples_df.csv', index=False)
        overall_stats = generate_results(df, stop_df, trip_df, trip_samples_df, time_interval=whole_time_interval)
        ##own
        overall_stats['time'] = 'whole period'
        analysis_results = [overall_stats]

        # iterate over each day, starting at 3am
        days = df.ts.dt.floor('d').apply(lambda x: str(x)[0:10]).unique()
        for day in tqdm(days):
            # day = days[0]
            dt = datetime.datetime.strptime(f"{day} 3", "%Y-%m-%d %H")
            start_ts = pytz.timezone('Europe/Berlin').localize(dt)
            end_ts = start_ts + timedelta(days=1)

            trip_point_subset = trip_samples_df[(trip_samples_df.ts >= start_ts) & (trip_samples_df.ts <= end_ts)].copy()
            point_subset = df[(df.ts >= start_ts) & (df.ts <= end_ts)].copy()
            stop_subset = stop_df[(stop_df.stop >= start_ts) & (stop_df.start <= end_ts)].copy()
            trip_subset = trip_df[(trip_df.stop >= start_ts) & (trip_df.start <= end_ts)].copy()

            # omit this day if there is no data
            if len(stop_subset) == 0 and len(trip_subset) == 0:
                continue

            # limit start & stop boundaries of subset
            if len(stop_subset) > 0:
                if stop_subset.iloc[0].start < start_ts:
                    stop_subset.loc[stop_subset.iloc[0].name, 'start'] = start_ts
                if stop_subset.iloc[-1].stop > end_ts:
                    stop_subset.loc[stop_subset.iloc[-1].name, 'stop'] = end_ts
            if len(trip_subset) > 0:
                if trip_subset.iloc[0].start < start_ts:
                    trip_subset.loc[trip_subset.iloc[0].name, 'start'] = start_ts
                if trip_subset.iloc[-1].stop > end_ts:
                    trip_subset.loc[trip_subset.iloc[-1].name, 'stop'] = end_ts

            # find interval (relevant for first and last day in list)
            if len(trip_point_subset) > 0:
                if len(stop_subset) > 0:
                    period_start = min(trip_point_subset.iloc[0].ts, stop_subset.iloc[0].start)
                    period_stop = max(trip_point_subset.iloc[-1].ts, stop_subset.iloc[-1].stop)
                else:
                    period_start = trip_point_subset.iloc[0].ts
                    period_stop = trip_point_subset.iloc[-1].ts
            elif len(stop_subset) > 0:
                period_start = stop_subset.iloc[0].start
                period_stop = stop_subset.iloc[-1].stop
            interval = (period_stop - period_start).total_seconds()

            # compute stats

            stats = generate_results(point_subset, stop_subset, trip_subset, trip_point_subset, interval)
            stats['time'] = day
            analysis_results.append(stats)

            

        # create dataframe
        results_df = pd.DataFrame(analysis_results).set_index('time')



        #####################################################################
        #* save report & stops
        #####################################################################

        results_df.to_csv(f'{output}/{filename_wo_ext}/report.csv')

        # save stops
        projected_coordinates = stop_df.apply(lambda r: Projector.project_UTM33N_to_WSG84(r.x, r.y), axis=1)
        stop_df['lat'] = projected_coordinates.apply(lambda x: x[0][0])
        stop_df['lon'] = projected_coordinates.apply(lambda x: x[1][0])

        stop_df['address'] = 'unknown'
        for uid in tqdm(range(stop_df.unique_id.max() + 1)):
            stops = stop_df[stop_df.unique_id == uid]
            address = AddressLookup.lookup_WSG84(stops.iloc[0].lat, stops.iloc[0].lon)
            indices = stops.index
            stop_df.loc[indices, 'address'] = address









        #####################################################################
        #* save trip details
        #####################################################################

        trip_infos = pd.DataFrame()
        trip_samples_df = Helper.add_distance_to_next(trip_samples_df)
        for i in range(len(trip_df)):
            start = trip_df.iloc[i]['start']
            end = trip_df.iloc[i]['stop']

            trip = trip_samples_df[(trip_samples_df['ts']>=start)&(trip_samples_df['ts']<=end)]
            trip['trip_id']=i
            trip_infos = trip_infos.append(trip)




        #####################################################################
        #* unique locations
        #####################################################################

        # convert to string, so csv doesnt save Timestamp(ns, tz) and only datetime
        stop_df['start'] = stop_df.apply(lambda x: str(x.start), axis=1)
        stop_df['stop'] = stop_df.apply(lambda x: str(x.stop), axis=1)

        uid_group = stop_df.groupby('unique_id')
        unique_locations = pd.DataFrame()
        unique_locations['x'] = uid_group.x.mean()
        unique_locations['y'] = uid_group.y.mean()
        unique_locations['duration'] = uid_group.duration.sum()
        unique_locations['stop_count'] = uid_group.duration.count()
        unique_locations


        # add lat lon
        projected_coordinates = unique_locations.apply(lambda r: Projector.project_UTM33N_to_WSG84(r.x, r.y), axis=1)
        unique_locations['lat'] = projected_coordinates.apply(lambda x: x[0][0])
        unique_locations['lon'] = projected_coordinates.apply(lambda x: x[1][0])

        unique_locations['starts'] = uid_group.start.agg(list)
        unique_locations['stops'] = uid_group.stop.agg(list)
        unique_locations['durations'] = uid_group.duration.apply(list)

        # now drop x,y
        unique_locations.drop(['x', 'y'], axis=1)

        # add classification
        classified_stops = unique_locations.apply(lambda r: Stop_Classifier.classify_stop(r.lat, r.lon), axis=1)
        unique_locations['class'] = classified_stops.apply(lambda x: x[0])
        unique_locations['name'] = classified_stops.apply(lambda x: x[1])


        ## Home and Work are classified different:
        # Home place: The place where the most time was spent overall
        # Work place: The place where the second most time was spent in total

        unique_locations = unique_locations.sort_values(by=['duration'],ascending=False)
        unique_locations['class'].iloc[0] = 'Home' 
        unique_locations['name'].iloc[0] = 'Home Location' 
        unique_locations['class'].iloc[1] = 'work_education'
        unique_locations['name'].iloc[1] = 'Work Location' 


        adresses = unique_locations.apply(lambda r: AddressLookup.lookup_WSG84(r.lat, r.lon), axis=1)
        unique_locations['adress'] = adresses.apply(lambda x: x)


        #unique_locations.to_csv(f'{filename_wo_ext}_unique_stops.csv', index=False)
        unique_locations.to_csv(f'{output}/{filename_wo_ext}/unique_stops.csv', index=False)
        #trip_alldata_df.to_csv(f'{filename_wo_ext}'+'trip_alldata.csv', index=False)
        trip_alldata_df.to_csv(f'{output}/{filename_wo_ext}/alldata.csv', index=False)
