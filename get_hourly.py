import pandas as pd
import datetime as dt

class DataFetcher:
    def __init__(self):
        directory_file = open("data_directory.txt","r")
        self.data_path = directory_file.read()

    def get_latest_filenames_url(self, year, day):
        year = str(year)

        if day < 99:
            day = "0" + str(day)
        else:
            day = str(day)

        filenames_url = "https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/6/MOD06_L2/" + year + "/" + day + ".csv"
        return filenames_url
        #filenames = pd.read_csv(filenames_url)

    def get_latest_filenames(self, latest_filenames_url):
        try:
            return pd.read_csv(latest_filenames_url)
        except:
            #TODO: log failure to read new file
            return pd.DataFrame({'A' : []})


x = DataFetcher()

year = dt.datetime.today().year
day = dt.datetime.today().day

latest_filenames_url = x.get_latest_filenames_url(year, day)

print(latest_filenames_url)
pd.read_csv(latest_filenames_url)


latest_filenames = x.get_latest_filenames(latest_filenames_url)
latest_filenames.head()
