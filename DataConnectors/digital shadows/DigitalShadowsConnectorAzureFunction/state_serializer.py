""" handle and save last updated time here """
from datetime import datetime
#import os

class state:
    before_time = datetime.now()

    """ converts datetime string to DS type time """
    def convert_to_DS_time(date, hour, minute, second):
        parsed_str = date + "T" + hour + "%3A" + minute + "%3A" + second + ".000Z"  
        return parsed_str

    def convert_to_datetime(date_var):
        date = str(date_var[0:10]).split('-')
        time = str(date_var[11:19]).split(':')
        parsed_date = datetime(int(date[0]), int(date[1]), int(date[2]), int(time[0]), int(time[1]), int(time[2]))
        return parsed_date


    """ gets the last updated time(needs work on implementation of incremental and historical poll by saving the state) """
    def get_last_updated(self):     
        self.after_time = datetime.strptime("2021-09-01 05:23:25", "%Y-%m-%d %H:%M:%S")
        #os.environ['aftertime'] = str(self.after_time)
