from Helper.Helper import Helper
from AddressLookup.AddressLookup import AddressLookup



SAME_PLACE_THRESHOLD = 100 # distance in meter


class LocationComparison:

    @staticmethod
    def generate_unique_ids(stop_df):
        same_places = set()
        for main_idx, main_row in stop_df.iterrows():
            subset = stop_df[stop_df.index != main_idx]
            same_place_ids = []
            for sub_idx, sub_row in subset.iterrows():
                dist = Helper.distance(main_row.x, main_row.y, sub_row.x, sub_row.y)
                if dist <= SAME_PLACE_THRESHOLD:
                    same_place_ids.append(sub_idx)
            
            if len(same_place_ids) > 0:
                same_place_ids.append(main_idx)
                same_places.add(frozenset(same_place_ids))

        stop_df['unique_id'] = -1
        for cluster in same_places:
            cluster_ids = list(cluster)
            stop_df.loc[list(cluster), 'unique_id'] = min(cluster_ids)
        individual_ids = stop_df[stop_df.unique_id == -1].index
        stop_df.loc[individual_ids, 'unique_id'] = individual_ids

        # return dense ids
        numbers = stop_df.unique_id.unique()
        replacement = list(range(0, len(numbers)))
        unique_ids = stop_df.unique_id.map(dict(zip(numbers, replacement)))

        return unique_ids



    @staticmethod
    def identify_home(stop_df, verbose=False):
        if not 'unique_id' in stop_df:
            stop_df = LocationComparison.generate_unique_ids(stop_df)

        home_unique_id = stop_df.groupby('unique_id').duration.sum().idxmax()
        home_group = stop_df[stop_df.unique_id == home_unique_id].groupby('unique_id')
        home_x = home_group.x.mean().iloc[0]
        home_y = home_group.y.mean().iloc[0]

        # print home address
        if verbose:
            home_address = AddressLookup.lookup_UTM33N(home_x, home_y)
            print(f'home address is: {home_address}')
        
        return (home_x, home_y, home_unique_id)