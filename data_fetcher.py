import datetime as dt
import urllib as ul
import pandas as pd


class DataFetcher:

    laadsurl = "https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/6/MOD06_L2/"

    def __init__(self):
        directory_file = open("data_directory.txt","r")
        self.data_path = directory_file.read()[:-1]
        self.update_datetime()

    def __set_year(self):
        self.year = str(dt.datetime.today().year)

    def __set_day(self):
        day_int = dt.datetime.now().timetuple().tm_yday

        if day_int < 100:
            self.day = "0" + str(day_int)
        else:
            self.day = str(day_int)

    def __set_hour(self):
        hour_int = dt.datetime.today().hour

        if hour_int < 10:
            self.hour = "0" + str(hour_int)
        else:
            self.hour = str(hour_int)

    def update_datetime(self):
        self.__set_year()
        self.__set_day()
        self.__set_hour()

    def get_latest_filenames_url(self):
        filenames_url = self.laadsurl + self.year + "/" + self.day + ".csv"
        return filenames_url

    def get_latest_filenames(self):
        latest_filenames_url = self.get_latest_filenames_url()
        try:
            return pd.read_csv(latest_filenames_url)
        except:
            #TODO: log failure to read file csv
            return pd.DataFrame({'A' : []})

    def get_latest_file_url(self):
        latest_file_name = self.get_latest_filenames().iloc[-1]["name"]
        latest_file_url = self.laadsurl + self.year + "/" + self.day + "/" + latest_file_name
        return latest_file_url

    def download_latest_file(self):
        try:
            latest_file_url = self.get_latest_file_url()
            path_to_write = self.data_path + self.year + self.day + self.hour + ".hdf"
            ul.request.urlretrieve(latest_file_url, path_to_write)
            self.latest_file_path = path_to_write
            return True
        except:
            #TODO: log failure to download latest data file
            return False

