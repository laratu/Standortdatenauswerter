import numpy as np


class Helper:

    @staticmethod
    def distance(ax, ay, bx, by):
        return np.sqrt(np.square(ax - bx) + np.square(ay - by))

    @staticmethod
    def add_distance_to_next(df):
        df['prev_x'] = df.x.shift(-1)
        df['prev_y'] = df.y.shift(-1)
        df['distance_to_next'] = Helper.distance(df.x, df.y, df.prev_x, df.prev_y)
        return df.drop(['prev_x', 'prev_y'], axis=1)