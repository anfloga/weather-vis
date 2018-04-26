import datetime as dt
import urllib as ul
import shutil as si
import pandas as pd
import os


class DataFetcher:

    laadsurl = "https://ladsweb.modaps.eosdis.nasa.gov/archive/allData/6/MOD06_L2/"
    latest_files = []
    latest_file_urls = []

    def __init__(self):
        directory_file = open("data_directory.txt","r")
        self.data_path = directory_file.read()[:-1]
        self.update_datetime()

    def set_year(self):
        self.year = str(dt.datetime.today().year)

    def set_day(self):
        day_int = dt.datetime.now().timetuple().tm_yday - 1

        if day_int < 100:
            self.day = "0" + str(day_int)
        else:
            self.day = str(day_int)

    def set_hour(self):
        hour_int = dt.datetime.today().hour

        if hour_int < 10:
            self.hour = "0" + str(hour_int)
        else:
            self.hour = str(hour_int)

    def set_minute(self):
        minute_int = dt.datetime.today().minute

        if minute_int < 10:
            self.minute = "0" + str(minute_int)
        else:
            self.minute = str(minute_int)

    def add_new_filename(self, filename):
        if len(self.latest_files) > 2:
            os.remove(self.latest_files[0])
        del self.latest_files[0]
        self.latest_files.append(filename)

    def update_datetime(self):
        self.set_year()
        self.set_day()
        self.set_hour()
        self.set_minute()

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

    def get_file_metadata(self):
        latest_file_names = self.get_latest_filenames()
        latest_file_names["url"] = latest_file_names.apply(lambda x: self.laadsurl + self.year + "/" + self.day + "/" + x["name"], axis=1)
        return latest_file_names

    def download_files(self):
        try:
            metadata = self.get_file_metadata()

            data_dir = self.data_path + self.year + self.day + self.hour + "/"

            if not os.path.exists(data_dir):
                os.makedirs(data_dir)

            for index, row in metadata.iterrows():
                path_to_write = data_dir + row["name"]

                if path_to_write in self.latest_files:
                    return False

                ul.request.urlretrieve(row["url"], path_to_write)
                #self.add_new_filename(path_to_write)
                print(row["name"] + " downloaded")

            return True
        except Exception as ex:
            #TODO: log failure to download latest data file
            print(ex)
            return False


df = DataFetcher()
df.download_files()

