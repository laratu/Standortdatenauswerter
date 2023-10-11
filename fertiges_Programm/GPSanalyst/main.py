from StopGoAnalysis import StopGoAnalysis
from pathlib import Path
import gpxpy
import pandas as pd
from glob import glob
import os.path



##########################################################################
#* LocVal experiment
# This file collects all gpx data and evaluates them. 
# The analysis works with the help of the Stop&GO classifier, Openstreetmap data and other analysis functionalities.
# Folders:
# gpxData: Here the pure GPX data are stored
# csvdata: Here are the GPX data that have been converted to csv files.
# output: All evaluation files are located here, sorted by user name.
##########################################################################






##########################################################################
#* Convert all user GPX data to csv files 
# Save this in the given directory ('data')
##########################################################################

files = glob('gpxData/*.gpx*')
directory = 'csvdata'

for gpx_path in files:
    with open(gpx_path) as f:
        gpx = gpxpy.parse(f)

    points = []
    for segment in gpx.tracks[0].segments:
        for p in segment.points:
            points.append({
                'ts': p.time,
                'latitude': p.latitude,
                'longitude': p.longitude,
                'altitude': p.elevation,
            })

    df = pd.DataFrame.from_records(points)

    filename = gpx_path.split('/')[-1].split('.gpx')[0]
    df.to_csv(f'{directory}/{filename}.csv', index=False)




##########################################################################
#* Create or Update Login.csv
# Creates the login list. 
# If entries have already been made and new ones are to be added, 
# the old login list (logindata.csv) is scanned for new users. 
# User data that has already been analyzed does not have to be analyzed twice (finished_users).
##########################################################################


# investigates whether there is already evaluated user data.
finished_users = []


if os.path.isfile("./logindata.csv"):
   login_df = pd.read_csv('./logindata.csv')
   finished_users = login_df['username'].to_list()
else:
   login_df = pd.DataFrame(columns = ['username','password'])



# Logindata is created or updated
for gpx_path in files:
    # add user and password 
    username = gpx_path.split('/')[-1].split('.gpx')[0]

    if(username not in finished_users):
        login_df.loc[-1] = [username,'LocVal']  # adding a row
        login_df.index = login_df.index + 1  # shifting index
        login_df = login_df.sort_index() 
        print(username, 'not in', finished_users)

login_df.to_csv(f'logindata.csv', index=False)







####################################################################################
#* Perform the actual data evaluation with the Stop&GO classifier and the analysis. 
# output: saved in outputDirectory
# output: One folder is created per user. It contains 3 files: 
# - alldata.csv: all GPS data 
# - report.csv: an evaluation over all days 
# - unique_stops.csv: information about all visited locations
####################################################################################


outputDirectory = 'data'
analysis = StopGoAnalysis()
files = Path(directory).glob('*.csv')
for file in files:
    cur_user = str(file).split('/')[-1][::-1].split('.', 1)[1][::-1]

    if(cur_user not in finished_users):
        print(cur_user, 'not in ', finished_users)
        analysis.analyse(str(file), outputDirectory)






##########################################################################
#* Create Login.csv
# create Login.csv with 
##########################################################################

login_df = pd.DataFrame(columns = ['username','password'])

for gpx_path in files:
     # add user and password 
    username = gpx_path.split('/')[-1].split('.gpx')[0]
    login_df.loc[-1] = [username,'LocVal']  # adding a row
    login_df.index = login_df.index + 1  # shifting index
    login_df = login_df.sort_index() 
    print(username, '/n')

login_df.to_csv(f'logindata.csv', index=False)